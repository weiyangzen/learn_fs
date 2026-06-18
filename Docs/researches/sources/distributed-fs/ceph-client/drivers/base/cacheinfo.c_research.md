# sources/distributed-fs/ceph-client/drivers/base/cacheinfo.c

### Purpose
`cacheinfo.c` detects per-CPU cache topology and publishes it through CPU sysfs devices. It supports firmware-derived cache data from Device Tree and ACPI, architecture fallback hooks, shared CPU maps, last-level-cache sharing queries, and CPU hotplug setup/teardown.

### Important APIs, Types, And Functions
Key state is the per-CPU `struct cpu_cacheinfo`, arrays of `struct cacheinfo`, per-CPU `cache` devices, and per-index cache devices. Public or weak-extension functions include `get_cpu_cacheinfo()`, `last_level_cache_is_valid()`, `last_level_cache_is_shared()`, `init_of_cache_level()`, `cache_setup_acpi()`, `early_cache_level()`, `init_cache_level()`, `populate_cache_leaves()`, `fetch_cache_info()`, `detect_cache_attributes()`, and `cache_get_priv_group()`. Hotplug integration is through `cacheinfo_cpu_online()`, `cacheinfo_cpu_pre_down()`, and `cpuhp_setup_state()`.

### Control Flow
Cache discovery starts with `fetch_cache_info()`, which prefers ACPI on ACPI systems, otherwise Device Tree, then falls back to architecture hooks. `detect_cache_attributes()` ensures cacheinfo storage exists, populates cache leaves via architecture or firmware hooks, fills firmware properties if needed, and computes shared CPU maps. Device Tree parsing counts cache leaves from `cache-size`, `i-cache-size`, `d-cache-size`, or fallback unified/split assumptions, then walks cache nodes and records size, line size, set count, associativity, type, firmware token, and optional cache ID. CPU hotplug online detection creates `cpuX/cache` and `indexN` devices; pre-down removes sysfs devices and clears shared maps.

### State, Persistence, And Dependencies
State persists for the life of the kernel in per-CPU `ci_cpu_cacheinfo`; the file comments note cacheinfo memory is never freed after allocation, even across hotplug. Runtime sysfs state is tracked in `ci_cache_dev`, `ci_index_dev`, and `cache_dev_map`. `coherency_max_size` and per-CPU data-slice size are updated from discovered leaves. Dependencies include OF and ACPI cache description APIs, CPU hotplug, cpumasks, sysfs device helpers, architecture weak overrides, and `setup_pcp_cacheinfo()`.

### Integration Points
Consumers use `last_level_cache_is_shared()` and `get_cpu_cacheinfo()` to reason about CPU topology. Userspace observes `/sys/devices/system/cpu/cpuX/cache/indexY/` attributes such as `type`, `level`, `size`, `shared_cpu_map`, `shared_cpu_list`, and policy fields. Architecture code can override the weak discovery hooks or add a private sysfs attribute group per cache leaf.

### Risks
Firmware descriptions may be incomplete or inconsistent; the code falls back to architecture data only under specific conditions and treats invalid OF hierarchy ordering as errors. Shared-map correctness depends on cache IDs or stable firmware tokens; the fallback assumption marks all non-L1 caches as system-wide shared. `cache_private_groups` is a static mutable array used to splice one private group, so it assumes compatible use across leaves. CPU hotplug paths must keep sysfs devices, shared maps, and per-CPU slice sizes synchronized.

### Test Signals
High-value tests include DT systems with unified and split L1 caches, multi-level cache nodes, missing cache-size fallback, ACPI PPTT cache data, architecture fallback-only systems, CPU online/offline cycles, shared cache maps across sibling CPUs, last-level cache query correctness, hidden sysfs attributes for zero-valued fields, and allocation failure in cacheinfo or index-device creation.
