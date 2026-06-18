# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_interval.h

## Purpose
`drbd_interval.h` declares the interval node used by DRBD request and peer-request tracking, plus the public helpers for insertion, removal, membership checks, overlap lookup, and overlap iteration. It is the small data-structure contract behind DRBD's in-flight range conflict detection.

## Important APIs, Types, And Functions
`struct drbd_interval` contains an embedded `rb_node`, start `sector`, augmented subtree `end`, byte `size`, bitfields for `local`, `waiting`, and `completed`, and `partially_in_al_next_enr` for resuming partially successful activity-log admission. Inline helpers are `drbd_clear_interval`, which clears rb-node membership state, and `drbd_interval_empty`, which tests `RB_EMPTY_NODE`. Exported functions are `drbd_insert_interval`, `drbd_contains_interval`, `drbd_remove_interval`, `drbd_find_overlap`, and `drbd_next_overlap`. `drbd_for_each_overlap` wraps the find/next sequence.

## Control Flow
The header does not implement the search algorithms beyond inlines and the iteration macro. Callers initialize an interval, fill `sector` and `size`, insert it into a selected rb root, and later use `drbd_for_each_overlap` to scan conflicting intervals for a target range. The `waiting` flag lets code mark intervals whose owner is sleeping for progress, and `completed` lets conflict detection ignore requests that have already completed but may still be present for cleanup or accounting.

## State And Persistence
Intervals are transient in-memory state embedded in higher-level request objects. `sector` and `size` describe the range, `end` is maintained by the augmented tree implementation, and flags describe request-local conflict/wait status. There is no on-disk persistence in this file, but interval state influences when activity-log updates and replicated writes can proceed.

## Dependencies
The header depends on Linux `types.h` and `rbtree.h`. It is included by `drbd_int.h` so that `struct drbd_request`, `struct drbd_peer_request`, activity-log code, and request code can embed and manipulate intervals.

## Integration Points
The interval API integrates with `drbd_device.read_requests` and `drbd_device.write_requests`, request submission, peer request handling, activity-log functions (`drbd_al_begin_io*`, `drbd_al_complete_io`), and `drbd_wait_misc`. The `partially_in_al_next_enr` field is specifically tied to resuming `drbd_al_begin_io_nonblock` after partial progress.

## Risks
Because this structure is embedded in live I/O objects, caller ordering is critical: the rb node must be cleared before first use, inserted only once, removed before owner free, and protected by the appropriate DRBD lock. `size` is bytes while `sector` and `end` are sectors, so callers must keep 512-byte alignment. The flags are compact bitfields, which is convenient but can hide concurrency assumptions; simultaneous updates without the request lock would be unsafe.

## Test Signals
Build coverage catches struct/API mismatches. Runtime signals include activity-log conflict tests, read/write overlap tests, two-primary conflict tests, request restart behavior after waits, and assertions that interval nodes are empty after completion and teardown. Unit-style interval tests should validate the macro iterates all and only overlapping intervals.
