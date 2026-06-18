## `sources/distributed-fs/ceph-client/arch/x86/include/asm/amd/nb.h`

Purpose: declares AMD northbridge discovery, GART, L3 cache partitioning, MMCONFIG, and NUMA helper interfaces.

Important APIs and types: `struct amd_nb_bus_dev_range`, `struct amd_l3_cache`, `struct amd_northbridge`, and `struct amd_northbridge_info` model AMD NB PCI devices and feature state. Functions include `early_is_amd_nb()`, `amd_get_mmconfig_range()`, `amd_flush_garts()`, `amd_numa_init()`, subcache get/set helpers, `amd_nb_num()`, `amd_nb_has_feature()`, and `node_to_amd_nb()`.

Control flow: enabled builds provide real functions from AMD NB code. Disabled builds return safe defaults. `amd_gart_present()` checks CPU vendor/family/model for legacy GART availability.

State and persistence: implementation owns discovered northbridge arrays and feature flags; this header exposes the contract. L3 cache/subcache settings may persist in hardware registers.

Dependencies and integration points: PCI, resources, AMD node helpers, NUMA init, GART/IOMMU, EDAC/cache drivers, and CPU model data.

Risks: disabled stub macros have inconsistent function-like usage in this snapshot (`amd_nb_num(x)`), so call-site expectations matter. Wrong family/model checks can expose unsupported GART paths.

Test signals: AMD platform boot, NUMA discovery, GART flush paths, L3 subcache controls, and builds without `CONFIG_AMD_NB`.
