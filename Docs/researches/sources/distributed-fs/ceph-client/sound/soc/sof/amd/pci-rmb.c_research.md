# sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-rmb.c

Purpose: PCI binding and SOF descriptor for AMD Rembrandt ACP6.x platforms.

Important APIs/types/functions: `rembrandt_chip_info` provides ACP6.x PGFSM, interrupt, DSP software interrupt, error, SRAM PTE, semaphore, fusion runstall, and probe offsets. `rembrandt_desc` configures ACPI machine table, IPC3, firmware `sof-rmb.ri`, topology path, nocodec topology, and Rembrandt ops. `acp_pci_rmb_probe()` filters revision/config.

Control flow: probe requires `pci->revision == ACP_RMB_PCI_ID` and AMD config flag `FLAG_AMD_SOF` or `FLAG_AMD_SOF_ONLY_DMIC`, then delegates to `sof_pci_probe()`.

State and persistence: static descriptors.

Dependencies and integration points: SOF PCI glue, AMD machine config, Rembrandt DAI ops, common ACP driver.

Risks: no `.driver.pm` assignment unlike several other AMD PCI files, so PM behavior depends on generic defaults/module context. Strict revision gating prevents accidental binding but requires new revisions to be added elsewhere.

Test signals: Rembrandt PCI probe, firmware `sof-rmb.ri`, ACPI machine selection, and PM remove/probe behavior.
