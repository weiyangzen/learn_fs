# sources/distributed-fs/ceph-client/drivers/ufs/host/tc-dwc-g210-pci.c

## Purpose
Provides PCI glue for the Synopsys DesignWare UFS G210 test chip. It binds Synopsys PCI device IDs, chooses the 20-bit or 40-bit PHY initialization routine from a module parameter, maps BAR0, allocates a UFS host, and starts UFSHCD.

## Important APIs, types, and functions
`tc_type` is a module parameter accepting `20` or `40`. `tc_dwc_g210_pci_hba_vops` names the variant and uses `ufshcd_dwc_link_startup_notify`; probe mutates its `phy_initialization` pointer to `tc_dwc_g210_config_20_bit()` or `tc_dwc_g210_config_40_bit()`. `tc_dwc_g210_pci_probe()` uses `pcim_enable_device()`, `pci_set_master()`, `pcim_iomap_region()`, `ufshcd_alloc_host()`, and `ufshcd_init()`. Remove calls `ufshcd_remove()` after disabling runtime PM.

## Control flow and state
Probe rejects unspecified chip type with `-EPERM`, then initializes the PCI device and UFS host. Persistent state is in PCI driver data established by UFSHCD and the global variant ops structure. Runtime PM is allowed after successful initialization.

## Dependencies and integration points
Depends on PCI, UFSHCD core, DesignWare helper code, G210 exported configuration functions, and generic UFS PM callbacks. It is built with `ufshcd-dwc.o` and `tc-dwc-g210.o` through the Makefile.

## Risks and test signals
The global mutable `tc_dwc_g210_pci_hba_vops` is simple but assumes all probed devices use the same module parameter. Incorrect `tc_type` prevents probing or applies the wrong DME table. Test signals are successful probe for PCI IDs `0xB101`/`0xB102`, correct log line for 20-bit or 40-bit RMMI, link startup completion, and clean runtime PM transitions.
