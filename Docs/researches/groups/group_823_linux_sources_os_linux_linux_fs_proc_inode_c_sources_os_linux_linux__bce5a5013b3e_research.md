# Group Research: group_823_linux_sources_os_linux_linux_fs_proc_inode_c_sources_os_linux_linux__bce5a5013b3e

Scope: subset A from `Docs/research_subset_a.md`, covering the listed `sources/os/linux/linux/fs/proc` files. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/inode.c -->
# File Research: sources/os/linux/linux/fs/proc/inode.c

## Scope

This file implements procfs inode allocation, eviction, superblock operations, proc directory entry lifetime protection, regular proc file dispatch, symlink handling, and conversion from `struct proc_dir_entry` metadata into live VFS inodes.

## Public And Internal APIs Covered

- Proc inode cache setup: `proc_init_kmemcache()`.
- Superblock operations: `proc_sops`.
- Dentry invalidation helper: `proc_invalidate_siblings_dcache()`.
- Proc entry rundown: `proc_entry_rundown()`.
- Inode construction: `proc_get_inode()`.

## Key Behavior

- Allocates `struct proc_inode`, initializes PID/PDE/sysctl/namespace state, and frees associated PID/PDE references on final inode free.
- Eviction truncates page cache, clears inode state, evicts PID-specific state, and delegates sysctl teardown to `proc_sys_evict_inode()`.
- Dynamic PDE operations are protected with the `in_use` atomic; removal waits for active users and tracked openers with release hooks.
- Regular proc file operations dispatch into `struct proc_ops`, with permanent PDEs bypassing dynamic rundown overhead.
- `proc_get_inode()` applies PDE mode, uid/gid, size, nlink, and selects regular, directory, or symlink operations.

## Risks And Invariants

- Non-permanent PDE methods must only run while `use_pde()` holds the entry active.
- `close_pdeo()` prevents duplicate `proc_release()` calls when final close races PDE deletion.
- `proc_get_inode()` assumes PDE type is regular, directory, or symlink; other modes trigger `BUG()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/internal.h -->
# File Research: sources/os/linux/linux/fs/proc/internal.h

## Scope

This internal header defines procfs private structures, helper accessors, cross-file prototypes, process map private state, and feature stubs used by `fs/proc`.

## Key Structures And APIs

- `struct proc_dir_entry`: in-memory proc tree node with lifetime counters, unload synchronization, operation pointers, metadata, rb-tree links, name storage, and flags.
- `struct proc_inode`: embeds `struct inode` and adds PID, fd, PDE, sysctl, namespace, and sibling-inode state.
- `PROC_I()`, `PDE()`, `proc_pid()`, `get_proc_task()`, `pde_get()`, `is_empty_pde()`, `pde_force_lookup()`.
- `folio_precise_page_mapcount()` and `folio_average_page_mapcount()` for proc memory statistics.
- `struct proc_maps_private` and `struct proc_maps_locking_ctx` for `/proc/<pid>/maps`-style readers.

## Dependencies And Role

- Shared by `inode.c`, `root.c`, `proc_sysctl.c`, `proc_net.c`, `namespaces.c`, `task_mmu.c`, and task/NOMMU variants.
- Provides internal contracts between proc generic entries, PID entries, sysctl entries, network namespace entries, and memory reporting.

## Risks And Invariants

- `proc_dir_entry` lifetime uses several distinct counters and references; callers must use the matching mechanism.
- `PROC_I()` assumes procfs inodes embed `struct proc_inode`.
- `pde_force_lookup()` is critical for namespace-sensitive entries such as `/proc/net`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/interrupts.c -->
# File Research: sources/os/linux/linux/fs/proc/interrupts.c

## Scope

Registers `/proc/interrupts` and supplies a seq_file iterator over IRQ numbers.

## Behavior

- `int_seq_start()` and `int_seq_next()` iterate positions from 0 through `irq_get_nr_irqs()`.
- `.show` delegates formatting to `show_interrupts()`.
- `proc_interrupts_init()` registers the seq entry at `fs_initcall` time.

## Dependencies

- Depends on generic IRQ numbering and architecture/core `show_interrupts()` formatting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/interrupts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/kcore.c -->
# File Research: sources/os/linux/linux/fs/proc/kcore.c

## Scope

Implements `/proc/kcore`, an ELF core-file view of kernel virtual memory built from RAM, vmalloc, vmemmap, optional module, and optional kernel text ranges.

## Public And Internal APIs Covered

- `register_mem_pfn_is_ram()`, `kclist_add()`, `kcore_update_ram()`.
- Read path: `read_kcore_iter()`.
- File ops: `kcore_proc_ops`.
- Init and hotplug: `proc_kcore_init()`, `kcore_callback()`.

## Key Behavior

- Maintains `kclist_head` under `kclist_lock` and computes ELF program-header, note, and data offsets.
- Rebuilds RAM/VMEMMAP kcore entries lazily when memory hotplug marks `kcore_need_update`.
- Emits ELF header, PT_LOAD headers, note segment, then memory data.
- Handles vmalloc via `vread_iter()`, RAM through physical translation and nofault bounce buffer, and holes/inaccessible memory by zero-filling.
- `open_kcore()` requires `CAP_SYS_RAWIO` and passes lockdown `LOCKDOWN_KCORE`.

## Risks And Invariants

- Exposes raw kernel memory and is capability/lockdown gated.
- Must tolerate sparse, offline, hwpoisoned, unaccepted, and unmapped memory.
- File size and kcore list must remain consistent under the percpu rwsem.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/kcore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/kmsg.c -->
# File Research: sources/os/linux/linux/fs/proc/kmsg.c

## Scope

Registers `/proc/kmsg`, a proc interface to the kernel syslog stream.

## Behavior

- Open/release delegate to `do_syslog()` with proc-origin open/close actions.
- Reads return `-EAGAIN` for nonblocking callers when no unread data exists, otherwise use `SYSLOG_ACTION_READ`.
- Poll waits on `log_wait` and reports readability when unread syslog data exists.
- Creates owner-readable permanent `/proc/kmsg`.

## Dependencies

- Depends on syslog core and global `log_wait`; access policy lives in `do_syslog()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/kmsg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/loadavg.c -->
# File Research: sources/os/linux/linux/fs/proc/loadavg.c

## Scope

Implements `/proc/loadavg`.

## Behavior

- Fetches 1, 5, and 15 minute load averages with `get_avenrun()`.
- Emits traditional fields: load averages, runnable/total thread counts, and last PID cursor in the current task active PID namespace.
- Creates a permanent single-show proc entry.

## Dependencies

- Uses scheduler load counters, `nr_running()`, `nr_threads`, and PID namespace IDR cursor state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/loadavg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/meminfo.c -->
# File Research: sources/os/linux/linux/fs/proc/meminfo.c

## Scope

Implements `/proc/meminfo`, the global memory and swap statistics report.

## Behavior

- Gathers `sysinfo`, swap info, committed memory, file cache estimate, LRU counters, available memory, slab counters, and vmstat counters.
- Emits core fields including total/free/available memory, buffers/cache, active/inactive splits, swap, dirty/writeback, anonymous/file/shmem, slab, page tables, commit limit, vmalloc, percpu, balloon, GPU, and hugetlb stats.
- Conditional output covers highmem, NOMMU mmap-copy, zswap, shadow call stack, memory failure, THP, CMA, unaccepted memory, and architecture-specific lines.

## Dependencies

- Depends on VM, swap, LRU, vmstat, hugetlb, zswap, CMA, memory failure, memtest, percpu, and architecture hooks.

## Risks

- Values are sampled from multiple counters without a single global synchronization point.
- Field names and formatting are ABI-sensitive for userspace tools.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/meminfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/namespaces.c -->
# File Research: sources/os/linux/linux/fs/proc/namespaces.c

## Scope

Implements `/proc/<pid>/ns`, including namespace symlinks, readlink, lookup, and directory iteration.

## Behavior

- `ns_entries[]` includes configured namespace operation tables for net, uts, ipc, pid, pid-for-children, user, mount, cgroup, time, and time-for-children.
- Symlink resolution obtains the task, takes `exec_update_lock`, checks ptrace read access, gets the namespace path, and jumps to nsfs.
- `readlink` formats namespace names with `ns_get_name()`.
- Directory iteration and lookup instantiate symlink inodes carrying the chosen `proc_ns_operations`.

## Dependencies And Risks

- Access is gated by `ptrace_may_access(..., PTRACE_MODE_READ_FSCREDS)`.
- Symlink resolution returns `-ECHILD` under unsupported RCU path-walk contexts.
- Task references and `exec_update_lock` must be balanced on all paths.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/namespaces.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/nommu.c -->
# File Research: sources/os/linux/linux/fs/proc/nommu.c

## Scope

Implements NOMMU global region reporting through `/proc/maps`.

## Behavior

- Formats each `vm_region` in maps-like format: address range, permissions, sharing marker, offset, device, inode, and optional path.
- Iterates `nommu_region_tree` under `nommu_region_sem`.
- Registers `/proc/maps` for NOMMU kernels.

## Dependencies

- Depends on NOMMU `vm_region` global tree and semaphore.
- Represents global NOMMU regions, not per-process MMU VMAs.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/nommu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/page.c -->
# File Research: sources/os/linux/linux/fs/proc/page.c

## Scope

Implements physical page inspection proc files: `/proc/kpagecount`, `/proc/kpageflags`, and optional `/proc/kpagecgroup`.

## Behavior

- `kpage_read()` requires 64-bit entry alignment, clamps to max dump PFN, maps PFNs to online pages, and emits count, flags, or memcg inode values.
- `stable_page_flags()` snapshots page/folio state and translates internal flags to stable userspace KPF bits plus pseudo flags.
- `get_kpage_count()` uses precise page mapcount when available, otherwise average folio mapcount.
- Creates owner-readable page diagnostic proc entries at init.

## Dependencies And Risks

- Depends on page snapshots, folios, mapcount helpers, KSM, huge/THP, hugetlb, memcg, page idle, memory hotplug, and kernel-page-flags ABI constants.
- Output is diagnostic and races live page state; ABI bit meanings must remain stable.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/page.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/proc_net.c -->
# File Research: sources/os/linux/linux/fs/proc/proc_net.c

## Scope

Implements network-namespace-aware proc helpers and `/proc/<pid>/net` directory behavior.

## Public APIs

- `proc_create_net_data()`, `proc_create_net_data_write()`.
- `proc_create_net_single()`, `proc_create_net_single_write()`.
- `bpf_iter_init_seq_net()`, `bpf_iter_fini_seq_net()`.
- `proc_net_inode_operations`, `proc_net_operations`.

## Behavior

- Net seq/single open paths pin the relevant `struct net`, allocate seq private state, and store namespace tracking under `CONFIG_NET_NS`.
- Helper creation functions force lookup revalidation, attach net-aware proc ops, and register PDEs.
- `/proc/<pid>/net` lookup/readdir resolves the target task’s network namespace and delegates into that namespace’s proc tree.
- `subset=pid` restricts `/proc/<pid>/net` unless the mounter credential has `CAP_NET_ADMIN` in the network namespace userns.
- Per-net init creates a synthetic `net` PDE anchor and `stat` subdirectory; `/proc/net` is a symlink to `self/net`.

## Risks

- Namespace references must be paired correctly.
- `pde_force_lookup()` is necessary because `/proc/<pid>/net` contents can change after `setns(CLONE_NEWNET)`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/proc_net.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/proc_sysctl.c -->
# File Research: sources/os/linux/linux/fs/proc/proc_sysctl.c

## Scope

Implements `/proc/sys`: sysctl registration, rb-tree directory lookup, proc inode/dentry operations, handler dispatch, polling, namespace/set links, unregister invalidation, and command-line `sysctl.` argument application.

## Public APIs

- Registration: `register_sysctl_mount_point()`, `__register_sysctl_table()`, `register_sysctl_sz()`, `__register_sysctl_init()`, `unregister_sysctl_table()`.
- Poll notification: `proc_sys_poll_notify()`.
- Set lifecycle: `setup_sysctl_set()`, `retire_sysctl_set()`.
- Init and boot args: `proc_sys_init()`, `sysctl_is_alias()`, `do_sysctl_args()`.

## Key Behavior

- Sysctl entries are stored in rb-trees of `ctl_node` objects under `ctl_dir`, protected by `sysctl_lock`.
- Lookup pins headers, follows namespace links when needed, and creates proc inodes tied to `ctl_table_header` and `ctl_table` entries.
- Reads/writes go through `proc_sys_call_handler()`: permission check, kernel buffer allocation, user copy, BPF cgroup sysctl hook, proc handler call, and readback copy.
- Directory iteration fills dcache children and emits dirents from usable rb-tree entries.
- Unregistration waits for active users, invalidates dentries, removes rb-tree nodes, releases namespace links, and RCU-frees headers after references drain.
- Command-line sysctl handling temporarily mounts procfs, opens `sys/<path>`, writes the value, logs errors, and unmounts.

## Risks And Invariants

- `used`, `count`, `nreg`, and `unregistering` have separate lifetime meanings.
- Root does not automatically get write permission to read-only sysctls.
- Permanently empty mount-point headers reject later children.
- Namespace link insertion/removal must stay balanced.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/proc_sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/proc_tty.c -->
# File Research: sources/os/linux/linux/fs/proc/proc_tty.c

## Scope

Implements `/proc/tty`, `/proc/tty/drivers`, `/proc/tty/ldiscs`, and per-driver proc entries under `/proc/tty/driver`.

## Behavior

- `/proc/tty/drivers` iterates `tty_drivers` under `tty_mutex`.
- Output includes pseudo-driver entries for `/dev/tty`, `/dev/console`, optional `/dev/ptmx`, and optional `/dev/vc/0`.
- `proc_tty_register_driver()` creates per-driver proc entries when a driver exposes `proc_show`.
- `proc_tty_unregister_driver()` removes the stored entry.
- Init creates `/proc/tty`, preserved `/proc/tty/ldisc`, restricted `/proc/tty/driver`, and seq entries.

## Risks

- `/proc/tty/driver` is restricted because serial stats can leak password length and timing information.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/proc_tty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/root.c -->
# File Research: sources/os/linux/linux/fs/proc/root.c

## Scope

Implements procfs mount context parsing, superblock creation, reconfiguration, teardown, root directory operations, and global proc root initialization.

## Behavior

- Parses mount parameters `gid=`, `hidepid=`, `subset=`, and `pidns=`.
- `hidepid` accepts numeric values and strings: `off`, `noaccess`, `invisible`, `ptraceable`.
- `subset=` currently supports only `pid`.
- `pidns=` accepts an nsfs PID namespace file/path, checks type, capability, and descendant relationship, then updates fs context namespaces.
- `proc_fill_super()` allocates `proc_fs_info`, sets noexec/nodev/nosuid procfs flags, creates the root inode/dentry, and installs `self` and `thread-self`.
- `proc_root_init()` initializes proc caches, self links, top-level directories/symlinks, net/sys/tty subtrees, then registers procfs.
- Root lookup handles numeric PID directories before generic proc entries; root readdir emits static entries before PID directories.

## Risks And Invariants

- `pidns=` cannot be reconfigured for existing procfs instances.
- `subset=pid` cannot be changed on reconfigure.
- Root process entries start at `FIRST_PROCESS_ENTRY`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/root.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/self.c -->
# File Research: sources/os/linux/linux/fs/proc/self.c

## Scope

Implements the persistent `/proc/self` symlink.

## Behavior

- Resolves current task TGID in the proc superblock PID namespace.
- Formats the symlink target as the TGID decimal string.
- Creates a persistent symlink inode under proc root using `self_inum`.
- Allocates the stable inode number during proc root initialization.

## Risks

- Returns `-ENOENT` when the current task has no TGID in the mounted proc PID namespace.
- Uses atomic allocation mode when required by delayed link resolution context.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/self.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/softirqs.c -->
# File Research: sources/os/linux/linux/fs/proc/softirqs.c

## Scope

Implements `/proc/softirqs`.

## Behavior

- Header lists all possible CPUs.
- Each softirq row prints softirq name and per-CPU counters from `kstat_softirqs_cpu()`.
- Creates a permanent single-show proc entry.

## Dependencies

- Depends on `softirq_to_name`, `NR_SOFTIRQS`, possible CPU iteration, and kernel stat counters.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/softirqs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/stat.c -->
# File Research: sources/os/linux/linux/fs/proc/stat.c

## Scope

Implements `/proc/stat`: aggregate/per-CPU CPU time, IRQ counts, context switches, boot time, fork count, runnable/blocked counts, and softirq counts.

## Behavior

- `get_idle_time()` and iowait helper prefer NO_HZ CPU hooks and fall back to cpustat fields.
- `show_stat()` sums CPU times and IRQ counters over possible CPUs, emits per-online-CPU rows, and applies time namespace boot offset.
- Interrupt output includes total interrupt count and zero-filled gaps for inactive IRQs.
- Emits `ctxt`, `btime`, `processes`, `procs_running`, `procs_blocked`, and softirq totals.
- `stat_open()` sizes the seq buffer based on CPU and IRQ counts.

## Risks

- Values are sampled without a single global lock, so the report is monitoring-grade rather than atomic.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/stat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/task_mmu.c -->
# File Research: sources/os/linux/linux/fs/proc/task_mmu.c

## Scope

Implements MMU process memory proc interfaces: task memory summaries, `/proc/<pid>/maps`, `PROCMAP_QUERY`, `/proc/<pid>/smaps`, `/proc/<pid>/smaps_rollup`, `/proc/<pid>/clear_refs`, `/proc/<pid>/pagemap`, `PAGEMAP_SCAN`, and `/proc/<pid>/numa_maps`.

## Key Behavior

- Task summaries report virtual size, RSS splits, high-water values, locked/pinned memory, code/lib/data/stack, page table bytes, swap, and hugetlb usage.
- Maps iteration pins task/mm and uses mmap lock or per-VMA lock/RCU for plain maps where configured.
- `show_map_vma()` emits maps-compatible ranges and names such as paths, `[heap]`, `[stack]`, `[vdso]`, `[anon:name]`, and `[anon_shmem:name]`.
- `PROCMAP_QUERY` provides structured VMA lookup by address and filters, including VMA flags, file identity, name, and optional build ID.
- Smaps walks page tables to compute RSS, PSS, clean/dirty private/shared memory, referenced, anonymous, KSM, lazyfree, THP, hugetlb, swap, swap PSS, and locked PSS.
- `smaps_rollup` aggregates all VMAs and can drop/reacquire mmap lock under contention while resuming safely.
- `clear_refs` clears referenced/young bits, clears soft-dirty with write-protection and MMU notifier/TLB coordination, or resets high-water RSS.
- Pagemap encodes virtual pages into 64-bit entries and hides PFNs unless the opener has `CAP_SYS_ADMIN` in `init_user_ns`.
- `PAGEMAP_SCAN` classifies and coalesces page ranges, optionally write-protecting matching pages for async userfaultfd.
- NUMA maps reports policy and per-node page placement/statistics per VMA.

## Dependencies

- Depends on MM page walkers, VMA iterators, mmap/per-VMA locking, ptrace-gated `proc_mem_open()`, folios, rmap/mapcount, swap/softleaf entries, shmem, THP, HugeTLB, userfaultfd markers, MMU notifiers, TLB flushing, build-id parsing, mempolicy, and NUMA state.

## Risks And Invariants

- Access is gated through `proc_mem_open()`.
- Page-table-walking interfaces require stronger locking than plain maps.
- Pagemap PFN disclosure is capability-gated.
- Soft-dirty clearing and write-protect scans must coordinate with MMU notifiers and TLB flushing.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/task_mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/task_nommu.c -->
# File Research: sources/os/linux/linux/fs/proc/task_nommu.c

## Scope

Implements NOMMU per-task memory reporting: task memory summaries, virtual size/statm approximations, and `/proc/<pid>/maps`.

## Behavior

- `task_mem()` accounts VMA objects, regions, mm, fs, files, sighand, and task object sizes into private/shared byte totals.
- `task_vsize()` sums VMA ranges.
- `task_statm()` estimates total resident size from object sizes and text/data page counts.
- `nommu_vma_show()` prints maps-compatible VMA rows.
- Maps open stores the proc inode and obtains an mm through `proc_mem_open()`; release drops the mm reference.

## Risks

- NOMMU accounting is approximate and includes kernel object allocation sizes.
- Shared/private classification is based on reference counts and NOMMU shared mapping flags.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/task_nommu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/thread_self.c -->
# File Research: sources/os/linux/linux/fs/proc/thread_self.c

## Scope

Implements the persistent `/proc/thread-self` symlink.

## Behavior

- Resolves current TGID and TID in the mounted proc PID namespace.
- Formats target as `<tgid>/task/<tid>`.
- Creates a persistent symlink inode under proc root using `thread_self_inum`.
- Allocates the stable inode number during proc root initialization.

## Risks

- Returns `-ENOENT` when the current thread has no PID in the mounted proc PID namespace.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/thread_self.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/uptime.c -->
# File Research: sources/os/linux/linux/fs/proc/uptime.c

## Scope

Implements `/proc/uptime`.

## Behavior

- Sums idle time across all possible CPUs using `get_idle_time()`.
- Fetches boottime uptime, applies time namespace boot offset, and emits uptime plus idle time with two decimal places.
- Creates a permanent single-show proc entry.

## Notes

- Idle time can exceed wall-clock uptime on multicore systems.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/uptime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/util.c -->
# File Research: sources/os/linux/linux/fs/proc/util.c

## Scope

Provides decimal dentry-name parsing for proc lookup paths.

## Behavior

- `name_to_int()` converts a `struct qstr` to unsigned integer.
- Rejects leading zeroes in multi-character numbers, non-decimal characters, and overflow.
- Returns `~0U` on failure.

## Risk

- Callers must treat `~0U` as an invalid sentinel.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/proc/version.c -->
# File Research: sources/os/linux/linux/fs/proc/version.c

## Scope

Implements `/proc/version`.

## Behavior

- Formats `linux_proc_banner` with system name, release, and version from `utsname()`.
- Creates a permanent single-show proc entry.

## Dependency

- Depends on UTS/kernel version data and the global proc banner format.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/proc/version.c -->