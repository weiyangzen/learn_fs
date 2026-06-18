# sources/distributed-fs/ceph-client/kernel/bpf/syscall.c

## Purpose

`syscall.c` is the central implementation of the `bpf(2)` syscall and a large amount of user-visible BPF object lifecycle plumbing. It validates `union bpf_attr`, dispatches all supported BPF commands, allocates and exposes maps, programs, links, BTF objects, tokens, runtime-stat handles, and iterator FDs, and bridges those objects into subsystems such as cgroups, tracing, perf events, TCX/netkit, sockmaps, netns BPF, bpffs, LSM, and offload drivers.

The file is intentionally broad: it provides the policy and object-management layer while delegating type-specific behavior to map ops, program ops, link ops, verifier helpers, BTF helpers, and network/tracing subsystems.

## Important APIs, Types, And Functions

- Global registries: `prog_idr`, `map_idr`, and `link_idr` publish BPF programs, maps, and links by numeric ID under spinlocks. `sysctl_unprivileged_bpf_disabled` controls unprivileged BPF creation policy.
- Syscall validation: `bpf_check_uarg_tail_zero()` enforces forward-compatible zero tails for oversized `union bpf_attr`; `CHECK_ATTR()` enforces per-command unused fields.
- Map APIs: `map_create()`, `map_lookup_elem()`, `map_update_elem()`, `map_delete_elem()`, `map_get_next_key()`, `map_lookup_and_delete_elem()`, `map_freeze()`, `bpf_map_do_batch()`, and generic batch helpers implement syscall map operations.
- Map lifetime: `bpf_map_alloc_id()`, `bpf_map_free_id()`, `bpf_map_put()`, `bpf_map_put_with_uref()`, `bpf_map_new_fd()`, `bpf_map_release()`, and `bpf_map_mmap()` manage IDs, FDs, refcounts, user refs, mmap write tracking, RCU/workqueue delayed destruction, memcg association, and map-value special field cleanup.
- BTF-record handling: `map_check_btf()`, `btf_record_find()`, `btf_record_dup()`, `btf_record_equal()`, `bpf_obj_free_fields()`, `bpf_obj_pin_uptrs()`, and uptr unpin helpers validate and maintain map values containing spin locks, timers, workqueues, task work, kptrs, uptrs, list/rbtree nodes, and refcounts.
- Program APIs: `bpf_prog_load()`, `bpf_prog_load_check_attach()`, `find_prog_type()`, `bpf_prog_alloc_id()`, `bpf_prog_get()`, `bpf_prog_get_type_dev()`, `bpf_prog_get_info_by_fd()`, and `bpf_prog_test_run()` implement load, verifier entry, attach-type validation, ID/FD exposure, statistics, and introspection.
- Link APIs: `bpf_link_init()`, `bpf_link_prime()`, `bpf_link_settle()`, `bpf_link_put()`, `bpf_link_get_from_fd()`, `link_create()`, `link_update()`, `link_detach()`, and `bpf_link_get_info_by_fd()` provide generic bpf_link lifecycle and syscall operations.
- Attach dispatch: `bpf_prog_attach()`, `bpf_prog_detach()`, and `bpf_prog_query()` route legacy attach APIs to cgroup, sockmap, LIRC, flow dissector, TCX, netkit, and netns implementations.
- Tracing and perf links: `bpf_tracing_prog_attach()`, `bpf_raw_tp_link_attach()`, `bpf_perf_link_attach()`, and related link ops manage trampoline, raw tracepoint, tracepoint, kprobe, uprobe, and perf-event link metadata.
- Other command handlers: `bpf_obj_pin()`, `bpf_obj_get()`, `bpf_btf_load()`, `bpf_btf_get_fd_by_id()`, `bpf_task_fd_query()`, `bpf_enable_stats()`, `bpf_iter_create()`, `bpf_prog_bind_map()`, `token_create()`, `prog_stream_read()`, and `prog_assoc_struct_ops()`.
- Kernel/BPF helper bridge: `kern_sys_bpf()`, `bpf_sys_bpf()`, `bpf_sys_close()`, and `bpf_kallsyms_lookup_name()` expose restricted syscall-like helpers to BPF syscall programs.

## Control Flow

The user entry point is `SYSCALL_DEFINE3(bpf)`, which calls `__sys_bpf(cmd, USER_BPFPTR(uattr), size)`. `__sys_bpf()` verifies zeroed tail bytes, copies a bounded `union bpf_attr`, runs `security_bpf()`, and switches on `enum bpf_cmd`. Each command handler repeats command-specific tail-field checks and then performs capability, token, FD type, mode, flag, BTF, and subsystem validation before touching the target object.

Map creation selects `bpf_map_types[attr->map_type]`, optionally substitutes offload ops, handles `BPF_F_TOKEN_FD`, applies unprivileged and capability gates, allocates the concrete map, validates name/BTF/special fields/exclusive program hash, invokes LSM hooks, allocates a public ID, saves memcg state, and returns an anon-inode FD. Map element operations obtain the map from the FD without taking a new map ref for the file-held object, validate file mode and op flags, copy keys/values from user or kernel pointers, dispatch to offload, per-CPU, fd-array, sockmap, struct_ops, queue/stack, or generic map ops, and conditionally wait for non-sleepable program RCU readers after map-in-map changes.

Program load validates flags, token grants, global unprivileged state, instruction count, attach targets, capabilities by program class, optional signatures, device binding, license, name, and LSM state. It then calls the verifier through `bpf_check()`, publishes an ID, adds kallsyms/perf/audit notifications, and finally creates the program FD. On errors before public exposure it frees directly; after ID exposure it uses normal `bpf_prog_put()` paths.

Link creation first gets the program FD and validates attach type. It then routes by program type to cgroup links, trampoline links, iterator links, raw tracepoint links, netns links, sockmap links, XDP, TCX, netkit, netfilter, perf-event links, kprobe multi, or uprobe multi. Generic link creation uses `bpf_link_prime()` to reserve fd/file/id before attachment and `bpf_link_settle()` to publish only after attach succeeds.

The in-kernel path `kern_sys_bpf()` calls the same dispatcher for most commands through a kernel pointer wrapper, with a special `BPF_PROG_TEST_RUN` path for syscall programs that invokes `bpf_prog_run()` under sleepable recursion and runtime-stat handling.

## State And Persistence Behavior

State is mostly kernel-resident and reference-counted. IDR tables persist objects by ID until last references are dropped and ID removal runs. FD-backed anon-inodes hold references through file private data. bpffs pin/get commands persist objects through filesystem dentries outside this file. Maps hold `refcnt` and `usercnt`, a freeze bit, mmap write count, optional BTF metadata, optional object cgroup, optional owner program info, and possible special BTF value records. Programs hold aux state including ID, BTF, maps, attach target, token, load time, stats, module refs, verifier metadata, and JIT symbols. Links hold link type, program, attach type, ID, sleepable semantics, and concrete link-op private state.

Destruction is deliberately deferred. Map freeing can wait for RCU or RCU Tasks Trace and then workqueue context. Program freeing can defer through workqueue and RCU/RCU Tasks Trace depending on sleepable state and exposed JIT symbols. Links may wait for RCU, RCU Tasks Trace, or tracepoint SRCU before deallocation. Runtime stats are toggled by a static key held open by a special `bpf-stats` FD or sysctl.

## Dependencies And Integration Points

This file integrates with `linux/bpf_types.h` for map/program/link type tables, BTF parsing and object IDs, the verifier, bpffs object pin/get, LSM hooks (`security_bpf*`), audit and perf events, ftrace/trampoline code, kprobe/uprobe/perf link helpers, cgroup BPF, sockmap/sockhash, LIRC, netns BPF, TCX/netkit, XDP, netfilter, BPF tokens, memcg accounting, module refs, kallsyms visibility rules, and sysctl registration under `kernel/`.

`tcx.c`, `trampoline.c`, `task_iter.c`, `token.c`, and `sysfs_btf.c` are direct neighbors in this set: TCX attach is dispatched from here, trampoline links are created and released through here, iterators are surfaced by `BPF_ITER_CREATE` and tracing attach, token command and capability decisions are consumed during map/prog/BTF operations, and BTF sysfs complements `BPF_BTF_LOAD`/BTF info APIs.

## Risks And Edge Cases

The biggest risks are authorization gaps, lifetime bugs, and ABI regressions. Every command has distinct capability/token and flag rules, so new BPF commands or fields must update `CHECK_ATTR` last fields, token policy, LSM hooks, and info-copy paths together. Map special fields are sensitive: kptr/uptr/timer/workqueue/list/rbtree cleanup must match map update, delete, free, freeze, and mmap semantics. Link lifetime is subtle because some hooks can run after detach and require the right grace period flavor. Public ID exposure creates failure-path constraints; after publishing, cleanup must use refcounted put paths. Introspection paths must avoid leaking JIT addresses or raw instructions unless `bpf_dump_raw_ok()` permits it.

Concurrency hazards include IDR lookup/ref races, map writes concurrent with mmap/freeze, RCU-protected map/program readers, dynamic attach/detach races, fget/fput ownership, and syscall-program recursion. Batch operations must carefully update partial counts on faults. `BPF_F_TOKEN_FD` fallback behavior intentionally ignores unusable tokens and reverts to ambient capability checks, which is easy to misread.

## Test Signals

Relevant tests should cover `tools/testing/selftests/bpf` syscall, map, prog load, BTF, token, link, tracing, cgroup, TCX/netkit, iterator, perf-event, and verifier cases. High-signal checks include unknown `union bpf_attr` tail rejection, per-command flag rejection, map BTF special-field acceptance/rejection, map freeze versus writable mmap, map-in-map update synchronization, unprivileged sysctl modes, token-delegated map/prog/BTF operations, BPF object get-info truncation and address redaction, link create/update/detach by every supported attach type, public ID lookup races, batch partial-count behavior, and syscall-program helper restrictions.
