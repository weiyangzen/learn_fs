# subset-b-006016 Research

Grouped source research for the Ceph-client Linux kernel BPF support files in `kernel/bpf`, covering verifier logging, trie and queue/stack maps, map-in-map metadata, iterators and preload assets, allocator/lifetime helpers, net namespace attach points, device offload, CO-RE relocation plumbing, reuseport sockets, and ring buffers. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/log.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/log.c

Purpose: implements BPF verifier logging and verifier-state pretty printing. It validates user log attributes, streams formatted verifier output either to the kernel log or to a user buffer, supports fixed and rotating log-buffer modes, finalizes truncated rotating buffers into linear strings, prints source line info from BTF, and renders register/stack/dynptr/iterator state for verifier diagnostics. The source was read as a complete 827-line file.

Important APIs/functions: `bpf_vlog_init`, `bpf_verifier_vlog`, `bpf_vlog_reset`, `bpf_vlog_finalize`, `bpf_verifier_log_write`, `bpf_log`, `verbose_linfo`, `reg_type_str`, `dynptr_type_str`, `iter_type_str`, `iter_state_str`, `tnum_strn`, `print_verifier_state`, `bpf_vlog_alignment`, and `print_insn_state`. It uses `struct bpf_verifier_log`, `struct bpf_verifier_env`, `struct bpf_reg_state`, `struct bpf_func_state`, BTF line records, verifier stack slot tags, and log-level flags such as `BPF_LOG_FIXED` and `BPF_LOG_KERNEL`.

Control flow: `bpf_vlog_init` stores syscall-supplied logging attributes and rejects inconsistent combinations. `bpf_verifier_vlog` formats into the verifier temporary kernel buffer, updates maximum length accounting, and either writes linearly in fixed mode or writes into a circular user buffer in rotating mode. User-copy failures null out `ubuf`, causing finalization to report `-EFAULT`. `bpf_vlog_reset` rewinds the logical log end during verifier backtracking and zero-terminates the current user slot. `bpf_vlog_finalize` rotates wrapped circular output back to the start of the user buffer using three in-place reversals. State printers walk active registers, stack slots, acquired refs, callback flags, and scratched-state masks, then mark state clean after differential printing.

State and persistence: all state is in the caller-owned verifier log/env; no persistent storage is written. `start_pos`, `end_pos`, and `len_max` persist across verifier passes and can outlive individual logging calls. The user log buffer is updated incrementally and finalized at syscall completion. Static string tables and `env->tmp_str_buf` are transient formatting helpers.

Dependencies/integration: integrates with the verifier core, BTF line info, `copy_to_user`/`copy_from_user`, `put_user`, `tnum`, and exported GPL symbols used by other BPF code. `verbose_linfo` depends on `bpf_find_linfo` and BTF string offsets. `print_insn_state` is tied to verifier instruction tracing and the scratch-state optimizer.

Risks and edge cases: log length arithmetic intentionally uses 64-bit positions but exposes `u32` actual size, so truncation and overflow behavior must stay exact. Rotating-buffer finalization copies each byte through user memory twice and must preserve NUL termination even after faults. `reg_type_str` uses a single temporary buffer and cannot be used twice in one format. Pretty-printer output is user-facing debugging ABI in practice; changes can break tests and developer workflows. Kernel-log mode bypasses user-buffer accounting.

Test signals: verifier selftests that assert exact log fragments, tests for short log buffers and `BPF_LOG_FIXED`, CO-RE/BTF line-info verifier-log tests, fault-injection around user buffers, and syzkaller-style coverage for unusual register/stack states and reset/finalize paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/log.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/lpm_trie.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/lpm_trie.c

Purpose: implements `BPF_MAP_TYPE_LPM_TRIE`, a no-prealloc longest-prefix-match map for byte-array keys such as IPv4/IPv6 prefixes. It stores real value nodes and synthetic intermediate nodes in an RCU-visible binary trie and returns the most specific non-intermediate prefix matching a lookup key. The source was read as a complete 789-line file.

Important APIs/functions: `trie_lookup_elem`, `trie_update_elem`, `trie_delete_elem`, `trie_get_next_key`, `trie_alloc`, `trie_free`, `trie_check_btf`, `trie_mem_usage`, and `trie_map_ops`. Important types are `struct lpm_trie`, `struct lpm_trie_node`, `struct bpf_lpm_trie_key_u8`, and flag `LPM_TREE_NODE_FLAG_IM`. Helpers include `extract_bit`, `__longest_prefix_match`, `lpm_trie_node_alloc`, and `trie_check_add_elem`.

Control flow: allocation validates `BPF_F_NO_PREALLOC`, key/value size bounds, map flags, and initializes a `bpf_mem_alloc` cache. Lookup walks from the RCU root, compares the node prefix with the key using word-sized big-endian comparisons, remembers the last real node, and descends by the next bit. Update allocates a new node before locking, walks to the insertion slot, handles empty insert, real-node replacement, intermediate-node conversion, ancestor insertion, or creation of a new intermediate splitter. Delete locks the trie, finds an exact real node, then either marks a two-child node intermediate, removes a leaf plus unnecessary intermediate parent, or promotes a single child. `get_next_key` returns keys in postorder, preferring more-specific prefixes before less-specific ones.

State and persistence: trie contents live in map memory and persist until map deletion. `n_entries` counts real entries, not intermediate nodes. Nodes are published through RCU pointers and freed through `bpf_mem_cache_free_rcu`; `trie_free` can raw-free nodes because no BPF program can still access the map. Data is stored big-endian in node `data[]`, followed by the map value.

Dependencies/integration: uses BPF map ops, BTF map IDs, generic batch operations, `bpf_mem_alloc`, RCU, `rqspinlock_t`, and map access flags. It integrates with syscall map operations and eBPF helper map access. BTF checking only requires a struct key type embedding the LPM key shape.

Risks and edge cases: prefix lengths greater than `max_prefixlen` are rejected. Empty trie, root replacement, and intermediate-node collapse are mutation hot spots. The raw res spinlock can return busy errors under resilient locking. Memory accounting reports real entries only and can understate intermediate-node memory. The best-fit traversal assumes valid big-endian key layout and key sizes matching map creation.

Test signals: BPF selftests for LPM trie insert/lookup/delete, IPv4/IPv6 longest-prefix behavior, `BPF_NOEXIST`/`BPF_EXIST` semantics, postorder `get_next_key`, invalid prefix lengths, full-map `-ENOSPC`, BTF key validation, batch ops, and concurrent lookup/update/delete stress under RCU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/lpm_trie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/map_in_map.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/map_in_map.c

Purpose: provides shared helpers for map-in-map outer maps, including cloning inner-map metadata at outer-map creation, validating later inner-map file descriptors against that metadata, and managing references when inner maps are stored or removed. The source was read as a complete 134-line file.

Important APIs/functions: `bpf_map_meta_alloc`, `bpf_map_meta_free`, `bpf_map_meta_equal`, `bpf_map_fd_get_ptr`, `bpf_map_fd_put_ptr`, and `bpf_map_fd_sys_lookup_elem`. It uses `struct bpf_map`, BTF records, BTF refs, array map metadata extensions, and map refcount/free-defer fields.

Control flow: `bpf_map_meta_alloc` resolves the supplied inner map FD, rejects nested map-in-map, requires the inner map to provide `map_meta_equal`, allocates either a base `struct bpf_map` clone or `struct bpf_array`-sized clone for array/percpu-array verifier needs, copies ABI-relevant attributes, duplicates the BTF record, and refs the same BTF object. `bpf_map_fd_get_ptr` resolves an inserted FD, checks it against the outer map's stored metadata, and increments the inner map reference only on match. `bpf_map_fd_put_ptr` optionally marks inner-map free deferral according to sleepable users, then drops the map ref.

State and persistence: outer maps persist a metadata-only clone in `inner_map_meta`; stored inner maps carry normal BPF map references. Metadata includes BTF record and optional array fields but no live contents. Free deferral flags persist on inner maps until normal map release observes them.

Dependencies/integration: includes `map_in_map.h`, uses `__bpf_map_get`, `bpf_map_inc`, `bpf_map_put`, `btf_record_dup/equal`, `btf_get/put`, `array_map_ops`, and `percpu_array_map_ops`. It is called by array-of-maps/hash-of-maps implementations and syscall FD lookup paths.

Risks and edge cases: BTF record duplication must keep the same BTF object because internal record fields point into BTF-owned data. Equality ignores `max_entries` in this file, relying on type-specific comparisons where needed; map type covers ops equality. Nested maps are rejected. Sleepable reference accounting affects whether one or multiple RCU grace periods are required before freeing removed inner maps.

Test signals: map-in-map selftests for valid/invalid inner FD insertion, metadata mismatches, BTF-enabled value records, array/percpu-array inner maps, nested-map rejection, reference leak checks, and sleepable-program map lifetime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/map_in_map.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/map_in_map.h -->
# sources/distributed-fs/ceph-client/kernel/bpf/map_in_map.h

Purpose: declares the map-in-map metadata and FD pointer helper API used by outer map implementations. The source was read as a complete 19-line file.

Important APIs/types: forward declares `struct file` and `struct bpf_map`; declares `bpf_map_meta_alloc`, `bpf_map_meta_free`, `bpf_map_fd_get_ptr`, `bpf_map_fd_put_ptr`, and `bpf_map_fd_sys_lookup_elem`.

Control flow: no runtime flow is defined here. The header gives outer map code a common contract for creating metadata, resolving an inner-map FD to a refcounted pointer, dropping stored pointers, and returning an inner map ID for syscall lookup.

State and persistence: the header owns no storage. It describes helpers that operate on outer-map metadata and inner-map references.

Dependencies/integration: includes `<linux/types.h>` and is included by `map_in_map.c` and map types that support inner map storage. It is part of the BPF map implementation boundary rather than a UAPI header.

Risks and edge cases: callers must pass the correct outer map and honor the `need_defer` lifetime semantics on put. Prototype drift from implementation would break multiple map types at compile time.

Test signals: compile coverage of array-of-maps/hash-of-maps and map-in-map selftests that exercise all helper paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/map_in_map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/map_iter.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/map_iter.c

Purpose: registers BPF iterator targets for iterating BPF maps and map elements, exposes fdinfo/link-info for map element iterators, and registers the `bpf_map_sum_elem_count` kfunc. The source was read as a complete 229-line file.

Important APIs/functions: `bpf_map_seq_start`, `bpf_map_seq_next`, `bpf_map_seq_show`, `bpf_map_seq_stop`, `bpf_iter_attach_map`, `bpf_iter_detach_map`, `bpf_iter_map_show_fdinfo`, `bpf_iter_map_fill_link_info`, `bpf_map_iter_init`, `bpf_map_sum_elem_count`, and the late init kfunc registration. It defines iterator contexts `struct bpf_iter__bpf_map` and uses generated `struct bpf_iter__bpf_map_elem`.

Control flow: the generic map iterator stores the current map ID in `seq->private`, gets the current or next map with a reference, runs the attached iterator BPF program in `show`, and drops refs in `next`/`stop`. The map-element iterator attach path accepts only hash, LRU hash, array, and their percpu variants, then verifies the iterator program's maximum key/value access against actual map key/value storage. Late init registers `bpf_map` and `bpf_map_elem` targets and separately registers the elem-count kfunc for all program types.

State and persistence: iterator state is per-open seq-file private data. Map refs are acquired for the current element and released as the sequence advances. Map-element links hold a user ref to the target map through `aux->map` until detach. `bpf_map_sum_elem_count` only reads per-CPU `elem_count` counters and returns zero if unavailable.

Dependencies/integration: integrates with `bpf_iter_reg_target`, BTF IDs for `struct bpf_map`, `bpf_iter_run_prog`, map registry ID iteration, map user refs, seq_file, and BTF kfunc ID registration. The preload iterator program calls the kfunc to print current element counts.

Risks and edge cases: map ID iteration races with map deletion and relies on ref acquisition helpers. Access bounds must account for percpu value expansion using `round_up(value_size, 8) * num_possible_cpus()`. `stop` runs the iterator program with a NULL map on end, so iterator programs must tolerate NULL context pointers.

Test signals: BPF iterator selftests for map iteration, map element iterator access bounds, fdinfo/link-info contents, detaching map links, percpu map values, and kfunc invocation from iterator programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/map_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/memalloc.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/memalloc.c

Purpose: implements a BPF-specific memory allocator safe in arbitrary BPF execution contexts, including IRQ-disabled and NMI contexts. It fronts kmalloc/percpu allocation with per-CPU caches, asynchronous irq_work refill/trim, memcg accounting, and RCU/RCU-tasks-trace delayed freeing for objects visible to BPF programs. The source was read as a complete 1039-line file.

Important APIs/functions: `bpf_mem_alloc_init`, `bpf_mem_alloc_percpu_init`, `bpf_mem_alloc_percpu_unit_init`, `bpf_mem_alloc_destroy`, `bpf_mem_alloc`, `bpf_mem_free`, `bpf_mem_free_rcu`, `bpf_mem_cache_alloc`, `bpf_mem_cache_free`, `bpf_mem_cache_free_rcu`, `bpf_mem_cache_raw_free`, `bpf_mem_cache_alloc_flags`, `bpf_mem_alloc_check_size`, and `bpf_mem_alloc_set_dtor`. Core internal helpers include `unit_alloc`, `unit_free`, `unit_free_rcu`, `alloc_bulk`, `free_bulk`, `check_free_by_rcu`, `do_call_rcu_ttrace`, and cache drain/destroy routines.

Control flow: initialization creates either one fixed-size per-CPU cache or an array of 11 kmalloc-like buckets, sets watermarks, captures memcg if enabled, and pre-fills a small number of objects. Allocation disables IRQs, increments a per-CPU `active` guard, pops from the current CPU free list, records the originating cache in the hidden header, and queues irq_work when below the low watermark. Freeing adds the object to the current CPU cache or an atomic extra list if interrupted by another allocator path, then queues trimming if above the high watermark. RCU freeing first waits for regular RCU when needed, then always routes to RCU Tasks Trace before final reuse/free. Destroy marks caches draining, syncs irq_work, drains all lists, waits for pending callbacks if necessary, and frees per-CPU cache metadata.

State and persistence: cache state is per-CPU and persists for the owning `struct bpf_mem_alloc` lifetime. Each object has hidden `llist_node`/cache metadata before the returned pointer. Objects can temporarily live in normal free lists, extra free lists, RCU pending lists, or tasks-trace pending lists. Destructors and destructor context are stored in the allocator and invoked on final free.

Dependencies/integration: uses `llist`, `irq_work`, `local_t`, `call_rcu_hurry`, `call_rcu_tasks_trace`, memcg object charging, percpu allocation, and BPF map/kptr/dynptr users. `notrace` annotations prevent recursive BPF attachment from corrupting allocator lists. Several maps in this subset use `bpf_mem_alloc` for lockless/RCU-safe element lifetime.

Risks and edge cases: allocator correctness depends on IRQ disabling plus `active` counters for list mutation, especially under NMI BPF programs. Destroy must not free destructor context before late callbacks finish. Percpu and non-percpu objects have different hidden header layouts. Size checks cap dynamic allocations at 4096 bytes including overhead. Refilling with `GFP_NOWAIT` can fail; callers must handle NULL. Incorrect RCU flavor selection can cause use-after-free in sleepable programs.

Test signals: BPF hash/trie map stress tests, kptr/dynptr allocator tests, sleepable program lifetime tests, memcg accounting tests, fault injection for allocation failure, KASAN/KCSAN/lockdep, RT-kernel coverage for IRQ/preemption behavior, and leak warnings from `check_leaked_objs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/memalloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/mmap_unlock_work.h -->
# sources/distributed-fs/ceph-client/kernel/bpf/mmap_unlock_work.h

Purpose: provides a small helper abstraction for deferring `mmap_read_unlock()` from IRQ-disabled BPF lookup paths into `irq_work` when directly unlocking the mmap semaphore could deadlock. The source was read as a complete 65-line file.

Important APIs/types: `struct mmap_unlock_irq_work`, per-CPU declaration `mmap_unlock_work`, `bpf_mmap_unlock_get_irq_work`, and `bpf_mmap_unlock_mm`.

Control flow: callers ask `bpf_mmap_unlock_get_irq_work` whether the current context requires deferred unlock. In IRQ-disabled non-RT context it returns the current CPU work item unless that work is already busy; in PREEMPT_RT it forces fallback because trying the mmap semaphore in IRQ-disabled context is not allowed. `bpf_mmap_unlock_mm` either unlocks immediately or records the mm, releases lockdep ownership, and queues irq_work to perform the actual unlock later.

State and persistence: uses one per-CPU work object, so only one deferred mmap unlock per CPU can be outstanding. The `mm` pointer is transient until the queued work runs.

Dependencies/integration: depends on `irq_work`, `mm_struct`, `mmap_read_unlock`, lockdep `rwsem_release`, IRQ state helpers, and PREEMPT_RT configuration. It is included by BPF memory/VMA lookup code that can run with IRQs disabled.

Risks and edge cases: if per-CPU irq_work is already busy, callers must take a fallback path or risk losing an unlock. Lockdep state is manually adjusted before the real unlock, so misuse can hide or create lockdep anomalies. PREEMPT_RT behavior intentionally differs.

Test signals: BPF helpers that inspect user memory/VMA under IRQ-disabled contexts, PREEMPT_RT build/runtime coverage, lockdep runs, and stress that forces concurrent per-CPU deferred unlock attempts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/mmap_unlock_work.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/mprog.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/mprog.c

Purpose: implements generic multi-program attach/detach/query operations for BPF attach points that maintain ordered arrays of programs and optional links. It supports positional insertion before/after existing programs, replacement, deletion from exact/front/back positions, and revision-based stale-update detection. The source was read as a complete 452-line file.

Important APIs/functions: `bpf_mprog_attach`, `bpf_mprog_detach`, `bpf_mprog_query`, plus internal `bpf_mprog_link`, `bpf_mprog_prog`, `bpf_mprog_tuple_relative`, `bpf_mprog_replace`, `bpf_mprog_insert`, `bpf_mprog_delete`, `bpf_mprog_pos_exact`, `bpf_mprog_pos_before`, `bpf_mprog_pos_after`, and `bpf_mprog_fetch`. Important types are `struct bpf_mprog_entry`, `struct bpf_mprog_fp`, `struct bpf_mprog_cp`, and `struct bpf_tuple`.

Control flow: relative arguments are converted from an ID or FD into a tuple containing a refcounted link or program. Attach first checks revision, duplicate program insertion, replacement target, max capacity, and before/after constraints; if all selected rules agree on one index, it either writes in place for replacement or copies to the peer entry, grows the peer, inserts the tuple, and increments revision/count. Detach similarly resolves optional relative tuple and exact target, fetches the program/link at the final index, rejects deleting link-owned programs from non-link paths, then copies/shrinks the peer and marks the removed tuple for later release. Query copies revision, count, program IDs, and optional link IDs to user memory.

State and persistence: the attach point stores ordered `bpf_mprog_entry` arrays. Mutations use a peer/double-buffer style so readers can continue using the old entry until the owner publishes `entry_new`. Program/link references acquired for relative lookups are released before return. Removed tuples are marked for release through the mprog infrastructure rather than freed inline.

Dependencies/integration: relies on helpers from `<linux/bpf_mprog.h>`, BPF link/prog ID and FD lookup APIs, user-copy helpers, and attach-point-specific locking/publishing outside this file. It is a shared engine for BPF subsystems that support multiple ordered programs.

Risks and edge cases: before/after/replacement flags can produce conflicting positions and must fail with `-ERANGE`/specific lookup errors. Revision mismatches return `-ESTALE`. Link/program tuple matching returns `-EBUSY` when the same program is present under a different link ownership. Query truncation returns `-ENOSPC` after copying as much as requested. Capacity is capped by `bpf_mprog_max()`.

Test signals: attach-point selftests for ordered multi-attach, before/after by FD and ID, replacement, deletion of first/last/exact entries, link-owned deletion rejection, stale revision, duplicate attach, query truncation, and mixed link/program arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/mprog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/net_namespace.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/net_namespace.c

Purpose: manages BPF programs and BPF links attached to network namespaces for attach types such as flow dissector and socket lookup. It maintains per-netns run arrays, direct program attaches, link-based attaches, auto-detach during namespace teardown, link update/fdinfo/info operations, and attach-type static-branch accounting. The source was read as a complete 565-line file.

Important APIs/functions: `netns_bpf_prog_query`, `netns_bpf_prog_attach`, `netns_bpf_prog_detach`, `netns_bpf_link_create`, `bpf_netns_link_release`, `bpf_netns_link_update_prog`, `bpf_netns_link_fill_info`, `netns_bpf_pernet_init`, `netns_bpf_pernet_pre_exit`, and `netns_bpf_init`. Important types are `struct bpf_netns_link`, `struct netns_bpf`, `struct bpf_prog_array`, and enum `netns_bpf_attach_type`.

Control flow: direct program attach only targets the current netns, rejects link coexistence, validates attach-specific rules, and installs or updates a one-entry run array. Direct detach rejects link-owned attach points and removes the run array if the expected old program matches. Link create resolves target netns FD, allocates and primes a `BPF_LINK_TYPE_NETNS`, then attaches it by checking max program count, direct-attach incompatibility, attach-specific validation, run-array reallocation, and list insertion. Link release removes the link from the list, decrements static-branch need for the attach type, rebuilds or clears the run array, and clears the link's `net` pointer. Pernet pre-exit clears run arrays, marks links auto-detached, and drops direct programs.

State and persistence: per-netns BPF state stores direct programs, link lists, and RCU-published run arrays. Links deliberately do not hold a netns reference so namespace teardown auto-detaches them. `netns_bpf_mutex` serializes all updates and protects `bpf_netns_link.net`.

Dependencies/integration: integrates with `struct net`, pernet subsystem registration, `bpf_prog_array`, flow dissector attach checks, socket lookup static branch `bpf_sk_lookup_enabled`, BPF link infrastructure, namespace FD lookup, and user-copy query paths.

Risks and edge cases: direct attaches and links are mutually exclusive per attach type. Link release can race with `cleanup_net`, so `net` must be read and cleared under `netns_bpf_mutex`. Rebuilding run arrays can fail on release; safe delete fallback preserves behavior with a warning. Flow dissector supports only one program, socket lookup up to 64 links. Updating a link rejects type mismatches and auto-detached/dead netns links.

Test signals: netns BPF selftests for flow dissector and sk_lookup attach/query/detach, direct-vs-link conflict handling, namespace teardown auto-detach, link update, fdinfo/link-info netns inode fields, max program count, and static-branch enable/disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/net_namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/offload.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/offload.c

Purpose: implements BPF program and map device offload/dev-bound support. It tracks registered offload-capable netdevices, binds programs/maps to devices, delegates verifier/translation/map operations to driver `ndo_bpf`/offload ops, reports offload metadata, and cleans up or migrates offloaded objects when netdevices unregister. The source was read as a complete 866-line file.

Important APIs/functions: `bpf_prog_dev_bound_init`, `bpf_prog_dev_bound_inherit`, `bpf_prog_offload_verifier_prep`, `bpf_prog_offload_verify_insn`, `bpf_prog_offload_finalize`, `bpf_prog_offload_replace_insn`, `bpf_prog_offload_remove_insns`, `bpf_prog_dev_bound_destroy`, `bpf_prog_offload_compile`, `bpf_prog_offload_info_fill`, `bpf_map_offload_map_alloc/free`, `bpf_map_offload_lookup/update/delete/get_next_key`, `bpf_map_offload_info_fill`, `bpf_offload_dev_match`, `bpf_prog_dev_bound_match`, `bpf_offload_prog_map_match`, `bpf_offload_dev_netdev_register/unregister`, `bpf_offload_dev_create/destroy/priv`, `bpf_dev_bound_netdev_unregister`, `bpf_dev_bound_kfunc_check`, and `bpf_dev_bound_resolve_kfunc`.

Control flow: offload device registration inserts `bpf_offload_netdev` records into an rhashtable under `bpf_devs_lock`. Program creation validates type/flags/ifindex, checks `ndo_bpf`, marks whether true offload was requested, and creates a `bpf_prog_offload` record linked to the netdev. Verifier hooks call driver prepare/insn/finalize operations under a read lock. Compile replaces host execution with a warning stub and asks the device to translate. Map allocation checks CAP_SYS_ADMIN, map type, target netdev, and calls `BPF_OFFLOAD_MAP_ALLOC`; element operations delegate to driver map ops. Netdev unregister removes the hash entry, moves programs/maps to an alternate netdev on the same offload device if possible, otherwise destroys offload state and frees map IDs.

State and persistence: global `offdevs` rhashtable tracks netdev bindings. Each bound program has `prog->aux->offload`; each offloaded map has `struct bpf_offloaded_map` with netdev and driver ops. Lists of progs/maps persist on `bpf_offload_netdev` until object or device teardown. Offload info exposes device ifindex and netns device/inode plus optional jited image bytes.

Dependencies/integration: uses RTNL, `bpf_devs_lock`, rhashtable, netdevice `ndo_bpf`, XDP metadata ops, namespace path helpers, verifier offload ops, map ID management, `bpf_map_area_alloc`, and exported GPL symbols for drivers. Lock ordering explicitly forbids taking RTNL while holding `bpf_devs_lock`.

Risks and edge cases: lock ordering between RTNL, netdev ops lock, and `bpf_devs_lock` is critical. Programs requested as true offload require a real offload device, while dev-bound-only entries can create bound-only records. Device unregister may invalidate resolved kfunc pointers; attach-time matching is expected to render stale programs unusable. Host execution of device programs intentionally warns. Offloaded map dynamic memory in drivers is not counted in `map_mem_usage`.

Test signals: BPF offload driver selftests where available, netdev unregister/migration tests, verifier offload callback coverage, dev-bound XDP metadata kfunc checks, map offload syscall tests, namespace info fill tests, and lockdep/KASAN around unregister and object destroy races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/offload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/percpu_freelist.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/percpu_freelist.c

Purpose: implements a simple per-CPU freelist used by BPF maps for preallocated elements. It provides IRQ-safe public push/pop wrappers and lower-level variants for callers that already disabled IRQs. The source was read as a complete 137-line file.

Important APIs/functions: `pcpu_freelist_init`, `pcpu_freelist_destroy`, `pcpu_freelist_push`, `pcpu_freelist_pop`, `__pcpu_freelist_push`, `__pcpu_freelist_pop`, and `pcpu_freelist_populate`. Internal helpers manipulate `struct pcpu_freelist_head` and `struct pcpu_freelist_node`.

Control flow: initialization allocates one head per possible CPU, initializes resilient spinlocks, and clears heads. Populate distributes a buffer of fixed-size elements across CPU heads without locking before publication. Push first tries the current CPU list; if locking fails, it scans other possible CPUs until it can insert. Pop scans from the current CPU across possible CPUs, skips empty heads, and removes the first node from a lock it can acquire. Public wrappers disable/restore local IRQs around the lower-level operations.

State and persistence: freelist state is held in per-CPU `first` pointers protected by `rqspinlock_t`. Nodes are embedded in caller-owned preallocated elements and persist until popped or the freelist is destroyed.

Dependencies/integration: uses percpu allocation, `for_each_possible_cpu`, `for_each_cpu_wrap`, `raw_res_spin_lock`, and local IRQ control. It is included by prealloc map implementations that need low-overhead allocation without general kmalloc.

Risks and edge cases: `__pcpu_freelist_push` spins forever until some CPU list lock is acquired, so resilient spinlock behavior matters. Pop can return NULL when all lists are empty or locks are contended. Public and double-underscore variants have different IRQ preconditions. Populate assumes the buffer is not yet concurrently visible.

Test signals: preallocated hash/array map stress tests, empty/full freelist behavior, IRQ-disabled caller coverage, CPU hotplug-like possible CPU configurations, and lockdep/resilient-spinlock diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/percpu_freelist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/percpu_freelist.h -->
# sources/distributed-fs/ceph-client/kernel/bpf/percpu_freelist.h

Purpose: declares the per-CPU freelist structures and API used by BPF preallocated maps. The source was read as a complete 33-line file.

Important APIs/types: `struct pcpu_freelist_head`, `struct pcpu_freelist`, `struct pcpu_freelist_node`, `pcpu_freelist_push`, `pcpu_freelist_pop`, `__pcpu_freelist_push`, `__pcpu_freelist_pop`, `pcpu_freelist_populate`, `pcpu_freelist_init`, and `pcpu_freelist_destroy`.

Control flow: no executable flow is defined here. The comments specify that public functions perform spin_lock_irqsave-style IRQ handling while the double-underscore variants only spin-lock and require callers to have disabled IRQs.

State and persistence: the header defines the per-CPU head pointer and embedded node format but owns no storage.

Dependencies/integration: includes spinlock, percpu, and `rqspinlock` declarations. It is a private kernel BPF header consumed by the implementation and map code.

Risks and edge cases: misuse of the underscore variants without IRQ exclusion can race with public paths. Element structs must embed `pcpu_freelist_node` in compatible storage.

Test signals: compile coverage of map users and runtime freelist push/pop tests through preallocated map operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/percpu_freelist.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/preload/Kconfig -->
# sources/distributed-fs/ceph-client/kernel/bpf/preload/Kconfig

Purpose: defines Kconfig options for building the BPF preload facility that embeds kernel-specific BPF iterator programs and pins useful introspection links into bpffs. The source was read as a complete 21-line file.

Important APIs/options: `menuconfig BPF_PRELOAD` and `config BPF_PRELOAD_UMD`. `BPF_PRELOAD` depends on `BPF`, `BPF_SYSCALL`, and `!COMPILE_TEST`; `BPF_PRELOAD_UMD` is a tristate defaulting to module.

Control flow: no runtime flow. Kconfig controls whether the preload module is built and whether embedded iterator programs are available.

State and persistence: build-time configuration only. Runtime persistence comes from the module and bpffs links described in companion files.

Dependencies/integration: integrates with kernel Kconfig, BPF syscall availability, and module build rules in the preload Makefile. `!COMPILE_TEST` prevents broad allmodconfig/allyesconfig enablement.

Risks and edge cases: enabling depends on BPF syscall support and generated skeleton compatibility. Default module build means missing module load prevents bpffs debug files from appearing.

Test signals: Kconfig dependency tests, allmodconfig behavior, module build/load checks, and bpffs introspection file presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/preload/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/preload/Makefile -->
# sources/distributed-fs/ceph-client/kernel/bpf/preload/Makefile

Purpose: builds the `bpf_preload` kernel module and points its CFLAGS at the in-tree libbpf headers needed by generated lightweight skeleton code. The source was read as a complete 7-line file.

Important APIs/rules: `LIBBPF_INCLUDE = $(srctree)/tools/lib`, `obj-$(CONFIG_BPF_PRELOAD_UMD) += bpf_preload.o`, `CFLAGS_bpf_preload_kern.o += -I$(LIBBPF_INCLUDE)`, and `bpf_preload-objs += bpf_preload_kern.o`.

Control flow: no runtime flow. Kbuild compiles `bpf_preload_kern.o` into the module when `CONFIG_BPF_PRELOAD_UMD` is enabled.

State and persistence: build metadata only.

Dependencies/integration: integrates with Kbuild, the preload Kconfig, and generated skeleton headers that include libbpf internal skeleton support.

Risks and edge cases: include path drift in `tools/lib` or skeleton API changes can break module builds. The module has a single object, so generated header changes fully rebuild it.

Test signals: kernel module build with `CONFIG_BPF_PRELOAD_UMD=m/y`, include path validation, and modpost/module load checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/preload/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/preload/bpf_preload.h -->
# sources/distributed-fs/ceph-client/kernel/bpf/preload/bpf_preload.h

Purpose: defines the small kernel interface by which the preload module exposes preloaded BPF links to the core BPF filesystem machinery. The source was read as a complete 16-line file.

Important APIs/types: `struct bpf_preload_info` with `link_name` and `struct bpf_link *link`, `struct bpf_preload_ops` with `preload` callback and module owner, external `bpf_preload_ops`, and constant `BPF_PRELOAD_LINKS` set to 2.

Control flow: no executable flow. The active module installs a `bpf_preload_ops` implementation; callers invoke `preload` to obtain named links.

State and persistence: the global `bpf_preload_ops` pointer is runtime state owned by the loaded module. Returned links are persistent BPF link objects until module unload or link release.

Dependencies/integration: depends on `struct bpf_link` and module ownership. It integrates `bpf_preload_kern.c` with BPF FS link pinning/introspection code.

Risks and edge cases: `BPF_PRELOAD_LINKS` must match the module's populated link array. `link_name[16]` bounds names such as `maps.debug` and `progs.debug`; longer names would be truncated by callers using `strscpy`.

Test signals: module load/unload, preload callback returning two valid links, link names matching bpffs expectations, and safe behavior when `bpf_preload_ops` is NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/preload/bpf_preload.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/preload/bpf_preload_kern.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/preload/bpf_preload_kern.c

Purpose: kernel module implementation that loads the embedded iterator BPF skeleton, attaches map and program iterators, converts their link FDs into kernel `bpf_link` refs, and exposes them as `maps.debug` and `progs.debug` through `bpf_preload_ops`. The source was read as a complete 94-line file.

Important APIs/functions: `load_skel`, `free_links_and_skel`, `preload`, module `load`, and `fini`. Important state includes `maps_link`, `progs_link`, `skel`, and static `struct bpf_preload_ops ops`.

Control flow: `load_skel` opens the endian-specific `iterators_bpf` skeleton, loads it, attaches both iterator programs, converts skeleton link FDs to kernel links, closes the original FDs to avoid stealing init's standard descriptors, and leaves the links referenced globally. On module init, successful skeleton load publishes `bpf_preload_ops`. On module exit, the global ops pointer is cleared and links/skeleton are destroyed. The `preload` callback fills two `bpf_preload_info` entries with stable link names and link pointers.

State and persistence: `maps_link`, `progs_link`, and `skel` persist for the module lifetime. `bpf_preload_ops` is the externally visible registration pointer. No file-backed state is written by this file directly; BPF FS consumers use the exposed links.

Dependencies/integration: includes generated little- or big-endian lightweight skeleton header by compile-time byte order, uses `bpf_link_get_from_fd`, `bpf_link_put`, `close_fd`, late init/module exit, and imports `BPF_INTERNAL` namespace.

Risks and edge cases: any skeleton load/attach failure must clean up partial state. Closing skeleton FDs after taking link refs is required to avoid FD ownership side effects. `bpf_preload_ops` publication must happen only after both links are valid. Generated skeleton/API drift can break module load.

Test signals: module insertion/removal, presence and readability of `maps.debug`/`progs.debug` in bpffs, failure-injection through skeleton load/attach, fd-leak checks, and endian-specific build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/preload/bpf_preload_kern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/preload/iterators/Makefile -->
# sources/distributed-fs/ceph-client/kernel/bpf/preload/iterators/Makefile

Purpose: builds the embedded iterator BPF object and generates lightweight skeleton headers for little- and big-endian BPF targets. The source was read as a complete 67-line file.

Important APIs/rules: variables for `CLANG`, `LLC`, `LLVM_STRIP`, bpftool/libbpf paths, output directories, `all`, `big`, `clean`, `iterators.lskel-%.h`, `$(OUTPUT)/%/iterators.bpf.o`, `$(BPFOBJ)`, and `$(DEFAULT_BPFTOOL)`. The skeleton rule runs `bpftool gen skeleton -L`.

Control flow: building `all` generates the little-endian skeleton; building `big` generates the big-endian skeleton. The object rule compiles `iterators.bpf.c` with `--target=bpf -m$*`, strips debug info, and stores per-endian outputs. Libbpf and bootstrap bpftool are built from in-tree tools as prerequisites.

State and persistence: generated `.output` content and skeleton headers persist in the source/build tree until `clean` removes `.output` and `iterators`.

Dependencies/integration: depends on clang/LLVM strip, bpftool bootstrap, libbpf static archive and installed headers, tools UAPI headers, and the preload kernel module including the generated headers.

Risks and edge cases: toolchain mismatch can change embedded BPF/BTF blobs and skeleton API. Big-endian skeleton generation is separate and easy to omit. `clean` removes the output directory and `iterators` path but not necessarily already checked-in skeleton headers depending on invocation context.

Test signals: `make` and `make big` under the iterator directory, reproducibility checks for generated skeletons, clang target support for both endiannesses, and module build consuming both headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/preload/iterators/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/preload/iterators/iterators.bpf.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/preload/iterators/iterators.bpf.c

Purpose: BPF-side iterator programs used by the preload module to print human-readable summaries of loaded BPF maps and programs. It is compiled into the generated skeleton headers embedded in the kernel module. The source was read as a complete 118-line file.

Important APIs/functions: `get_name`, `dump_bpf_map`, `dump_bpf_prog`, external kfunc symbol `bpf_map_sum_elem_count`, and GPL license section. It defines CO-RE-friendly shadow structs for iterator contexts, `bpf_map`, `bpf_prog`, `bpf_prog_aux`, `btf`, and BTF type/header data under `preserve_access_index`.

Control flow: `dump_bpf_map` receives a map iterator context, skips NULL end callbacks, prints a header at sequence number zero, and emits map ID, name, max entries, and summed current entries. `dump_bpf_prog` similarly skips NULL programs, prints a header, reads `prog->aux`, resolves a function name from BTF function info with `get_name` falling back to program name, and prints attached function/destination names. `get_name` validates BTF presence, probes the BTF type pointer, bounds-checks the name offset against BTF string length, and returns the string pointer or fallback.

State and persistence: BPF program state is transient per iterator callback. Output is written to the iterator `seq_file`; no maps are declared except skeleton rodata. The compiled object and skeleton persist as generated build artifacts.

Dependencies/integration: uses `bpf_helpers.h`, `bpf_core_read.h`, `BPF_SEQ_PRINTF`, `bpf_probe_read_kernel`, CO-RE relocation, BPF iterator attach types `iter/bpf_map` and `iter/bpf_prog`, and the kernel kfunc registered in `map_iter.c`.

Risks and edge cases: `dump_bpf_prog` dereferences `aux->func_info[0]`, `attach_func_name`, and `dst_prog->aux->name`; verifier/CO-RE assumptions must match iterator-visible program shapes. `get_name` only bounds-checks `name_off` against `str_len`; invalid BTF type arrays would rely on verifier/kernel read safety. Output format changes affect user-visible preload debug files.

Test signals: loading the generated iterator skeleton, reading `maps.debug` and `progs.debug`, CO-RE relocation tests across kernel BTF layouts, NULL end-callback behavior, and presence of sane table headers/rows under active maps/programs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/preload/iterators/iterators.bpf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/preload/iterators/iterators.lskel-big-endian.h -->
# sources/distributed-fs/ceph-client/kernel/bpf/preload/iterators/iterators.lskel-big-endian.h

Purpose: generated lightweight skeleton for the big-endian build of `iterators.bpf.c`. It embeds serialized BPF instructions, BTF, rodata, map/program/link descriptors, and inline helpers to open, load, attach, detach, and destroy the iterator programs. The source was read as a complete 437-line generated header.

Important APIs/types: `struct iterators_bpf`, `iterators_bpf__open`, `iterators_bpf__load`, `iterators_bpf__attach`, `iterators_bpf__detach`, `iterators_bpf__destroy`, `iterators_bpf__open_and_load`, `iterators_bpf__dump_bpf_map__attach`, and `iterators_bpf__dump_bpf_prog__attach`. It includes `<bpf/skel_internal.h>` and uses `bpf_load_and_run`, `skel_link_create`, `skel_closenz`, and `skel_alloc/free`.

Control flow: `open` allocates and sizes the skeleton context. `load` fills `bpf_load_and_run_opts` with big-endian serialized data/instruction blobs and asks the in-kernel loader to create maps/programs. `attach` creates `BPF_TRACE_ITER` links for map and program iterator programs and records link FDs. `detach` closes link FDs; `destroy` detaches, closes program/map FDs, and frees the skeleton.

State and persistence: skeleton state is heap allocated and owns map/program/link FDs until destroyed or until `bpf_preload_kern.c` converts link FDs into kernel link refs and zeroes them. The embedded object data is static in the header.

Dependencies/integration: generated by bpftool from `iterators.bpf.c` using `-mbig`. It is included by `bpf_preload_kern.c` when the kernel compile byte order is big endian.

Risks and edge cases: manual edits would be lost or desynchronize from the BPF source. Embedded byte order must match the target. Load failures propagate as negative errors, but callers must still destroy partial skeletons. Because this header contains raw generated blobs, source review focuses on the wrapper API and generation provenance.

Test signals: big-endian build coverage, successful skeleton load/attach in the preload module, bpftool regeneration diff checks, and reading generated bpffs debug iterator files on big-endian targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/preload/iterators/iterators.lskel-big-endian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/preload/iterators/iterators.lskel-little-endian.h -->
# sources/distributed-fs/ceph-client/kernel/bpf/preload/iterators/iterators.lskel-little-endian.h

Purpose: generated lightweight skeleton for the little-endian build of `iterators.bpf.c`. It embeds serialized BPF instructions, BTF, rodata, descriptors, and inline helpers used by the preload module on little-endian kernels. The source was read as a complete 435-line generated header.

Important APIs/types: `struct iterators_bpf`, `iterators_bpf__open`, `iterators_bpf__load`, `iterators_bpf__attach`, `iterators_bpf__detach`, `iterators_bpf__destroy`, `iterators_bpf__open_and_load`, `iterators_bpf__dump_bpf_map__attach`, and `iterators_bpf__dump_bpf_prog__attach`. It uses `struct bpf_loader_ctx`, map/program descriptors, link FD slots, `bpf_load_and_run`, and `skel_link_create`.

Control flow: `open` allocates skeleton storage and sets context size through the links offset. `load` passes little-endian embedded object data and instructions to the loader. Attach creates `BPF_TRACE_ITER` links for both iterator programs in order, returning the first error. Destroy is idempotent for NULL skeletons and closes links, program FDs, map FD, then frees memory.

State and persistence: static embedded BPF/BTF data persists in the module text/rodata; runtime FD state persists in the allocated skeleton until consumed/destroyed. The preload module transfers link ownership by calling `bpf_link_get_from_fd`, closing the original FDs, and zeroing the skeleton link fields.

Dependencies/integration: generated by bpftool from `iterators.bpf.c` using little-endian BPF target output. Included by `bpf_preload_kern.c` on little-endian builds.

Risks and edge cases: generated blobs must be regenerated from the matching BPF source and toolchain. Wrapper functions assume positive link FDs indicate success. API drift in `skel_internal.h` or `bpf_load_and_run_opts` can break build/load.

Test signals: standard little-endian kernel build, preload module load, successful creation of both iterator links, bpffs `maps.debug`/`progs.debug` output, and regeneration diff checks against the BPF source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/preload/iterators/iterators.lskel-little-endian.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/prog_iter.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/prog_iter.c

Purpose: registers the `bpf_prog` BPF iterator target so iterator programs can walk loaded BPF programs through seq_file. The source was read as a complete 106-line file.

Important APIs/functions: `bpf_prog_seq_start`, `bpf_prog_seq_next`, `bpf_prog_seq_show`, `bpf_prog_seq_stop`, `bpf_prog_iter_init`, and iterator context `struct bpf_iter__bpf_prog`. It defines `bpf_prog_seq_ops`, `bpf_prog_seq_info`, and `bpf_prog_reg_info`.

Control flow: seq start gets the current or next program ID and returns a referenced `struct bpf_prog`; next increments the ID cursor, drops the previous program, and fetches the next; show builds iterator metadata/context and runs the attached iterator BPF program; stop either runs the end callback with NULL or drops the current program reference. Late init fills the BTF ID for `struct bpf_prog` and registers the target.

State and persistence: each iterator file has private `prog_id` cursor state. Program refs persist only while a seq item is active. The iterator target registration persists for kernel lifetime after late init.

Dependencies/integration: uses BPF program ID registry helpers, BPF iterator registration, BTF ID lookup for `struct bpf_prog`, seq_file operations, and the preload `dump_bpf_prog` iterator program.

Risks and edge cases: the end callback passes NULL `prog`, so iterator programs must check it. Program deletion during iteration relies on ref acquisition. The context pointer is not marked trusted unlike map iterator, so verifier expectations differ.

Test signals: BPF iterator selftests over loaded programs, preload `progs.debug` output, program deletion while iterating, and BTF target registration at late init.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/prog_iter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/queue_stack_maps.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/queue_stack_maps.c

Purpose: implements BPF queue and stack map types using a fixed-size circular buffer and a shared map implementation with different pop/peek semantics. The source was read as a complete 288-line file.

Important APIs/functions: `queue_stack_map_alloc_check`, `queue_stack_map_alloc`, `queue_stack_map_free`, `queue_stack_map_push_elem`, `queue_map_pop_elem`, `stack_map_pop_elem`, `queue_map_peek_elem`, `stack_map_peek_elem`, unsupported lookup/update/delete/get_next_key stubs, `queue_stack_map_mem_usage`, `queue_map_ops`, and `stack_map_ops`. Important type: `struct bpf_queue_stack`.

Control flow: allocation validates zero key size, nonzero value size, supported flags, and value-size upper bound, then allocates `max_entries + 1` slots so head/tail equality can mean empty. Push validates flags, treats `BPF_EXIST` as overwrite-oldest-on-full, rejects `BPF_NOEXIST`, locks the map, optionally advances tail if replacing on full, copies value at head, and advances head. Queue get reads from tail and optionally advances tail; stack get reads from `head - 1` and optionally moves head back. Empty pop/peek zeroes the output buffer and returns `-ENOENT`.

State and persistence: `head`, `tail`, `size`, and inline `elements[]` persist for map lifetime. All operations mutate in-memory state under `rqspinlock_t`; no external persistence exists.

Dependencies/integration: uses BPF map ops, BTF map ID, map access flags, `bpf_map_area_alloc/free`, resilient spinlocks, and syscall/BPF helper push/pop/peek operations.

Risks and edge cases: full capacity is `max_entries` despite allocating one extra slot. `BPF_EXIST` intentionally overwrites the oldest queue/stack slot when full, while default push returns `-E2BIG`. Lookup/update/delete/get_next_key are unsupported. Lock acquisition can return `-EBUSY` through resilient spinlocks. Large value sizes are capped by `KMALLOC_MAX_SIZE` for user accessibility.

Test signals: queue/stack map selftests for FIFO/LIFO ordering, empty zero-fill, full-map overwrite vs `-E2BIG`, unsupported operations returning errors, map flags validation, BTF metadata, and concurrent producer/consumer stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/queue_stack_maps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/range_tree.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/range_tree.c

Purpose: implements a range allocator helper used by BPF arena to track free contiguous slot ranges. It represents set bits as interval nodes and also indexes ranges by size for best-fit lookup. The source was read as a complete 262-line file.

Important APIs/functions: `range_tree_init`, `range_tree_destroy`, `range_tree_find`, `range_tree_clear`, `range_tree_set`, and `is_range_tree_set`. Important internal type: `struct range_node`, with interval-tree node, range-size rb node, start/last bounds, and subtree max field.

Control flow: `range_tree_find` walks the size-sorted rbtree for a range at least as large as requested, keeping the smallest suitable best-fit candidate by moving through the tree. `range_tree_clear` removes a range from the set by iterating overlapping interval nodes, splitting a covering node, trimming left/right overlaps, or deleting fully covered nodes. `range_tree_set` first checks if the whole range is already set, clears overlaps, finds adjacent left/right ranges, merges both, extends one side, or allocates a new node. Destroy removes all interval nodes and frees them.

State and persistence: `struct range_tree` owns two cached rb roots that reference the same `range_node` objects. Nodes persist until ranges are cleared/destroyed. External locking is required by design; the implementation does not synchronize its rb trees internally.

Dependencies/integration: uses Linux `INTERVAL_TREE_DEFINE`, rb trees, `kmalloc_nolock`/`kfree_nolock`, BPF arena users, and `range_tree.h`. Comments note the split/merge logic is based on XFS bitmap interval handling.

Risks and edge cases: `last = start + len - 1` can wrap if callers pass invalid ranges; callers must bound inputs. `start - 1` and `last + 1` adjacency probes rely on unsigned wrap semantics and valid arena limits. Allocation failure while splitting can leave earlier trimming already applied in `range_tree_clear`. External locking is mandatory.

Test signals: BPF arena allocation/free tests, best-fit range selection tests, split/merge/adjacency cases, full-range initialization/teardown, invalid/overflow range fuzzing, and KASAN/rbtree debug coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/range_tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/range_tree.h -->
# sources/distributed-fs/ceph-client/kernel/bpf/range_tree.h

Purpose: declares the BPF arena range-tree structure and operations for setting, clearing, checking, finding, initializing, and destroying contiguous ranges. The source was read as a complete 21-line file.

Important APIs/types: `struct range_tree` with `it_root` and `range_size_root`; functions `range_tree_init`, `range_tree_destroy`, `range_tree_clear`, `range_tree_set`, `is_range_tree_set`, and `range_tree_find`.

Control flow: no executable flow is defined in the header. It exposes the API contract implemented by `range_tree.c`.

State and persistence: callers embed or allocate `struct range_tree`; its roots persist until `range_tree_destroy`. Range nodes are private to the implementation.

Dependencies/integration: requires rb-tree types from included kernel headers through users/implementation. It is a private BPF kernel header for BPF arena allocation logic.

Risks and edge cases: callers must provide synchronization and valid range bounds because the API does not encode locking or maximum size. `range_tree_find` returns signed `s64`, using negative errno values for failure.

Test signals: compile coverage of BPF arena users and runtime tests for all range-tree API functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/range_tree.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/relo_core.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/relo_core.c

Purpose: imports the shared libbpf CO-RE relocation implementation into the kernel BPF tree by including `../../tools/lib/bpf/relo_core.c`. The source was read as a complete 2-line file.

Important APIs/functions: this file defines no local functions; it compiles the shared `relo_core.c` implementation in the kernel build context. The imported code provides CO-RE relocation logic used for BTF-based field/type relocations.

Control flow: runtime/control flow is entirely in the included libbpf source. This wrapper only selects the implementation at compile time.

State and persistence: no local state. Imported relocation code operates on BTF/relo data supplied by callers.

Dependencies/integration: tightly couples kernel BPF CO-RE support to the in-tree `tools/lib/bpf/relo_core.c` source. Any include-path or API mismatch between kernel and tools code will surface here.

Risks and edge cases: sharing code by textual include can expose kernel builds to assumptions from tools/lib/bpf. Local review must include the imported file for behavioral changes, even though this wrapper is tiny. License tag allows LGPL/BSD dual-licensed imported implementation.

Test signals: CO-RE relocation selftests, BTF relocation verifier tests, kernel build with tools/lib/bpf changes, and compile warnings/errors from included code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/relo_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/reuseport_array.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/reuseport_array.c

Purpose: implements the `BPF_MAP_TYPE_REUSEPORT_SOCKARRAY` storage for sockets participating in SO_REUSEPORT groups. It lets userspace update slots with socket FDs, allows BPF reuseport selection to look up sockets, and coordinates socket detach/free through socket callback user data. The source was read as a complete 353-line file.

Important APIs/functions: `bpf_sk_reuseport_detach`, `reuseport_array_alloc_check`, `reuseport_array_lookup_elem`, `reuseport_array_delete_elem`, `reuseport_array_free`, `reuseport_array_alloc`, `bpf_fd_reuseport_array_lookup_elem`, `bpf_fd_reuseport_array_update_elem`, `reuseport_array_get_next_key`, `reuseport_array_mem_usage`, and `reuseport_array_ops`. Important type: `struct reuseport_array` with RCU socket pointer slots.

Control flow: allocation delegates most validation to array map checks but requires value size to be `u32` or `u64`. Update converts the supplied value to an FD, resolves the socket, performs quick validation, then under `reuseport_lock` and the new socket callback lock revalidates socket family/protocol/type, hashed/reuseport/RCU-free state, user-data availability, and flag semantics. It stores a flagged pointer to the target slot in `sk_user_data`, RCU-publishes the socket in the array slot, and clears old socket user data if replacing. Delete locks `reuseport_lock`, clears the socket's user data, and clears the RCU slot. Free walks slots under RCU and socket callback locks to clear user data before freeing the array.

State and persistence: map slots hold RCU `struct sock *` pointers. Each attached socket stores a flagged pointer back to its array slot in `sk_user_data`, allowing `bpf_sk_reuseport_detach` to null the slot on socket close/disconnect. Map memory persists until map free; socket references come from the FD during update and reuseport/socket lifetime rules thereafter.

Dependencies/integration: uses socket reuseport core, `reuseport_lock`, `sk_callback_lock`, `sockfd_lookup`, socket cookies, array map allocation checks, BPF map ops, BTF map IDs, RCU, and socket user-data flags `SK_USER_DATA_BPF`/`SK_USER_DATA_NOCOPY`.

Risks and edge cases: socket eligibility checks are race-sensitive and repeated under locks. `sk_user_data` must not already be used. Free intentionally does not take `reuseport_lock` and relies on callback locks plus RCU to race safely with detach. Value size controls whether lookup returns a cookie through the syscall FD path. The map ops do not expose update in `reuseport_array_ops`; specialized FD update helper is used.

Test signals: reuseport sockarray selftests for UDP/TCP IPv4/IPv6 sockets, FD update and cookie lookup, delete/free while sockets close, `BPF_NOEXIST`/`BPF_EXIST` behavior, unsupported sockets, busy `sk_user_data`, and RCU/KASAN stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/reuseport_array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/ringbuf.c -->
# sources/distributed-fs/ceph-client/kernel/bpf/ringbuf.c

Purpose: implements BPF ring buffer and user ring buffer map types plus helpers for kernel-produced records, dynptr reservations, output/query operations, mmap/poll support, overwrite mode, and draining user-produced samples through BPF callbacks. The source was read as a complete 880-line file.

Important APIs/functions: map ops `ringbuf_map_ops` and `user_ringbuf_map_ops`; allocation/mmap/poll helpers `ringbuf_map_alloc`, `bpf_ringbuf_alloc`, `ringbuf_map_mmap_kern`, `ringbuf_map_mmap_user`, `ringbuf_map_poll_kern`, `ringbuf_map_poll_user`; BPF helper prototypes for `bpf_ringbuf_reserve`, `bpf_ringbuf_submit`, `bpf_ringbuf_discard`, `bpf_ringbuf_output`, `bpf_ringbuf_query`, `bpf_ringbuf_reserve_dynptr`, `bpf_ringbuf_submit_dynptr`, `bpf_ringbuf_discard_dynptr`, and `bpf_user_ringbuf_drain`. Important types are `struct bpf_ringbuf`, `struct bpf_ringbuf_map`, and `struct bpf_ringbuf_hdr`.

Control flow: allocation validates flags, zero key/value sizes, power-of-two page-aligned size, allocates meta/data pages, double-maps data pages with `vmap`, initializes positions and waitqueue/irq_work. Kernel-producer reserve locks the ring, advances `pending_pos` past committed records, checks space against consumer and pending positions, optionally advances `overwrite_pos`, writes a busy header and page offset, publishes producer position with release ordering, and returns the record payload. Submit/discard clear the busy bit, optionally set discard, and wake readers depending on flags and consumer position. Output reserves, copies data, and commits. Query returns approximate positions/sizes. User-ringbuf drain uses an atomic busy bit instead of a spinlock, validates user-produced headers/positions, skips discarded records, invokes a BPF callback with a local dynptr, advances consumer position, and wakes producers as needed.

State and persistence: ring state persists in vmapped map memory: consumer, producer, pending, and overwrite positions plus data records. For kernel-producer maps, userspace can write only the consumer page; producer/data mappings are read-only. For user-producer maps, userspace cannot write consumer position but can write producer/data pages. Data pages are mapped twice to make wraparound records virtually contiguous.

Dependencies/integration: uses BPF map ops, BTF map IDs, helper prototypes/verifier argument types, dynptr support, wait queues, poll, irq_work wakeups, `remap_vmalloc_range`, vmalloc page arrays, memory barriers, resilient spinlocks, and user-space libbpf ringbuf conventions.

Risks and edge cases: size and position arithmetic must preserve 8-byte alignment and avoid records larger than `UINT_MAX/4`. Memory ordering between producers and consumers is central. Overwrite mode must advance only on record boundaries and not pass busy records. User-ringbuf validation must reject malformed producer positions, oversized samples, busy records, and samples extending beyond advertised producer space. Mmap permissions differ by map type. Wakeup flags can cause missed or excessive notifications if mishandled.

Test signals: BPF ringbuf selftests for reserve/submit/discard/output/query, dynptr helpers, mmap permission checks, poll wakeups, wraparound/double-mapping behavior, overwrite mode, user ringbuf drain callbacks, malformed user producer data, multi-producer concurrency, and KASAN/KCSAN/lockdep coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/bpf/ringbuf.c -->
