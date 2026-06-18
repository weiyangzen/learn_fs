# Research: subset-b-005920

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock.h

Purpose: Defines the generic Linux spinlock interface used by the Ceph client source snapshot. It is the umbrella header that selects SMP, UP, debug, and PREEMPT_RT behavior and exposes the public `raw_spin_*()`, `spin_*()`, `rwlock_*()` integration, atomic decrement-and-lock helpers, bucket lock allocation, and cleanup-based lock guards.

Important APIs/types/functions: `raw_spin_lock_init()`, `raw_spin_is_locked()`, `raw_spin_lock_irqsave()`, `raw_spin_unlock_irqrestore()`, `spinlock_check()`, `spin_lock_init()`, `spin_lock*()`, `spin_unlock*()`, `spin_trylock*()`, `spin_is_locked()`, `spin_is_contended()`, `assert_spin_locked()`, `spin_needbreak()`, `rwlock_needbreak()`, `atomic_dec_and_lock()`, `atomic_dec_and_raw_lock()`, `alloc_bucket_spinlocks()`, and many `DEFINE_LOCK_GUARD_1*()` guard classes.

Control flow: The header first pulls generic type declarations, then chooses architecture spin primitives from `<asm/spinlock.h>` on SMP or `spinlock_up.h` on UP. It wraps low-level `arch_spin_*()` operations in `do_raw_spin_*()` unless debug spinlocks provide out-of-line checking. It includes either `spinlock_api_smp.h` or `spinlock_api_up.h` for `_raw_*()` operations, then maps ordinary `spinlock_t` to raw spinlocks when `CONFIG_PREEMPT_RT` is disabled or includes `spinlock_rt.h` for sleeping RT locks.

State and persistence behavior: No persistent storage is managed here, but lock state is stored in `raw_spinlock_t`/`spinlock_t`, lockdep maps, debug ownership fields, IRQ flags, preemption counters, and memory-ordering barriers. `smp_mb__after_spinlock()` documents RCsc ordering expectations and defaults to `kcsan_mb()` if the architecture does not override it.

Dependencies: Depends on preemption, IRQ flags, bottom halves, lockdep, cleanup guards, architecture barriers, MMI/O write barriers, `spinlock_types.h`, `spinlock_api_{smp,up}.h`, and optionally `rwlock.h`/`spinlock_rt.h`. Kernel C annotations such as `__acquires`, `__releases`, and `typecheck()` are part of the contract.

Integration points: Used by most in-kernel synchronization users, including SSB headers in this subset. PREEMPT_RT integration is a major compatibility point: non-RT callers get raw spinning semantics while RT callers get rtmutex-backed `spinlock_t` semantics. Cleanup guard macros allow lexical lock management via compiler cleanup infrastructure.

Risks: Misusing IRQ-save flags, mixing raw and regular locks, relying on `spin_is_locked()` for synchronization, or assuming `spinlock_t` always spins can break across UP/debug/RT configurations. Architecture implementations must satisfy the documented memory ordering after lock acquisition.

Test signals: Build coverage across `CONFIG_SMP`, UP, `CONFIG_DEBUG_SPINLOCK`, `CONFIG_DEBUG_LOCK_ALLOC`, and `CONFIG_PREEMPT_RT`; lockdep tests for nested and nest-lock paths; KCSAN/RCU scheduler tests for `smp_mb__after_spinlock()` ordering; runtime stress using `atomic_dec_and_lock*()` and guard-class lock/unlock balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_api.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock_api.h

Purpose: Compatibility shim that includes `linux/spinlock.h`. It exists so code including the older or narrower `spinlock_api.h` name receives the full generic spinlock API.

Important APIs/types/functions: Exports no definitions of its own; all visible symbols come from `spinlock.h`.

Control flow: A single preprocessor include redirects users to the canonical header.

State and persistence behavior: No state.

Dependencies: Entirely dependent on `linux/spinlock.h`.

Integration points: Source compatibility for call sites expecting `spinlock_api.h`.

Risks: Direct include can hide accidental dependency on the umbrella spinlock header; any semantic change is inherited from `spinlock.h`.

Test signals: Compile-only tests that include `spinlock_api.h` without separately including `spinlock.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_api_smp.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock_api_smp.h

Purpose: Declares and optionally inlines raw spinlock operations for SMP or debug builds. It is internal to `spinlock.h` and guarded against direct inclusion.

Important APIs/types/functions: `_raw_spin_lock()`, `_raw_spin_lock_nested()`, `_raw_spin_lock_nest_lock()`, `_raw_spin_lock_bh()`, `_raw_spin_lock_irq()`, `_raw_spin_lock_irqsave()`, `_raw_spin_trylock()`, `_raw_spin_trylock_irq()`, `_raw_spin_trylock_irqsave()`, `_raw_spin_unlock*()`, `_raw_spin_trylock_bh()`, and `in_lock_functions()`.

Control flow: Function prototypes are provided for out-of-line implementations in `kernel/spinlock.c`. Configuration macros such as `CONFIG_INLINE_SPIN_LOCK` redirect public `_raw_*()` names to inline `__raw_*()` functions. Inline lock acquisition disables preemption or interrupts/bottom halves, records lockdep acquisition, then calls `LOCK_CONTENDED()` with `do_raw_spin_trylock()`/`do_raw_spin_lock()`. Unlock releases lockdep state, performs raw unlock, then restores preemption/IRQ/BH state.

State and persistence behavior: Updates preemption counters, local IRQ/BH disable state, lockdep maps, and architecture lock words. Trylock paths restore state on failure.

Dependencies: Requires `spinlock.h` to provide `raw_spinlock_t`, `do_raw_spin_*()`, lockdep helpers, local IRQ/BH helpers, and architecture implementations.

Integration points: Included by `spinlock.h` for SMP and debug spinlock builds. Pulls in `rwlock_api_smp.h` when PREEMPT_RT is not active.

Risks: Ordering and state restoration bugs can leave preemption/IRQs disabled or lockdep inconsistent. Lockdep intentionally avoids lockbreak preempt-spin ops in some configurations, so timing differs by config.

Test signals: Lockdep acquisition/release tests, trylock failure tests verifying IRQ/BH/preempt restoration, SMP contention stress, and builds for all inline/uninline configuration combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_api_smp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_api_up.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock_api_up.h

Purpose: Implements raw spinlock and rwlock APIs for UP non-debug builds, where no real inter-CPU exclusion is required but compiler annotations, IRQ state, bottom-half state, and preemption accounting still matter.

Important APIs/types/functions: Macro implementations for `_raw_spin_lock*()`, `_raw_read_lock*()`, `_raw_write_lock*()`, `_raw_spin_unlock*()`, read/write unlocks, trylock variants, `in_lock_functions()`, and `assert_raw_spin_locked()`.

Control flow: Lock macros disable preemption, IRQs, or bottom halves as requested, then issue sparse/lock annotations. Trylock variants always succeed after applying the corresponding state changes. Unlock macros reverse the state changes and release annotations.

State and persistence behavior: No hardware lock word is used in non-debug UP mode. Runtime state is limited to preempt count and local IRQ/BH state.

Dependencies: Must only be included from `spinlock.h`, and relies on preemption, IRQ, softirq, and sparse annotation helpers.

Integration points: Selected by `spinlock.h` when neither SMP nor debug spinlock support requires the SMP API path.

Risks: Since trylocks always succeed and lock state is not represented, code that incorrectly relies on lock contention behavior may pass on UP and fail on SMP. Incorrect flag variable types are caught by outer macros in `spinlock.h`.

Test signals: UP build tests, sparse lock annotation checks, and unit-like compile tests for all IRQ/BH/irqsave variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_api_up.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_rt.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock_rt.h

Purpose: Provides PREEMPT_RT semantics for `spinlock_t` by mapping regular spinlocks to rtmutex-backed sleeping locks while preserving the source-level spinlock API.

Important APIs/types/functions: `__spin_lock_init()`, `spin_lock_init()`, `local_spin_lock_init()`, `rt_spin_lock()`, `rt_spin_lock_nested()`, `rt_spin_lock_nest_lock()`, `rt_spin_unlock()`, `rt_spin_trylock()`, `rt_spin_trylock_bh()`, `spin_lock*()`, `spin_unlock*()`, `spin_trylock*()`, `spin_is_locked()`, and `assert_spin_locked()`.

Control flow: Initialization sets up the embedded `rt_mutex_base` and optional lockdep metadata. Normal lock operations call `rt_spin_lock()`; BH variants disable/enable bottom halves around the rt lock; IRQ and irqsave variants do not actually disable interrupts and set saved flags to zero because RT spinlocks may sleep.

State and persistence behavior: Lock state lives in the embedded rtmutex base and lockdep map. IRQ-save flags are intentionally synthetic. Contention is not reported through `spin_is_contended()`.

Dependencies: Requires `spinlock.h` inclusion context, `rtmutex.h` through `spinlock_types.h`, lockdep type checking, local BH helpers, and `rwlock_rt.h`.

Integration points: Included by `spinlock.h` when `CONFIG_PREEMPT_RT` is enabled. Callers that need true non-sleeping exclusion must use raw spinlocks, not regular `spinlock_t`.

Risks: Code assuming interrupts are disabled inside `spin_lock_irqsave()` or assuming locks cannot sleep is wrong on RT. Such code may deadlock or violate atomic context constraints.

Test signals: PREEMPT_RT build and runtime tests, lockdep nesting tests, atomic-context misuse detection, and tests that verify flags are handled safely by irqsave/restore call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_rt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_types.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock_types.h

Purpose: Defines the public `spinlock_t` type and initializers, selecting raw-spinlock-backed layout for non-RT kernels and rtmutex-backed layout for PREEMPT_RT kernels.

Important APIs/types/functions: `spinlock_t`, `__SPIN_LOCK_UNLOCKED()`, `DEFINE_SPINLOCK()`, `__LOCAL_SPIN_LOCK_UNLOCKED()` on RT, plus inclusion of `rwlock_types.h`.

Control flow: The preprocessor branches on `CONFIG_PREEMPT_RT`. Non-RT uses a union around `raw_spinlock_t` and optional lockdep overlay. RT includes `rtmutex.h` and defines `spinlock_t` as an `rt_mutex_base` plus optional lockdep map.

State and persistence behavior: Declares the memory layout for lock state. Non-RT state is a raw architecture lock and optional debug/lockdep metadata; RT state is rtmutex wait/owner state.

Dependencies: Depends on `spinlock_types_raw.h`, `rtmutex.h` when RT is enabled, and `rwlock_types.h`.

Integration points: Consumed by `spinlock.h` and any code that statically declares spinlocks.

Risks: Structure layout is configuration-dependent, so code must treat `spinlock_t` as opaque. Direct field access outside the locking implementation is fragile.

Test signals: Compile tests for static initializers in RT and non-RT builds; lockdep map offset assumptions; ABI-sensitive build checks in modules that embed `spinlock_t`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_types_raw.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock_types_raw.h

Purpose: Defines `raw_spinlock_t`, the low-level lock type used when callers require true spinning semantics and by regular spinlocks on non-RT kernels.

Important APIs/types/functions: `raw_spinlock_t`, `SPINLOCK_MAGIC`, `SPINLOCK_OWNER_INIT`, `RAW_SPIN_DEP_MAP_INIT()`, `SPIN_DEP_MAP_INIT()`, `LOCAL_SPIN_DEP_MAP_INIT()`, `SPIN_DEBUG_INIT()`, `__RAW_SPIN_LOCK_INITIALIZER()`, `__RAW_SPIN_LOCK_UNLOCKED()`, and `DEFINE_RAW_SPINLOCK()`.

Control flow: Selects architecture raw lock types from `<asm/spinlock_types.h>` on SMP or `spinlock_types_up.h` on UP, then layers debug ownership and lockdep metadata over `arch_spinlock_t`.

State and persistence behavior: Raw lock state is the architecture lock word plus optional debug magic, owner CPU, owner pointer, and dependency map. Static initializers define the persistent initial state for global locks.

Dependencies: Uses `linux/types.h`, architecture or UP spinlock types, and `lockdep_types.h`.

Integration points: Foundation for `spinlock_types.h`, `spinlock.h`, raw lock APIs, and synchronization in low-level code where sleeping is not allowed.

Risks: Debug and lockdep fields affect size/layout. Callers must not assume raw locks are interchangeable with `spinlock_t` under RT.

Test signals: Static initializer build tests, debug spinlock owner tracking, lockdep wait-type validation, and architecture-specific raw lock tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_types_raw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_types_up.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock_types_up.h

Purpose: Defines UP architecture spinlock and rwlock placeholder types for use under `spinlock_types_raw.h`.

Important APIs/types/functions: `arch_spinlock_t`, `__ARCH_SPIN_LOCK_UNLOCKED`, `arch_rwlock_t`, and `__ARCH_RW_LOCK_UNLOCKED`.

Control flow: With `CONFIG_DEBUG_SPINLOCK`, `arch_spinlock_t` stores a volatile integer with inverted semantics: `1` unlocked, `0` locked. Without debug, the type is empty. RW locks are empty in both modes.

State and persistence behavior: Only debug UP spinlocks carry a lock state value. Non-debug UP locks have no storage.

Dependencies: Must be included through `spinlock_types_raw.h`.

Integration points: Used by UP builds to satisfy generic lock type declarations without pulling architecture SMP primitives.

Risks: Empty lock storage means layout and behavior differ sharply from SMP; code must not inspect lock internals.

Test signals: UP debug and non-debug builds; compile checks for static lock initialization; debug tests that catch uninitialized or double-lock patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_types_up.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_up.h -->
# sources/distributed-fs/ceph-client/include/linux/spinlock_up.h

Purpose: Provides UP implementations of `arch_spin_*()` and `arch_rwlock_*()` primitives used by generic spinlock wrappers.

Important APIs/types/functions: `arch_spin_is_locked()`, `arch_spin_lock()`, `arch_spin_trylock()`, `arch_spin_unlock()`, `arch_spin_is_contended()`, and read/write lock macros.

Control flow: Debug UP spinlocks mutate the `slock` field and use compiler barriers to constrain instruction movement. Non-debug UP primitives are barrier-only no-ops, with trylocks always returning success. RW lock primitives are always barrier-only.

State and persistence behavior: Debug UP spinlocks store a simple locked/unlocked state; non-debug locks store none. Compiler barriers remain important for faulting memory accesses and code motion.

Dependencies: Requires inclusion from `spinlock.h` and uses `asm/processor.h`/`asm/barrier.h`.

Integration points: Selected by `spinlock.h` on non-SMP builds before the generic API layer wraps preemption and IRQ semantics.

Risks: The absence of atomic operations is correct only for UP. Bugs hidden by always-success trylocks can appear on SMP.

Test signals: UP debug lock misuse tests, compiler build coverage, and sparse lock annotation behavior through the upper API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spinlock_up.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/splice.h -->
# sources/distributed-fs/ceph-client/include/linux/splice.h

Purpose: Declares the kernel splice, tee, vmsplice, and direct file-range transfer interfaces plus descriptors used to move data between files, pipes, sockets, userspace memory, and page arrays.

Important APIs/types/functions: `SPLICE_F_*` flags, `struct splice_desc`, `struct partial_page`, `struct splice_pipe_desc`, `splice_actor`, `splice_direct_actor`, `splice_from_pipe()`, `__splice_from_pipe()`, `splice_to_pipe()`, `add_to_pipe()`, `vfs_splice_read()`, `splice_direct_to_actor()`, `do_splice()`, `do_splice_direct()`, `splice_file_range()`, `splice_copy_file_range()`, `do_tee()`, `splice_to_socket()`, `splice_grow_spd()`, `splice_shrink_spd()`, and pipe buffer ops exports.

Control flow: The header does not implement the splice loops, but its descriptors show the flow: pipe buffers and page descriptors are passed to actor callbacks, `splice_desc` tracks remaining/current length, file position, flags, and wakeup needs, and higher-level helpers route file-to-pipe, pipe-to-file, direct, tee, and socket transfers.

State and persistence behavior: Transfer state is transient in descriptors, file offsets, pipe buffers, page refs, and wakeup flags. No on-disk persistence is managed here.

Dependencies: Depends on `pipe_fs_i.h`, `struct file`, `struct page`, pipe buffer operations, and VFS file-position conventions.

Integration points: VFS `copy_file_range`, `sendfile`, socket splicing, pipes, and filesystem `splice_read`/`splice_write` implementations. Distributed filesystems such as Ceph can interact through VFS read/write/splice paths.

Risks: Mismanaging page ownership with `SPLICE_F_GIFT`, nonblocking semantics, EOF callbacks, or partial-page lengths can leak refs, block unexpectedly, or corrupt transfer accounting.

Test signals: Splice/tee/vmsplice syscall tests, nonblocking pipe tests, file offset preservation tests, socket splice tests, and filesystem-specific splice read/write coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/splice.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spmi.h -->
# sources/distributed-fs/ceph-client/include/linux/spmi.h

Purpose: Defines the System Power Management Interface bus model, including SPMI devices, controllers, drivers, command opcodes, registration helpers, and register access helpers.

Important APIs/types/functions: `SPMI_MAX_SLAVE_ID`, `SPMI_CMD_*`, `struct spmi_device`, `to_spmi_device()`, `spmi_device_alloc/add/remove/put()`, `struct spmi_controller`, controller command callbacks, `spmi_controller_alloc/add/remove/put()`, devm controller helpers, `struct spmi_driver`, `spmi_driver_register/unregister()`, `module_spmi_driver()`, `spmi_find_device_by_of_node()`, register read/write helpers, and reset/sleep/wakeup/shutdown command helpers.

Control flow: Controller drivers allocate and add a `spmi_controller` with callbacks for command/read/write transactions. Device instances attach to controllers by USID. Client drivers register `spmi_driver` objects and bind through the driver model. Helper functions route standard register operations to controller callbacks with the right SPMI opcode.

State and persistence behavior: Runtime state is in embedded `struct device` objects, controller number, USID, driver data, and controller callbacks. Power state transitions are represented by SLEEP/WAKEUP/SHUTDOWN commands, not persistent storage.

Dependencies: Uses Linux device model, module ownership, OF node lookup, and `mod_devicetable.h`.

Integration points: PMIC and power-management devices on SPMI buses; runtime PM can issue SLEEP and WAKEUP commands as described in driver comments.

Risks: Invalid USID/opcode/length combinations can fail bus transactions. Controller callbacks must validate address widths and transfer sizes. Runtime PM balancing in client probe/remove must match command-side behavior.

Test signals: Controller registration tests, OF matching, client probe/remove, register read/write opcodes including extended long address paths, and runtime suspend/resume command traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/spmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sprintf.h -->
# sources/distributed-fs/ceph-client/include/linux/sprintf.h

Purpose: Declares kernel formatted-printing and scanning APIs plus pointer hashing controls.

Important APIs/types/functions: `num_to_str()`, `sprintf()`, `vsprintf()`, `snprintf()`, `vsnprintf()`, `scnprintf()`, `vscnprintf()`, `kasprintf()`, `kvasprintf()`, `kvasprintf_const()`, `sscanf()`, `vsscanf()`, `no_hash_pointers`, `hash_pointers_finalize()`, and `rust_fmt_argument()`.

Control flow: The header supplies prototypes with `__printf`/`__scanf` compiler format checking. Implementations elsewhere format into caller buffers, allocate formatted strings, parse input strings, and handle `%p` pointer hashing policy.

State and persistence behavior: Formatting state is transient. `no_hash_pointers` and hash finalization affect global pointer-display policy.

Dependencies: Requires compiler attributes, kernel types, `stdarg.h`, GFP allocation types, and Rust formatting integration for `%pA`.

Integration points: Kernel logging, sysfs/proc/debugfs text generation, allocation formatting, and Rust-to-C formatting support.

Risks: `sprintf()` can overflow if callers do not size buffers; pointer formatting can leak addresses if hashing is disabled or not finalized correctly; format-string mismatches should be caught by attributes.

Test signals: Format compiler warnings, lib/vsprintf tests, pointer hashing tests, allocation-failure tests for `kasprintf`, and Rust `%pA` formatting tests where enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sprintf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sram.h -->
# sources/distributed-fs/ceph-client/include/linux/sram.h

Purpose: Declares a generic SRAM executable-copy helper.

Important APIs/types/functions: `sram_exec_copy(struct gen_pool *pool, void *dst, void *src, size_t size)`.

Control flow: When `CONFIG_SRAM_EXEC` is enabled, an external implementation copies executable content into SRAM from a gen_pool-backed allocation. Otherwise the inline stub returns `NULL`.

State and persistence behavior: No state in the header; implementation likely affects SRAM contents and instruction-cache coherency.

Dependencies: Forward-declares `struct gen_pool` and uses `size_t`.

Integration points: Platform code needing to execute small routines from SRAM, often for low-power or timing-sensitive paths.

Risks: Callers must handle `NULL` when SRAM execution is disabled or unavailable. Executable memory copying requires cache, permissions, and pool-lifetime correctness.

Test signals: Build coverage with and without `CONFIG_SRAM_EXEC`; platform tests validating copied code executes and fallback paths handle `NULL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sram.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/srcu.h -->
# sources/distributed-fs/ceph-client/include/linux/srcu.h

Purpose: Defines the public Sleepable RCU API for synchronization domains whose readers may sleep. It selects tiny or tree SRCU implementations and exposes read-side, update-side, callback, polling, flavor-checking, dereference, and cleanup guard helpers.

Important APIs/types/functions: `init_srcu_struct*()`, `DEFINE_SRCU*()` from included implementations, `srcu_read_lock/unlock()`, `srcu_read_lock_fast/unlock_fast()`, `srcu_read_lock_fast_updown/unlock_fast_updown()`, `srcu_down_read/up_read()`, NMI-safe and notrace variants, `call_srcu()`, `cleanup_srcu_struct()`, `synchronize_srcu()`, `synchronize_srcu_expedited()`, `srcu_barrier()`, `get_state_synchronize_srcu()`, `start_poll_synchronize_srcu()`, `poll_state_synchronize_srcu()`, `srcu_dereference*()`, and `DEFINE_LOCK_GUARD_1(srcu*)`.

Control flow: Public read locks validate the configured reader flavor, call implementation-specific `__srcu_read_lock*()`, and annotate lockdep. Unlock paths validate cookies/pointers, release lockdep state, and call implementation-specific unlock. Update-side APIs wait for or start grace periods, and polling cookies track grace-period completion state.

State and persistence behavior: SRCU domains maintain reader counters, callback queues, grace-period sequence state, lockdep maps, and implementation-specific work/irq_work state. The read-lock return value or per-CPU counter pointer must be passed to the matching unlock.

Dependencies: Uses mutexes, RCU core APIs, workqueues, segmented callback lists, lockdep, and either `srcutiny.h` or `srcutree.h`.

Integration points: Subsystems that need sleepable read-side critical sections, notifier chains, pointer dereference checking, and callback deferral. Distributed filesystem code can use SRCU for object lifetime and mount/session state protected across blocking paths.

Risks: Mixing reader flavors on one `srcu_struct`, unlocking in the wrong context for `srcu_read_lock()`, waiting for a grace period while inside a read-side section, or using fast readers when RCU is not watching can deadlock or violate ordering.

Test signals: RCU torture tests, lockdep/prove-RCU flavor warnings, NMI-safe reader tests, callback/barrier tests, polling-cookie tests, and cleanup/init lifetime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/srcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/srcutiny.h -->
# sources/distributed-fs/ceph-client/include/linux/srcutiny.h

Purpose: Provides the tiny SRCU implementation for small/non-tree configurations, using compact counters and a workqueue-driven grace-period mechanism.

Important APIs/types/functions: `struct srcu_struct`, `srcu_drive_gp()`, `srcu_tiny_irq_work()`, `__SRCU_STRUCT_INIT()`, `DEFINE_SRCU*()`, `struct srcu_usage` dummy, `__srcu_read_lock()`, `__srcu_ptr_to_ctr()`, `__srcu_ctr_to_ptr()`, fast/updown read wrappers, `synchronize_srcu_expedited()`, `srcu_barrier()`, `srcu_expedite_current()`, and `srcu_torture_stats_print()`.

Control flow: `__srcu_read_lock()` disables preemption, selects the active counter from `srcu_idx`, increments nesting, reenables preemption, and returns the counter index. Fast APIs encode that index as a fake per-CPU pointer for compatibility with the public API. Expedited synchronize and barrier collapse to `synchronize_srcu()`.

State and persistence behavior: State is local to `struct srcu_struct`: two nesting counters, GP running/waiting flags, current and maximum requested index, waitqueue, callback list head/tail, work item, irq_work item, and optional lockdep map.

Dependencies: `irq_work_types.h`, `swait.h`, workqueue and RCU types from `srcu.h`.

Integration points: Selected by `srcu.h` under `CONFIG_TINY_SRCU`. Provides API compatibility with tree SRCU while minimizing storage and complexity.

Risks: Tiny SRCU lacks tree scalability and flavor checking is a no-op. Fast variants are compatibility wrappers rather than separate scalable fast paths.

Test signals: Tiny SRCU builds, rcutorture tiny flavor, nested read sections, callback wakeups, and stats printing for grace-period progress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/srcutiny.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/srcutree.h -->
# sources/distributed-fs/ceph-client/include/linux/srcutree.h

Purpose: Defines the scalable tree SRCU implementation data structures, initializers, state-machine constants, and fast reader inline paths.

Important APIs/types/functions: `struct srcu_ctr`, `struct srcu_data`, `struct srcu_node`, `struct srcu_usage`, `struct srcu_struct`, `SRCU_SIZE_*`, `SRCU_STATE_*`, `SRCU_EC_*`, `__SRCU_USAGE_INIT()`, `__DEFINE_SRCU()`, `DEFINE_SRCU*()`, `__srcu_read_lock()`, `synchronize_srcu_expedited()`, `srcu_barrier()`, `srcu_expedite_current()`, `__srcu_ptr_to_ctr()`, `__srcu_ctr_to_ptr()`, `__srcu_read_lock_fast()`, `__srcu_read_unlock_fast()`, fast-updown variants, and `srcu_check_read_flavor()`.

Control flow: Static definitions allocate per-CPU `srcu_data` and a `srcu_usage`. Fast read locks load `ssp->srcu_ctrp`, increment per-CPU lock counters with `this_cpu_inc()` or NMI-safe atomic increments, apply barriers to keep critical sections contained, and return the counter pointer. Unlock increments the corresponding unlock counter. The update-side implementation elsewhere uses `srcu_usage`/`srcu_node` state to aggregate callbacks and advance grace periods.

State and persistence behavior: Persistent SRCU domain state includes per-CPU lock/unlock counters, callback segmented lists, GP-needed sequence numbers, work/timer/irq_work items, combining tree nodes, barrier completion state, sizing transition state, and reader flavor. The `SRCU_SIZE_*` state machine gradually transitions from small to fully initialized tree operation.

Dependencies: `rcu_node_tree.h`, `completion.h`, atomics, per-CPU accessors, raw spinlocks, mutexes, timers, workqueues, and RCU sequence/callback infrastructure.

Integration points: Used by `srcu.h` under `CONFIG_TREE_SRCU`; supports scalable callback and grace-period management for high-CPU-count systems.

Risks: Reader flavor mismatches, incorrect per-CPU pointer/index conversion, premature use of partially initialized combining tree data, or missing RCU-watching constraints in fast readers can break grace-period ordering.

Test signals: TREE_SRCU rcutorture, PROVE_RCU flavor checks, high-CPU callback stress, small-to-big transition coverage, expedited and barrier tests, and NMI-safe fast-reader tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/srcutree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb.h -->
# sources/distributed-fs/ceph-client/include/linux/ssb/ssb.h

Purpose: Defines the Sonics Silicon Backplane core bus model, device/driver abstractions, SPROM board data, bus registration APIs, MMIO access wrappers, power management hooks, DMA translation, and host-bus integration.

Important APIs/types/functions: `struct ssb_sprom`, `struct ssb_boardinfo`, `struct ssb_bus_ops`, core/vendor/board constants, `struct ssb_device`, `dev_to_ssb_dev()`, drvdata helpers, `struct ssb_driver`, `ssb_driver_register/unregister()`, `enum ssb_bustype`, `struct ssb_bus`, `struct ssb_init_invariants`, bus registration functions for SoC/PCI/PCMCIA/SDIO, suspend/resume, `ssb_device_enable/disable/is_enabled()`, `ssb_read*/write*()`, block I/O helpers, `ssb_dma_translation()`, powerup/powerdown, `ssb_commit_settings()`, and address-match helpers.

Control flow: Host-specific registration fills an `ssb_bus`, enumerates cores into `ssb_device` entries, populates invariant board/SPROM data, and registers devices with the driver model. Per-device MMIO operations dispatch through `ssb_bus_ops`. Device drivers bind via `ssb_driver` probe/remove/suspend/resume hooks. Power helpers coordinate bus-level power state around device activity.

State and persistence behavior: Runtime bus state includes MMIO base, mapped core/window state, BAR lock, host-bus pointer, quirks, chip ID/revision/package, device array, board/SPROM data, optional GPIO/watchdog state, list linkage, and power flags. SPROM contents represent persistent board configuration read into memory.

Dependencies: Linux device model, lists, spinlocks, PCI, GPIO, DMA mapping, platform devices, SSB register constants, and companion SSB core headers.

Integration points: Broadcom SSB-based wireless, Ethernet, MIPS SoC, PCI bridge, PCMCIA, SDIO, GPIO, watchdog, and architecture pcibios fixups.

Risks: Incorrect core window switching under `bar_lock`, stale SPROM fallback data, wrong host-bus union use, and DMA translation mistakes can break device access. The fixed `SSB_MAX_NR_CORES` device array depends on register-map constants.

Test signals: Enumeration on each host bus, SPROM parse/fallback tests, read/write/block I/O traces, suspend/resume and powerdown tests, DMA mapping tests, and SSB driver probe/remove coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_chipcommon.h -->
# sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_chipcommon.h

Purpose: Defines ChipCommon core registers, capability bits, PLL/clock/PMU constants, GPIO/watchdog interfaces, and the `ssb_chipcommon` accessor surface for SSB chips.

Important APIs/types/functions: Hundreds of `SSB_CHIPCO_*` register and bitfield constants, `struct ssb_chipcommon`, `ssb_chipcommon_available()`, `chipco_read32/write32()`, mask/set helpers, `ssb_chipcommon_init()`, suspend/resume, clock query/timing functions, `enum ssb_clkmode`, `ssb_chipco_set_clockmode()`, watchdog setter, IRQ mask/status helpers, GPIO helpers, serial init, PMU init, LDO voltage and PA reference controls, and spur-avoid PLL update.

Control flow: Driver code probes ChipCommon availability through `cc->dev`, uses register accessor macros over SSB MMIO, initializes clocks/timing/PMU, and manipulates GPIO/IRQ/watchdog registers through typed helper functions.

State and persistence behavior: Hardware register state covers chip ID/capabilities, interrupt masks, flash/OTP/JTAG, GPIO, clock control, watchdog, and PMU resources. In-memory `ssb_chipcommon` points to the backing SSB device.

Dependencies: SSB MMIO wrappers, serial-port definitions from MIPS header when serial is enabled, PMU and GPIO subsystems, and chip revision-specific register semantics.

Integration points: Central integration for Broadcom SoC clocking, GPIO, serial, flash, PMU, watchdog, and board bring-up.

Risks: Register definitions are revision-sensitive; using GPIO/PMU/watchdog helpers without checking availability or capability bits can touch invalid hardware. Mask/set helpers perform read-modify-write and need proper locking at call sites.

Test signals: ChipCommon probe on multiple revisions, clock-mode transitions, GPIO read/write/IRQ tests, watchdog timer tests, PMU voltage/spur-avoid tests, and suspend/resume register preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_chipcommon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_extif.h -->
# sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_extif.h

Purpose: Describes the SSB External Interface core used on BCM47xx-family chips for external chip selects, PCMCIA/flash/asynchronous devices, UARTs, watchdog, clocking, and GPIO.

Important APIs/types/functions: `SSB_EXTIF_*` address/register/bit constants, GPIO register offset macros with `BUILD_BUG_ON`, wait-count fields, watchdog clock limits, `struct ssb_extif`, `ssb_extif_available()`, clock/timing/watchdog helpers, GPIO helpers, and optional serial init.

Control flow: When `CONFIG_SSB_DRIVER_EXTIF` is enabled, callers operate on a real `struct ssb_extif` containing an SSB device and GPIO lock. When disabled, the same API compiles to safe stubs returning false, zero, or success as appropriate.

State and persistence behavior: Hardware state is in EXTIF registers for chip-select configuration, wait counts, watchdog timer, clock dividers, UART, and GPIO. In-memory state is the core device pointer and GPIO lock.

Dependencies: SSB device accessors, spinlocks, serial port definitions if serial is enabled, and compile-time SSB driver configuration.

Integration points: Board flash, PCMCIA, external UART/Bluetooth, GPIO, and watchdog support on SSB embedded platforms.

Risks: Wait-count and chip-select programming is timing-sensitive; incorrect GPIO index usage is prevented at compile time only for constant indexes. Disabled stubs can hide missing hardware support if callers do not check availability.

Test signals: EXTIF-enabled and disabled builds, GPIO register access tests, watchdog maximum tests, flash/PCMCIA timing validation, and serial initialization tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_extif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_gige.h -->
# sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_gige.h

Purpose: Defines the SSB Gigabit Ethernet pseudo-PCI bridge/core interface and helper queries used by Ethernet drivers on Broadcom SSB SoCs.

Important APIs/types/functions: GigE register offsets and flags, `struct ssb_gige`, `pdev_is_ssb_gige_core()`, `pdev_to_ssb_gige()`, `ssb_gige_is_rgmii()`, `ssb_gige_have_roboswitch()`, DMA/posted-write quirk helpers, MAC/PHY address helpers, `ssb_gige_pcibios_plat_dev_init()`, `ssb_gige_map_irq()`, `ssb_gige_init()`, and `ssb_gige_exit()`.

Control flow: With `CONFIG_SSB_DRIVER_GIGE`, a PCI device can be identified as the SSB GigE core, converted to `struct ssb_gige` through the PCI ops container, and queried for board/SoC quirks and SPROM-provided MAC/PHY data. Without the config, helpers return disabled/error values.

State and persistence behavior: Runtime state includes SSB device pointer, spinlock, RGMII/GMII mode, PCI controller/ops, and I/O/memory resources. Board state comes from `bus->sprom`.

Dependencies: `ssb.h`, PCI core, spinlocks, resource management, and board flags from SPROM.

Integration points: MIPS/BCM47xx PCI platform initialization and Ethernet MAC drivers that query PHY mode, MAC address, DMA limitations, posted-write flushing, and IRQ mapping.

Risks: `ssb_gige_exit()` deliberately calls `BUG()` when enabled because the bridge cannot be unregistered, so it must not be used as a normal unload path. Wrong `pdev_to_ssb_gige()` assumptions can return `NULL`.

Test signals: Enabled/disabled build coverage, PCI platform-device initialization, IRQ mapping, MAC/PHY SPROM data tests, and hardware-specific DMA/posted-write quirk validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_gige.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_mips.h -->
# sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_mips.h

Purpose: Defines MIPS core support data for SSB embedded systems, including serial ports, parallel/serial flash descriptors, CPU clock, and IRQ mapping.

Important APIs/types/functions: `struct ssb_serial_port`, `struct ssb_pflash`, optional `struct ssb_sflash`, `struct ssb_mipscore`, `ssb_mipscore_init()`, `ssb_cpu_clock()`, and `ssb_mips_irq()`.

Control flow: Enabled builds initialize a MIPS core object with discovered serial/flash resources and expose clock/IRQ helpers. Disabled builds define an empty `ssb_mipscore` and no-op/zero-return stubs.

State and persistence behavior: Runtime state includes SSB device pointer, serial-port descriptors, parallel flash metadata, and optional serial flash metadata. Flash descriptors describe persistent storage windows but do not manipulate contents here.

Dependencies: SSB device declarations and configuration for MIPS and serial flash support.

Integration points: BCM47xx-style MIPS boot/platform code, serial console setup, flash mapping, and IRQ routing for SSB devices.

Risks: Disabled stubs return IRQ 0, which callers must treat carefully. Flash window/buswidth values are hardware-derived and must match actual board wiring.

Test signals: MIPS SSB platform boot tests, serial-port enumeration, CPU clock calculations, flash map detection, and IRQ mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_mips.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_pci.h -->
# sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_pci.h

Purpose: Defines SSB PCI core registers, translation settings, state flags, and helpers for PCI host/core initialization and IRQ routing.

Important APIs/types/functions: `SSB_PCICORE_*` register/bit constants, SB-to-PCI translation constants, `SSB_PCICORE_BFL_NOPCI`, `struct ssb_pcicore`, `ssb_pcicore_init()`, `ssb_pcicore_dev_irqvecs_enable()`, `ssb_pcicore_plat_dev_init()`, and `ssb_pcicore_pcibios_map_irq()`.

Control flow: Enabled builds expose real initialization and IRQ-vector helpers. Disabled builds provide an empty type and stubs returning success for init/IRQ-vector enable or `-ENODEV` for platform PCI init/map IRQ.

State and persistence behavior: Runtime state includes SSB PCI device pointer and bit flags recording setup, host mode, and cardbus mode. Hardware state includes PCI control, arbiter, interrupt, GPIO, translation, config, and SPROM shadow registers.

Dependencies: PCI types, SSB device definitions, board flags, and architecture pcibios integration.

Integration points: SSB-as-PCI-host support, PCI client configuration, IRQ routing, SPROM shadow access, and embedded platform PCI setup.

Risks: Translation window programming and IRQ routing are chip-revision sensitive. Disabled stubs may compile users but leave platform PCI unsupported at runtime.

Test signals: PCI host and client mode enumeration, IRQ vector enable tests, config-space access, SPROM shadow access, and disabled-config compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_driver_pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_embedded.h -->
# sources/distributed-fs/ceph-client/include/linux/ssb/ssb_embedded.h

Purpose: Declares embedded-platform convenience APIs for SSB watchdog and GPIO operations at the bus level.

Important APIs/types/functions: `ssb_watchdog_timer_set()`, `ssb_gpio_in()`, `ssb_gpio_out()`, `ssb_gpio_outen()`, `ssb_gpio_control()`, `ssb_gpio_intmask()`, and `ssb_gpio_polarity()`.

Control flow: Implementations elsewhere choose the appropriate underlying ChipCommon or EXTIF GPIO/watchdog backend for a given `ssb_bus`.

State and persistence behavior: Functions manipulate hardware watchdog and GPIO register state; no state is stored in this header.

Dependencies: `ssb.h` and `linux/types.h`.

Integration points: Embedded Broadcom board code, watchdog drivers, GPIO drivers, and platform initialization.

Risks: Bus-level helpers must serialize GPIO access using the locks held in `struct ssb_bus` or core-specific structs. Wrong backend selection can touch absent hardware.

Test signals: Embedded SSB builds, GPIO controller tests, watchdog timer tests, and boards with ChipCommon versus EXTIF GPIO backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_embedded.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_regs.h -->
# sources/distributed-fs/ceph-client/include/linux/ssb/ssb_regs.h

Purpose: Provides the SSB physical address map, PCI config register offsets, core enumeration constants, target/initiator state registers, identification fields, SPROM layout constants, board flags, country codes, and address-match masks.

Important APIs/types/functions: `SSB_*` address constants such as `SSB_ENUM_BASE`, `SSB_CORE_SIZE`, `SSB_MAX_NR_CORES`, PCI config offsets, backplane register offsets (`SSB_TMSLOW`, `SSB_TMSHIGH`, `SSB_IDLOW`, `SSB_IDHIGH`, etc.), SPROM size/base/revision constants, SPROM field masks, board flag masks, country-code enum, and `SSB_ADM_*` address-match masks.

Control flow: No executable control flow. The constants drive enumeration, register decode, SPROM parsing, reset/enable sequences, interrupt routing, and address-window calculations in SSB implementations.

State and persistence behavior: Describes hardware register and SPROM persistent data layout. The header itself stores no state.

Dependencies: Expected to be included by SSB core headers and C files; assumes kernel integer types are available through includers.

Integration points: SSB bus enumeration, PCI and SoC register programming, SPROM parsing, board quirk selection, and memory/flash window mapping.

Risks: Incorrect constants corrupt hardware access. SPROM fields are revision-specific and must be parsed with the right base/size/mask. `SSB_MAX_NR_CORES` depends directly on enumeration range constants.

Test signals: Register decode tests against known chip dumps, SPROM parsing fixtures for revisions 1/4/10/11, board flag quirk tests, and enumeration count validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssb/ssb_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssbi.h -->
# sources/distributed-fs/ceph-client/include/linux/ssbi.h

Purpose: Declares SSBI read/write accessors and adapts them to regmap-style single-register callbacks.

Important APIs/types/functions: `ssbi_write()`, `ssbi_read()`, `ssbi_reg_read()`, and `ssbi_reg_write()`.

Control flow: `ssbi_reg_read()` reads one byte through `ssbi_read()` and stores it into an `unsigned int` on success. `ssbi_reg_write()` truncates the value to one byte and writes it through `ssbi_write()`.

State and persistence behavior: No state in the header. Operations affect device registers behind the provided device/context pointer.

Dependencies: `linux/types.h`; uses `struct device` through declarations.

Integration points: Qualcomm/Android-era SSBI bus devices and regmap adapters.

Risks: Register helper callbacks are byte-wide; callers must not expect multi-byte regmap semantics. `void *context` is treated as the device pointer expected by `ssbi_read/write`.

Test signals: Bus read/write transaction tests, regmap single-byte callback tests, error propagation tests, and value truncation coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ssbi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stackdepot.h -->
# sources/distributed-fs/ceph-client/include/linux/stackdepot.h

Purpose: Declares Stack Depot, a deduplicating storage service for stack traces used by sanitizers and debugging subsystems to avoid storing repeated stack arrays per object.

Important APIs/types/functions: `depot_stack_handle_t`, handle layout constants, `union handle_parts`, `struct stack_record`, `depot_flags_t`, `STACK_DEPOT_FLAG_CAN_ALLOC`, `STACK_DEPOT_FLAG_GET`, initialization APIs, `stack_depot_save_flags()`, `stack_depot_save()`, `__stack_depot_get_stack_record()`, `stack_depot_fetch()`, `stack_depot_print()`, `stack_depot_snprint()`, `stack_depot_put()`, `stack_depot_set_extra_bits()`, and `stack_depot_get_extra_bits()`.

Control flow: Users initialize Stack Depot early or at runtime, save stack entries to receive compact handles, later fetch or print entries by handle, optionally hold/release references with `STACK_DEPOT_FLAG_GET`, and may use spare handle bits for caller metadata.

State and persistence behavior: When enabled, stack records live in depot pools and hash lists, with handle fields encoding pool index, offset, and extra bits. Reference-counted records can be freed through an RCU-safe freelist path. No on-disk persistence exists.

Dependencies: GFP allocation, page sizing, list heads, refcounts, RCU cookies, and `CONFIG_STACKDEPOT`/frame-count configuration.

Integration points: KASAN, SLUB debugging, leak detection, and any subsystem storing many repeated stack traces.

Risks: Saving without allocation permission in contexts that need new pools can fail. Users of `STACK_DEPOT_FLAG_GET` must call `stack_depot_put()` or refcounts can overflow/leak. Extra bits must fit `STACK_DEPOT_EXTRA_BITS`.

Test signals: Stack depot initialization modes, save/fetch deduplication tests, no-allocation context tests, refcount put/evict tests, snprint output tests, and extra-bit encode/decode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stackdepot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stackprotector.h -->
# sources/distributed-fs/ceph-client/include/linux/stackprotector.h

Purpose: Defines stack canary generation policy and boot-time stack protector initialization hook.

Important APIs/types/functions: `CANARY_MASK`, `get_random_canary()`, and `boot_init_stack_canary()`.

Control flow: `get_random_canary()` masks `get_random_long()` so 64-bit canaries include a zero byte to limit unterminated string overflow attacks. If stack protector or ARM64 pointer authentication is enabled, architecture code supplies `boot_init_stack_canary()`; otherwise it is a no-op.

State and persistence behavior: Generated canaries seed per-task or per-CPU stack protector state in architecture code; this header only defines the random generation helper and mask.

Dependencies: Compiler definitions, scheduler, random number generation, endian/word-size config, and optional `asm/stackprotector.h`.

Integration points: Early boot, task stack protection, compiler-emitted stack-protector checks, and ARM64 pointer-auth support.

Risks: Incorrect endian mask would remove the wrong byte. Early boot must have enough randomness or architecture fallback behavior.

Test signals: Architecture boot tests with stack protector enabled/disabled, canary mask checks on endian/word-size variants, and compiler stack-protector fault tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stackprotector.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stacktrace.h -->
# sources/distributed-fs/ceph-client/include/linux/stacktrace.h

Purpose: Declares generic and architecture stack-walking interfaces for saving, printing, and reliably collecting kernel/user stack traces.

Important APIs/types/functions: `stack_trace_consume_fn`, `arch_stack_walk()`, `arch_stack_walk_reliable()`, `arch_stack_walk_user()`, `stack_trace_print()`, `stack_trace_snprint()`, `stack_trace_save*()`, `filter_irq_stacks()`, legacy `struct stack_trace`, `save_stack_trace*()`, and `stack_trace_save_tsk_reliable()`.

Control flow: Architecture stack walkers call a consumer callback for each address. Generic save functions fill caller-provided arrays with optional skip counts. Reliable variants return errors for unsupported/unreliable stacks and require inactive pinned tasks when walking non-current tasks.

State and persistence behavior: Stack traces are transient arrays of instruction pointers. The legacy `struct stack_trace` stores buffer, count, capacity, and skip state during collection.

Dependencies: Architecture unwind support, task and register structures, errno values, and `CONFIG_STACKTRACE`/`CONFIG_ARCH_STACKWALK`.

Integration points: Debugging, livepatch reliability checks, stack depot, tracing, warnings, and user stack capture.

Risks: Reliable walking has strict task-state requirements. Buffer size limits truncate traces. User stack walking depends on register validity and architecture support.

Test signals: Architecture unwind tests, reliable-stacktrace selftests, stack trace print/snprint tests, IRQ stack filtering tests, and disabled-config stub tests returning `-ENOSYS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stacktrace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/start_kernel.h -->
# sources/distributed-fs/ceph-client/include/linux/start_kernel.h

Purpose: Provides the canonical prototype for the kernel entry function `start_kernel()`.

Important APIs/types/functions: `extern asmlinkage void __init __noreturn start_kernel(void);`.

Control flow: No implementation here. Architecture boot code eventually calls `start_kernel()`, which never returns.

State and persistence behavior: No state in the header; annotations place implementation in init context and mark non-returning behavior.

Dependencies: `linkage.h` and `init.h` for calling convention and section/lifetime annotations.

Integration points: Architecture boot assembly/C handoff and early kernel initialization.

Risks: Signature or annotation mismatch would break boot entry linkage or compiler assumptions.

Test signals: Architecture boot builds, linker symbol checks, and early boot smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/start_kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stat.h -->
# sources/distributed-fs/ceph-client/include/linux/stat.h

Purpose: Defines internal kernel file metadata structures and constants used by VFS stat/statx paths.

Important APIs/types/functions: Permission aggregate macros, `UTIME_NOW`, `UTIME_OMIT`, `struct kstat`, `KSTAT_ATTR_FS_IOC_FLAGS`, `KSTAT_ATTR_VFS_FLAGS`, `STATX_CHANGE_COOKIE`, and `STATX_ATTR_CHANGE_MONOTONIC`.

Control flow: No executable flow. Filesystems fill `struct kstat`; VFS/statx code converts it to user-visible stat data according to `result_mask` and requested flags.

State and persistence behavior: `struct kstat` is a transient metadata snapshot containing mode, link count, block size, attributes, inode/device IDs, ownership, size, timestamps, blocks, mount ID, change cookie, subvolume, DIO alignment, and atomic-write limits.

Dependencies: Architecture stat definitions, UAPI stat constants, kernel types, time, and uid/gid wrappers.

Integration points: VFS `getattr`, stat/statx syscalls, NFSd change-cookie handling, and filesystem-specific attribute reporting. Ceph-style distributed filesystems use this structure to return remote inode metadata through VFS.

Risks: Incorrect `result_mask`, timestamp, attribute, or alignment fields can mislead userspace. Internal statx extension bits must not collide with public ABI unexpectedly.

Test signals: stat/statx syscall tests, filesystem getattr tests, DIO alignment reporting tests, change-cookie tests, and permission macro compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/statfs.h -->
# sources/distributed-fs/ceph-client/include/linux/statfs.h

Purpose: Defines internal kernel filesystem-statistics structures, mount flag constants, and fsid helpers.

Important APIs/types/functions: `struct kstatfs`, `ST_*` flag constants, `vfs_get_fsid()`, `u64_to_fsid()`, and `uuid_to_fsid()`.

Control flow: Filesystems populate `kstatfs`; VFS translates it to statfs/statvfs userspace structures. `uuid_to_fsid()` folds a 16-byte UUID into a 64-bit fsid by XORing its two little-endian halves.

State and persistence behavior: `kstatfs` is a transient snapshot of filesystem type, block sizes, block/file counts, fsid, name length, fragment size, flags, and spare fields.

Dependencies: Kernel types, architecture statfs ABI, and byteorder helpers.

Integration points: VFS `statfs`, mount flag reporting, filesystem fsid generation. Distributed filesystems need stable fsid behavior for clients and exports.

Risks: Unstable or colliding fsids can confuse userspace or network export clients. `f_flags` must accurately represent mount semantics.

Test signals: statfs/statvfs syscall tests, UUID-to-fsid fixtures, mount flag propagation tests, and filesystem-specific statfs coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/statfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/static_call.h -->
# sources/distributed-fs/ceph-client/include/linux/static_call.h

Purpose: Defines the static call API, which gives function-pointer flexibility with direct-call or patched-call performance when architecture support exists.

Important APIs/types/functions: `DECLARE_STATIC_CALL()`, `DEFINE_STATIC_CALL()`, `DEFINE_STATIC_CALL_NULL()`, `DEFINE_STATIC_CALL_RET0()`, `static_call()`, `static_call_cond()`, `static_call_update()`, `static_call_query()`, `arch_static_call_transform()`, `static_call_init()`, `static_call_force_reinit()`, `struct static_call_mod`, `struct static_call_tramp_key`, `__static_call_update()`, `static_call_text_reserved()`, `__static_call_return0()`, and export macros.

Control flow: Static call definitions create a key and, when supported, an architecture trampoline. `static_call(name)(...)` calls through a trampoline or function pointer. `static_call_update()` stores the new target and may patch trampoline/callsite text under CPU read locking. Inline-capable architectures use site metadata generated by objtool/compiler plugins for direct callsite patching. Generic fallback updates only the function pointer.

State and persistence behavior: Static call state lives in `struct static_call_key` target pointers, optional module/site lists, trampolines, and patched kernel text. Updates affect runtime dispatch globally.

Dependencies: CPU hotplug read locks, architecture static-call support, `static_call_types.h`, module/export infrastructure, objtool or compiler plugin metadata for inline callsites, and text patching safety.

Integration points: Performance-sensitive kernel indirection points where retpolines or indirect calls are expensive; module use can be limited to trampoline-only exports.

Risks: Calling NULL static calls without `static_call_cond()` is invalid. Argument evaluation is unconditional even for conditional/null/ret0 optimized calls. Text patching must avoid reserved ranges and module lifetime races.

Test signals: Static call selftests, update/query tests, NULL and RET0 behavior tests, module load/unload tests, objtool site validation, and architecture text-patching tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/static_call.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/static_call_types.h -->
# sources/distributed-fs/ceph-client/include/linux/static_call_types.h

Purpose: Defines shared static-call symbol naming, site metadata, declarations, call expression macros, and `struct static_call_key` layouts used by `static_call.h` and architecture code.

Important APIs/types/functions: `STATIC_CALL_KEY_PREFIX`, `STATIC_CALL_KEY()`, `STATIC_CALL_TRAMP_PREFIX`, `STATIC_CALL_TRAMP()`, `STATIC_CALL_SITE_*` flags, `struct static_call_site`, `DECLARE_STATIC_CALL()`, `__raw_static_call()`, `__static_call()`, `struct static_call_key`, `static_call_mod()`, and `static_call()`.

Control flow: Macro expansion constructs symbol names for keys and trampolines. With static-call support, `static_call()` resolves to the trampoline and may mark the key addressable for tooling. Without support, it casts the stored function pointer in the key.

State and persistence behavior: The key holds the active function pointer and, for inline-capable builds, either module metadata or static callsite pointers. Site metadata uses relative addresses and key references with low-bit flags.

Dependencies: Kernel types, stringify/paste helpers, compiler addressability support, module configuration, and architecture/tooling support.

Integration points: Included by `static_call.h`, architecture assembly/C code, objtool-generated `.static_call_sites`, and modules using static calls.

Risks: Symbol naming and addressability are part of tooling contracts; changing them breaks objtool/module linkage. Low-bit flag encoding requires aligned key pointers.

Test signals: Build/link tests for declared/defined static calls, objtool static-call site generation, module static-call use, and generic fallback builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/static_call_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/static_key.h -->
# sources/distributed-fs/ceph-client/include/linux/static_key.h

Purpose: Compatibility include for static keys that forwards to the jump-label implementation.

Important APIs/types/functions: No local APIs; all static key/static branch definitions come from `linux/jump_label.h`.

Control flow: Single include.

State and persistence behavior: No local state; jump-label static keys manage state elsewhere.

Dependencies: `linux/jump_label.h`.

Integration points: Source compatibility for code including `static_key.h`.

Risks: All behavior and build requirements are inherited from jump labels.

Test signals: Compile-only tests for code including `static_key.h` and using static branch APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/static_key.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stdarg.h -->
# sources/distributed-fs/ceph-client/include/linux/stdarg.h

Purpose: Provides kernel-local varargs definitions backed by compiler builtins.

Important APIs/types/functions: `va_list`, `va_start`, `va_end`, `va_arg`, and `va_copy`.

Control flow: Macro wrappers expand directly to compiler builtins.

State and persistence behavior: `va_list` state is local to a variadic function call frame.

Dependencies: Compiler support for builtin varargs.

Integration points: Formatting, logging, scanning, and any variadic kernel APIs such as `sprintf.h`.

Risks: ABI correctness depends on compiler builtin behavior; callers must still pair `va_start`/`va_end` and use matching argument types.

Test signals: Variadic formatting build/tests and compiler portability checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stdarg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stddef.h -->
# sources/distributed-fs/ceph-client/include/linux/stddef.h

Purpose: Defines kernel equivalents of common Cstddef constructs and layout helper macros for safer structure introspection and flexible-array patterns.

Important APIs/types/functions: `NULL`, anonymous enum `false/true`, `offsetof()`, `sizeof_field()`, `offsetofend()`, `struct_group()`, `struct_group_attr()`, `struct_group_tagged()`, `DECLARE_FLEX_ARRAY()`, `__TRAILING_OVERLAP()`, and `TRAILING_OVERLAP()`.

Control flow: Pure macro definitions. Struct group macros create mirrored anonymous/named substructures with identical layouts; trailing overlap creates a union allowing a flexible array member to overlap explicitly declared trailing fields.

State and persistence behavior: No runtime state, but macros define compile-time structure layout and affect ABI/layout of containing structs.

Dependencies: UAPI `linux/stddef.h` for lower-level helper macros such as `__struct_group` and `__DECLARE_FLEX_ARRAY`, and compiler `__builtin_offsetof`.

Integration points: Kernel structures needing layout-safe grouped fields, flexible arrays in unions, and compile-time size/offset checks.

Risks: Layout macros affect ABI and must be used carefully in UAPI or packed structures. `TRAILING_OVERLAP` must match the intended flexible-array offset exactly.

Test signals: Compile-time layout assertions, `offsetof`/`sizeof_field` tests, flexible-array warning tests, and structure group ABI checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stddef.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stm.h -->
# sources/distributed-fs/ceph-client/include/linux/stm.h

Purpose: Declares System Trace Module infrastructure for registering STM devices and trace sources and writing STP packets.

Important APIs/types/functions: `enum stp_packet_type`, `enum stp_packet_flags`, `enum stm_source_type`, `struct stm_data`, `stm_register_device()`, `stm_unregister_device()`, `struct stm_source_data`, `stm_source_register_device()`, `stm_source_unregister_device()`, and `stm_source_write()`.

Control flow: An STM hardware driver fills `struct stm_data` with master/channel ranges and callbacks, then registers it. Source drivers fill `struct stm_source_data` and register sources. When linked, writes flow through `stm_source_write()` to the selected STM device `packet()` callback with master/channel/packet metadata.

State and persistence behavior: Runtime state is owned by STM class internals through opaque `stm` and `src` pointers plus source/device linkage. Hardware state includes channel configuration and packet output.

Dependencies: Linux device model, module ownership, trace/ftrace source users, and hardware-specific STM packet callbacks.

Integration points: Intel STM and other system trace modules, ftrace-to-STM routing, userspace trace sources, and policy-managed channel allocation.

Risks: `packet()` callbacks must report consumed payload accurately and return `-ENOTSUPP` for unsupported type/flag combinations. Bad link/unlink handling can leave channels active or leak source associations.

Test signals: STM device/source registration tests, packet callback contract tests, ftrace source writes, policy/channel allocation tests, and unregister cleanup tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stmmac.h -->
# sources/distributed-fs/ceph-client/include/linux/stmmac.h

Purpose: Defines platform data for the Synopsys/STMicroelectronics stmmac Ethernet driver, including DMA, AXI, queue, safety, core type, clocks, PHY/PCS, callbacks, flags, and SoC glue hooks.

Important APIs/types/functions: queue limits, RX checksum constants, CSR clock divisors, MTL algorithm and queue mode constants, DMA burst constants, `struct stmmac_mdio_bus_data`, `struct stmmac_dma_cfg`, `struct stmmac_axi`, `struct stmmac_rxq_cfg`, `struct stmmac_txq_cfg`, `struct stmmac_safety_feature_cfg`, `struct dwmac4_addrs`, `enum dwmac_core_type`, `STMMAC_FLAG_*`, and `struct plat_stmmacenet_data`.

Control flow: Platform or device-tree glue populates `plat_stmmacenet_data` before the stmmac core probes. The driver consumes PHY interface, queue counts/config, DMA/AXI parameters, clock/reset handles, callbacks for SoC-specific setup, MAC/PCS/SerDes hooks, timestamp configuration, and interrupt vector assignments.

State and persistence behavior: This is configuration state passed into the network driver. It persists for the lifetime of the platform device and points to clocks, resets, node references, queue arrays, callback private data, and embedded fallback DMA config.

Dependencies: Platform device support, phylink, clocks, reset controls, net device types, PTP/system counter types, and stmmac core internals.

Integration points: Platform Ethernet glue, phylink/PCS/PHY, MDIO, DMA/AXI, PTP timestamping, MSI routing, safety features, clock/reset management, and SoC-specific MAC setup.

Risks: Incorrect queue counts beyond `MTL_MAX_*`, mismatched PHY interface/clock callbacks, wrong DMA burst settings, or invalid clock/reset pointers can prevent link bring-up or corrupt DMA. Callback lifetimes must match `bsp_priv` and device lifetime.

Test signals: stmmac probe on representative platforms, phylink mode matrix, MDIO clock divider tests, multi-queue traffic tests, DMA burst/performance tests, suspend/resume, PTP timestamp tests, and safety interrupt injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stmmac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stmp3xxx_rtc_wdt.h -->
# sources/distributed-fs/ceph-client/include/linux/stmp3xxx_rtc_wdt.h

Purpose: Defines platform data for the STMP3xxx RTC watchdog integration.

Important APIs/types/functions: `struct stmp3xxx_wdt_pdata` with `wdt_set_timeout(struct device *dev, u32 timeout)`.

Control flow: Platform code supplies a timeout-setting callback that the watchdog/RTC driver can invoke with the target device and timeout value.

State and persistence behavior: No state in the header. Runtime state is the callback pointer and any platform-specific device registers it manipulates.

Dependencies: Uses `struct device` and `u32` via includer context.

Integration points: STMP3xxx RTC and watchdog drivers.

Risks: Callback lifetime and device pointer validity are critical. Timeout units must be consistently interpreted by provider and caller.

Test signals: Platform-data probe tests, watchdog timeout set tests, and null/missing callback handling in the consuming driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stmp3xxx_rtc_wdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stmp_device.h -->
# sources/distributed-fs/ceph-client/include/linux/stmp_device.h

Purpose: Declares common helpers and register offset conventions for devices using the STMP set/clear/toggle register layout.

Important APIs/types/functions: `STMP_OFFSET_REG_SET`, `STMP_OFFSET_REG_CLR`, `STMP_OFFSET_REG_TOG`, and `stmp_reset_block(void __iomem *)`.

Control flow: Drivers use base register addresses plus SET/CLR/TOG offsets for atomic-style bit manipulation and can call `stmp_reset_block()` to reset a hardware block.

State and persistence behavior: Header has no state; operations affect MMIO register state of STMP-style devices.

Dependencies: MMIO pointer annotation `__iomem` via includer context.

Integration points: STMP/i.MX-style platform drivers with common register layout.

Risks: Passing the wrong base address to reset or offset calculations can modify unrelated registers. Reset timing and completion are implementation-specific.

Test signals: Register offset unit checks in drivers, hardware reset tests, and build coverage for drivers including this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/stmp_device.h -->
