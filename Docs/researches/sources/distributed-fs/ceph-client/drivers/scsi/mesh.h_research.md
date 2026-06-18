# sources/distributed-fs/ceph-client/drivers/scsi/mesh.h

## Purpose
`mesh.h` is the private hardware contract for the PowerMac MESH SCSI driver in `mesh.c`. It defines per-command private result storage, the memory-mapped MESH register layout, sequence-register commands, SCSI bus signal bits, bus phase encodings, exception/error/interrupt bits, and synchronous-transfer parameter helpers.

## Important APIs, Types, And Macros
`struct mesh_cmd_priv` stores the command residual counter, SCSI message byte, and status byte that `mesh.c` later folds into `struct scsi_cmnd.result`. `mesh_priv()` wraps `scsi_cmd_priv()` and depends on the SCSI host template's `cmd_size` matching `sizeof(struct mesh_cmd_priv)`.

`struct mesh_regs` maps the sparse MESH register file: count low/high, FIFO, sequence, bus status registers, FIFO count, exception, error, interrupt mask, interrupt status, initiator source ID, destination ID, sync parameters, chip ID, and selection timeout. Each visible register is separated by 15 padding bytes, matching the controller's MMIO spacing.

`SEQ_*` macros encode hardware sequence commands and modifiers. `SEQ_DMA_MODE`, `SEQ_TARGET`, `SEQ_ATN`, and `SEQ_ACTIVE_NEG` are command modifiers, while low-nibble commands include arbitration, select, command, status, data in/out, message in/out, bus-free wait, parity enable/disable, reselection enable/disable, controller reset, and FIFO flush.

`BS0_*` and `BS1_*` represent SCSI bus control/status signals. `BP_*` macros derive SCSI phase values from `BS0_MSG`, `BS0_CD`, and `BS0_IO`. `EXC_*`, `ERR_*`, and `INT_*` define exception, error, and interrupt bits consumed by `mesh.c` interrupt handlers. `SYNC_OFF()`, `SYNC_PER()`, `SYNC_PARAMS()`, and `ASYNC_PARAMS` encode the MESH sync parameter register.

## Control Flow
The header has no independent executable flow beyond `mesh_priv()`. Its constants directly drive `mesh.c`: probe and reset write `SEQ_RESETMESH`, `SEQ_FLUSHFIFO`, `SEQ_ENBRESEL`, source ID, selection timeout, and `ASYNC_PARAMS`; command start uses `SEQ_ARBITRATE`, `SEQ_SELECT`, and `SEQ_DISRESEL`; data phases combine `SEQ_DATAIN`/`SEQ_DATAOUT` with `SEQ_DMA_MODE`; message timing uses `SEQ_MSGIN`, `SEQ_MSGOUT`, and `SEQ_ATN`; interrupt dispatch reads `INT_ERROR`, `INT_EXCEPTION`, and `INT_CMDDONE`; phase mismatch dispatch compares `BP_DATAIN`, `BP_DATAOUT`, `BP_COMMAND`, `BP_STATUS`, `BP_MSGOUT`, and `BP_MSGIN`.

## State And Persistence
The structures describe volatile kernel and device state only. `struct mesh_regs` is an MMIO view and must not be copied as persistent memory. `struct mesh_cmd_priv` persists only for one SCSI command lifetime and is allocated by the SCSI core as command-private storage. The sync parameter macros encode negotiated target state kept in `struct mesh_target` in `mesh.c`, not on disk.

## Dependencies And Integration Points
The header assumes the including file has declarations for `struct scsi_cmnd` and `scsi_cmd_priv()`, which `mesh.c` gets from SCSI headers. It is private to the MESH driver and is tied to PowerMac MESH hardware rather than a UAPI. The register and bit definitions are consumed through PowerPC I/O helpers in `mesh.c`.

## Risks And Edge Cases
The sparse `struct mesh_regs` layout is ABI-sensitive. Any packing, padding, type-width, or ordering change would shift MMIO offsets and break hardware access. Register fields are declared as byte-sized C objects rather than accessor functions, so users must continue to use correct MMIO read/write helpers and ordering flushes.

The sync parameter comments assume a 50 MHz clock for their explanatory timing; `mesh.c` recalculates periods from device-tree `clock-frequency`, so future code should not hard-code the comment's example. `ASYNC_PARAMS` is a magic hardware value and must stay aligned with MESH expectations.

## Test Signals
Compile-time validation should confirm that `mesh_template.cmd_size` still matches `struct mesh_cmd_priv`, that `struct mesh_regs` offsets match hardware documentation, and that every bus phase and interrupt/error bit is exercised by `mesh.c` probe, reset, command, data, message, exception, and recovery tests.
