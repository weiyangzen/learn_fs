# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/map_fixed_noreplace.c

## Purpose

`map_fixed_noreplace.c` validates `MAP_FIXED_NOREPLACE`: mappings must fail if any requested page overlaps an existing VMA and must succeed when merely adjacent.

## Important APIs, Types, and Functions

The file uses `mmap()`, `munmap()`, `sysconf(_SC_PAGE_SIZE)`, `errno`, and kselftest result helpers. `find_base_addr()` reserves and immediately releases a five-page address window to produce a likely free base. `dump_maps()` prints `/proc/<pid>/maps` for failure diagnostics.

## Control Flow

`main()` finds a base address, verifies a five-page mapping can be established there, unmaps it, maps the middle three pages, then tests five-page, contained, end-overlap, start-overlap, start-adjacent, and end-adjacent requests. Overlap cases must return `MAP_FAILED`; adjacency cases must succeed. The final five-page unmap validates cleanup.

## State and Persistence Behavior

All state is process-local VMA layout. The test intentionally creates and removes anonymous `PROT_NONE` mappings at fixed addresses. It does not write persistent files.

## Dependencies and Integration Points

The test integrates with the mm selftest suite and directly exercises kernel VMA collision detection for `MAP_FIXED_NOREPLACE`, a flag used by allocators and runtimes that require deterministic address placement without clobbering existing mappings.

## Risks and Edge Cases

The free base address is discovered by a reservation/unmap race against the same process, but other mappings could still appear between discovery and testing. The test treats unexpected success on overlap as fatal because that would imply the flag replaced a mapping. It does not assert the exact `errno`, only success/failure behavior.

## Test Signals

There are nine planned pass results covering initial mapping, four overlap failures, two adjacency successes, and final unmap success. Failure paths dump maps to make address layout visible.
