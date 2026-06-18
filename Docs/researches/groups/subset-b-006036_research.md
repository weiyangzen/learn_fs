# subset-b-006036 Research

Grouped research for Linux kernel livepatch, liveupdate/kexec handover, and locking event support under `sources/distributed-fs/ceph-client/kernel`. Each section preserves the source path in its title and is delimited for deterministic splitting into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/core.c -->
# sources/distributed-fs/ceph-client/kernel/livepatch/core.c

## Purpose
`core.c` is the central Kernel Live Patching coordinator. It owns the global livepatch mutex, active patch list, `/sys/kernel/livepatch` kobject tree, patch enable/disable paths, symbol and relocation resolution, dynamic NOP generation for atomic replace, object lifecycle handling, and module load/unload integration. It wires patch metadata from `struct klp_patch` into ftrace redirection via `patch.c` and task consistency transitions via `transition.c`.

## Important APIs, Types, and Functions
Global state is `klp_mutex`, `klp_patches`, and the root kobject `klp_root_kobj`. `klp_enable_patch()` is the exported entry point used by livepatch module init code. Module hooks are `klp_module_coming()` and `klp_module_going()`. Relocation APIs include `klp_apply_section_relocs()`, `clear_relocate_add()`, `klp_find_section_by_name()`, `klp_write_object_relocs()`, and `klp_apply_object_relocs()`.

Symbol resolution centers on `klp_find_object_symbol()`, `klp_resolve_symbols()`, and `klp_write_section_relocs()`, which parse `.klp.sym.<object>.<symbol>,<sympos>` and `.klp.rela.<object>.*` sections and support unexported symbol references. Lifecycle helpers include `klp_init_patch_early()`, `klp_init_patch()`, `klp_init_object()`, `klp_init_object_loaded()`, `klp_free_patch_start()`, `klp_free_patch_finish()`, `klp_free_patch_async()`, `klp_free_replaced_patches_async()`, `klp_unpatch_replaced_patches()`, and `klp_discard_nops()`.

The sysfs interface exposes per-patch `enabled`, `transition`, `force`, `replace`, and `stack_order`; per-object `patched`; and per-function kobjects named `<old_name>,<sympos>`. Attribute handlers include `enabled_store()`, `enabled_show()`, `transition_show()`, `force_store()`, `replace_show()`, `stack_order_show()`, and `patched_show()`.

## Control Flow
Patch enable starts in `klp_enable_patch()`: validate the patch/module/object/function metadata, require the module to be marked as a livepatch module, verify livepatch subsystem initialization, check state compatibility, take a module reference, initialize early list/kobject state, create sysfs nodes, resolve currently loaded objects, and call `__klp_enable_patch()`. `__klp_enable_patch()` initializes a transition to `KLP_TRANSITION_PATCHED`, runs pre-patch callbacks for loaded objects, registers function redirections via `klp_patch_object()`, starts the transition, marks the patch enabled, and attempts immediate completion.

Disable flows through the `enabled` sysfs attribute to `__klp_disable_patch()`. It rejects concurrent transitions, initializes an unpatch transition, runs pre-unpatch callbacks, starts task migration to the unpatched state, clears `patch->enabled`, and asks transition code to complete. If the sysfs write targets the currently transitioning patch, `enabled_store()` reverses the transition instead.

Module arrival is handled by `klp_module_coming()`: mark the module `klp_alive`, find matching patch objects, apply module-specific livepatch relocations, resolve function addresses and sizes, run pre-patch callbacks, and patch the object before module init completes. Module departure via `klp_module_going()` clears `klp_alive` and calls `klp_cleanup_module_patches_limited()` to unpatch objects, run callbacks, clear relocations, and null loaded-object pointers.

## State and Persistence Behavior
Livepatch state is in memory and exposed through sysfs. `klp_patches` contains enabled or transitioning patches; replaced and disabled patch modules may still be loaded but are not active in the list after cleanup. Patch/object/function structures track `enabled`, `forced`, `replace`, `patched`, `transition`, `dynamic`, `nop`, `old_func`, `new_func`, and symbol sizes. Module object state is intentionally not refcounted through `obj->mod`; removal is coordinated by `klp_module_going()` and the module `klp_alive` flag.

Atomic replace persistence is handled by dynamically adding NOP functions and objects to the new patch for old functions no longer present. After a successful replace transition, replaced patches and dynamic NOPs are unpatched and asynchronously freed. Forced transitions mark patch modules as `forced` so module references are not dropped too early.

## Dependencies and Integration Points
This file depends on module/kallsyms/ELF/moduleloader APIs, ftrace patching through `patch.c`, state compatibility in `state.c`, transition consistency in `transition.c`, sysfs/kobject infrastructure, RCU, and architecture relocation helpers. It integrates with module loader livepatch relocation sections, the module coming/going notifier path, reboot/module lifetime through module references, and `/sys/kernel/livepatch` administration.

## Risks and Test Signals
Relocation parsing is strict and ABI-sensitive; incorrect symbol names, duplicate symbols without `old_sympos`, or module-specific access to vmlinux livepatch symbols produce load failures. Memory barriers between transition flag writes, ftrace stack publication, and task state updates are correctness-critical. Module unload races rely on `klp_alive` and no extra module reference for target modules. Tests should cover livepatch module load/unload, ambiguous symbol failures, vmlinux and module-specific `.klp.rela.*` sections, atomic replace with removed functions, sysfs disable/reverse/force paths, late module patching, callback rollback, and reliable cleanup after failed enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/core.h -->
# sources/distributed-fs/ceph-client/kernel/livepatch/core.h

## Purpose
`core.h` is the internal livepatch core contract shared by the livepatch implementation files. It exposes the global serialization lock, active patch list iteration helpers, patch/free/replace helper prototypes, object-loaded predicate, and callback wrappers.

## Important APIs, Types, and Functions
It declares `extern struct mutex klp_mutex` and `extern struct list_head klp_patches`. Iteration macros `klp_for_each_patch()` and `klp_for_each_patch_safe()` abstract traversal of the global patch list. Prototypes include `klp_free_patch_async()`, `klp_free_replaced_patches_async()`, `klp_unpatch_replaced_patches()`, and `klp_discard_nops()`.

The inline `klp_is_object_loaded()` treats vmlinux objects as always loaded and module objects as loaded when `obj->mod` is set. Callback wrappers are `klp_pre_patch_callback()`, `klp_post_patch_callback()`, `klp_pre_unpatch_callback()`, and `klp_post_unpatch_callback()`.

## Control Flow
Consumers include core lifecycle code, ftrace patching, state compatibility, and transition code. The callback wrappers normalize optional object callbacks and maintain `obj->callbacks.post_unpatch_enabled`, ensuring `post_unpatch` only runs after a successful `pre_patch` path.

## State and Persistence Behavior
The header does not store state itself. It defines access to process-wide livepatch state and enforces the callback flag convention used across enable, disable, module load, and rollback paths.

## Dependencies and Integration Points
It includes `<linux/livepatch.h>` and depends on `struct klp_patch`, `struct klp_object`, callback layouts, and kernel list/mutex facilities supplied through livepatch headers. It is consumed by `core.c`, `patch.c`, `state.c`, and `transition.c`.

## Risks and Test Signals
The callback wrappers are deceptively small but define rollback semantics. Regressions can double-run `post_unpatch`, skip it after a successful pre-patch, or treat unloaded module objects as patchable. Test signals include callback order tests around successful enable/disable, pre-patch failure, module unload, and atomic replace cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/patch.c -->
# sources/distributed-fs/ceph-client/kernel/livepatch/patch.c

## Purpose
`patch.c` implements the ftrace-backed function redirection layer for livepatch. It maps each original function address to one `struct klp_ops` ftrace registration, maintains an RCU-protected stack of replacement `struct klp_func` entries for that original function, and updates function instruction pointers at ftrace time according to the current task's livepatch transition state.

## Important APIs, Types, and Functions
The global `klp_ops` list tracks registered ftrace operations. `klp_find_ops()` locates the ftrace registration for an old function. `klp_patch_object()` patches every function in a loaded object; `klp_unpatch_object()`, `klp_unpatch_objects()`, and `klp_unpatch_objects_dynamic()` remove all or only dynamic NOP entries.

The hot path is `klp_ftrace_handler()`. Internal helpers are `klp_patch_func()`, `klp_unpatch_func()`, and `__klp_unpatch_object()`. `struct klp_ops` itself is declared in `patch.h` and contains a global list node, `func_stack`, and `struct ftrace_ops`.

## Control Flow
When the first livepatch function targets an original function, `klp_patch_func()` allocates `struct klp_ops`, initializes `fops` with the livepatch ftrace handler and IP modification flags, adds the new `klp_func` to `func_stack`, installs an ftrace filter at the original function location, and registers the ftrace function. Later patches for the same original function only push another `klp_func` onto the existing stack.

At runtime, `klp_ftrace_handler()` enters under ftrace recursion protection, reads the top `klp_func` with RCU, observes memory barriers required by transition setup, and decides whether to use the top replacement or a previous stack entry. During patching, tasks that have switched to the patched state use the top replacement. During unpatching, tasks still in the patched state may continue to see the patched entry, while unpatched tasks skip to the previous entry or original function. NOP entries deliberately avoid changing the instruction pointer.

Unpatching removes a function from the stack with `list_del_rcu()`. If the stack becomes singular, it unregisters ftrace, removes the filter, deletes the `klp_ops` node, and frees it; otherwise it only removes the function stack entry.

## State and Persistence Behavior
State is transient kernel memory: one ftrace registration per original function and an RCU-visible stack of active replacement functions. `func->patched` records whether a specific `klp_func` is active. RCU synchronization is delegated to ftrace unregister and transition synchronization so removed stack entries are not observed after freeing.

## Dependencies and Integration Points
This file depends on ftrace IP modification support, RCU list primitives, livepatch task transition state from `transition.c`, and object/function metadata initialized by `core.c`. It is called by core enable/disable and module load/unload paths.

## Risks and Test Signals
The main risks are ftrace registration failure cleanup, stack ordering mistakes during cumulative and atomic replace patches, selecting the wrong function during transition, and missing RCU/ftrace synchronization before freeing entries. Tests should include stacking multiple patches on one function, unpatching the top and final entries, NOP replace entries, concurrent task transitions, forced transitions, and ftrace filter/register failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/patch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/patch.h -->
# sources/distributed-fs/ceph-client/kernel/livepatch/patch.h

## Purpose
`patch.h` defines the internal ftrace patching interface used by the livepatch core and transition logic.

## Important APIs, Types, and Functions
`struct klp_ops` groups the global list node, RCU-visible `func_stack`, and registered `struct ftrace_ops`. The header declares `klp_find_ops()`, `klp_patch_object()`, `klp_unpatch_object()`, `klp_unpatch_objects()`, and `klp_unpatch_objects_dynamic()`.

## Control Flow
Core code calls `klp_patch_object()` after an object's symbols and relocations are ready. Transition and replace cleanup call unpatch helpers to remove normal or dynamic NOP stack entries. `klp_find_ops()` lets stack-checking logic find the previous active function for a given original function.

## State and Persistence Behavior
The header does not allocate state; it describes the in-memory ftrace state stack used by `patch.c`. The stack is part of live runtime redirection and is not persistent across module unload or reboot.

## Dependencies and Integration Points
It includes livepatch, list, and ftrace headers. It is used by `core.c` and `transition.c` to connect lifecycle management to function redirection.

## Risks and Test Signals
The `func_stack` contract is central: the first element is active unless transition state selects a lower entry. Tests should verify that stack traversal, replace cleanup, and transition stack checks agree on ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/patch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/shadow.c -->
# sources/distributed-fs/ceph-client/kernel/livepatch/shadow.c

## Purpose
`shadow.c` implements the livepatch shadow variable API: an RCU-safe global hash table mapping an arbitrary parent object pointer and caller-defined ID to a patch-owned data buffer. It lets livepatches attach auxiliary state to existing kernel objects without changing those object layouts.

## Important APIs, Types, and Functions
The internal `struct klp_shadow` contains an hlist node, RCU head, parent `obj`, numeric `id`, and flexible `data[]`. Global state is `klp_shadow_hash` and `klp_shadow_lock`.

Exported APIs are `klp_shadow_get()`, `klp_shadow_alloc()`, `klp_shadow_get_or_alloc()`, `klp_shadow_free()`, and `klp_shadow_free_all()`. Internal helpers are `klp_shadow_match()`, `__klp_shadow_get_or_alloc()`, and `klp_shadow_free_struct()`.

## Control Flow
Lookups run under `rcu_read_lock()` and scan the hash bucket keyed by the object pointer. Allocation first checks locklessly, speculatively allocates zeroed storage, rechecks under `klp_shadow_lock`, optionally invokes the constructor under that spinlock, then publishes the entry with `hash_add_rcu()`. `klp_shadow_alloc()` warns and returns `NULL` on duplicates; `klp_shadow_get_or_alloc()` returns the existing data pointer.

Freeing acquires the spinlock, removes matching entries with `hash_del_rcu()`, runs an optional destructor, and defers memory release with `kfree_rcu()`. `klp_shadow_free_all()` scans every bucket and removes all entries with a given ID.

## State and Persistence Behavior
Shadow variables are runtime-only and persist until explicitly freed by the livepatch or until system shutdown. The data payload is owned by the caller. The implementation guarantees the shadow structure remains alive for concurrent readers via RCU but does not serialize access to caller payload contents.

## Dependencies and Integration Points
The file integrates with the public livepatch shadow API in `<linux/livepatch.h>`, kernel hashtable helpers, spinlocks, RCU, and slab allocation. Livepatch replacement code and callbacks can use it to migrate or annotate state across patched object lifetimes.

## Risks and Test Signals
Constructors run under a spinlock and must not sleep. Callers must handle payload locking and lifetime after free; a returned data pointer is not protected after the caller leaves its own synchronization. Duplicate allocation behavior differs between `alloc` and `get_or_alloc`. Tests should stress concurrent get/free, duplicate allocation, constructor failure, destructor execution, free-all by ID, and invalid sleeping constructors under lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/shadow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/state.c -->
# sources/distributed-fs/ceph-client/kernel/livepatch/state.c

## Purpose
`state.c` tracks compatibility of system state modifications declared by livepatches. It lets patches declare custom state IDs and versions, then prevents cumulative replace patches from discarding or downgrading state already modified by installed livepatches.

## Important APIs, Types, and Functions
`klp_for_each_state()` iterates a patch's state array until an ID of zero. Exported APIs are `klp_get_state()` and `klp_get_prev_state()`. Internal compatibility helpers are `klp_is_state_compatible()` and `klp_is_patch_compatible()`, with the last declared in `state.h` for core enable validation.

## Control Flow
`klp_get_state()` scans a specific patch for an ID. `klp_get_prev_state()` is only valid during a transition and scans installed patches before `klp_transition_patch`, returning the latest matching state. During patch enable, `klp_is_patch_compatible()` checks every state from every active old patch. If the new patch declares the same state, its version must be at least as new; if it omits the state, it is compatible only when the new patch is not an atomic replace patch.

## State and Persistence Behavior
The state table is static metadata in livepatch modules. No state is persisted by this file; it protects semantic persistence of externally modified kernel state across patch stacking and replacement.

## Dependencies and Integration Points
It depends on livepatch metadata structures, the active patch list from `core.h`, and `klp_transition_patch` from `transition.h`. Patch callbacks use `klp_get_state()` and `klp_get_prev_state()` to migrate or understand prior livepatch state.

## Risks and Test Signals
Missing or lower-version state in a replace patch can make kernel state incompatible after old patches are removed, so enable must fail. `klp_get_prev_state()` relies on transition ordering and should not be used outside transition callbacks. Tests should cover cumulative patch compatibility, non-replace patch coexistence, previous-state lookup ordering, and enable rejection for state downgrades.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/state.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/state.h -->
# sources/distributed-fs/ceph-client/kernel/livepatch/state.h

## Purpose
`state.h` exposes the internal compatibility check used by livepatch core enable logic.

## Important APIs, Types, and Functions
The only declared function is `bool klp_is_patch_compatible(struct klp_patch *patch)`.

## Control Flow
`core.c` calls this before taking ownership of a new livepatch module and before initializing patch structures. The check scans existing patch state metadata and rejects incompatible replace patches.

## State and Persistence Behavior
The header has no state. It provides access to state compatibility policy implemented in `state.c`.

## Dependencies and Integration Points
It includes `<linux/livepatch.h>` for `struct klp_patch`. It links the state subsystem into the patch enable path.

## Risks and Test Signals
The main risk is bypassing this check in new enable paths. Test signals are livepatch enable tests with state arrays and replace/non-replace combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/transition.c -->
# sources/distributed-fs/ceph-client/kernel/livepatch/transition.c

## Purpose
`transition.c` implements the livepatch consistency model. It tracks the currently transitioning patch, target patch state, per-task patch states, pending thread flags, reliable-stack checks, scheduler-assisted task switching, transition reversal, forced completion, and final cleanup once every task has safely moved to the target patch state.

## Important APIs, Types, and Functions
Global transition state is `klp_transition_patch`, `klp_target_state`, `klp_signals_cnt`, per-CPU `klp_stack_entries`, and static key `klp_sched_try_switch_key`. Public functions are `klp_init_transition()`, `klp_start_transition()`, `klp_try_complete_transition()`, `klp_cancel_transition()`, `klp_reverse_transition()`, `klp_force_transition()`, `klp_update_patch_state()`, `__klp_sched_try_switch()`, and `klp_copy_process()`.

Important helpers include `klp_synchronize_transition()`, `klp_complete_transition()`, `klp_check_stack_func()`, `klp_check_stack()`, `klp_check_and_switch_task()`, `klp_try_switch_task()`, and `klp_send_signals()`. Delayed work `klp_transition_work` periodically retries straggler tasks.

## Control Flow
`klp_init_transition()` sets `klp_transition_patch`, chooses target state, initializes all tasks and idle tasks to the opposite initial state, issues ordering barriers, and marks every function in the patch as `transition = true`. `klp_start_transition()` sets `TIF_PATCH_PENDING` for tasks whose `patch_state` differs from the target, marks idle tasks pending, enables scheduler switching through a static key, and resets signal retry count.

`klp_try_complete_transition()` attempts to move normal and idle tasks by checking whether they are already switched or can be switched safely. With reliable stacks, inactive tasks are inspected for frames in to-be-patched or to-be-unpatched functions; if safe, `patch_state` is updated and `TIF_PATCH_PENDING` is cleared. Incomplete transitions schedule retry work and periodically wake kthreads or set notify signals on userspace tasks.

When complete, `klp_complete_transition()` handles replace cleanup, unpatches objects on disable, synchronizes against ftrace handler readers, clears function transition flags, resets every task to `KLP_TRANSITION_IDLE`, invokes post callbacks, and clears global transition state. Disabled patches or replaced patches are then asynchronously freed by `klp_try_complete_transition()`.

## State and Persistence Behavior
Transition state is transient and process-wide. Per-task `task->patch_state` and `TIF_PATCH_PENDING` define which function stack entry ftrace may expose to that task. The scheduler static key remains enabled only during an active transition. Forced transitions clear pending flags even if tasks are active, marking patches as forced so cleanup avoids unsafe module reference drops.

## Dependencies and Integration Points
This file integrates with scheduler hooks (`__klp_sched_try_switch()`), fork path (`klp_copy_process()`), tasklist and CPU iteration, reliable stacktrace support, ftrace stack state from `patch.c`, object callbacks and patch list helpers from `core.c`, and architecture support signaled by `klp_have_reliable_stack()`.

## Risks and Test Signals
Correctness depends on memory barriers between task states, function transition flags, and ftrace stack visibility. Architectures without reliable stacks may leave transitions pending until kernel exit or force. Forced completion can break the consistency model and is deliberately administrator-controlled. Tests should cover patch and unpatch transitions, long-sleeping tasks on patched functions, CPU-bound kthreads, idle/offline CPUs, fork during transition, reverse transition via sysfs, forced transition, atomic replace cleanup, and no stale `TIF_PATCH_PENDING` after completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/transition.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/transition.h -->
# sources/distributed-fs/ceph-client/kernel/livepatch/transition.h

## Purpose
`transition.h` declares the internal livepatch transition interface used by core and patching code.

## Important APIs, Types, and Functions
It exposes `extern struct klp_patch *klp_transition_patch` and declares `klp_init_transition()`, `klp_cancel_transition()`, `klp_start_transition()`, `klp_try_complete_transition()`, `klp_reverse_transition()`, and `klp_force_transition()`.

## Control Flow
Core enable/disable code initializes and starts transitions through this API, sysfs reversal and force paths use the reverse/force calls, and state compatibility code uses `klp_transition_patch` to identify previously installed patches during callbacks.

## State and Persistence Behavior
The header itself has no state but exposes the single global active-transition pointer. Only one transition can run at a time.

## Dependencies and Integration Points
It includes `<linux/livepatch.h>`. It bridges `core.c`, `state.c`, and the scheduler/ftrace transition implementation.

## Risks and Test Signals
Any new caller must hold the livepatch mutex or otherwise satisfy transition serialization. Tests should verify concurrent enable/disable attempts return busy and do not corrupt `klp_transition_patch`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/livepatch/transition.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/liveupdate/Kconfig

## Purpose
`Kconfig` defines the configuration menu for Kexec Handover and the Live Update Orchestrator. It ties live update support to architecture kexec handover capability, KHO scratch memory, file-based kexec, libfdt, CMA, debug options, and optional memfd preservation.

## Important APIs, Types, and Functions
Configuration symbols are `KEXEC_HANDOVER`, `KEXEC_HANDOVER_DEBUG`, `KEXEC_HANDOVER_DEBUGFS`, `KEXEC_HANDOVER_ENABLE_DEFAULT`, `LIVEUPDATE`, and `LIVEUPDATE_MEMFD`. `KEXEC_HANDOVER` selects `MEMBLOCK_KHO_SCRATCH`, `KEXEC_FILE`, `LIBFDT`, and `CMA`; `LIVEUPDATE` depends on `KEXEC_HANDOVER`; `LIVEUPDATE_MEMFD` depends on memfd and shmem support.

## Control Flow
Build-time selection controls which source files compile and which command-line defaults apply. `KEXEC_HANDOVER_ENABLE_DEFAULT` initializes KHO as enabled unless `kho=off` is passed. `LIVEUPDATE` enables the `/dev/liveupdate` orchestrator and KHO subtree management.

## State and Persistence Behavior
The file has no runtime state. Its choices determine whether handover metadata, scratch reservations, debugfs, and liveupdate state persistence are available.

## Dependencies and Integration Points
It integrates with architecture KHO support, kexec file loading, FDT metadata, CMA/memblock scratch handling, debugfs, and memfd/shmem liveupdate support.

## Risks and Test Signals
Configuration dependency mistakes can produce builds without required memblock/libfdt/CMA support or expose LUO without KHO. Test signals include `allmodconfig`/`allyesconfig` builds, KHO disabled by command line despite default enable, debugfs on/off builds, and LIVEUPDATE_MEMFD dependency builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/Makefile -->
# sources/distributed-fs/ceph-client/kernel/liveupdate/Makefile

## Purpose
`Makefile` maps liveupdate/KHO configuration symbols to object files and groups the LUO implementation into a composite `luo.o`.

## Important APIs, Types, and Functions
`luo-y` contains `luo_core.o`, `luo_file.o`, `luo_flb.o`, and `luo_session.o`. `obj-$(CONFIG_KEXEC_HANDOVER)` builds `kexec_handover.o`; debug and debugfs objects are conditional; `obj-$(CONFIG_LIVEUPDATE)` builds `luo.o`.

## Control Flow
The build system compiles KHO core independently when enabled and links LUO as a multi-object unit only when liveupdate is configured. Optional debug functionality is split so production builds can omit checks and debugfs.

## State and Persistence Behavior
No runtime state. The object grouping determines which initcalls and exported symbols enter the kernel image.

## Dependencies and Integration Points
It is driven by the Kconfig symbols in the same directory and kernel kbuild composite object rules.

## Risks and Test Signals
Missing an object from `luo-y` would silently remove an initcall or exported registration function. Build tests should cover KHO-only, KHO+debug, KHO+debugfs, and full LIVEUPDATE configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/kexec_handover.c -->
# sources/distributed-fs/ceph-client/kernel/liveupdate/kexec_handover.c

## Purpose
`kexec_handover.c` implements Kexec Handover metadata and preserved-memory management. It lets the current kernel mark pages, folios, vmalloc areas, and FDT subtrees for preservation across a kexec, then lets the next kernel discover the KHO FDT, reserve preserved memory in memblock, restore page ownership, recreate vmalloc mappings, and use scratch memory for safe early boot allocation.

## Important APIs, Types, and Functions
Global control includes `kho_enable`, `kho_is_enabled()`, early params `kho=` and `kho_scratch=`, outgoing state `struct kho_out`, incoming state `struct kho_in`, global `kho_scratch`, and `kho_scratch_cnt`. The preservation radix tree uses `struct kho_radix_tree`, `kho_radix_add_page()`, `kho_radix_del_page()`, `kho_radix_walk_tree()`, and helpers to encode/decode physical address plus order into a key.

Memory APIs exported to other subsystems are `kho_preserve_folio()`, `kho_unpreserve_folio()`, `kho_restore_folio()`, `kho_preserve_pages()`, `kho_unpreserve_pages()`, `kho_restore_pages()`, `kho_preserve_vmalloc()`, `kho_unpreserve_vmalloc()`, `kho_restore_vmalloc()`, `kho_alloc_preserve()`, `kho_unpreserve_free()`, and `kho_restore_free()`. FDT subtree APIs are `kho_add_subtree()`, `kho_remove_subtree()`, and `kho_retrieve_subtree()`. Boot/kexec integration includes `kho_memory_init()`, `kho_populate()`, `kho_fill_kimage()`, and `kho_locate_mem_hole()`.

## Control Flow
On cold boot with KHO enabled, `kho_memory_init()` reserves scratch areas using memblock and CMA alignment. Later `kho_init()` allocates the outgoing radix tree root and preserved root FDT, initializes debugfs, writes the KHO FDT root with the physical address of the memory map, creates kexec metadata, initializes scratch pageblocks as CMA, and exposes the outgoing FDT in debugfs.

For an incoming KHO boot, early platform code calls `kho_populate()` with FDT and scratch physical ranges. It validates the FDT header and compatible string, retrieves the preserved memory map pointer, maps scratch descriptors, adds scratch areas to memblock, marks them as KHO scratch, reserves the descriptor array, forces early memblock allocation to scratch only, and records incoming FDT/scratch metadata. Then `kho_memory_init()` releases scratch to CMA-like pageblocks and calls `kho_mem_retrieve()` to walk the prior radix tree and reserve all preserved pages with `KHO_PAGE_MAGIC` and order stored in `page->private`.

Preserving pages inserts encoded PFN/order ranges into the outgoing radix tree, with `kho_preserve_pages()` splitting a range by alignment and NUMA node boundaries. Restoring checks the magic/order in `page->private`, clears it, initializes page or folio refcounts and compound metadata, adjusts managed page counts, and returns the page/folio. Vmalloc preservation serializes physical chunks into preserved `struct kho_vmalloc_chunk` pages and restore reconstructs a vmalloc area from restored pages.

Kexec image setup stores the outgoing FDT physical address in `image->kho.fdt`, copies scratch descriptors into a kexec segment, and constrains regular kexec buffer placement to KHO scratch regions when KHO is active.

## State and Persistence Behavior
Persistent handover state is the KHO root FDT, subtree physical pointers and sizes, the preserved-memory radix tree, preserved page contents, scratch descriptor array, and optional kexec metadata. Page order/magic is reconstructed in the new kernel by reserving preserved pages and writing `page->private`. Runtime outgoing state is protected by mutexes on the FDT and radix tree. KHO deliberately avoids preserving scratch areas and debug mode can detect overlap.

## Dependencies and Integration Points
The file depends on memblock internals, CMA/pageblock migration, kexec file loading, libfdt, early ioremap, vmalloc internals, KASAN vmalloc unpoisoning, kmemleak exclusion, KHO ABI headers, and `kexec_handover_internal.h` debug/debugfs helpers. LUO uses `kho_alloc_preserve()`, FDT subtree APIs, and page/vmalloc preservation for session/file state.

## Risks and Test Signals
Preserved memory reservation is safety-critical: missing a radix entry can let the new kernel overwrite live state, while stale entries leak memory. Radix key encoding must distinguish order and physical address across the full address range. Scratch sizing and reservation failures disable KHO. `kho_restore_page()` trusts magic/order in `page->private` and must reject double restores. Vmalloc restore must exactly match total pages, flags, and order. Tests should cover cold and incoming KHO boots, malformed FDTs, scratch override parsing, lowmem/global/per-node scratch allocation, page/folio/vmalloc preserve-restore-unpreserve cycles, subtree add/remove/retrieve, kexec metadata versioning, crash-kexec bypass, and debug scratch-overlap detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/kexec_handover.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/kexec_handover_debug.c -->
# sources/distributed-fs/ceph-client/kernel/liveupdate/kexec_handover_debug.c

## Purpose
`kexec_handover_debug.c` provides optional KHO debug validation helpers, currently focused on detecting attempts to preserve memory that overlaps KHO scratch areas.

## Important APIs, Types, and Functions
The exported/internal function is `kho_scratch_overlap(phys_addr_t phys, size_t size)`. It scans global `kho_scratch` descriptors and `kho_scratch_cnt`.

## Control Flow
For each scratch region, the function computes `[scratch_start, scratch_end)` and tests interval overlap with `[phys, phys + size)`. It returns true on the first overlap, otherwise false.

## State and Persistence Behavior
The file does not persist state; it reads scratch descriptors prepared by KHO boot memory setup.

## Dependencies and Integration Points
It includes `kexec_handover_internal.h`. `kho_preserve_folio()` and `kho_preserve_pages()` call this helper under `CONFIG_KEXEC_HANDOVER_DEBUG` and reject overlapping preservations.

## Risks and Test Signals
The overlap check assumes non-overflowing `phys + size`; very large ranges should be scrutinized. Tests should preserve ranges before, inside, spanning, and after scratch areas and verify non-debug builds compile to the inline false helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/kexec_handover_debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/kexec_handover_debugfs.c -->
# sources/distributed-fs/ceph-client/kernel/liveupdate/kexec_handover_debugfs.c

## Purpose
`kexec_handover_debugfs.c` exposes KHO incoming and outgoing metadata through debugfs. It lets developers inspect root FDT blobs, preserved subtree blobs, and scratch region physical addresses/sizes.

## Important APIs, Types, and Functions
Global `debugfs_root` is `/sys/kernel/debug/kho`. Internal `struct fdt_debugfs` stores list linkage, `debugfs_blob_wrapper`, and dentry. Public helpers are `kho_debugfs_init()`, `kho_in_debugfs_init()`, `kho_out_debugfs_init()`, `kho_debugfs_blob_add()`, and `kho_debugfs_blob_remove()`. Show helpers are `scratch_phys_show()` and `scratch_len_show()`.

## Control Flow
`kho_debugfs_init()` creates the root directory. `kho_out_debugfs_init()` creates `out`, `out/sub_fdts`, and readonly files for scratch physical addresses and lengths. `kho_in_debugfs_init()` creates `in`, exposes the incoming root FDT as a blob, walks FDT subnodes, validates subtree pointer and size properties, maps them with `phys_to_virt()`, and exposes each as a blob under `in/sub_fdts`.

`kho_debugfs_blob_add()` chooses either the root KHO debugfs directory or `sub_fdts` and creates a blob wrapper; `kho_debugfs_blob_remove()` removes the matching wrapper by data pointer.

## State and Persistence Behavior
Debugfs state is runtime-only and mirrors live KHO FDT pointers. Blob wrappers point directly at preserved or allocated FDT memory; they do not copy blob contents. Entries are removed when subtrees are removed or recursively if init fails.

## Dependencies and Integration Points
It depends on debugfs, libfdt, KHO ABI property names, `phys_to_virt()`, and scratch globals from KHO core. It is called by KHO init and subtree add/remove paths when `CONFIG_KEXEC_HANDOVER_DEBUGFS` is enabled.

## Risks and Test Signals
Debugfs exposes raw handover metadata to root and can show stale data if blobs are freed without removal. Incoming subtree validation must tolerate malformed FDT nodes. Tests should mount debugfs and verify `kho/out/fdt`, `out/sub_fdts`, scratch files, incoming FDT blobs after KHO boot, subtree add/remove cleanup, and debugfs-disabled inline stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/kexec_handover_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/kexec_handover_internal.h -->
# sources/distributed-fs/ceph-client/kernel/liveupdate/kexec_handover_internal.h

## Purpose
`kexec_handover_internal.h` is the private KHO header shared by core, debug, and debugfs implementations. It declares scratch globals and provides conditional debug/debugfs APIs or no-op stubs.

## Important APIs, Types, and Functions
When debugfs is enabled, `struct kho_debugfs` contains a root directory, subtree directory, and list of FDT blob wrappers; otherwise it is an empty struct. It declares `kho_scratch`, `kho_scratch_cnt`, `kho_debugfs_init()`, `kho_in_debugfs_init()`, `kho_out_debugfs_init()`, `kho_debugfs_blob_add()`, `kho_debugfs_blob_remove()`, and `kho_scratch_overlap()`.

## Control Flow
KHO core can call the debugfs and debug functions unconditionally; the header resolves them to real implementations or inline no-ops/false based on configuration.

## State and Persistence Behavior
The header exposes global scratch descriptor state. Debugfs list state exists only with `CONFIG_KEXEC_HANDOVER_DEBUGFS`.

## Dependencies and Integration Points
It includes public KHO types, list/types, and debugfs when configured. It is included by `kexec_handover.c`, `kexec_handover_debug.c`, and `kexec_handover_debugfs.c`.

## Risks and Test Signals
Stub signatures must stay compatible with real implementations so KHO core code remains config-independent. Build tests should cover every combination of KHO debug and debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/kexec_handover_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/luo_core.c -->
# sources/distributed-fs/ceph-client/kernel/liveupdate/luo_core.c

## Purpose
`luo_core.c` implements the Live Update Orchestrator entry points, boot-time FDT setup/retrieval, global enable state, reboot serialization hook, and `/dev/liveupdate` control device. It coordinates LUO sessions and file lifecycle-bound global data on top of KHO subtrees.

## Important APIs, Types, and Functions
Global state is `luo_global` with `enabled`, outgoing/incoming FDT pointers, and `liveupdate_num`, plus exported `luo_register_rwlock` for handler/FLB registration. Early/late init functions are `liveupdate_early_init()`, `luo_early_startup()`, `luo_late_startup()`, and `luo_fdt_setup()`. Public runtime functions are `liveupdate_reboot()` and `liveupdate_enabled()`.

The control device uses `struct luo_device_state`, `luo_open()`, `luo_release()`, `luo_ioctl()`, and ioctl handlers `luo_ioctl_create_session()` and `luo_ioctl_retrieve_session()`. It registers a misc device named `liveupdate`.

## Control Flow
The `liveupdate=` early parameter controls `luo_global.enabled`; KHO disablement forces LUO off. Early init tries to retrieve the LUO subtree from KHO. If present, it validates the LUO FDT compatible string, loads the liveupdate counter, and sets up incoming session and FLB headers. A failure in incoming restore panics through `luo_restore_fail()` because the preserved state may be inconsistent.

Late init prepares an outgoing LUO FDT when liveupdate is enabled. It allocates preserved FDT memory, writes compatible and incremented liveupdate number properties, adds session and FLB nodes, finalizes the FDT, and registers it as a KHO subtree.

Userspace opens `/dev/liveupdate` exclusively. Open triggers one-time session deserialization, so incoming sessions become available only when the controller starts. Ioctls create new outgoing sessions or retrieve named incoming sessions and return file descriptors.

On kexec reboot, `liveupdate_reboot()` serializes all outgoing sessions; if successful, it serializes FLB metadata. Errors abort reboot before KHO finalization.

## State and Persistence Behavior
LUO persists a dedicated FDT subtree through KHO, including a monotonic liveupdate number, session header pointer, and FLB header pointer. Runtime state includes incoming/outgoing FDT pointers, an exclusive-open flag, session lists, file handlers, FLBs, and preserved KHO allocations. `/dev/liveupdate` is singleton to avoid conflicting userspace controllers.

## Dependencies and Integration Points
It depends on KHO subtree APIs, libfdt, miscdevice/file descriptor APIs, UAPI liveupdate ioctls, session and FLB modules, and reboot/kexec integration through `liveupdate_reboot()`. File handler registration across LUO modules is serialized by `luo_register_rwlock`.

## Risks and Test Signals
Incoming FDT corruption is treated as fatal; tests must validate panic paths only in controlled environments. Ioctl size negotiation uses `copy_struct_from_user()` and minimum field offsets; ABI changes must preserve compatibility. Exclusive open prevents races but also serializes deserialization failures into `-EIO`. Tests should cover `liveupdate=on/off`, KHO disabled, cold boot with no subtree, incoming subtree validation, create/retrieve session ioctls, open exclusivity, and reboot serialization rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/luo_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/luo_file.c -->
# sources/distributed-fs/ceph-client/kernel/liveupdate/luo_file.c

## Purpose
`luo_file.c` implements LUO's preserved file descriptor lifecycle. It lets sessions preserve user file descriptors with type-specific registered handlers, freeze and serialize them before kexec, deserialize them in the next kernel, retrieve replacement file descriptors by token, and finish cleanup after userspace has reattached.

## Important APIs, Types, and Functions
Global registries are `luo_file_handler_list` and xarray `luo_preserved_files`. Internal `struct luo_file` tracks handler, `struct file`, serialized data, runtime private data, retrieve status, mutex, list node, and user token. Constants `LUO_FILE_PGCNT` and `LUO_FILE_MAX` size the preserved serialization array.

Core APIs are `luo_preserve_file()`, `luo_file_unpreserve_files()`, `luo_file_freeze()`, `luo_file_unfreeze()`, `luo_retrieve_file()`, `luo_file_finish()`, `luo_file_deserialize()`, `luo_file_set_init()`, and `luo_file_set_destroy()`. Registration exports are `liveupdate_register_file_handler()` and `liveupdate_unregister_file_handler()`.

## Control Flow
Preservation validates unique token and capacity, gets the user file via `fget()`, allocates preserved serialization memory if needed, finds a registered handler whose `can_preserve()` accepts the file, takes the handler module reference, inserts the file ID into the global xarray to prevent duplicate preservation, preserves dependent FLBs, allocates `struct luo_file`, calls handler `.preserve()`, stores returned serialized/private handles, and appends the file to the session file set.

Abort-before-reboot cleanup walks files in reverse preservation order, calls handler `.unpreserve()`, decrements FLB references, drops module references, erases xarray entries, drops file references, destroys mutexes, and frees serialization memory when empty.

Freeze walks files in FIFO order. Each file optionally calls handler `.freeze()` and updates `serialized_data`, then writes compatible string, serialized data, and token into the preserved array. If a freeze fails, previously frozen files are unfrozen and serialized memory is cleared. Unfreeze can also roll back all files after a reboot abort.

Deserialization maps the preserved file array, finds handlers by compatible string, takes module references, allocates `struct luo_file` objects with `file = NULL`, and stores token/data for later retrieval. Retrieval by token is idempotent after success, permanently returns the saved error after a failed retrieve attempt, calls handler `.retrieve()` on first success, takes LUO's ownership reference, and tracks the file in the xarray. Finish first checks every file's optional `.can_finish()`, then runs `.finish()`, releases FLBs/module refs/files, frees entries, and calls `kho_restore_free()` on the serialized array.

## State and Persistence Behavior
Per-file persistent state is serialized into `struct luo_file_ser` entries in KHO-preserved memory: handler compatible string, user token, and handler-provided opaque data. Runtime-only state includes `private_data`, file references, handler module references, xarray duplicate tracking, retrieve status, and mutexes. Failure policy after deserialization is intentionally leak-and-reboot because partial hardware/file restore cannot be safely undone.

## Dependencies and Integration Points
It depends on liveupdate handler/FLB public APIs, KHO preserved allocations, session-owned `struct luo_file_set`, xarray, module refcounting, file descriptor APIs, and `luo_register_rwlock`. Handlers for memfd, vfio, iommufd, or other subsystems plug in through `struct liveupdate_file_handler`.

## Risks and Test Signals
File IDs from handler `get_id()` must uniquely identify resources or duplicate preservation can slip through. Handler callbacks must maintain their own locking and serialized-data lifetime. Freeze rollback must unfreeze exactly the already frozen prefix. Retrieval records first failure permanently, which may surprise retry logic. Tests should cover duplicate tokens, duplicate file IDs, handler registration/unregistration, preserve error injection at every step, FLB rollback, freeze/unfreeze ordering, deserialize with missing handler, idempotent retrieve success, retrieve failure persistence, finish `-EBUSY`, and release paths for outgoing and incoming sessions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/luo_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/luo_flb.c -->
# sources/distributed-fs/ceph-client/kernel/liveupdate/luo_flb.c

## Purpose
`luo_flb.c` implements File-Lifecycle-Bound global data. FLBs let file handlers declare shared global state that should be preserved once when the first dependent file is preserved, referenced by every dependent file, restored on demand in the new kernel, and finished when the last dependent file is finished.

## Important APIs, Types, and Functions
Internal types are `struct luo_flb_header`, `struct luo_flb_global`, and `struct luo_flb_link`. Global state `luo_flb_global` contains incoming/outgoing serialized headers, the global FLB list, and a count capped by `LUO_FLB_MAX`.

Private per-FLB state is accessed through `luo_flb_get_private()`, which lazily initializes locks, list state, and counts in `struct luo_flb_private`. File lifecycle hooks are `luo_flb_file_preserve()`, `luo_flb_file_unpreserve()`, `luo_flb_file_finish()`, and their per-FLB helpers. Registration APIs are `liveupdate_register_flb()`, `liveupdate_unregister_flb()`, `liveupdate_flb_get_incoming()`, and `liveupdate_flb_get_outgoing()`. FDT setup/serialization functions are `luo_flb_setup_outgoing()`, `luo_flb_setup_incoming()`, and `luo_flb_serialize()`.

## Control Flow
`liveupdate_register_flb()` links an FLB to a registered file handler, checks callback presence, prevents duplicate per-handler and global compatible strings, adds the FLB to the global list on first use, and increments user count. Unregister removes links and drops the global entry when no handlers use it.

When a file is preserved, `luo_flb_file_preserve()` iterates the handler's FLB dependencies in registration order. For each dependency, `luo_flb_file_preserve_one()` calls `.preserve()` only when outgoing count is zero, stores returned data/object, takes the owner module reference, and increments count. On failure, already preserved FLBs in that operation are unpreserved in reverse.

Pre-reboot serialization walks all global FLBs and writes entries for those with outgoing count greater than zero: compatible name, opaque data, and reference count. In the new kernel, `luo_flb_retrieve_one()` finds the matching serialized entry, takes the module reference, calls `.retrieve()`, and caches the restored object. `liveupdate_flb_get_incoming()` exposes that cached object on demand. Finish decrements incoming count per dependent file and calls `.finish()` only when it reaches zero.

## State and Persistence Behavior
Persistent FLB state is a KHO-preserved header page plus `struct luo_flb_ser` entries containing compatible string, opaque data, and dependent-file count. Runtime outgoing and incoming private state separately track data, object pointer, reference counts, retrieved/finished flags, and locks. Module references are held while outgoing state is preserved or incoming state remains unfinished.

## Dependencies and Integration Points
It depends on LUO file handler private list fields, `luo_register_rwlock`, KHO preserved allocation, libfdt, module refs, and liveupdate FLB public callback types. File handlers call `liveupdate_register_flb()` to declare global dependencies and can query incoming/outgoing objects with the getter APIs.

## Risks and Test Signals
Lazy private initialization uses acquire/release ordering and a spinlock; races there would corrupt locks/lists. Count underflow or mismatched preserve/unpreserve/finish calls can leak modules or finish too early. `luo_flb_file_finish_one()` retrieves an FLB during finish if no one retrieved it earlier, so `.retrieve()` must be safe late. Serialization has a fixed one-page cap. Tests should cover multiple handlers sharing one FLB, duplicate compatible rejection, rollback on preserve failure, incoming lazy retrieve, finish after zero references, unregister-all while holding write lock, and capacity exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/luo_flb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/luo_internal.h -->
# sources/distributed-fs/ceph-client/kernel/liveupdate/luo_internal.h

## Purpose
`luo_internal.h` defines private LUO structs and function prototypes shared between core, session, file, and FLB implementations.

## Important APIs, Types, and Functions
`struct luo_ucmd` wraps a user buffer, user-provided size, and kernel command buffer. `luo_ucmd_respond()` copies the smaller of user and kernel struct sizes back to userspace. `luo_restore_fail()` panics on unrecoverable restore failures.

`struct luo_file_set` groups a list of preserved files, preserved serialization memory, and count. `struct luo_session` stores name, serialized pointer, list node, retrieval flag, file set, and mutex. The header declares session, file, and FLB internal APIs plus `extern struct rw_semaphore luo_register_rwlock`.

## Control Flow
Core ioctl handlers and session ioctl handlers use `luo_ucmd` for ABI-size-compatible command handling. Session code calls file-set APIs. File code calls FLB APIs. Early and late init call setup functions for incoming/outgoing session and FLB FDT nodes.

## State and Persistence Behavior
The header defines the runtime containers whose contents are serialized through KHO by the corresponding `.c` files. The panic macro encodes the policy that failed incoming deserialization is not recoverable.

## Dependencies and Integration Points
It includes public `<linux/liveupdate.h>` and user access helpers. It is included by every LUO implementation file and connects to UAPI structs defined in liveupdate ABI headers.

## Risks and Test Signals
`luo_ucmd_respond()` must not leak beyond the user's advertised size and must handle short new/old ABI structs. The panic policy should be validated in restore-failure tests. Structure invariants include initialized file-set lists, session mutexes, and zero counts on destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/luo_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/luo_session.c -->
# sources/distributed-fs/ceph-client/kernel/liveupdate/luo_session.c

## Purpose
`luo_session.c` implements named LUO sessions. A session is an anon-inode file descriptor that groups file descriptors to preserve, serializes the group into KHO memory before kexec, deserializes incoming sessions in the new kernel, and lets userspace retrieve preserved files by token.

## Important APIs, Types, and Functions
Internal `struct luo_session_header` tracks session count, list, rwsem, serialized header pointer, serialized array pointer, and active flag. Global `luo_session_global` has incoming and outgoing headers. Session allocation/lifetime helpers are `luo_session_alloc()`, `luo_session_free()`, `luo_session_insert()`, `luo_session_remove()`, `luo_session_getfile()`, and `luo_session_release()`.

Public/session APIs are `luo_session_create()`, `luo_session_retrieve()`, `luo_session_setup_outgoing()`, `luo_session_setup_incoming()`, `luo_session_deserialize()`, and `luo_session_serialize()`. Session fd ioctls are handled by `luo_session_ioctl()` with operations `luo_session_preserve_fd()`, `luo_session_retrieve_fd()`, and `luo_session_finish()`.

## Control Flow
Creating a session allocates a named session, inserts it into the outgoing list after duplicate/capacity checks, and returns an anon-inode file. Releasing an outgoing session before reboot unpreserves all files and removes the session. Retrieving an incoming session finds it by name, rejects repeated retrieval of the same session, returns an anon-inode file, and marks it retrieved.

Session fd ioctls preserve outgoing file descriptors by token, retrieve incoming file descriptors by token, or finish all files. The ioctl path validates command number, reads user struct size, checks minimum size, uses `copy_struct_from_user()`, and responds through `luo_ucmd_respond()`.

Outgoing setup allocates KHO-preserved session header pages and writes a session FDT node containing the physical header pointer. Serialization freezes each outgoing session's file set, writes the session name and file-set serialized metadata, and records the session count. On failure it walks already serialized sessions in reverse, unfreezes their files, and clears names.

Incoming setup reads the session node and header pointer from the LUO FDT. Deserialization is one-shot and caches the first error. It allocates each incoming session, inserts it, deserializes its files, then frees the preserved session header memory with `kho_restore_free()`.

## State and Persistence Behavior
Persistent session state is a KHO-preserved header page plus `struct luo_session_ser` array entries with session names and serialized file-set descriptors. Runtime state is separated into outgoing and incoming lists protected by r/w semaphores, plus per-session mutexes and retrieval flags. Incoming deserialization failures intentionally leak partial state and require reboot recovery.

## Dependencies and Integration Points
It depends on anon inode files, LUO file-set APIs, KHO preserved allocation, libfdt, UAPI liveupdate session ioctls, and core `/dev/liveupdate` create/retrieve paths.

## Risks and Test Signals
Session lookup is linear and duplicate names are rejected with bounded string comparison. Release returns errors if finishing an incoming session fails, which can surprise file-close paths. Serialization rollback uses `list_for_each_entry_continue_reverse()` and must match the already frozen prefix. Tests should cover capacity (`LUO_SESSION_MAX`), duplicate names, outgoing release cleanup, incoming repeated retrieval rejection, session ioctl ABI sizing, serialization failure rollback, one-shot deserialization error caching, and finishing with unretrieved files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/liveupdate/luo_session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/Makefile -->
# sources/distributed-fs/ceph-client/kernel/locking/Makefile

## Purpose
`kernel/locking/Makefile` selects core kernel locking implementation objects and disables instrumentation that would distort or recursively enter locking code.

## Important APIs, Types, and Functions
It disables KCOV for the directory, marks several objects for context analysis, builds core mutex/semaphore/rwsem/percpu-rwsem objects, disables KASAN/KCSAN for lockdep, removes ftrace instrumentation from lockdep and mutex-debug objects when function tracing is enabled, and conditionally builds debug, lockdep, spinlock, queued spinlock/rwlock, rtmutex, PREEMPT_RT, torture, ww mutex selftest, and lock event objects.

## Control Flow
Kbuild uses configuration symbols such as `DEBUG_IRQFLAGS`, `DEBUG_MUTEXES`, `LOCKDEP`, `PROC_FS`, `SMP`, `QUEUED_SPINLOCKS`, `RT_MUTEXES`, `PREEMPT_RT`, `LOCK_TORTURE_TEST`, `WW_MUTEX_SELFTEST`, and `LOCK_EVENT_COUNTS` to select implementation files.

## State and Persistence Behavior
No runtime state. Build selection determines which locking implementation and diagnostics exist in the kernel.

## Dependencies and Integration Points
It integrates with sanitizer/ftrace build flags, lockdep, debugfs lock event support, architecture spinlock implementations, PREEMPT_RT, and test modules.

## Risks and Test Signals
Instrumentation on lockdep or low-level locks can recurse and break the kernel, so flag removal matters. Build tests should cover tracing, sanitizer, PREEMPT_RT, lockdep, queued spinlock, and lock event configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/irqflag-debug.c -->
# sources/distributed-fs/ceph-client/kernel/locking/irqflag-debug.c

## Purpose
`irqflag-debug.c` provides a debug helper for IRQ flag misuse: it warns when `raw_local_irq_restore()` is called while IRQs are already enabled.

## Important APIs, Types, and Functions
The only function is exported `noinstr void warn_bogus_irq_restore(void)`. It wraps `WARN_ONCE(1, ...)` with `instrumentation_begin()` and `instrumentation_end()`.

## Control Flow
Low-level IRQ flag restore debugging code calls this helper on invalid restore state. The helper emits a one-time warning and returns.

## State and Persistence Behavior
The only state is the internal `WARN_ONCE` static state that suppresses repeated warnings. It has no persistent storage.

## Dependencies and Integration Points
It depends on bug/warn infrastructure, export symbols, and irqflags code. `noinstr` plus explicit instrumentation bracketing keeps it usable from low-level contexts.

## Risks and Test Signals
Because it is called from instrumentation-sensitive paths, adding tracing or sleeping code would be unsafe. Tests should exercise DEBUG_IRQFLAGS misuse under lockdep/debug kernels and verify the symbol exports for architecture/raw irqflag code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/irqflag-debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/lock_events.c -->
# sources/distributed-fs/ceph-client/kernel/locking/lock_events.c

## Purpose
`lock_events.c` implements debugfs reporting for low-overhead per-CPU locking event counters. It exposes one file per event under `/sys/kernel/debug/lock_event_counts/` and a `.reset_counts` write-only file.

## Important APIs, Types, and Functions
`lockevent_names[]` is generated from `lock_events_list.h`, with an additional `.reset_counts` entry. `DEFINE_PER_CPU(unsigned long, lockevents[lockevent_num])` stores counters. Public weak `lockevent_read()` sums per-CPU counters for a file's event ID. `lockevent_write()` resets all counters when writing to `.reset_counts`. `init_lockevent_counts()` creates debugfs files at `fs_initcall` time. `skip_lockevent()` hides PV qspinlock events on native bare metal when paravirt spinlocks are configured.

## Control Flow
At init, the code creates the debugfs directory, iterates event IDs, optionally skips PV-only names, and creates readonly files whose `i_private` stores the event ID. Reads sum all possible CPUs and return a decimal count. Writes to non-reset files are ignored by returning count; writes to reset loop over all possible CPUs and clear every event with `WRITE_ONCE()`.

## State and Persistence Behavior
Counters are per-CPU runtime statistics and reset on boot or `.reset_counts`. They are intentionally lossy because updates use raw per-CPU operations without expensive synchronization. Values persist while the kernel is running.

## Dependencies and Integration Points
It depends on debugfs, scheduler/per-CPU iteration, `lock_events.h`, optional paravirt spinlock detection, and event increment sites throughout locking code. The weak read function can be overridden by architecture or specialized code.

## Risks and Test Signals
Reading and resetting can be slow on large CPU systems. Event ID validation protects invalid reads. Debugfs creation failure removes partial entries. Tests should verify directory/file creation, PV event skipping on bare metal, per-CPU aggregation, reset semantics, weak override compatibility, and no measurable overhead when counters are not read.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/lock_events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/lock_events.h -->
# sources/distributed-fs/ceph-client/kernel/locking/lock_events.h

## Purpose
`lock_events.h` defines the lock event enum and low-overhead counter update macros used by locking implementations.

## Important APIs, Types, and Functions
`enum lock_events` is generated by including `lock_events_list.h`, followed by `lockevent_num` and `LOCKEVENT_reset_cnts`. Under `CONFIG_LOCK_EVENT_COUNTS`, it declares per-CPU `lockevents`, defines `__lockevent_inc()`, `lockevent_inc()`, `lockevent_cond_inc()`, `__lockevent_add()`, and `lockevent_add()`. Without the config, macros compile away while still evaluating relevant arguments for add/conditional calls. It also declares `lockevent_read()`.

## Control Flow
Locking hot paths call macros such as `lockevent_inc(lock_slowpath)` or `lockevent_cond_inc(ev, cond)`. In enabled builds, the macros update the current CPU counter with raw operations; disabled builds remove the update cost.

## State and Persistence Behavior
The header defines access to runtime per-CPU counters only when configured. No persistent state exists.

## Dependencies and Integration Points
It depends on the event list header and is consumed by queued spinlock, rwsem, rtmutex, lockdep, and debugfs reporting code.

## Risks and Test Signals
Event names must match enum constants generated by the list. Raw per-CPU updates can lose occasional counts during migration/preemption-sensitive contexts by design, so these are statistics, not exact accounting. Tests should build with and without `CONFIG_LOCK_EVENT_COUNTS` and compile every event macro call site.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/lock_events.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/lock_events_list.h -->
# sources/distributed-fs/ceph-client/kernel/locking/lock_events_list.h

## Purpose
`lock_events_list.h` is an X-macro list of supported locking statistics. It is included once to generate enum values and again to generate debugfs names.

## Important APIs, Types, and Functions
It defines `LOCK_EVENT(name)` if not already defined, then lists conditional PV qspinlock events, queued spinlock events, resilient queued spinlock timeout, rwsem events, rtlock/rtmutex slowpath events, and lockdep events.

Representative events include `pv_hash_hops`, `pv_kick_unlock`, `lock_pending`, `lock_slowpath`, `lock_use_node2/3/4`, `lock_no_node`, `rqspinlock_lock_timeout`, `rwsem_sleep_reader`, `rwsem_wake_writer`, `rwsem_opt_fail`, `rtmutex_slowlock`, `rtmutex_deadlock`, `lockdep_acquire`, and `lockdep_nocheck`.

## Control Flow
There is no executable flow. Inclusion context determines whether each `LOCK_EVENT()` expands into an enum constant, string table entry, or another generated artifact. Configuration guards include or exclude PV and queued spinlock-specific events.

## State and Persistence Behavior
The file defines the compile-time event namespace. Runtime state is allocated by `lock_events.c`/`lock_events.h` based on the generated `lockevent_num`.

## Dependencies and Integration Points
It is integrated into `lock_events.h` and `lock_events.c`, and event names are referenced by locking code macros and debugfs output.

## Risks and Test Signals
Adding, reordering, or conditionally compiling events changes enum IDs and debugfs file lists. Because names double as debugfs filenames, they should remain stable and descriptive. Tests should build all relevant config combinations and verify debugfs names match event macro call sites.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/locking/lock_events_list.h -->
