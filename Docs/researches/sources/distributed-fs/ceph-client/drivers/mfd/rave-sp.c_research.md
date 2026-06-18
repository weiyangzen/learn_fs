# sources/distributed-fs/ceph-client/drivers/mfd/rave-sp.c

## Purpose
`rave-sp.c` is the serdev MFD core for Zodiac Inflight Innovations RAVE supervisory processor MCUs. It implements framed UART transport, command translation, checksum variants, synchronous command execution, event ACK/notifier delivery, firmware status discovery, and DT child population.

## Important APIs, Types, And Functions
Protocol state is in `struct rave_sp_deframer`, `struct rave_sp_reply`, `struct rave_sp_checksum`, and `struct rave_sp`. Exported APIs are `rave_sp_exec()` and `devm_rave_sp_register_event_notifier()`. Framing helpers include `stuff()`, `rave_sp_write()`, `rave_sp_receive_buf()`, and `rave_sp_receive_frame()`. Variant hooks live in `struct rave_sp_variant_cmds` with legacy, RDU1, and RDU2 implementations.

## Control Flow
Probe reads `current-speed`, opens serdev, configures UART, selects variant data, initializes locks/notifier head, queries status or version commands, logs firmware/bootloader strings, and populates DT children. `rave_sp_exec()` translates a generic command, assigns an atomic ACK ID, installs expected reply under `reply_lock`, writes a stuffed frame with checksum, and waits up to one second. Receive deframes STX/DLE/ETX byte streams, verifies checksum, distinguishes events from replies, ACKs events, and notifies registered consumers.

## State And Persistence
State includes deframer progress, atomic ACK ID, one protected pending reply, notifier list, and firmware string allocations. MCU state is external and command-dependent. No on-disk persistence exists.

## Dependencies And Integration Points
It depends on serdev, OF child population, `linux/mfd/rave-sp.h`, CRC-ITU-T, unaligned helpers, blocking notifiers, and child devices under compatibles `zii,rave-sp-niu`, `zii,rave-sp-mezz`, `zii,rave-sp-esb`, `zii,rave-sp-rdu1`, and `zii,rave-sp-rdu2`.

## Risks
The deframer intentionally drops a frame when a second STX appears before ETX and returns partial consumption, so receive-path changes must respect serdev reentry. `rave_sp_exec()` does not check the return value of `rave_sp_write()`. Reply matching requires code, ACK ID, and minimum payload length; unexpected frames are ignored until timeout. Variant command maps are protocol ABI and easy to break.

## Test Signals
Test byte-stuffing, bad/short/oversized frames, CCITT and 8-bit checksums, command timeout, mismatched ACK IDs, event notification and ACK frames, all variant command translations, firmware status fallback, and concurrent child notifier registration/removal.
