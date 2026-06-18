# Research Group: subset-b-006018

This grouped report covers the requested BPF subsystem sources under `sources/distributed-fs/ceph-client/kernel/bpf/`. Each source file section is delimited for downstream reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/syscall.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/sysfs_btf.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/sysfs_btf.c

## Purpose

`sysfs_btf.c` exposes the built-in kernel BTF blob as `/sys/kernel/btf/vmlinux`. This gives user-space BPF tooling a stable way to read or mmap the kernel's BTF metadata for CO-RE relocation, introspection, and verifier-facing type discovery.

## Important APIs, Types, And Functions

- Linker symbols `__start_BTF` and `__stop_BTF` delimit the vmlinux BTF section generated during kernel link.
- `bin_attr_btf_vmlinux` is a read-only sysfs binary attribute named `vmlinux`.
- `btf_sysfs_vmlinux_mmap()` validates mmap requests and maps the physical pages backing the BTF blob with `remap_pfn_range()`.
- `btf_kobj` is the exported `struct kobject *` for `/sys/kernel/btf`.
- `btf_vmlinux_init()` sets the binary attribute private pointer and size, creates the `btf` kobject under `kernel_kobj`, and registers the binary file at `subsys_initcall` time.

## Control Flow

Initialization computes `size = __stop_BTF - __start_BTF`. If the BTF section is empty, it returns successfully without creating sysfs state. Otherwise it creates `/sys/kernel/btf` and registers `vmlinux` with `sysfs_create_bin_file()`. Reads use `sysfs_bin_attr_simple_read`.

The mmap path only accepts requests against the original BTF start pointer, offset zero, non-writable, non-executable, non-`VM_MAYSHARE` VMAs, and sizes no larger than the page-aligned BTF region. It marks the VMA `VM_DONTDUMP`, strips may-write/may-exec, and remaps the BTF physical PFNs read-only.

## State And Persistence Behavior

The BTF bytes are static kernel image data. The sysfs kobject and binary attribute persist after init for the lifetime of the kernel. No dynamic allocation beyond the kobject registration is maintained by this file.

## Dependencies And Integration Points

The file depends on linker-provided BTF section symbols, sysfs/kobject infrastructure, memory-management helpers, and the BTF build pipeline described by `scripts/link-vmlinux.sh`. It complements `syscall.c` BTF FD and info APIs by exposing the vmlinux BTF blob directly through sysfs.

## Risks And Edge Cases

The mmap path is intentionally strict. Incorrect page alignment of `__start_BTF`, integer wrap in `pfn + pages`, nonzero offsets, or overly large mappings return errors. Permission checks prevent writable or executable mappings of kernel metadata. If the BTF section is absent, tooling must handle the missing sysfs file.

## Test Signals

Useful checks include booting with BTF enabled and verifying `/sys/kernel/btf/vmlinux` exists and is non-empty, comparing file size to the BTF section size, reading the blob with bpftool/libbpf, mmaping read-only offset-zero ranges, and verifying writable/executable/nonzero-offset/oversized mmap attempts fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/sysfs_btf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/task_iter.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/task_iter.c

## Purpose

`task_iter.c` implements BPF iterator targets for tasks, task files, and task VMAs, plus kfunc iterator objects for task lists, cgroup tasks, and per-VMA traversal. These APIs let BPF programs walk kernel task-related state through `seq_file`-backed BPF iterators or verifier-recognized kfunc iterator patterns.

## Important APIs, Types, And Functions

- Seq iterator private state: `bpf_iter_seq_task_common`, `bpf_iter_seq_task_info`, `bpf_iter_seq_task_file_info`, and `bpf_iter_seq_task_vma_info`.
- Task traversal: `task_seq_get_next()` handles all tasks, one TID, or one thread group; `task_group_seq_get_next()` walks threads in a TGID.
- Seq targets: `task_seq_ops`, `task_file_seq_ops`, and `task_vma_seq_ops` run BPF iterator programs with contexts `bpf_iter__task`, `bpf_iter__task_file`, and `bpf_iter__task_vma`.
- Attach parsing: `bpf_iter_attach_task()` accepts at most one of `tid`, `pid`, or `pid_fd` and records iterator type/pid in aux info.
- Registration metadata: `task_reg_info`, `task_file_reg_info`, and `task_vma_reg_info` declare target names, BTF context argument IDs, resched support, seq private sizes, fdinfo, and link-info fill behavior.
- VMA helper: `bpf_find_vma()` invokes a BPF callback for a task VMA containing a requested address under a trylocked mmap read lock.
- Kfunc iterators: `bpf_iter_task_vma_new/next/destroy()`, `bpf_iter_css_task_new/next/destroy()`, and `bpf_iter_task_new/next/destroy()` expose verifier-managed iteration objects.
- Init: `task_iter_init()` initializes per-CPU mmap unlock irq work, fills BTF IDs, and registers the three seq iterator targets.

## Control Flow

For seq iterators, `BPF_ITER_CREATE` opens a link-backed iterator FD through the generic iterator layer. The seq start/next callbacks call task/file/VMA find functions, store enough cursor state to resume after user-space reads, and pass the current kernel object to `bpf_iter_run_prog()`. Stop callbacks either emit the final in-stop event or release held task/file/mm/mmap-lock references.

Task-file iteration walks each selected task while skipping threads that share file tables when requested, then uses `fget_task_next()` to acquire each file. Task-VMA iteration obtains an mm with `get_task_mm()`, takes `mmap_read_lock_killable()`, finds VMAs, and drops/reacquires the lock when contended, using previous VMA boundaries to avoid duplicating or skipping ranges after relock.

The VMA kfunc iterator is separate from seq iteration. It allocates opaque kernel data from `bpf_global_ma`, safely grabs a task and mm reference with `spin_trylock(&task->alloc_lock)`, locates VMAs through an RCU maple-tree walk followed by `lock_vma_under_rcu()`, returns a snapshot copy, and releases `vm_file`, task, and mm state in destroy.

## State And Persistence Behavior

Seq iterator state persists per open iterator file in seq private memory. It stores pid namespace references, task type/pid cursors, current task/file/fd, current mm/VMA, and previous VMA range. References are acquired only while needed and released on stop/next/fini. Kfunc iterator state is explicit BPF-side opaque storage backed by kernel allocations or embedded cursor fields and must be destroyed by the BPF program.

`DEFINE_PER_CPU(struct mmap_unlock_irq_work, mmap_unlock_work)` supports deferred mmap unlock mechanics used by `bpf_find_vma()` and initialized once at late init.

## Dependencies And Integration Points

The file integrates with the BPF iterator core, BTF ID infrastructure, pid namespaces, pidfd lookup, task and file reference helpers, mm/VMA locking, maple tree VMA iteration, cgroup task iterators, BPF memory allocator, and `mmap_unlock_work.h`. `syscall.c` reaches these targets through tracing program attach and iterator FD creation.

## Risks And Edge Cases

Reference and lock balance is the main risk. Seq stop paths must drop `task_struct`, `file`, `mm_struct`, and mmap locks exactly once, including final stop callbacks. VMA iteration must tolerate concurrent VMA mutation, lock contention, task exit, kernel threads with no mm, and user-space reads that split output buffers. The kfunc VMA iterator rejects IRQ-disabled contexts to avoid deadlocks and can return `-EBUSY` if it cannot safely lock task/mm state.

Iterator filtering also has correctness edges: only one of `tid`, `pid`, and `pid_fd` is allowed; TGID iteration must avoid duplicate shared files; pid namespace translation is captured at iterator creation.

## Test Signals

High-value tests include BPF iterator selftests for `task`, `task_file`, and `task_vma` over all tasks, one TID, one TGID, and pidfd selection; tests that force small seq read buffers to exercise resume paths; task exit during iteration; threads sharing files; VMA churn and mmap lock contention; `bpf_find_vma()` success, miss, invalid flags, no-mm, and busy paths; and verifier/kfunc tests requiring new/next/destroy pairing for task, css-task, and VMA iterators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/task_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/tcx.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/tcx.c

## Purpose

`tcx.c` implements BPF TCX attach, detach, query, and bpf_link support for ingress and egress classifier programs on net devices. It is the syscall/link-facing glue between generic multi-program BPF attachment infrastructure and TCX per-device hook storage.

## Important APIs, Types, And Functions

- Legacy attach path: `tcx_prog_attach()`, `tcx_prog_detach()`, and `tcx_prog_query()` serve `BPF_PROG_ATTACH`, `BPF_PROG_DETACH`, and `BPF_PROG_QUERY`.
- Device cleanup: `tcx_uninstall()` removes all TCX programs/links from one net-device direction during netdevice teardown.
- Link attach path: `tcx_link_attach()` allocates a `struct tcx_link`, primes a generic `bpf_link`, attaches it to the TCX mprog entry, and settles the link FD.
- Link ops: `tcx_link_release()`, `tcx_link_detach()`, `tcx_link_update()`, `tcx_link_dealloc()`, `tcx_link_fdinfo()`, and `tcx_link_fill_info()`.
- TCX helpers from `net/tcx.h`: `tcx_entry_fetch_or_create()`, `tcx_entry_fetch()`, `tcx_entry_update()`, `tcx_entry_sync()`, `tcx_entry_free()`, `tcx_entry_is_active()`, `tcx_skeys_inc()`, and `tcx_skeys_dec()`.
- Multi-program helpers: `bpf_mprog_attach()`, `bpf_mprog_detach()`, `bpf_mprog_commit()`, `bpf_mprog_clear_all()`, `bpf_mprog_query()`, and tuple iteration.

## Control Flow

All public operations take `rtnl_lock()` and look up the target net device by `target_ifindex` in the caller's network namespace. Attach optionally resolves a replacement program if `BPF_F_REPLACE` is set, fetches or creates the ingress/egress TCX entry, and delegates ordering/revision/relative-FD semantics to `bpf_mprog_attach()`. If a new entry object is returned, the device pointer is updated, TCX static keys are incremented, and the mprog transaction is committed. Errors free a newly-created empty entry.

Detach fetches the current entry and calls `bpf_mprog_detach()`. If the resulting entry is inactive it updates the device direction to `NULL`, syncs, decrements static keys, commits, and frees the old entry. Query is a locked lookup followed by `bpf_mprog_query()`.

`tcx_link_attach()` creates a persistent link around the same mprog attach operation. Link release detaches the link-owned program. Link update replaces the program in-place with `BPF_F_REPLACE | BPF_F_ID`, swaps `link->prog` on success, and drops the old program ref.

`tcx_uninstall()` clears all programs for a direction during device teardown, sets link `dev` pointers to `NULL` so future release/update reports a dead link, drops program refs for non-link tuples, and decrements static keys per tuple.

## State And Persistence Behavior

TCX state lives on `struct net_device` through ingress/egress mprog entries. Entries hold ordered programs and/or links plus revision state managed by the generic mprog layer. `struct tcx_link` stores the generic `bpf_link` and a raw `net_device *` that is valid only while protected by RTNL and cleared by uninstall. TCX static keys track active ingress/egress hooks and are incremented/decremented when entries become active or inactive.

## Dependencies And Integration Points

`syscall.c` dispatches SCHED_CLS programs with `BPF_TCX_INGRESS` or `BPF_TCX_EGRESS` to this file for both legacy attach and `BPF_LINK_CREATE`. The implementation depends on netdevice lookup, RTNL locking, generic bpf_link lifecycle, generic bpf_mprog ordered attachment semantics, and TCX hook update/sync helpers.

## Risks And Edge Cases

RTNL locking must cover device lookup, entry replacement, and link `dev` access. Replacement paths must put the replacement program on all exits. Static key accounting must match entry activation and uninstall behavior; missed decrements would leave hooks enabled, while extra decrements could disable live hooks. `tcx_uninstall()` must handle both link-backed and prog-backed tuples without double-putting link programs. Link update must reject stale `old_prog` and dead-device cases.

## Test Signals

Tests should cover ingress and egress attach/detach/query, link attach/release/detach/update, relative ordering flags, expected revision mismatch, replacement by ID, device-not-found errors, device teardown while links are alive, fdinfo/link-info ifindex reporting before and after teardown, and concurrent attach/detach serialized by RTNL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/tcx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/tnum.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/tnum.c

## Purpose

`tnum.c` implements tracked-number arithmetic used by the BPF verifier to represent partially-known integer values. A `struct tnum` stores known bits in `value` and unknown bits in `mask`; operations return conservative tnums that cover every concrete result possible from the operands.

## Important APIs, Types, And Functions

- Constructors: `tnum_const()`, `tnum_range()`, and global `tnum_unknown`.
- Bit shifts and arithmetic: `tnum_lshift()`, `tnum_rshift()`, `tnum_arshift()`, `tnum_add()`, `tnum_sub()`, `tnum_neg()`, and `tnum_mul()`.
- Bitwise operations: `tnum_and()`, `tnum_or()`, `tnum_xor()`, `tnum_bswap16()`, `tnum_bswap32()`, and `tnum_bswap64()`.
- Set-like operations: `tnum_overlap()`, `tnum_intersect()`, `tnum_union()`, `tnum_in()`, and `tnum_step()`.
- Size/subregister helpers: `tnum_cast()`, `tnum_subreg()`, `tnum_clear_subreg()`, `tnum_with_subreg()`, and `tnum_const_subreg()`.
- Diagnostics and constraints: `tnum_is_aligned()` and `tnum_sbin()`.

## Control Flow

Most operations are pure functions that combine input `value` and `mask` bit patterns. Arithmetic uses carry/borrow-aware formulas to expand uncertainty when unknown input bits can affect known output bits. Multiplication performs long multiplication over the uncertain multiplier, unioning accumulator states when a multiplier bit is unknown. `tnum_range()` computes a common prefix and unknown suffix covering a min/max interval.

`tnum_step()` is a compact enumeration helper: given a tnum and a current value `z`, it returns the smallest concrete member of the tnum greater than `z`, clamping to min or max when outside the range. It increments within the tnum mask by filling non-mask positions to propagate carry through gaps.

## State And Persistence Behavior

There is no mutable persistent state. All functions operate by value and return a new `struct tnum`. The only global is the immutable all-unknown `tnum_unknown`.

## Dependencies And Integration Points

The file depends on `linux/tnum.h`, basic kernel bit helpers such as `fls64()`, and byte-swap helpers. The primary integration point is verifier scalar range/value tracking; tnums are used to reason about pointer offsets, register values, alignment, subregister writes, and safety constraints.

## Risks And Edge Cases

Correctness requires over-approximation. Under-approximating any operation can make the verifier accept unsafe programs; excessive over-approximation can reject valid programs. Important edge cases include full-width ranges where `1ULL << 64` would be undefined, arithmetic right shifts with 32-bit versus 64-bit signed interpretation, multiplication with unknown bits, casts where `size * 8` reaches the supported width, and `tnum_step()` carry behavior when `d & ~mask` is zero or high-bit-sensitive.

## Test Signals

Useful tests include verifier selftests for scalar arithmetic, subregister behavior, alignment, bounds propagation, and branch pruning. Unit-style tests should compare tnum operation results against exhaustive concrete sets for small bit widths, check range extremes including `0..U64_MAX`, validate byte swaps and casts, and verify `tnum_step()` enumerates members monotonically without skipping valid values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/tnum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/token.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/token.c

## Purpose

`token.c` implements BPF token objects, which delegate a bounded subset of BPF capabilities from a bpffs mount's user namespace to token holders. Tokens let user namespaces expose selected BPF commands, map types, program types, and attach types without granting broad global privileges.

## Important APIs, Types, And Functions

- Capability checks: `bpf_token_capable()` applies namespace capability checks and LSM token capability policy; `bpf_ns_capable()` allows `CAP_SYS_ADMIN` to satisfy non-admin capability checks in the token namespace.
- Lifetime: `bpf_token_inc()`, `bpf_token_put()`, deferred `bpf_token_put_deferred()`, `bpf_token_free()`, and `bpf_token_release()`.
- FD interface: `bpf_token_fops` supports release and fdinfo display through `bpf_token_show_fdinfo()`.
- Creation: `bpf_token_create()` validates a bpffs root FD, namespace ownership, `CAP_BPF`, non-init user namespace, delegation mount options, LSM policy, pseudo inode/file creation, and token initialization.
- Introspection and lookup: `bpf_token_get_info_by_fd()` and `bpf_token_get_from_fd()`.
- Delegation filters: `bpf_token_allow_cmd()`, `bpf_token_allow_map_type()`, and `bpf_token_allow_prog_type()`.

## Control Flow

Token creation receives a bpffs FD from `BPF_TOKEN_CREATE`. It verifies the FD refers to the bpffs mount root, checks access permissions, requires the current user namespace to match the bpffs superblock namespace, requires `CAP_BPF` in that namespace, rejects init-user-namespace creation, and requires at least one delegation mask in bpffs mount options. It then creates an unlinked pseudo inode/file, allocates a token, copies delegation masks from mount options, calls `security_bpf_token_create()`, takes a user namespace ref, stores the token in file private data, and publishes the FD.

Consumers get a token via `bpf_token_get_from_fd()`, verify the file ops, increment the token refcount, and then use `bpf_token_allow_*()` plus `bpf_token_capable()` in syscall paths. If a token does not grant a command/type, callers generally drop it and fall back to ambient task capabilities.

## State And Persistence Behavior

A token stores an atomic refcount, deferred free work item, owning user namespace, and four 64-bit allow masks: commands, map types, program types, and attach types. The token persists while its FD or any temporarily acquired references exist. Final release is deferred to a workqueue, where LSM cleanup, user namespace put, and memory free occur.

## Dependencies And Integration Points

The file integrates with bpffs superblock/mount options, user namespaces, capability checks, LSM hooks (`security_bpf_token_*`), pseudo inode/file allocation, fd helpers, and `syscall.c` command paths for map create, program load, BTF load/get, and token info. bpffs mount options are the persistent policy source; token FDs are the transport.

## Risks And Edge Cases

The security boundary depends on strict bpffs-root and namespace checks. Allowing token creation from nested paths, mismatched namespaces, or init user namespace would weaken delegation semantics. Mask sizes are capped by build-time checks in fdinfo; new BPF enum values beyond 63 require rethinking mask representation. Deferred freeing must avoid use-after-free while syscall paths hold temporary references. LSM denial must consistently override namespace capability success.

## Test Signals

Tests should cover token creation success from a delegated bpffs mount in a non-init user namespace, failure from non-root bpffs dentries, non-bpffs FDs, no delegation masks, init user namespace, missing `CAP_BPF`, and mismatched user namespaces. Operation tests should verify allowed and denied command/map/prog/attach masks, fdinfo and `BPF_OBJ_GET_INFO_BY_FD` output, refcounting across close and concurrent use, and LSM hook denial paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/token.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/trampoline.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/trampoline.c

## Purpose

`trampoline.c` manages BPF trampolines used by fentry, fexit, fmod_ret, fsession, LSM, and freplace programs. It maps attach targets to generated executable trampoline images, patches kernel call sites through ftrace direct calls or architecture text pokes, tracks attached programs, and provides enter/exit routines for recursion, RCU, migration, sleepable execution, and runtime statistics.

## Important APIs, Types, And Functions

- Registries and locking: `trampoline_key_table`, `trampoline_ip_table`, and `trampoline_mutex` map trampoline keys and IPs to `struct bpf_trampoline`; each trampoline also has `tr->mutex`.
- Capability check: `bpf_prog_has_trampoline()` identifies tracing/LSM program attach types that use trampolines.
- Image symbols: `bpf_image_ksym_init()`, `bpf_image_ksym_add()`, and `bpf_image_ksym_del()` publish trampoline images to BPF kallsyms and perf ksymbol events.
- Ftrace/direct ops: `direct_ops_alloc/free/add/del/mod()`, `bpf_tramp_ftrace_ops_func()`, `register_fentry()`, `modify_fentry()`, and `unregister_fentry()` abstract config-specific call-site patching.
- Lookup and lifecycle: `bpf_trampoline_lookup()`, `bpf_trampoline_get()`, and `bpf_trampoline_put()`.
- Image lifecycle: `bpf_tramp_image_alloc()`, `bpf_tramp_image_put()`, and RCU/percpu-ref callbacks free generated executable code after readers are gone.
- Program attach: `bpf_trampoline_link_prog()`, `__bpf_trampoline_link_prog()`, `bpf_trampoline_unlink_prog()`, and `bpf_attach_type_to_tramp()`.
- Cgroup LSM shim support: `bpf_trampoline_link_cgroup_shim()` and `bpf_trampoline_unlink_cgroup_shim()`.
- Runtime hooks: `bpf_trampoline_enter()`, `bpf_trampoline_exit()`, `__bpf_prog_enter*()`, `__bpf_prog_exit*()`, `__bpf_tramp_enter()`, and `__bpf_tramp_exit()`.
- Weak arch hooks: `arch_prepare_bpf_trampoline()`, `arch_alloc_bpf_trampoline()`, `arch_free_bpf_trampoline()`, `arch_protect_bpf_trampoline()`, and `arch_bpf_trampoline_size()`.

## Control Flow

`bpf_trampoline_get()` obtains or creates a trampoline by key and target IP, initializes the function model/address from attach-target metadata, and returns a refcounted object. Linking a program classifies it as fentry, fexit, modify-return, fsession, LSM modify-return/fexit, or freplace. Freplace is exclusive: it rejects existing fentry/fexit users, marks the target program extended, and patches the target directly to jump to the replacement. Other kinds are inserted into per-kind hlist arrays and trigger `bpf_trampoline_update()`.

`bpf_trampoline_update()` snapshots attached links, derives flags for call-original, restore-registers, skip-frame, IP-argument, shared IPMODIFY, and tail-call context, asks the architecture for image size, allocates executable memory, prepares and protects the trampoline image, and then registers or modifies the call site. When replacing an old image, it publishes the new one first and retires the old one through `bpf_tramp_image_put()`.

Image retirement is multi-stage. Trampolines that call the original function patch their epilogue path to avoid fexit execution, wait for Tasks RCU and/or percpu refs around original-function execution, then free through workqueue and RCU. Fentry-only images use RCU Tasks Trace and Tasks RCU to cover sleepable and non-sleepable code regions.

Runtime enter/exit functions are selected based on program sleepability, recursion tracking, and LSM cgroup shim status. They set BPF run context, acquire the right RCU flavor, disable migration where needed, update stats under the static key, and restore state on exit.

## State And Persistence Behavior

Each trampoline persists while refcounted by attached links or lookup users. It stores target key/IP/function model, current image, flags, direct ftrace ops, extension program, per-kind attached link lists, and counts. Generated images persist separately until all possible executing contexts have passed the required grace periods. Freplace marks target program aux state (`is_extended`) while active.

## Dependencies And Integration Points

This file is used by tracing and extension attach paths in `syscall.c`. It integrates with ftrace direct-call APIs, architecture BPF trampoline generation, BTF attach target models, BPF verifier attach checks, JIT executable memory accounting, BPF kallsyms, perf ksymbol events, RCU/RCU Tasks/RCU Tasks Trace, percpu refs, static calls/ftrace IPMODIFY sharing, BPF LSM cgroup shims, and BPF runtime stats.

## Risks And Edge Cases

The main risks are live-code patching races, incompatible ftrace IPMODIFY sharing, stale executable images, and exclusivity violations between freplace and fentry/fexit. Lock ordering is subtle: normal order is trampoline mutex before ftrace direct mutex before ftrace lock, but ftrace callbacks sometimes require trylocking to avoid deadlock. Grace-period selection must match whether trampoline code can sleep, call original functions, or execute fexit/fmod_ret sections. Architecture weak defaults return `-ENOTSUPP`; each supported architecture must implement size, prepare, allocation/protection, and text-poke semantics correctly.

## Test Signals

Tests should cover fentry, fexit, fmod_ret, fsession, LSM, and freplace attachment and detachment; freplace rejection when target programs are tail-call entries or already have fentry/fexit; concurrent attach/detach/update under ftrace direct-call configs; sleepable tracing programs; runtime stats; recursion miss accounting; cgroup LSM shim reuse and release; module target lifetime; and architecture-specific trampoline image bounds and cleanup under stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/trampoline.c -->
