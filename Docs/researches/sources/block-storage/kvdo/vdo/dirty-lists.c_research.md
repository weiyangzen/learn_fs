# File Research: sources/block-storage/kvdo/vdo/dirty-lists.c

## Purpose
Implements age-bucketed dirty element tracking. Elements are held in a ring of lists by dirty period and expired via callback when they exceed a maximum age or when all dirty lists are flushed.

## Main Behavior
- `vdo_make_dirty_lists()` allocates a flexible-array structure with `maximum_age` list heads.
- `vdo_set_dirty_lists_current_period()` initializes oldest/current period and ring offset.
- `vdo_add_to_dirty_lists()` moves an element into the correct period bucket, expires it immediately if too old, and ignores updates that do not make the element newly older.
- `vdo_advance_dirty_lists_period()` advances periods and expires buckets as they age out.
- `vdo_flush_dirty_lists()` expires every pending bucket.
- Expired elements are spliced into an `expired` list and passed to the caller callback, which must empty the list.

## Invariants
The callback is required to remove all expired elements. Period advancement expires at most as needed to keep `next_period - oldest_period <= maximum_age`.
