# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-layerscape.c

Purpose: Implements Layerscape root-complex glue for DWC PCIe. It handles PF LUT access, root-port mode validation, bridge header cleanup, message filtering, non-posted error response behavior, SoC-specific PME_Turn_Off and L2-exit sequences, and host suspend/resume integration.

Important APIs and types: `struct ls_pcie` stores the DWC pointer, matched `ls_pcie_drvdata`, PF LUT base, optional SCFG regmap/index, and endian flag. `struct ls_pcie_drvdata` selects PF LUT offset, host ops, L2-exit callback, and SCFG/PM support. Main functions are `ls_pcie_host_init()`, `ls_pcie_send_turnoff_msg()`, `ls_pcie_exit_from_l2()`, `ls1021a_pcie_*()`, `ls1043a_pcie_*()`, `ls_pcie_probe()`, `ls_pcie_suspend_noirq()`, and `ls_pcie_resume_noirq()`.

Control flow: Probe allocates objects, maps `regs` as DBI, sets `pf_lut_base` from drvdata, optionally resolves the SCFG phandle and port index, validates that the controller header is a PCI bridge, then calls `dw_pcie_host_init()`. Host init configures bridge slave error forwarding, temporarily enables DBI read-only writes to clear the multifunction bit, and drops non-vendor message TLPs. Runtime PM hooks call generic DWC suspend/resume only for PM-capable variants; resume first invokes the variant L2-exit sequence through PF MCR, SCFG reset bits, or LS1043A LUT debug soft reset.

State and persistence: Persistent hardware state includes PEX internal configuration, PF LUT command bits, message-filter and error-response registers, bridge header type, SCFG PME/reset bits, and DWC host/iATU/MSI state. Driver state is minimal and static after probe, aside from generic DWC suspend flags.

Dependencies and integration points: Uses the DWC host core, syscon regmap for SCFG-backed SoCs, PCI host bridge resources, OF match data, and noirq system sleep callbacks. `pme_turn_off` callbacks plug into `dw_pcie_suspend_noirq()`.

Risks: PM sequences are SoC-specific and timeout/handshake behavior differs between PF LUT and SCFG paths. The driver returns `-ENODEV` if firmware has not configured bridge mode, so bootloader/RCW setup is part of the contract. Endian selection affects all PF LUT accesses. Clearing multifunction and dropping message TLPs are broad register changes that can affect unusual devices or future capabilities.

Test signals: Probe all supported compatible strings, confirm root-port header detection, enumeration behind the bridge, error-response behavior for failed non-posted requests, PME_Turn_Off on suspend, L2 exit on resume, LS1021A/LS1043A SCFG paths, big-endian DT operation, and clean `dw_pcie_host_deinit()` on remove.
