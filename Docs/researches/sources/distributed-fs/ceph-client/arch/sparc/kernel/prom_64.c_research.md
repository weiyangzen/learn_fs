# sources/distributed-fs/ceph-client/arch/sparc/kernel/prom_64.c

Purpose: supplies SPARC64-specific Open Firmware device-tree path construction, CPU-node discovery/topology population, and console discovery for sun4u and sun4v systems.

Important APIs/functions: implements `prom_early_alloc()`, `build_path_component()`, `arch_find_n_match_cpu_physical_id()`, `of_find_node_by_cpuid()`, `of_populate_present_mask()`, `of_fill_in_cpu_data()`, and `of_console_init()`. Bus-specific path helpers cover sun4u, sun4v, SBUS, PCI/PCIe, UPA, virtual-devices, EBus, I2C, USB, and IEEE1394.

Control flow: path construction first checks parent bus type, then falls back to sun4v or sun4u root/platform formatting based on `tlb_type`. CPU iteration chooses `reg` on hypervisor systems or `upa-portid`/`portid`/`cpuid` elsewhere, validates CPU IDs against `NR_CPUS`, and invokes callbacks to find nodes, count present CPUs, or populate cache/topology data. Hypervisor systems skip OF CPU mask/cache population because those come from machine descriptions. Console init uses PROM stdout instance path/package resolution and validates display or serial device type.

State and persistence: stores boot-time console path/options/device and fills runtime `cpu_data()` fields for cache sizes, clock tick, core IDs, and processor IDs. It also marks possible/present CPUs. No persistent storage is written.

Dependencies and integration points: depends on PROM instance/path APIs, OF property traversal, `tlb_type`, sun4v/sun4u CPU identity conventions, SMP CPU masks, `cpu_data()`, `smp_fill_in_sib_core_maps()`, and shared `prom_common.c` globals.

Risks: CPU ID property choice varies by platform and firmware; missing IDs halt boot during iteration. Full-path formatting must preserve historic OF naming for boot device matching. Hypervisor systems deliberately bypass parts of OF CPU discovery, so code changes must not regress MDESC-based topology.

Test signals: boot on sun4u and sun4v systems, correct CPU present/possible masks, cache/topology fields in `/proc/cpuinfo`, `of_find_node_by_cpuid()` matches, device paths for PCI/UPA/virtual devices, and valid serial/display console paths with options.
