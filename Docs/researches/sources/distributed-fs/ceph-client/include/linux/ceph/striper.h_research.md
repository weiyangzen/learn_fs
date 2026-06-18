# sources/distributed-fs/ceph-client/include/linux/ceph/striper.h

## Purpose

`striper.h` declares helpers that map logical Ceph file byte ranges to RADOS object extents and map object extents back to file ranges according to a `ceph_file_layout`.

## Important APIs, Types, and Functions

Types include `ceph_object_extent`, callback type `ceph_object_extent_fn_t`, and `ceph_file_extent`. APIs are `ceph_calc_file_object_mapping()`, `ceph_file_to_extents()`, `ceph_iterate_extents()`, `ceph_extent_to_file()`, `ceph_get_num_objects()`, plus helpers `ceph_object_extent_init()` and `ceph_file_extents_bytes()`.

## Control Flow

Callers provide a layout and file offset/length. The striper computes object number, object offset, and contiguous length for each stripe/object piece, optionally allocates/list-links extents, invokes a callback for each mapped stripe unit, or reverses an object extent into file extents.

## State and Persistence Behavior

The header owns no state. `ceph_object_extent` instances are caller-allocated list nodes; mapping results reflect persistent file layout fields.

## Dependencies and Integration Points

It depends on list/types and forward-declared `ceph_file_layout` from `ceph_fs.h`. It integrates with CephFS read/write paths and OSD request construction.

## Risks and Edge Cases

Layout validation must happen before mapping. Arithmetic over large offsets, lengths, stripe counts, and object sizes can overflow if implementations are careless. Callback allocation failure must unwind partially built extent lists.

## Test Signals

Test stripe-unit boundaries, multi-object ranges, zero-length behavior, large offsets, reverse mapping, total byte accounting, invalid layout rejection by callers, and callback failure unwinding.
