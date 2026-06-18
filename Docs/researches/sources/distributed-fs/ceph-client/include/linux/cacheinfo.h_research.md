## sources/distributed-fs/ceph-client/include/linux/cacheinfo.h

**Purpose:** This header describes CPU cache topology data and exposes cacheinfo discovery helpers.

**Important APIs/types/functions:** `enum cache_type` classifies instruction, data, separate, and unified caches. `struct cacheinfo` stores cache ID, type, level, line size, sets, ways, partitions, size, shared CPU mask, attributes, firmware token, sysfs disable flag, and private data. `struct cpu_cacheinfo` stores per-CPU cache leaf arrays and discovery flags. APIs include `get_cpu_cacheinfo()`, early/init/populate helpers, ACPI/PPTT and OF cache setup, last-level cache queries, `cache_get_priv_group()`, `get_cpu_cacheinfo_level()`, `get_cpu_cacheinfo_id()`, `use_arch_cache_info()`, and aliasing macros.

**Control flow, state, persistence:** Cacheinfo is populated during CPU topology initialization/hotplug and may be exposed through sysfs. Inline lookup helpers require the CPU hotplug lock and scan per-CPU leaf arrays.

**Dependencies/integration:** Depends on bitops, CPU masks, CPU hotplug locking, SMP, ACPI PPTT, OF, and architecture cachetype support.

**Risks and test signals:** Risks include missing hotplug locking, incorrect shared CPU masks, firmware token mismatches, wrong aliasing detection, and exposing invalid sysfs leaves. Test signals include cache sysfs topology tests, CPU hotplug, ACPI/DT boot variants, last-level sharing checks, and lockdep for `cpus_read_lock`.
