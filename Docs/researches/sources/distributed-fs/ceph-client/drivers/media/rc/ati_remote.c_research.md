<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ati_remote.c -->
# sources/distributed-fs/ceph-client/drivers/media/rc/ati_remote.c

Purpose: USB driver for ATI/X10 RF remote receivers, exposing non-mouse remote buttons through rc-core scancodes and optional pointer/mouse-like events through the input subsystem.

Important APIs and functions: module parameters are `channel_mask`, `debug`, `repeat_filter`, `repeat_delay`, and `mouse`. Device identity and keymap selection use `ati_remote_table`, `struct ati_receiver_type`, and `get_medion_keymap`. Runtime state is `struct ati_remote`. Main functions include `ati_remote_open/close`, input and rc open/close wrappers, `ati_remote_sendpacket`, `ati_remote_initialize`, `ati_remote_input_report`, interrupt callbacks `ati_remote_irq_in/out`, buffer allocation/free, input/rc initialization, `ati_remote_probe`, and `ati_remote_disconnect`.

Control flow: probe validates two interrupt endpoints, allocates URBs/coherent buffers and an rc device, detects model-specific keymap, initializes USB interrupt URBs and sends two hardware init packets, registers the rc device, optionally registers an input mouse device, and stores driver data. On first rc/input open it submits the IN URB; last close kills it. Each input packet is validated by length/header/checksum/channel, masked by `channel_mask`, decoded into either mouse events, scrollwheel repeats, or rc-core keydown/keyup events. The IN URB resubmits itself after each successful packet.

State and persistence: state is in `struct ati_remote`: URBs, coherent buffers, endpoint descriptors, rc/input device pointers, duplicate/repeat timing, acceleration timing, names/phys paths, wait queue, send flags, and open-user count. No persistent storage exists; remote channel configuration is external to the driver.

Dependencies and integration points: depends on USB input helpers, wait queues/jiffies, mutexes, and rc-core. Integrates with rc keymaps such as ATI X10, Medion variants, and SnapStream Firefly, plus the input subsystem for pointer events.

Risks: `ati_remote_alloc_buffers` returns failure on partial allocation but cleanup must tolerate NULL members, which current free paths do. Duplicate filtering is heuristic and intentionally bypasses rc-core repeat handling to avoid regressions. The `mouse` module parameter is read-only after load. Channel masks use one-based bit numbering in user-facing documentation but zero-based remote numbers internally.

Test signals: probe for all USB IDs, Medion descriptor-based keymap selection, open/close reference counting across rc and mouse users, checksum/channel filtering, repeat behavior, pointer acceleration, disconnect while open, and module parameter coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/rc/ati_remote.c -->
