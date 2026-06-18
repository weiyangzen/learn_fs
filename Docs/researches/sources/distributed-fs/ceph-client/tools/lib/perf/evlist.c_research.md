## sources/distributed-fs/ceph-client/tools/lib/perf/evlist.c

Purpose: Implements libperf event-list management: evsel ownership, map propagation, open/close/enable/disable orchestration, ID hashing, polling, and mmap setup.

Important APIs/functions: `perf_evlist__new/init/delete/add/remove/set_maps/open/close/enable/disable`, ID helpers `perf_evlist__id_add[_fd]`, polling helpers, mmap entry points `perf_evlist__mmap[_ops]`, `perf_evlist__munmap()`, mmap iteration, leader/group helpers, and `perf_evlist__go_system_wide()`.

Control flow: Evlist owns a list of evsels. Map propagation derives each evsel CPU/thread map from user CPUs, PMU CPUs, system-wide flags, requires-CPU constraints, and CPU-index-0-only events, pruning empty events. Open iterates evsels and rolls back on failure. Mmap computes required mmap count, allocates pollfd capacity, then maps per-thread when any CPU is present or per-CPU otherwise, sharing outputs with `PERF_EVENT_IOC_SET_OUTPUT`.

State/persistence: Maintains evsel list, CPU/thread maps, all-CPU union, fdarray poll state, ID hash table, mmap arrays, and first mmap links. State is process memory plus perf FDs/mmaps.

Dependencies/integration: Uses internal evsel/cpumap/threadmap/mmap/xyarray/fdarray APIs, perf ioctls, poll, and public libperf iteration macros.

Risks: Map propagation ownership is subtle and can remove evsels. Mmap setup must keep refcounts balanced across shared outputs and pollfd filtering. ID fallback reads are incompatible with group format. `has_user_cpus` is meaningful but not set in this file’s `set_maps()`, so callers/other code must manage it.

Test signals: Existing libperf evlist tests should cover map propagation, open rollback, group leaders, ID hash lookup, poll filtering, mmap per-thread/per-CPU cases, overwrite buffers, system-wide events, and refcount sanitizer runs.
