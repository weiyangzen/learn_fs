# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-cnl.c

Purpose: PCI binding module for Cannon Lake, Coffee Lake, and Comet Lake SOF HDA devices.

Important APIs: descriptor variants `cnl_desc`, `cfl_desc`, and `cml_desc` share CNL chip info/ops and IPC3 default with IPC4 support, dspless support, ACPI target states, firmware/library/topology paths, nocodec topology, and SoundWire alternate machine tables. `sof_pci_ids` maps LP/H/S PCI IDs to the appropriate descriptor. The PCI driver delegates probe/remove/shutdown to common SOF HDA/PCI helpers.

Control flow: PCI match selects a descriptor, `hda_pci_intel_probe()` confirms SOF ownership, and common probe consumes machine tables and firmware defaults.

State and persistence: static descriptors and ID table only.

Dependencies and integration: integrates CNL ops, HDA generic/common, SOF PCI core, and Intel ACPI machine tables including SoundWire variants.

Risks and test signals: risks are descriptor-level: wrong firmware name per SKU, alt machine mismatch, IPC4 AVS path coverage, and dspless selection. Test each PCI ID, machine matching with/without SoundWire, IPC3/IPC4 boot, and nocodec/dspless behavior.
