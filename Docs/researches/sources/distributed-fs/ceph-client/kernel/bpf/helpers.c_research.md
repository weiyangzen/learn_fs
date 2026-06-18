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
