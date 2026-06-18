# sources/distributed-fs/ceph-client/arch/x86/pci/amd_bus.c

## Purpose
Provides native early PCI host bridge resource and NUMA topology probing for older AMD/Hygon systems, plus enables extended CF8 config-space access on AMD family 10h and newer CPUs. It fills the shared `pci_root_infos` list for fallback use when ACPI is absent, incomplete, or ignored.

## Important APIs, types, and functions
- `struct amd_hostbridge` and `hb_probes[]` identify legacy AMD northbridge devices supported by the maintenance-mode probe.
- `early_root_info_init()` reads AMD northbridge bus-range, IO, MMIO, TOM/TOM2, and MMCONFIG registers, allocates `pci_root_info` entries, and populates root resources.
- `find_pci_root_info()` locates an existing root by AMD node/link.
- `cap_resource()` clamps 64-bit hardware ranges to `resource_size_t`.
- `amd_bus_cpu_online()` enables `ENABLE_CF8_EXT_CFG` in `MSR_AMD64_NB_CFG` for each online CPU.
- `pci_enable_pci_io_ecs()` enables extended CF8 config through PCI northbridge function registers when possible.
- `pci_io_ecs_init()` installs the CPU hotplug callback and marks `PCI_HAS_IO_ECS`.
- `amd_postcore_init()` gates everything to AMD/Hygon vendors and runs as a `postcore_initcall`.

## Control flow
At postcore init, non-AMD/Hygon systems return immediately. `early_root_info_init()` first checks `early_pci_allowed()`, scans known host bridge locations, creates bus-range records from function 1 config-map registers, and on older families extracts IO/MMIO aperture routing. It subtracts RAM and MMCONFIG holes from candidate ranges, adds explicit bridge windows, assigns leftovers to the default node/link, and logs the resulting resources. Then `pci_io_ecs_init()` enables extended config access through PCI/MSR paths and registers a CPU hotplug state to keep ECS enabled on secondary CPUs.

## State and persistence
The main persistent state is the global `pci_root_infos` list allocated by `alloc_pci_root_info()` and appended with `update_res()`. CPU MSR state is changed to enable extended CF8 config. `pci_probe` is updated with `PCI_HAS_IO_ECS` when ECS is available.

## Dependencies and integration points
Depends on early CF8 config helpers from `early.c`, AMD northbridge helpers (`amd_get_mmconfig_range`, `amd_nb_bus_dev_ranges`, `early_is_amd_nb`), CPU hotplug, topology/resource range helpers, and `bus_numa.c` resource list APIs. ACPI code may use the populated node/resource information as fallback when firmware data is missing or disabled.

## Risks and edge cases
This code intentionally supports only older families through Fam15h_00h-0fh for topology and through Fam11h for native resource extraction. Firmware/ACPI should be authoritative on newer systems. Range subtraction around TOM/TOM2 and MMCONFIG must avoid exposing RAM or ECAM as PCI MMIO. MSR writes must be applied on all CPUs. Early config access can be disabled by `pci=noearly`.

## Test signals
Boot old AMD/Hygon systems with and without ACPI `_CRS`; inspect `PCI: root bus` resources, node/link logs, TOM/TOM2 messages, and availability of extended config space. CPU hotplug should leave ECS enabled. Resource assignment failures or devices on the wrong NUMA node suggest incorrect bridge register interpretation.
