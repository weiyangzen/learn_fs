<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/imm.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/imm.h

## Purpose

`imm.h` supplies version history, transfer mode constants, low-level parallel-port register macros, timing constants, and small declarations used by the Iomega MatchMaker (`imm`) SCSI host adapter implementation.

## Important APIs, Types, and Constants

- `IMM_VERSION` identifies the driver version string used in proc output.
- Transfer modes are `IMM_AUTODETECT`, `IMM_NIBBLE`, `IMM_PS2`, `IMM_EPP_8`, `IMM_EPP_16`, `IMM_EPP_32`, and `IMM_UNKNOWN`.
- `IMM_MODE_STRING[]` maps mode values to display strings.
- Tuning constants include `IMM_BURST_SIZE`, `IMM_SELECT_TMO`, `IMM_SPIN_TMO`, `IMM_DEBUG`, and `IN_EPP_MODE()`.
- `CONNECT_EPP_MAYBE` and `CONNECT_NORMAL` parameterize `imm_connect()`.
- Register read/write macros wrap raw `inb()`/`outb()` for data, status, control, EPP, FIFO, and ECR registers. `w_ctr()` optionally uses `outb_p()` under `CONFIG_SCSI_IZIP_SLOW_CTR`.
- `imm_scsi_pointer()` returns the command-private `struct scsi_pointer` allocated through the SCSI host template.
- The header forward-declares `imm_engine()`.

## Control Flow and State

The header does not implement command flow, but its constants drive `imm.c` probing and transfer paths. Mode constants choose between nibble, PS/2 byte, and EPP data paths. Register macros are used by every hardware phase: CPP connect/disconnect, target select, command output, data transfer, status reads, reset pulses, and ECP/EPP cleanup. `imm_scsi_pointer()` centralizes access to per-command phase and scatterlist cursor state.

## Dependencies and Integration Points

It includes kernel, module, I/O port, delay, proc, block, scheduler, interrupt, asm I/O, and SCSI host headers expected by `imm.c`. It assumes `imm_struct` is already defined before inclusion, which is why `imm.c` declares the typedef before including this header.

## Risks and Edge Cases

- `IMM_MODE_STRING` is defined in the header as a `static` array; this is acceptable for the single including C file but would create per-translation-unit copies if included elsewhere.
- Register macros perform raw I/O with no locking; callers must own the parport and preserve timing.
- `imm_scsi_pointer()` assumes the SCSI host template `cmd_size` reserves `struct scsi_pointer`; mismatches would corrupt command-private memory.
- `IMM_SPIN_TMO` and select timeout values directly affect timeout behavior on slow hardware.
- The header depends on include ordering for `imm_struct`, making it non-standalone.

## Test Signals

Build success validates include ordering and command-private sizing. Runtime proc output should show `IMM_VERSION` and a valid `IMM_MODE_STRING` entry. Mode-specific read/write tests exercise the register macros, while slow-control builds validate the `CONFIG_SCSI_IZIP_SLOW_CTR` branch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/imm.h -->
