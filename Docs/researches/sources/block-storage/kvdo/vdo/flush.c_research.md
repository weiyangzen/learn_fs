# File Research: sources/block-storage/kvdo/vdo/flush.c

## Purpose
Implements VDO flush generation tracking and flush bio completion. It coordinates logical zones, packer flushing, pending flush generations, backing-device submission, allocation-failure handling, and flusher drain/resume.

## Main Behavior
- `vdo_make_flusher()` creates a flusher tied to the packer thread and preallocates a spare `vdo_flush`.
- `vdo_launch_flush()` captures incoming flush bios into a `vdo_flush`; if allocation fails, it queues bios and uses/reuses the spare when possible.
- `flush_vdo()` assigns a new flush generation, queues it for notification, and starts notifying zones if idle.
- Notification walks logical zones, increments each zone generation, then increments the packer generation.
- `vdo_complete_flushes()` completes pending flushes when all logical zones have advanced past that generation.
- Completion forwards original bios to the backing device using selected bio queue rotation and counts acknowledged/outgoing flushes.
- Drain waits for no pending flushes and no queued waiting flush bios.

## Dependencies
Uses admin-state machinery, logical zones, packer, read-only notifier, VDO completions, wait queues, bio lists, thread config, and io submission.

## Invariants
Flusher callbacks assert execution on the flusher/packer thread. Flush generation completion must happen in order via `first_unacknowledged_generation`.
