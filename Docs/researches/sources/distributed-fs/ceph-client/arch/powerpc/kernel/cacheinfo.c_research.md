<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cacheinfo.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/cacheinfo.c

Purpose: Builds PowerPC cache topology objects and exposes per-CPU cache information through sysfs.

Important APIs/types/functions: `struct cache_dir`, `struct cache_index_dir`, `struct cache_type_info`, `struct cache`, cache property readers, cache chain creation/linking helpers, sysfs attribute show methods, `cacheinfo_cpu_online()`, `cacheinfo_cpu_offline()`, `cacheinfo_teardown()`, and `cacheinfo_rebuild()`.

Control flow: On CPU online, code finds the CPU OF node, creates or reuses L1 split/unified cache objects, walks `next-cache` nodes for higher levels, marks shared CPU maps, creates `/sys/devices/system/cpu/cpuN/cache/index*`, and conditionally adds size/line/sets/associativity attributes. Offline removes sysfs first, clears CPU bits, and frees cache objects with empty masks.

State and persistence: Global `cache_list`, per-CPU `cache_dir_pcpu`, cache object refcounts/OF refs, shared CPU masks, and sysfs kobjects persist while CPUs are online.

Dependencies and integration points: Depends on OF cache properties, CPU devices, cpumasks, thread-group topology maps, hotplug locking, kobjects/sysfs, and `cacheinfo.h` hooks from sysfs code.

Risks: Cache sharing and thread-group group IDs must be correct or sysfs topology is misleading. Kobject lifetime and OF node refs must be balanced during hotplug/suspend rebuild.

Test signals: CPU online/offline stress, sysfs cache attribute validation against device tree, suspend/resume rebuild on pSeries, memory-leak/refcount checks, and big-core/thread-group topology tests.

Source read size: 953 lines, 24117 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/cacheinfo.c -->
