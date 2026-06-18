# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-apl.c

Purpose: PCI binding module for Apollo Lake/Broxton and Gemini Lake SOF HDA devices.

Important APIs: defines `bxt_desc` and `glk_desc` `struct sof_dev_desc` entries with ACPI machine tables, APL chip info, IPC3+IPC4 support, dspless support, firmware/library/topology defaults, nocodec topology, `sof_apl_ops`, `sof_apl_ops_init`, and `hda_ops_free`. `sof_pci_ids` maps `HDA_APL` and `HDA_GLK` IDs. The `pci_driver` uses `hda_pci_intel_probe`, `sof_pci_remove`, and `sof_pci_shutdown`.

Control flow: module registration exposes the PCI IDs; probe is delegated to common HDA PCI selection and SOF PCI core, which then uses the descriptor for ops and firmware selection.

State and persistence: static descriptors and PCI ID table only.

Dependencies and integration: imports SOF PCI device helpers, APL HDA ops, Intel ACPI match tables, and HDA generic/common namespaces.

Risks and test signals: risks include wrong default firmware/topology paths, IPC default mismatch, or descriptor ops mismatch. Test APL/GLK PCI match, IPC3 default boot, IPC4 AVS firmware path, dspless mode, nocodec topology, and remove/shutdown.
