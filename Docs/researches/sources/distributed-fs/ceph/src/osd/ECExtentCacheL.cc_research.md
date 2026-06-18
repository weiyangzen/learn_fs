# sources/distributed-fs/ceph/src/osd/ECExtentCacheL.cc

## Purpose

Implements the legacy intrusive extent cache used by `ECCommonL::RMWPipeline`. It tracks unstable extents for ordered overlapping partial overwrites, pins extents to write operations, returns cached RMW read data, and releases extents when the owning write completes.

## Important APIs, Types, and Functions

Important methods are `extent::_link_pin_state`, `_unlink_pin_state`, `unlink`, `link`, `move`, `remove_and_destroy_if_empty`, `get_or_create`, `get_if_exists`, `object_extent_set::get_containing_range`, `reserve_extents_for_rmw`, `get_remaining_extents_for_rmw`, `present_rmw_update`, and `print`. The implementation uses `object_extent_set::traverse_update()` from the header for splitting, replacing, and pin-updating interval fragments.

## Control Flow and Data Flow

`reserve_extents_for_rmw()` opens or finds the object extent set, walks each write range, pins all written extents to the current write pin, and returns the subset of requested reads that were missing from cache. `get_remaining_extents_for_rmw()` walks already pinned/present extents and builds an `extent_map` from cached buffer slices. `present_rmw_update()` fills or replaces buffer data for extents after transaction generation. Releasing a pin unlinks and destroys every extent owned by that pin, then deletes an empty per-object cache.

## State and Persistence Behavior

State is entirely in memory: `per_object_caches` owns `object_extent_set` nodes, each set owns intrusive `extent` nodes, and each extent also belongs to exactly one `pin_state` list. A present extent stores a `bufferlist`; a pending extent has no buffer. No data is written to disk by this class.

## Dependencies and Integration Points

It depends on `ECExtentCacheL.h`, Boost intrusive sets/lists, Ceph `bufferlist`, `extent_set`, and `extent_map`. `ECCommonL::RMWPipeline` is the primary caller: it opens write pins, reserves read/write extents, reads cache misses remotely, presents generated writes, and releases pins when commits finish or on interval change.

## Risks and Edge Cases

Intrusive ownership invariants are strict: every extent must be linked into one object set and one pin list, and unlink/move temporarily violates the two-link invariant only in controlled code. `traverse_update()` may split head/tail fragments around update ranges, so off-by-one or buffer length mismatches would corrupt cached data. `get_remaining_extents_for_rmw()` asserts extents are present and pinned by a write, so callers must pass exactly `to_read - remote_read`.

## Test Signals

Test reserving empty ranges, first-write misses, overlapping writes that move pin ownership, partial overlap split into head/middle/tail, cache hit reads after `present_rmw_update()`, release deleting empty object sets, print formatting, and assertion/sanitizer coverage for pin release on normal finish and `on_change()`.
