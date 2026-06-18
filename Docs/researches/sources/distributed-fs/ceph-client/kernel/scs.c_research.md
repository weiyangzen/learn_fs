# sources/distributed-fs/ceph-client/kernel/scs.c

## Purpose

`kernel/scs.c` implements generic Shadow Call Stack allocation and lifetime support for tasks. It allocates per-task shadow stacks from vmalloc memory, keeps a small per-CPU cache for interrupt-safe freeing, accounts memory usage in VM statistics, integrates with KASAN poisoning, and verifies/records usage during release when debug stack usage is enabled.

## Important APIs, Types, and Functions

The file exports or defines `dynamic_scs_enabled` for `CONFIG_DYNAMIC_SCS`, `scs_alloc()`, `scs_free()`, `scs_init()`, `scs_prepare()`, and `scs_release()`. Internal helpers include `__scs_account()`, `__scs_alloc()`, `scs_cleanup()`, and `scs_check_usage()`.

The main state is `static DEFINE_PER_CPU(void *, scs_cache[NR_CACHED_SCS])`, with `NR_CACHED_SCS` set to 2 to mirror the vmap stack cache depth. Task integration uses `task_scs(tsk)` and `task_scs_sp(tsk)`, and stack integrity relies on `__scs_magic(s)`, `SCS_END_MAGIC`, and `task_scs_end_corrupted()`.

## Control Flow

Allocation begins in `scs_prepare()`, which exits early if `scs_is_enabled()` is false. Otherwise it calls `scs_alloc()`. `__scs_alloc()` first tries to pop a stack from the current CPU cache with `this_cpu_xchg()`, unpoisons and zeros it when found, and falls back to `__vmalloc_node_range()` with `GFP_SCS` on cache miss. `scs_alloc()` resets the KASAN tag, writes the end magic, poisons the vmalloc area to catch accidental accesses, and increments `NR_KERNEL_SCS_KB` for the allocation's NUMA node.

Freeing begins in `scs_release()`, which ignores disabled or empty task SCS state, warns on end-magic corruption, optionally records highest observed usage, and calls `scs_free()`. `scs_free()` decrements accounting and tries to insert the stack into a per-CPU cache using `this_cpu_cmpxchg()`. If the cache is full, it unpoisons the vmalloc area and uses `vfree_atomic()` because release can happen in interrupt context.

CPU hotplug cleanup is registered by `scs_init()` with `cpuhp_setup_state()`. `scs_cleanup()` drains another CPU's cache with regular `vfree()` and clears slots when that CPU is being prepared or torn down by the hotplug state callback.

## State and Persistence

The durable task state is the shadow-stack base and current SCS stack pointer stored in `task_struct`. Cached freed stacks persist per CPU until reused or hotplug cleanup. VM accounting persists through `NR_KERNEL_SCS_KB`. The static `highest` value in `scs_check_usage()` tracks the largest observed shadow-stack usage for debug logging.

## Dependencies and Integration Points

The implementation depends on `linux/scs.h`, vmalloc, KASAN vmalloc poisoning/unpoisoning, NUMA page accounting through `vmalloc_to_page()` and `mod_node_page_state()`, CPU hotplug, task lifecycle hooks that call `scs_prepare()` and `scs_release()`, and architecture/compiler SCS support that consumes `task_scs_sp()`.

## Risks and Edge Cases

The most sensitive behavior is lifetime and context: `scs_free()` must not sleep, so cache insertion and `vfree_atomic()` are required. Reused cached stacks must be unpoisoned, zeroed, retagged, then poisoned again in the right order. Accounting assumes `vmalloc_to_page(s)` succeeds for SCS allocations. Corruption detection only happens on release. Hotplug cleanup must not race with cache users on the target CPU outside the CPU hotplug lifecycle.

## Test Signals

Useful tests include task fork/exit with SCS enabled and disabled, allocation failure returning `-ENOMEM`, cache reuse on repeated short-lived tasks, cache overflow falling back to `vfree_atomic()`, CPU hotplug draining cached stacks, KASAN reports for accidental SCS access, end-magic corruption warnings, and `CONFIG_DEBUG_STACK_USAGE` highest-usage logging.
