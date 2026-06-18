# sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_core.h

## Purpose
This header defines the firmware mailbox protocol contract for miXart. It enumerates message IDs, declares request/response structures exchanged with embedded firmware, defines clock/audio/stream format constants, and exports mailbox, IRQ, and reset functions implemented in `mixart_core.c`.

## Important APIs, types, and functions
`enum mixart_message_id` names connector, console, physical I/O, stream, system, service, and clock messages. `struct mixart_msg` is the generic message envelope used by all send APIs. The many packed structs map directly to firmware payloads: connector enumeration and audio info, streaming group creation/deletion, stream/group start-stop requests, timer notifications, clock properties, stream format parameters, output/input level messages, physical I/O enumeration, and stream level controls.

The exported functions are `snd_mixart_init_mailbox`, `snd_mixart_exit_mailbox`, `snd_mixart_send_msg`, `snd_mixart_send_msg_wait_notif`, `snd_mixart_send_msg_nonblock`, `snd_mixart_interrupt`, `snd_mixart_threaded_irq`, and `snd_mixart_reset_board`.

## Control flow
There is no executable control flow, but the structure definitions drive runtime message flow. Setup uses system and connector messages to enumerate hardware; PCM open/close uses stream group messages; prepare and clock setup use clock and stream-parameter messages; trigger uses stage start/stop messages; mixer controls use physical I/O and stream-level messages; IRQ handling decodes service timer and trace messages.

## State and persistence behavior
The header encodes firmware-visible state rather than owning state directly. Packed payloads preserve binary layout across host/firmware communication. `MIXART_MAX_TIMER_NOTIFY_STREAMS` is derived from `MSG_DEFAULT_SIZE` to keep timer notifications inside the fixed mailbox buffer.

## Dependencies and integration points
It depends on `struct mixart_uid` and constants from `mixart.h` being visible before inclusion in implementation files. It is included by main, core, firmware, and mixer sources and is the shared ABI with firmware.

## Risks and edge cases
Because structs are packed firmware ABI, changing field order, width, signedness, or maximum counts can break hardware communication. Endianness is handled in mailbox copy paths, so every payload must remain composed of 32-bit-aligned firmware words unless the copy logic changes. The timer-notification size calculation protects the default mailbox buffer and should be rechecked if stream structures grow.

## Test signals
Build tests catch missing declarations; runtime tests should exercise every message family: firmware enumeration, stream creation/deletion, clock setting, format setting, stage start/stop, timer notifications, and mixer level updates. Cross-endian builds are important because payload byte-swapping depends on these definitions.
