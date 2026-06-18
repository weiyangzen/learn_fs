# sources/distributed-fs/ceph/src/librados/snap_set_diff.cc

## Purpose
This file implements `calc_snap_set_diff()`, which computes the object byte ranges that differ between two snapshots from a librados `snap_set_t`. It also reports the end snapshot object's size/existence, the clone snapshot id covering the end point, and whether the whole object must be treated as changed.

## Important APIs, Types, and Functions
The sole exported function is `calc_snap_set_diff(CephContext*, const librados::snap_set_t&, snap_t start, snap_t end, interval_set<uint64_t> *diff, uint64_t *end_size, bool *end_exists, snap_t *clone_end_snap_id, bool *whole_object)`. It walks `snap_set.clones`, interprets HEAD as the interval `[seq + 1, SNAP_HEAD]`, interprets non-HEAD clones from their `snaps` vector, and uses each clone's `size` and `overlap` vector to build the changed extents.

## Control Flow
The function initializes all outputs and scans clones in order. It skips clones whose effective snapshot interval ends before `start`. When it first reaches the start position, it records the start size or, if the object did not exist at `start`, inserts the whole current clone size into `diff`. If `end` falls inside the current clone interval, it sets `end_size`, `end_exists`, and `clone_end_snap_id`, then returns with the accumulated diff. If `end` is after the current clone, it compares the current clone to the next clone: it starts with a maximal interval up to the larger relevant size boundary, erases overlap extents, and unions the resulting intervals into `diff`. Truncation below the start size can erase ranges that should no longer count as changed.

If a non-HEAD clone has an empty `snaps` vector, the function cannot derive an interval, clears `diff`, sets `whole_object`, and returns. If the scan runs out before reaching `end`, it clears the diff and, if the object existed at `start`, marks `[0,start_size)` as changed because the object no longer exists at `end`.

## State and Persistence Behavior
The function is pure with respect to Ceph storage. It mutates only caller-provided output objects. Its result is derived from persisted object snapset metadata supplied by the caller and is used to answer diff-like API queries.

## Dependencies and Integration Points
It depends on `librados::snap_set_t`, `interval_set`, Ceph debug logging, and snapshot id conventions including `SNAP_HEAD`. It integrates with librados snap listing/diff consumers that need changed extents without reading all object data.

## Risks and Test Signals
Risks are off-by-one snapshot interval interpretation, trimmed snapshot behavior where `b < cloneid`, empty snap vectors, truncation across start/end, and incorrect overlap erasure. Tests should include HEAD-only objects, object creation after start, deletion before end, growth, shrink, overlapping clones, empty snaps causing `whole_object`, and end snapshots that land exactly on clone interval boundaries.
