# sources/distributed-fs/ceph-client/include/uapi/sound/asequencer.h

## Purpose
`asequencer.h` defines the ALSA sequencer userspace ABI for MIDI-style event routing, client/port management, subscriptions, queues, timing, UMP notifications, pools, and sequencer ioctls. It is the contract for `/dev/snd/seq` event read/write and control operations.

## Important APIs, Types, and Constants
`SNDRV_SEQ_VERSION` declares the protocol version. Event type constants span system/result, note, controller, timing, queue control, client/port lifecycle, subscription lifecycle, UMP endpoint/block changes, fixed user events, variable-length SysEx/user events, kernel-private events, hardware-specific events, and `SNDRV_SEQ_EVENT_NONE`.

Addressing and event payload types include `struct snd_seq_addr`, `snd_seq_connect`, `snd_seq_ev_note`, `snd_seq_ev_ctrl`, `snd_seq_ev_ext`, `snd_seq_result`, `snd_seq_real_time`, `union snd_seq_timestamp`, `snd_seq_ev_queue_control`, `snd_seq_ev_quote`, `snd_seq_ev_ump_notify`, `union snd_seq_event_data`, `struct snd_seq_event`, and `struct snd_seq_ump_event`. Event flags cover timestamp type, absolute/relative time, fixed/variable/user-memory length, priority, and UMP packets.

Management structures include `snd_seq_system_info`, `snd_seq_running_info`, `snd_seq_client_info`, `snd_seq_client_pool`, `snd_seq_remove_events`, `snd_seq_port_info`, `snd_seq_queue_info`, `snd_seq_queue_status`, `snd_seq_queue_tempo`, `snd_seq_queue_timer`, `snd_seq_queue_client`, `snd_seq_port_subscribe`, `snd_seq_query_subs`, and `snd_seq_client_ump_info`. Ioctls provide protocol query, client ID/info, UMP info, port create/delete/query/set, subscriptions, queue create/delete/status/tempo/timer/client, pool control, event removal, and client/port iteration.

## Control Flow and State
Sequencer flow is event-oriented. A client opens `/dev/snd/seq`, queries its client ID, optionally sets client metadata and pool sizes, creates ports with capabilities/type flags, subscribes port pairs, then writes `snd_seq_event` records or reads delivered events. Timestamped events are queued using tick or real-time queues; direct events use `SNDRV_SEQ_QUEUE_DIRECT`. Queue ioctls create, configure, start/stop, and monitor timing queues.

## State and Persistence Behavior
Kernel sequencer state persists while clients, ports, queues, subscriptions, and pools exist. Event queues, client filters, port attributes, UMP endpoint/block metadata, and queue tempo/timer settings live in kernel memory and are exposed through ioctl structures. `snd_seq_ev_ext` carries a userspace pointer and length for variable data, so data lifetime is tied to the write operation and must be copied safely by the kernel.

## Dependencies and Integration Points
It includes `<sound/asound.h>` for timer IDs, protocol macros, ioctl definitions, and base ALSA types. Integration points include ALSA raw MIDI/UMP clients, MIDI applications, synth drivers, queue/timer infrastructure, and alsa-lib sequencer wrappers.

## Risks and Test Signals
Risks include 32/64-bit pointer ABI in `snd_seq_ev_ext` and quoted events, variable event length validation, queue timestamp mode mistakes, event filter bitmap bounds, and UMP-to-legacy conversion behavior. Tests should cover UAPI compilation, client/port lifecycle ioctls, subscription routing, queue tempo/timer behavior, SysEx variable events, UMP-capable clients, and compat-mode reads/writes.
