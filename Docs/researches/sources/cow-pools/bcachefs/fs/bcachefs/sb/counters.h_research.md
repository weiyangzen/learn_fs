# File Research: sources/cow-pools/bcachefs/fs/bcachefs/sb/counters.h

This header declares persistent counter APIs and event accounting macros.

Key elements:
- Superblock-to-CPU and CPU-to-superblock synchronization declarations.
- Counter init/exit/reset and recent-counter text rendering declarations.
- Counter ioctl declaration.
- Exports counter names, flags, stable map, and superblock field ops.
- Defines `event_inc`, `event_add`, `event_trace`, `event_add_trace`, and `event_inc_trace`.

Important invariant:
- `event_inc()` is only valid for `TYPE_COUNTER` counters and `event_add()` is only valid for `TYPE_SECTORS`; compile-time checks enforce the expected type.
