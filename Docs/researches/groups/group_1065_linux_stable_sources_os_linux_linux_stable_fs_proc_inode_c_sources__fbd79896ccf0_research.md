# Group Research: group_1065_linux_stable_sources_os_linux_linux_stable_fs_proc_inode_c_sources__fbd79896ccf0

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux-stable`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/inode.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/inode.c

Implements procfs inode allocation, eviction, superblock operations, proc_dir_entry lifetime protection, and generic file-operation dispatch for regular proc entries.

Key points:
- Defines `proc_sops`, backed by proc-specific inode slab allocation/freeing.
- `proc_evict_inode()` tears down PID tracking and sysctl inode associations.
- `proc_invalidate_siblings_dcache()` invalidates dentries tied to sysctl/PDE sibling inode lists across superblocks.
- Uses `proc_dir_entry::in_use` with a negative bias to block new users during removal.
- Tracks open files with custom release hooks via `struct pde_opener`, allowing removal and last close to coordinate exactly one `proc_release()`.
- Wraps `proc_ops` methods for read, read_iter, write, poll, ioctl, compat ioctl, mmap, get_unmapped_area, open, release, and lseek.
- Permanent PDEs bypass runtime `use_pde()` accounting for faster static entries.
- `proc_get_inode()` materializes VFS inodes from PDE metadata and selects file ops based on type, read_iter, and compat ioctl flags.

Dependencies/contracts:
- Consumes `struct proc_dir_entry`, `struct proc_inode`, and `struct pde_opener` from `internal.h`.
- Calls PID cleanup from proc base code and sysctl cleanup from `proc_sysctl.c`.
- Central lifetime layer for dynamically registered proc files.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/proc/internal.h

Internal procfs header shared by proc implementation files.

Key points:
- Defines `struct proc_dir_entry`, including reference counts, openers list, proc ops, seq/single callbacks, rb-tree child directory state, ownership, mode, and inline name storage.
- Defines PDE sizing macros and helpers for permanent entries and optional `proc_ops` capabilities.
- Defines `struct proc_inode`, embedding VFS inode plus PID, PDE, sysctl, namespace, and file-descriptor metadata.
- Provides `PROC_I()`, `PDE()`, `proc_pid()`, and `get_proc_task()` helpers.
- Declares proc root, PID, generic directory, inode, namespace, net, sysctl, tty, self, thread-self, and task memory interfaces.
- Provides mapcount helpers used by page, smaps, kpagecount, and numa reporting.
- Defines `proc_maps_private` and `proc_maps_locking_ctx` shared by MMU/NOMMU task map reporting.

Dependencies/contracts:
- This header is the local ABI between procfs implementation units.
- PDE lifetime fields are tightly coupled to `inode.c`.
- The sysctl inode sibling list is coupled to `proc_sysctl.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/interrupts.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/interrupts.c

Creates `/proc/interrupts`.

Key points:
- Defines a simple seq_file iterator over positions `0..irq_get_nr_irqs()`.
- Delegates formatting to architecture/core IRQ function `show_interrupts`.
- Registers `interrupts` during `fs_initcall`.

Dependencies/contracts:
- Depends on generic IRQ numbering and `show_interrupts()`.
- Read-only proc seq entry.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/interrupts.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/kcore.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/kcore.c

Implements `/proc/kcore`, an ELF core-file view of kernel virtual memory.

Key points:
- Maintains `kclist_head` of memory ranges with types such as RAM, vmalloc, vmemmap, text, and user.
- Computes ELF header, program header, note, and data offsets dynamically.
- Builds ELF notes for PRSTATUS, PRPSINFO, TASKSTRUCT, and VMCOREINFO.
- Updates RAM mappings on memory hotplug through a notifier and `kcore_need_update`.
- Uses a percpu rwsem to protect the kcore range list.
- `read_kcore_iter()` streams ELF metadata and memory contents, zero-filling holes or unsafe pages.
- Avoids unsafe reads using `copy_from_kernel_nofault()`, `vread_iter()`, PFN checks, hwpoison/offline/unaccepted checks, and architecture translation hooks.
- `open_kcore()` requires `CAP_SYS_RAWIO` and passes lockdown check `LOCKDOWN_KCORE`.
- Registers `/proc/kcore` as read-only for root and permanent.

Dependencies/contracts:
- Interacts with memory hotplug, vmalloc, memblock, sparsemem/vmemmap, lockdown, and architecture address translation.
- Security-sensitive memory disclosure surface.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/kcore.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/kmsg.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/kmsg.c

Implements `/proc/kmsg`, exposing the kernel log stream.

Key points:
- `open`, `release`, `read`, and `poll` delegate to `do_syslog()` with `SYSLOG_FROM_PROC`.
- Nonblocking reads return `-EAGAIN` when no unread log data exists.
- Poll waits on `log_wait` and reports readable when unread data exists.
- Registers read-only root entry `kmsg` as permanent.

Dependencies/contracts:
- Uses syslog subsystem semantics and permissions.
- One of the proc entries backed directly by kernel logging infrastructure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/kmsg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/loadavg.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/loadavg.c

Implements `/proc/loadavg`.

Key points:
- Reads avenrun via `get_avenrun()`.
- Formats 1, 5, and 15 minute load averages, running/thread counts, and last PID cursor in the current active PID namespace.
- Registers `loadavg` as a permanent single proc file.

Dependencies/contracts:
- Uses scheduler load accounting and PID namespace IDR cursor.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/loadavg.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/meminfo.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/meminfo.c

Implements `/proc/meminfo`.

Key points:
- Formats global memory, swap, LRU, slab, vmalloc, percpu, hugepage, zswap, CMA, THP, unaccepted memory, balloon, and GPU reclaim counters.
- Computes `Cached` from file pages minus swapcache and buffers.
- Uses `si_meminfo()`, `si_swapinfo()`, `vm_memory_committed()`, `si_mem_available()`, and VM stat counters.
- Provides weak `arch_report_meminfo()` extension hook.
- Registers `meminfo` as a permanent single proc file.

Dependencies/contracts:
- Text ABI consumed heavily by userspace tools.
- Feature-specific fields are gated by kernel config.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/meminfo.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/namespaces.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/namespaces.c

Implements `/proc/<pid>/ns` directory and namespace symlinks.

Key points:
- Builds `ns_entries[]` from enabled namespace types: net, uts, ipc, pid, pid_for_children, user, mount, cgroup, time, and time_for_children.
- Namespace symlink readlink/get_link require `ptrace_may_access(..., PTRACE_MODE_READ_FSCREDS)`.
- `proc_ns_get_link()` resolves to an nsfs path using `ns_get_path()` and `nd_jump_link()`.
- `proc_ns_readlink()` formats namespace names with `ns_get_name()`.
- Lookup and readdir instantiate symlink inodes with `proc_pid_make_inode()`, store `ns_ops`, and use PID dentry operations.
- Directory inode ops use PID getattr and forbid chmod via `proc_nochmod_setattr`.

Dependencies/contracts:
- Security depends on ptrace access checks.
- Bridges procfs PID entries with nsfs namespace file identity.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/namespaces.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/nommu.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/nommu.c

Creates global NOMMU `/proc/maps` for kernel-known memory regions.

Key points:
- Iterates `nommu_region_tree` under `nommu_region_sem`.
- Formats each `vm_region` like a maps line: start/end, permissions, offset, dev, inode, and optional file path.
- Registers `/proc/maps` only in NOMMU builds through `fs_initcall`.

Dependencies/contracts:
- Separate from per-process NOMMU maps in `task_nommu.c`.
- Exposes the flat NOMMU region list.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/nommu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/page.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/page.c

Implements PFN-indexed binary proc files: `/proc/kpagecount`, `/proc/kpageflags`, and optionally `/proc/kpagecgroup`.

Key points:
- `kpage_read()` validates 64-bit alignment and walks PFNs up to `get_max_dump_pfn()`.
- Sparsemem rounds max PFN to section boundary to allow early section memmap inspection.
- `kpagecount` reports mapcount using precise or average folio mapcount helpers.
- `stable_page_flags()` snapshots page/folio state and maps internal flags to stable userspace KPF bits.
- Exports flags for mapped, anon, KSM, compound head/tail, hugetlb, THP, zero page, buddy, offline, pgtable, slab, idle, locked, dirty, LRU, referenced, active, reclaim, swapcache, mlocked, hwpoison, reserved, owner/private, and arch bits.
- `kpagecgroup` reports memory cgroup inode when `CONFIG_MEMCG`.
- All entries are permanent read-only proc files.

Dependencies/contracts:
- Stable binary ABI; consumers index by PFN and read `u64` records.
- Uses page snapshot APIs to reduce races while reporting live page state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/page.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/proc_net.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/proc_net.c

Implements network namespace-aware proc entries and `/proc/<pid>/net`.

Key points:
- `PDE_NET()` obtains the namespace from a proc net directory PDE.
- `seq_open_net()` pins the net namespace and opens seq private state; release drops net refs.
- Provides exported helpers: `proc_create_net_data()`, `proc_create_net_data_write()`, `proc_create_net_single()`, and `proc_create_net_single_write()`.
- Net proc entries force lookup because `/proc/net` can change across `setns(CLONE_NEWNET)`.
- `/proc/<pid>/net` lookup/readdir uses the target task's `nsproxy->net_ns`.
- Per-net init allocates anchor PDE `net->proc_net`, creates `stat`, assigns root uid/gid in the net user namespace, and marks lookup forced.
- Global init creates `/proc/net -> self/net` symlink and registers pernet operations.

Dependencies/contracts:
- Uses net namespace lifetime tracking, seq_file private state, and task namespace access.
- Anchor PDE for `/proc/<pid>/net` is not normally instantiated as its own inode.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/proc_net.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/proc_sysctl.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/proc_sysctl.c

Implements `/proc/sys` sysctl registration, lookup, inode materialization, reads/writes, polling, unregister, namespace links, and boot-time sysctl argument handling.

Key points:
- Maintains sysctl directories as rb-trees of `ctl_node` entries protected by `sysctl_lock`.
- `ctl_table_header` has `used`, `count`, `nreg`, unregister completion, parent, root, set, and sibling inode list state.
- `insert_header()` inserts tables and creates namespace link entries when needed.
- `start_unregistering()` waits for active users, invalidates proc dentries, then erases entries.
- `proc_sys_make_inode()` creates proc inodes for sysctl entries and links them into header inode lists for invalidation/eviction.
- File IO routes through `proc_sys_call_handler()`: checks permission, allocates a kernel buffer, copies write input, runs BPF cgroup sysctl hook, calls the table `proc_handler`, and copies read output.
- Poll support uses `ctl_table_poll`.
- Directory lookup/readdir follows sysctl links and fills dcache entries.
- Dentry ops revalidate/delete on unregister and compare visibility for namespaced sysctls.
- Registration validates table shape, handlers, mode bits, data pointers, maxlen, and scalar handler array restrictions.
- `register_sysctl_mount_point()` supports permanently empty sysctl directories for mount points.
- `do_sysctl_args()` parses kernel command-line sysctl aliases/options by temporarily mounting procfs and writing `/proc/sys/...`.

Dependencies/contracts:
- Central sysctl proc ABI.
- Interacts with BPF cgroup sysctl hooks, security/permission model, proc inode eviction, dcache invalidation, and namespace-specific sysctl sets.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/proc_sysctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/proc_tty.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/proc_tty.c

Implements `/proc/tty` and TTY driver proc integration.

Key points:
- Creates `/proc/tty`, `/proc/tty/ldisc`, and restricted `/proc/tty/driver`.
- `/proc/tty/drivers` lists pseudo drivers first, then registered `tty_driver` entries.
- Holds `tty_mutex` while iterating `tty_drivers`.
- `show_tty_range()` formats driver name, device path, major/minor range, and driver type/subtype.
- `proc_tty_register_driver()` creates per-driver entries under `/proc/tty/driver` when driver supplies `proc_show`.
- `proc_tty_unregister_driver()` removes the per-driver proc entry.
- `/proc/tty/driver` is user-read/execute only to reduce leakage from serial counters.

Dependencies/contracts:
- Used by TTY core registration/unregistration paths.
- Exposes stable `/proc/tty` userspace-visible hierarchy.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/proc_tty.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/root.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/root.c

Implements procfs filesystem registration, mount context parsing, root superblock setup, and root directory behavior.

Key points:
- Defines mount context options: `gid`, `hidepid`, `subset`, and `pidns`.
- `hidepid` accepts numeric or string values: `off`, `noaccess`, `invisible`, `ptraceable`.
- `subset=pid` restricts visible proc content to PID-related subset.
- `pidns=` can accept an nsfs file/path on new mounts, checks `CAP_SYS_ADMIN` in target user namespace and descendant relationship, and cannot be reconfigured.
- `proc_fill_super()` allocates `proc_fs_info`, sets proc superblock flags/magic/ops, creates root inode from `proc_root`, and installs persistent `self` and `thread-self`.
- `proc_reconfigure()` reapplies mutable mount options.
- `proc_kill_sb()` drops pid namespace and frees fs info after anonymous superblock teardown.
- `proc_root_init()` initializes proc caches, special symlinks/directories, net, tty, sysctl, and registers filesystem last.
- Root readdir combines static proc entries first, then PID directories at `FIRST_PROCESS_ENTRY`.
- `proc_root` is the static root PDE.

Dependencies/contracts:
- Mount-time policy root for PID namespace and hidepid behavior.
- Uses `proc_sops` from `inode.c` and generic/PID proc directory handlers.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/root.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/self.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/self.c

Implements persistent `/proc/self` symlink.

Key points:
- `proc_self_get_link()` returns current task TGID in the proc superblock PID namespace.
- Returns `-ENOENT` if current task is not visible in that namespace.
- Allocates link target with GFP mode depending on RCU/dentry context.
- `proc_setup_self()` creates a persistent symlink dentry during superblock fill.
- `proc_self_init()` allocates stable inode number.

Dependencies/contracts:
- Per-mount PID namespace aware.
- Used by proc root setup.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/self.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/softirqs.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/softirqs.c

Implements `/proc/softirqs`.

Key points:
- Formats per-CPU counts for each softirq type.
- Header lists possible CPUs; rows use `softirq_to_name[]` and `kstat_softirqs_cpu()`.
- Registers `softirqs` as a permanent single proc file.

Dependencies/contracts:
- Exposes kernel softirq accounting in the standard text format.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/softirqs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/stat.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/stat.c

Implements `/proc/stat`.

Key points:
- Exports aggregate and per-online-CPU cputime counters.
- Uses `get_cpu_idle_time_us()` and `get_cpu_iowait_time_us()` when available, otherwise falls back to cpustat.
- Includes interrupt totals, per-IRQ counts with gaps zero-filled, context switches, boot time, forks, runnable and iowait task counts, and softirq totals.
- Applies time namespace boot-time adjustment with `timens_sub_boottime()`.
- `stat_open()` sizes seq buffer based on online CPUs and IRQ count.
- Registers `stat` as permanent and uses `seq_read_iter`.

Dependencies/contracts:
- Stable userspace ABI for system accounting tools.
- Uses scheduler, IRQ, cputime, tick, and time namespace data.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/stat.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/task_mmu.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/task_mmu.c

Implements MMU-backed process memory proc files: `/proc/<pid>/maps`, `smaps`, `smaps_rollup`, `clear_refs`, `pagemap`, and `numa_maps`.

Key points:
- `task_mem()`, `task_vsize()`, and `task_statm()` provide process memory summaries for status/statm.
- Shared seq iteration over VMAs uses `proc_maps_private`; with `CONFIG_PER_VMA_LOCK`, plain maps can use per-VMA locks and RCU, while smaps/numa use `mmap_lock`.
- `show_map_vma()` formats maps lines and supports file paths, `[heap]`, `[stack]`, `[vdso]`, arch names, and named anonymous mappings.
- `PROCMAP_QUERY` ioctl on maps returns structured VMA info, optional VMA name, and optional ELF build ID.
- smaps walks PTE/PMD/hugetlb entries and accounts RSS, PSS, dirty/clean, referenced, anonymous, KSM, lazyfree, THP, hugetlb, swap, and locked memory.
- `smaps_rollup` aggregates across VMAs and temporarily releases/reacquires `mmap_lock` under contention with restart logic.
- `clear_refs` supports types 1-5: all, anon, mapped, soft-dirty, and reset high-water RSS; soft-dirty clearing write-protects PTEs/PMDs with MMU notifier/TLB handling.
- `pagemap` exposes binary virtual-page-indexed `u64` records, hides PFNs unless caller has `CAP_SYS_ADMIN` in init user namespace, and reports present, swapped, file/shared-anon, soft-dirty, exclusive, uffd-wp, and guard bits.
- `PAGEMAP_SCAN` ioctl scans ranges by page categories and can optionally write-protect matching pages for userfaultfd async WP.
- `numa_maps` reports policy, file/heap/stack markers, huge status, per-node page counts, dirty/active/writeback/swapcache/mapcount data.

Dependencies/contracts:
- Heavy coupling to mm page table walking, folios, rmap/mapcount, THP, hugetlb, shmem, swap, soft-dirty, userfaultfd, MMU notifiers, NUMA policy, ptrace access, and proc PID lifetime.
- Security-sensitive: pagemap PFN disclosure is capability-gated.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/task_mmu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/task_nommu.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/task_nommu.c

Implements NOMMU process memory accounting and `/proc/<pid>/maps`.

Key points:
- `task_mem()` estimates process memory using VMA, region, mm, fs, files, sighand, and task object sizes; separates shared vs non-shared memory.
- `task_vsize()` sums VMA ranges.
- `task_statm()` estimates resident/statm values from kernel object sizes and regions.
- `nommu_vma_show()` formats per-process maps lines with permissions, offsets, dev/inode, file path, and `[stack]`.
- Seq iteration pins task and mm, takes `mmap_read_lock_killable()`, and iterates VMAs.
- Exposes only `proc_pid_maps_operations`; smaps/pagemap features are MMU-specific.

Dependencies/contracts:
- NOMMU replacement for selected APIs declared in `internal.h`.
- Uses `proc_mem_open()` for ptrace-gated mm access.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/task_nommu.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/thread_self.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/thread_self.c

Implements persistent `/proc/thread-self` symlink.

Key points:
- Link target is `<tgid>/task/<pid>` for the current thread in the proc superblock PID namespace.
- Returns `-ENOENT` if current thread is invisible in that namespace.
- Allocates target buffer with GFP mode appropriate for lookup context.
- `proc_setup_thread_self()` creates persistent symlink dentry during superblock fill.
- `proc_thread_self_init()` allocates stable inode number.

Dependencies/contracts:
- Per-mount PID namespace aware.
- Complements `/proc/self` for thread-specific proc access.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/thread_self.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/uptime.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/uptime.c

Implements `/proc/uptime`.

Key points:
- Sums idle time across possible CPUs using `kcpustat_cpu_fetch()` and `get_idle_time()`.
- Reads boottime with `ktime_get_boottime_ts64()`.
- Applies time namespace adjustment with `timens_add_boottime()`.
- Prints uptime and aggregate idle time with two decimal places.
- Registers `uptime` as a permanent single proc file.

Dependencies/contracts:
- Uses `get_idle_time()` exported by `stat.c`.
- Time namespace aware.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/uptime.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/util.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/util.c

Small proc utility file.

Key points:
- Implements `name_to_int()` for converting dentry qstr names to unsigned integers.
- Rejects leading-zero multi-character names, non-digits, and overflow.
- Returns `~0U` as invalid sentinel.

Dependencies/contracts:
- Used by proc PID/name lookup code to parse numeric directory names.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/util.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/version.c -->
# File Research: sources/os/linux/linux-stable/fs/proc/version.c

Implements `/proc/version`.

Key points:
- Formats `linux_proc_banner` with system name, release, and version from `utsname()`.
- Registers `version` as a permanent single proc file.

Dependencies/contracts:
- Stable text ABI for kernel version reporting.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/proc/version.c -->