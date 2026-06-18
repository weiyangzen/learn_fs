# sources/distributed-fs/ceph-client/mm/kasan/report_generic.c

## Purpose

`report_generic.c` supplies KASAN report helpers for the generic shadow-byte mode. It interprets shadow memory values, extracts slab allocation/free metadata, decodes stack-frame poisoning metadata, and exposes compiler-generated `__asan_report_*_noabort` entry points.

## Important APIs, Types, and Functions

Important functions are `kasan_find_first_bad_addr()`, `kasan_get_alloc_size()`, `kasan_complete_mode_report_info()`, `kasan_metadata_fetch_row()`, `kasan_print_aux_stacks()`, and, under `CONFIG_KASAN_STACK`, `kasan_print_address_stack_frame()`. Internal classifiers include `get_shadow_bug_type()`, `get_wild_bug_type()`, and `get_bug_type()`. The `DEFINE_ASAN_REPORT_LOAD/STORE` macros export fixed-size load/store report shims plus `__asan_report_load_n_noabort()` and `__asan_report_store_n_noabort()`.

## Control Flow

When common reporting asks for generic details, `kasan_find_first_bad_addr()` walks shadow bytes from the access start until it finds poison. `kasan_get_alloc_size()` scans object shadow bytes, treating zero as a full valid granule, 1..7 as a partial final granule, and poison as the end or an uncomputable freed object. `kasan_complete_mode_report_info()` classifies the bug from shadow values and copies alloc/free stack tracks from slab-side KASAN metadata. Stack reports parse compiler frame descriptions by finding `KASAN_STACK_LEFT`, validating `KASAN_CURRENT_STACK_FRAME_MAGIC`, and printing object ranges inside the frame.

## State and Persistence Behavior

This file owns no long-lived storage. It reads persistent runtime state from KASAN shadow memory, slab alloc/free metadata, and stack depot handles. Stack-depot handles are retained by allocation metadata elsewhere; this file only copies or prints them.

## Dependencies and Integration Points

It integrates with `report.c` through the mode helper API and with compiler ASAN instrumentation through the exported report symbols. It depends on `kasan_mem_to_shadow()`, `addr_has_metadata()`, shadow poison constants such as `KASAN_SLAB_REDZONE`, `KASAN_SLAB_FREE_META`, stack depot, slab metadata, current task stack layout, and arch stack-growth assumptions.

## Risks and Edge Cases

Shadow bytes can be racy with buggy kernel writes, so some classifications are best-effort. Freed objects can return allocation size 0, causing common code to fall back to cache object size. Stack-frame decoding is only supported for the current task's own stack and assumes the compiler frame description format remains stable.

## Test Signals

Signals include generic KASAN KUnit coverage for OOB, UAF, invalid free, stack OOB, alloca OOB, global OOB, vmalloc OOB, auxiliary work stacks, ASAN compiler callbacks, and reports whose metadata rows match expected shadow poison bytes.
