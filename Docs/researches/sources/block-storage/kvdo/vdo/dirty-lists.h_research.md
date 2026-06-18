# File Research: sources/block-storage/kvdo/vdo/dirty-lists.h

## Purpose
Declares the opaque dirty-list tracker used for age-based writeback/expiry.

## API
- `vdo_dirty_callback`: callback invoked with expired elements and context.
- `vdo_make_dirty_lists()`: allocate tracker.
- `vdo_set_dirty_lists_current_period()`: one-time initial period setup.
- `vdo_add_to_dirty_lists()`: add or move a list entry by old/new dirty period.
- `vdo_advance_dirty_lists_period()`: advance current period and expire old lists.
- `vdo_flush_dirty_lists()`: expire all outstanding dirty entries.

## Integration
Designed for intrusive Linux `list_head` entries owned by caller structures.
