# sources/distributed-fs/ceph-client/include/linux/kstack_erase.h

## Purpose

`kstack_erase.h` declares stack erasure helpers for clearing unused kernel stack contents and tracking stack depth. It is part of the stackleak hardening path. The source was read as a complete 89-line file.

## Important APIs, Types, and Functions

Constants are `KSTACK_ERASE_POISON` and `KSTACK_ERASE_SEARCH_DEPTH`. Under `CONFIG_KSTACK_ERASE`, helpers include `stackleak_task_low_bound()`, `stackleak_task_high_bound()`, `stackleak_find_top_of_poison()`, `stackleak_task_init()`, `stackleak_erase()`, `stackleak_erase_on_task_stack()`, `stackleak_erase_off_task_stack()`, and `__sanitizer_cov_stack_depth()`.

## Control Flow

Task creation initializes the lowest erasable stack pointer. Instrumentation updates stack depth. On syscall/exit-style paths, erase functions find the region above recently used stack and overwrite unused stack memory while preserving `STACK_END_MAGIC` and top-of-stack `pt_regs`.

## State and Persistence Behavior

Per-task `lowest_stack` and optional metrics persist in `task_struct`. Stack poison values persist only until overwritten by later stack usage or erasure.

## Dependencies and Integration Points

It depends on task stack helpers, architecture stacktrace support, linkage/noinstr annotations, and sanitizer coverage instrumentation.

## Risks and Edge Cases

The poison value must point into an unused virtual hole for the platform. Bounds must avoid corrupting stack canaries, `STACK_END_MAGIC`, or `pt_regs`. The poison search depth trades performance against stale stack retention.

## Test Signals

Stackleak selftests, boot tests with hardening enabled, syscall stack erasure checks, metrics validation, architecture stack-bound tests, and disabled-config build coverage are useful.
