# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-artpec6.c

Purpose: Implements Axis ARTPEC-6/ARTPEC-7 DWC PCIe glue for both root-complex and endpoint modes. It performs variant-specific PHY and NoC power sequencing, core reset control, LTSSM start/stop, address fixups for translated CPU/controller addresses, endpoint feature/IRQ support, and RC/EP OF-mode selection.

Important APIs and types: `struct artpec6_pcie` stores the DWC pointer, syscon regmap, PHY register mapping, variant, and mode. `struct artpec_pcie_of_data` selects ARTPEC6/ARTPEC7 and RC/EP mode. Key functions are `artpec6_pcie_cpu_addr_fixup()`, `artpec6_pcie_establish_link()`, `artpec6_pcie_stop_link()`, `artpec6_pcie_init_phy_a6()`, `artpec6_pcie_init_phy_a7()`, `artpec6_pcie_wait_for_phy_*()`, `artpec6_pcie_host_init()`, `artpec6_pcie_ep_init()`, `artpec6_pcie_raise_irq()`, and `artpec6_pcie_probe()`.

Control flow: Probe maps the `phy` resource, gets `axis,syscon-pcie`, installs DWC ops, then dispatches to RC or EP mode based on match data and Kconfig. RC host init optionally sets ARTPEC7 N_FTS values, asserts reset, initializes PHY/NoC/reference clock fields, deasserts reset, waits for PHY readiness, and enters generic DWC host initialization. EP mode clears device-type bits, initializes the DWC endpoint controller, initializes endpoint registers, and notifies EPC clients. Link start/stop toggles the syscon LTSSM bit.

State and persistence: Hardware state includes syscon `PCIECFG`, `PCIESTAT`, `NOCCFG`, PHY status/ASIC handshake registers, reset bits, reference-clock selection, LTSSM enable, and DWC RC/EP/iATU state. `cpu_addr_fixup()` changes DWC parent-bus offset behavior by subtracting RC config or EP address-space bases.

Dependencies and integration points: Integrates with the DWC host and endpoint cores, syscon regmap, platform resources, OF match data, and PCI endpoint framework. Endpoint features expose common DWC BAR defaults and MSI capability; INTx is explicitly unsupported.

Risks: Variant-specific sequencing is timing-sensitive and uses retry loops that log errors but continue. Address fixup is critical for correct iATU parent-bus offsets; broken DT ranges will be warned and corrected by the common core. EP mode supports MSI but not INTx/MSI-X, so EPF expectations must match. ARTPEC7 reference-clock selection depends on hardware strap/status.

Test signals: Boot ARTPEC6/7 RC and EP compatibles, verify PHY wait logs, link training, DWC parent-bus offset warnings/absence, ARTPEC7 N_FTS programming, endpoint EPC init notification, MSI raise success and INTx rejection, suspend/reset recovery where applicable, and enumeration behind RC mode.
