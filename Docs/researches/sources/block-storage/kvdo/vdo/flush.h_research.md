# File Research: sources/block-storage/kvdo/vdo/flush.h

## Purpose
Declares flush request state and flusher APIs.

## Main Structure
- `struct vdo_flush`: completion object, list of covered bios, wait queue entry, and flush generation.

## API
- Lifecycle: `vdo_make_flusher()`, `vdo_free_flusher()`.
- Query/debug: `vdo_get_flusher_thread_id()`, `vdo_dump_flusher()`.
- Operation: `vdo_launch_flush()`, `vdo_complete_flushes()`.
- Admin state: `vdo_drain_flusher()`, `vdo_resume_flusher()`.

## Integration
Used by the DM target map path for flush bios and by suspend/resume administrative flows.
