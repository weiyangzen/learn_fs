# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-mtl.c

Purpose: PCI binding module for Meteor Lake and Arrow Lake SOF HDA devices.

Important APIs: `sof_mtl_ops_init()` installs MTL ops into static `sof_mtl_ops`. `mtl_desc`, `arl_desc`, and `arl_s_desc` specify ACPI target states, machine/SDW tables, chip info (`mtl_chip_info` or `arl_s_chip_info`), IPC4-only support, dspless support, SOF IPC4 firmware/library/topology paths, nocodec topology, ops init/free, and SKU-specific firmware names. PCI IDs map MTL, ARL-S, and ARL devices.

Control flow: common PCI probe selects a descriptor by device ID; SOF core initializes MTL ops; HDA common code consumes chip info for stream alignment, SoundWire, boot, and topology behavior.

State and persistence: static ops table, descriptors, and ID table.

Dependencies and integration: depends on `mtl.h`, HDA common/generic, SOF PCI, and Intel ACPI match tables.

Risks and test signals: risks include ARL versus ARL-S descriptor mixups, static ops reuse, firmware path mismatches, and dspless/IPC4-only assumptions. Test each PCI ID, MTL/ARL firmware selection, SoundWire alt machine selection, dspless mode, remove/shutdown, and PM.
