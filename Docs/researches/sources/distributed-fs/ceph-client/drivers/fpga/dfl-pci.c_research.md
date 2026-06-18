# sources/distributed-fs/ceph-client/drivers/fpga/dfl-pci.c

Purpose: PCIe front-end for Intel and Silicom FPGA devices that expose Device Feature Lists. It enables the PCI device, configures DMA and MSI-X, discovers DFL MMIO ranges either from Intel VSEC records or legacy BAR0/FME port-offset registers, and asks the DFL core to create container, FME, port, AFU, and private-feature devices.

Important APIs and functions: `cci_pcie_id_tbl` matches PF and VF device IDs for Intel PACs, D5005/N3000/N6000/N6001/C6100, and Silicom PAC N5010/N5011. `cci_pci_probe` uses `pcim_enable_device`, `pci_set_master`, DMA mask negotiation, and `cci_enumerate_feature_devs`. `find_dfls_by_vsec` parses vendor-specific capability `PCI_VSEC_ID_INTEL_DFLS`, validates BAR indicators and offsets, and records each DFL range in `dfl_fpga_enum_info`. `find_dfls_by_default` maps BAR0, detects FME or Port headers, and for PFs walks FME port-offset registers. `cci_pci_sriov_configure` coordinates SR-IOV enable/disable with DFL port access-mode helpers.

Control flow: probe prepares PCI resources, creates driver data, allocates all MSI-X vectors if present, constructs a Linux IRQ table, discovers DFL ranges, and calls `dfl_fpga_feature_devs_enumerate`. VSEC discovery is preferred; default BAR0 discovery is fallback. Remove disables SR-IOV for PFs, removes DFL feature devices, and frees IRQ vectors.

State and persistence: driver state is `struct cci_drvdata` with the DFL container pointer and PCI-managed resources. Device state includes MSI-X vector allocation, DMA mask, bus mastering, SR-IOV enablement, and FME port access-mode bits. It does not persist configuration across reboot.

Dependencies and integration points: depends on the PCI subsystem, MSI-X support, DFL core enumeration APIs, DFL header helpers from `dfl.h`, and SR-IOV core callbacks. It supplies the physical MMIO and IRQ inventory consumed by `dfl.c`; downstream FME, port, and DFL bus drivers bind after enumeration.

Risks and test signals: risks include malformed VSEC bounds, duplicate BAR records, legacy discovery assuming BAR0 starts with a valid DFL header, `WARN_ON` rather than hard failure for excessive port count, and SR-IOV requiring user-space to release exactly one port per VF. Test signals are PCI probe logs, correct `fpga_region`, `dfl-fme`, `dfl-port`, and `dfl_dev.*` children, MSI-X interrupt delivery, VF creation after port release, and clean remove with SR-IOV disabled.
