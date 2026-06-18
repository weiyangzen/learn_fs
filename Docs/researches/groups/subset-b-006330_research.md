# subset-b-006330 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/genpd.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/genpd.py

## Purpose
`genpd.py` registers `lx-genpd-summary`, a GDB view that mirrors `/sys/kernel/debug/pm_genpd/pm_genpd_summary` for generic PM domains. It is intended for live kernel or vmcore debugging where sysfs/debugfs is unavailable.

## Important APIs, Types, and Functions
The script caches `struct generic_pm_domain`, `struct pm_domain_data`, and `struct device_link`. `kobject_get_path()` recursively reconstructs a device kobject path. `rtpm_status_str()` formats runtime PM state from `struct dev_pm_info`. `LxGenPDSummary.summary_one()` prints domain status, child domains from `parent_links`, and devices from `dev_list`.

## Control Flow
`invoke()` checks for `gpd_list`, prints headers, walks the global genpd list through `lists.list_for_each_entry()`, and calls `summary_one()` for each domain. Each domain walk nests a device-link list traversal and a PM-domain device list traversal.

## State and Persistence Behavior
The command is read-only. Its only persistent state is cached GDB type lookup state in `CachedType`; all PM state is read from kernel data structures at invocation time.

## Dependencies and Integration Points
It depends on `linux.utils` and `linux.lists`, plus kernel symbols `gpd_list` and the PM domain structure layout. It integrates into the loader through `vmlinux-gdb.py`.

## Risks and Test Signals
Recursive kobject path reconstruction can fail or recurse deeply if kobject parents are corrupt. Runtime status indexing assumes the kernel enum values match the local string table. Test with a kernel built with genpd users and compare output against debugfs `pm_genpd_summary`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/genpd.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/interrupts.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/interrupts.py

## Purpose
`interrupts.py` implements `lx-interruptlist`, a `/proc/interrupts`-style GDB command for inspecting IRQ descriptors, per-CPU counts, architecture interrupt counters, and clock/error interrupt statistics.

## Important APIs, Types, and Functions
`show_irq_desc()` loads IRQ descriptors from the `sparse_irqs` maple tree, filters hidden/chained/no-count descriptors, and formats chip, hardware IRQ, trigger level, descriptor name, and actions. Architecture helpers include `x86_show_interupts()`, `arm_common_show_interrupts()`, `aarch64_show_interrupts()`, and `arch_show_interrupts()`.

## Control Flow
`LxInterruptList.invoke()` calculates field width from `nr_irqs`, prints CPU headers, iterates IRQ numbers, and appends architecture-specific lines. Descriptor lookup goes through `mapletree.mtree_load()`, then count collection uses `cpus.each_online_cpu()` and `cpus.per_cpu()`.

## State and Persistence Behavior
The script mutates no kernel state. Output is a best-effort snapshot of live counters and descriptor pointers, with no locking or consistency guarantee.

## Dependencies and Integration Points
It depends on generated constants, CPU helpers, maple tree helpers, and kernel IRQ symbols such as `nr_irqs`, `sparse_irqs`, `irq_stat`, `ipi_desc`, and `tick`/machine-check counters depending on architecture.

## Risks and Test Signals
The action-chain loop is fragile around missing `struct irqaction` debug info and corrupted `next` pointers. Architecture support is explicit; unsupported targets raise an error. Test by comparing with `/proc/interrupts` on x86, arm, and arm64 kernels and by exercising sparse IRQ configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/interrupts.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/kasan.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/kasan.py

## Purpose
`kasan.py` registers `lx-kasan_mem_to_shadow`, which translates a kernel memory address to its KASAN shadow address for generic or software-tagged KASAN configurations.

## Important APIs, Types, and Functions
`KasanMemToShadow` lazily initializes `mm.page_ops().ops` and uses `KASAN_SHADOW_SCALE_SHIFT` plus `KASAN_SHADOW_OFFSET` to compute `(addr >> scale) + offset`.

## Control Flow
The command is registered only when KASAN generic or SW tags are configured. `invoke()` validates one hex argument, initializes page operations on first use, computes the shadow address, and prints it.

## State and Persistence Behavior
The command is read-only. It keeps one cached `p_ops` object across invocations, so changes to loaded objfiles or architecture context are not automatically reflected inside this command instance.

## Dependencies and Integration Points
It depends on KASAN constants exposed through `linux.constants` and architecture memory constants assembled in `linux.mm`.

## Risks and Test Signals
The guard condition in `invoke()` mixes `not CONFIG_KASAN_GENERIC` with `or CONFIG_KASAN_SW_TAGS`, which can reject SW-tagged configurations despite registration intent. Validate with known KASAN shadow mappings on arm64 and generic KASAN kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/kasan.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/lists.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/lists.py

## Purpose
`lists.py` provides shared traversal and validation helpers for Linux `list_head` and `hlist` structures, plus the `lx-list-check` diagnostic command.

## Important APIs, Types, and Functions
`list_for_each()` yields node addresses from a circular `struct list_head`. `list_for_each_entry()` wraps nodes with `container_of()`. `hlist_for_each()` and `hlist_for_each_entry()` do the same for `hlist_head`. `list_check()` verifies `prev->next` and `next->prev` integrity.

## Control Flow
Traversal resolves pointer-vs-value inputs, checks type compatibility, handles a null `next` as an uninitialized empty list, then follows links until it reaches the head. `LxListChk.invoke()` parses one expression and calls `list_check()`.

## State and Persistence Behavior
All helpers are read-only and stateless aside from `CachedType` invalidation. Iterators expose live memory directly and do not snapshot the list.

## Dependencies and Integration Points
Many other GDB helpers use this file for task lists, module lists, genpd lists, slab lists, and vmalloc lists. It depends on `linux.utils.container_of()`.

## Risks and Test Signals
Corrupt non-circular lists can loop forever unless a bad pointer triggers `gdb.MemoryError`. `hlist_for_each()` dereferences `first` before checking null-like state. Test with known good lists and intentionally corrupted list fixtures under GDB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/lists.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/mapletree.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/mapletree.py

## Purpose
`mapletree.py` implements enough of Linux maple tree lookup to support GDB commands that need sparse indexed kernel objects, notably IRQ descriptor lookup.

## Important APIs, Types, and Functions
`Mas` models a minimal maple allocation/search state. Low-level helpers decode tagged maple entries: `mte_safe_root()`, `mte_node_type()`, `mte_to_node()`, `mte_dead_node()`, `ma_pivots()`, `ma_slots()`, and `mt_slot()`. `mtree_load()` is the public lookup API.

## Control Flow
`mtree_load()` creates a `Mas`, starts from `ma_root`, handles empty and single-entry roots, then calls `mtree_lookup_walk()` for internal nodes. The walk chooses the first pivot covering the requested index, descends through slots until a leaf, retries if a dead node resets the state, and suppresses xarray zero entries.

## State and Persistence Behavior
The module is read-only. `Mas` is transient per lookup and contains traversal bounds, node, offset, and status copied from kernel state.

## Dependencies and Integration Points
It depends on generated maple constants, xarray tagging helpers, and `CachedType` lookups. `interrupts.py` consumes it for `sparse_irqs`.

## Risks and Test Signals
The implementation covers current 64-bit maple node layouts and dense/range/arange constants; kernel layout drift can break traversal. Type checking is strict but cannot validate logical tree corruption. Test against known maple-tree users such as IRQ descriptors and compare with in-kernel lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/mapletree.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/mm.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/mm.py

## Purpose
`mm.py` supplies architecture-specific memory translation helpers and GDB commands for PFN, physical address, virtual address, `struct page`, and KASAN-tag-aware conversions.

## Important APIs, Types, and Functions
`page_ops` chooses `x86_page_ops` or `aarch64_page_ops` and requires `CONFIG_SPARSEMEM_VMEMMAP`. Both implementations expose `pfn_valid()`, `pfn_to_page()`, `page_to_pfn()`, `virt_to_phys()`, `virt_to_page()`, `page_to_virt()`, `page_address()`, and `folio_address()`. Commands include `lx-pfn_to_page`, `lx-page_to_pfn`, `lx-page_address`, `lx-page_to_phys`, `lx-virt_to_phys`, `lx-virt_to_page`, `lx-sym_to_pfn`, and `lx-pfn_to_kaddr`.

## Control Flow
Each command parses a numeric argument, instantiates `page_ops().ops`, calls the relevant conversion, and prints a result. Architecture constructors read kernel layout symbols such as `page_offset_base`, `vmemmap_base`, `phys_base`, `mem_section`, `memstart_addr`, and arm64 `TCR_EL1`.

## State and Persistence Behavior
Conversion objects cache derived address-space constants during construction. The script does not mutate kernel state. Results are snapshots of current symbol/register state; KASAN tag reset logic affects arm64 address handling.

## Dependencies and Integration Points
`page_owner.py`, `slab.py`, `vmalloc.py`, and `kasan.py` depend on these helpers. Integration requires generated config constants, full debug info for `struct page` and `struct mem_section`, and architecture symbols.

## Risks and Test Signals
The code only supports x86_64 and arm64 sparse vmemmap kernels. Incorrect VA bits, KASAN mode, or page table layout constants will produce plausible but wrong addresses. Test conversion round trips, `pfn_valid()` over holes, arm64 tagged addresses, and known symbol-to-physical translations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/mm.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/modules.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/modules.py

## Purpose
`modules.py` provides module enumeration, lookup, and text-address diagnostics for GDB sessions.

## Important APIs, Types, and Functions
`module_list()` walks the global `modules` list. `find_module_by_name()` matches `struct module.name`. `$lx_module()` returns the matched module object. `lx-lsmod` prints module text base, aggregate memory size, refcount, and source users. `lx-getmod-by-textaddr` maps an address to a module text range.

## Control Flow
Commands use `lists.list_for_each_entry()` over `struct module.list`, then read `module.mem[LX_MOD_*]`, refcounts, and `source_list` entries. Address lookup compares against `LX_MOD_TEXT` base and size.

## State and Persistence Behavior
Read-only. Module state is live target state and may be inconsistent on a running target without stop-the-world debugging.

## Dependencies and Integration Points
`symbols.py` uses `module_list()` for symbol loading. The module memory layout depends on constants generated from the target kernel.

## Risks and Test Signals
No module support returns empty iterators; command output assumes modern `struct module.mem[]` layout. Refcount output subtracts one, matching kernel `lsmod` semantics. Test with loaded modules, users, and addresses inside and outside module text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/modules.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/page_owner.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/page_owner.py

## Purpose
`page_owner.py` registers `lx-dump-page-owner`, a GDB implementation of page-owner inspection for allocation and free stack traces tied to PFNs.

## Important APIs, Types, and Functions
`DumpPageOwner` reads `page_ext`, `page_owner`, `page_owner_ops.offset`, `migrate_reason_names`, and PFN bounds. `lookup_page_ext()`, `page_ext_get()`, and `get_page_owner()` locate metadata. `read_page_owner_by_addr()` prints one PFN; `read_page_owner()` scans allocated pages.

## Control Flow
`invoke()` checks `CONFIG_PAGE_OWNER` and `page_owner_inited`, initializes `mm.page_ops`, reads global bounds, and dispatches either to full scan or `--pfn`. Full scan skips invalid PFN ranges in `MAX_ORDER_NR_PAGES` chunks and jumps by allocation order after a hit.

## State and Persistence Behavior
Read-only. It reconstructs page ownership from persistent kernel `page_ext` state and stackdepot handles; no data is cached across invocations except class fields updated during command execution.

## Dependencies and Integration Points
It depends on `mm.py` for PFN/page conversion and `stackdepot.py` for stack trace printing. It requires page owner, page extension, and stack depot debug symbols/constants.

## Risks and Test Signals
PFN validation and page extension offsets are architecture/config-sensitive. Full scans can be expensive on large memory dumps. Test with a small page-owner-enabled kernel, known allocated PFNs, invalid PFNs, and freed-page records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/page_owner.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/pgtable.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/pgtable.py

## Purpose
`pgtable.py` registers `translate-vm`, an x86 page-table walker that decodes CR3 and the hierarchy entries used to translate a virtual address.

## Important APIs, Types, and Functions
`Cr3` decodes CR3 flags and the root physical address. `PageHierarchyEntry` reads an eight-byte entry, decodes present/RW/user/cache/accessed/dirty/PAT/global/page-size/protection-key/NX bits, and computes either a page physical address or next-level address. `entry_va()` maps physical page-table addresses into the direct map.

## Control Flow
`TranslateVM.invoke()` parses the virtual address, reads `$cr3` and `$cr4`, chooses four or five levels from LA57, prints CR3 information, then repeatedly prints each page hierarchy entry until a leaf or non-present entry.

## State and Persistence Behavior
Read-only. It reads live registers and memory at invocation time; no persistent state survives the command.

## Dependencies and Integration Points
It depends on x86 paging layout, `page_offset_base`, target memory access, and little-endian entry reads. It is loaded by `vmlinux-gdb.py`.

## Risks and Test Signals
The tool is x86-only and uses a narrow `PHYSICAL_ADDRESS_MASK` expression that may not match every CPU physical-address width. It does not handle userspace CR3 PCID masking beyond the current masks. Test with known kernel/user mappings, huge pages, non-present entries, and LA57 kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/pgtable.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/proc.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/proc.py

## Purpose
`proc.py` implements GDB equivalents of selected `/proc` views: command line, version, I/O resources, mounts, and FDT dumping.

## Important APIs, Types, and Functions
Commands include `lx-cmdline`, `lx-version`, `lx-iomem`, `lx-ioports`, `lx-mounts`, and `lx-fdtdump`. Helpers include `get_resources()` for resource trees, `show_lx_resources()`, `info_opts()`, and `LxFdtDump.fdthdr_to_cpu()`.

## Control Flow
Resource commands recursively walk child/sibling `struct resource` trees. `lx-mounts` finds a task by PID, reads its mount namespace, walks the namespace RB tree, reconstructs mount paths through VFS helpers, and formats flags. `lx-fdtdump` reads `initial_boot_params`, validates the FDT magic, dumps the blob to a local file, and reports header fields.

## State and Persistence Behavior
Most commands are read-only. `lx-fdtdump` writes a host-side DTB file; default name is `fdtdump.dtb`. No kernel state is modified.

## Dependencies and Integration Points
It depends on constants, task iteration, list/RB tree helpers, VFS name helpers, and target endianness utilities.

## Risks and Test Signals
Mount path reconstruction cannot call filesystem callbacks and may omit escaping or special proc formatting. FDT dump file creation is host-side and can overwrite the default file. Test against `/proc/cmdline`, `/proc/version`, `/proc/iomem`, `/proc/ioports`, `/proc/mounts`, and a valid `dtc` parse of the dumped DTB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/proc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/radixtree.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/radixtree.py

## Purpose
`radixtree.py` provides GDB helpers for xarray/radix-tree lookup and iteration, including `$lx_radix_tree_lookup()` and `lx-radix-tree`.

## Important APIs, Types, and Functions
`lookup()` resolves a root and descends internal nodes. `load_root()`, `descend()`, `next_chunk()`, `next_slot()`, and `for_each_slot()` implement iteration using `RadixTreeIter`. Internal entries are identified with `LX_RADIX_TREE_INTERNAL_NODE` and retry entries with `LX_XA_RETRY_ENTRY`.

## Control Flow
Lookup handles empty roots, direct single entries at index zero, max-index bounds, and slot descent by shifts. Iteration finds the next non-empty chunk, yields slot addresses, then advances within that chunk until another chunk is needed.

## State and Persistence Behavior
Read-only and stateless except transient iterator objects. It presents live tree contents without locking.

## Dependencies and Integration Points
It depends on xarray/radix constants and `utils.CachedType`. It is used directly by users through the registered command/function and can support other helpers.

## Risks and Test Signals
The code assumes current xarray node layout and tagged pointer conventions. Retry entries and concurrent modification are only minimally handled. Test with known xarrays containing direct entries, internal nodes, empty slots, and high indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/radixtree.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/rbtree.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/rbtree.py

## Purpose
`rbtree.py` implements Linux RB-tree traversal helpers and GDB functions for first, last, next, and previous nodes.

## Important APIs, Types, and Functions
`rb_inorder_for_each()` recursively yields nodes in order. `rb_inorder_for_each_entry()` wraps each node with `container_of()`. `rb_first()`, `rb_last()`, `rb_parent()`, `rb_empty_node()`, `rb_next()`, and `rb_prev()` mirror kernel RB-tree helpers. GDB functions are `$lx_rb_first`, `$lx_rb_last`, `$lx_rb_next`, and `$lx_rb_prev`.

## Control Flow
First/last descend left/right from `root->rb_node`. Next/prev handle child subtrees first and then climb parent pointers encoded in `__rb_parent_color`.

## State and Persistence Behavior
Read-only. Traversal is a direct read of live memory and has no cycle protection beyond pointer semantics.

## Dependencies and Integration Points
`proc.py` and `timerlist.py` use these helpers for mount and timer RB trees. It depends on `utils.container_of()` and type caches.

## Risks and Test Signals
Corrupt trees can recurse indefinitely or produce bad pointer dereferences. `rb_prev()` returns a dereferenced node in one branch and a pointer in another, which can surprise callers. Test first/last/next/prev on empty, single-node, and multi-node trees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/rbtree.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/slab.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/slab.py

## Purpose
`slab.py` provides SLUB debugging commands: `lx-slabinfo` for cache summaries and `lx-slabtrace` for allocation/free site aggregation.

## Important APIs, Types, and Functions
Helpers decode slab folios, object addresses, object indexes, freelist hardening, original allocation size, and `struct track` metadata. `slabtrace()` aggregates locations by call site, stack handle, and wasted bytes. `slabinfo()` prints active objects, total objects, object size, objects per slab, and pages per slab.

## Control Flow
Both commands require `CONFIG_SLUB_DEBUG`. `slabtrace()` finds the named cache, walks node partial/full lists, builds a free-object bitmap from the freelist, skips free objects, reads alloc/free tracks, aggregates locations, and optionally prints stack depot traces. `slabinfo()` walks all caches and per-node partial lists to derive counts.

## State and Persistence Behavior
Read-only. Local aggregation state exists only for the command invocation.

## Dependencies and Integration Points
It depends on list traversal, stack depot, constants, and `mm.page_ops()` for slab address conversion and KASAN tag reset.

## Risks and Test Signals
Freelist decoding must match `CONFIG_SLAB_FREELIST_HARDENED`; corrupted freelists can index outside the bitmap. Full scans are expensive on large caches. Test with SLUB debug enabled, cache names with and without `SLAB_STORE_USER`, and compare `lx-slabinfo` with `/proc/slabinfo`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/slab.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/stackdepot.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/stackdepot.py

## Purpose
`stackdepot.py` decodes stack depot handles and prints stored stack traces through `lx-stack_depot_lookup`.

## Important APIs, Types, and Functions
`stack_depot_fetch()` splits a handle with `union handle_parts`, computes pool index and offset, and returns stack entries plus count from `struct stack_record`. `stack_depot_print()` disassembles each entry address with `gdb.execute("x /i")`.

## Control Flow
The command validates one hex handle, casts it to an unsigned int, fetches entries, and prints instructions for each recorded frame. Invalid pool indexes return empty data; disabled stack depot raises an error.

## State and Persistence Behavior
Read-only and stateless. It reads persistent kernel stack depot pools.

## Dependencies and Integration Points
`page_owner.py` and `slab.py` call `stack_depot_print()`. It depends on `CONFIG_STACKDEPOT`, `stack_pools`, `pools_num`, `stack_depot_disabled`, and handle layout debug info.

## Risks and Test Signals
The output is instruction-oriented, not symbolic backtrace formatting. Handle-part layout drift or pool corruption can lead to wrong offsets. Test with known handles from page owner or SLUB tracks and invalid/zero handles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/stackdepot.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/symbols.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/symbols.py

## Purpose
`symbols.py` registers `lx-symbols`, a symbol loader that reloads vmlinux, loaded module symbols, and optional JITed BPF debug objects.

## Important APIs, Types, and Functions
`LxSymbols` tracks module paths, module files, loaded modules, load breakpoints, BPF monitors, BPF program maps, and temporary debug objects. It implements module file scanning, module section argument construction, `load_module_symbols()`, `load_all_symbols()`, BPF add/remove handlers, and cleanup. s390 helpers handle vmcore KASLR offsets and decompressor state.

## Control Flow
`invoke()` optionally skips s390 decompressor execution, parses paths and `-bpf`, clears previous monitors, reloads vmlinux, loads all module symbols, restores breakpoint enabled state, and installs a module-load breakpoint. With `-bpf`, it creates BPF monitors that add or remove symbol files as BPF ksyms appear.

## State and Persistence Behavior
The command mutates the GDB session state: symbol files are dropped and reloaded, breakpoints are temporarily disabled by GDB and restored, internal loaded-module/BPF dictionaries persist, and temporary BPF debug objects remain until cleanup.

## Dependencies and Integration Points
It integrates with `modules.py`, `bpf.py`, `utils.pagination_off()`, and GDB breakpoint/objfile APIs. It depends on local `.ko`/`.ko.debug` files and kernel module section metadata.

## Risks and Test Signals
Wrong module search paths produce missing symbols; section layout mismatches produce misleading addresses. BPF object cleanup is important to avoid stale temp files. Test module load/unload refresh, s390 vmcore offsets, breakpoint preservation, and BPF JIT symbol add/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/symbols.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/tasks.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/tasks.py

## Purpose
`tasks.py` exposes Linux task iteration, PID lookup, process listing, and `thread_info` lookup for GDB scripts.

## Important APIs, Types, and Functions
`task_lists()` walks `init_task` and each signal thread list. `get_task_by_pid()` returns the first matching task. `$lx_task_by_pid`, `lx-ps`, `$lx_thread_info`, and `$lx_thread_info_by_pid` are registered GDB interfaces. `get_thread_info()` handles both embedded and stack-based `thread_info`.

## Control Flow
Task traversal iterates every thread in each thread group through `signal.thread_head`, then advances the global process list through `task.tasks.next`. Commands format task address, PID, and `comm`, or return thread info.

## State and Persistence Behavior
Read-only. Results reflect the stopped target's current task lists with no locking or snapshot.

## Dependencies and Integration Points
It depends on `lists.py` and `utils.container_of()`. `proc.py` uses `get_task_by_pid()` for mount namespace lookup.

## Risks and Test Signals
Corrupt task lists can loop or dereference invalid pointers. PID namespaces are not modeled; lookup compares raw `task_struct.pid`. Test with multi-threaded processes, kernel threads, PID 1, and architectures with embedded versus stack `thread_info`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/tasks.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/timerlist.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/timerlist.py

## Purpose
`timerlist.py` implements `lx-timerlist`, a GDB version of `/proc/timer_list` for hrtimer bases, active timers, tick devices, and broadcast masks.

## Important APIs, Types, and Functions
`ktime_get()` reads the monotonic timekeeper base. `print_timer()`, `print_active_timers()`, `print_base()`, `print_cpu()`, `print_tickdevice()`, and `pr_cpumask()` format timer queues and clock event devices.

## Control Flow
`invoke()` reads `hrtimer_bases` and `HRTIMER_MAX_CLOCK_BASES`, prints current time, walks online CPUs and clock bases, traverses active timer RB trees via `rbtree.rb_next()`, then prints broadcast/per-CPU tick device data when configured.

## State and Persistence Behavior
Read-only. Time and timer queues are sampled without locking, so deltas are approximate and intended for debugging.

## Dependencies and Integration Points
It depends on generated timer/tick constants, CPU helpers, RB-tree traversal, and memory-reading utilities for cpumasks.

## Risks and Test Signals
`ktime_get()` omits hardware counter deltas, so relative expiry data is approximate. `pr_cpumask()` formatting is sensitive to byte ordering and CPU count. Test against `/proc/timer_list` on high-res, nohz, and broadcast-tick configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/timerlist.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/utils.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/utils.py

## Purpose
`utils.py` is the shared foundation for the Linux GDB helper suite: type caching, `container_of`, endian-aware memory reads, architecture and gdbserver detection, vmcore parsing, vmlinux lookup, and pagination control.

## Important APIs, Types, and Functions
`CachedType` caches GDB type lookups and invalidates on new objfiles. Scalar type getters expose common kernel types. `container_of()` and `$container_of()` compute enclosing structures. `read_u16/u32/u64/ulong/atomic_long()` decode target memory. `is_target_arch()`, `get_gdbserver_type()`, `qemu_phy_mem_mode()`, `parse_vmcore()`, `get_vmlinux()`, and `pagination_off()` support higher-level commands.

## Control Flow
Helpers are called directly by other modules. Type caching lazily resolves types and attaches a one-shot new-objfile handler. `qemu_phy_mem_mode()` and `pagination_off()` are context managers that save state, apply a temporary mode, and restore it.

## State and Persistence Behavior
Global caches store type, endianness, architecture, and gdbserver detection results. These are GDB-session state only; target kernel memory is not modified.

## Dependencies and Integration Points
Almost every helper imports this module. It relies on Python GDB APIs, inferior memory reads, monitor packets for QEMU physical-memory mode, and objfile metadata.

## Risks and Test Signals
`offset_of()` uses a null pointer expression and string parsing; unusual GDB formatting can break it. Cached endianness/architecture may go stale if the target changes. Test type invalidation after `symbol-file`, memory read decoding on big/little endian targets, and QEMU/KGDB detection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/utils.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/vfs.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/vfs.py

## Purpose
`vfs.py` provides GDB functions for VFS object naming: full dentry path reconstruction and inode-to-dentry lookup.

## Important APIs, Types, and Functions
`dentry_name()` recursively walks `d_parent` and concatenates `d_name.name`. `$lx_dentry_name()` returns that path. `$lx_i_dentry()` returns the dentry containing an inode's first `i_dentry` hlist node via `container_of()`.

## Control Flow
Dentry naming stops at self-parented or null parents. Inode lookup checks `i_dentry.first`; empty lists return an empty string, otherwise it computes the enclosing `struct dentry`.

## State and Persistence Behavior
Read-only and stateless. It samples live VFS objects without taking locks.

## Dependencies and Integration Points
`proc.py` uses `dentry_name()` for mount path reconstruction. The file depends on `utils.container_of()` and `struct dentry` layout.

## Risks and Test Signals
Recursive path building can loop on corrupt parent pointers and does not escape names like `/proc` output does. Inodes with multiple dentries only return the first. Test with root dentries, nested paths, deleted dentries, and inodes with no dentry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/vfs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/vmalloc.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/vmalloc.py

## Purpose
`vmalloc.py` implements `lx-vmallocinfo`, a GDB view of busy vmalloc/vmap areas similar to `/proc/vmallocinfo`.

## Important APIs, Types, and Functions
`is_vmalloc_addr()` uses `mm.page_ops()` to compare tag-reset addresses against architecture `VMALLOC_START/END`. `LxVmallocInfo.invoke()` walks `vmap_nodes[i].busy.head` and formats either `vm_map_ram` areas or full `struct vm_struct` metadata.

## Control Flow
The command requires `CONFIG_MMU`, iterates all `nr_vmap_nodes`, walks each busy list, prints ranges, size, caller, page count, physical address, flags, and whether `pages` itself is vmalloc-backed.

## State and Persistence Behavior
Read-only. It reflects current vmap allocator state without synchronization.

## Dependencies and Integration Points
It depends on list traversal, vmalloc constants, and memory-layout helpers from `mm.py`.

## Risks and Test Signals
The vmap node layout is kernel-version sensitive. Corrupt busy lists or stale `vm` pointers can break formatting. Test by comparing with `/proc/vmallocinfo`, including `ioremap`, `vmalloc`, `vmap`, `usermap`, and `vm_map_ram` entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/vmalloc.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/xarray.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/linux/xarray.py

## Purpose
`xarray.py` contains small tagged-entry predicates used by radix tree and maple tree helpers.

## Important APIs, Types, and Functions
`xa_is_internal()` checks low tag bits, `xa_mk_internal()` constructs an internal entry, `xa_is_zero()` detects the zero entry, and `xa_is_node()` detects node-like internal entries above the low-address threshold.

## Control Flow
Each helper casts the GDB value to unsigned long and applies xarray tag constants and bit masks.

## State and Persistence Behavior
No state is stored or modified.

## Dependencies and Integration Points
`mapletree.py` uses `xa_is_node()` and `xa_is_zero()`. `radixtree.py` carries related xarray retry-entry logic. The file depends on `utils.get_ulong_type()`.

## Risks and Test Signals
Tagged pointer conventions are architecture and kernel-layout dependent. Test with known xarray zero entries, retry entries, direct values, and node pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/linux/xarray.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/vmlinux-gdb.py -->
# sources/distributed-fs/ceph-client/scripts/gdb/vmlinux-gdb.py

## Purpose
`vmlinux-gdb.py` is the entry loader for the Linux kernel GDB helper suite. It updates `sys.path`, verifies GDB capability, rejects reduced debug info, and imports helper modules for command registration.

## Important APIs, Types, and Functions
The file has no exported functions. Its behavior is import side effects: importing `linux.constants`, `utils`, `symbols`, `modules`, `dmesg`, `tasks`, `config`, `cpus`, `lists`, `rbtree`, `proc`, `timerlist`, `clk`, `genpd`, `device`, `vfs`, `pgtable`, `radixtree`, `interrupts`, `mm`, `stackdepot`, `page_owner`, `slab`, `vmalloc`, and `kasan`.

## Control Flow
It inserts the scripts directory, probes minimal GDB Python expression/execution support, then imports modules. If `CONFIG_DEBUG_INFO_REDUCED` is true, it raises because type-complete scripts would be unreliable.

## State and Persistence Behavior
It mutates the Python import path and registers many GDB commands/functions through imported module side effects.

## Dependencies and Integration Points
This is sourced by GDB when debugging vmlinux and is the integration point for all listed GDB helpers.

## Risks and Test Signals
The script references `sys` and `gdb` without importing them locally, relying on GDB's execution environment. Path construction assumes the kernel scripts layout. Test by sourcing it in GDB with full and reduced debug-info kernels and checking command registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gdb/vmlinux-gdb.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gen-btf.sh -->
# sources/distributed-fs/ceph-client/scripts/gen-btf.sh

## Purpose
`gen-btf.sh` generates BTF data for a target ELF, handling the different final embedding/linking flows for vmlinux and modules.

## Important APIs, Types, and Functions
Shell functions include `usage()`, `is_enabled()`, `gen_btf_data()`, `gen_btf_o()`, `embed_btf_data()`, and `cleanup()`. Inputs are environment tools/flags such as `PAHOLE`, `RESOLVE_BTFIDS`, `OBJCOPY`, `CC`, `KBUILD_*`, `CLANG_FLAGS`, `objtree`, and optional `--btf_base`.

## Control Flow
Argument parsing sets `BTF_BASE`; absence means vmlinux mode, presence means module mode. `gen_btf_data()` runs pahole into detached `.BTF.1`, then `resolve_btfids` to produce `.BTF` and related data. Vmlinux mode builds a relocatable `.btf.o`; module mode objcopies `.BTF` and optional `.BTF.base`/`.BTF_ids` into the module and patches IDs.

## State and Persistence Behavior
It writes temporary and final files adjacent to the ELF. `trap cleanup EXIT` removes intermediate `.BTF.1`, `.BTF`, and module-only side files, leaving vmlinux `.btf.o`/`.BTF_ids` or modified module ELF.

## Dependencies and Integration Points
Consumed by kernel build/link flows, especially `link-vmlinux.sh` and module post-processing. It depends on pahole, resolve_btfids, objcopy, compiler, and config auto.conf.

## Risks and Test Signals
Big-endian ET_REL patching writes raw ELF header bytes and must stay correct. Module mode mutates the input ELF. Test vmlinux and module paths, big-endian config, missing `.BTF_ids`, and verbose build logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gen-btf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gen-crc-consts.py -->
# sources/distributed-fs/ceph-client/scripts/gen-crc-consts.py

## Purpose
`gen-crc-consts.py` emits C constants and tables for CRC variants, including slice-by-N tables, RISC-V carryless multiplication constants, and x86 PCLMUL folding constants.

## Important APIs, Types, and Functions
Polynomial helpers include `xor()`, `clmul()`, `div()`, `reduce()`, `bitreflect()`, and `fmt_poly()`. `CrcVariant` normalizes CRC width, polynomial, and bit order. Generators are `gen_slicebyN_tables()`, `gen_riscv_clmul_consts()`, and `gen_x86_pclmul_consts()`.

## Control Flow
The script expects two arguments: comma-separated constant types and comma-separated CRC variants like `crc32_lsb_0xedb88320`. It prints a generated-file header, parses variants, then dispatches each requested constant type to the matching generator.

## State and Persistence Behavior
It is a pure stdout generator with no file writes. All state is local polynomial arithmetic and generated text.

## Dependencies and Integration Points
It is intended for kernel build-time generation of CRC implementation data. Consumers compile the emitted C declarations into architecture-specific CRC code.

## Risks and Test Signals
The math is bit-order sensitive; wrong reflection or omitted high polynomial term produces silent incorrect CRCs. Argument validation uses assertions and exceptions rather than friendly diagnostics. Test generated constants against known CRC test vectors for each variant and against independent table/folding implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gen-crc-consts.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gen-randstruct-seed.sh -->
# sources/distributed-fs/ceph-client/scripts/gen-randstruct-seed.sh

## Purpose
`gen-randstruct-seed.sh` creates a random seed file and a hashed-seed C header definition for randstruct builds.

## Important APIs, Types, and Functions
It reads 32 bytes from `/dev/urandom` via `od`, strips whitespace, writes the raw hex seed to `$1`, hashes that seed with `sha256sum`, and writes `#define RANDSTRUCT_HASHED_SEED "..."` to `$2`.

## Control Flow
There is no argument validation; positional arguments are expected to be output paths.

## State and Persistence Behavior
The script writes two host files and consumes system randomness. Re-running changes both outputs and therefore affects randomized layout reproducibility.

## Dependencies and Integration Points
It depends on POSIX shell plus `od`, `tr`, `sha256sum`, and `cut`. It integrates with randstruct plugin/build logic that needs a private seed and a non-secret hash.

## Risks and Test Signals
Missing arguments can redirect into empty path errors. Tool availability differs on non-GNU systems. Test output length, hash consistency with the seed file, and build reproducibility when the seed is preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gen-randstruct-seed.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gen_packed_field_checks.c -->
# sources/distributed-fs/ceph-client/scripts/gen_packed_field_checks.c

## Purpose
`gen_packed_field_checks.c` is a host generator that emits C preprocessor macros for checking packed fields up to `MAX_PACKED_FIELD_SIZE`.

## Important APIs, Types, and Functions
`main()` prints `CHECK_PACKED_FIELDS_1`, recursive `CHECK_PACKED_FIELDS_N` macros for `N=2..50`, and a dispatcher macro `CHECK_PACKED_FIELDS(fields)` using nested `__builtin_choose_expr()` on `ARRAY_SIZE(fields)`.

## Control Flow
The first macro directly checks index zero. Each later macro wraps the previous one in `do { ... } while (0)` and adds the next index. The dispatcher selects the matching macro or emits a `BUILD_BUG_ON_MSG` for arrays larger than the generator supports.

## State and Persistence Behavior
The program writes generated text to stdout and has no persistent state.

## Dependencies and Integration Points
It depends on host C compilation and kernel macros available to the generated output (`ARRAY_SIZE`, `CHECK_PACKED_FIELD`, `BUILD_BUG_ON_MSG`).

## Risks and Test Signals
The maximum size is hard-coded to 50; consumers with larger arrays must regenerate with a higher constant. Test by compiling the generated header, exercising boundary sizes 1, 50, and 51.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gen_packed_field_checks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/Makefile -->
# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/Makefile

## Purpose
The `gendwarfksyms/Makefile` builds the host-side `gendwarfksyms` utility used for DWARF-derived symbol version generation.

## Important APIs, Types, and Functions
It defines `hostprogs-always-y += gendwarfksyms` and lists component objects: `gendwarfksyms.o`, `cache.o`, `die.o`, `dwarf.o`, `kabi.o`, `symbols.o`, and `types.o`.

## Control Flow
Kbuild host tooling compiles the listed C files and links them into the host program whenever this script directory is built.

## State and Persistence Behavior
Build outputs are host binaries/objects managed by Kbuild. The Makefile itself has no runtime state.

## Dependencies and Integration Points
The component sources depend on elfutils/libdw/libdwfl, libelf, zlib, and kernel host helper headers such as `hash.h` and `hashtable.h`.

## Risks and Test Signals
Missing host libraries or Kbuild host flags will fail the build. Test by invoking the scripts host build and running the resulting binary on example objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/cache.c -->
# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/cache.c

## Purpose
`cache.c` implements a small integer cache used by `gendwarfksyms` for repeated address/file/expansion lookups.

## Important APIs, Types, and Functions
`struct cache_item` stores an unsigned long key, int value, and hash node. `cache_set()`, `cache_get()`, `cache_init()`, and `cache_free()` manage a hashtable embedded in `struct cache`.

## Control Flow
Callers initialize a cache, insert key/value pairs, query by key with `-1` as miss, and free all entries when a processing phase ends.

## State and Persistence Behavior
Cache state is process-local and heap-backed. There is no deduplication in `cache_set()`, so repeated keys can create multiple entries; `cache_get()` returns the first matching entry in the hash chain.

## Dependencies and Integration Points
Used by DWARF processing for source-file privacy caching and expansion-cycle detection. It depends on kernel-style hashtable macros and `xmalloc()`.

## Risks and Test Signals
Using `-1` as a miss sentinel means cached values must not need negative data. Duplicate keys can waste memory or hide newer values. Test insert/get/free, miss behavior, duplicate-key semantics, and leak checks under repeated CU processing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/die.c -->
# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/die.c

## Purpose
`die.c` owns the DWARF DIE cache for `gendwarfksyms`, storing partially and fully rendered type fragments keyed by DIE address and processing state.

## Important APIs, Types, and Functions
The central map is `{die->addr, enum die_state} -> struct die`. `die_map_get()` creates or returns a cache entry. `die_map_add_string()`, `die_map_add_linebreak()`, and `die_map_add_die()` append render fragments. `die_map_for_each()` and `die_map_free()` support later type expansion and cleanup.

## Control Flow
DWARF walkers request cache entries for desired states, append fragments while rendering, and mark states in `dwarf.c`. Later `types.c` iterates the map to build type strings. Cleanup frees fragment strings, FQNs, and cache entries while reporting debug statistics.

## State and Persistence Behavior
The die map is global process state for one `gendwarfksyms` run across processed CUs/objects until freed. It persists rendered fragments and FQNs to avoid repeated DWARF walks.

## Dependencies and Integration Points
It is used heavily by `dwarf.c` and `types.c`, and depends on kernel list/hashtable helpers and allocation wrappers.

## Risks and Test Signals
State identity relies on DIE addresses being stable and meaningful within libdw objects. Incorrect state transitions can reuse incomplete strings. Test duplicate DIE reuse, complete vs unexpanded entries, FQN ownership, and cleanup under `--dump-die-map`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/die.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/dwarf.c -->
# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/dwarf.c

## Purpose
`dwarf.c` walks DWARF compile units, finds exported symbols, renders their type signatures into canonical fragments, resolves fully qualified names, and applies stable kABI interpretation rules while populating the DIE map.

## Important APIs, Types, and Functions
Attribute helpers read DWARF strings, flags, udata, and references. Type processors cover base, typedef, modifiers, pointers, arrays, subroutines, structures/classes/unions, variants, enumerations, members, parameters, and unspecified assembly types. `process_cu()` is the entry point. kABI support includes reserved, ignored, renamed, declaration-only, byte-size, enumerator, and type-string behavior.

## Control Flow
`process_cu()` first resolves FQNs by recursively visiting scopes. It then scans namespaces/classes/structures for exported `DW_TAG_subprogram` and `DW_TAG_variable` DIEs matching the symbol table, initializes per-symbol expansion state, and renders a symbol cache. Missing external symbols can be represented by `__gendwarfksyms_ptr_` pointer DIEs and processed after the CU scan.

## State and Persistence Behavior
It writes global DIE-map entries, symbol DIE addresses, pointer fallback DIE addresses, and per-symbol expansion caches. Private `.c` definitions can be treated as declarations to avoid versioning private implementation details.

## Dependencies and Integration Points
It depends on libdw, `symbols.c`, `die.c`, `cache.c`, `kabi.c`, and `types.c`. Its output fragments are later expanded and CRC'd by `generate_symtypes_and_versions()`.

## Risks and Test Signals
DWARF layout differences across compilers are high risk. Recursion and expansion suppression must avoid cycles while still detecting ABI-relevant nested changes. kABI union conventions are policy-sensitive. Test with GCC/Clang/Rust-like linkage names, examples in `examples/kabi_ex.h`, symbol pointer fixtures, private `.c` definitions, anonymous scopes, and `--stable`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/dwarf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/examples/kabi.h -->
# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/examples/kabi.h

## Purpose
`examples/kabi.h` provides userspace-testable macros that emit `gendwarfksyms` kABI rules and demonstrate ABI-preserving structure evolution patterns.

## Important APIs, Types, and Functions
Rule macros emit strings into `.discard.gendwarfksyms.kabi_rules`: `KABI_DECLONLY`, `KABI_ENUMERATOR_IGNORE`, `KABI_ENUMERATOR_VALUE`, `KABI_BYTE_SIZE`, and `KABI_TYPE_STRING`. Layout macros include `KABI_RESERVE`, `KABI_RESERVE_ARRAY`, `KABI_IGNORE`, `KABI_REPLACE`, `KABI_USE`, `KABI_USE2`, and `KABI_USE_ARRAY`.

## Control Flow
The macros expand at compile time into static used section entries or unions with static assertions that replacement fields fit the reserved size/alignment.

## State and Persistence Behavior
The header contributes ELF section data consumed by `kabi.c`; it does not create runtime state in the tested program.

## Dependencies and Integration Points
It mirrors kernel-style kABI macro patterns and is included by `kabi_ex.h` examples.

## Risks and Test Signals
Correctness depends on developers preserving actual ABI compatibility; the macros can hide version changes but cannot prove semantic safety. Test by compiling example objects and checking emitted stable output with FileCheck.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/examples/kabi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/examples/kabi_ex.c -->
# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/examples/kabi_ex.c

## Purpose
`examples/kabi_ex.c` instantiates variables for the kABI example types so DWARF contains concrete exported-like symbols to inspect.

## Important APIs, Types, and Functions
It includes `kabi_ex.h` and defines global variables of `struct s`, `enum e`, `ex0*` through `ex5*`, and integer `ex6a`.

## Control Flow
There is no executable control flow; the declarations force compiler emission of DWARF type information.

## State and Persistence Behavior
The compiled object contains global symbols and DWARF/debug section state used by example validation.

## Dependencies and Integration Points
The file is consumed by the documented example commands in `kabi_ex.h`, often piping `nm` output into `gendwarfksyms --stable`.

## Risks and Test Signals
Compiler optimization/debug flags can affect DWARF emission. Test with `gcc -g -c examples/kabi_ex.c` and the FileCheck commands documented in the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/examples/kabi_ex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/examples/kabi_ex.h -->
# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/examples/kabi_ex.h

## Purpose
`examples/kabi_ex.h` is an executable specification for stable kABI features. It defines example types and embeds FileCheck expectations for `--dump-dies` and `--dump-versions`.

## Important APIs, Types, and Functions
The header exercises declaration-only rules, ignored/overridden enumerators, reserved fields, reserved arrays, ignored hole fields, replacement fields, byte-size overrides, type-string overrides, and type strings for non-existent types or symbols.

## Control Flow
At compile time it defines structures/enums and static assertions proving replacement layouts remain size-compatible. At test time the comments drive FileCheck over `gendwarfksyms` output.

## State and Persistence Behavior
It emits kABI rule section entries through macros from `kabi.h` and creates type DWARF for the example object.

## Dependencies and Integration Points
It depends on `kabi.h`, `kabi_ex.c`, `nm`, `gendwarfksyms`, and FileCheck for validation.

## Risks and Test Signals
Expectations can be compiler-sensitive, especially type spelling (`unsigned long` variants) and DWARF member ordering. It is the primary regression signal for stable kABI rendering behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/examples/kabi_ex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/examples/symbolptr.c -->
# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/examples/symbolptr.c

## Purpose
`examples/symbolptr.c` demonstrates `__gendwarfksyms_ptr_` fallback symbols used when an exported symbol lacks direct DWARF type information.

## Important APIs, Types, and Functions
`__GENDWARFKSYMS_EXPORT(sym)` creates a used pointer variable in `___gendwarfksyms_ptr+sym` with `typeof(sym) *`. The file declares/defines function and pointer symbols `f`, `g`, and `p`.

## Control Flow
There is no runtime flow. The section variables force the compiler to emit pointer type information that `symbols.c` and `dwarf.c` can associate with exports.

## State and Persistence Behavior
Compiled objects contain special section symbols and DWARF pointer types used during version generation.

## Dependencies and Integration Points
It integrates with `SYMBOL_PTR_PREFIX` handling in `gendwarfksyms.h`, `symbols.c`, and `dwarf.c`.

## Risks and Test Signals
The pointer symbol must have the same type as the exported symbol. Test that `gendwarfksyms` can version symbols absent from direct DWARF by using the pointer fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/examples/symbolptr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/gendwarfksyms.c -->
# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/gendwarfksyms.c

## Purpose
`gendwarfksyms.c` is the command-line driver for the DWARF-based symbol version generator.

## Important APIs, Types, and Functions
Global flags include `debug`, `dump_dies`, `dump_die_map`, `dump_types`, `dump_versions`, `stable`, and `symtypes`. `usage()`, `process_module()`, and `main()` orchestrate reading exports, processing object files, optional symtypes output, and cleanup.

## Control Flow
`main()` parses options, reads exported symbol names from stdin, opens an optional symtypes file, then for each input object opens it, reads symbol addresses, reads kABI rules, reports it to libdwfl, walks modules/CUs via `process_module()`, and finally generates symtypes/versions and prints `#SYMVER` lines.

## State and Persistence Behavior
The process accumulates global symbol, DIE, type, and kABI maps across input objects. It writes optional symtypes output and stdout symbol-version records, then frees maps before exit.

## Dependencies and Integration Points
It depends on libdwfl callbacks, libelf file descriptors, `symbols.c`, `kabi.c`, `dwarf.c`, `types.c`, and host build infrastructure.

## Risks and Test Signals
Partial processing across multiple objects can produce duplicate or overridden versions. File descriptor and DWFL lifetime handling must stay balanced. Test malformed arguments, missing exports, multiple object files, `--stable`, `--symtypes`, and all dump options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/gendwarfksyms.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/gendwarfksyms.h -->
# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/gendwarfksyms.h

## Purpose
`gendwarfksyms.h` defines shared state, diagnostics, type declarations, and cross-module APIs for the `gendwarfksyms` utility.

## Important APIs, Types, and Functions
It declares global flags, diagnostic macros, check macros, DWARF tag aliases, `SYMBOL_PTR_PREFIX`, symbol state/types, DIE state/fragments, the generic cache, expansion/kABI processing state, and public functions from `symbols.c`, `die.c`, `cache.c`, `dwarf.c`, `types.c`, and `kabi.c`.

## Control Flow
The header does not execute control flow, but its macros standardize error handling: `error()` exits, `warn()` reports, and `check()`/`checkp()` turn nonzero or negative results into fatal errors.

## State and Persistence Behavior
It defines the contracts for global process state: symbol maps, DIE maps, caches, expansion state, and kABI rule maps.

## Dependencies and Integration Points
It includes DWARF/libdwfl/libelf-facing headers and kernel host helpers (`hash.h`, `hashtable.h`, `xalloc.h`), making it the central interface for all C files in the directory.

## Risks and Test Signals
Macro names can shadow variables, especially `debug`. Enum bounds must match cleanup/stat loops. Test by compiling with warnings and running all example modes to exercise each declared API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/gendwarfksyms.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/kabi.c -->
# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/kabi.c

## Purpose
`kabi.c` reads and serves stable kABI rule metadata emitted into ELF section `.discard.gendwarfksyms.kabi_rules`.

## Important APIs, Types, and Functions
Rules are versioned four-field records: version, type, target, value. Supported tags are `declonly`, `enumerator_ignore`, `enumerator_value`, `byte_size`, and `type_string`. Public query APIs include `kabi_is_declonly()`, `kabi_is_enumerator_ignored()`, `kabi_get_enumerator_value()`, `kabi_get_byte_size()`, `kabi_get_type_string()`, and `kabi_free()`.

## Control Flow
`kabi_read_rules()` returns immediately unless `--stable` is enabled. It opens the ELF, finds the rule section, validates size/null termination/version/type fields, copies target/value strings into a hash map, and leaves queries to lookup by type and target.

## State and Persistence Behavior
The rule map is global process state until `kabi_free()`. Rules from multiple files can accumulate during a run.

## Dependencies and Integration Points
`dwarf.c` uses declaration, enumerator, and byte-size rules while rendering. `types.c` uses type-string overrides during type expansion/versioning.

## Risks and Test Signals
Malformed rule sections are fatal. Duplicate rules are not explicitly rejected, so lookup order can matter. Numeric values are decimal-only via `strtoul()`. Test missing section, bad version, every rule type, duplicate rules, and examples from `kabi_ex.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/kabi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/symbols.c -->
# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/symbols.c

## Purpose
`symbols.c` manages the exported-symbol table, ELF symbol address resolution, pointer fallback matching, and final `#SYMVER` output.

## Important APIs, Types, and Functions
It maintains hash maps by symbol name and by `{section,address}`. Public APIs include `symbol_read_exports()`, `symbol_read_symtab()`, `symbol_get()`, `symbol_set_ptr()`, `symbol_set_die()`, `symbol_set_crc()`, `symbol_for_each()`, `symbol_print_versions()`, `symbol_free()`, and `is_symbol_ptr()`.

## Control Flow
Exports are read from stdin into unprocessed symbols. ELF global symbols set section/address data. DWARF processing marks DIE or pointer DIE addresses. Type expansion sets CRCs, propagating the same CRC to address aliases. Version printing warns for symbols that never reached processed state.

## State and Persistence Behavior
The symbol maps are global heap state for the process. `state`, `crc`, `addr`, `die_addr`, and `ptr_die_addr` persist across object/CU processing until freed.

## Dependencies and Integration Points
It depends on libelf/gelf, kernel hash helpers, and `gendwarfksyms.h`. `dwarf.c` queries and mutates symbol state; `types.c` finalizes CRCs.

## Risks and Test Signals
Alias propagation by address can override versions and emits warnings. Symbols without debug info depend on `__gendwarfksyms_ptr_` naming. Test duplicate exports, aliases, undefined symbols, `SHT_SYMTAB_SHNDX`, pointer fallbacks, and missing debug info warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/symbols.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/types.c -->
# sources/distributed-fs/ceph-client/scripts/gendwarfksyms/types.c

## Purpose
`types.c` expands cached DIE fragments into symtypes strings, resolves nested type references, calculates CRC32 symbol versions, and optionally writes a symtypes file.

## Important APIs, Types, and Functions
It defines `type_list_entry`, `type_expansion`, `type_map`, and `version`. Key routines include `type_map_add()`, `type_map_get()`, `get_type_name()`, `__type_expand()`, `type_parse()`, `expand_type()`, `expand_symbol()`, `calculate_version()`, and `generate_symtypes_and_versions()`.

## Control Flow
Generation has three phases: iterate `die_map` to keep the longest expansion for each named type, iterate symbols to expand their type strings and calculate CRCs by recursively expanding type references, then write sorted type-map entries if a symtypes file was requested. Expansion-cycle caches prevent infinite recursion.

## State and Persistence Behavior
`type_map` and expansion caches are process-global during generation and freed at the end. Symbol CRCs are written back into `symbols.c` state. Type-string kABI overrides can synthesize types absent from DWARF.

## Dependencies and Integration Points
It consumes DIE fragments from `die.c`, symbols from `symbols.c`, kABI overrides from `kabi.c`, and zlib `crc32()`.

## Risks and Test Signals
The "longest expansion wins" heuristic is central and can mask shorter incomplete expansions. Type reference parsing is strict, especially quoted names with spaces. Test recursive types, anonymous types, type-string overrides, missing type references, symtypes sorting, and `--dump-versions`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/gendwarfksyms/types.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/generate_builtin_ranges.awk -->
# sources/distributed-fs/ceph-client/scripts/generate_builtin_ranges.awk

## Purpose
`generate_builtin_ranges.awk` generates address range records that map built-in module code/data ranges inside vmlinux sections back to module names.

## Important APIs, Types, and Functions
`get_module_info()` maps object files to module names by reading adjacent `.cmd` files and validating against `modules.builtin`. `update_entry()` stores sorted range records. Main AWK patterns parse `modules.builtin`, `vmlinux.map`, and optionally `vmlinux.o.map`, supporting both GNU ld and LLVM lld map formats.

## Control Flow
Phase one records built-in module names. Phase two parses top-level linker map sections, bases, anchors, section addends, and detects whether a `vmlinux.o.map` pass is needed. Phase three records contiguous object ranges by module, clamping suspicious end offsets. The `END` block inserts anchor records and prints entries sorted by adjusted address.

## State and Persistence Behavior
State is held in AWK associative arrays: module validation, object-to-module cache, section bases/sizes/addends, anchors, range entries, and counts. Output is stdout only.

## Dependencies and Integration Points
It depends on GNU awk features such as `ARGIND`, `strtonum()`, and `asorti()`. It is part of the kernel build pipeline that produces `modules.builtin.ranges`.

## Risks and Test Signals
Linker map format drift is high risk. Address handling strips high hex digits to avoid AWK integer limits, which assumes kernel address ranges fit the remaining bits. `.cmd` parsing differs for C and Rust module variables. Test GNU ld and lld maps, direct-object and `vmlinux.a` links, multi-module objects, anchors, ignored sections, and modules with hyphen/underscore names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/scripts/generate_builtin_ranges.awk -->
