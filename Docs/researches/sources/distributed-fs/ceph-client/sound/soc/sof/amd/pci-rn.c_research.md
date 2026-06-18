# sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-rn.c

Purpose: PCI binding and SOF descriptor for AMD Renoir ACP3.x platforms.

Important APIs/types/functions: `renoir_chip_info` defines ACP3.x PGFSM, interrupt, DSP interrupt, error, I2S error, SRAM PTE, semaphore, clock mux, and probe offsets. `renoir_desc` selects ACPI machine table, IPC3 firmware `sof-rn.ri`, topology path, nocodec topology, and Renoir ops. `acp_pci_rn_probe()` filters revision/config before `sof_pci_probe()`.

Control flow: only revision `ACP_RN_PCI_ID` and AMD SOF config flags bind. The PCI driver uses `sof_pci_pm` for PM callbacks.

State and persistence: static descriptors only.

Dependencies and integration points: common ACP probe, Renoir DAI ops, AMD machine config, SOF PCI device layer.

Risks: ACP3.x has older register masks and PSP behavior, so descriptor fields must align with branches in common ACP code. Config flag gating means BIOS/ACPI machine config directly affects binding.

Test signals: Renoir device enumeration, firmware `sof-rn.ri`, DAI/topology match, runtime/system PM.
