# sources/distributed-fs/ceph-client/drivers/scsi/pcmcia/nsp_message.c

Purpose: directly included message phase helpers for `nsp_cs.c`. They manually transfer SCSI message-in/out bytes because the chip only interrupts on phase changes and must poll for additional REQ assertions.

Important APIs/functions: `nsp_message_in()` reads `SCSIDATAIN`, toggles ACK through `SCSIBUSCTRL`, waits for REQ negation, and records `MsgBuffer`/`MsgLen`. `nsp_message_out()` writes buffered messages through `nsp_xfer()` while polling for more message-out REQ signals.

Control flow/state: called by `nspintr()` in message phases. State is the active command's `nsp_hw_data::MsgBuffer` and `MsgLen`; no external persistence.

Dependencies/integration: depends on `nsp_negate_signal()`, `nsp_expect_signal()`, `nsp_xfer()`, indexed I/O helpers, SCSI message constants, and direct inclusion into `nsp_cs.c`.

Risks/test signals: timing-sensitive ACK/REQ sequencing and bounded message buffer behavior. Test IDENTIFY/SDTR message-out, SDTR and command-complete message-in, disconnect handling, and maximum message length.
