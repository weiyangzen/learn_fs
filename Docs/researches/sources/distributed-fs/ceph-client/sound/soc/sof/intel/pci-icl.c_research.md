# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-icl.c

Purpose: PCI binding module for Ice Lake and Jasper Lake/N-series SOF HDA devices.

Important APIs: `icl_desc` uses ICL chip info, ICL ops, IPC3 default with IPC4 support, ICL machine and SoundWire alternate tables. `jsl_desc` uses JSL chip info but CNL ops/init, with IPC3 default and IPC4 AVS paths. `sof_pci_ids` maps ICL LP/H and ICL_N/JSL_N IDs. The PCI driver uses common HDA PCI probe and SOF PCI remove/shutdown.

Control flow: descriptor choice determines whether ICL-specific post-fw-run/HPRO behavior or CNL-derived JSL behavior is installed by SOF core.

State and persistence: static descriptors and ID table only.

Dependencies and integration: depends on ICL/CNL ops namespaces, HDA generic/common, SOF PCI, and ACPI match tables.

Risks and test signals: risks include JSL using CNL ops with JSL chip info, IPC type fallback, SoundWire alt machines on ICL only, and firmware path accuracy. Test all PCI IDs, IPC3 and IPC4 paths, ICL SoundWire, JSL no-alt-machine path, dspless/nocodec, and remove/shutdown.
