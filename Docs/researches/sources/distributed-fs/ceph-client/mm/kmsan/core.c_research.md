# sources/distributed-fs/ceph-client/mm/kmsan/core.c

## Purpose
`core.c` implements the central KMSAN metadata operations: task context initialization, memory poisoning and unpoisoning, metadata copy/move semantics, origin-chain creation, contiguous metadata validation, and range checking that converts poisoned shadow bytes into user-visible reports.

## Important APIs, Types, And Functions
Global `kmsan_enabled` gates runtime behavior, and `DEFINE_PER_CPU(struct kmsan_ctx, kmsan_percpu_ctx)` provides interrupt-context metadata state. `kmsan_internal_task_create()` initializes a task's KMSAN context and unpoisons thread info. `kmsan_internal_poison_memory()` and `kmsan_internal_unpoison_memory()` set shadow/origin state. `kmsan_save_stack_with_flags()` stores origin stacks in stack depot with extra bits for depth and UAF status. `kmsan_internal_memmove_metadata()` copies shadow/origin metadata using memmove ordering. `kmsan_internal_chain_origin()` creates chain-origin stack-depot records. `kmsan_internal_check_memory()` scans a range for poisoned bytes and reports contiguous same-origin regions. `kmsan_metadata_is_contiguous()` validates that a logical range maps to one contiguous metadata range or is entirely untracked.

## Control Flow
Poisoning saves a stack with optional UAF metadata and writes shadow bytes to `0xff` plus matching origin slots. Unpoisoning writes zero shadow bytes and clears origin slots only when the corresponding shadow group is fully zero. Metadata memmove first looks up destination metadata; if the source is untracked it unpoisons the destination, otherwise it copies shadow byte-by-byte in forward or backward order and chains origins for poisoned bytes. Memory checking walks page-sized chunks, groups consecutive poisoned bytes by origin, and calls `kmsan_report()` whenever the origin changes or an untracked/unpoisoned gap ends a group.

## State And Persistence
The file persists global enable state and per-CPU contexts. Memory initialization state is encoded outside this file in shadow and origin pages, while origin stack traces persist in stack depot. Origin chains carry extra bits for maximum chain depth and whether the origin represents use-after-free.

## Dependencies And Integration Points
It depends on `kmsan_get_metadata()` and `kmsan_get_shadow_origin_ptr()` from `shadow.c`, reporting from `report.c`, context definitions from `linux/kmsan_types.h`, stack depot/stacktrace APIs, vmalloc address translation, and page metadata maintained by KMSAN initialization and hooks. It is called by compiler instrumentation, allocator hooks, page hooks, and explicit checks in `hooks.c`.

## Risks
The implementation assumes metadata contiguity for bulk operations; violating that assumption triggers diagnostic output and can make reports unreliable. Origin slot alignment is delicate because one origin covers `KMSAN_ORIGIN_SIZE` bytes. Origin chaining can allocate, so entry points must avoid recursion with runtime guards. A failed stack-depot save can return zero, which intentionally suppresses reports for that origin.

## Test Signals
KUnit tests cover uninitialized kmalloc/page/stack data, UAF origins, function-parameter propagation, `kmsan_check_memory()`, memcpy alignment and origin-gap handling, long origin chains, stackdepot roundtrips, and unpoisoning behavior. Runtime warning paths in `kmsan_metadata_is_contiguous()` are important negative signals.
