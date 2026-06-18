# sources/distributed-fs/ceph-client/sound/soc/sof/amd/pci-acp70.c

Purpose: PCI binding and SOF descriptor for AMD ACP7.0, ACP7.1, and ACP7.2 revisions.

Important APIs/types/functions: `acp70_chip_info` defines ACP70 register offsets, interrupt/error fields, SoundWire details, register range, and probe/fusion offsets. `acp70_desc` points to ACP70 ACPI machine tables and SoundWire alt tables with IPC3 firmware `sof-acp_7_0.ri`. `acp70_pci_probe()` allows revisions `ACP70_PCI_ID`, `ACP71_PCI_ID`, and `ACP72_PCI_ID`, then gates by AMD SOF config flags.

Control flow: PCI match enters revision switch, rejects unknown revisions, checks `snd_amd_acp_find_config()`, then delegates to `sof_pci_probe()`.

State and persistence: static chip and device descriptors only.

Dependencies and integration points: common ACP ops, SOF PCI glue, AMD ACPI machine tables, SoundWire support, and PM via `sof_pci_pm`.

Risks: one descriptor is shared for three revisions; any register/layout divergence beyond common branch handling would need descriptor or runtime updates. SoundWire wake/PME logic depends on ACP70-specific offsets.

Test signals: PCI probe on all accepted revisions, ACP70 wake interrupts, SoundWire machines, firmware/topology load.
