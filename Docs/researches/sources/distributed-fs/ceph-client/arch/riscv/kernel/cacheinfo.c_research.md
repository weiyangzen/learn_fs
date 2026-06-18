# sources/distributed-fs/ceph-client/arch/riscv/kernel/cacheinfo.c

Purpose: Provides RISC-V cacheinfo population and private cache attribute plumbing for Linux sysfs cache descriptions.

Important APIs/types/functions: `riscv_set_cacheinfo_ops()`, `cache_get_priv_group()`, `get_cache_size()`, `get_cache_geometry()`, `init_cache_level()`, `populate_cache_leaves()`, and the optional `struct riscv_cacheinfo_ops` provider.

Control flow: Boot or CPU bringup calls generic cacheinfo setup, then `populate_cache_leaves()` fills leaves from ACPI cache descriptors or walks DT CPU/cache nodes. Runtime helpers look up the current CPU cache leaf by level/type and return size or encoded geometry. Private sysfs groups are delegated to registered RISC-V cache ops.

State and persistence: Persistent state is the global `rv_cache_ops` pointer and per-CPU `cpu_cacheinfo` leaves owned by generic cacheinfo. No storage is written to disk.

Dependencies and integration points: Depends on ACPI cache info, OF cache nodes, Linux cacheinfo, and RISC-V vendor/platform code that may register private cache attributes.

Risks and test signals: The current-CPU lookup assumes homogeneous cache topology for the UABI. Bad DT cache-level ordering, missing ACPI split-level data, or stale private ops can expose wrong sysfs cache data. Test with DT and ACPI RISC-V boots, `lscpu`/sysfs cache inspection, hotplug cacheinfo initialization, and vendor cache private attribute coverage.
