# sources/distributed-fs/ceph-client/fs/ceph/util.c

## Purpose
`util.c` provides non-inline CephFS helper functions for file layout validation/conversion and mapping Linux open flags or Ceph file modes to required capability bits.

## Important APIs, Types, And Functions
It implements `ceph_file_layout_is_valid()`, `ceph_file_layout_from_legacy()`, `ceph_file_layout_to_legacy()`, `ceph_flags_to_mode()`, and `ceph_caps_for_mode()`. The relevant data structures are `struct ceph_file_layout` and `struct ceph_file_layout_legacy`.

## Control Flow
Layout validation checks nonzero stripe unit/object size, minimum stripe-unit alignment, object-size multiple of stripe unit, and nonzero stripe count. Legacy conversion translates little-endian fields and treats all-zero legacy layout as no pool (`pool_id = -1`). Flag/mode conversion maps VFS access modes to `CEPH_FILE_MODE_*` and then to cap masks.

## State, Persistence, And Dependencies
There is no mutable state. The helpers depend on Linux open flag constants and Ceph protocol/layout definitions.

## Integration Points
Mount, inode fill, layout xattrs, file open, and cap acquisition paths use these helpers to validate layouts and request the correct MDS capabilities for read, write, lazy IO, or directory pins.

## Risks
Incorrect cap mapping can over-request or under-request MDS caps, affecting cache coherency or write permissions. Layout validation must stay aligned with MDS/OSD layout constraints and legacy encoding semantics.

## Test Signals
Test valid and invalid stripe layouts, all-zero legacy layouts, endian conversion, read/write/read-write/directory/lazy open flag mappings, and cap masks consumed by open/write paths.
