# sources/distributed-fs/ceph-client/net/ceph/striper.c

## Purpose
`striper.c` maps Ceph file byte ranges to RADOS object extents and maps object extents back to file extents according to `struct ceph_file_layout`. It encapsulates stripe unit, stripe count, object size, object set, and object-number arithmetic used by CephFS IO and OSD request construction.

## Important APIs, types, and functions
- `ceph_calc_file_object_mapping()` maps a file offset/length to object number, object offset, and contiguous bytes within the current stripe unit.
- `ceph_file_to_extents()` maps a file range to a sorted list of merged `struct ceph_object_extent` records, allocating new extents through a caller callback and invoking an action callback per stripe-unit segment.
- `ceph_iterate_extents()` repeats the file-to-object walk against an already populated extent list and invokes the action callback for containing extents.
- `ceph_extent_to_file()` reverse maps an object range to one or more file extents.
- `ceph_get_num_objects()` computes the number of objects needed to cover a file size.

## Control flow
`ceph_calc_file_object_mapping()` divides the file offset by stripe unit to get global block number and block offset, divides block number by stripe count to get stripe number and stripe position, divides stripe number by stripes-per-object to get object set number and position, then derives object number and object offset. It caps mapped length to the remainder of the stripe unit.

`ceph_file_to_extents()` loops through the requested file range one stripe unit at a time. For each segment it looks up the last extent for the object number. If the new segment is contiguous with the previous object extent, it extends that record; otherwise it asks the caller to allocate a new extent and inserts it in sorted object order. A final validation pass warns and fails if the list is unsorted or overlapping.

`ceph_iterate_extents()` performs the same mapping loop without allocation; every computed object segment must be contained in the provided list. `ceph_extent_to_file()` computes the number of stripe-unit intersections covered by an object range, allocates that many `ceph_file_extent` records, and reconstructs file offsets from object number, object offset, stripe position, and object set number.

## State and persistence behavior
The file itself is stateless. It computes deterministic mappings from a supplied `ceph_file_layout`. Callers own all extent lists and allocated reverse-mapping arrays.

## Dependencies and integration points
`osd_client.c` uses layout calculation when building object requests from file offsets. CephFS read/write paths depend on these mappings to split file IO into object IO. The file depends on Linux 64-bit division helpers and Ceph layout/type declarations.

## Risks and edge cases
- Layout fields must be valid: zero stripe unit, zero stripe count, or object size not divisible by stripe unit would break division or mapping assumptions.
- Extent merging assumes successive calls map sorted file ranges into a shared object extent list.
- Reverse mapping allocation size depends on `objoff + objlen` and stripe unit math; very large ranges need overflow awareness.
- `ceph_get_num_objects()` has nontrivial remainder logic for partially used final object sets.

## Test signals
Test single-object layouts, multi-object stripe counts, multi-stripe objects, unaligned offsets, ranges crossing stripe-unit boundaries, ranges crossing object boundaries, merge behavior for adjacent object segments, sorted-list validation, reverse mapping round trips, zero-length reverse mapping, and object count calculations at exact period and partial-period boundaries.
