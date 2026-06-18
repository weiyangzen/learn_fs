# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-rcar-host.c

Purpose: Implements the Renesas R-Car PCIe root-complex platform driver. It allocates a `pci_host_bridge`, initializes regulators, runtime PM, clocks, PHY, register windows, link training, INTx forwarding, MSI support, config-space access, and suspend/resume handling for older R-Car SoCs.

Important APIs/types/functions: `struct rcar_pcie_host` embeds shared `struct rcar_pcie` and host resources. `struct rcar_msi` tracks the 32-vector MSI bitmap, parent IRQ domain, and mask lock. PCI config access is exposed through `rcar_pcie_ops`, with `rcar_pcie_read_conf()` and `rcar_pcie_write_conf()` routing into `rcar_pcie_config_access()`. Other key paths include `rcar_pcie_hw_init()`, `rcar_pcie_enable()`, `rcar_pcie_enable_msi()`, `rcar_pcie_parse_map_dma_ranges()`, `rcar_pcie_probe()`, `rcar_pcie_resume()`, and the ARM-only abort workaround.

Control flow: Probe enables optional supplies and runtime PM, maps MMIO, obtains MSI IRQs and the `pcie_bus` clock, maps DMA inbound ranges, runs the SoC-specific PHY init callback from the OF match table, initializes the controller as a root port, waits for data-link active, enables MSI if configured, then calls `pci_host_probe()`. Config cycles special-case root bus devfn 0 as internal config space and use Type 0/Type 1 PIO for child buses. MSI interrupts read `PCIEMSIFR`, dispatch through the MSI domain, and clear unexpected vectors.

State and persistence: Runtime state is mainly MMIO register programming, runtime PM state, clock/PHY power, IRQ-domain allocations, and the MSI allocation bitmap. Inbound/outbound windows and MSI target registers persist in hardware until reset, suspend, or teardown. Resume rebuilds DMA windows, PHY/link state, MSI address and masks, and resource windows.

Dependencies/integration: Depends on Linux PCI host bridge APIs, generic MSI parent domains, irqdomain, runtime PM, regulators, clocks, PHY, OF resources, and common R-Car helpers from `pcie-rcar.c`/`pcie-rcar.h`.

Risks: Config reads can produce hardware aborts on ARM, hence the inline exception-table workaround. Sub-32-bit config writes perform read-modify-write and can be unsafe around RW1C fields. Window splitting is limited by `MAX_NR_INBOUND_MAPS`; bad DT ranges can fail mapping. Link-down is treated as no device. MSI IRQs are shared with non-MSI sources, so handler filtering must remain correct.

Test signals: Build on ARM and arm64 R-Car configs, DT probe for all compatible strings, link-up/link-down boot logs, config-space enumeration, MSI allocation/free, INTx behavior, DMA to inbound windows, suspend/resume with allocated MSIs, and ARM abort handler coverage.
