# sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-vangogh.c

Purpose: PCI binding and SOF descriptor for AMD Vangogh ACP5.x platforms.

Important APIs/types/functions: `vangogh_chip_info` names the chip, provides ACP5.x PGFSM/interrupt/DSP interrupt/SRAM PTE/semaphore/probe offsets. `vangogh_desc` configures Vangogh ACPI machine table, IPC3 firmware `sof-vangogh.ri`, topology path, nocodec topology, and Vangogh ops. `acp_pci_vgh_probe()` gates by revision/config.

Control flow: accepts only `ACP_VANGOGH_PCI_ID` and AMD SOF config flags, then delegates to `sof_pci_probe()`. PM uses `sof_pci_pm`.

State and persistence: static descriptors.

Dependencies and integration points: Vangogh ops add DMI-quirk overrides for signed firmware and post-run delay. Common ACP loader uses `.name = "vangogh"` for signed code/data firmware names.

Risks: quirked devices such as Steam Deck OLED depend on descriptor name and DMI data to select signed firmware filenames and delay behavior. Missing error/I2S offsets may limit common error reporting for this generation.

Test signals: Vangogh PCI probe, normal and DMI-signed firmware load, post firmware run delay on resume, and machine-table topology selection.
