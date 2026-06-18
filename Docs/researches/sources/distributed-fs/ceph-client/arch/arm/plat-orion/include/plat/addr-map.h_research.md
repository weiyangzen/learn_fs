# sources/distributed-fs/ceph-client/arch/arm/plat-orion/include/plat/addr-map.h

Purpose: Declares Orion CPU/MBus address-window configuration data structures and setup APIs used by platform code to map DRAM and device windows.

Important APIs/types: `struct orion_addr_map_cfg` describes total windows, remappable windows, bridge register base, hardware I/O coherency, and optional callbacks for remap eligibility and register base selection. `struct orion_addr_map_info` describes one mapping: window index, base, size, MBus target, attribute, and remap value. APIs are `orion_config_wins`, `orion_setup_cpu_win`, and `orion_setup_cpu_mbus_target`. `orion_mbus_dram_info` is declared externally.

Control flow and state: This header contains no executable code, but callers pass configuration arrays to implementation code that programs hardware windows. Callback fields allow SoC variants to override default window behavior.

Dependencies and integration: Depends on `struct mbus_dram_target_info` and Linux `__iomem`/`u32` types from includers. `pcie.c` indirectly relies on MBus DRAM information when creating PCIe decode windows.

Risks and tests: Invalid size/base alignment can create overlapping or unmapped windows at boot. Tests should verify per-SoC window tables, remap callback behavior, coherency settings, and boot memory/device access after mapping changes.
