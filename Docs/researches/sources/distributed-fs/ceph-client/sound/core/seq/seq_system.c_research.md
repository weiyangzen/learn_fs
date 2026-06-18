# sources/distributed-fs/ceph-client/sound/core/seq/seq_system.c

## Purpose
`seq_system.c` creates and manages the ALSA sequencer internal "System" client. It provides the timer-control port used to manipulate queues and the announce port used to broadcast client/port lifecycle and UMP notifications.

## Important APIs, Types, and Functions
- `snd_seq_system_client_init()` creates the kernel system client and its Timer and Announce ports.
- `snd_seq_system_client_done()` deletes the system client.
- `snd_seq_system_broadcast()` broadcasts fixed system events to announce subscribers.
- `snd_seq_system_notify()` sends a system event directly to a client/port.
- `event_input_timer()` forwards timer-port events to `snd_seq_control_queue()`.
- `sys_announce_subscribe()` and `sys_announce_unsubscribe()` track announce subscription count.

## Control Flow
Initialization creates a kernel client named `System`, then creates a fixed Timer port with write/read/subscription capabilities and an input callback to queue control. It creates a fixed Announce port with read/subscription capabilities and subscription callbacks. Broadcasts are skipped unless the announce port exists and at least one subscriber is present.

## State and Persistence
Static runtime state stores `sysclient`, `announce_port`, and `announce_subscribed`. There is no persistent state. On teardown `sysclient` and `announce_port` are reset before deleting the kernel client.

## Dependencies and Integration Points
Depends on sequencer kernel client APIs, queue control (`seq_queue.c`), and timer event semantics. Client and port lifecycle macros in `seq_system.h` are used by client/port management and UMP endpoint code.

## Risks
`announce_subscribed` is a plain integer and relies on sequencer subscription serialization. Broadcast events are dropped when no subscribers exist, which is intended but relevant for consumers expecting history. Timer-control input must validate queue permissions downstream.

## Test Signals
Test system client initialization failure unwind, timer port queue-control routing, announce subscribe/unsubscribe counts, lifecycle broadcasts to subscribers, direct system notification, and UMP change notifications.
