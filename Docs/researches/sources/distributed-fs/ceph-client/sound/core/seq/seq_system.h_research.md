# sources/distributed-fs/ceph-client/sound/core/seq/seq_system.h

## Purpose
`seq_system.h` declares the system client interfaces and provides convenience macros for broadcasting ALSA sequencer client, port, and UMP lifecycle events.

## Important APIs, Types, and Functions
- `snd_seq_system_broadcast()` and `snd_seq_system_notify()` are the exported event paths.
- `notify_event()` wraps normal broadcast calls.
- `snd_seq_system_ump_notify()` reuses the broadcast layout for UMP endpoint/function-block notifications.
- Macros such as `snd_seq_system_client_ev_client_start()` and `snd_seq_system_client_ev_port_exit()` encode standard lifecycle event types.
- Declares system client init/done functions.

## Control Flow
Callers use macros when clients or ports start, exit, or change. UMP code calls the inline notification helper with a client id and block id. The implementation in `seq_system.c` fills the event header and dispatches via the system client.

## State and Persistence
The header holds no state; it exposes the notification contract.

## Dependencies and Integration Points
Includes `<sound/seq_kernel.h>`. Used by client manager, port management, UMP client code, and any sequencer component emitting lifecycle notifications.

## Risks
The UMP helper relies on binary compatibility between `struct snd_seq_ev_ump_notify` and `struct snd_seq_addr` fields used by the broadcast path. Macro use hides the atomic flag, always using non-atomic broadcasts for normal lifecycle events.

## Test Signals
Compile-time layout assumptions for UMP notifications and runtime tests that lifecycle macros reach announce-port subscribers with the expected event type/address fields.
