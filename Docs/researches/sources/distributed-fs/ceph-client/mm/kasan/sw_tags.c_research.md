# sources/distributed-fs/ceph-client/mm/kasan/sw_tags.c

## Purpose

`sw_tags.c` is the software tag-based KASAN runtime. It initializes per-CPU tag pseudo-random state, checks instrumented memory accesses by comparing pointer tags against shadow tags, exposes HWASAN compiler callbacks, and forwards mismatches to common KASAN reporting.

## Important APIs, Types, and Functions

Important state is per-CPU `prng_state`. Main functions are `kasan_init_sw_tags()`, `kasan_random_tag()`, `kasan_check_range()`, `kasan_byte_accessible()`, fixed-size `__hwasan_load/store*_noabort` callbacks, `__hwasan_loadN_noabort()`, `__hwasan_storeN_noabort()`, `__hwasan_tag_memory()`, and `kasan_tag_mismatch()`.

## Control Flow

Initialization seeds each CPU PRNG from cycles, initializes shared tag state through `kasan_init_tags()`, enables KASAN, and logs stacktrace status. Access checking ignores zero-size ranges, detects range wraparound, bypasses native kernel tag `KASAN_TAG_KERNEL`, strips tags, validates metadata coverage, then walks every shadow granule touched by the access. Any tag mismatch calls `kasan_report()` and returns the inverse of whether a report was emitted. HWASAN callbacks are thin wrappers around `kasan_check_range()` or `kasan_poison()`.

## State and Persistence Behavior

Only PRNG state is owned here, and it is per-CPU runtime state. Memory tags persist in shadow memory via `kasan_poison()` and `kasan_unpoison()` from `shadow.c`. The random generator intentionally trades cryptographic strength for low overhead and probabilistic coverage.

## Dependencies and Integration Points

This file integrates with compiler HWASAN instrumentation, the shared tag stack-ring code in `tags.c`, common reporting in `report.c`, and shadow memory operations in `shadow.c`. It also includes kernel highmem/kmap compatibility handling through the special native kernel tag.

## Risks and Edge Cases

Tag checking is probabilistic and can miss accesses when tags match by chance. Range wraparound is treated as a reportable OOB. Preemption during PRNG update may duplicate tags across contexts, which is accepted by design. Native kernel-tag bypass suppresses false positives but can hide tag mismatches from paths that lose pointer tags.

## Test Signals

Signals include HWASAN load/store callback tests, tag mismatch reports, random-tag distribution smoke tests, native-kernel-tag bypass cases around kmap/page_address style pointers, and `kasan_byte_accessible()` checks for tagged and untagged addresses.
