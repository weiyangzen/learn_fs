# sources/distributed-fs/ceph-client/mm/kasan/report.c

## Purpose

`report.c` is the common KASAN error reporting engine. It serializes reports, applies boot-time report policy, suppresses recursive KASAN checks while printing, gathers generic object context, and delegates mode-specific details to helpers implemented by the generic, software-tag, or hardware-tag report files.

## Important APIs, Types, and Functions

Key state includes `kasan_flags`, `KASAN_BIT_REPORTED`, `KASAN_BIT_MULTI_SHOT`, `enum kasan_arg_fault`, `kasan_arg_fault`, and `report_lock`. Boot interfaces are `early_kasan_fault()` for `kasan.fault=report|panic|panic_on_write` and `kasan_set_multi_shot()` for `kasan_multi_shot`. KUnit-only helpers `kasan_save_enable_multi_shot()`, `kasan_restore_multi_shot()`, `kasan_kunit_test_suite_start()`, and `kasan_kunit_test_suite_end()` adjust reporting behavior during sanitizer tests. The public report entry points are `kasan_report_invalid_free()`, `kasan_report()`, optional `kasan_report_async()`, and `kasan_non_canonical_hook()`.

## Control Flow

Normal memory-access reporting enters `kasan_report()`, saves/restores user access state, rejects reports if software-mode suppression or one-shot gating says no, calls `start_report()`, fills `struct kasan_report_info`, calls `complete_report_info()`, prints the report, then calls `end_report()`. Invalid frees use `kasan_report_invalid_free()` with a non-access report type and bypass the software suppression check because invalid free is an allocator event rather than a poisoned-memory load. `complete_report_info()` finds the first bad address, slab/cache/object, allocation size, and fixed bug type for invalid or double frees, then calls `kasan_complete_mode_report_info()` to classify mode-specific access bugs and fill stack tracks. `print_report()` emits the error header, tag metadata when available, address/object/page/stack descriptions, and surrounding metadata bytes. Hardware-tag async faults use `kasan_report_async()` and can only print a conservative invalid-access report with no address details.

## State and Persistence Behavior

Reporting state is runtime-only. `kasan_flags` persists across the booted kernel to enforce one-shot behavior unless `kasan_multi_shot` or KUnit enables repeated reports. `kasan_arg_fault` is set during early boot and becomes read-only after init. `report_lock` serializes console output; `current->kasan_depth` or hardware tag-check suppression prevents recursion while report code reads poisoned areas. Reports taint the kernel with `TAINT_BAD_PAGE`, can trigger `check_panic_on_warn()`, and may panic depending on `kasan.fault`.

## Dependencies and Integration Points

This file depends on slab metadata (`kasan_addr_to_slab()`, `nearest_obj()`), shadow/tag helpers (`kasan_find_first_bad_addr()`, `kasan_get_alloc_size()`, `kasan_metadata_fetch_row()`, `kasan_print_tags()`), stack depot, vmalloc and module address helpers, lockdep, ftrace warning handling, KUnit, and `trace_error_report_end(ERROR_DETECTOR_KASAN, ...)`. It is the central integration point between compiler/hardware KASAN checks and human-readable kernel diagnostics.

## Risks and Edge Cases

The highest risks are recursive faults during reporting, deadlocks while printk touches poisoned memory, misleading classification when tag-based stack-ring evidence is stale, and address decoding for non-canonical pointers. The code deliberately uses one-shot reporting by default to avoid flooding after memory corruption. `panic_on_write` treats invalid frees as writes because allocator metadata is being modified.

## Test Signals

Useful signals include KASAN KUnit tests with multi-shot enabled, boot tests for `kasan.fault` and `kasan_multi_shot`, invalid-free and double-free reports, software-mode suppressed sections around slab metadata, hardware-tag async fault reports, stack/object/page/vmalloc metadata in dmesg, and tracepoint emission for KASAN reports.
