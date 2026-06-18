# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rockchip.c

Purpose: Provides common Rockchip AXI PCIe resource, reset, PHY, clock, and configuration-access helpers shared by host and endpoint drivers.

Important APIs/types/functions: Exports `rockchip_pcie_parse_dt()`, `rockchip_pcie_init_port()`, `rockchip_pcie_get_phys()`, `rockchip_pcie_deinit_phys()`, `rockchip_pcie_enable_clocks()`, `rockchip_pcie_disable_clocks()`, and `rockchip_pcie_cfg_configuration_accesses()`. These operate on the shared `struct rockchip_pcie` declared in `pcie-rockchip.h`.

Control flow: `rockchip_pcie_parse_dt()` maps either RC `axi-base` or EP `mem-base`, maps `apb-base`, obtains PHYs, reads `num-lanes` and max link speed, obtains PM/core reset controls, grabs PERST/reset GPIO depending on mode, and gets all clocks. `rockchip_pcie_init_port()` asserts resets, initializes all PHYs, deasserts PM resets, programs generation/lane/mode bits, powers PHYs, waits for PLL lock, and deasserts core resets. `rockchip_pcie_cfg_configuration_accesses()` programs outbound region 0 as Type 0 or Type 1 config access.

State and persistence: The helper fills shared driver state fields such as MMIO bases, resources, PHY pointers, reset arrays, clocks, lane count, link generation, GPIO, and mode flag. Hardware reset, client config, and region-0 translation registers persist after initialization until reprogrammed or reset.

Dependencies/integration: Uses platform resources by name, OF PCI max-link-speed, reset controls, PHY framework, clock bulk APIs, GPIO descriptors, and local Rockchip register definitions.

Risks: Resource names are ABI with DT. The common parser already obtains PHYs; endpoint code also calls `rockchip_pcie_get_phys()` after parsing, so changes around PHY acquisition must account for both users. Reset order is hardware-sensitive; the header explicitly warns not to reorder core reset deassert sequencing. All four PHY lanes are initialized even if fewer lanes are used.

Test signals: Host and endpoint builds, probe with legacy and per-lane PHY models, reset/clock error-path unwinding, PHY PLL lock timeout handling, Type 0/Type 1 config enumeration, and endpoint mode initialization.
