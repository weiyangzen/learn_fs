# sources/distributed-fs/ceph-client/drivers/scsi/qlogicfas408.c

## Purpose
`qlogicfas408.c` implements the shared low-level command engine for QLogic FAS408-compatible SCSI controllers. It is used by wrappers such as the ISA `qlogicfas` driver and PCMCIA-style integrations to program registers, perform PIO pseudo-DMA transfers, process interrupts, map SCSI status, and expose SCSI error-handling callbacks.

## Important APIs, Types, And Functions
Exported entry points are `qlogicfas408_info()`, `qlogicfas408_queuecommand()`, `qlogicfas408_abort()`, `qlogicfas408_host_reset()`, `qlogicfas408_biosparam()`, `qlogicfas408_ihandl()`, `qlogicfas408_get_chip_type()`, `qlogicfas408_setup()`, `qlogicfas408_detect()`, and `qlogicfas408_disable_ints()`. Internal helpers include `ql_zap()` for chip/SCSI reset, `ql_pdma()` for pseudo-DMA FIFO transfer, `ql_wai()` for polled interrupt/status waits, `ql_icmd()` to program and launch a command, `ql_pcmd()` to complete data/status/message phases, and `ql_ihandl()` to bridge hardware interrupt state to `scsi_done()`.

## Control Flow
The SCSI mid-layer enters `qlogicfas408_queuecommand_lck()`. It rejects commands addressed to the initiator ID, busy-waits until no command is active, then calls `ql_icmd()` to clear stale interrupts/FIFO state, program transfer and timing registers, write the CDB, store `priv->qlcmd`, and issue select-and-send-command. The IRQ handler takes the host lock, verifies the adapter interrupt bit, retrieves `priv->qlcmd`, calls `ql_pcmd()`, clears the active command, and completes the command.

`ql_pcmd()` validates selection/command completion status, clears residual FIFO data, programs the transfer count for data phases, iterates the scatterlist with `ql_pdma()`, waits for bus service, retrieves status and message bytes, disconnects, waits for bus-free indication, and fills host/status/message result fields. Error paths set `DID_NO_CONNECT`, `DID_BAD_INTR`, `DID_ERROR`, `DID_PARITY`, `DID_TIME_OUT`, `DID_ABORT`, or `DID_RESET`.

## State And Persistence
The core stores volatile adapter state in `struct qlogicfas408_priv`: current command, abort/reset flag, base port, initiator ID, IRQ, interrupt type, and info string. Static configuration words (`qlcfg5`, `qlcfg6`, `qlcfg7`, `qlcfg8`, `qlcfg9`, `qlcfgc`) derive from header macros for clock, parity, sync, and cable timing. No persistent storage is modified; all state is hardware register state or in-memory SCSI host private data.

## Dependencies And Integration Points
The code depends on port I/O (`inb`, `outb`, `insl`, `outsl`), jiffies timeouts, scatterlist helpers, SCSI command result helpers, SCSI host locking, and the macros/types in `qlogicfas408.h`. Wrappers must allocate host private storage of `struct qlogicfas408_priv`, fill `qbase`, `qinitid`, `int_type`, and IRQ information, and route interrupts to `qlogicfas408_ihandl()`.

## Risks And Edge Cases
Several waits are busy loops against hardware registers; the file itself notes historic concern about non-terminating hardware waits. Transfers above 16 MiB are not supported by the 24-bit transfer count. `ql_pdma()` may stop early on interrupt bits and does not report residual length directly. Abort/reset is communicated through `qabort`, so races with active pseudo-DMA or status phase handling are delicate. `qlogicfas408_detect()` uses repeated reads and XOR comparisons that are terse and hardware-specific. The reset callback assumes `cmd` is non-NULL despite a comment that a PCMCIA stub historically called it with `NULL`.

## Test Signals
Signals include successful chip detection and setup, one-command-at-a-time queueing, CDB launch to non-initiator targets, scatter-gather reads and writes through pseudo-DMA, status/message handling for good and check-condition completions, timeout handling in `ql_wai()` and status-phase waits, abort and host reset during an active command, parity/error interrupt handling invoking `ql_zap()`, BIOS geometry output for small and large capacities, and unload paths calling `qlogicfas408_disable_ints()`.
