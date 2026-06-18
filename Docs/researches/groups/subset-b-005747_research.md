# Research Report: subset-b-005747

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/inode.c -->
## sources/distributed-fs/ceph-client/fs/proc/inode.c

Purpose: implements the generic procfs inode layer: proc inode allocation/free, proc superblock operations, proc dir entry inode instantiation, dynamic entry lifetime protection, file-operation wrappers, symlink support, mount option display, and dcache invalidation for entries whose backing task/sysctl state disappears.

Important APIs and functions: exports `proc_sops`, `proc_init_kmemcache`, `proc_invalidate_siblings_dcache`, `proc_entry_rundown`, `proc_link_inode_operations`, and `proc_get_inode`. Important internals are `proc_alloc_inode`, `proc_free_inode`, `proc_evict_inode`, `use_pde`, `unuse_pde`, `close_pdeo`, `proc_reg_open`, `proc_reg_release`, the `proc_reg_*` read/write/poll/ioctl/mmap/llseek wrappers, and compat/read-iter file-operation tables.

Control flow: proc root initialization calls `proc_init_kmemcache` before proc inodes or `proc_dir_entry` objects are allocated. `proc_get_inode` converts a `proc_dir_entry` into a VFS inode, selecting regular, iterator, compat, directory, symlink, or empty-directory operations from PDE flags and mode. Regular proc file operations dispatch through wrapper functions that either call permanent PDE operations directly or temporarily increment `pde->in_use` to block removal while a callback runs. Open paths register files with custom release hooks in `pde_openers`; removal calls `proc_entry_rundown`, biases `in_use` negative, waits for active callbacks, and force-closes pending openers.

State and persistence behavior: procfs state is in-memory. `struct proc_inode` stores PID, fd, namespace, PDE, sysctl header, sibling-dcache tracking, and operation payloads. `struct proc_dir_entry` lifetime uses `refcnt`, `in_use`, `pde_openers`, `pde_unload_lock`, and optional unload completion. Eviction clears pagecache, releases task PID tracking, and hands sysctl inodes to `proc_sys_evict_inode`. `proc_show_options` reflects per-superblock hidepid, gid, and pid-only subset state.

Dependencies and integration points: integrates VFS inode/superblock/file operation APIs, proc generic registration, pid and sysctl proc backends, seq_file, compat ioctl, mmap area selection, mount option reporting, and dentry alias invalidation. `proc_invalidate_siblings_dcache` is used by sysctl unregister and similar dynamic namespaces to invalidate all aliases across proc superblocks.

Risks: the PDE rundown protocol is concurrency-sensitive: missing `use_pde`/`unuse_pde` pairing can race module removal, and opener tracking must call release exactly once despite concurrent close and remove. Permanent entries bypass protections and must only be used for never-removed callbacks. Dcache invalidation crosses superblocks and must hold active references carefully. Sysctl pointers are nulled on eviction to avoid stale unregister references.

Test signals: open/read/write/poll/ioctl/mmap dynamic proc entries while removing them; forced module removal with an fd held open; compat ioctl builds; proc symlink readlink after entry removal; sysctl unregister dcache invalidation; hidepid/gid/subset mount option display; KASAN/lockdep coverage around `pde_unload_lock`, completions, and proc inode eviction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/internal.h -->
## sources/distributed-fs/ceph-client/fs/proc/internal.h

Purpose: defines the private procfs data model and cross-file contracts shared by proc root, pid entries, sysctl, network proc entries, task memory views, namespace links, and generic proc registration.

Important APIs and types: declares `struct proc_dir_entry`, `struct proc_inode`, `union proc_op`, `struct pde_opener`, `struct proc_maps_locking_ctx`, and `struct proc_maps_private`. Key helpers include `PROC_I`, `PDE`, `proc_pid`, `get_proc_task`, `pde_get`, `is_empty_pde`, `pde_force_lookup`, `proc_splice_unmountable`, `folio_precise_page_mapcount`, and `folio_average_page_mapcount`. It also declares core entry points such as `proc_get_inode`, `proc_entry_rundown`, `proc_lookup_de`, `proc_readdir_de`, `proc_setup_self`, `proc_setup_thread_self`, `proc_sys_init`, `proc_net_init`, and task maps/smaps/pagemap operation tables.

Control flow: the header has no runtime dispatcher, but it establishes how proc modules cooperate. Generic registration fills `proc_dir_entry` fields, inode creation stores the PDE in `proc_inode`, pid and sysctl code recover task/sysctl state through the inline helpers, and task memory files share `proc_maps_private` to pin the inode, task, mm, VMA iterator, locking state, and optional NUMA mempolicy.

State and persistence behavior: all structures are kernel-resident and tied to procfs object lifetimes. PDEs form an rb-tree directory hierarchy, carry callback pointers and callback-private data, and use `refcnt` plus `in_use` for removal safety. `proc_inode` extends VFS inodes with proc-specific task, sysctl, namespace, and sibling-inode metadata. Mapcount helpers snapshot folio mapping state for proc page-monitor outputs.

Dependencies and integration points: includes procfs public API, namespaces, refcounting, scheduler task APIs, memory-management APIs, binfmt/coredump state, and page mapcount configuration. It is the main internal ABI between `inode.c`, `generic.c`, `root.c`, `base.c`, `array.c`, `proc_sysctl.c`, `proc_net.c`, and task MMU/NOMMU files.

Risks: because this is an internal ABI, field invariants are broad: permanent PDEs must not disappear, forced lookup must be used for namespace-sensitive dentries, proc maps locking semantics differ under `CONFIG_PER_VMA_LOCK`, and mapcount helpers have different precision under `CONFIG_PAGE_MAPCOUNT`. Changing structure layout or flag meaning can break many proc subtrees.

Test signals: all relevant config combinations (`CONFIG_PROC_SYSCTL`, `CONFIG_NET`, `CONFIG_TTY`, `CONFIG_PROC_PAGE_MONITOR`, `CONFIG_PAGE_MAPCOUNT`, `CONFIG_PER_VMA_LOCK`, MMU/NOMMU); proc entry create/remove tests; pid/task lookup under exiting tasks; smaps/kpagecount mapcount validation; namespace-sensitive dentry revalidation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/interrupts.c -->
## sources/distributed-fs/ceph-client/fs/proc/interrupts.c

Purpose: implements `/proc/interrupts`, exposing per-IRQ interrupt accounting through seq_file iteration.

Important APIs and functions: defines `int_seq_ops` with `int_seq_start`, `int_seq_next`, `int_seq_stop`, and architecture/core-provided `show_interrupts`; registers the file in `proc_interrupts_init` via `proc_create_seq`.

Control flow: the sequence position is treated as an IRQ number. Iteration starts while `*pos <= irq_get_nr_irqs()`, increments until it exceeds the current IRQ limit, and delegates each row to `show_interrupts`. `fs_initcall(proc_interrupts_init)` creates the root proc entry during boot.

State and persistence behavior: no private persistent state is stored in this file. It reads live IRQ topology and statistics from the generic IRQ subsystem on demand. The seq cursor is the only per-read state.

Dependencies and integration points: depends on `linux/interrupt.h`, `linux/irqnr.h`, procfs, and seq_file. The formatting and per-architecture data come from the IRQ subsystem's `show_interrupts` implementation.

Risks: IRQ counts and the number of IRQ descriptors can change while userspace reads, so output is a live snapshot rather than an atomic global view. Off-by-one errors in iterator bounds would either omit the synthetic header/last IRQ row expected by `show_interrupts` or walk past the IRQ limit.

Test signals: read `/proc/interrupts` on systems with sparse IRQs, many MSI/MSI-X vectors, CPU hotplug, and changing IRQ allocations; compare row count to `irq_get_nr_irqs`; verify seq_file seek/re-read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/interrupts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/kcore.c -->
## sources/distributed-fs/ceph-client/fs/proc/kcore.c

Purpose: implements `/proc/kcore`, an ELF core-image view of kernel virtual memory for privileged readers. It builds program headers over RAM, vmalloc, vmemmap, kernel text, and module ranges, emits ELF notes including vmcoreinfo, and reads memory with architecture-safe access helpers.

Important APIs and functions: exports `register_mem_pfn_is_ram` and init-time `kclist_add`. Main internals include `update_kcore_size`, `kcore_ram_list`, `kcore_update_ram`, `append_kcore_note`, `read_kcore_iter`, `open_kcore`, `release_kcore`, `kcore_callback`, `proc_kcore_text_init`, `add_modules_range`, and `proc_kcore_init`. State is held in `kclist_head`, `kcore_nphdr`, `kcore_*_len`, `kcore_data_offset`, `kcore_need_update`, and `proc_root_kcore`.

Control flow: boot init creates `/proc/kcore`, records special text/vmalloc/module ranges, builds RAM ranges, and registers a memory-hotplug notifier. Open requires `CAP_SYS_RAWIO` and passes `security_locked_down(LOCKDOWN_KCORE)`, allocates a page bounce buffer, refreshes RAM ranges if hotplug marked them stale, and updates inode size. Reads first synthesize the ELF header, program headers, and note segment, then translate file offsets to kernel virtual addresses and copy page-sized chunks from the matching `kcore_list` entry.

State and persistence behavior: memory range metadata persists in a global list protected by `kclist_lock`, a percpu rwsem. Hotplug sets `kcore_need_update`, and the next open rebuilds RAM/VMEMMAP entries. The proc entry size mirrors generated ELF metadata plus the highest virtual offset. Each open file owns a temporary bounce page.

Dependencies and integration points: depends on ELF/core note definitions, vmcoreinfo, memory hotplug, memblock/system RAM walkers, vmalloc `vread_iter`, capability and lockdown LSM checks, page offline freeze/thaw, architecture hooks for physical-to-virtual translation and kernel text sections, and procfs read-iter support.

Risks: `/proc/kcore` is security-sensitive and must remain gated by capability and lockdown. Reads can touch volatile kernel memory, offline pages, hwpoisoned pages, unaccepted memory, vmalloc holes, and architecture-specific mappings; bad filtering can fault or disclose invalid data. Hotplug update and range list replacement must avoid readers seeing freed entries. ELF note sizing must guard against vmcoreinfo races.

Test signals: permission and lockdown denial; `readelf -h/-l /proc/kcore`; reads across ELF header, notes, RAM holes, vmalloc area, text/module ranges; memory online/offline while opening; hwpoison/offline page reads returning zeros; KASAN/lockdep around `kclist_lock` and page-offline freeze.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/kcore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/kmsg.c -->
## sources/distributed-fs/ceph-client/fs/proc/kmsg.c

Purpose: implements `/proc/kmsg`, a legacy privileged stream over the kernel printk/syslog buffer.

Important APIs and functions: `kmsg_open`, `kmsg_release`, `kmsg_read`, and `kmsg_poll` wrap `do_syslog` actions `SYSLOG_ACTION_OPEN`, `CLOSE`, `READ`, and `SIZE_UNREAD`. `kmsg_proc_ops` marks the entry permanent and uses generic llseek; `proc_kmsg_init` creates the file with mode `S_IRUSR`.

Control flow: opening notifies syslog with `SYSLOG_FROM_PROC`. Reads return `-EAGAIN` for nonblocking callers when no unread data is available, otherwise delegate to `do_syslog`. Poll waits on `log_wait` and reports readable events when unread bytes exist. Release closes the proc syslog session.

State and persistence behavior: no proc-private persistent state exists. State is held by the global printk/syslog subsystem and any syslog permission/rate semantics implemented there.

Dependencies and integration points: depends on procfs, poll, syslog/printk internals, `log_wait`, and VFS file flags. It coexists with `/dev/kmsg` and syslog syscalls but uses the `SYSLOG_FROM_PROC` source tag.

Risks: kernel log access can disclose sensitive data, so permissions and syslog capability checks in `do_syslog` are security-critical. Blocking/nonblocking behavior must match legacy readers. Multiple readers interact through global syslog buffer state, not isolated per-file queues.

Test signals: read as root and unprivileged user under different `dmesg_restrict` settings; nonblocking empty read returns `-EAGAIN`; poll wakes on printk; open/close interactions with other syslog consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/kmsg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/loadavg.c -->
## sources/distributed-fs/ceph-client/fs/proc/loadavg.c

Purpose: implements `/proc/loadavg`, reporting 1/5/15-minute load averages, runnable/total thread counts, and the last allocated PID cursor in the reader's active PID namespace.

Important APIs and functions: `loadavg_proc_show` calls `get_avenrun`, `nr_running`, global `nr_threads`, and `idr_get_cursor(&task_active_pid_ns(current)->idr)`. `proc_loadavg_init` registers a permanent single-file proc entry.

Control flow: each read computes fixed-point load averages with a small bias (`FIXED_1/200`) and formats the traditional five fields. The initcall creates `loadavg` under proc root.

State and persistence behavior: no local state persists. Values are live scheduler and PID namespace snapshots; they are not mutually atomic.

Dependencies and integration points: depends on scheduler load average accounting, PID namespaces, procfs single-file helpers, and seq_file output. It is consumed by uptime/top/procps-style tools.

Risks: output semantics are ABI-stable, so field order and formatting must not change. The last PID field is namespace-sensitive and can be surprising if current task's active PID namespace differs from the proc mount namespace.

Test signals: compare `/proc/loadavg` with scheduler load under idle and CPU-bound workloads; read from nested PID namespaces; verify permanent entry creation and stable formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/loadavg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/meminfo.c -->
## sources/distributed-fs/ceph-client/fs/proc/meminfo.c

Purpose: implements `/proc/meminfo`, the central text summary of system memory, swap, slab, vmalloc, hugepage, zswap, GPU, CMA, poisoned, unaccepted, and architecture-specific memory counters.

Important APIs and functions: `meminfo_proc_show` gathers counters via `si_meminfo`, `si_swapinfo`, `vm_memory_committed`, `si_mem_available`, `global_node_page_state`, `global_zone_page_state`, `pcpu_nr_pages`, `hugetlb_report_meminfo`, `memtest_report_meminfo`, and weak `arch_report_meminfo`. `show_val_kb` formats page counts as kB; `proc_meminfo_init` registers the permanent proc file.

Control flow: each read builds a live snapshot: base RAM/swap totals, file cache adjusted for swapcache and buffers, LRU lists, slab reclaimability, writeback/dirty state, page table usage, commit limit, vmalloc, per-config optional sections, hugepage data, and architecture extensions. Init creates a single seq file and marks its PDE permanent.

State and persistence behavior: no local state is stored. All reported values come from VM, swap, memcg-independent global page state, atomic counters, and architecture hooks. Some fields intentionally report zero for compatibility (`NFS_Unstable`, `Bounce`, `WritebackTmp`, `VmallocChunk`).

Dependencies and integration points: integrates with the VM page allocator, swap, slab, hugetlb, transparent hugepages, zswap, CMA, memory failure, unaccepted memory, percpu allocator, GPU reclaim counters, and procfs/seq_file. Userspace treats field names as ABI.

Risks: the file is a non-atomic multi-counter snapshot, so values may not add up exactly under memory pressure. Field removal or reordering can break userspace parsers. New counters must use correct units and config guards. Cached memory calculation must avoid underflow.

Test signals: parse field presence across configs; compare totals under memory allocation, swap, zswap, THP, hugetlb, CMA, memory hotplug, and NUMA workloads; ABI tests for field names and kB formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/meminfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/namespaces.c -->
## sources/distributed-fs/ceph-client/fs/proc/namespaces.c

Purpose: implements `/proc/<pid>/ns`, exposing namespace membership as symlinks and directory entries for configured namespace types.

Important APIs and functions: the `ns_entries` table selects enabled `proc_ns_operations`. Core functions are `proc_ns_get_link`, `proc_ns_readlink`, `proc_ns_instantiate`, `proc_ns_dir_readdir`, and `proc_ns_dir_lookup`. Exports `proc_ns_dir_operations` and `proc_ns_dir_inode_operations`.

Control flow: readdir obtains the task from the proc inode, emits dots, and emits one entry per enabled namespace operation using `proc_fill_cache`. Lookup scans `ns_entries` by name and instantiates a symlink inode bound to that namespace operation. Symlink traversal enforces `ptrace_may_access(PTRACE_MODE_READ_FSCREDS)`, obtains the namespace path via `ns_get_path`, and jumps to the nsfs dentry; readlink formats the namespace name via `ns_get_name`.

State and persistence behavior: namespace link inodes carry `PROC_I(inode)->ns_ops` and task PID state inherited from `proc_pid_make_inode`. Dentries use PID dentry operations so they revalidate against task lifetime. No namespace reference persists in the proc inode beyond operation metadata; the target path is obtained at access time.

Dependencies and integration points: integrates proc pid lookup, nsfs operations, ptrace access checks, pid/user/net/uts/ipc/mnt/cgroup/time namespace implementations, and VFS symlink/readlink handling.

Risks: namespace symlinks are security-sensitive because they reveal and can open namespace file descriptors; ptrace-mode checks must be preserved. Task exit can race lookup/readlink. Config-dependent table order is user-visible in directory listings.

Test signals: list and read `/proc/<pid>/ns` across namespace configs; permission denial under ptrace restrictions; task exit during readdir/readlink; `setns` users opening namespace symlinks; nested pid/user namespace behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/namespaces.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/nommu.c -->
## sources/distributed-fs/ceph-client/fs/proc/nommu.c

Purpose: implements global `/proc/maps` for NOMMU kernels, listing all `vm_region` objects known to the kernel.

Important APIs and functions: `nommu_region_show` formats one region, `nommu_region_list_start/next/stop/show` implement seq iteration over `nommu_region_tree`, and `proc_nommu_init` registers the file.

Control flow: opening/reading the seq file takes `nommu_region_sem` for the duration of iteration, walks the rb-tree from the first node to the requested position, and formats each region with address range, permissions, offset, device/inode, and optional file path.

State and persistence behavior: no local state persists; the source of truth is the global NOMMU region rb-tree. The read lock stabilizes the region list during seq traversal.

Dependencies and integration points: depends on NOMMU VM region tracking, rb-tree iteration, seq_file, procfs, and VFS path formatting. It is distinct from per-process `task_nommu.c` maps.

Risks: long reads hold `nommu_region_sem`, so very large region sets can delay region mutation. ABI formatting must remain compatible with proc maps parsers while representing NOMMU-specific shared/private flags.

Test signals: NOMMU builds; mapped file and anonymous regions; concurrent mmap/munmap while reading; seq seek behavior; path formatting for deleted or special files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/nommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/page.c -->
## sources/distributed-fs/ceph-client/fs/proc/page.c

Purpose: implements global page-monitor files `/proc/kpagecount`, `/proc/kpageflags`, and optionally `/proc/kpagecgroup`, exposing physical page mapcounts, stable page flags, and owning memory-cgroup inode IDs as arrays of 64-bit records indexed by PFN.

Important APIs and functions: `kpage_read` is the common aligned array reader. `get_max_dump_pfn`, `get_kpage_count`, `stable_page_flags`, `kpagecount_read`, `kpageflags_read`, `kpagecgroup_read`, and `proc_page_init` implement each file. `stable_page_flags` is exported GPL for other kernel users.

Control flow: reads require offset and size alignment to `sizeof(u64)`, clamp to the maximum dumpable PFN, loop PFN-by-PFN through `pfn_to_online_page`, compute the requested value or zero for holes, copy it to userspace, and periodically reschedule. `stable_page_flags` snapshots page/folio state and maps internal flags into documented `KPF_*` bits including pseudo flags for NOPAGE, THP, huge, zero page, mmap, anon, KSM, buddy, offline, pgtable, slab, idle, swapcache, hwpoison, and architecture/private bits.

State and persistence behavior: no file-local state persists. Values are live snapshots of struct page, folio, memcg, and mapcount state. Sparsemem extends readable PFNs to populated early sections even beyond `max_pfn` alignment.

Dependencies and integration points: depends on memory hotplug/online pages, page snapshots, folio flags, mapcount helpers from `internal.h`, KSM, THP, hugetlb, memcg, page idle, memory failure, and procfs permanent file registration.

Risks: these interfaces expose low-level memory layout signals; permissions are root-read-only but still security-sensitive. Page state can change while reading, so output is not atomic. Mapcount precision depends on config. Device-zone TODO notes that not all memmap initialization can be identified.

Test signals: aligned and misaligned reads; reads across holes and sparsemem section edges; THP/hugetlb/KSM/zero/offline/hwpoison page flag bits; memcg enabled/disabled builds; compare kpagecount with mapped pages under `CONFIG_PAGE_MAPCOUNT` and fallback configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/page.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/proc_net.c -->
## sources/distributed-fs/ceph-client/fs/proc/proc_net.c

Purpose: implements network-namespace-aware proc entries and `/proc/<pid>/net`, including helper APIs used by networking code to create per-net seq and single proc files.

Important APIs and functions: exports `proc_create_net_data`, `proc_create_net_data_write`, `proc_create_net_single`, `proc_create_net_single_write`, `proc_net_inode_operations`, `proc_net_operations`, `bpf_iter_init_seq_net`, `bpf_iter_fini_seq_net`, and `proc_net_init`. Internals include `PDE_NET`, `get_proc_net`, `seq_open_net`, `seq_release_net`, `single_open_net`, `single_release_net`, `get_proc_task_net`, `proc_tgid_net_lookup`, `proc_tgid_net_readdir`, and pernet init/exit handlers.

Control flow: networking subsystems register entries under a net namespace's proc tree with seq or single callbacks. Opening a seq entry resolves the net namespace from the PDE parent, gets a net reference, allocates seq private state of caller-specified size, and stores/tracks the net reference. `/proc/<pid>/net` lookup and readdir resolve the target task's `nsproxy->net_ns` under task lock and then delegate to that namespace's `proc_net` tree. `proc_net_init` creates `/proc/net -> self/net` and registers pernet setup.

State and persistence behavior: each `struct net` owns `proc_net` and `proc_net_stat` PDE anchors. Per-open seq files hold a net reference in `seq_net_private`, with optional namespace tracker under `CONFIG_NET_NS`. Proc net dentries use forced lookup because `setns(CLONE_NEWNET)` can change visible content beneath the same path.

Dependencies and integration points: integrates network namespace lifetime, pernet subsystem registration, proc generic registration, seq_file, BPF iterator net initialization, task namespace lookup, and proc pid dentry/inode behavior.

Risks: net namespace references must be acquired before callbacks and released exactly once. `/proc/<pid>/net` must reflect the target task's current net namespace and not cache stale dentries. Writable helpers allow network subsystems to mutate state via proc; mode/write callback validation matters.

Test signals: create/read per-net proc entries from multiple netns; `setns` while resolving `/proc/self/net`; task exit during `/proc/<pid>/net` lookup; BPF iterator net ref lifecycle; writable proc_net entries with and without write callbacks; pernet cleanup removing `stat` and net anchors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/proc_net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/proc_sysctl.c -->
## sources/distributed-fs/ceph-client/fs/proc/proc_sysctl.c

Purpose: implements `/proc/sys`, the procfs frontend and registry machinery for sysctl tables, including registration/unregistration, directory creation, namespaced table links, dentry revalidation, handler dispatch, polling, permissions, mount points, and boot-time `sysctl.*` command-line writes.

Important APIs and functions: exports `register_sysctl_mount_point`, `proc_sys_poll_notify`, `register_sysctl_sz`, `__register_sysctl_table`, `__register_sysctl_init`, `unregister_sysctl_table`, `setup_sysctl_set`, `retire_sysctl_set`, `proc_sys_init`, `sysctl_is_alias`, and `do_sysctl_args`. Core internals include `find_entry`, `insert_header`, `use_table`, `start_unregistering`, `proc_sys_make_inode`, `proc_sys_lookup`, `proc_sys_call_handler`, `proc_sys_readdir`, `proc_sys_permission`, dentry ops, `get_subdir`, `sysctl_follow_link`, validation helpers, `insert_links`, and `drop_sysctl_table`.

Control flow: registration allocates a `ctl_table_header`, validates entries, walks/creates the path with `sysctl_mkdir_p`, inserts entries into rb-trees under `sysctl_lock`, and may create link tables in the root set for non-root sysctl sets. Lookup grabs the containing header, finds an rb-tree entry, follows namespace links when needed, creates an inode bound to the table/header, and splices it into the dcache. Reads and writes grab the header, check sysctl permissions, allocate a kernel buffer, run cgroup BPF sysctl hooks, call the table's `proc_handler`, and copy results. Unregistration drops registration counts, waits for active users, invalidates sibling dentries, erases rb-tree entries, drops links, and frees by RCU when inodes release the header.

State and persistence behavior: sysctl registry state is in kernel memory: `ctl_dir` rb-trees, `ctl_table_header` refcounts (`count`, `nreg`, `used`), unregister completions, sibling inode lists, namespace sets, and optional poll wait/event counters. Sysctl data values live in caller-owned storage referenced by table entries and remain valid until unregistration completes. Boot-time command-line sysctl setting temporarily mounts proc and writes `/proc/sys/...`.

Dependencies and integration points: integrates the sysctl core, procfs inode/dentry APIs, VFS read/write iterators, security hooks, cgroup BPF sysctl programs, fs_context-mounted procfs, kernel command-line parsing, namespace-aware `ctl_table_root` lookup, and RCU freeing.

Risks: this is a high-risk lifetime and ABI surface. Caller-owned tables must outlive registration; unregister must block new users while waiting for existing handlers; dcache aliases for namespaced sysctls can otherwise expose stale or wrong tables; link tables must stay balanced; permission semantics deliberately do not grant root write access to read-only entries. Handler buffers are bounded by `KMALLOC_MAX_SIZE`, but handlers still parse user-controlled strings. Boot command-line writes happen after proc mount and can differ from early parameters.

Test signals: register/unregister under concurrent read/write/readdir/poll; duplicate-name rejection; permanently empty mount points; non-root/namespaced sysctl sets and link projection; cgroup BPF sysctl allow/deny/modify paths; mode/handler/table validation failures; boot `sysctl.foo=bar` and alias parameters; dentry revalidation after unregister; RCU/lockdep/KASAN coverage around `sysctl_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/proc_sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/proc_tty.c -->
## sources/distributed-fs/ceph-client/fs/proc/proc_tty.c

Purpose: implements `/proc/tty`, `/proc/tty/drivers`, `/proc/tty/ldiscs`, and per-driver proc hooks under `/proc/tty/driver`.

Important APIs and functions: exports `proc_tty_register_driver`, `proc_tty_unregister_driver`, and `proc_tty_init`. Internals include `show_tty_range`, `show_tty_driver`, `t_start`, `t_next`, `t_stop`, and `tty_drivers_op`.

Control flow: init creates the proc tty directories, ldisc/driver listing files, and a restricted `tty/driver` directory. `/proc/tty/drivers` locks `tty_mutex`, emits pseudo-driver rows once at the head of the global driver list, then emits one or more ranges per registered `tty_driver`. Driver registration creates `tty/driver/<driver_name>` when the driver provides `ops->proc_show`; unregister removes it and clears `driver->proc_entry`.

State and persistence behavior: persistent proc state is limited to `proc_tty_driver` and each `tty_driver->proc_entry`. The driver list and ldisc list are live TTY subsystem state. The driver directory is user-read/search-only due to serial timing information concerns.

Dependencies and integration points: depends on the TTY core's global `tty_drivers` list, `tty_mutex`, driver proc callbacks, tty ldisc seq ops, and procfs create/remove helpers.

Risks: per-driver proc entries must be removed before driver structures disappear. `/proc/tty/driver/serial` style outputs can leak usage timing, hence restricted permissions must remain. Formatting is ABI-like for procps and diagnostics.

Test signals: register/unregister TTY drivers with proc callbacks; read `/proc/tty/drivers` with pseudo drivers, multi-major ranges, PTYs, VT, console, and serial drivers; permission checks on `/proc/tty/driver`; concurrent driver unregister while reading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/proc_tty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/root.c -->
## sources/distributed-fs/ceph-client/fs/proc/root.c

Purpose: implements procfs mount/context handling, superblock construction, root directory behavior, mount options, filesystem registration, and boot initialization of the static proc tree.

Important APIs and functions: exports `proc_root_init` and defines global `proc_root`. Key internals include `struct proc_fs_context`, `proc_parse_hidepid_param`, `proc_parse_subset_param`, `proc_parse_pidns_param`, `proc_parse_param`, `proc_apply_options`, `proc_fill_super`, `proc_reconfigure`, `proc_get_tree`, `proc_init_fs_context`, `proc_kill_sb`, `proc_root_getattr`, `proc_root_lookup`, and `proc_root_readdir`.

Control flow: `proc_init_fs_context` creates a mount context bound to the current active PID namespace and its user namespace. Option parsing handles `gid=`, `hidepid=`, `subset=pid`, and optionally `pidns=` from an nsfs file or path. `proc_fill_super` allocates `proc_fs_info`, applies options, sets proc superblock flags and operations, creates the root inode from `proc_root`, and installs persistent `self` and `thread-self` dentries. Root lookup first tries numeric PID lookup, then static proc entries; readdir emits static entries before switching to PID directories at `FIRST_PROCESS_ENTRY`.

State and persistence behavior: each proc superblock owns `proc_fs_info` with pid namespace, hidepid policy, pid gid, and pid-only subset setting. Reconfigure can update hidepid/gid/subset but rejects pid namespace changes. `proc_root` is a static permanent PDE anchoring the global proc tree; each mounted superblock has its own root dentry/inode.

Dependencies and integration points: integrates fs_context, user and PID namespaces, nsfs pidns files, proc inode/super ops, proc self/thread-self setup, proc net/sys/tty initialization, generic proc registration, NFSd/openprom mount points, and VFS anonymous superblocks.

Risks: mount option parsing affects process visibility and namespace semantics. `pidns=` permission rules must match joining pid namespaces and only allow descendant namespaces. Error unwinding in `proc_fill_super` is sparse after allocation failures. Root readdir position split between static and PID entries is ABI-sensitive.

Test signals: mount proc with numeric and string hidepid values, gid, subset=pid, and pidns file/path; reconfigure hidepid/gid/subset and reject pidns reconfigure; root lookup for static names and numeric PIDs; nested PID/user namespace mounts; unmount frees pid namespace and `proc_fs_info` via RCU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/root.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/self.c -->
## sources/distributed-fs/ceph-client/fs/proc/self.c

Purpose: implements the persistent `/proc/self` symlink, resolving at read time to the caller's thread-group ID in the proc mount's PID namespace.

Important APIs and functions: `proc_self_get_link`, `proc_setup_self`, and `proc_self_init`; global `self_inum` stores the allocated inode number.

Control flow: init allocates a stable proc inode number. Superblock fill calls `proc_setup_self`, which creates a persistent root dentry named `self`, allocates a symlink inode with `proc_self_inode_operations`, and attaches it with `d_make_persistent`. Link resolution computes `task_tgid_nr_ns(current, proc_pid_ns(inode->i_sb))`, allocates a decimal string, and frees it through delayed-call cleanup.

State and persistence behavior: each proc mount has a persistent dentry/inode for `self`, but the symlink target is dynamic per calling task and pid namespace. `self_inum` is initialized once and reused across mounts.

Dependencies and integration points: depends on proc superblock PID namespace state, scheduler task IDs, VFS delayed symlink cleanup, and proc root setup.

Risks: link resolution can fail with `-ENOENT` when current has no TGID in the mount namespace, and RCU-walk context requires atomic allocation or `-ECHILD`. The target format is ABI-stable.

Test signals: readlink `/proc/self` from init and nested PID namespaces; RCU path-walk behavior; persistent dentry creation failure during proc mount; compare target with `getpid()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/self.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/softirqs.c -->
## sources/distributed-fs/ceph-client/fs/proc/softirqs.c

Purpose: implements `/proc/softirqs`, exposing per-CPU counters for each softirq vector.

Important APIs and functions: `show_softirqs` formats the table using `softirq_to_name`, `for_each_possible_cpu`, and `kstat_softirqs_cpu`; `proc_softirqs_init` creates a permanent single proc file.

Control flow: each read prints a CPU header row, then one row per `NR_SOFTIRQS` vector with fixed-width per-possible-CPU counters. Init creates and marks the proc entry permanent.

State and persistence behavior: no local state is stored. Counters are live kernel softirq statistics and can change during output.

Dependencies and integration points: depends on kernel softirq names/statistics, procfs, and seq_file. It complements aggregate softirq data in `/proc/stat`.

Risks: output is not atomic across CPUs, and CPU hotplug can change online status while possible CPUs remain stable. Formatting is consumed by monitoring tools.

Test signals: read under network/block/timer softirq load; compare aggregates with `/proc/stat`; CPU hotplug systems; verify all configured softirq names appear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/softirqs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/stat.c -->
## sources/distributed-fs/ceph-client/fs/proc/stat.c

Purpose: implements `/proc/stat`, reporting aggregate and per-CPU time accounting, interrupt counts, context switches, boot time, fork count, runnable/blocked process counts, and softirq counters.

Important APIs and functions: exports `get_idle_time` for `/proc/uptime`. Main functions are `get_iowait_time`, `show_irq_gap`, `show_all_irqs`, `show_stat`, `stat_open`, and `proc_stat_init`. Architecture hooks `arch_irq_stat_cpu` and `arch_irq_stat` default to zero if not supplied.

Control flow: `stat_open` sizes the seq buffer based on CPU and IRQ counts. `show_stat` fetches boot time adjusted for time namespaces, accumulates cpustat values over possible CPUs, uses tick/nohz idle and iowait accessors when available, prints aggregate `cpu` and per-online-CPU rows, prints a dense interrupt vector with gaps filled by zeros, and emits process/softirq summaries.

State and persistence behavior: no local state persists. Values are live scheduler, irq, time namespace, and kernel stat snapshots. `get_idle_time` and `get_iowait_time` fall back to cpustat fields for offline or unsupported nohz accounting.

Dependencies and integration points: integrates scheduler cputime accounting, kernel_stat IRQ/softirq counters, IRQ descriptor enumeration, time namespaces, boot-time accounting, procfs permanent entries, and `/proc/uptime`.

Risks: userspace depends on exact field order and units in USER_HZ ticks. Aggregate values are non-atomic and may not equal a sum of later per-CPU reads. IRQ vector gaps must be preserved to keep IRQ-number indexing. Time namespace adjustment affects `btime`.

Test signals: compare CPU counters under workloads, nohz idle, offline CPUs, and virtualization steal/guest time; verify interrupt vector length with sparse IRQs; read from time namespaces; monitor buffer sizing on large CPU/IRQ systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/task_mmu.c -->
## sources/distributed-fs/ceph-client/fs/proc/task_mmu.c

Purpose: implements MMU-backed per-task memory proc files: `/proc/<pid>/maps`, `smaps`, `smaps_rollup`, `clear_refs`, `pagemap`, `numa_maps`, and the `PROCMAP_QUERY` and `PAGEMAP_SCAN` ioctls. It also supplies task memory/statm helpers used by other proc PID files.

Important APIs and functions: exports `task_mem`, `task_vsize`, `task_statm`, `proc_pid_maps_operations`, `proc_pid_smaps_operations`, `proc_pid_smaps_rollup_operations`, `proc_clear_refs_operations`, `proc_pagemap_operations`, and optionally `proc_pid_numa_maps_operations`. Major internals include VMA iteration helpers `m_start/m_next/m_stop`, `show_map_vma`, `do_procmap_query`, smaps walkers (`smaps_account`, `smap_gather_stats`, `show_smap`, `show_smaps_rollup`), `clear_refs_write`, pagemap walkers/readers, `do_pagemap_scan`, and NUMA walkers.

Control flow: map-like seq files open by pinning the target mm through `proc_mem_open(PTRACE_MODE_READ)`, then each read pins the task/mm, locks VMAs with either per-VMA locking or `mmap_lock`, iterates VMAs plus gate VMA, and formats rows. `PROCMAP_QUERY` copies a versioned query struct, finds a matching VMA by address/flags, optionally copies a name and build ID, and returns metadata. `smaps` walks page tables per VMA to compute RSS/PSS/dirty/swap/hugetlb/THP flags; rollup aggregates all VMAs and may drop/reacquire `mmap_lock` under contention. `clear_refs` parses a numeric mode, takes write mmap lock, clears referenced or soft-dirty state, coordinates MMU notifiers, and flushes TLBs. `pagemap` reads aligned 64-bit entries over virtual pages and hides PFNs unless caller has `CAP_SYS_ADMIN`. `PAGEMAP_SCAN` validates masks/ranges, walks pages, reports matching ranges, and can userfaultfd-write-protect matching pages.

State and persistence behavior: per-open state lives in `proc_maps_private`, `pagemapread`, or scan private buffers; target mm references are retained until release via `mmdrop`. Persistent effects include clearing referenced bits, clearing soft-dirty state, resetting high-water RSS, setting UFFD write-protect markers, and TLB/MMU-notifier side effects. Most reports are live, non-atomic snapshots of mm/VMA/page-table state.

Dependencies and integration points: deeply integrates VFS proc PID access checks, ptrace permission, mm/VMA iterators, per-VMA locks, mmap locking, pagewalk, rmap/mapcount, THP, hugetlb, shmem, KSM, swap, soft-dirty, userfaultfd, MMU notifiers, pkeys, build-id parsing, NUMA mempolicy, and seq_file.

Risks: this is one of procfs's most concurrency- and security-sensitive files. Pagemap must not disclose PFNs without privilege. Page-table walkers must handle migration/device-private/guard/marker entries, THP splitting, HugeTLB partial ranges, and mm teardown. Soft-dirty and UFFD-WP modifications require correct notifier/TLB ordering and pinned-page handling. Per-VMA lock fallback must avoid iterator corruption. Output ABI is heavily consumed by debuggers, profilers, CRIU, and monitoring tools.

Test signals: maps/smaps/pagemap reads while target mutates VMAs or exits; PFN hiding for unprivileged readers; PROCMAP_QUERY with names/build IDs and partial user structs; clear_refs modes 1-5; soft-dirty tracking with pinned/COW pages; THP, HugeTLB, shmem swap, KSM, device-private, guard regions; PAGEMAP_SCAN masks, output buffer limits, WP matching, and fatal-signal interruption; NUMA maps with policies and node distribution; lockdep/KCSAN pagewalk coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/task_mmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/task_nommu.c -->
## sources/distributed-fs/ceph-client/fs/proc/task_nommu.c

Purpose: implements NOMMU per-task memory reporting for `/proc/<pid>/maps`, task memory summaries, virtual size, and statm-like values.

Important APIs and functions: exports `task_mem`, `task_vsize`, `task_statm`, and `proc_pid_maps_operations`. Internals include `nommu_vma_show`, `proc_get_vma`, seq iterator functions `m_start/m_next/m_stop`, `maps_open`, `map_release`, and `pid_maps_open`.

Control flow: task memory helpers take `mmap_read_lock`, iterate VMAs, and account VMA objects, backing `vm_region` allocations, region spans, mm/fs/files/sighand/task object sizes, and shared versus private ownership heuristics. The maps file opens by pinning the target mm with ptrace read permission, then seq iteration locks the mm, initializes a VMA iterator from the file position, formats each VMA, and releases task/mm refs at stop.

State and persistence behavior: no persistent mutations occur. Per-open seq private state stores the proc inode and pinned mm reference until release. Reported memory is an approximate live accounting based on object sizes and NOMMU region sharing.

Dependencies and integration points: depends on NOMMU VMA/region structures, `kobjsize`, VFS file path formatting, proc PID task/mm access, ptrace permission, mmap locking, and seq_file. It is the NOMMU counterpart to `task_mmu.c`.

Risks: memory accounting is approximate and can double-count or classify shared objects based on reference counts. Iterator positions use virtual addresses and `-1UL` sentinel semantics. Output must stay maps-compatible despite NOMMU-specific `S/s` shared flags.

Test signals: NOMMU builds with private and shared mappings; task exit during maps read; mmap changes while reading; statm/memory summary sanity; file-backed and stack VMA formatting; ptrace permission denial.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/task_nommu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/thread_self.c -->
## sources/distributed-fs/ceph-client/fs/proc/thread_self.c

Purpose: implements the persistent `/proc/thread-self` symlink, resolving to the caller's task directory path within its thread group.

Important APIs and functions: `proc_thread_self_get_link`, `proc_setup_thread_self`, `proc_thread_self_init`, and global `thread_self_inum`.

Control flow: init allocates a stable inode number. Superblock fill creates a persistent symlink dentry named `thread-self`. Link resolution computes both TGID and TID in the proc mount's PID namespace and formats `"<tgid>/task/<pid>"` into a delayed-call-freed buffer.

State and persistence behavior: the dentry/inode are persistent per proc superblock, while the target string is dynamically generated per caller. The inode number is allocated once at boot.

Dependencies and integration points: depends on proc superblock PID namespace state, scheduler PID/TGID namespace helpers, proc root setup, and VFS symlink delayed calls.

Risks: returns `-ENOENT` if the caller lacks a PID in the mount namespace. RCU path walk requires atomic allocation or `-ECHILD`. The target format is ABI-stable and must match `/proc/<tgid>/task/<tid>`.

Test signals: readlink from main thread and secondary threads; nested PID namespace behavior; RCU lookup path; compare target with `/proc/self/task/<tid>` existence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/thread_self.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/uptime.c -->
## sources/distributed-fs/ceph-client/fs/proc/uptime.c

Purpose: implements `/proc/uptime`, reporting system uptime and accumulated idle time in seconds with two decimal places.

Important APIs and functions: `uptime_proc_show` uses `kcpustat_cpu_fetch`, exported `get_idle_time`, `ktime_get_boottime_ts64`, and `timens_add_boottime`; `proc_uptime_init` registers a permanent single proc entry.

Control flow: each read sums idle nanoseconds over all possible CPUs, obtains boottime uptime, applies time namespace offset, converts idle nanoseconds to seconds/nanoseconds, and formats both values. Init creates and marks the PDE permanent.

State and persistence behavior: no local state persists. Values are live snapshots from scheduler idle accounting and timekeeping.

Dependencies and integration points: depends on `/proc/stat`'s `get_idle_time`, kernel cpustat, time namespaces, procfs, and seq_file. Userspace tools compare it with `/proc/stat` idle counters.

Risks: idle time is summed over possible CPUs, so on multicore systems it can exceed wall-clock uptime. Snapshot is non-atomic across CPUs. Time namespace adjustment affects the uptime component but not the cumulative idle accounting in the same way wall-clock users may expect.

Test signals: compare idle sum with `/proc/stat`; read in time namespaces; CPU hotplug/possible CPU configs; nohz idle fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/uptime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/util.c -->
## sources/distributed-fs/ceph-client/fs/proc/util.c

Purpose: provides a small procfs utility for parsing decimal path components into unsigned integers, primarily for numeric proc entries such as PIDs or file descriptors.

Important APIs and functions: exports `name_to_int(const struct qstr *qstr)`.

Control flow: `name_to_int` rejects names with leading zeroes longer than one character, rejects non-digits, checks for unsigned overflow using `(~0U - 9) / 10`, accumulates the number, and returns `~0U` as an invalid sentinel.

State and persistence behavior: stateless pure parser; it reads only the supplied qstr.

Dependencies and integration points: depends on dcache qstr definitions and proc internal callers in numeric lookup paths. The invalid sentinel must be understood by callers as "not a valid decimal name."

Risks: the sentinel collides with the maximum unsigned value, so callers must not allow that as a valid object number. Leading-zero rejection is ABI-relevant for proc numeric names. Overflow checks must run before multiply/add.

Test signals: parse `0`, normal PIDs, leading-zero strings, non-digit strings, empty-like qstrs from lookup callers, `UINT_MAX`, and overflow values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/version.c -->
## sources/distributed-fs/ceph-client/fs/proc/version.c

Purpose: implements `/proc/version`, exposing the kernel banner built from UTS sysname, release, and version.

Important APIs and functions: `version_proc_show` formats `linux_proc_banner` with `utsname()->sysname`, `release`, and `version`; `proc_version_init` registers a permanent single proc file.

Control flow: each read emits one banner line through seq_file. Init creates `version` under proc root and marks it permanent.

State and persistence behavior: no local state persists. It reads current UTS namespace/system naming data and static kernel banner format.

Dependencies and integration points: depends on UTS name accessors, procfs single-file creation, and seq_file. It is a longstanding userspace ABI for kernel version reporting.

Risks: output format is legacy ABI; changing banner content or newline behavior can break parsers. UTS namespace interactions should match other version/name proc outputs.

Test signals: read `/proc/version`; compare with `uname` fields and kernel build version; check behavior in UTS namespaces; verify permanent entry creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/proc/version.c -->
