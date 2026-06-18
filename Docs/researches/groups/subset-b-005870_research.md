# Research: subset-b-005870

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lis3lv02d.h -->
# sources/distributed-fs/ceph-client/include/linux/lis3lv02d.h

## Purpose
This header defines platform data and board-level constants for ST LIS3LV02D-family accelerometer drivers. It lets board code describe axis wiring, interrupt routing, click/wakeup capabilities, power hooks, and optional block-read behavior without embedding those details in the transport driver.

## Important APIs, Types, and Functions
The central type is `struct lis3lv02d_platform_data`, which carries click flags, wakeup flags, IRQ routing, duration/threshold values, axis maps, default control register values, and platform callbacks such as setup, release, power-on, and power-off. Macros such as `LIS3_CLICK_SINGLE_X`, `LIS3_IRQ1_*`, `LIS3_WAKEUP_*`, `LIS3_HIPASS_*`, `LIS3_DEV_X`, and `LIS3_INV_DEV_X` encode hardware features and board orientation.

## Control Flow
There is no executable control flow in the header. Driver probe code consumes the platform-data structure, maps logical axes to device axes, configures interrupts and filter bits, and invokes board callbacks around device setup and power transitions.

## State and Persistence Behavior
The header owns no persistent state. State is provided by board data and becomes runtime driver configuration. Incorrect axis or IRQ constants persist only through compiled board files and can affect every boot.

## Dependencies and Integration Points
It integrates with LIS3 platform, SPI, or I2C accelerometer drivers and board files that still use platform data rather than firmware properties. It depends on integer bit fields matching the hardware register programming expected by the driver.

## Risks and Test Signals
Risks include inverted axes, missing wake events, wrong interrupt polarity, and broken suspend/resume power sequencing. Test signals are accelerometer input events, orientation sanity checks, click/wakeup interrupt delivery, and suspend/resume cycles with power callbacks enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lis3lv02d.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list.h -->
# sources/distributed-fs/ceph-client/include/linux/list.h

## Purpose
This is the kernel's generic intrusive linked-list API. It provides circular doubly linked `struct list_head` lists and single-pointer `struct hlist_head` hash lists, along with initializer, mutation, traversal, and container-conversion helpers used throughout the kernel.

## Important APIs, Types, and Functions
The list API includes `LIST_HEAD_INIT`, `LIST_HEAD`, `INIT_LIST_HEAD`, `list_add`, `list_add_tail`, `list_del`, `list_del_init`, `list_replace`, `list_swap`, `list_move`, `list_bulk_move_tail`, `list_cut_position`, `list_splice*`, and typed iteration macros such as `list_for_each_entry_safe`. Hardened builds route through `__list_add_valid()` and `__list_del_entry_valid()` and slowpath reporters. The hlist API includes `INIT_HLIST_NODE`, `hlist_unhashed`, `hlist_add_head`, `hlist_del_init`, `hlist_move_list`, `hlist_splice_init`, and typed hlist traversal macros.

## Control Flow
Most operations rewrite adjacent `next` and `prev` pointers inline. The circular list head is both sentinel and empty-list representation. Safe iterators prefetch the next node before user code may delete the current one. Hlist deletion uses the `pprev` backlink to update either a head pointer or predecessor `next` pointer without a two-pointer head.

## State and Persistence Behavior
The only state is embedded in caller-owned list nodes. Deleted regular list nodes are poisoned by `list_del`; `list_del_init` returns them to self-linked empty state. The API does not lock; callers must serialize concurrent mutation or use RCU-specific variants elsewhere.

## Dependencies and Integration Points
It depends on `container_of`, `WRITE_ONCE`, `READ_ONCE`, `poison.h`, and memory barriers for careful empty checks. It is a foundational dependency for cache, filesystem, networking, LSM, lockdep, livepatch, and driver structures.

## Risks and Test Signals
Common failures are double add, double delete, stale iterators, using unsafe iteration while deleting, and assuming `list_empty()` is a synchronization primitive. Useful signals are `CONFIG_LIST_HARDENED`, `CONFIG_DEBUG_LIST`, KASAN/UAF reports, lockdep coverage around caller locks, and targeted tests that exercise add/delete/splice/cut paths under the intended synchronization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_bl.h -->
# sources/distributed-fs/ceph-client/include/linux/list_bl.h

## Purpose
This header implements bit-locked hlist buckets. It packs a bucket lock bit into the low bit of the first-node pointer so hash tables can have compact per-bucket locking without a separate spinlock per bucket.

## Important APIs, Types, and Functions
`struct hlist_bl_head` stores `first`, whose low bit is `LIST_BL_LOCKMASK`; `struct hlist_bl_node` stores `next` and `pprev`. APIs include `INIT_HLIST_BL_HEAD`, `INIT_HLIST_BL_NODE`, `hlist_bl_first`, `hlist_bl_empty`, `hlist_bl_add_head`, `hlist_bl_add_before`, `hlist_bl_add_behind`, `hlist_bl_del`, `hlist_bl_del_init`, `hlist_bl_lock`, `hlist_bl_unlock`, `hlist_bl_is_locked`, and traversal macros.

## Control Flow
Readers mask the lock bit before dereferencing the first node. Writers acquire the bit spinlock on the bucket head, update hlist links, and preserve lock-bit encoding when replacing `first`. Deletion mirrors hlist deletion and poisons or reinitializes nodes depending on the public helper.

## State and Persistence Behavior
State is caller-owned bucket heads and nodes. The lock bit is transient synchronization state and must never leak into node pointers after masking. The header has no persistence behavior.

## Dependencies and Integration Points
It depends on `linux/list.h` and `linux/bit_spinlock.h`. Typical integration is memory-sensitive hash tables where each bucket needs local exclusion.

## Risks and Test Signals
Risks include forgetting to hold the bucket lock for mutation, dereferencing an unmasked first pointer, and alignment assumptions that would make the low bit unavailable. Test signals include debug list assertions, lockdep coverage around bucket locking, hash-table insertion/deletion stress, and KASAN reports for corrupted links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_bl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_lru.h -->
# sources/distributed-fs/ceph-client/include/linux/list_lru.h

## Purpose
This header declares the generic LRU list infrastructure used by shrinkers and reclaimable kernel caches. It provides NUMA-node and optional memcg-aware sublists, item counting, isolation, and walking contracts for reclaim callbacks.

## Important APIs, Types, and Functions
`enum lru_status` defines walker outcomes: removed, removed-retry, rotate, skip, retry, and stop. `struct list_lru_one` holds a list, item count, and spinlock. `struct list_lru_node` and `struct list_lru` aggregate per-node and memcg-aware state. APIs include `list_lru_init`, `list_lru_init_memcg`, `list_lru_destroy`, `list_lru_add`, `list_lru_add_obj`, `list_lru_del`, `list_lru_del_obj`, `list_lru_count_one`, `list_lru_count_node`, `list_lru_count`, `list_lru_walk_one`, `list_lru_walk_one_irq`, and shrinker wrappers.

## Control Flow
Add/delete route an item to a sublist by NUMA node and optionally memcg. Walkers acquire the sublist lock and call a `list_lru_walk_cb`; the callback returns an `lru_status` instructing the framework to remove, rotate, retry, skip, or stop. Callbacks may drop the lock only if they return with it held.

## State and Persistence Behavior
Runtime state is per-node/per-memcg linked lists and counts. Counts may be temporarily negative during memcg reparenting. The infrastructure has no persistence, but it affects reclaim behavior and memory pressure response.

## Dependencies and Integration Points
It integrates with shrinkers, memory cgroups, NUMA node masks, xarrays, and cache subsystems such as dentries and inodes. Memcg calls require the cgroup to be protected by RCU or a css reference.

## Risks and Test Signals
Risks include deleting with the wrong node/memcg, callback lock contract violations, inaccurate shrinker counts under concurrent mutation, and memcg reparenting races. Test signals are shrinker stress, memcg create/delete tests, lockdep on list locks, reclaim under pressure, and object leak/count consistency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_lru.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_nulls.h -->
# sources/distributed-fs/ceph-client/include/linux/list_nulls.h

## Purpose
This header defines nulls-terminated hlists, a hash-list variant whose end marker encodes a bucket value. It supports lockless lookup patterns that can detect when traversal ended in the wrong bucket after concurrent movement.

## Important APIs, Types, and Functions
`struct hlist_nulls_head` stores `first`; `struct hlist_nulls_node` stores `next` and `pprev`. `NULLS_MARKER(value)` encodes an odd-valued terminal pointer. APIs include `INIT_HLIST_NULLS_HEAD`, `HLIST_NULLS_HEAD_INIT`, `is_a_nulls`, `get_nulls_value`, `hlist_nulls_unhashed`, `hlist_nulls_unhashed_lockless`, `hlist_nulls_empty`, `hlist_nulls_add_head`, `hlist_nulls_del`, and traversal macros.

## Control Flow
Insertion replaces the head first pointer and links the node ahead of the old first pointer, which may be a nulls marker. Traversal stops when `is_a_nulls()` detects the marker and can verify the marker value. Deletion updates predecessor storage and poisons the node.

## State and Persistence Behavior
State lives in caller-owned nodes and marker values. The marker is not a real object pointer and must be recognized before container conversion. There is no persistent state.

## Dependencies and Integration Points
It depends on `poison.h`, `const.h`, and external synchronization/RCU patterns in callers. Networking and hash-table users rely on the nulls value to detect concurrent hash bucket changes.

## Risks and Test Signals
Risks include treating a marker as a node, using the wrong nulls value, and assuming traversal is safe without the caller's required RCU/locking rules. Test signals are lookup retry coverage, debug poisoning failures, KCSAN/KASAN reports, and hash-table stress under concurrent insert/delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_nulls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_private.h -->
# sources/distributed-fs/ceph-client/include/linux/list_private.h

## Purpose
This header supplies list traversal/container helpers for structures with private `struct list_head` members. It avoids direct field access in macro expansions by computing the member offset and doing pointer arithmetic.

## Important APIs, Types, and Functions
The API mirrors common `list.h` typed helpers with `list_private_` prefixes: `list_private_entry`, first/last entry helpers, next/previous helpers, circular helpers, `list_private_entry_is_head`, forward/reverse iterators, continue/from variants, safe variants, and `list_private_safe_reset_next`. `__list_private_offset()` derives the member offset.

## Control Flow
Macros convert between list nodes and containing objects, then use the underlying `list_head` links for traversal. Safe variants cache the next object before caller code can delete the current object.

## State and Persistence Behavior
No state is owned here. The caller owns list heads and embedded nodes, and the same mutation and locking rules as `list.h` apply.

## Dependencies and Integration Points
It depends on `linux/compiler.h` and `linux/list.h`. It is useful for code that wants typed iteration over private list members while keeping the member name unavailable to ordinary direct users.

## Risks and Test Signals
Risks include giving the wrong type/member pair, using unsafe iterators while deleting, and assuming the privacy wrapper changes locking semantics. Build errors around private members, debug-list reports, and iterator tests over add/delete paths are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_sort.h -->
# sources/distributed-fs/ceph-client/include/linux/list_sort.h

## Purpose
This header declares the kernel linked-list sort helper. It lets callers sort an intrusive `struct list_head` list using a caller-provided comparison function.

## Important APIs, Types, and Functions
`list_cmp_func_t` is a nonnull comparator taking private context plus two list entries. `list_sort(void *priv, struct list_head *head, list_cmp_func_t cmp)` sorts the list in place.

## Control Flow
The implementation is external. The declared control contract is that `list_sort` walks and relinks list entries according to the comparator result while preserving the caller's embedded nodes.

## State and Persistence Behavior
The header owns no state. Sorting mutates only caller-owned list links at runtime and does not allocate or persist metadata through this declaration.

## Dependencies and Integration Points
It depends on `linux/types.h` and forward-declares `struct list_head`. Consumers include subsystems that need deterministic ordering without copying list contents into arrays.

## Risks and Test Signals
Risks are invalid comparators, sorting a concurrently modified list, and passing corrupt or uninitialized list heads. Test signals are sorted-order assertions, duplicate-key stability expectations documented by the implementation, debug-list checks, and lockdep coverage of caller serialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/list_sort.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/litex.h -->
# sources/distributed-fs/ceph-client/include/linux/litex.h

## Purpose
This header provides LiteX CSR access helpers. LiteX exposes many registers as arrays of 8-bit subregisters, so these helpers assemble and split 8, 16, 32, and 64-bit values over byte-wide MMIO locations.

## Important APIs, Types, and Functions
Internal helpers `_write_litex_subregister()` and `_read_litex_subregister()` operate on one byte-wide register slot using `writeb`/`readb`. Public helpers `litex_write8`, `litex_write16`, `litex_write32`, `litex_write64`, `litex_read8`, `litex_read16`, `litex_read32`, and `litex_read64` provide typed CSR access.

## Control Flow
Write helpers decompose the value into big-endian byte lanes and write successive subregisters. Read helpers read successive subregisters and reconstruct the value by shifting and ORing.

## State and Persistence Behavior
State is external hardware register state. The helpers do not cache values or persist data; ordering and visibility follow MMIO access semantics from `linux/io.h`.

## Dependencies and Integration Points
It depends on `linux/io.h` and integrates with LiteX platform drivers for FPGA-generated SoCs, soft peripherals, and SoC controller blocks.

## Risks and Test Signals
Risks include using the helpers on non-LiteX register layouts, wrong register width, endianness mismatch, and missing barriers around higher-level protocols. Test signals are CSR readback tests, hardware smoke tests, and bus fault or timeout diagnostics from LiteX peripherals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/litex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/livepatch.h -->
# sources/distributed-fs/ceph-client/include/linux/livepatch.h

## Purpose
This header defines the core kernel livepatch API and data model. It describes patch modules, target objects, replacement functions, system state records, transition states, shadow variables, and module loader hooks.

## Important APIs, Types, and Functions
Key structures are `struct klp_func`, `struct klp_object`, `struct klp_state`, and `struct klp_patch`. Iteration helpers walk static arrays and dynamic lists. APIs include `klp_enable_patch`, `klp_module_coming`, `klp_module_going`, `klp_find_section_by_name`, `klp_copy_process`, `klp_update_patch_state`, `klp_patch_pending`, `klp_have_reliable_stack`, `klp_shadow_get`, `klp_shadow_alloc`, `klp_shadow_get_or_alloc`, `klp_shadow_free`, `klp_get_state`, and `klp_apply_section_relocs`. Disabled livepatch builds provide no-op or false fallbacks.

## Control Flow
A patch module describes objects and functions. Enabling resolves old symbols, applies relocations, stacks ftrace redirections, and moves tasks through patched/unpatched transition states. Module coming/going hooks attach or detach object-specific patches as target modules load or unload.

## State and Persistence Behavior
State is runtime only: global patch lists, object/function patched flags, task `TIF_PATCH_PENDING`, kobjects, completion for cleanup, and shadow variable tables. Patch state does not persist across reboot.

## Dependencies and Integration Points
It depends on modules, ftrace, completions, lists, external livepatch metadata, scheduler transition hooks, reliable stacktrace support, and ELF relocation data.

## Risks and Test Signals
Risks include ambiguous old symbols, unreliable stack transitions, broken relocation sections, module lifetime races, incorrect replace semantics, and leaked shadow data. Test signals include livepatch selftests, sysfs patch state, task transition completion, ftrace redirection checks, module load/unload tests, and shadow allocation/free coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/livepatch.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/livepatch_external.h -->
# sources/distributed-fs/ceph-client/include/linux/livepatch_external.h

## Purpose
This header defines external livepatch metadata formats and callback naming conventions used by patch-generation tooling and livepatch modules.

## Important APIs, Types, and Functions
It exports section/name prefixes `KLP_RELOC_SEC_PREFIX`, `KLP_SYM_PREFIX`, and callback prefixes for pre/post patch and unpatch functions. Callback typedefs include `klp_pre_patch_t`, `klp_post_patch_t`, `klp_pre_unpatch_t`, and `klp_post_unpatch_t`. `struct klp_callbacks` groups optional callbacks. `struct klp_func_ext` and `struct klp_object_ext` provide compact generated descriptions consumed before conversion to core livepatch structures.

## Control Flow
Tooling emits metadata sections and callback pointers using these names. The livepatch loader later discovers sections, resolves compact external records, and invokes callbacks around object patch/unpatch operations.

## State and Persistence Behavior
The header itself owns no state. Metadata persists inside the livepatch module object file and is converted into runtime `klp_object`/`klp_func` state when loaded.

## Dependencies and Integration Points
It depends on basic types and forward-declared `struct klp_object`. It integrates with objtool/create-diff-object style tooling, module ELF sections, and `livepatch.h`.

## Risks and Test Signals
Risks include prefix mismatches, callback prototype mistakes, stale generated metadata, and callback failure semantics preventing later callbacks. Test signals are module section inspection, livepatch enable/disable tests, callback ordering tests, and symbol-resolution diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/livepatch_external.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/livepatch_helpers.h -->
# sources/distributed-fs/ceph-client/include/linux/livepatch_helpers.h

## Purpose
This header provides convenience macros for livepatch patch source files. It registers callbacks into discardable metadata sections, supplies object naming, adapts static calls, and helps define syscall replacements.

## Important APIs, Types, and Functions
`KLP_OBJNAME` resolves to the module build name or `vmlinux`. `KLP_PRE_PATCH_CALLBACK`, `KLP_POST_PATCH_CALLBACK`, `KLP_PRE_UNPATCH_CALLBACK`, and `KLP_POST_UNPATCH_CALLBACK` place callback pointers in `.discard.klp_callback_ptrs`. `KLP_STATIC_CALL(name)` converts a static call to an indirect call through the key. `KLP_SYSCALL_DEFINE1` through `KLP_SYSCALL_DEFINE6` wrap syscall replacement definitions, with x86-64-specific stubs.

## Control Flow
The macros expand at compile time into section entries and syscall wrapper functions. The livepatch loader later reads callback pointer sections. Syscall macros generate ABI entry stubs that cast, validate, protect, and call a patch-local implementation.

## State and Persistence Behavior
State is static module metadata and generated functions. There is no runtime storage owned by the header.

## Dependencies and Integration Points
It depends on syscall wrapper macros, livepatch core types, static-call definitions, module build names, and x86 syscall wrapper conventions.

## Risks and Test Signals
Risks include architecture-limited syscall support, wrong object name selection, using `KLP_STATIC_CALL` where direct static-call semantics are required, and callback pointer section mistakes. Test signals are successful patch module build, objtool metadata inspection, livepatch callback execution, and syscall ABI tests on patched syscalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/livepatch_helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/livepatch_sched.h -->
# sources/distributed-fs/ceph-client/include/linux/livepatch_sched.h

## Purpose
This header connects livepatch task transitions to scheduler activity. It lets the scheduler opportunistically switch a task's patch state when a static key is enabled.

## Important APIs, Types, and Functions
With `CONFIG_LIVEPATCH`, it declares `__klp_sched_try_switch()` and `DECLARE_STATIC_KEY_FALSE(klp_sched_try_switch_key)`. `klp_sched_try_switch(struct task_struct *curr)` checks the static key and the task state. Without livepatch it compiles to an empty inline.

## Control Flow
On scheduler paths, the inline checks `static_branch_unlikely()` and whether the current task has `TASK_FREEZABLE` state bits before calling the out-of-line transition helper.

## State and Persistence Behavior
State is runtime livepatch transition state and a static branch key. Nothing persists across boot.

## Dependencies and Integration Points
It depends on jump labels and scheduler task state. It integrates with livepatch consistency transitions and scheduler code that can safely observe current tasks.

## Risks and Test Signals
Risks include missed transition opportunities, excessive scheduler overhead if the static key is mishandled, and incorrect state filtering. Test signals are livepatch transition selftests, static-key enable/disable tracing, and confirmation that tasks converge out of `TIF_PATCH_PENDING`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/livepatch_sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/liveupdate.h -->
# sources/distributed-fs/ceph-client/include/linux/liveupdate.h

## Purpose
This header declares a live update orchestrator interface for preserving and restoring file-related kernel state across a kexec-style kernel transition. It defines file handlers and file-lifecycle-bound shared objects.

## Important APIs, Types, and Functions
`struct liveupdate_file_op_args` carries handler, file, serialized data, retrieve status, and private runtime data. `struct liveupdate_file_ops` defines `can_preserve`, `preserve`, `unpreserve`, `freeze`, `unfreeze`, `retrieve`, `can_finish`, `finish`, and `get_id`. `struct liveupdate_file_handler` registers compatible file types. FLB support uses `struct liveupdate_flb_op_args`, `struct liveupdate_flb_ops`, `struct luo_flb_private_state`, `struct luo_flb_private`, and `struct liveupdate_flb`. Public APIs include `liveupdate_enabled`, `liveupdate_reboot`, registration calls, and `liveupdate_flb_get_incoming/outgoing`; disabled builds return false, zero, or `-EOPNOTSUPP`.

## Control Flow
Outgoing kernels preserve file state, optionally freeze it before transition, and serialize opaque handles. Incoming kernels retrieve file objects, wait until `can_finish` permits completion, then call `finish`. FLBs run preserve/retrieve/finish once for shared data when first/last dependent files cross lifecycle boundaries.

## State and Persistence Behavior
State includes handler lists, FLB lists, per-FLB incoming/outgoing counts, serialized `u64` handles, live object pointers, locks, and finished/retrieved flags. Persisted cross-kernel state is represented by serialized handles in LUO/KHO data, not by the C structures themselves.

## Dependencies and Integration Points
It depends on KHO LUO ABI headers, UAPI liveupdate definitions, files, modules, lists, mutexes, and rwsems. It integrates with kexec/live-update orchestration and drivers that can preserve file-backed resources such as memfd, VFIO, or shared subsystem objects.

## Risks and Test Signals
Risks include handler compatibility drift, leaked private data on abort, FLB refcount bugs, retrieve/finish ordering errors, module lifetime issues, and invalid serialized handles. Test signals are enabled/disabled config behavior, preserve-abort-unpreserve tests, preserve-reboot-retrieve-finish tests, FLB first/last user tests, and fault injection in each callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/liveupdate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/llc.h -->
# sources/distributed-fs/ceph-client/include/linux/llc.h

## Purpose
This small header exposes LLC socket option constants for kernel users. It names option IDs used with IEEE 802.2 LLC configuration.

## Important APIs, Types, and Functions
The API is macro-only, defining option identifiers such as `LLC_OPT_RETRY`, `LLC_OPT_SIZE`, `LLC_OPT_ACK_TMR_EXP`, `LLC_OPT_P_TMR_EXP`, `LLC_OPT_REJ_TMR_EXP`, and `LLC_OPT_BUSY_TMR_EXP`.

## Control Flow
There is no executable control flow. Socket option dispatch code interprets these constants when users or protocol code configure LLC behavior.

## State and Persistence Behavior
No state is stored here. Socket state lives in LLC protocol structures configured through these option IDs.

## Dependencies and Integration Points
It integrates with LLC networking code, socket option handlers, and any UAPI-adjacent code that needs the same numeric option contract.

## Risks and Test Signals
Risks are ABI mismatch and misinterpreting timer/retry option numbers. Test signals are LLC socket option tests, protocol conformance tests, and packet-level validation of retry/timer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/llc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/llist.h -->
# sources/distributed-fs/ceph-client/include/linux/llist.h

## Purpose
This header implements lockless NULL-terminated singly linked lists for multiple-producer/single-consumer and batch-drain patterns. It is intended for low-overhead enqueue and delete-all workflows.

## Important APIs, Types, and Functions
`struct llist_head` stores the first node; `struct llist_node` stores `next`. APIs include `LLIST_HEAD_INIT`, `LLIST_HEAD`, `init_llist_head`, `init_llist_node`, `llist_on_list`, `llist_entry`, traversal macros for deleted lists, `llist_empty`, `llist_next`, `llist_add_batch`, `__llist_add_batch`, `llist_add`, `llist_del_all`, `__llist_del_all`, `llist_del_first`, `llist_del_first_init`, `llist_del_first_this`, and `llist_reverse_order`.

## Control Flow
Producers push nodes with cmpxchg on `head->first`; batch add links the batch tail to the observed first pointer until the exchange succeeds. `llist_del_all` atomically swaps the head to NULL and returns a newest-to-oldest chain. Single-item delete uses external implementation and has stricter consumer concurrency rules.

## State and Persistence Behavior
State is volatile list links in caller-owned nodes. `init_llist_node` uses a self pointer to mark a node as off-list. The API has no persistence and generally permits traversal only after nodes have been removed from the live list.

## Dependencies and Integration Points
It depends on atomics, `try_cmpxchg`, `xchg`, `container_of`, and `WRITE_ONCE`/`READ_ONCE`. It integrates with work queues, deferred frees, and fast producer paths.

## Risks and Test Signals
Risks include multiple consumers using `llist_del_first` without locks, traversing live lists, ABA-like sequences described in the header, and NMI use on architectures lacking NMI-safe cmpxchg. Test signals are producer/consumer stress tests, KCSAN, architecture config checks, and order validation after `llist_reverse_order`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/llist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/llist_api.h -->
# sources/distributed-fs/ceph-client/include/linux/llist_api.h

## Purpose
This compatibility header includes the kernel lockless list API under an alternate name. Its entire content is an include of `linux/llist.h`.

## Important APIs, Types, and Functions
It re-exports all declarations and macros from `llist.h`, including `struct llist_head`, `struct llist_node`, `llist_add`, `llist_del_all`, and traversal helpers.

## Control Flow
There is no independent control flow. The preprocessor redirects users to `llist.h`.

## State and Persistence Behavior
No state is declared here. Runtime behavior is exactly the state behavior of `llist.h`.

## Dependencies and Integration Points
Its only dependency and integration point is `linux/llist.h`. It likely exists for source compatibility with code that includes the `_api` name.

## Risks and Test Signals
Risks are limited to include-order or stale compatibility assumptions. Test signals are build coverage for users of this header and the same concurrency tests used for `llist.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/llist_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/local_lock.h -->
# sources/distributed-fs/ceph-client/include/linux/local_lock.h

## Purpose
This header exposes per-CPU local lock APIs. It gives callers a uniform way to protect CPU-local data across non-RT and PREEMPT_RT kernels while preserving lockdep annotations.

## Important APIs, Types, and Functions
Macros include `local_lock_init`, `local_lock`, `local_lock_irq`, `local_lock_irqsave`, `local_unlock`, `local_unlock_irq`, `local_unlock_irqrestore`, `local_trylock_init`, `local_trylock`, `local_trylock_irqsave`, `local_lock_is_locked`, `local_lock_nested_bh`, and `local_unlock_nested_bh`. It also declares lock-guard helper classes for scoped cleanup.

## Control Flow
Public macros map a per-CPU base lock to the current CPU instance with `__this_cpu_local_lock()`, then call implementation macros from `local_lock_internal.h`. IRQ variants save or modify interrupt state as appropriate.

## State and Persistence Behavior
State is per-CPU lock instances supplied by callers. No state persists beyond runtime; ownership and acquired state are implementation-dependent.

## Dependencies and Integration Points
It depends on `local_lock_internal.h`, lock guard infrastructure, per-CPU variables, IRQ state handling, and lockdep. It integrates with code that must remain correct under PREEMPT_RT semantics.

## Risks and Test Signals
Risks include using a local lock for cross-CPU protection, passing non-per-CPU storage to per-CPU macros, and assuming IRQ disabling on RT where semantics differ. Test signals are PREEMPT_RT builds, lockdep assertions, IRQ/preemption context tests, and scoped guard compile coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/local_lock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/local_lock_internal.h -->
# sources/distributed-fs/ceph-client/include/linux/local_lock_internal.h

## Purpose
This internal header implements `local_lock.h` for both normal and PREEMPT_RT kernels. It is deliberately not included directly and carries the low-level preemption, migration, IRQ, lockdep, and trylock behavior.

## Important APIs, Types, and Functions
On non-RT kernels it defines `local_lock_t` and `local_trylock_t` context lock structures with optional `lockdep_map`, owner, and acquired state. Internal macros include `INIT_LOCAL_LOCK`, `__local_lock_init`, `__local_lock`, IRQ variants, trylock variants, release variants, nested-BH helpers, and `__local_lock_is_locked`. On PREEMPT_RT, both lock types map to `spinlock_t`, using `migrate_disable()` plus spin locking.

## Control Flow
Non-RT acquisition disables preemption or IRQs and records lockdep ownership; trylock checks an acquired byte and may fail without blocking. Release clears owner/acquired state then reenables preemption or IRQs. RT acquisition disables migration and takes a per-CPU spinlock, leaving the section preemptible.

## State and Persistence Behavior
Runtime state is per-CPU lock contents, owner tracking, lockdep maps, and trylock acquired bytes or RT spinlock state. No persistence exists.

## Dependencies and Integration Points
It depends on per-CPU definitions, irqflags, lockdep, debug locks, current task, scheduler state, and spinlocks under RT. `local_lock.h` is the public integration point.

## Risks and Test Signals
Risks include direct inclusion, incorrect assumptions about preemption/IRQ state across RT and non-RT, trylock use from NMI/hardirq on RT, and misuse of `local_lock_is_locked` without disabled migration/preemption. Test signals are lockdep owner warnings, PREEMPT_RT test boots, context tracking assertions, and trylock failure-path coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/local_lock_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockd/bind.h -->
# sources/distributed-fs/ceph-client/include/linux/lockd/bind.h

## Purpose
This header defines the binding contract between the kernel lock manager service (`lockd`) and filesystem clients/servers such as NFS. It centralizes lockd lifecycle and callback entry points.

## Important APIs, Types, and Functions
The file declares lockd-facing structures and operations for starting/stopping lockd, binding protocol operations, and notifying or recovering file locks. It includes service-related prototypes and callback hooks used by NFS lock management code.

## Control Flow
Callers bind lockd support, request lockd startup when network file locking is needed, and release it when no longer required. Lock recovery and grace-period callbacks flow through the declared operation hooks.

## State and Persistence Behavior
The header owns no state. Runtime state is held by lockd, NFS client/server structures, network namespaces, and file-lock tables. Persistent behavior is external, for example recovery after server reboot.

## Dependencies and Integration Points
It integrates with `fs/lockd`, NFS, `struct file_lock`, network namespaces, RPC services, and kernel lock manager recovery code.

## Risks and Test Signals
Risks include lockd lifetime imbalance, missed recovery notifications, namespace leaks, and mismatched callback versions. Test signals are NFS lock/unlock tests, lockd module unload/load, server reboot grace-period tests, and rpcdebug traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockd/bind.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockdep.h -->
# sources/distributed-fs/ceph-client/include/linux/lockdep.h

## Purpose
This header declares the runtime locking correctness validator API. It lets lock primitives register classes, report acquire/release events, assert contexts, collect lock statistics, and compile to low-overhead stubs when lockdep is disabled.

## Important APIs, Types, and Functions
It defines lock dependency graph records such as `struct lock_list` and `struct lock_chain`, and APIs including `lockdep_init`, `lockdep_reset`, `lockdep_free_key_range`, `lockdep_register_key`, `lockdep_init_map_type`, `lockdep_set_class*`, `lock_acquire`, `lock_release`, `lock_sync`, `lock_is_held_type`, `lock_pin_lock`, `lock_repin_lock`, `lock_unpin_lock`, and lock-stat hooks. Macros map spinlock, rwlock, mutex, rwsem, seqcount, and generic lock-map events to these primitives.

## Control Flow
Lock initialization maps an instance to a key/class/subclass. On acquire, lockdep records a held-lock stack entry, updates dependency chains, and validates ordering. Release removes the held entry. Assertion macros query current task lock state or IRQ/preemption tracking. Disabled builds replace most operations with stubs and assumptions for static analysis.

## State and Persistence Behavior
Runtime state includes per-task recursion/depth fields, lock classes, dependency graph edges, chain caches, held locks, pin cookies, and optional timing statistics. It is diagnostic state only and does not persist across boot.

## Dependencies and Integration Points
It depends on `lockdep_types.h`, SMP/per-CPU data, debug locks, stack traces, interrupt state tracking, and all lock primitive implementations that embed `dep_map`.

## Risks and Test Signals
Risks include unregistered dynamic keys, false class sharing, missing acquire/release annotations, recursion disabling left on, and different semantics between enabled and disabled configs. Test signals are `CONFIG_PROVE_LOCKING`, lockdep splats, lock-stat data, selftests, IRQ/preemption assertion failures, and absence of false positives after correct subclassing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockdep_api.h -->
# sources/distributed-fs/ceph-client/include/linux/lockdep_api.h

## Purpose
This compatibility header re-exports the lockdep API by including `linux/lockdep.h`.

## Important APIs, Types, and Functions
All APIs come from `lockdep.h`, including lock class keys, lockdep maps, acquire/release annotations, assertions, and disabled-config stubs.

## Control Flow
There is no independent control flow. Include processing redirects users to the main lockdep header.

## State and Persistence Behavior
No state is declared here; runtime state is the lockdep state declared and implemented through `lockdep.h` and related files.

## Dependencies and Integration Points
Its only dependency is `linux/lockdep.h`. It supports users that include the historical or narrower API name.

## Risks and Test Signals
Risks are limited to duplicate include expectations and stale compatibility includes. Build coverage and lockdep tests for the underlying API are sufficient signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockdep_api.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockdep_types.h -->
# sources/distributed-fs/ceph-client/include/linux/lockdep_types.h

## Purpose
This header defines the core data types used by lockdep. It separates structural definitions from the larger lockdep API so lock primitives can embed maps and keys without pulling in all lockdep functions.

## Important APIs, Types, and Functions
It defines `enum lockdep_wait_type`, `enum lockdep_lock_type`, `struct lockdep_subclass_key`, `struct lock_class_key`, `struct lock_class`, `struct lock_time`, `struct lock_class_stats`, `struct lockdep_map`, `struct pin_cookie`, and `struct held_lock` when lockdep is enabled. Disabled builds define empty `lock_class_key`, `lockdep_map`, and `pin_cookie`. Constants include `MAX_LOCKDEP_SUBCLASSES`, `LOCK_TRACE_STATES`, `NR_LOCKDEP_CACHING_CLASSES`, `MAX_LOCKDEP_KEYS`, and `INITIAL_CHAIN_KEY`.

## Control Flow
There is no runtime control flow in the header. The fields support lockdep's graph building, class caching, held-lock stack accounting, IRQ context separation, and lock-stat timing.

## State and Persistence Behavior
The types carry runtime diagnostic state in lock instances, class tables, and task held-lock stacks. They do not persist. Disabled builds intentionally erase most storage footprint.

## Dependencies and Integration Points
It depends on `linux/types.h`. It is embedded by spinlocks, mutexes, rwsems, local locks, wait override maps, and lockdep internals.

## Risks and Test Signals
Risks include ABI/layout-sensitive changes, exhausting key/class bit limits, incorrect wait-type classification, and assuming fields exist under `!CONFIG_LOCKDEP`. Test signals are allmodconfig builds, lockdep selftests, lock-stat builds, and compile coverage for disabled lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockdep_types.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockref.h -->
# sources/distributed-fs/ceph-client/include/linux/lockref.h

## Purpose
This header defines `struct lockref`, a combined spinlock and reference count optimized for objects that frequently need atomic refcount updates with fallback locking.

## Important APIs, Types, and Functions
`struct lockref` contains a `union` of `aligned_u64 lock_count` for cmpxchg-capable platforms and a struct with `spinlock_t lock` plus `int count`. APIs include `lockref_init`, `lockref_get`, `lockref_put_return`, `lockref_get_not_zero`, `lockref_put_or_lock`, `lockref_mark_dead`, `lockref_get_not_dead`, and `__lockref_is_dead`.

## Control Flow
Fast paths may use cmpxchg on the combined lock/count word when alignment and architecture support allow it. Slow paths take the embedded spinlock to update count or hold the object while final put processing runs.

## State and Persistence Behavior
State is the object's embedded lock and reference count. A negative count marks a dead object. No persistence exists beyond object lifetime.

## Dependencies and Integration Points
It depends on spinlocks and generated bounds for alignment/size checks. It integrates with dcache and other reference-counted kernel objects that need lock-coupled lifetime transitions.

## Risks and Test Signals
Risks include count underflow, resurrecting dead objects, alignment assumptions for cmpxchg, and missed locking around object teardown. Test signals are refcount stress, lockdep on fallback locks, dcache lifetime tests, and KASAN/UAF detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lockref.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/log2.h -->
# sources/distributed-fs/ceph-client/include/linux/log2.h

## Purpose
This header provides integer base-2 logarithm, power-of-two rounding, bit-width, and related helpers for kernel code. It supports both compile-time constant folding and runtime builtins.

## Important APIs, Types, and Functions
Functions/macros include `__ilog2_u32`, `__ilog2_u64`, `is_power_of_2`, `__roundup_pow_of_two`, `__rounddown_pow_of_two`, `const_ilog2`, `ilog2`, `roundup_pow_of_two`, `rounddown_pow_of_two`, `__order_base_2`, `order_base_2`, `__bits_per`, `bits_per`, and `max_pow_of_two_factor`.

## Control Flow
Constant macros use compile-time conditional expressions to produce folded results. Runtime helpers use bit operations such as leading-zero count and shifts. Rounding helpers convert a value to the next or previous power of two.

## State and Persistence Behavior
There is no state. Results are pure functions of integer inputs.

## Dependencies and Integration Points
It depends on `linux/types.h` and `linux/bitops.h`. Callers include allocators, block code, bitmaps, hash tables, and protocol sizing logic.

## Risks and Test Signals
Risks include undefined or special behavior for zero, overflow when rounding large values, signed/unsigned surprises, and misuse where exact powers are required. Test signals are compile-time assertions, boundary tests around 0/1/max values, and sanitizer coverage for shifts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/log2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/logic_iomem.h -->
# sources/distributed-fs/ceph-client/include/linux/logic_iomem.h

## Purpose
This header declares logical I/O memory region support, allowing virtualized or indirect MMIO providers to register operations behind resource ranges.

## Important APIs, Types, and Functions
`struct logic_iomem_ops` describes byte/word/long/qword read/write callbacks and copy/set style operations. `struct logic_iomem_region_ops` associates operations with a region. `logic_iomem_add_region()` registers a resource-backed logical region with the framework.

## Control Flow
Provider drivers register a resource and callbacks. Later I/O memory access paths can dispatch accesses that fall in the logical region to the provider operations rather than ordinary direct MMIO.

## State and Persistence Behavior
The header declares no storage. Runtime state is registered region metadata and provider-owned backing state. No persistence is implied.

## Dependencies and Integration Points
It depends on `linux/types.h` and `linux/ioport.h`. It integrates with resource management, logical MMIO providers, and architecture I/O access hooks.

## Risks and Test Signals
Risks include overlapping resources, incomplete operation tables, width/endianness mistakes, and lifetime bugs if a provider unregisters while mappings remain. Test signals are region registration tests, MMIO read/write emulation tests, resource conflict diagnostics, and driver remove stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/logic_iomem.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/logic_pio.h -->
# sources/distributed-fs/ceph-client/include/linux/logic_pio.h

## Purpose
This header provides logical PIO support for platforms where I/O port space is translated through host bridge ranges or indirect operations rather than native x86-style ports.

## Important APIs, Types, and Functions
It defines range flags, `struct logic_pio_hwaddr`, `struct logic_pio_host_ops`, `logic_inb/inw/inl`, `logic_outb/outw/outl`, string I/O helpers, and optional macro aliases from `inb`/`outb` to logical functions. Registration APIs include `find_io_range_by_fwnode`, `logic_pio_trans_hwaddr`, `logic_pio_register_range`, `logic_pio_unregister_range`, and `logic_pio_trans_cpuaddr`.

## Control Flow
Host bridges register PIO ranges. Accessors translate a logical port address to either an MMIO-backed range or indirect host operation, then perform the read/write or string transfer. Address translation can use firmware nodes or raw hardware addresses.

## State and Persistence Behavior
Runtime state is the registered range list and provider operations. No data persists; registrations are tied to host bridge lifetime.

## Dependencies and Integration Points
It depends on firmware nodes and architecture `IO_SPACE_LIMIT`. It integrates with PCI host bridges, ACPI/DT-described I/O windows, and generic port I/O users.

## Risks and Test Signals
Risks include range overlap, wrong translation offsets, indirect-vs-MMIO type mismatches, and unexpected macro aliasing on architectures. Test signals are PCI I/O BAR tests, firmware range parsing, port access smoke tests, and unregister/remove stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/logic_pio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lp.h -->
# sources/distributed-fs/ceph-client/include/linux/lp.h

## Purpose
This header defines internal structures and constants for the parallel printer (`lp`) driver. It bridges UAPI printer settings with kernel parport device state.

## Important APIs, Types, and Functions
Macros address `lp_table` fields, define special parport selection values, buffer size, control bits, dummy data, and delay constants. `struct lp_stats` tracks chars, sleeps, maxrun, and wakeups. `struct lp_struct` holds flags, timing, wait queues, mutex, parport device pointer, device number, buffer, and stats.

## Control Flow
The implementation uses these fields to serialize writes, wait for printer readiness, strobe data through parport control bits, and collect statistics.

## State and Persistence Behavior
State is per-minor runtime driver state in `lp_table` entries and optional stats. Printer hardware state is external. No persistence exists beyond module/device lifetime.

## Dependencies and Integration Points
It depends on wait queues, mutexes, and `uapi/linux/lp.h`. It integrates with the parport core and character device operations for `/dev/lp*`.

## Risks and Test Signals
Risks include timing-sensitive printer handshakes, stale parport pointers, buffer lifetime issues, and flag races. Test signals are parport printer writes, ioctl compatibility, wait/timeout behavior, stats inspection, and module unload while devices are idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lru_cache.h -->
# sources/distributed-fs/ceph-client/include/linux/lru_cache.h

## Purpose
This header declares the DRBD-originated LRU cache framework for tracking a bounded active set of labeled objects and pending label changes. It is designed for activity logs and persistent write-intent style metadata.

## Important APIs, Types, and Functions
`struct lc_element` contains hash collision linkage, list membership, refcount, index, current label, and pending new label. `struct lru_cache` holds `lru`, `free`, `in_use`, and `to_be_changed` lists, a kmem cache, element metadata, hash slots, element array, stats, flags, and pending-change limits. APIs include `lc_create`, `lc_reset`, `lc_destroy`, `lc_del`, `lc_get_cumulative`, `lc_try_get`, `lc_find`, `lc_get`, `lc_put`, `lc_committed`, `lc_seq_printf_stats`, `lc_seq_dump_details`, `lc_try_lock_for_transaction`, `lc_try_lock`, `lc_unlock`, `lc_is_used`, and `lc_element_by_index`.

## Control Flow
Lookups map labels to elements through hash slots. `lc_get` may hit an active element, reuse an LRU/free element, or mark pending changes for transaction commit. `lc_put` drops references and moves unused elements toward LRU. Transaction locks stop active-set changes while metadata is committed.

## State and Persistence Behavior
Runtime state tracks active labels, refcounts, LRU order, free entries, dirty/locked/starving flags, and pending changes. The cache itself does not write persistence, but its pending-change model exists so callers can persist activity-log transactions.

## Dependencies and Integration Points
It depends on lists, slab caches, bit operations, strings, and seq files. Integration is with DRBD-like replication metadata, resync tracking, and diagnostic seq output.

## Risks and Test Signals
Risks include missing external serialization, transaction lock misuse, starvation when the active set is too small, lost pending changes, and incorrect label/index persistence by callers. Test signals include DRBD activity-log tests, crash-recovery simulations, seq stats, starvation counters, and lock/dirty flag assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lru_cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm/apparmor.h -->
# sources/distributed-fs/ceph-client/include/linux/lsm/apparmor.h

## Purpose
This header defines the AppArmor-specific portion of the generic `struct lsm_prop` property model.

## Important APIs, Types, and Functions
It forward-declares `struct aa_label` and defines `struct lsm_prop_apparmor` with an AppArmor label pointer.

## Control Flow
There is no control flow. LSM property producers fill this field and consumers inspect it through generic LSM property plumbing.

## State and Persistence Behavior
The structure stores a runtime pointer to an AppArmor label; label lifetime is managed by AppArmor, not this header.

## Dependencies and Integration Points
It integrates with the LSM property aggregation code and AppArmor's label implementation.

## Risks and Test Signals
Risks include stale label pointers and missing initialization when AppArmor is disabled or absent. Test signals are AppArmor label propagation tests and build coverage with different LSM configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm/apparmor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm/bpf.h -->
# sources/distributed-fs/ceph-client/include/linux/lsm/bpf.h

## Purpose
This header defines BPF LSM-specific property storage for the generic LSM property container.

## Important APIs, Types, and Functions
`struct lsm_prop_bpf` carries a BPF LSM identifier field, using Linux integer types.

## Control Flow
There is no executable flow. Security code fills and reads the field through `struct lsm_prop`.

## State and Persistence Behavior
The field is runtime security metadata. It is not persisted by this header.

## Dependencies and Integration Points
It depends on `linux/types.h` and integrates with BPF LSM hooks and generic LSM property aggregation.

## Risks and Test Signals
Risks include uninitialized identifiers or inconsistent interpretation across LSM stacking. Test signals are BPF LSM selftests and LSM property conversion coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm/bpf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm/selinux.h -->
# sources/distributed-fs/ceph-client/include/linux/lsm/selinux.h

## Purpose
This header defines the SELinux-specific property payload used by the generic LSM property model.

## Important APIs, Types, and Functions
`struct lsm_prop_selinux` contains SELinux security identifiers, typically subject/object SID-style values represented with fixed-width types.

## Control Flow
There is no control flow. SELinux fills these properties and generic LSM helpers consume them for audit, context conversion, or object labeling.

## State and Persistence Behavior
The structure stores runtime security IDs. Actual label policy state and persistence are managed by SELinux policy and object xattrs, not the header.

## Dependencies and Integration Points
It depends on `linux/types.h` and integrates with SELinux, generic LSM properties, audit, and security context conversion hooks.

## Risks and Test Signals
Risks include SID mismatch, zero/uninitialized IDs, and stacking bugs when multiple LSMs provide properties. Test signals are SELinux policy tests, audit context output, and secctx conversion selftests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm/selinux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm/smack.h -->
# sources/distributed-fs/ceph-client/include/linux/lsm/smack.h

## Purpose
This header defines the Smack-specific security property payload used by the generic LSM property container.

## Important APIs, Types, and Functions
It forward-declares `struct smack_known` and defines `struct lsm_prop_smack` with a pointer to a Smack label object.

## Control Flow
There is no executable flow. Smack property producers store a label pointer, and generic LSM property consumers can carry it alongside other LSM metadata.

## State and Persistence Behavior
The header stores no independent state. The pointer references runtime Smack label state managed by Smack.

## Dependencies and Integration Points
It integrates with Smack and generic LSM property stacking code.

## Risks and Test Signals
Risks include stale label pointers, missing initialization, and stacking conversion mistakes. Test signals are Smack access tests, audit label output, and multi-LSM property tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm/smack.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm_audit.h -->
# sources/distributed-fs/ceph-client/include/linux/lsm_audit.h

## Purpose
This header declares common LSM audit data structures and helpers. It standardizes how security modules pass object, network, IPC, key, inode, file, and other context into audit logging.

## Important APIs, Types, and Functions
It defines `struct lsm_network_audit`, `struct lsm_ioctlop_audit`, InfiniBand audit structures, and `struct common_audit_data` with a type discriminator plus union-like fields for paths, dentries, inodes, tasks, keys, files, capabilities, lockdown, notifications, and netlink types. APIs include `ipv4_skb_to_auditdata`, `ipv6_skb_to_auditdata`, `common_lsm_audit`, and `audit_log_lsm_data`, with no-op stubs when auditing is not enabled.

## Control Flow
Security modules populate `common_audit_data`, optionally extract packet addresses, then call common audit helpers to format fields into audit buffers. Disabled configs compile calls away.

## State and Persistence Behavior
The structures are per-event transient data. Persistent audit records are produced by the audit subsystem, not by this header.

## Dependencies and Integration Points
It depends on audit, paths, keys, sk_buffs, IPv6, spinlocks, RDMA verbs, and security modules. It integrates with SELinux, Smack, AppArmor, lockdown, key, network, and filesystem hooks.

## Risks and Test Signals
Risks include wrong discriminator values, uninitialized union fields, leaking sensitive data, and audit records missing network or object context. Test signals are audit log assertions, LSM denial tests, IPv4/IPv6 packet audit coverage, and build coverage with `CONFIG_AUDIT` off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm_audit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm_count.h -->
# sources/distributed-fs/ceph-client/include/linux/lsm_count.h

## Purpose
This header computes the maximum number of enabled Linux Security Modules at compile time. The result sizes static-call tables and other LSM stacking arrays.

## Important APIs, Types, and Functions
It defines per-LSM enabled-list macros for capabilities, SELinux, Smack, AppArmor, TOMOYO, Yama, LoadPin, Lockdown, SafeSetID, BPF LSM, Landlock, IMA, EVM, and IPE. `COUNT_LSMS()` uses variadic argument counting from `linux/args.h`, and `MAX_LSM_COUNT` expands to the computed count when security is enabled, otherwise zero.

## Control Flow
There is no runtime flow. Preprocessor conditionals include one marker per configured LSM, and macro argument counting produces a compile-time integer.

## State and Persistence Behavior
No state exists. The count affects compiled object sizes and static-call table layout.

## Dependencies and Integration Points
It depends on Kconfig symbols and `linux/args.h`. It integrates with `lsm_hooks.h` static-call table definitions.

## Risks and Test Signals
Risks include forgetting to add a new LSM, over- or under-sizing static-call arrays, and disabled-security build regressions. Test signals are all LSM Kconfig matrix builds, static assertions around table sizes, and boot logs showing expected enabled LSMs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm_count.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm_hook_defs.h -->
# sources/distributed-fs/ceph-client/include/linux/lsm_hook_defs.h

## Purpose
This header is the authoritative X-macro list of LSM hooks. It is included with different `LSM_HOOK` definitions to generate hook function pointer unions, static-call tables, dispatch code, and defaults.

## Important APIs, Types, and Functions
Each `LSM_HOOK(return_type, default, name, args...)` entry defines one security hook. The file covers filesystem, path, inode, file, task, credentials, IPC, key, network, XFRM, BPF, audit, io_uring, perf, lockdown, notification, block-device, and initramfs hooks. Defaults encode allow, deny, unsupported, or void behavior.

## Control Flow
There is no direct control flow. Generated callers use this list to invoke registered LSM callbacks in stacking order, applying the per-hook default when no module handles a hook or when a hook family is disabled.

## State and Persistence Behavior
The header owns no state. It shapes generated runtime hook lists and static-call slots in the security framework.

## Dependencies and Integration Points
It is included by `lsm_hooks.h` and security implementation files with a caller-defined `LSM_HOOK` macro. It depends on many forward-declared kernel types being visible at include sites.

## Risks and Test Signals
Risks include prototype drift, wrong default return values, missing conditional guards for optional subsystems, and breaking all generated users of a hook. Test signals are full security Kconfig builds, LSM selftests, hook registration tests, and behavior checks for unsupported/default hook paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm_hook_defs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm_hooks.h -->
# sources/distributed-fs/ceph-client/include/linux/lsm_hooks.h

## Purpose
This header defines the LSM hook registration framework. It turns `lsm_hook_defs.h` into typed function-pointer storage, static-call tables, hook descriptors, blob size declarations, and LSM registration records.

## Important APIs, Types, and Functions
`union security_list_options` contains a function pointer for every LSM hook. `struct lsm_static_call`, `struct lsm_static_calls_table`, `struct lsm_id`, `struct security_hook_list`, `struct lsm_blob_sizes`, and `struct lsm_info` are central types. `LSM_HOOK_INIT` initializes hook descriptors. `security_add_hooks` registers callbacks. `DEFINE_LSM` and `DEFINE_EARLY_LSM` place LSM descriptors in init sections. `lsm_get_xattr_slot` allocates xattr output slots.

## Control Flow
An LSM defines `struct security_hook_list` entries and a `struct lsm_info`. During boot, the framework orders LSMs, allocates blob offsets, registers hooks, and fills static-call tables from last to first so dispatch can jump directly to the first active callback.

## State and Persistence Behavior
Runtime state includes `static_calls_table`, registered hook descriptors, blob size allocations, enable flags, and init ordering. The state is initialized at boot and is not persistent.

## Dependencies and Integration Points
It depends on UAPI LSM IDs, security core declarations, RCU lists, xattrs, static calls, jump labels, unroll helpers, and `lsm_count.h`. It integrates every in-kernel LSM with the common security hook dispatch layer.

## Risks and Test Signals
Risks include bad hook initialization, wrong LSM ordering or exclusivity flags, static-call table sizing errors, blob offset conflicts, and xattr slot overrun. Test signals are boot-time enabled LSM logs, LSM selftests, multi-LSM stacking tests, static-call coverage, and xattr allocation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lsm_hooks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lwq.h -->
# sources/distributed-fs/ceph-client/include/linux/lwq.h

## Purpose
This header declares a lightweight queue built on `llist` plus a spinlock for dequeue serialization. It supports fast lockless enqueue and ordered dequeue of batches.

## Important APIs, Types, and Functions
`struct lwq_node` wraps an `llist_node`; `struct lwq` contains an `llist_head`, spinlock, and dequeue cursor. APIs include `lwq_init`, `lwq_empty`, `__lwq_dequeue`, typed `lwq_dequeue`, `lwq_dequeue_all`, `lwq_for_each_safe`, `lwq_enqueue`, and `lwq_enqueue_batch`.

## Control Flow
Enqueue uses `llist_add` or batch add into the lockless head. Dequeue takes the queue lock, drains or advances the internal list, and typed macros convert nodes back to containing structures. Batch dequeue can return a chain for caller traversal.

## State and Persistence Behavior
Runtime state is queued node links, the llist head, the spinlock, and the current dequeue list. No persistence exists.

## Dependencies and Integration Points
It depends on `container_of`, spinlocks, and `llist.h`. It integrates with producer-heavy subsystems that want low-overhead enqueue but serialized consumer processing.

## Risks and Test Signals
Risks include enqueueing an already queued node, traversing live llist contents, failing to hold dequeue serialization, and order surprises from llist newest-first behavior. Test signals are concurrent producer stress, queue drain/order tests, lockdep on dequeue paths, and KCSAN.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lwq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lz4.h -->
# sources/distributed-fs/ceph-client/include/linux/lz4.h

## Purpose
This header declares the kernel LZ4 compression interface, including one-shot, high-compression, streaming compression, streaming decompression, dictionary handling, bounds, and state-buffer sizes.

## Important APIs, Types, and Functions
Constants include `LZ4_MEMORY_USAGE`, `LZ4_MAX_INPUT_SIZE`, `LZ4_COMPRESSBOUND`, `LZ4_MEM_COMPRESS`, `LZ4HC_MEM_COMPRESS`, and `LZ4_DISTANCE_MAX`. State types are `LZ4_stream_t`, `LZ4_streamHC_t`, and `LZ4_streamDecode_t`. APIs include `LZ4_compressBound`, `LZ4_compress_default`, `LZ4_compress_fast`, `LZ4_compress_destSize`, safe and fast decompressors, HC compression and reset/load/save dictionary helpers, streaming continue functions, and dictionary-based decompression.

## Control Flow
Callers allocate work memory or stream state, then compress blocks into caller-sized buffers. Streaming functions preserve recent history or saved dictionaries across blocks. Safe decompression validates input and output bounds; fast decompression assumes trusted input and known output size.

## State and Persistence Behavior
One-shot APIs use caller-provided work memory transiently. Streaming state stores hash tables, offsets, dictionary pointers, prefix state, and HC chains. Compressed data may be persisted by callers, but the header manages no storage.

## Dependencies and Integration Points
It depends on kernel types and string helpers. Integration points include zram, filesystems, network/storage compression, and any kernel subsystem using raw LZ4 blocks.

## Risks and Test Signals
Risks include undersized output buffers, using fast decompression on untrusted data, invalid source sizes above `LZ4_MAX_INPUT_SIZE`, stale dictionary memory, and stream-state reuse without reset. Test signals are compression round trips, malformed-input tests, boundary-size tests, dictionary/ring-buffer streaming tests, and sanitizer/fuzzer coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lz4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lzo.h -->
# sources/distributed-fs/ceph-client/include/linux/lzo.h

## Purpose
This header declares the kernel LZO1X and LZO-RLE compression/decompression interfaces and error code contract.

## Important APIs, Types, and Functions
It defines work-memory size `LZO1X_1_MEM_COMPRESS`, worst-case bound macro `lzo1x_worst_compress`, compressors `lzo1x_1_compress`, `lzo1x_1_compress_safe`, `lzorle1x_1_compress`, `lzorle1x_1_compress_safe`, decompressor `lzo1x_decompress_safe`, and result codes from `LZO_E_OK` through `LZO_E_INVALID_ARGUMENT`.

## Control Flow
Compression reads a source buffer into a caller-provided destination and work memory, returning output length and status. Safe variants add argument/bounds checking. Decompression validates encoded input and stops on overrun, EOF, or lookbehind errors.

## State and Persistence Behavior
No state is stored in the header. Work memory and output buffers are caller-owned; compressed bytes may be persisted by higher layers.

## Dependencies and Integration Points
It uses size types and integrates with kernel subsystems that support LZO compression, including filesystems, zram, and image formats.

## Risks and Test Signals
Risks include insufficient destination space, ignoring negative error codes, unsafe input trust assumptions, and incorrect worst-case sizing. Test signals are round-trip tests, malformed-stream tests, all error-code paths, and compression-bound boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lzo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/arm_mhuv2_message.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox/arm_mhuv2_message.h

## Purpose
This header defines the message payload used by ARM MHUv2 mailbox clients.

## Important APIs, Types, and Functions
`struct arm_mhuv2_mbox_msg` carries channel/protocol-specific data fields for an MHUv2 transfer. The header only defines the data contract and includes fixed-width kernel types.

## Control Flow
There is no code flow. Mailbox clients populate the message and pass it to the MHUv2 mailbox controller, which interprets and sends it.

## State and Persistence Behavior
Messages are transient request data. Persistent state lives in firmware, remote processors, or mailbox controller driver state.

## Dependencies and Integration Points
It depends on `linux/types.h` and integrates with the generic mailbox framework and ARM MHUv2 controller/client drivers.

## Risks and Test Signals
Risks include field interpretation mismatches between client and controller, wrong channel use, and remote firmware protocol drift. Test signals are mailbox send/receive tests, remote endpoint acknowledgements, and controller trace logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/arm_mhuv2_message.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/brcm-message.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox/brcm-message.h

## Purpose
This header defines Broadcom mailbox message formats, especially scatter-gather command messages for SBA-style mailbox engines.

## Important APIs, Types, and Functions
`enum brcm_message_type` identifies message categories. `struct brcm_sba_command` describes command flags, source/destination scatterlists, and lengths. Flags include `BRCM_SBA_CMD_TYPE_A/B/C`, `BRCM_SBA_CMD_HAS_RESP`, and `BRCM_SBA_CMD_HAS_OUTPUT`. `struct brcm_message` wraps type-specific payloads.

## Control Flow
Mailbox clients construct a Broadcom message, optionally describing DMA scatterlists and response/output expectations, then submit it through the mailbox framework to the controller or accelerator.

## State and Persistence Behavior
The structures are transient command descriptors. DMA buffers and scatterlists are caller-managed and must outlive the mailbox transaction.

## Dependencies and Integration Points
It depends on `linux/scatterlist.h` and integrates with Broadcom mailbox controllers, SBA offload engines, and mailbox clients using scatter-gather data movement.

## Risks and Test Signals
Risks include invalid scatterlists, incorrect response/output flags, buffer lifetime bugs, and DMA mapping mismatches. Test signals are mailbox transaction completion, DMA API debugging, response validation, and scatter-gather boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/brcm-message.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/exynos-message.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox/exynos-message.h

## Purpose
This header defines Exynos mailbox message metadata for doorbell and data-channel transfers.

## Important APIs, Types, and Functions
It defines channel type constants `EXYNOS_MBOX_CHAN_TYPE_DOORBELL` and `EXYNOS_MBOX_CHAN_TYPE_DATA`, plus `struct exynos_mbox_msg` for message content and channel selection.

## Control Flow
Clients fill an Exynos message and submit it through the mailbox API. The controller interprets whether the operation is doorbell-style notification or data transfer.

## State and Persistence Behavior
Messages are transient. Controller registers and remote firmware state are external.

## Dependencies and Integration Points
It integrates with Samsung Exynos mailbox controller and client drivers using the generic mailbox framework.

## Risks and Test Signals
Risks include wrong channel type, payload size mismatch, and remote endpoint protocol mismatch. Test signals are interrupt/doorbell delivery, data echo tests, and controller debug logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/exynos-message.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/mchp-ipc.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox/mchp-ipc.h

## Purpose
This header defines Microchip IPC mailbox message and SBI channel metadata.

## Important APIs, Types, and Functions
`struct mchp_ipc_msg` carries message command/data fields. `struct mchp_ipc_sbi_chan` associates an SBI channel with mailbox framework structures and identifiers.

## Control Flow
Clients prepare an IPC message and submit it through a mailbox channel. SBI channel descriptors let platform code bind firmware-facing channels to mailbox controller plumbing.

## State and Persistence Behavior
Message data is transient. Channel state is runtime driver/controller state, not owned by the header.

## Dependencies and Integration Points
It depends on `linux/mailbox_controller.h` and `linux/types.h`. It integrates with Microchip mailbox/IPCore drivers and firmware protocols.

## Risks and Test Signals
Risks include wrong command IDs, channel misregistration, remote firmware incompatibility, and lifetime issues for channel descriptors. Test signals are firmware command responses, mailbox timeout handling, and channel registration/remove tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/mchp-ipc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/mtk-cmdq-mailbox.h -->
# sources/distributed-fs/ceph-client/include/linux/mailbox/mtk-cmdq-mailbox.h

## Purpose
This header defines the MediaTek Command Queue mailbox client interface. It describes command packet layout, event/wait encodings, callback data, and helpers for extracting mailbox-private address-shift data.

## Important APIs, Types, and Functions
Constants include instruction size, subsystem shift, opcode shift, jump pass, WFE option bits, and `CMDQ_MAX_EVENT`. `enum cmdq_code` lists command opcodes. `struct cmdq_cb_data` carries completion status and packet data. `struct cmdq_mbox_priv` exposes thread and physical-address shift metadata. `struct cmdq_pkt` holds the command buffer, buffer size, command count, mailbox client, and completion callback. APIs include `cmdq_get_mbox_priv` and `cmdq_get_shift_pa`.

## Control Flow
Clients build a `cmdq_pkt` as a sequence of 64-bit instructions, submit it through a mailbox channel, and receive callback data on completion. Wait-for-event instructions use the WFE bit encodings and event IDs.

## State and Persistence Behavior
Packet buffers and callbacks are caller-managed runtime state. Hardware queue state and events live in the CMDQ controller; no persistence is provided.

## Dependencies and Integration Points
It depends on platform devices, slab/types, and mailbox channel structures. It integrates with MediaTek display, multimedia, and SoC drivers that offload register programming to CMDQ hardware.

## Risks and Test Signals
Risks include malformed instruction encoding, insufficient packet buffer sizing, wrong physical-address shift, event ID overflow, and callback lifetime bugs. Test signals are CMDQ packet submission tests, hardware completion interrupts, timeout/error status checks, and display/media pipeline smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mailbox/mtk-cmdq-mailbox.h -->
