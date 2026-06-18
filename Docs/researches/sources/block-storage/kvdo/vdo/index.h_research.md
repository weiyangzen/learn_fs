# File Research: sources/block-storage/kvdo/vdo/index.h

Internal declarations for the UDS index engine.

Key responsibilities:
- Defines `index_callback_t`.
- Defines `struct index_zone` with open/writing chapters and per-zone virtual chapter range.
- Defines `struct uds_index`, including layout, volume index, volume, zones, chapter counters, save flags, chapter writer, callback, triage queue, and flexible array of zone queues.
- Defines request stages: triage, index, and message.
- Declares lifecycle, save, storage replacement, stats, enqueue, and idle-wait functions.

Dependencies:
- Includes layout/session/open-chapter/volume/volume-index headers.

Notable risks:
- `struct uds_index` exposes many mutable fields across modules; synchronization contracts are mostly implicit in queue/thread ownership.
- `zone_queues[]` is a flexible array; allocation must include space for `zone_count` queue pointers.
