# Group Research: group_236_bcachefs_tools_sources_cow_pools_bcachefs_tools_include_linux_rhasht_586315bd9e93

Scope: `Docs/research_subset_a.md`, source tree `sources/cow-pools/bcachefs-tools`.

This group is a compact user-space Linux-kernel compatibility layer for bcachefs-tools. It provides kernel-like headers, concurrency primitives, block I/O plumbing, allocation helpers, percpu emulation, sysfs/debugfs models, compression/hash APIs, and small utility implementations needed to compile or run kernel-derived bcachefs code outside the kernel.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/rhashtable.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/rhashtable.h

Purpose: Kernel-style resizable hash table API and inline implementation for user-space bcachefs-tools.

Key contents:
- Defines `struct rhash_lock_head` and `struct bucket_table`, including bucket array, random hash seed, walker list, RCU header, and `future_tbl` used during resizing.
- Provides nulls-marker handling, object/key hash helpers, load-factor helpers, bucket selection, and bucket bit-lock operations.
- Implements inline lookup, insert, lookup-insert, remove, replace, and rhlist wrapper operations.
- Supports RCU traversal macros for `rht_for_each*`, `rht_for_each_entry*`, and `rhl_for_each*`.

Behavior and design:
- Buckets steal low pointer bit `BIT(0)` as a lock marker; nulls markers identify chain ends without storing them in buckets.
- Lookups walk current and future tables under RCU and retry when a moved object is detected.
- Insert paths enforce `RHT_ELASTICITY`, return existing objects for duplicate keys, and schedule deferred resize work above load thresholds.
- Removal and replacement handle ongoing resize by walking through `future_tbl`.

Dependencies:
- Uses `linux/rhashtable-types.h`, RCU helpers, bit spinlocks, workqueues, jhash, nulls lists, and kernel-style error pointer APIs.

Research notes:
- This is one of the most complete kernel-derived headers in the group, not a simple stub.
- Correctness depends on the surrounding user-space RCU and workqueue compatibility layers.
- The API surface is broad enough for kernel bcachefs code to use normal rhashtable patterns largely unchanged.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/rhashtable.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/rwsem.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/rwsem.h

Purpose: User-space implementation of Linux read/write semaphores.

Key contents:
- Defines `struct rw_semaphore` around `pthread_rwlock_t`.
- Provides `init_rwsem`, read lock/unlock, write lock/unlock, and trylock helpers.
- `down_read_interruptible()` and `down_read_killable()` always block normally and return `0`.
- Defines cleanup guard helpers for read and write lock scopes.

Behavior and design:
- Maps kernel rwsem semantics to pthread rwlocks.
- Interruptible and killable variants do not observe signals in this environment.
- Intended for API compatibility rather than exact kernel scheduler behavior.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/rwsem.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/scatterlist.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/scatterlist.h

Purpose: Minimal Linux scatterlist data structure and traversal helpers.

Key contents:
- Defines `struct scatterlist` with `page_link`, `offset`, and `length`.
- Provides low-bit encoded chain/end markers through `sg_is_chain`, `sg_is_last`, and `sg_chain_ptr`.
- Implements page assignment, buffer assignment, `sg_next`, `for_each_sg`, chaining, end marking, virtual address access, and table initialization.

Behavior and design:
- Preserves kernel pointer-bit encoding semantics for chain and terminator state.
- Uses `virt_to_page`, `offset_in_page`, and `page_address` compatibility helpers from elsewhere.
- Useful for code that expects kernel scatterlist iteration over page-backed buffers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/scatterlist.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/sched.h

Purpose: User-space substitute for core Linux scheduler/task definitions.

Key contents:
- Defines task state constants, task flags, `TASK_COMM_LEN`, and `MAX_RT_PRIO`.
- Defines `struct task_struct` backed by `pthread_t`, thread function/data, atomic usage count, state, kthread flags, completion, flags, command name, pid, bio list, embedded signal struct, and simple runtime accounting.
- Exposes thread-local `current`.
- Implements task state setters, task refcount helpers, `cond_resched()` no-op, `need_resched()` false, schedule and timeout declarations, I/O schedule wrappers, wake-up declaration, and time helpers.

Behavior and design:
- Emulates enough of the scheduler/task API for bcachefs kernel-derived code.
- Time helpers use `clock_gettime()` for monotonic and realtime values.
- Signal and preemption behavior are simplified elsewhere in the compatibility layer.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/clock.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/sched/clock.h

Purpose: Empty compatibility placeholder.

Key contents:
- File is zero bytes.

Behavior and design:
- Satisfies includes of `<linux/sched/clock.h>` from kernel-derived code.
- No declarations or behavior are provided here.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/clock.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/cputime.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/sched/cputime.h

Purpose: Minimal CPU accounting compatibility shim.

Key contents:
- Defines `task_cputime_adjusted()` inline.
- Always returns `0` for user time and system time.

Behavior and design:
- Avoids implementing scheduler CPU accounting in user space.
- Keeps callers that expect the kernel API compiling.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/cputime.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/debug.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/sched/debug.h

Purpose: Empty compatibility placeholder.

Key contents:
- File is zero bytes.

Behavior and design:
- Satisfies kernel include dependencies for scheduler debug declarations.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/debug.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/mm.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/sched/mm.h

Purpose: Memory-allocation context flag helpers.

Key contents:
- Defines `PF_MEMALLOC` and `PF_MEMALLOC_NOFS`.
- Implements `memalloc_flags_save()` and `memalloc_flags_restore()`.
- Provides `memalloc_noio_save/restore`, `memalloc_nofs_save/restore`, and `memalloc_noreclaim_save/restore`.

Behavior and design:
- Tracks allocation-context flags in `current->flags`.
- Documentation mirrors kernel intent around avoiding IO/FS reclaim recursion.
- Restore implementation clears the provided saved flag mask from `current->flags`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/mm.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/rt.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/sched/rt.h

Purpose: Real-time scheduler compatibility stub.

Key contents:
- Defines `rt_task()`.

Behavior and design:
- `rt_task()` always returns `0`; user-space bcachefs-tools does not model kernel RT scheduling.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/rt.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/signal.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/sched/signal.h

Purpose: Signal state compatibility stubs.

Key contents:
- Defines `fatal_signal_pending()`, `signal_pending()`, and `signal_pending_state()`.

Behavior and design:
- All helpers return `0`.
- Kernel paths that are signal-aware compile, but user-space signal interruption is not modeled through these helpers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/signal.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/sysctl.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/sched/sysctl.h

Purpose: Minimal scheduler sysctl constant shim.

Key contents:
- Defines `sysctl_hung_task_timeout_secs` as `HZ * 10`.

Behavior and design:
- Provides a compile-time value for code expecting the kernel hung-task sysctl.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/sysctl.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/task.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/sched/task.h

Purpose: Empty compatibility placeholder.

Key contents:
- File is zero bytes.

Behavior and design:
- Satisfies includes of `<linux/sched/task.h>`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/task.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/task_stack.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/sched/task_stack.h

Purpose: Empty compatibility placeholder.

Key contents:
- File is zero bytes.

Behavior and design:
- Satisfies includes of `<linux/sched/task_stack.h>`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sched/task_stack.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/semaphore.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/semaphore.h

Purpose: Kernel semaphore type and API declarations.

Key contents:
- Defines `struct semaphore` with raw spinlock, count, and wait list.
- Provides initializer macros and `sema_init()`.
- Declares `down`, interruptible/killable/trylock/timeout variants, and `up`.

Behavior and design:
- Header supplies type layout and declarations; implementation is elsewhere.
- Uses compatibility spinlock and list primitives.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/semaphore.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/seq_buf.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/seq_buf.h

Purpose: Kernel-style sequential string buffer API.

Key contents:
- Defines `struct seq_buf` with buffer pointer, size, length, and read position.
- Implements initialization, clearing, overflow checks, overflow marking, remaining-space query, used-byte query, termination, buffer acquisition, and commit.
- Declares printf, vprintf, user-copy, puts, putc, and human-readable formatting helpers.

Behavior and design:
- Overflow is represented by setting `len > size`.
- `seq_buf_commit()` treats negative byte counts as overflow.
- This is a formatting utility used by tracing/debug/status code.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/seq_buf.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/seq_file.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/seq_file.h

Purpose: Minimal `seq_file` structure definition.

Key contents:
- Defines `struct seq_file` fields for buffer state, offsets, versioning, poll event, associated file, and private data.

Behavior and design:
- This file only supplies data layout for code that implements or consumes seq-style file operations.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/seq_file.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/seqlock.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/seqlock.h

Purpose: Basic sequence counter implementation.

Key contents:
- Defines `seqcount_t`.
- Implements `seqcount_init`, `read_seqcount_begin`, `read_seqcount_retry`, `write_seqcount_begin`, and `write_seqcount_end`.

Behavior and design:
- Readers spin while sequence is odd.
- Uses memory barriers around read and write critical sections.
- Provides seqlock-style consistency without full lock type support.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/seqlock.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/shrinker.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/shrinker.h

Purpose: User-space shrinker interface declarations.

Key contents:
- Defines `struct shrink_control`.
- Defines `SHRINK_STOP`.
- Defines `struct shrinker` with count, scan, optional text callback, tuning fields, list node, and private data.
- Declares allocation, registration, free, run, and init functions.

Behavior and design:
- Used by `slab.h`, `kthread.c`, and allocation paths to retry allocation after memory reclamation callbacks.
- Provides kernel-compatible memory pressure hooks in user space.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/shrinker.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/siphash.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/siphash.h

Purpose: SipHash and HalfSipHash API declarations and optimized inline dispatch.

Key contents:
- Defines `siphash_key_t` and `hsiphash_key_t`.
- Declares aligned and unaligned generic hash functions plus fixed-size helpers.
- Provides `siphash_key_is_zero()`.
- Implements inline `siphash()` and `hsiphash()` dispatch, with constant-size fast paths for 4/8/16/24/32 byte SipHash and 4/8/12/16 byte HalfSipHash inputs.

Behavior and design:
- Uses endian conversion helpers to match kernel semantics.
- Falls back to unaligned implementations when efficient unaligned access is unavailable.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/siphash.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sizes.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/sizes.h

Purpose: Standard Linux size constants.

Key contents:
- Defines `SZ_1` through `SZ_2G` as integer constants.
- Defines `SZ_4G` through `SZ_64T` using `_AC(..., ULL)`.

Behavior and design:
- Pure macro header for readable size expressions in kernel-derived code.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sizes.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/slab.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/slab.h

Purpose: User-space implementation of kernel allocation APIs.

Key contents:
- Defines kmalloc alignment and size constants.
- Implements `kmalloc`, `kzalloc`, `krealloc`, `krealloc_array`, `kmalloc_array`, `kcalloc`, `kvmalloc`, `kvcalloc`, and free aliases.
- Implements page allocation wrappers using aligned allocation.
- Provides minimal `kmem_cache` support for fixed-size object allocation.
- Implements vmalloc/vzalloc and executable vmalloc with `mprotect`.
- Defines VM flag constants and stub mapping helpers.

Behavior and design:
- Allocation retries up to 10 times, calling `run_shrinkers()` between failures.
- `kmalloc()` uses `posix_memalign()` for nonzero sizes with power-of-two alignment capped at `PAGE_SIZE`.
- `krealloc()` copies up to the lesser malloc usable size of old and new blocks.
- Kernel NUMA/node distinctions are ignored.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/slab.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sort.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/sort.h

Purpose: Sorting compatibility API.

Key contents:
- Defines `cmp_int`.
- Declares `sort_r`.
- Implements `sort()` as a wrapper over C library `qsort`.
- Aliases nonatomic sort variants.

Behavior and design:
- Ignores optional swap callback in `sort()`.
- Provides enough API compatibility for simple kernel sort users.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sort.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/spinlock.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/spinlock.h

Purpose: Lock guard macro definitions for spinlocks.

Key contents:
- Includes cleanup helpers and spinlock type definitions.
- Defines guard helpers for `spinlock`, `spinlock_irqsave`, `spinlock_irq`, and `raw_spinlock`.
- Large raw/spin/rwlock guard set is present under `#if 0`.

Behavior and design:
- Provides scoped lock cleanup support compatible with kernel-style guard syntax.
- Actual spinlock type and operations are in `spinlock_types.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/spinlock.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/spinlock_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/spinlock_types.h

Purpose: User-space spinlock type implementation.

Key contents:
- Defines `raw_spinlock_t` as a wrapper around `pthread_mutex_t`.
- Provides initializers and raw spin lock, unlock, trylock, irq, and irqsave variants.
- Typedefs `spinlock_t` to `raw_spinlock_t`.
- Defines `DEFINE_SPINLOCK`, `spin_lock_init`, lock/unlock aliases, irq/bh variants, and `spin_trylock`.

Behavior and design:
- Kernel spinlocks become pthread mutexes.
- Interrupt flags are ignored or set to zero; no real interrupt masking exists in user space.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/spinlock_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/srcu.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/srcu.h

Purpose: Simplified SRCU API mapped to RCU compatibility functions.

Key contents:
- Defines empty `struct srcu_struct`.
- Provides read lock/unlock no-ops returning index `0`.
- Maps SRCU polling and callback functions to RCU polling/callback APIs.
- Provides no-op expedited synchronize, barrier, cleanup, and init helpers.
- Defines scoped SRCU guard helper.

Behavior and design:
- SRCU is not independently modeled; it is treated as ordinary RCU or no-op where possible.
- Suitable only for bcachefs-tools user-space assumptions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/srcu.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/stat.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/stat.h

Purpose: Linux permission macro compatibility.

Key contents:
- Includes system `stat.h`.
- Defines `S_IRWXUGO`, `S_IALLUGO`, `S_IRUGO`, `S_IWUGO`, and `S_IXUGO`.

Behavior and design:
- Provides kernel-style aggregate permission masks for user-space code.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/stat.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/static_key.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/static_key.h

Purpose: Static branch/static key compatibility stub.

Key contents:
- Defines `struct static_key` and `struct static_key_false`.
- Provides no-op enable/disable helpers.
- `static_key_enabled()` always returns false.
- Defines `DEFINE_STATIC_KEY_FALSE`, `static_branch_unlikely`, and `static_branch_likely`.

Behavior and design:
- Does not implement jump labels.
- Branch macros inspect the stored `.key.v` field, but enable/disable do not mutate it.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/static_key.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/string.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/string.h

Purpose: Kernel string helper declarations and aliases.

Key contents:
- Includes libc string/stdlib and kernel string helper headers.
- Declares `strlcpy`, `strscpy`, `strim`, `memzero_explicit`, `match_string`, and `memscan`.
- Defines `kstrndup` and `kstrdup` as libc allocation wrappers.
- Defines `strtomem_pad`.

Behavior and design:
- Bridges kernel string API calls to libc-backed or project-provided implementations.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/string.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/string_choices.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/string_choices.h

Purpose: Constant string selection helpers.

Key contents:
- Defines boolean-to-string helpers for enable/disable, enabled/disabled, hi/lo, high/low, read/write, on/off, yes/no, up/down, true/false.
- Defines inverted macro aliases.
- Provides `str_plural()`.

Behavior and design:
- Matches newer kernel helper style for consistent status text.
- Pure inline/macro utility header.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/string_choices.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/string_helpers.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/string_helpers.h

Purpose: String formatting and padding helper declarations.

Key contents:
- Defines `enum string_size_units`.
- Declares `string_get_size()`.
- Implements `memcpy_and_pad()`.

Behavior and design:
- Provides kernel-style unit formatting API and fixed-width string field padding.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/string_helpers.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/swap.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/swap.h

Purpose: Swap/reclaim accounting stub.

Key contents:
- Defines `mm_account_reclaimed_pages()` as a no-op.

Behavior and design:
- Keeps memory reclaim call sites compiling without maintaining VM page accounting.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/swap.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sysfs.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/sysfs.h

Purpose: sysfs type declarations and basic operation declarations.

Key contents:
- Defines `struct attribute`, `attribute_group`, `bin_attribute`, and `sysfs_ops`.
- Declares file and bin-file create/remove functions.
- Provides no-op link create/remove helpers.

Behavior and design:
- Backed by `linux/kobject.c`, which builds an in-memory sysfs/debugfs tree and exposes read/write/list operations.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/thread_with_file.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/thread_with_file.h

Purpose: Stub for stdio redirection used by thread-with-file kernel code.

Key contents:
- Forward declares `struct stdio_redirect`.
- Defines `stdio_redirect_vprintf()` and `stdio_redirect_printf()` as empty inline functions.

Behavior and design:
- No actual redirection is implemented in this user-space build path.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/thread_with_file.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/thread_with_file_types.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/thread_with_file_types.h

Purpose: Empty compatibility placeholder.

Key contents:
- File is zero bytes.

Behavior and design:
- Satisfies includes for thread-with-file type declarations.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/thread_with_file_types.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/time.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/time.h

Purpose: Empty compatibility placeholder.

Key contents:
- File is zero bytes.

Behavior and design:
- Time definitions used by this group are in `time64.h` and `sched.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/time.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/time64.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/time64.h

Purpose: Kernel time64 compatibility helpers.

Key contents:
- Aliases `timespec64` to libc `timespec`.
- Defines `time64_t` and standard millisecond/microsecond/nanosecond constants.
- Implements `ns_to_timespec`, `timespec_to_ns`, `timespec_trunc`, and `set_normalized_timespec64`.
- Defines time64 aliases for timespec helpers.

Behavior and design:
- Provides enough kernel time arithmetic for filesystem timestamp handling.
- Warns on illegal granularity in `timespec_trunc()`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/time64.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/timer.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/timer.h

Purpose: Timer API declaration and minimal state structure.

Key contents:
- Defines `struct timer_list` with expiry, callback, and pending flag.
- Implements `timer_setup`, stack timer aliases, `timer_pending`, and `add_timer`.
- Declares deletion, synchronous deletion, modification, and flush functions.

Behavior and design:
- Timer implementation is elsewhere.
- API provides kernel-like delayed work/timer integration for workqueue code.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/timer.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/tracepoint.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/tracepoint.h

Purpose: Tracepoint macro compatibility layer.

Key contents:
- Defines trace macro helpers such as `PARAMS`, `TP_PROTO`, `TP_ARGS`, and `TP_CONDITION`.
- `DECLARE_TRACE` and related macros generate empty trace functions and registration stubs returning `-ENOSYS`.
- Defines event class and trace event macros as no-op or declaration-producing wrappers.

Behavior and design:
- Compile-time compatibility for kernel trace event declarations.
- Runtime tracing is disabled; trace enabled helpers return false.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/tracepoint.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/typecheck.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/typecheck.h

Purpose: Kernel compile-time type checking macros.

Key contents:
- Defines `typecheck(type, x)`.
- Defines `typecheck_fn(type, function)`.

Behavior and design:
- Uses GCC `typeof` and pointer comparison assignments to force compile-time type compatibility.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/typecheck.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/unaligned.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/unaligned.h

Purpose: Top-level unaligned access include shim.

Key contents:
- Includes `<asm/unaligned.h>`.

Behavior and design:
- Delegates architecture-specific unaligned helpers to the asm compatibility header.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/unaligned.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/unaligned/be_byteshift.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/unaligned/be_byteshift.h

Purpose: Big-endian unaligned access through byte shifts.

Key contents:
- Implements `__get_unaligned_be16/32/64` and `__put_unaligned_be16/32/64`.
- Provides public `get_unaligned_be*` and `put_unaligned_be*` wrappers.

Behavior and design:
- Avoids unaligned native loads by assembling values byte-by-byte in big-endian order.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/unaligned/be_byteshift.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/unaligned/be_struct.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/unaligned/be_struct.h

Purpose: Big-endian unaligned access through packed structs.

Key contents:
- Includes `packed_struct.h`.
- Maps big-endian get/put helpers to `__get_unaligned_cpu*` and `__put_unaligned_cpu*`.

Behavior and design:
- This variant assumes CPU-endian access matches intended use through packed structs.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/unaligned/be_struct.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/unaligned/generic.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/unaligned/generic.h

Purpose: Generic typed unaligned access macros.

Key contents:
- Declares `__bad_unaligned_access_size()`.
- Defines `__get_unaligned_le`, `__get_unaligned_be`, `__put_unaligned_le`, and `__put_unaligned_be`.

Behavior and design:
- Uses compile-time size selection for 1, 2, 4, and 8 byte objects.
- Unsupported sizes call a link-time error helper.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/unaligned/generic.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/unaligned/le_byteshift.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/unaligned/le_byteshift.h

Purpose: Little-endian unaligned access through byte shifts.

Key contents:
- Implements `__get_unaligned_le16/32/64` and `__put_unaligned_le16/32/64`.
- Provides public get/put wrappers.

Behavior and design:
- Assembles and stores values byte-by-byte in little-endian order.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/unaligned/le_byteshift.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/unaligned/le_struct.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/unaligned/le_struct.h

Purpose: Little-endian unaligned access through packed structs.

Key contents:
- Includes `packed_struct.h`.
- Maps little-endian get/put helpers to CPU packed-struct get/put helpers.

Behavior and design:
- Provides direct packed access where CPU byte order matches the intended little-endian representation.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/unaligned/le_struct.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/unaligned/packed_struct.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/unaligned/packed_struct.h

Purpose: CPU-endian unaligned access through packed wrapper structs.

Key contents:
- Defines packed structs for `u16`, `u32`, and `u64`.
- Implements `__get_unaligned_cpu16/32/64` and `__put_unaligned_cpu16/32/64`.

Behavior and design:
- Relies on packed struct layout to allow compiler-supported unaligned access.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/unaligned/packed_struct.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/unicode.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/unicode.h

Purpose: Unicode normalization/casefold API declarations.

Key contents:
- Defines Unicode age packing macros and `UTF8_LATEST`.
- Defines helpers to extract major, minor, and revision fields.
- Defines `enum utf8_normalization`.
- Defines `struct unicode_map`.
- Declares validation, comparison, casefold, normalization, hash, load/unload, and version parsing functions.

Behavior and design:
- Provides kernel Unicode API surface for filesystem name handling.
- Actual Unicode table and algorithm implementations are elsewhere.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/unicode.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/uuid.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/uuid.h

Purpose: Minimal UUID type and helper definitions.

Key contents:
- Defines `UUID_SIZE`.
- Defines `__uuid_t` as 16 bytes.
- Defines `UUID_INIT`.
- Implements `uuid_equal()`.

Behavior and design:
- Provides enough UUID support for kernel-derived filesystem structures.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/uuid.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/vmalloc.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/vmalloc.h

Purpose: vmalloc include shim.

Key contents:
- Includes `linux/slab.h`.

Behavior and design:
- vmalloc functions are implemented in `slab.h`; this header exists for include compatibility.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/vmalloc.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/wait.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/wait.h

Purpose: Kernel wait queue API declarations and wait macros.

Key contents:
- Defines `wait_queue_t`, wait queue function type, wait queue flags, wait queue entry, and wait queue head.
- Declares wake, prepare, finish, and wake function helpers.
- Defines wait queue initialization macros.
- Implements `wait_event`, interruptible/freezable/killable wrappers, timeout variants, and bit wait helpers.
- Declares bit wait wake/wait primitives.

Behavior and design:
- Provides kernel-style condition waiting around `schedule()` and `schedule_timeout()`.
- Interruptible/freezable/killable variants collapse to normal wait behavior.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/wait.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/wait_bit.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/wait_bit.h

Purpose: Bit wait helper declarations.

Key contents:
- Defines `struct wait_bit_key`.
- Defines `wait_bit_action_f`.
- Declares `out_of_line_wait_on_bit_timeout()`.

Behavior and design:
- Complements `wait.h` bit-wait macros and out-of-line wait implementation.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/wait_bit.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/workqueue.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/workqueue.h

Purpose: Kernel workqueue API declarations and work structure definitions.

Key contents:
- Defines `work_struct`, `delayed_work`, pending-bit helpers, initialization macros, and `to_delayed_work()`.
- Defines major workqueue flags and limits.
- Declares global system workqueues.
- Declares allocation, destruction, queueing, delayed work, flushing, draining, cancellation, scheduling, and diagnostics helpers.
- Provides inline wrappers for `schedule_work`, delayed scheduling, and flushing scheduled work.

Behavior and design:
- Mirrors kernel workqueue API enough for async bcachefs code.
- Implementation is elsewhere; this header supplies core types and call surface.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/workqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/xattr.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/xattr.h

Purpose: Kernel extended attribute API declarations.

Key contents:
- Includes UAPI xattr constants.
- Defines `XATTR_CREATE` and `XATTR_REPLACE` if missing.
- Defines `struct xattr_handler` and `struct xattr`.
- Provides `xattr_handler_can_list()` and `xattr_prefix()`.
- Declares VFS/generic xattr get, list, set, remove, allocation, and security helpers.

Behavior and design:
- Supports filesystem xattr handler tables and generic operations.
- Actual generic/VFS implementations are elsewhere.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/xxhash.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/xxhash.h

Purpose: xxHash API declarations.

Key contents:
- Declares one-shot `xxh32()` and `xxh64()`.
- Provides `xxhash()` word-size dispatch.
- Defines private state structs for 32-bit and 64-bit streaming hash state.
- Declares reset, update, digest, and state copy functions.

Behavior and design:
- Header is dual-license BSD/GPL derived from xxHash.
- Provides API surface; implementation is outside this file.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/xxhash.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/zlib.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/zlib.h

Purpose: zlib compatibility aliases.

Key contents:
- Includes system `<zlib.h>`.
- Defines workspace size helpers as `0`.
- Maps kernel-prefixed zlib inflate/deflate calls to zlib functions.
- Defines `DEF_MEM_LEVEL`.

Behavior and design:
- Uses host zlib directly rather than kernel workspaces.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/zlib.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/zstd.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/zstd.h

Purpose: Kernel-style wrapper API for upstream zstd.

Key contents:
- Includes upstream `<zstd.h>` and local zstd error definitions.
- Declares helper functions for bounds, error checks, error names, min/max compression level, and parameter selection.
- Typedefs zstd parameter, frame, context, stream, and buffer types to upstream ZSTD types.
- Declares single-pass compression/decompression, streaming compression/decompression, frame size, and frame header APIs.

Behavior and design:
- Exposes kernel-style lower-case `zstd_*` functions while using upstream ZSTD types.
- Workspace-bound functions preserve kernel allocation style even in user space.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/zstd.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/zstd_errors.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/zstd_errors.h

Purpose: ZSTD error code definitions.

Key contents:
- Defines visibility/API macros.
- Defines `ZSTD_ErrorCode` enum with stable and unstable error values.
- Declares `ZSTD_getErrorCode()` and `ZSTD_getErrorString()`.

Behavior and design:
- Mirrors upstream zstd error API for compatibility with kernel-style zstd wrapper header.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/zstd_errors.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/trace/define_trace.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/trace/define_trace.h

Purpose: Empty trace include placeholder.

Key contents:
- File is zero bytes.

Behavior and design:
- Satisfies trace event headers that include `<trace/define_trace.h>` after macro definitions.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/trace/define_trace.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/trace/events/lock.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/trace/events/lock.h

Purpose: Lock trace event declarations.

Key contents:
- Defines `TRACE_SYSTEM lock`.
- Defines lock contention flags.
- Under lockdep/stat configs, declares lock acquire/release/contended/acquired events.
- Always declares `contention_begin` and `contention_end` trace events.
- Includes `<trace/define_trace.h>` outside include guard.

Behavior and design:
- With this project’s `tracepoint.h`, these events compile to no-op trace functions and disabled tracepoint registration.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/trace/events/lock.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/uapi/linux/magic.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/uapi/linux/magic.h

Purpose: Filesystem magic number constants.

Key contents:
- Defines many Linux superblock magic constants for local, network, pseudo, virtual, and special filesystems.
- Includes `BCACHEFS_SUPER_MAGIC`.
- Includes constants for ext, btrfs, f2fs, xfs, overlayfs, fuse, proc, sysfs, cgroup, bpf, zonefs, and others.

Behavior and design:
- Pure UAPI macro header for filesystem type identification.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/uapi/linux/magic.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/uapi/linux/xattr.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/uapi/linux/xattr.h

Purpose: UAPI extended attribute constants.

Key contents:
- Defines `XATTR_CREATE` and `XATTR_REPLACE` when enabled by libc compatibility.
- Defines namespace prefixes and prefix lengths for OS/2, macOS, btrfs, security, system, trusted, and user xattrs.
- Defines named security attributes for EVM, IMA, SELinux, Smack, and capabilities.
- Defines POSIX ACL xattr names.

Behavior and design:
- Provides stable string constants shared by user-space and kernel-style code.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/uapi/linux/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/initramfs/hook.in -->
# File Research: sources/cow-pools/bcachefs-tools/initramfs/hook.in

Purpose: initramfs-tools hook template for bcachefs.

Key contents:
- Implements `prereqs` handler.
- Sources `/usr/share/initramfs-tools/hook-functions`.
- Adds `bcachefs` kernel module.
- Adds loaded chacha20 and poly1305 modules for encrypted bcachefs filesystems.
- Copies `bcachefs` and `mount.bcachefs` into initramfs `/sbin`.

Behavior and design:
- Uses `@ROOT_SBINDIR@` substitution at build/install time.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/initramfs/hook.in -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/atomic64.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/atomic64.c

Purpose: Generic spinlock-backed 64-bit atomic implementation when `ATOMIC64_SPINLOCK` is enabled.

Key contents:
- Defines a 16-entry cacheline-aligned lock array.
- Hashes atomic variable addresses to locks.
- Implements `atomic64_read`, `atomic64_set`, arithmetic/bitwise operations, return variants, fetch variants, decrement-if-positive, cmpxchg, try_cmpxchg, xchg, and add_unless.

Behavior and design:
- Only compiled under `ATOMIC64_SPINLOCK`.
- Uses raw spinlock irqsave wrappers, which in user space map to pthread mutex locking.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/atomic64.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/bio.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/bio.c

Purpose: User-space implementation of core Linux bio allocation, lifecycle, copying, splitting, and completion helpers.

Key contents:
- Maps `blk_status_t` values to errno and strings.
- Implements bio data copy between iterators, zero-fill, clone, split, advance, reset, put/free, and virtual segment addition.
- Implements chained bio completion without unbounded recursion.
- Provides `bio_kmalloc`, `bio_alloc`, and `bio_alloc_bioset`.
- Implements `bioset_init`, `bioset_exit`, and global `fs_bio_set` constructor/destructor.

Behavior and design:
- bioset allocation uses mempools for bio objects and bio_vec arrays.
- Inline vectors are used when vector count fits `BIO_INLINE_VECS`; larger vectors use the bvec mempool.
- Completion honors `BIO_CHAIN` remaining counts and propagates status to parent bios.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/bio.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/blkdev.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/blkdev.c

Purpose: User-space block-device I/O backend for kernel-style bio submission.

Key contents:
- Defines sync and Linux AIO fops for read/write.
- Implements `generic_make_request()` for read, write, flush, preflush, FUA, and discard.
- Implements `submit_bio_wait()`.
- Implements block-device open/close helpers, capacity and logical block size queries, nonrotational check, and initialization.
- Implements an AIO completion thread using `io_getevents()`.

Behavior and design:
- Starts with sync fops before thread initialization, then `blkdev_init()` switches to AIO if available.
- Falls back to sync I/O when `io_setup()` returns `-ENOSYS`.
- Read/write bios become `iovec` arrays and dispatch via `preadv`, `pwritev2`, or libaio vector operations.
- Discard is implemented as hole punching in `generic_make_request()`, while `blkdev_issue_discard()` itself currently returns `0`.
- `blkdev_issue_zeroout()` is explicitly unimplemented and calls `BUG()`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/blkdev.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/closure.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/closure.c

Purpose: Kernel bcache/bcachefs closure asynchronous refcount implementation.

Key contents:
- Implements `closure_sub()` state transitions for normal put, requeue, and completion/destruction.
- Implements wait-list wakeup and `closure_wait()`.
- Implements synchronous wait helpers `__closure_sync`, `closure_return_sync`, and `__closure_sync_timeout`.
- Optional `CONFIG_DEBUG_CLOSURES` support tracks closures and exposes debugfs output.

Behavior and design:
- Uses atomic remaining counter bits for refcount, sleeping, destructor, waiting, and guard flags.
- Wakeups use lockless linked lists and reverse order to preserve FIFO fairness.
- Sleeping closures store `current` and are woken through `wake_up_process()`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/closure.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/crc64.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/crc64.c

Purpose: CRC64 ECMA-182 calculation.

Key contents:
- Includes generated CRC64 table.
- Implements `crc64_be()` for big-endian CRC64 over a byte buffer.
- Exports the symbol.

Behavior and design:
- Table-driven update: index from high CRC byte xor input byte, then table xor shifted CRC.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/crc64.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/crc64table.h -->
# File Research: sources/cow-pools/bcachefs-tools/linux/crc64table.h

Purpose: Generated CRC64 lookup table.

Key contents:
- Defines `crc64table[256]` as a cacheline-aligned static `u64` table.
- Header marks itself generated and not for manual editing.

Behavior and design:
- Used by `crc64.c` for ECMA-182 CRC64 computation.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/crc64table.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/fs.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/fs.c

Purpose: POSIX ACL xattr handler placeholders.

Key contents:
- Defines `nop_posix_acl_access` and `nop_posix_acl_default`.
- Sets names to POSIX ACL access/default xattr names and flags to ACL type constants.

Behavior and design:
- Provides no-operation handler objects for filesystems that reference POSIX ACL handlers.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/fs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/fs_parser.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/fs_parser.c

Purpose: Filesystem parser constant lookup helpers.

Key contents:
- Defines `bool_names` constant table mapping `"0"`, `"1"`, `"false"`, `"no"`, `"true"`, and `"yes"`.
- Implements internal `__lookup_constant()`.
- Implements `lookup_constant()` with fallback value.

Behavior and design:
- Simple string equality lookup for mount/config option parsing.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/fs_parser.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/generic-radix-tree.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/generic-radix-tree.c

Purpose: Generic radix tree backing implementation.

Key contents:
- Implements pointer lookup and allocating lookup for `struct __genradix`.
- Implements forward and reverse iterator peek helpers.
- Implements preallocation and full tree free.
- Exports all public functions.

Behavior and design:
- Uses root pointer low bits to encode depth.
- Grows tree depth with compare-exchange, preserving lockless/concurrent insertion behavior.
- Allocated nodes are zeroed through `genradix_alloc_node()`.
- Iterators skip missing subtrees and manage overflow/end state with `SIZE_MAX`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/generic-radix-tree.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/int_sqrt.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/int_sqrt.c

Purpose: Integer square root implementation.

Key contents:
- Implements `int_sqrt()` for `unsigned long`.
- Implements `int_sqrt64()` for 32-bit `BITS_PER_LONG` builds.
- Exports symbols.

Behavior and design:
- Uses shift-and-subtract algorithm.
- Returns floor of square root.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/int_sqrt.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/kobject.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/kobject.c

Purpose: User-space kobject/sysfs/debugfs model.

Key contents:
- Implements kobject init, add, delete, get, put, and cleanup.
- Tracks a single root kobject and parent/child relationships with dynamic arrays under a mutex.
- Implements sysfs file/bin-file creation and removal.
- Implements path lookup for sysfs attributes and bin attributes.
- Implements sysfs read/list/write operations, including HTML directory listing.
- Implements debugfs create file/dir, path lookup, directory listing, and file reading.

Behavior and design:
- Uses in-memory trees rather than actual sysfs/debugfs filesystem nodes.
- Starts an HTTP server lazily when per-filesystem debugfs entries are created.
- Debugfs removal functions are stubs.
- Attribute reads call `sysfs_ops->show`; writes call `sysfs_ops->store` or bin write callback.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/kobject.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/kstrtox.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/kstrtox.c

Purpose: Kernel-style string-to-integer conversion functions.

Key contents:
- Implements radix autodetection and prefix handling.
- Implements internal `_parse_integer()`.
- Implements `kstrtoull`, `kstrtoll`, `_kstrtoul`, `_kstrtol`, `kstrtouint`, `kstrtoint`, `kstrtou16`, `kstrtos16`, `kstrtou8`, `kstrtos8`, and `kstrtobool`.

Behavior and design:
- Supports optional plus sign for unsigned conversions and plus/minus for signed conversions.
- Allows one trailing newline before NUL.
- Returns `-EINVAL` on parse errors and `-ERANGE` on overflow.
- `kstrtobool()` accepts common `y/n/1/0/on/off` forms by initial characters.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/kstrtox.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/kstrtox.h -->
# File Research: sources/cow-pools/bcachefs-tools/linux/kstrtox.h

Purpose: Internal kstrtox parser declarations.

Key contents:
- Declares `_parse_integer_fixup_radix()`.
- Declares `_parse_integer()`.

Behavior and design:
- Small private header for `linux/kstrtox.c`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/kstrtox.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/kthread.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/kthread.c

Purpose: User-space implementation of kernel kthread API using pthreads.

Key contents:
- Defines kthread state bits for per-cpu, stop, park, and parked.
- Implements pthread start wrapper that registers RCU thread state, initializes percpu state, sets `current`, waits for scheduling, runs the thread function, completes exit, and unregisters.
- Implements `kthread_create`, `kthread_should_stop`, `kthread_freezable_should_stop`, and `kthread_stop`.

Behavior and design:
- New threads start in `TASK_UNINTERRUPTIBLE` and are awakened via `wake_up_process()`.
- Uses 32 KiB pthread stack size.
- Retries thread creation after `run_shrinkers()` on failure.
- `kthread_stop()` sets stop bit, wakes the thread, waits for exit completion, and returns `0`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/kthread.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/llist.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/llist.c

Purpose: Lockless singly-linked list operations.

Key contents:
- Implements `llist_add_batch()`.
- Implements `llist_del_first()`.
- Implements `llist_reverse_order()`.
- Exports symbols.

Behavior and design:
- Uses `cmpxchg` on the head pointer.
- Supports multiple adders; `llist_del_first()` is safe only for one consumer as in kernel semantics.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/llist.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/mempool.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/mempool.c

Purpose: Kernel mempool implementation for user-space allocation reliability.

Key contents:
- Implements mempool initialization, creation, resize, allocation, free, exit, and destroy.
- Provides slab, kmalloc, and page allocator/free wrappers.
- Includes optional debug poisoning hooks under slab debug configs.
- Uses wait queues and spinlocks for pool coordination.

Behavior and design:
- Preallocates `min_nr` elements.
- `mempool_alloc()` first tries direct allocation, then reserved pool, then waits for a returned element.
- `mempool_free()` refills the pool if below `min_nr`, otherwise frees through backing allocator.
- Uses memory barriers to preserve kernel mempool ordering guarantees.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/mempool.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/min_heap.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/min_heap.c

Purpose: Exported wrappers around inline min-heap helpers.

Key contents:
- Implements wrappers for heap init, peek, full check, sift down/up, heapify, pop, pop-push, push, and delete.
- Exports each wrapper.

Behavior and design:
- Delegates all logic to inline implementations from `linux/min_heap.h`.
- Provides linkable symbols when non-inline references are needed.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/min_heap.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/percpu.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/percpu.c

Purpose: User-space emulation of Linux percpu variables.

Key contents:
- Defines per-thread TLS chunk pointers and CPU IDs.
- Tracks all percpu chunks, static section size, dynamic arena use, callbacks, free runs, dynamic initializers, and allocation size metadata.
- Implements callback registration, per-thread initialization, dynamic percpu allocation, dynamic init registration, free, and constructor/destructor setup.
- Initializes slot 0 before module init constructors.

Behavior and design:
- Each thread gets a chunk containing static percpu storage followed by a fixed dynamic arena.
- Static percpu variables are resolved by offset from linker section symbols.
- Dynamic `alloc_percpu()` returns an offset cast to pointer; resolution adds that offset into each thread chunk.
- New chunks are zeroed and run registered per-thread initializers.
- Free uses a simple free-run list; if appending to the free list fails, it leaks the slot rather than aborting.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/percpu.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/percpu_register.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/percpu_register.c

Purpose: Register bcachefs percpu variables needing per-thread setup.

Key contents:
- Constructor calls `bch_percpu_register()`.
- Registers `bch2_lock_graph_init_one` and `bch2_lock_graph_exit_one` for `bch2_lock_graph`.

Behavior and design:
- Bridges kernel-style module-time percpu initialization to dynamic user-space thread creation.
- Kept outside synced filesystem source to avoid clobbering.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/percpu_register.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/preempt.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/preempt.c

Purpose: Preemption API no-op implementation for user-space percpu model.

Key contents:
- Implements `preempt_disable()` and `preempt_enable()` as empty functions.

Behavior and design:
- Comments explain that user-space percpu storage is per-thread, so disabling preemption is unnecessary for `this_cpu_ptr()` access.
- Cross-thread percpu reads keep eventual-consistency semantics.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/preempt.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/printk.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/printk.c

Purpose: printk and stack dump support.

Key contents:
- Implements `vprintk()` and `printk()` using stdio.
- Strips kernel loglevel control prefix when present.
- Implements `dump_stack()` by formatting task backtrace into a printbuf and writing to stderr.

Behavior and design:
- Provides simple user-space logging compatible with kernel call sites.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/printk.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/ratelimit.c -->
# File Research: sources/cow-pools/bcachefs-tools/linux/ratelimit.c

Purpose: Kernel-style rate limiting implementation.

Key contents:
- Implements `___ratelimit()`.
- Uses interval, burst, flags, begin time, atomic remaining count, and raw spinlock.
- Emits suppressed-callback warnings through `printk()` when configured.

Behavior and design:
- Zero interval disables limiting; nonpositive burst suppresses unless interval rules allow.
- Lock contention path may allow callbacks based on atomic remaining count.
- Resets state when interval expires and tracks missed callbacks when suppressed.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/linux/ratelimit.c -->