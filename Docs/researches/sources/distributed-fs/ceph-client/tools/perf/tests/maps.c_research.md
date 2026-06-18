# sources/distributed-fs/ceph-client/tools/perf/tests/maps.c

## Purpose
Tests `struct maps` overlap handling for merging kcore maps around BPF program maps and for inserting maps that split or eclipse existing ranges.

## Important APIs, Types, and Functions
- `struct map_def` holds expected map name/start/end triples.
- `check_maps_cb()`, `failed_cb()`, and `check_maps()` compare actual map rb-tree order, ranges, DSO names, and refcounts against expected arrays.
- `test__maps__merge_in()` validates `maps__merge_in()`.
- `test__maps__fixup_overlap_and_insert()` validates `maps__fixup_overlap_and_insert()`.

## Control Flow
The merge test creates maps for three BPF programs, inserts them, then creates kcore maps. Merging `kcore1` across the whole range should split around BPF maps. Merging hidden `kcore2` should not alter the expected layout. Merging `kcore3` partly hidden by existing maps should add only the new tail range. The fixup test starts with target and next maps, inserts a split map inside target and expects target to be split into two ranges around it, then inserts an eclipse map covering `next_map` and expects `next_map` to be removed.

## State and Persistence
All state is heap-resident maps/DSOs and a `struct maps` object. Refcounts are part of validation; cleanup uses `maps__zput()` and `map__zput()`. No external state is touched.

## Dependencies and Integration Points
Exercises core map insertion, overlap fixup, range splitting, DSO-backed map creation, and test suite registration through `suite__maps` with two test cases.

## Risks and Edge Cases
- Exact refcount value `1` is asserted for each expected map, so ownership changes can fail this test even if ranges are correct.
- The tests use synthetic names/ranges and do not cover every overlap geometry.
- `check_maps()` assumes iteration order matches expected sorted order.

## Test Signals
Passing shows overlap merge and insert APIs preserve protected BPF ranges, split/eclipsed maps correctly, and maintain expected reference ownership.
