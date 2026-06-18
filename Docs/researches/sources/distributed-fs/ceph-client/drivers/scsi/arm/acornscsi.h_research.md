# sources/distributed-fs/ceph-client/drivers/scsi/arm/acornscsi.h

## Purpose

`acornscsi.h` is the private hardware and state header for `acornscsi.c`. It defines the WD33C93A SBIC register map, uPC71071 DMAC register map, bit definitions, driver phase enums, DMA/message/command enums, status-ring debugging structures, and the `AS_Host` per-adapter state layout.

## Important APIs, Types, and Functions

The central type is `AS_Host`, which stores host pointers, MMIO bases, current command pointers, SCSI phase state, reconnect identity, active `struct scsi_pointer`, message queue, statistics, issue/disconnected queues, per-target sync/disconnect information, busy LUN bitmap, DMA bookkeeping, card page-register state, and per-target/host status rings.

Important definitions include SBIC register constants (`SBIC_OWNID`, `SBIC_CTRL`, `SBIC_TRANSCNT*`, `SBIC_SYNCHTRANSFER`, `SBIC_CMND`, `SBIC_ASR`, `SBIC_SSR`), SBIC commands (`CMND_RESET`, `CMND_SELWITHATN`, `CMND_XFERINFO`, `CMND_ASSERTATN`, `CMND_NEGATEACK`), DMAC registers and masks, phase enums (`PHASE_*`), interrupt-return enums (`INTR_*`), DMA direction (`DMA_IN`, `DMA_OUT`), sync negotiation state (`SYNC_*`), command classes (`CMD_READ`, `CMD_WRITE`, `CMD_MISC`), and data direction values.

## Control Flow

The header encodes the vocabulary used by the implementation's state machine. SBIC command/status constants drive phase transitions, DMAC fields drive setup/cleanup, and `ADD_STATUS()` records a circular trace for each target plus host slot 8. `AS_Host` joins these hardware details to SCSI mid-layer state and shared queue/message modules.

## State and Persistence Behavior

The header defines only in-memory state. The persistent runtime state is per host and includes active/disconnected commands, queue state, target sync settings, busy LUN bits, DMA buffer pointers, and recent status traces. Reset paths reinitialize this state rather than reading or writing durable configuration.

## Dependencies and Integration Points

It includes `queue.h` and `msgqueue.h` and expects Linux SCSI structures to be visible from including code. The `struct scsi_pointer` embedded in `AS_Host` is populated through `arm_scsi.h` helpers. The constants are consumed directly by `acornscsi.c`.

## Risks and Edge Cases

This header is an ABI-like contract between the driver and specific Acorn SCSI hardware. Wrong bit definitions or enum assumptions can break command selection, message phases, DMA masking, or reset handling. `ADD_STATUS()` assumes `host` is in scope and uses power-of-two ring sizing. The busy-LUN bitmap is sized for 8 targets times 8 LUNs and assumes target/lun values fit that layout.

## Test Signals

Build coverage should catch missing SCSI/queue/message definitions. Runtime validation should inspect status rings, per-target sync values, busy-LUN clearing after disconnect/abort/reset, and correct SBIC/DMAC register programming during probe and transfer.
