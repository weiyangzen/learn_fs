# sources/distributed-fs/ceph-client/arch/mips/lantiq/xway/sysctrl.c

Purpose: initializes XWAY-family PMU/CGU/EBU system-control blocks, registers clock gates and static clocks, and provides legacy PMU enable/disable exports.

Important APIs/functions: `ltq_soc_init`, `ltq_pmu_enable`, `ltq_pmu_disable`, `pmu_enable`, `pmu_disable`, `cgu_enable`, `cgu_disable`, `pci_enable`, `pci_ext_enable`, `pci_ext_disable`, `clkout_enable`, `clkdev_add_pmu`, `clkdev_add_cgu`, `clkdev_add_pci`, and `clkdev_add_clkout`.

Control flow: `ltq_soc_init()` finds DT core nodes for PMU/CGU/EBU, maps resources, clears EBU flash write-protect, registers generic clocks, selects VR9 register offsets if needed, conditionally adds PCI, then branches by machine compatibility to add SoC-specific static rates and PMU clock gates for USB, PCIe, Ethernet/PPE/switch, SDIO, DEU, USIF, MEI, GPHY, analog PHYs, and other blocks. `usb_set_clock()` adjusts USB CGU source bits.

State and persistence: global MMIO bases `pmu_membase`, `ltq_cgu_membase`, `ltq_ebu_membase`, mutable CGU offset variables, and a PMU spinlock. Registered clkdev objects persist for the kernel lifetime.

Dependencies and integration: called during Lantiq timer init; consumed by many platform drivers through `clk_get`; depends on OF matching, `clkdev`, Lantiq MMIO helpers, and SoC-specific rate helpers.

Risks: missing DT nodes or remaps panic. PMU enable failure panics, while disable failure only warns. Clock names are DT-address-string sensitive, and several `con_id` values use literal `"NULL"` rather than NULL.

Test signals: boot across all compatible strings, clk lookup for each platform device, PCI/USB/Ethernet probe success, PMU timeout absence, and static clock rate validation.
