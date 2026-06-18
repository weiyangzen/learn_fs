
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/memtrace.c

Purpose: implements PowerNV debugfs-controlled runtime reservation of contiguous per-NUMA-node RAM for hardware tracing, exposing reserved memory as noncached trace buffers.

Important APIs/types/functions: `struct memtrace_entry` tracks each reserved region. `memtrace_enable_set()` is the debugfs control write path. `memtrace_alloc_node()` allocates contiguous pages, flushes cache, marks pages offline, and removes the linear mapping. `memtrace_init_debugfs()` maps each region with `ioremap()` and creates per-node debugfs files `trace`, `start`, and `size`. `memtrace_free_regions()` reverses mappings and returns pages through `arch_create_linear_mapping()` and `free_contig_range()`.

Control flow: machine device init creates `arch_debugfs_dir/memtrace/enable`. Writing a nonzero aligned size frees any previous reservation, allocates one region per online node, creates debugfs entries, and records the active size. Writing zero frees all reservations. Reads and mmap of per-node `trace` expose the reserved memory buffer.

State and persistence: global state is protected by `memtrace_mutex`: `memtrace_size`, `memtrace_array`, and `memtrace_array_nr`. Reserved pages are marked `PageOffline` and removed from normal linear mapping until freed. Debugfs entries are ephemeral runtime state.

Dependencies and integration points: depends on PowerNV machine init, memory hotplug, contiguous page allocation, architecture linear mapping hooks, cache flushes, NUMA online node iteration, debugfs, ioremap, and remap_pfn_range.

Risks: allocation failure can leave partial per-node reservations that later control writes must clean up. Mapping and page-offline manipulation are privileged and memory-management sensitive. Debugfs `trace` exposes raw physical trace buffers. Size must align with memory block size or memory hotplug assumptions break.

Test signals: enable/disable cycles, partial allocation failure recovery, mmap/read of trace buffers, NUMA-node coverage, page offline status, memory hotplug interactions, and debugfs cleanup after free.
