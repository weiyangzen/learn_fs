# sources/distributed-fs/ceph-client/tools/testing/selftests/mm/mremap_test.c

## Purpose

`mremap_test.c` is a comprehensive `mremap()` functional and performance selftest. It validates alignment constraints, large-region remaps at PTE/PMD/PUD granularities, data preservation, VMA merge behavior, multi-VMA moves, `MREMAP_DONTUNMAP`, userfaultfd-invalid multi-move handling, and optional 1 GiB performance comparisons.

## Important APIs, Types, and Functions

`struct config` captures source alignment, destination alignment, region size, overlap, and destination preamble size. `struct test` adds a name and expected failure. Core helpers are `get_sqrt()`, `is_remap_region_valid()`, `get_mmap_min_addr()`, `is_range_mapped()`, `get_source_mapping()`, `remap_region()`, and `run_mremap_test_case()`. Scenario helpers include `mremap_expand_merge()`, `mremap_expand_merge_offset()`, `mremap_move_within_range()`, `mremap_move_multiple_vmas()`, `mremap_shrink_multiple_vmas()`, `mremap_move_multiple_vmas_split()`, `mremap_move_multi_invalid_vmas()`, and `mremap_move_1mb_from_start()`.

## Control Flow

`main()` parses validation threshold and random seed, precomputes a random byte buffer, builds 15 functional cases and three optional 1 GiB performance cases, and sets the plan to include alignment tests, merge tests, and miscellaneous multi-VMA tests. Each normal test maps a source at a requested non-coincidental alignment, copies a validation pattern, chooses a destination that avoids existing mappings unless overlap is expected, optionally maps a preamble before the destination, times `mremap(MREMAP_MAYMOVE | MREMAP_FIXED)`, verifies moved bytes and preamble bytes, and cleans mappings. Misc tests use `/proc/self/maps` to assert merge or movement behavior across gaps and invalid UFFD-registered VMAs.

## State and Persistence Behavior

All state is anonymous process mappings and an optional userfaultfd. The test reads `/proc/sys/vm/mmap_min_addr` to avoid forbidden low addresses and `/proc/self/maps` for mapping validation. It uses deterministic random data derived from the printed seed.

## Dependencies and Integration Points

It depends on Linux `mremap`, `MAP_FIXED_NOREPLACE`, procfs, and optional `userfaultfd`. It integrates with page table move optimizations, VMA merge logic, destination overwrite semantics, multi-VMA remapping, and data-integrity validation.

## Risks and Edge Cases

The test can map very large virtual ranges up to 2 GiB and optionally validate 1 GiB moves fully when `-t 0` is used. Address search can be slow or fail in crowded address spaces. Some code contains duplicated `goto error` and duplicated comments, but behavior remains clear. UFFD tests skip or partially validate based on permission and syscall support.

## Test Signals

Pass signals include expected xfail for overlapping or misaligned cases, successful data preservation for aligned cases, single-VMA merge after expansion, non-corruption of adjacent ranges, successful multi-VMA move/shrink/split operations, and correct `EFAULT` plus partial movement behavior for UFFD-invalid multi-VMA moves.
