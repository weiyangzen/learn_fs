# Research: subset-b-006015

Work item `subset-b-006015` covers six Linux kernel BPF source files under `sources/distributed-fs/ceph-client/kernel/bpf/`. Each section below is wrapped for deterministic reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/helpers.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/helpers.c

## Purpose

`helpers.c` is the central implementation and registration point for many generic eBPF helpers and kfuncs. It backs map operations, time and task identity helpers, formatting helpers, dynptr operations, BPF timers/workqueues/task work, BPF-owned objects and graph containers, task/cgroup/key reference kfuncs, string kfuncs, and the default helper-prototype lookup used by verifier program-type operations.

The file is not Ceph-specific despite the repository path. It is kernel BPF runtime plumbing: it defines what BPF programs can call, how those calls are described to the verifier through `struct bpf_func_proto` and BTF kfunc ID sets, and how helper-owned state is initialized, referenced, cancelled, and freed.

## Important APIs, Types, And Functions

Map helpers include `bpf_map_lookup_elem`, `bpf_map_update_elem`, `bpf_map_delete_elem`, stack/queue helpers `bpf_map_push_elem`, `bpf_map_pop_elem`, `bpf_map_peek_elem`, and `bpf_map_lookup_percpu_elem`. These mostly delegate to `map->ops` and rely on verifier-supplied argument constraints in the corresponding `bpf_func_proto` objects.

Task/time/system helpers include `bpf_get_smp_processor_id`, `bpf_get_numa_node_id`, `bpf_ktime_get_ns`, `bpf_ktime_get_boot_ns`, `bpf_ktime_get_coarse_ns`, `bpf_ktime_get_tai_ns`, `bpf_get_current_pid_tgid`, `bpf_get_current_uid_gid`, `bpf_get_current_comm`, `bpf_jiffies64`, and cgroup helpers guarded by `CONFIG_CGROUPS`.

Synchronization and map-value support include `bpf_spin_lock`, `bpf_spin_unlock`, `copy_map_value_locked`, and `bpf_kptr_xchg`. Spin-lock helpers use either architecture spinlocks or an atomic fallback, save/restore local IRQ state, and expose poisoned BTF IDs so the verifier supplies the real lock type.

Formatting support centers on `bpf_bprintf_prepare`, `bpf_try_get_buffers`, `bpf_put_buffers`, `bpf_bprintf_cleanup`, and `bpf_snprintf`. It validates BPF format strings, supports bounded per-CPU nested buffers, copies `%s`/`%pks`/`%pus` data safely, and emits binary argument buffers for `bstr_printf`.

Async support introduces `struct bpf_async_cb`, `struct bpf_hrtimer`, `struct bpf_work`, and `struct bpf_async_kern`. Public helper/kfunc entry points include `bpf_timer_init`, `bpf_timer_set_callback`, `bpf_timer_start`, `bpf_timer_cancel`, `bpf_timer_cancel_async`, `bpf_wq_init`, `bpf_wq_set_callback`, `bpf_wq_start`, plus cleanup hooks `bpf_timer_cancel_and_free` and `bpf_wq_cancel_and_free`.

Dynptr support includes metadata helpers such as `bpf_dynptr_init`, `bpf_dynptr_set_null`, `__bpf_dynptr_size`, read/write helpers `bpf_dynptr_read`, `bpf_dynptr_write`, pointer-return helpers `bpf_dynptr_data`, `bpf_dynptr_slice`, `bpf_dynptr_slice_rdwr`, and kfuncs `bpf_dynptr_adjust`, `bpf_dynptr_clone`, `bpf_dynptr_copy`, `bpf_dynptr_memset`, `bpf_dynptr_from_file`, and `bpf_dynptr_file_discard`.

BPF object and container kfuncs include `bpf_obj_new`, `bpf_percpu_obj_new`, `bpf_obj_drop`, `bpf_percpu_obj_drop`, `bpf_refcount_acquire`, list operations `bpf_list_push_front`, `bpf_list_push_back`, `bpf_list_pop_front`, `bpf_list_pop_back`, and rbtree operations `bpf_rbtree_add`, `bpf_rbtree_remove`, `bpf_rbtree_first`, `bpf_rbtree_root`, `bpf_rbtree_left`, `bpf_rbtree_right`.

Kernel object reference kfuncs include `bpf_task_acquire`, `bpf_task_release`, `bpf_task_from_pid`, `bpf_task_from_vpid`, and, under cgroup support, `bpf_cgroup_acquire`, `bpf_cgroup_release`, `bpf_cgroup_ancestor`, `bpf_cgroup_from_id`, `bpf_task_under_cgroup`, and `bpf_task_get_cgroup1`.

String and user-copy kfuncs include `bpf_copy_from_user_str`, `bpf_copy_from_user_task_str`, `bpf_strcmp`, `bpf_strcasecmp`, `bpf_strncasecmp`, `bpf_strnchr`, `bpf_strchr`, `bpf_strchrnul`, `bpf_strrchr`, `bpf_strnlen`, `bpf_strlen`, `bpf_strspn`, `bpf_strcspn`, `bpf_strstr`, `bpf_strcasestr`, `bpf_strnstr`, and `bpf_strncasestr`.

Registration is concentrated in `bpf_base_func_proto()` for classic helper IDs and `kfunc_init()` for BTF kfunc sets. `generic_btf_ids`, `common_btf_ids`, and `generic_dtor_ids` encode verifier flags such as `KF_ACQUIRE`, `KF_RELEASE`, `KF_RET_NULL`, `KF_RCU`, `KF_SLEEPABLE`, `KF_ITER_NEW`, and `KF_IMPLICIT_ARGS`.

## Control Flow

Classic helper calls are shallow wrappers: the BPF program calls a helper ID, verifier dispatch obtains a `struct bpf_func_proto` through `bpf_base_func_proto()`, and the runtime helper delegates into kernel subsystems. Map helpers validate RCU expectations with `WARN_ON_ONCE(!bpf_rcu_lock_held())` before using map ops.

`bpf_base_func_proto()` has capability-gated phases. Some helpers are always exposed, then helpers requiring `CAP_BPF` are exposed only when `bpf_token_capable(prog->aux->token, CAP_BPF)` succeeds, and tracing/perf-oriented helpers are exposed only under `CAP_PERFMON`. Some helpers are additionally disabled by lockdown checks or compile-time config.

Timer/workqueue initialization uses `__bpf_async_init()` to allocate the hidden callback object, initialize the hrtimer or work item, attach it to the map value's embedded `bpf_timer`/`bpf_wq`, and reject initialization if the map has no user reference. Start/cancel paths either execute directly or enqueue `struct bpf_async_cmd` into a lockless list for `irq_work` handling when hard IRQ or IRQ-disabled context prevents synchronous work.

Callback installation uses `bpf_async_update_prog_callback()` to safely swap the callback function and BPF program reference. Timer callbacks derive the map key from the value, invoke the BPF callback, and guard against self-cancel deadlocks through per-CPU `hrtimer_running`. Workqueue callbacks run under trace RCU and migration disable.

Dynptr control flow first validates non-null state, flags, and offset/length bounds, then dispatches by dynptr type. Local and ringbuf dynptrs use direct memory moves; skb/xdp dynptrs call packet helpers; file dynptrs use `freader_fetch` and explicit discard cleanup.

BPF object/container kfuncs are verifier-coupled. The verifier rewrites implicit `meta`, offsets, and callback arguments. Runtime code performs allocation, field initialization, ownership checks via `owner` pointers, linked-list/rbtree mutation, and recursive field destruction through BTF records.

Task work scheduling flows from `bpf_task_work_schedule_signal()` or `_resume()` into `bpf_task_work_schedule()`, then through an IRQ work trampoline to `task_work_add()`, then finally into `bpf_task_work_callback()`. A small state machine prevents reuse after free and coordinates standby, pending, scheduling, scheduled, running, and freed states.

## State And Persistence Behavior

Most helper state is transient runtime state: per-CPU bprintf buffers, per-CPU currently-running async callbacks, timer/workqueue/task-work contexts embedded in map values, dynptr metadata, and BPF-owned heap objects.

State tied to BPF maps persists as long as the map value or map user reference persists. Timers, workqueues, and task work must be cancelled when map values are deleted, updated, or released through map uref cleanup hooks. BPF object allocations are freed through `bpf_obj_drop`/destructors or RCU-delayed free paths.

Dynptrs are stack/local program objects except file dynptrs, which allocate a `bpf_dynptr_file_impl` containing `struct freader` state that must be released through `bpf_dynptr_file_discard`.

The file also persists global registration state after `late_initcall(kfunc_init)`: helper prototypes and BTF kfunc ID sets become available for verifier lookup for supported program types.

## Dependencies And Integration Points

This file integrates with BPF maps, verifier metadata, BTF, BPF memory allocators, RCU and RCU Tasks Trace, hrtimers, workqueues, task work, cgroups, kernel keys/signature verification, skb/xdp packet helpers, perf/tracing helpers, lockdown/security hooks, and architecture-specific stack walking and spinlock behavior.

Important cross-file dependencies include verifier helpers from `bpf_verifier.h`, BTF records and field metadata, map `ops` implementations, ringbuf helpers, cgroup storage helpers, task local storage helpers, and optional iterator kfuncs registered in other files such as `kmem_cache_iter.c`.

## Risks And Edge Cases

Async lifetime is the highest-risk area. The code must avoid use-after-free when map user references disappear while timers/workqueues/task work are being started or cancelled. The refcount, RCU Tasks Trace, irq_work fallback, and repeated cancel-after-grace logic are all essential and easy to regress.

Deadlock avoidance is subtle for timer cancellation from callbacks, nested async scheduling from irq_work, local IRQ save/restore around BPF spin locks, and task_work cancellation after state transitions.

Dynptr risks include offset/length overflow, writable access to read-only dynptrs, non-linear skb/xdp data semantics, file contents changing behind an unrestricted-size file dynptr, and requiring explicit discard for file dynptr allocation state.

Formatting and string kfuncs deliberately use nofault copies and size limits. Regressions can expose kernel memory, accept invalid format strings, or allow unbounded scans.

Helper exposure is security-sensitive. Mistakes in `bpf_base_func_proto()` capability gates, lockdown checks, kfunc flags, or implicit-argument annotations can widen BPF program authority beyond the verifier's assumptions.

## Test Signals

Relevant test signals include BPF selftests for helpers, timers, workqueues, task work, dynptr read/write/slice/copy/memset, object allocation/refcount/list/rbtree kfuncs, kfunc registration, cgroup/task kfunc references, key/signature kfuncs, string kfuncs, and verifier rejection tests for invalid argument types and capabilities.

Runtime stress should include concurrent map value deletion/update while timers and workqueues are active, callback self-cancel attempts, IRQ-disabled start/cancel paths, nested bprintf calls beyond the allowed level, dynptr boundary cases, and mount/token capability combinations that alter helper availability.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/inode.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/inode.c

## Purpose

`inode.c` implements bpffs, the pseudo filesystem used to pin and retrieve BPF maps, programs, and links through filesystem paths. It provides inode creation, object typing, seq_file display for maps, user-facing `BPF_OBJ_PIN`/`BPF_OBJ_GET` path operations, mount option parsing, optional preload population, and filesystem registration.

## Important APIs, Types, And Functions

`enum bpf_type` distinguishes `BPF_TYPE_PROG`, `BPF_TYPE_MAP`, and `BPF_TYPE_LINK`. `bpf_any_get()` and `bpf_any_put()` apply the matching reference operation for each object type. `bpf_fd_probe_obj()` tries a user fd as map, then program, then link.

`bpf_get_inode()` creates bpffs inodes for directories, regular pinned objects, and symlinks. `bpf_inode_type()` uses inode operation table identity (`bpf_prog_iops`, `bpf_map_iops`, `bpf_link_iops`) to recover the object kind.

Map display uses `struct map_iter`, `map_seq_start()`, `map_seq_next()`, `map_seq_show()`, `bpffs_map_open()`, and `bpffs_map_release()`. It uses `map_get_next_key()` and optional `map_seq_show_elem()` support to make `cat /sys/fs/bpf/...` useful for maps that expose debug output.

Pinning uses `bpf_mkobj_ops()`, `bpf_mkprog()`, `bpf_mkmap()`, `bpf_mklink()`, `bpf_obj_do_pin()`, and `bpf_obj_pin_user()`. Retrieval uses `bpf_obj_do_get()` and `bpf_obj_get_user()`, returning new fds through `bpf_prog_new_fd()`, `bpf_map_new_fd()`, or `bpf_link_new_fd()`.

Filesystem operations include `bpf_mkdir()`, `bpf_symlink()`, `bpf_lookup()`, `bpf_dir_iops`, `bpf_super_ops`, `bpf_fill_super()`, `bpf_get_tree()`, `bpf_init_fs_context()`, `bpf_kill_super()`, and `bpf_init()`.

Mount delegation parsing uses `struct bpf_mount_opts`, `find_bpffs_btf_enums()`, `find_btf_enum_const()`, `seq_print_delegate_opts()`, `bpf_show_options()`, and `bpf_parse_param()`. Options include uid, gid, mode, and delegation masks for commands, map types, program types, and attach types.

Preload support uses exported `bpf_preload_ops`, `bpf_preload_mod_get()`, `bpf_preload_mod_put()`, `populate_bpffs()`, and `bpf_iter_link_pin_kernel()` to pin kernel-created iterator links into a new bpffs mount.

## Control Flow

For pinning, `bpf_obj_pin_user()` first resolves the fd to a referenced BPF object, then `bpf_obj_do_pin()` creates a dentry with `start_creating_user_path()`, verifies the parent is a bpffs directory, applies `security_path_mknod()`, and invokes `vfs_mkobj()` with the right object constructor. On failure after fd probing, the object reference is released.

For lookup, `bpf_obj_get_user()` validates requested flags, resolves the path, checks path permissions, verifies the inode operation table corresponds to a pinned BPF object, takes a new object reference, touches atime, and creates the matching fd. Link retrieval requires `O_RDWR`.

Map read control flow is a seq_file iterator. The first output line is a warning header, then `map_seq_next()` walks map keys under RCU using `map_get_next_key()`, and `map_seq_show()` delegates element formatting to `map->ops->map_seq_show_elem()`.

Mount creation allocates a fs context with defaults from current fsuid/fsgid and mode `0777`, parses parameters, then `bpf_fill_super()` requires privileges for non-init user namespaces, initializes a simple superblock, sets root ownership/mode, optionally populates preload links, and finally enables sticky bit plus requested mode.

## State And Persistence Behavior

Pinned objects persist through inode `i_private` and object references. `bpf_destroy_inode()` releases pinned object references based on inode type and frees symlink targets. Unlinking removes the filesystem entry and inode release drops the BPF object reference.

bpffs mount options persist in `sb->s_fs_info` for the lifetime of the mount. Root inode uid/gid/mode reflect parsed options. Delegation masks are displayed in `/proc/mounts` using BTF enum names when available.

Preloaded links are pinned into the root of a bpffs instance during mount population. The preload module is temporarily referenced while the kernel calls its preload operations.

## Dependencies And Integration Points

This file depends on VFS helpers, fs_context parsing, Linux security hooks, BPF object fd/reference APIs, map operation callbacks, BTF enum introspection, and the optional `bpf_preload` module. It exports `bpf_prog_get_type_path()` for kernel users that need to open a pinned program by path and verify a program type.

## Risks And Edge Cases

The inode operation pointer is the object type discriminator, so any future inode operation change must preserve this invariant or update `bpf_inode_type()`. Reference mismatches in pin/get/error paths would leak BPF objects or prematurely free them.

Name handling reserves dots in non-private bpffs directories; changing that policy could conflict with future special files created by `populate_bpffs()`. Mount delegation parsing uses BTF enum names and hex fallback; malformed masks or privilege bypasses would affect BPF token delegation.

Map `cat` output is explicitly debug-only and format-unstable. It depends on maps safely implementing `map_seq_show_elem()` and `map_get_next_key()` under RCU.

## Test Signals

Useful tests include BPF selftests for pin/get/unpin of maps, programs, and links; permission and flag validation; link `O_RDWR` enforcement; map seq output; bpffs mount uid/gid/mode/delegation options; preload link population; and cleanup of object references after unlink and unmount.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/kmem_cache_iter.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/kmem_cache_iter.c

## Purpose

`kmem_cache_iter.c` implements a BPF iterator target and open-coded iterator kfuncs for walking kernel slab `struct kmem_cache` objects. It exposes slab cache metadata to BPF iterator programs while coordinating with slab lifetime rules through `slab_mutex` and explicit refcount handling.

## Important APIs, Types, And Functions

`struct bpf_iter_kmem_cache` is the public opaque iterator state. `struct bpf_iter_kmem_cache_kern` stores the current `struct kmem_cache *`. `KMEM_CACHE_POS_START` is a sentinel for the not-yet-started state.

Open-coded iterator kfuncs are `bpf_iter_kmem_cache_new()`, `bpf_iter_kmem_cache_next()`, and `bpf_iter_kmem_cache_destroy()`. They initialize the cursor, return successive slab caches, and release the current cache reference.

Seq-file integration uses `struct bpf_iter__kmem_cache`, `union kmem_cache_iter_priv`, `kmem_cache_iter_seq_start()`, `kmem_cache_iter_seq_next()`, `kmem_cache_iter_seq_stop()`, and `kmem_cache_iter_seq_show()`.

Registration uses `BTF_ID_LIST_GLOBAL_SINGLE(bpf_kmem_cache_btf_id, struct, kmem_cache)`, `DEFINE_BPF_ITER_FUNC(kmem_cache, ...)`, `bpf_kmem_cache_reg_info`, and `bpf_kmem_cache_iter_init()`.

## Control Flow

The open-coded iterator starts with `kit->pos = KMEM_CACHE_POS_START`. `bpf_iter_kmem_cache_next()` locks `slab_mutex`, handles empty lists, translates the sentinel to the first entry, advances from the previous entry otherwise, increments `next->refcount` for active caches, and drops/destroys the previous cache after releasing the mutex if its refcount reaches zero.

The seq-file iterator starts by scanning `slab_caches` to the requested position while holding `slab_mutex`. It takes a reference to the selected active cache, stores it in private iterator state, calls the attached BPF iterator program in `show`, and invokes the program one final time with `s == NULL` from `stop` for end-of-iteration semantics.

Registration happens at `late_initcall`, fills the BTF ID for `struct kmem_cache`, and registers the target name `kmem_cache` with `BPF_ITER_RESCHED` and a trusted nullable BTF pointer context argument.

## State And Persistence Behavior

Iterator state is per-open or per open-coded iterator invocation and stores only the current cache pointer. It does not own the global slab list; it temporarily bumps `kmem_cache->refcount` for active entries and releases that reference on next/destroy/stop.

Boot caches have negative refcounts and are deliberately not touched. Cache destruction may be deferred until after dropping `slab_mutex` when the iterator releases the last active reference.

## Dependencies And Integration Points

The file reaches into `../../mm/slab.h` for `kmem_cache`, `slab_caches`, and `slab_mutex`. It integrates with BPF iterator registration, BTF ID resolution, seq_file, and slab allocator lifetime rules.

## Risks And Edge Cases

The seq start path scans by position instead of keeping a reference across all mutations, so concurrent deletion can skip or miss entries. Comments call this rare and acceptable. Refcount handling is delicate: destroying under `slab_mutex` would be unsafe, while failing to destroy after refcount reaches one would leak caches awaiting destruction.

The iterator is sleepable because it takes `slab_mutex`. BTF flags and registration must continue to reflect that or verifier assumptions will be wrong.

## Test Signals

Tests should cover open-coded iterator use, seq iterator use through BPF iter links, empty slab lists, early destroy without next, full iteration with final NULL callback, and concurrent cache create/destroy stress under slab debug or KASAN.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/kmem_cache_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/link_iter.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/link_iter.c

## Purpose

`link_iter.c` registers a BPF iterator target named `bpf_link` that walks live BPF links and passes each `struct bpf_link *` to a BPF iterator program. It provides the seq_file glue needed for iterator links that enumerate kernel BPF link objects.

## Important APIs, Types, And Functions

`struct bpf_iter_seq_link_info` stores the current `link_id` cursor. `bpf_link_seq_start()`, `bpf_link_seq_next()`, `bpf_link_seq_stop()`, and `bpf_link_seq_show()` implement the seq operations. `__bpf_link_seq_show()` builds the iterator context and invokes the attached BPF program.

`struct bpf_iter__bpf_link` is the BTF-visible iterator context containing `meta` and nullable `link`. `DEFINE_BPF_ITER_FUNC(bpf_link, ...)` declares the iterator callback signature.

Registration uses `BTF_ID_LIST_SINGLE(btf_bpf_link_id, struct, bpf_link)`, `bpf_link_seq_info`, `bpf_link_reg_info`, and `bpf_link_iter_init()`.

## Control Flow

Iteration starts by calling `bpf_link_get_curr_or_next(&info->link_id)`, which returns a referenced link at or after the current ID. `start` bumps `*pos` from zero to one for seq semantics. `next` increments both the seq position and `link_id`, releases the current link with `bpf_link_put()`, and acquires the next one.

`show` runs the attached BPF iterator program with `in_stop == false`. `stop` either emits the final `link == NULL` callback with `in_stop == true` or releases the last referenced link.

At init, the file fills the context argument BTF ID for `struct bpf_link` and registers the target.

## State And Persistence Behavior

The iterator keeps only a per-open numeric link ID cursor. It does not persist link state. Each returned link is reference-counted during the current seq item and released in `next` or `stop`.

The final NULL callback is observable by iterator programs and allows end-of-iteration flushing.

## Dependencies And Integration Points

This file depends on BPF link ID allocation/lookup, BPF link reference counting, BPF iterator registration, BTF IDs, and seq_file. It integrates with bpffs through pinned iterator links and with user space via BPF iter link reads.

## Risks And Edge Cases

The cursor uses current-or-next ID lookup, so links created or deleted concurrently can be skipped or observed depending on timing. Correct reference release in `next` and `stop` is critical. The final NULL callback must happen only when no current object is held.

The iterator context argument is nullable; verifier and BPF programs must handle the NULL end marker.

## Test Signals

Tests should create multiple BPF links, iterate them, delete links during iteration, verify no reference leaks, verify final NULL callback behavior, and confirm BTF context typing for `struct bpf_link *`.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/link_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/liveness.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/liveness.c

## Purpose

`liveness.c` implements verifier dataflow analyses for BPF register and stack-slot liveness. The results let the verifier know which registers and stack slots are live before instructions, supporting state pruning and correctness around subprograms, callbacks, helper/kfunc stack accesses, and frame-pointer-derived pointer flows.

The file has two major analyses: stack liveness across function instances and call chains, and whole-program register liveness over the control-flow graph.

## Important APIs, Types, And Functions

`struct per_frame_masks` stores `may_read`, `must_write`, and computed `live_before` stack-slot masks per instruction and frame. `struct func_instance` identifies a subprogram instance by callsite and depth and owns lazily allocated per-frame mask arrays. `struct bpf_liveness` owns the function-instance hash table, cached live-stack query, and complexity counter.

Initialization and lookup functions include `bpf_stack_liveness_init()`, `bpf_stack_liveness_free()`, `call_instance()`, `find_instance()`, `lookup_instance()`, `mark_stack_read()`, and `mark_stack_write()`.

CFG successor handling is centralized in `bpf_jmp_offset()` and `bpf_insn_successors()`. The latter accounts for normal fallthrough, jumps, exits, `ldimm64` two-instruction width, and precomputed jump tables in `insn_aux_data[idx].jt`.

Stack fixed-point functions include `update_insn()`, `update_instance()`, `bpf_live_stack_query_init()`, and `bpf_stack_slot_alive()`.

Argument/frame-pointer tracking uses `struct arg_track`, `enum arg_track_state`, `arg_track_join()`, `arg_track_alu64()`, `fill_from_stack()`, `spill_to_stack()`, `clear_stack_for_all_offs()`, and `arg_track_xfer()`.

Access recording functions include `record_stack_access_off()`, `record_stack_access()`, `record_imprecise()`, `record_load_store_access()`, `record_call_access()`, and `find_callback_subprog()`.

Recursive subprogram analysis uses `compute_subprog_args()`, `analyze_subprog()`, `merge_instances()`, `fresh_instance()`, and public `bpf_compute_subprog_arg_access()`.

Register liveness uses `struct insn_live_regs`, `compute_insn_live_regs()`, and public `bpf_compute_live_registers()`.

## Control Flow

Stack analysis starts with `bpf_compute_subprog_arg_access()`, which allocates temporary per-subprogram state and callsite stack snapshots. It walks subprograms in reverse topological order, creates or reuses `func_instance` objects, and calls `analyze_subprog()`.

`analyze_subprog()` first computes local argument/frame-pointer dataflow for one subprogram instance. It then recurses into pseudo-call callees or known callback subprograms when frame-pointer-derived arguments are passed. After analyzing a callee, it pulls the callee's entry liveness back to the caller callsite so parent stack slots stay live when the callee reads them.

`compute_subprog_args()` performs a forward fixed-point pass over the subprogram in reverse postorder. It tracks how registers and stack spill slots derive from frame pointers, propagates states to CFG successors with a lattice join, then performs a second pass to record stack reads/writes implied by loads, stores, helper calls, and kfunc calls.

After reads and writes are recorded, `update_instance()` computes stack `live_before` masks by repeatedly applying `live_before = (successor_live & ~must_write) | may_read` until no instruction changes.

Register liveness is computed by `bpf_compute_live_registers()`. It first computes instruction-level `use` and `def` masks, invokes stack/subprogram access analysis, then iterates over CFG postorder until `in` and `out` register sets reach a fixed point. Final results are stored in `env->insn_aux_data[i].live_regs_before`.

## State And Persistence Behavior

All state is verifier-run scoped. `env->liveness` persists for the lifetime of verification and is freed by `bpf_stack_liveness_free()`. Per-instance frame mask arrays are lazily allocated only for frames and instructions that observe stack accesses.

Temporary analysis arrays (`at_in`, stack snapshots, callsite stack maps, register live state) are allocated with kernel-accounted memory and freed before returning. The persistent outputs are stack liveness masks in `env->liveness` and register masks in `env->insn_aux_data`.

The query cache in `struct live_stack_query` stores the current verifier state's instances, callsites, current frame, and instruction index to avoid repeated hash lookups during stack-slot alive queries.

## Dependencies And Integration Points

This file depends on verifier structures in `linux/bpf_verifier.h`, BPF instruction encoding, verifier CFG postorder data, subprogram metadata, helper/kfunc stack access summaries, callback detection, jump table metadata, `spis_t` stack-slot bit operations, BTF-aware call summaries, and verifier logging.

It integrates directly with verifier state pruning through `bpf_stack_slot_alive()` and register liveness through `live_regs_before`. It also supports verifier debug output when `BPF_LOG_LEVEL2` is enabled.

## Risks And Edge Cases

The analysis is conservative when frame-pointer identity becomes imprecise, when callbacks are ambiguous, when helper/kfunc stack access size is unknown, or when parent-frame stack can be accessed. Conservative marking can reduce pruning efficiency but avoids unsoundness.

Function instances are keyed by callsite and depth. Incorrect keying or merging can conflate different call chains and either miss stack reads or overstate writes. `must_write` is especially subtle because repeated analysis of an instance intersects writes across passes.

Callback handling is specialized for helpers such as `bpf_loop`, `bpf_for_each_map_elem`, `bpf_find_vma`, and `bpf_user_ringbuf_drain`. Adding callback-capable helpers without updating `find_callback_subprog()` can make stack liveness inaccurate.

Complexity is bounded by `subprog_calls > 10000`; very complex call/callback graphs can fail verification with `-E2BIG`. Allocation pressure can fail verification with `-ENOMEM`.

CFG successor correctness is foundational. Incorrect handling of jump tables, `ldimm64`, exits, or conditional jumps would affect both stack and register fixed points.

## Test Signals

Relevant tests include verifier selftests for register liveness, dead register pruning, stack slot pruning, helper and kfunc stack read/write summaries, callbacks receiving stack pointers, nested subprograms, global and async callback subprograms, jump-table control flow, imprecise pointer arithmetic, partial stack writes, atomic stack operations, and BPF_LOG_LEVEL2 diagnostic output.

Stress tests should include deep call chains, repeated callsite instances, ambiguous callbacks, parent-stack access through spilled frame pointers, and large CFGs approaching the complexity limit.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/liveness.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/local_storage.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/local_storage.c

## Purpose

`local_storage.c` implements legacy cgroup local-storage map support under `CONFIG_CGROUP_BPF`. It provides shared and per-CPU cgroup storage maps keyed by cgroup ID or by `(cgroup_inode_id, attach_type)`, plus allocation, lookup, update, seq display, and link/unlink operations used when BPF programs attach to cgroups.

## Important APIs, Types, And Functions

`struct bpf_cgroup_storage_map` embeds `struct bpf_map` and adds a spinlock, rb-tree root, and ordered list of storages. `map_to_storage()` converts from generic map to cgroup storage map. `attach_type_isolated()` distinguishes the full `struct bpf_cgroup_storage_key` key mode from the plain `u64 cgroup_inode_id` mode.

Lookup and indexing use `bpf_cgroup_storage_key_cmp()`, `cgroup_storage_lookup()`, `cgroup_storage_insert()`, and `cgroup_storage_get_next_key()`. Storage objects are indexed in both an rb-tree for lookup and a list for key iteration.

Map operations include `cgroup_storage_lookup_elem()`, `cgroup_storage_update_elem()`, `bpf_percpu_cgroup_storage_copy()`, `bpf_percpu_cgroup_storage_update()`, `cgroup_storage_map_alloc()`, `cgroup_storage_map_free()`, `cgroup_storage_delete_elem()`, `cgroup_storage_check_btf()`, `cgroup_storage_seq_show_elem()`, and `cgroup_storage_map_usage()`.

Program and cgroup integration functions include `bpf_cgroup_storage_assign()`, `bpf_cgroup_storage_alloc()`, `bpf_cgroup_storage_free()`, `bpf_cgroup_storage_link()`, and `bpf_cgroup_storage_unlink()`.

The exported map ops table is `cgroup_storage_map_ops`, with BTF ID metadata for `struct bpf_cgroup_storage_map`.

## Control Flow

Map allocation validates key size, value size, map flags, NUMA node, and zero `max_entries`, then initializes the embedded map, spinlock, rb-tree, and list. Per-CPU storage caps value size at `PCPU_MIN_UNIT_SIZE`; shared storage uses the general local storage max.

Storage lookup locks the map unless the caller already holds it, walks the rb-tree by key comparison, and returns the matching `struct bpf_cgroup_storage` or NULL. Element lookup returns the shared buffer's data pointer. Shared updates either copy under `BPF_F_LOCK` or allocate a new buffer, initialize BTF fields, atomically swap `storage->buf`, and RCU-free the old buffer.

Per-CPU copy/update paths find the storage under RCU, then either copy one CPU selected via `BPF_F_CPU` or iterate all possible CPUs. Values are rounded to 8-byte units for full per-CPU dumps, avoiding kernel data leaks because per-CPU allocation is zero-filled.

When a BPF program using cgroup storage is attached, `bpf_cgroup_storage_alloc()` creates the storage for the map assigned in `prog->aux->cgroup_storage[stype]`, allocating either a shared `bpf_storage_buffer` or per-CPU buffer. `bpf_cgroup_storage_link()` sets the key from cgroup ID and attach type, inserts into the map rb-tree and map list, and links into `cgroup->bpf.storages`. Unlink removes all three relationships.

Map free takes `cgroup_lock()`, walks all storages, unlinks and frees each, validates empty indices, and frees the map memory.

## State And Persistence Behavior

Map-level state is persistent for the map lifetime: rb-tree index, list of storages, spinlock, and map metadata. Storage-level state persists while a cgroup attachment owns it and is tied to both the BPF map and the cgroup.

Shared storage values are RCU-swapped buffers. Per-CPU storage values live in per-CPU allocations. Storage objects are freed after RCU grace periods through shared or per-CPU callbacks.

Delete-by-key is not supported and returns `-EINVAL`; storage lifetime is controlled by cgroup attach/detach and map release paths rather than arbitrary map deletes.

## Dependencies And Integration Points

The file is compiled only under `CONFIG_CGROUP_BPF`. It depends on cgroup internals, `struct bpf_cgroup_storage`, BPF map allocation helpers, BTF type checking and display, spin locks, rb-trees, RCU, per-CPU allocation, and cgroup attach infrastructure.

It integrates with BPF program aux state through `bpf_cgroup_storage_assign()` and with cgroup storage lists through `cgroup->bpf.storages`.

## Risks And Edge Cases

Key shape determines isolation semantics. A map with plain `u64` keys ignores attach type, while `struct bpf_cgroup_storage_key` includes it; BTF validation must match the chosen key size or user space can see confusing failures.

Shared updates allocate a new value and swap it under RCU, so readers must stay in RCU critical sections. Per-CPU copy/update flags pack CPU IDs into upper bits; invalid CPU values or flag combinations should be caught by map syscall validation and these helpers.

Map memory accounting reports only the map object and explicitly does not count dynamically allocated storage elements, which can understate memory usage.

Lock ordering between map spinlock, cgroup lock, and RCU must remain consistent. Link/unlink touches rb-tree, map list, and cgroup list under the map lock.

## Test Signals

Tests should cover shared and per-CPU cgroup storage maps, both key formats, BTF key validation, `BPF_F_LOCK` updates, per-CPU `BPF_F_CPU` and all-CPU copy/update behavior, get-next-key ordering, seq_file display, attach/detach link/unlink, and map free with live storages.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/local_storage.c -->
