# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-skl.c

Purpose: PCI binding module for Skylake and Kaby Lake SOF HDA devices using AVS/IPC4-only firmware support.

Important APIs: `skl_desc` and `kbl_desc` specify SKL chip info, SKL ops/init/free, IPC4-only support, dspless mode, firmware/topology paths, nocodec topology, and machine tables. PCI IDs map SKL_LP and KBL_LP. The `pci_driver` delegates to common HDA PCI probe/remove/shutdown and SOF PCI PM.

Control flow: PCI match selects SKL or KBL firmware path and machine table; common HDA probe handles driver ownership and generic stream/codec setup.

State and persistence: static descriptors and ID table only.

Dependencies and integration: depends on SKL HDA ops, HDA common/generic, SOF PCI, and ACPI match tables.

Risks and test signals: risks include IPC4-only assumption on older platforms, firmware path differences, and missing ACPI target state use compared with newer descriptors. Test SKL/KBL PCI IDs, AVS firmware boot, dspless/nocodec, machine matching, and remove/shutdown.
