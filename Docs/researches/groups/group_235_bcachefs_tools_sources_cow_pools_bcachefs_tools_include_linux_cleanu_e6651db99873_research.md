# Group Research: group_235_bcachefs_tools_sources_cow_pools_bcachefs_tools_include_linux_cleanu_e6651db99873

Scope checked against `Docs/research_subset_a.md`: `sources/cow-pools/bcachefs-tools` is included in subset A. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/cleanup.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/cleanup.h

Purpose: Provides kernel-style scope cleanup helpers for bcachefs-tools userspace builds using GCC/Clang `__cleanup__` attributes.

Key APIs and macros:
- `DEFINE_FREE()`, `__free()`, `no_free_ptr()`, `return_ptr()` implement automatic LIFO cleanup and explicit ownership transfer.
- `DEFINE_CLASS()`, `EXTEND_CLASS()`, `CLASS()` build cleanup-backed scoped object classes.
- `DEFINE_GUARD()`, `DEFINE_GUARD_COND()`, `guard()`, `scoped_guard()`, `scoped_cond_guard()` build RAII-style lock guards.
- `DEFINE_LOCK_GUARD_0/1()` and conditional variants support lock guards with no native lock object or with extra saved state.

Integration:
- Depends on `linux/kernel.h` for compiler helpers, `BUILD_BUG_ON`, `typeof_member`, and boolean constants.
- Used by mutex, preempt, irqflags, percpu rwsem, and RCU wrappers to provide kernel-like scoped locking in userspace.

Behavior notes:
- Cleanup order is reverse declaration order, which matters when cleanup actions depend on locks.
- The header explicitly warns not to mix `goto` unwinding and cleanup helpers in the same routine unless all resources are converted.
- Conditional guards encode failed acquisition as a null lock pointer and skip/fail the guarded body.

Risks:
- Misordered declarations can free resources after locks have already been released.
- `no_free_ptr()` relies on cleanup functions tolerating NULL.
- Macros use GNU C extensions heavily and are not portable to strict ISO C.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/cleanup.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/closure.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/closure.h

Purpose: Declares the bcache closure asynchronous completion/refcount framework.

Key types:
- `struct closure_waitlist` wraps an `llist_head`.
- `struct closure` stores a work callback, optional parent closure, atomic remaining count, and optional debug metadata.
- `closure_fn` is a workqueue callback signature.

Key APIs:
- Reference flow: `closure_init()`, `closure_init_stack()`, `closure_get()`, `closure_put()`, `closure_get_not_zero()`.
- Waiting: `closure_sync()`, `closure_sync_timeout()`, `closure_wait()`, `closure_wake_up()`, wait-event macros.
- Async continuation: `continue_at()`, `continue_at_nobarrier()`, `closure_return()`, `closure_return_with_destructor()`, `closure_call()`.
- Debug hooks become no-ops without `CONFIG_DEBUG_CLOSURES`.

Integration:
- Depends on `llist`, scheduler/task headers, and workqueues.
- Functions such as `closure_sub()`, `__closure_wake_up()`, and sync implementations are external.

Behavior notes:
- Closures start with count 1 and `CLOSURE_RUNNING`; in-flight operations add refs, continuations drop the running ref.
- `continue_at()` must be followed by return because ownership moves to the next callback or parent.
- Parent closures are refcounted so nested async work behaves like a continuation stack.

Risks:
- Incorrect ref ownership can run continuations too early or after object lifetime ends.
- Debug flags help catch misuse but are compiled out normally.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/closure.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/compiler.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/compiler.h

Purpose: Userspace substitute for Linux compiler annotations, barriers, READ/WRITE_ONCE, and cache flush stubs.

Key APIs and macros:
- Compiler barriers: `barrier()`, `barrier_data()`, `OPTIMIZER_HIDE_VAR()`.
- Attributes and annotations: `__always_inline`, `noinline`, `__packed`, `__printf`, `__must_check`, `__cleanup`, `__rcu`, `__percpu`, etc.
- Branch hints: `likely()`, `unlikely()`, `unreachable()`.
- Type helpers: `__same_type()`, `typeof_member()`, `is_signed_type()`, `is_unsigned_type()`, `__is_constexpr()`.
- Access helpers: `ACCESS_ONCE()`, `READ_ONCE()`, `WRITE_ONCE()`, `lockless_dereference()`.

Integration:
- Includes `linux/types.h`.
- Supplies `__cleanup()` used by `cleanup.h`.
- Cache flush APIs are no-op userspace stubs.

Behavior notes:
- `READ_ONCE`/`WRITE_ONCE` use may-alias typedefs for 1, 2, 4, and 8 byte accesses and barrier-protected memcpy for larger objects.
- Defines `CONFIG_X86_64` when compiled on x86_64.

Risks:
- Many kernel annotations are erased, so static-analysis and address-space checks are not preserved.
- Memory semantics are compiler-level unless paired with real atomic/barrier primitives elsewhere.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/compiler.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/completion.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/completion.h

Purpose: Declares a kernel-like completion primitive backed by userspace wait queues.

Key APIs:
- `struct completion { unsigned int done; wait_queue_head_t wait; }`
- `DECLARE_COMPLETION()`, `DECLARE_COMPLETION_ONSTACK()`
- `init_completion()`, `reinit_completion()`
- External: `complete()`, `wait_for_completion()`, `wait_for_completion_timeout()`
- `wait_for_completion_interruptible()` maps to a blocking wait and returns 0.

Integration:
- Depends on `linux/wait.h`.

Behavior notes:
- Inline initialization resets `done` and initializes the wait queue.
- Actual signaling and blocking behavior lives outside this header.

Risks:
- Interruptible waits are simplified and cannot report signal interruption.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/completion.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/console.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/console.h

Purpose: Stubs kernel console locking in userspace.

Key APIs:
- `console_lock()` no-op.
- `console_trylock()` always true.
- `console_unlock()` no-op.

Integration:
- Lets kernel-derived code compile where console serialization has no userspace equivalent.

Risks:
- Code relying on console lock serialization receives no protection.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/console.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/cpumask.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/cpumask.h

Purpose: Maps kernel CPU-mask concepts to bcachefs-tools per-thread percpu slots.

Key APIs:
- Extern `bch_percpu_nr_cpus`.
- CPU count macros return `bch_percpu_nr_cpus`.
- `cpu_online/possible/present/active(cpu)` check slot bounds.
- `raw_smp_processor_id()` returns 0.
- `for_each_cpu*()` and `for_each_possible/online/present_cpu()` iterate over registered percpu chunks.

Integration:
- Coupled to `linux/percpu.c` chunk registry.

Behavior notes:
- “CPU” means userspace thread slot, not OS CPU.
- Mask arguments are ignored by iteration macros.

Risks:
- Code expecting actual CPU affinity or mask filtering gets broad iteration over all registered thread slots.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/cpumask.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/crc32c.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/crc32c.h

Purpose: Thin include wrapper for CRC32C helpers.

Key APIs:
- Includes `"tools-util.h"`; this header declares no symbols itself.

Integration:
- Provides kernel-compatible include path for code expecting `linux/crc32c.h`.

Risks:
- All actual CRC32C API availability depends on `tools-util.h`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/crc32c.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/crc64.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/crc64.h

Purpose: Declares CRC64 big-endian checksum routine.

Key APIs:
- `u64 __pure crc64_be(u64 crc, const void *p, size_t len);`

Integration:
- Includes `linux/types.h`.
- Implementation is external.

Risks:
- Header only exposes the function; polynomial details and table behavior are elsewhere.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/crc64.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/crypto.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/crypto.h

Purpose: Minimal userspace surface for kernel crypto algorithm registration.

Key types and APIs:
- `struct crypto_alg` with list linkage, name, type, and `alloc_tfm` callback.
- `crypto_register_alg(struct crypto_alg *alg)`.
- `struct crypto_tfm { struct crypto_alg *alg; }`
- Defines `CRYPTO_MINALIGN` and `CRYPTO_MINALIGN_ATTR`.

Integration:
- Depends on `kernel`, `list`, and `slab` shims.
- Used where bcachefs crypto code expects kernel crypto registration shapes.

Risks:
- Extremely small subset of kernel crypto API; no transform operation API is defined here.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/crypto.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/ctype.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/ctype.h

Purpose: Compatibility include for C character classification.

Key APIs:
- Includes system `<ctype.h>`.

Integration:
- Lets kernel-derived code include `linux/ctype.h`.

Risks:
- Uses libc semantics, not any custom kernel ctype table.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/ctype.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/dcache.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/dcache.h

Purpose: Minimal dentry/qstr compatibility definitions.

Key APIs:
- `struct dentry` with `d_sb`, `d_inode`, `is_debugfs`, and `name`.
- `shrink_dcache_sb()` no-op.
- `QSTR_INIT()` and `QSTR()` constructors.

Integration:
- Forward-declares `super_block` and `inode`.
- `QSTR` relies on `struct qstr` defined elsewhere, notably `linux/kernel.h`.

Risks:
- Dentry model is skeletal and not a real VFS cache.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/dcache.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/debugfs.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/debugfs.h

Purpose: Declares minimal debugfs creation/removal APIs.

Key APIs:
- `debugfs_create_file()`
- `debugfs_create_dir()`
- `debugfs_remove()`
- `debugfs_remove_recursive()`

Integration:
- Depends on `linux/fs.h`, `seq_file.h`, `types.h`, and `compiler.h`.
- Uses `struct dentry` and `struct file_operations`.

Risks:
- Header is declarative only; userspace behavior depends on external implementation.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/debugfs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/device.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/device.h

Purpose: Tiny userspace device/class compatibility shim.

Key APIs:
- Empty `struct class` and `struct device`.
- `class_create()` allocates a class via `kzalloc`; `class_destroy()` frees it.
- `device_create()` allocates a device; `device_unregister()` frees it.
- `device_destroy()` no-op.

Integration:
- Depends on `linux/slab.h` and `linux/types.h`.

Risks:
- No sysfs/devtmpfs/device-model behavior is implemented.
- `device_create()` ignores parent, devt, drvdata, and formatted name.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/device.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/dynamic_fault.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/dynamic_fault.h

Purpose: Disables dynamic fault injection in userspace builds.

Key APIs:
- `dynamic_fault(_class)` returns 0.
- `race_fault()` returns 0.

Integration:
- Lets fault-injection call sites compile.

Risks:
- Test/fault paths guarded by these macros are unreachable in tools builds.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/dynamic_fault.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/err.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/err.h

Purpose: Implements Linux encoded error-pointer helpers.

Key APIs:
- `MAX_ERRNO 4095`, `IS_ERR_VALUE()`.
- `ERR_PTR()`, `PTR_ERR()`, `IS_ERR()`, `IS_ERR_OR_NULL()`, `ERR_CAST()`, `PTR_ERR_OR_ZERO()`.

Integration:
- Includes `asm/errno.h`, compiler, and types shims.

Behavior notes:
- Uses the kernel convention that high invalid pointer values encode negative errno values.

Risks:
- Assumes userspace address layout leaves the encoded error-pointer range unmapped.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/err.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/errname.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/errname.h

Purpose: Converts errno values to printable names/messages.

Key APIs:
- `errname(int err)` returns `strerror(abs(err))`.

Integration:
- Includes `<string.h>`.

Risks:
- Returns libc error strings, not Linux kernel symbolic names such as `-EINVAL`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/errname.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/export.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/export.h

Purpose: Stubs kernel module export macros.

Key APIs:
- `EXPORT_SYMBOL*()` and `EXPORT_UNUSED_SYMBOL*()` no-op.
- `THIS_MODULE` is null.
- `KBUILD_MODNAME` is empty.

Integration:
- Lets kernel-derived module/export annotations compile in userspace.

Risks:
- No symbol visibility, module ownership, or refcount semantics are provided.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/export.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/freezer.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/freezer.h

Purpose: Stubs kernel freezer support.

Key APIs:
- `try_to_freeze()`, `set_freezable()` no-op.
- `freezing(task)` false.
- `freezable_schedule()` and timeout variant call regular scheduler functions.
- `__refrigerator()` no-op.

Integration:
- Expects `schedule()`/`schedule_timeout()` from scheduler shims.

Risks:
- Threads never enter a frozen state in userspace tools.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/freezer.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/fs_parser.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/fs_parser.h

Purpose: Minimal filesystem parameter parser declarations.

Key APIs:
- `struct constant_table { const char *name; int value; }`
- `lookup_constant()`
- External `bool_names[]`.

Integration:
- Used by mount/option parsing code expecting kernel fs parser helpers.

Risks:
- Only constant lookup surface is present; full kernel fs parameter parsing is absent.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/fs_parser.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/generic-radix-tree.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/generic-radix-tree.h

Purpose: Generic sparse array/radix tree wrapper for typed objects.

Key types:
- `struct __genradix` stores tagged root pointer.
- `struct genradix_node` is either an interior child pointer array or a leaf data page.
- `GENRADIX(type)` creates a typed radix container with a zero-sized type witness.
- `struct genradix_iter` tracks byte offset and logical position.

Key APIs:
- Init/free: `DEFINE_GENRADIX`, `genradix_init()`, `genradix_free()`.
- Lookup/allocation: `genradix_ptr()`, `genradix_ptr_inlined()`, `genradix_ptr_alloc()`, preallocated variants.
- Iteration: `genradix_iter_init()`, `genradix_iter_peek()`, `genradix_iter_peek_prev()`, `genradix_for_each*()`.
- Preallocation: `genradix_prealloc()`.

Integration:
- Depends on page/log2/math/slab/types/overflow helpers.
- Core non-inline implementation is external: `__genradix_free`, `__genradix_ptr`, `__genradix_ptr_alloc`, iterator helpers, `__genradix_prealloc`.

Behavior notes:
- Root pointer stores tree depth in low bits.
- Addressing is by byte offset; public macros translate object index to offset.
- Object size must not exceed 512-byte `GENRADIX_NODE_SIZE`.
- Non-power-of-two object sizes avoid straddling leaf pages.

Risks:
- Header notes existing overflow assumptions around inode-number-sized indexes.
- Callers must handle NULL on missing entries or allocation failure.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/generic-radix-tree.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/genhd.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/genhd.h

Purpose: Empty compatibility header.

Key APIs:
- None.

Integration:
- Satisfies include paths for kernel code that includes `linux/genhd.h`.

Risks:
- Any caller needing block-disk declarations must obtain them elsewhere.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/genhd.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/gfp.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/gfp.h

Purpose: Redirects GFP allocation definitions to slab compatibility.

Key APIs:
- Includes `linux/slab.h`.

Integration:
- `gfp_t` and GFP flags are supplied by other headers such as `kernel.h`/`slab.h`.

Risks:
- No standalone definitions in this file.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/gfp.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/hash.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/hash.h

Purpose: Integer and pointer hash helpers using multiplicative golden-ratio constants.

Key APIs:
- `GOLDEN_RATIO_32`, `GOLDEN_RATIO_64`, `GOLDEN_RATIO_PRIME`.
- `__hash_32_generic()`, `hash_32_generic()`, `hash_64_generic()`.
- `hash_long()`, `hash_ptr()`, `hash32_ptr()`.

Integration:
- Depends on word size via `BITS_PER_LONG`.
- Can include arch hash overrides if `CONFIG_HAVE_ARCH_HASH` is set.

Behavior notes:
- Hashes by multiplying with a large odd constant and taking high bits.
- `hash32_ptr()` folds a pointer to 32 bits rather than strongly hashing it.

Risks:
- Not cryptographic.
- `bits` argument must be sensible for shift widths.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/hash.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/hex.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/hex.h

Purpose: Empty compatibility header.

Key APIs:
- None.

Integration:
- Hex digit arrays/macros are instead defined in `linux/kernel.h`.

Risks:
- Include-only compatibility; no declarations here.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/hex.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/idr.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/idr.h

Purpose: Provides IDR/IDA data structures and declarations for ID-to-pointer and integer ID allocation.

Key types:
- `struct idr_layer`, `struct idr`.
- `struct ida` with mutex, depth, and flat bitmap-tree nodes.

Key APIs:
- IDR declarations: `idr_find_slowpath`, `idr_preload`, `idr_alloc_cyclic`, `idr_for_each`, `idr_get_next`, `idr_replace`, `idr_destroy`, `idr_init`, `idr_is_empty`.
- IDR inline stubs: `idr_alloc()` returns 0, `idr_remove()` no-op, `idr_preload_end()` enables preemption.
- `idr_find()` uses RCU hint fast path then slowpath.
- IDA declarations: `ida_init`, `ida_destroy`, `ida_alloc_range`, `ida_free`, `ida_alloc_batch`, `ida_find_first`.
- IDA wrappers: `ida_alloc`, `ida_alloc_min`, `ida_alloc_max`.

Integration:
- Depends on bitmap, bitops, preempt, rcupdate, spinlock.
- IDA userspace implementation is described as an Eytzinger-layout bitmap tree, not kernel xarray.

Risks:
- `idr_alloc()`/`idr_remove()` are stubbed, so pointer ID allocation may be incomplete or intentionally unused.
- IDR lockless lookup requires caller-managed lifetime discipline.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/idr.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/ioprio.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/ioprio.h

Purpose: Defines Linux I/O priority bit layout and constants.

Key APIs:
- `IOPRIO_BITS`, `IOPRIO_CLASS_SHIFT`, `IOPRIO_PRIO_MASK`.
- `IOPRIO_PRIO_CLASS()`, `IOPRIO_PRIO_DATA()`, `IOPRIO_PRIO_VALUE()`, `ioprio_valid()`.
- Classes: none, realtime, best-effort, idle.
- Who constants: process, process group, user.
- `IOPRIO_BE_NR`, `IOPRIO_NORM`.

Integration:
- Pure macro/enum header.

Risks:
- No syscalls or setters/getters are provided.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/ioprio.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/irqflags.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/irqflags.h

Purpose: Stubs local interrupt flag operations for userspace.

Key APIs:
- `local_irq_save(flags)` sets flags to 0.
- Restore/disable/enable are no-ops.
- Defines an `irqsave` cleanup guard with no lock/unlock behavior.

Integration:
- Depends on `linux/cleanup.h`.

Risks:
- Provides no serialization; only preserves call structure.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/irqflags.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/jhash.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/jhash.h

Purpose: Jenkins 32-bit hash implementation.

Key APIs:
- `jhash_size()`, `jhash_mask()`.
- Internal mix/final macros `__jhash_mix`, `__jhash_final`.
- `jhash()` for byte sequences.
- `jhash2()` for u32 arrays.
- `jhash_1word`, `jhash_2words`, `jhash_3words`.

Integration:
- Depends on `linux/bitops.h` and unaligned packed-struct access.

Behavior notes:
- Processes 12-byte blocks then final tail bytes.
- Hash result depends on endianness.
- Initial state uses `JHASH_INITVAL`, length, and caller seed.

Risks:
- Not cryptographic.
- Fallthrough switch style relies on compiler accepting intentional fallthrough.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/jhash.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/jiffies.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/jiffies.h

Purpose: Userspace jiffies/time comparison compatibility.

Key APIs:
- Wrap-safe time comparison macros for unsigned long and u64.
- `HZ` set to 1000.
- Conversion helpers between jiffies, msecs, and nsecs.
- `sched_clock()`, `local_clock()`, `ktime_get_ns()`.
- `jiffies` macro maps monotonic coarse clock ns to msec jiffies.

Integration:
- Uses `clock_gettime(CLOCK_MONOTONIC_COARSE)`.
- Depends on kernel/time/typecheck/types shims.

Risks:
- Jiffies are computed on demand, not a global tick counter.
- `jiffies_to_msecs()` and `msecs_to_jiffies()` are identity because `HZ=1000`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/jiffies.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/kernel.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/kernel.h

Purpose: Central userspace kernel compatibility header for types, constants, macros, string parsing declarations, qstr, and utility declarations.

Key APIs:
- Defines `gfp_t`, GFP flags, integer typedefs, `sector_t`, `phys_addr_t`.
- Bit and config macros: `BIT`, `BIT_ULL`, `IS_ENABLED`, `IS_BUILTIN`, `IS_MODULE`, `IS_REACHABLE`.
- Limits: `U8_MAX` through `S64_MIN`.
- Alignment and object macros: `ALIGN`, `PTR_ALIGN`, `ARRAY_SIZE`, `container_of`, `struct_group`.
- Panic/misc: `panic()`, `might_sleep()`, `cpu_relax()`.
- String conversion declarations and wrappers: `kstrtoul`, `kstrtol`, `kstrtoull`, `kstrtoll`, integer-width wrappers.
- Printbuf declarations: `prt_u64`, `prt_vprintf`, `prt_printf`.
- Hex digit arrays/macros.
- `struct qstr`, `QSTR_INIT`.
- `unsafe_memcpy`, `DECLARE_FLEX_ARRAY`, `copy_to_user`.

Integration:
- Includes many core shims: bug/cache/cleanup/compiler/dcache/kmsan/static_key, then math/minmax/byteorder.
- Other compatibility headers depend on it for basic kernel-like environment.

Risks:
- GFP flags mostly collapse to 0/1/2 and do not model kernel reclaim behavior.
- `copy_to_user()` is plain memcpy and cannot detect user faulting.
- `panic()` prints then calls `BUG()`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/kernel.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/key.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/key.h

Purpose: Minimal key retention and payload structure support.

Key types:
- `struct user_key_payload` with length and flexible data.
- `struct key` with atomic usage count, key serial, semaphore, and inline payload.

Key APIs:
- `user_key_payload()`
- `key_put()` decrements usage and frees at zero.
- `__key_get()`, `key_get()`.

Integration:
- Depends on `linux/types.h`, `linux/atomic.h`, and system `keyutils.h`.

Risks:
- Assumes keys are allocated with malloc-compatible storage.
- No lookup, permissions, keyring, or payload mutation API.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/key.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/kmemleak.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/kmemleak.h

Purpose: Kmemleak annotation compatibility.

Key APIs:
- Under `CONFIG_DEBUG_KMEMLEAK`, declares kmemleak allocation/free/ignore/scan APIs.
- Without it, all APIs are inline no-ops.
- Recursive helpers skip tracing when `SLAB_NOLEAKTRACE` is set.
- `kmemleak_erase()` nulls a pointer only in debug implementation; no-op otherwise.

Integration:
- Depends on `slab` and `vmalloc` shims.

Risks:
- In normal userspace builds annotations provide no leak detection.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/kmemleak.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/kmsan-checks.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/kmsan-checks.h

Purpose: KMSAN annotation compatibility.

Key APIs:
- Under `CONFIG_KMSAN`, declares poison/unpoison/check/copy/memmove hooks.
- Otherwise all hooks are no-op inline functions.

Integration:
- Included by `linux/kernel.h`.

Risks:
- In normal tools builds memory-initialization annotations do nothing.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/kmsan-checks.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/kobject.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/kobject.h

Purpose: Minimal kobject/sysfs object model for userspace bcachefs tooling.

Key types:
- `struct kobj_type` with release/sysfs/default group callbacks.
- `struct kobj_attribute` with show/store callbacks.
- `struct kobject` with name, parent, type, atomic ref, state flags, and dynamic arrays for subdirs/files/bin_files.
- `enum kobject_action`.

Key APIs:
- `kobject_init`, `kobject_get`, `kobject_add`, `kobject_del`, `kobject_put`.
- `kobject_uevent_env()` no-op.
- `sysfs_read_or_html_dirlist()`, `sysfs_write()`.
- `fs_kobj` defined as NULL.

Integration:
- Uses `util/darray.h` to store userspace sysfs tree children.

Risks:
- Uevents are ignored.
- This is a userspace approximation, not kernel kobject lifetime/sysfs behavior.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/kobject.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/kthread.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/kthread.h

Purpose: Declares userspace equivalents for kernel thread and kthread work APIs.

Key APIs:
- Thread lifecycle: `kthread_create`, `kthread_create_on_cpu`, `kthread_run`, `kthread_stop`, `kthread_should_stop`, park/freezer/data helpers.
- Worker types: `struct kthread_worker`, `struct kthread_work`.
- Init macros: `KTHREAD_WORKER_INIT`, `KTHREAD_WORK_INIT`, `DEFINE_KTHREAD_WORKER`, `DEFINE_KTHREAD_WORK`.
- Runtime APIs: `__init_kthread_worker`, `init_kthread_worker`, `init_kthread_work`, `kthread_worker_fn`, `queue_kthread_work`, flush functions.

Integration:
- Depends on err, lockdep, sched, spinlock, list.
- `kthread_run()` creates then calls `wake_up_process()`.

Risks:
- Real behavior is external; header only defines shapes and wrappers.
- CPU-specific creation cannot guarantee kernel-style CPU binding unless implementation does so.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/kthread.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/list.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/list.h

Purpose: Maps Linux list/hlist API to Userspace RCU `cds_list`/`cds_hlist`.

Key APIs:
- `list_head`, initialization, add/delete/replace/move/splice/entry/iteration macros map to `urcu/list.h`.
- Adds helpers: `list_empty_careful`, `list_move_tail`, `list_splice_init`, `list_splice_tail`, `list_splice_tail_init`, `list_last_entry`, `list_first_entry_or_null`, reverse-safe iteration, `list_count_nodes`, `list_is_last`.
- Hlist mappings and helpers: `hlist_head`, `hlist_node`, add/delete, `hlist_unhashed`, `hlist_del_init`, entry and iteration macros.

Integration:
- Depends on liburcu list/hlist headers.

Risks:
- Semantics follow liburcu implementation, not necessarily every kernel debug/list-hardening behavior.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/list.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/list_nulls.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/list_nulls.h

Purpose: Implements Linux hlist-null marker list variant.

Key APIs:
- `struct hlist_nulls_head`, `struct hlist_nulls_node`.
- `NULLS_MARKER`, init macros.
- `is_a_nulls()`, `get_nulls_value()`.
- `hlist_nulls_unhashed`, lockless variant, empty check.
- `hlist_nulls_add_head`, `hlist_nulls_del`.
- Iteration macros.

Integration:
- Depends on poison constants, const macros, and READ/WRITE_ONCE.

Behavior notes:
- End of list is encoded as low-bit nulls marker, not NULL.
- Delete poisons `pprev` with `LIST_POISON2`.

Risks:
- Requires stored object alignment so low bit distinguishes marker vs pointer.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/list_nulls.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/llist.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/llist.h

Purpose: Lockless singly-linked list API.

Key types:
- `struct llist_head`, `struct llist_node`.

Key APIs:
- Init: `LLIST_HEAD_INIT`, `LLIST_HEAD`, `init_llist_head`.
- Iteration over removed batches: `llist_for_each`, safe and entry variants.
- State/access: `llist_empty`, `llist_next`.
- Mutation: external `llist_add_batch`, inline `llist_add`, inline `llist_del_all`, external `llist_del_first`, `llist_reverse_order`.

Integration:
- Depends on atomic and kernel helpers; uses `xchg` for deleting all entries.

Behavior notes:
- Multiple producers can add while a consumer drains all entries.
- Deleted-all order is newest to oldest unless reversed.

Risks:
- Multiple consumers using `llist_del_first` need extra locking.
- Iteration is safe only after entries are removed from the live list.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/llist.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/lockdep.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/lockdep.h

Purpose: Stubs kernel lock dependency tracking.

Key APIs:
- Defines empty `struct lock_class_key`.
- Lock acquire/release/class/assert macros are no-ops.
- Debug display/check functions are inline no-ops.
- `lock_class_is_held()` returns 0.

Integration:
- Lets locking code compile without lockdep.

Risks:
- No deadlock detection, class validation, or held-lock assertions in userspace.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/lockdep.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/log2.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/log2.h

Purpose: Base-2 logarithm, power-of-two, bit-width, and allocation-order helpers.

Key APIs:
- `__ilog2_u32`, `__ilog2_u64`.
- `is_power_of_2`.
- `__roundup_pow_of_two`, `__rounddown_pow_of_two`.
- Constant-capable `const_ilog2`, `ilog2`, `roundup_pow_of_two`, `rounddown_pow_of_two`.
- `order_base_2`, `bits_per`, `get_order`.

Integration:
- Depends on `linux/types.h` and `linux/bitops.h`.

Behavior notes:
- Many macros have constant-expression paths for compile-time initialization.
- Some results are undefined for zero input, matching kernel behavior.

Risks:
- Callers must avoid zero where documented undefined.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/log2.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/lz4.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/lz4.h

Purpose: Adapts system LZ4 API to kernel-like call signatures.

Key APIs:
- Includes `<lz4.h>`.
- `LZ4_compress_destSize(src,dst,srclen,dstlen,workspace)` maps to 4-arg system function.
- `LZ4_compress_HC(...)` returns -1.
- Defines compression workspace and HC level constants as 0.

Risks:
- High-compression LZ4 is unsupported through this shim.
- Workspace arguments are ignored.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/lz4.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/math.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/math.h

Purpose: Kernel-style integer rounding, division, scaling, and math helpers.

Key APIs:
- `round_up`, `round_down`, `roundup`, `rounddown`.
- `DIV_ROUND_UP`, `DIV_ROUND_UP_ULL`, `DIV_ROUND_CLOSEST`, `DIV_ROUND_CLOSEST_ULL`, sector variants.
- `mult_frac`, `sector_div`, `reciprocal_scale`.
- External `int_pow`, `int_sqrt`; conditional `int_sqrt64`.
- Kernel-style `abs()` macro.

Integration:
- Depends on `linux/kernel.h`; uses `do_div` from math64 path.

Risks:
- Macro arguments and signedness require care despite some single-evaluation patterns.
- Division helpers assume nonzero divisors.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/math.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/math64.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/math64.h

Purpose: 64-bit division and multiply-shift helpers.

Key APIs:
- `do_div(n, base)` updates dividend and returns remainder.
- `div_u64_rem`, `div_s64_rem`, `div64_u64_rem`.
- `div64_u64`, `div64_s64`, `div_u64`, `div_s64`.
- `mul_u32_u32`.
- `mul_u64_u64_shr` with `__int128` fast path or manual 64x64 to 128-bit multiplication.

Integration:
- Depends on `linux/kernel.h`.

Risks:
- Division by zero is not guarded.
- Manual multiply path is endian-conditional and depends on correct `__BIG_ENDIAN`/layout macros.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/math64.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/mempool.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/mempool.h

Purpose: Declares Linux mempool API for guaranteed-reserve allocations.

Key types:
- `mempool_alloc_t`, `mempool_free_t`.
- `mempool_t` with spinlock, minimum/current counts, element cache, callbacks, and wait queue.

Key APIs:
- Init/create/resize/destroy/exit: `mempool_init*`, `mempool_create*`, `mempool_resize`, `mempool_destroy`, `mempool_exit`.
- Allocation: `mempool_alloc()` wrapper over `mempool_alloc_noprof()`, `mempool_free()`.
- Callback helpers for slab, kmalloc, and page pools.

Integration:
- Depends on wait, compiler, slab shims.
- Implementations are external.

Risks:
- Header declares reserve-pool mechanics but correctness depends on implementation honoring min reserve and waiting behavior.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/mempool.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/min_heap.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/min_heap.h

Purpose: Generic typed min-heap implementation with inline and external variants.

Key types:
- `MIN_HEAP_PREALLOCATED(type,name,n)` and `DEFINE_MIN_HEAP`.
- `min_heap_char` untyped backing alias.
- `struct min_heap_callbacks { less, swp }`.

Key APIs:
- Inline: init, peek, full, sift down/up, heapify, pop, pop-push, push, delete.
- External counterparts with the same operations.
- Public macros cast typed heap to `min_heap_char` and pass element size.

Behavior notes:
- Default swap selects 64-bit, 32-bit, or byte swapping based on alignment and size.
- Sift-down uses bottom-up path selection/backtracking.
- Push/pop/delete validate full/empty states with `WARN_ONCE`.

Integration:
- Depends on bug/string/types and type-casting macros.

Risks:
- Callback `less` must define a stable strict ordering.
- Pointer arithmetic on `void *` relies on GNU C.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/min_heap.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/minmax.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/minmax.h

Purpose: Type-aware min/max/clamp/range helpers.

Key APIs:
- `min`, `max`, `umin`, `umax`, `min3`, `max3`.
- `min_t`, `max_t`, `min_not_zero`.
- `clamp`, `clamp_t`, `clamp_val`.
- `min_array`, `max_array`.
- `in_range`, `in_range32`, `in_range64`.
- `swap`, uppercase unsafe constant macros.

Behavior notes:
- Uses `__auto_type` temporaries to avoid multiple evaluation.
- Signed/unsigned compatibility is enforced by helper expressions and constant checks.
- `in_range()` uses subtraction form and explicitly differs from `start <= val && val < start + len` on overflow.

Risks:
- Empty arrays are invalid for min/max array macros.
- Uppercase `MIN/MAX` evaluate arguments multiple times.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/minmax.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/mm.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/mm.h

Purpose: Userspace memory information compatibility.

Key APIs:
- Defines kernel-layout-compatible `struct sysinfo`.
- `si_meminfo()` calls `syscall(SYS_sysinfo)` and BUGs on error.
- External `_totalram_pages`; `totalram_pages()` returns it.
- `si_mem_available()` returns free RAM in pages.
- `mem_alloc_profiling_enabled()` false.

Integration:
- Depends on syscall/unistd, bug, and types shims.
- Struct padding is chosen to match kernel syscall layout, especially 32-bit.

Risks:
- `si_mem_available()` uses `freeram`, not kernel’s full available-memory heuristic.
- BUG on syscall failure is abrupt for tooling.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/mm.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/module.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/module.h

Purpose: Stubs Linux module metadata and maps module init to userspace constructors.

Key APIs:
- `module_init(initfn)` emits constructor that BUGs if init returns nonzero.
- `module_exit(exitfn)` defines an unused wrapper, not a destructor.
- `MODULE_*` metadata macros are no-ops.
- Module ref helpers no-op or return success.
- Kernel param structs and ops definitions.
- `param_set_bool()` calls `kstrtobool()`.

Integration:
- Includes kernel/stat/compiler/export.

Risks:
- Module exit is intentionally not run automatically.
- Module ownership/refcount behavior is absent.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/module.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/moduleparam.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/moduleparam.h

Purpose: Compatibility wrapper for module parameter definitions.

Key APIs:
- Includes `linux/module.h`.

Integration:
- All parameter types/macros come from `module.h`.

Risks:
- No additional functionality beyond include indirection.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/moduleparam.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/mutex.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/mutex.h

Purpose: Maps Linux mutex API to pthread mutexes.

Key APIs:
- `struct mutex { pthread_mutex_t lock; }`
- `DEFINE_MUTEX`
- `mutex_init`, `mutex_lock`, `mutex_trylock`, `mutex_unlock`
- Defines cleanup guard `mutex`.

Integration:
- Depends on pthreads and `cleanup.h` indirectly for `DEFINE_GUARD`.

Risks:
- No kernel mutex owner tracking, interruptible locking, or lockdep.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/mutex.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/osq_lock.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/osq_lock.h

Purpose: Stub optimistic spin queue lock structures.

Key APIs:
- `struct optimistic_spin_node`.
- `struct optimistic_spin_queue { atomic_t tail; }`.
- `OSQ_LOCK_UNLOCKED`, `osq_lock_init()`, `osq_is_locked()`.
- `osq_lock()` always false; `osq_unlock()` no-op.

Integration:
- Used by code that conditionally supports optimistic spinning.

Risks:
- Optimistic spinning never succeeds in userspace through this shim.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/osq_lock.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/overflow.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/overflow.h

Purpose: Overflow-safe arithmetic and allocation-size helpers.

Key APIs:
- Type bounds: `type_max`, `type_min`.
- Overflow checks: `check_add_overflow`, `check_sub_overflow`, `check_mul_overflow`, `check_shl_overflow`.
- Intentional wrapping helpers for add/sub/mul and assign forms.
- Fit/cast helpers: `overflows_type`, `castable_to_type`.
- Saturating size helpers: `size_mul`, `size_add`, `size_sub`, `array_size`, `array3_size`, `flex_array_size`, `struct_size`, `struct_size_t`.
- On-stack flexible object helpers: `DEFINE_RAW_FLEX`, `DEFINE_FLEX`.

Integration:
- Depends on compiler/limits/const and `__must_be_array`.

Behavior notes:
- Uses compiler builtins for arithmetic overflow.
- Size helpers saturate to `SIZE_MAX`.
- `DEFINE_FLEX` requires compile-time constant count.

Risks:
- `flex_array_size()` has a constant-expression path that can still rely on compile-time expression validity.
- `_Bool` arithmetic is explicitly considered an edge case.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/overflow.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/page.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/page.h

Purpose: Minimal page-size/page-address compatibility.

Key APIs:
- Defaults `PAGE_SIZE` to 4096 and `PAGE_SHIFT` to 12 if absent.
- `PAGE_MASK`, `linux_page_size`.
- `virt_to_page`, `offset_in_page`, `page_address`.
- `kmap_atomic`, `kunmap_atomic`, `kmap_local_page`, `kunmap_local`.
- `PageHighMem()` false.
- Static `zero_page` and `ZERO_PAGE()`.

Integration:
- Includes `<sys/user.h>`.

Risks:
- `struct page *` is only an address reinterpretation; no page metadata exists.
- Fixed 4 KiB fallback may mismatch host page size if not predefined.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/page.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/pagemap.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/pagemap.h

Purpose: Defines page-cache readahead page count.

Key APIs:
- `VM_READAHEAD_PAGES (SZ_128K / PAGE_SIZE)`.

Integration:
- Depends on prior definitions of `SZ_128K` and `PAGE_SIZE`.

Risks:
- No include guard or includes; must be included in a context that already defines required size/page macros.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/pagemap.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/percpu-refcount.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/percpu-refcount.h

Purpose: Simplified percpu refcount API backed by one atomic long.

Key types:
- `struct percpu_ref` with `atomic_long_t count`, release callback, and confirm callback pointer.

Key APIs:
- `percpu_ref_init`, `percpu_ref_exit`.
- Get/tryget: `percpu_ref_get_many`, `percpu_ref_get`, `percpu_ref_tryget`, `percpu_ref_tryget_live`.
- Put/kill/reinit: `percpu_ref_put_many`, `percpu_ref_put`, `percpu_ref_reinit`, `percpu_ref_kill`.
- State: `percpu_ref_is_zero`, `percpu_ref_is_dying`.

Behavior notes:
- `PERCPU_REF_INIT_DEAD` starts count at 0; otherwise starts at 1.
- Release callback runs when decrement reaches zero.
- Atomic/percpu mode flags are defined but not represented in the struct.

Risks:
- Does not implement kernel percpu fast path or mode switching.
- `tryget_live()` cannot distinguish killed from merely nonzero.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/percpu-refcount.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/percpu-rwsem.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/percpu-rwsem.h

Purpose: Simplified percpu read/write semaphore backed by a pthread mutex.

Key APIs:
- `struct percpu_rw_semaphore { pthread_mutex_t lock; }`
- Read and write lock/unlock APIs all lock/unlock the same mutex.
- Trylock uses `pthread_mutex_trylock`.
- Init/free/assert helpers.
- Cleanup guards: `percpu_read`, conditional `percpu_read_try`, and `percpu_write`.

Integration:
- Depends on pthread, cleanup, and preempt shims.

Risks:
- Read locks are exclusive, not shared.
- No percpu reader scalability or kernel rwsem semantics.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/percpu-rwsem.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/percpu.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/percpu.h

Purpose: Userspace implementation surface for static and dynamic percpu storage.

Key APIs and state:
- Allocation: `__alloc_percpu_gfp`, `__alloc_percpu`, `free_percpu`, `alloc_percpu*`.
- Static percpu: `DEFINE_PER_CPU` places variables in `bch_percpu` section; `DECLARE_PER_CPU`.
- Globals: section bounds, TLS current chunk/id, global chunk registry, CPU count, static size.
- Init/register: `bch_percpu_thread_init`, `bch_percpu_register`.
- Addressing: `this_cpu_ptr`, `per_cpu_ptr`, `raw_cpu_ptr`.
- Per-cpu operations: raw and this-cpu read/write/add/and/or/xchg/cmpxchg/cmpxchg_double and inc/dec variants.

Behavior notes:
- Each thread lazily gets a private chunk on first `this_cpu_ptr()` access.
- Dynamic percpu allocations are encoded as small offsets into each chunk’s dynamic arena.
- Static section pointers are resolved by subtracting `__start_bch_percpu`.

Integration:
- Coupled to `cpumask.h`, atomic size-specific helpers, and external percpu implementation.

Risks:
- Fixed `BCH_PERCPU_MAX_CPUS` and `BCH_PERCPU_DYNAMIC_SIZE`.
- Some macro paths rely on size-specific helper names existing.
- Correctness depends on every thread registering/getting a chunk before cross-thread access.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/percpu.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/poison.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/poison.h

Purpose: Defines kernel poison pointer and byte constants.

Key APIs:
- `POISON_POINTER_DELTA`.
- List poisons: `LIST_POISON1`, `LIST_POISON2`.
- Page/slab/free/redzone poison bytes.
- Various subsystem poison constants, including VFS, net, BPF, mutex, stack depot.

Integration:
- Used by list-null deletion and allocation/debug compatibility code.

Risks:
- Poison values are diagnostic only; userspace mapping behavior may vary.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/poison.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/posix_acl.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/posix_acl.h

Purpose: Defines in-memory POSIX ACL constants and structures.

Key APIs:
- ACL type/tag/permission constants.
- `struct posix_acl_entry` with tag, permission, and uid/gid union.
- `struct posix_acl` with RCU head, count, and flexible entries.

Integration:
- Depends on bug, slab, and rcupdate shims.

Risks:
- No refcount helpers, validation, or conversion functions are defined here.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/posix_acl.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/posix_acl_xattr.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/posix_acl_xattr.h

Purpose: Defines xattr wire format for POSIX ACLs.

Key APIs:
- `POSIX_ACL_XATTR_VERSION`.
- `posix_acl_xattr_entry` with little-endian tag/perm/id.
- `posix_acl_xattr_header` with version and flexible entries.
- Extern no-op ACL xattr handlers: `nop_posix_acl_access`, `nop_posix_acl_default`.

Integration:
- Includes `uapi/linux/xattr.h`.

Risks:
- Conversion between in-memory ACL and xattr format is not provided.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/posix_acl_xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/prandom.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/prandom.h

Purpose: Pseudo-random API compatibility mapped to real random bytes.

Key APIs:
- `prandom_bytes()` calls `get_random_bytes()`.
- Generated `prandom_int`, `prandom_long`, `prandom_u32`, `prandom_u64`.
- `prandom_u32_max(max)` returns modulo-reduced value.

Integration:
- Depends on `linux/random.h`.

Risks:
- `prandom_u32_max()` has modulo bias and no guard for `max == 0`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/prandom.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/preempt.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/preempt.h

Purpose: Declares userspace preemption serialization hooks and stubs migration control.

Key APIs:
- External `preempt_disable()`, `preempt_enable()`.
- No-resched/notrace variants map to those hooks.
- `preemptible()` returns 0.
- `migrate_disable()`/`migrate_enable()` are no-ops.
- Cleanup guards: `preempt`, `preempt_notrace`.

Behavior notes:
- Comments explain migration disable must not serialize long transactions in userspace to avoid deadlocks.

Integration:
- Depends on cleanup and irqflags.

Risks:
- CPU migration pinning semantics are absent.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/preempt.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/prefetch.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/prefetch.h

Purpose: Stubs prefetch hints.

Key APIs:
- `prefetch(p)` and `prefetchw(p)` evaluate the pointer into an unused temporary.

Risks:
- No hardware prefetch instruction is emitted.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/prefetch.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/pretty-printers.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/pretty-printers.h

Purpose: Declares printbuf helpers for options and bitflags.

Key APIs:
- `prt_string_option(struct printbuf *, const char * const[], size_t)`
- `prt_bitflags(struct printbuf *, const char * const[], u64)`

Integration:
- Relies on `struct printbuf` and `u64` being visible from includer context.

Risks:
- No include guard dependencies are pulled in for types; includer must provide them.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/pretty-printers.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/printk.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/printk.h

Purpose: Kernel printk/pr_* logging compatibility.

Key APIs:
- Kernel loglevel prefixes and `pr_fmt`.
- `vscnprintf`, `scnprintf`.
- External `vprintk`, `printk`, `dump_stack`.
- `no_printk`.
- `pr_emerg` through `pr_debug`, plus `_once` and `_ratelimited` variants.
- `printk_once`, `printk_deferred_once`, `printk_ratelimited`.

Integration:
- Ratelimited macros depend on ratelimit state definitions from `linux/ratelimit.h`; this file is mutually related to that header.
- Debug logging compiles out unless `DEBUG` or dynamic debug is enabled.

Risks:
- `printk_deferred_once` references `printk_deferred`, which must exist or be macro-defined in included context if used.
- Severity prefixes are strings; routing is implementation-defined in `printk`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/printk.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/random.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/random.h

Purpose: Random byte and bounded integer helpers for userspace.

Key APIs:
- `getrandom()` wrapper: syscall if available, otherwise reads external `urandom_fd`.
- `get_random_bytes()` BUGs unless requested bytes are fully read.
- Generated `get_random_int/long/u8/u16/u32/u64`.
- `get_random_u32_below()`, `__get_random_u32_below()`, `get_random_u64_below()`.

Integration:
- Depends on bug/kernel/log2/math64.
- Uses Linux `SYS_getrandom` when present.

Behavior notes:
- Bounded random helpers use multiply-high rejection to reduce modulo bias.
- Ceil <= 1 returns 0.

Risks:
- Partial reads or syscall failure trigger BUG.
- Fallback depends on `urandom_fd` being initialized externally.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/random.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/ratelimit.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/ratelimit.h

Purpose: Ratelimit state and helpers for printk/WARN throttling.

Key types:
- `struct ratelimit_state` with raw spinlock, interval, burst, remaining count, missed count, flags, and begin time.

Key APIs:
- Init macros and `DEFINE_RATELIMIT_STATE`.
- External `___ratelimit()`, macro `__ratelimit()`.
- `ratelimit_state_init`, `ratelimit_default_init`.
- Miss counters and interval reset.
- `ratelimit_state_exit`, `ratelimit_set_flags`.
- `WARN_ON_RATELIMIT`, `WARN_RATELIMIT`.

Integration:
- Depends on printk, sched/current, spinlock, jiffies constants.

Risks:
- Correct suppression/window behavior depends on external `___ratelimit`.
- If `RATELIMIT_MSG_ON_RELEASE` is set, exit logs through `current->comm`.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/ratelimit.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/rculist.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/rculist.h

Purpose: Maps Linux RCU hlist APIs to Userspace RCU list APIs.

Key APIs:
- Includes `urcu/rculist.h` and `urcu/rcuhlist.h`.
- Maps `hlist_add_head_rcu`, `hlist_del_rcu`, `hlist_for_each_rcu`, `hlist_for_each_entry_rcu`.

Integration:
- Depends on liburcu.

Risks:
- Only a small subset of RCU list helpers is mapped.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/rculist.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/rcupdate.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/rcupdate.h

Purpose: RCU compatibility layer over Userspace RCU.

Key APIs:
- `rcu_dereference_*`, `rcu_access_pointer`, `RCU_INIT_POINTER`.
- `kfree_rcu`, `kvfree_rcu` variants immediately call `kfree`.
- `rcu_head_init`, `rcu_head_after_call_rcu`.
- Defines cleanup guard `rcu` around `rcu_read_lock()`/`rcu_read_unlock()`.

Integration:
- Includes `<urcu.h>`, compiler, cleanup.

Risks:
- Immediate `kfree_rcu` is marked `XXX` and does not wait for grace periods.
- Code requiring deferred free semantics may be unsafe unless lifetime is otherwise controlled.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/rcupdate.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/refcount.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/refcount.h

Purpose: Reference count type and operations modeled after Linux `refcount_t`.

Key types:
- `refcount_t` wraps `atomic_t refs`.

Key APIs:
- Init/read/set: `REFCOUNT_INIT`, `refcount_set`, `refcount_read`.
- Increment: `refcount_add_not_zero`, `refcount_add`, `refcount_inc_not_zero`, `refcount_inc`.
- Decrement: `refcount_sub_and_test`, `refcount_dec_and_test`, `refcount_dec`.
- External helpers: `refcount_dec_if_one`, `refcount_dec_not_one`, lock-taking decrement helpers.

Behavior notes:
- Header documents kernel saturation semantics, but this userspace implementation mostly uses atomic operations without explicit saturation checks in shown inline code.
- Decrement-and-test uses release ordering and acquire after successful 1-to-0 transition.

Integration:
- Depends on atomic, bug, compiler, limits.

Risks:
- Inline functions do not enforce all documented saturation warnings/leak behavior.
- External helpers are required for lock-integrated decrement flows.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/refcount.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/rhashtable-types.h -->
# File Research: sources/cow-pools/bcachefs-tools/include/linux/rhashtable-types.h

Purpose: Defines resizable hash table type structures and init declarations.

Key types:
- `struct rhash_head`, `struct rhlist_head`.
- Function pointer typedefs for hash and compare callbacks.
- `struct rhashtable_params`.
- `struct rhashtable` with table pointer, config, work item, mutex, spinlock, and element count.
- `struct rhltable`, `struct rhashtable_walker`, `struct rhashtable_iter`.

Key APIs:
- `rhashtable_init()`
- `rhltable_init()`

Integration:
- Depends on atomic, compiler, mutex, workqueue, spinlock/list types.

Risks:
- This header only defines types and initialization declarations; insert/lookup/remove behavior must come from other rhashtable headers/implementations.
<!-- END FILE RESEARCH: sources/cow-pools/bcachefs-tools/include/linux/rhashtable-types.h -->