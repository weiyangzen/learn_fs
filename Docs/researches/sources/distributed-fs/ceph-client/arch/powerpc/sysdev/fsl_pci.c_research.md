<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_pci.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_pci.c

Purpose: Freescale MPC83xx/85xx/86xx PCI and PCIe host controller support, including bridge creation, config-space access quirks, ATMU window programming, DMA window setup, primary bridge selection, machine-check recovery, PME suspend hooks, and EDAC companion registration.

Important APIs/types/functions: exported/platform functions `fsl_pcibios_fixup_bus()`, `fsl_pcibios_fixup_phb()`, `mpc83xx_add_bridge()`, `fsl_pci_immrbar_base()`, `fsl_pci_mcheck_exception()`, `fsl_pci_assign_primary()`, static `fsl_add_bridge()`, `setup_pci_atmu()`, `setup_one_atmu()`, `fsl_pcie_check_link()`, `fsl_indirect_read_config()`, MPC83xx-specific config ops, PME syscore handlers, and platform driver `fsl_pci_driver`.

Control flow: early PCI fixup normalizes Freescale PCIe root bridge class codes. Bridge setup maps controller registers, allocates a `pci_controller`, sets indirect or MPC83xx config ops, validates PCIe link/host mode or PCI agent mode, enables command bits, applies controller errata, processes OF ranges, programs outbound and inbound ATMU windows, and enables SWIOTLB/device DMA setup when needed. `setup_pci_atmu()` disables windows, maps MEM/IO resources outwards, positions PCICSRBAR, creates inbound DMA windows sized to DRAM and optionally a 64-bit window, and handles kdump by avoiding inbound-window teardown. MPC83xx PCIe remaps type0/type1 config windows dynamically. Machine-check recovery recognizes loads from PCI memory space and synthesizes all-ones load results while advancing NIP. PM code sends PME turn-off/exit-L2 messages and reprograms ATMUs after resume.

State and persistence: global flags track FSL PCIe bus fixup and MPC83xx mode, `pci64_dma_offset` and `ppc_md.dma_set_mask` support 64-bit inbound DMA, `fsl_pci_primary` records the selected primary PHB, and each hose stores MMIO mappings, ranges, DMA window limits, and private data. Hardware ATMU, command, class-code, PME, and link-state registers persist across runtime and are restored/reprogrammed after resume.

Dependencies and integration points: depends on OF platform devices/ranges, PowerPC PCI controller infrastructure, indirect PCI ops, memblock DRAM size, SWIOTLB, EDAC platform device registration, MPIC/PME IRQs, PowerPC instruction decode helpers, and Freescale SoC revision/IMMR helpers.

Risks: ATMU sizing is complex and constrained by power-of-two windows, limited outbound/inbound slots, kdump in-flight DMA, and MSIIR placement. Link-state handling suppresses config access when links are down. Machine-check emulation must only handle safe load instructions from PCI memory. Primary bridge selection retains OF node references and must be coordinated with platform setup.

Test signals: PCI/PCIe enumeration on supported SoCs, link-down config access returning no devices, correct MEM/IO resources behind root bridges, DMA above 4 GiB with and without SWIOTLB, MSI address composition via IMMRBAR, kdump boot with in-flight DMA, PME suspend/resume, and recoverable PCI master-abort machine checks validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/sysdev/fsl_pci.c -->
