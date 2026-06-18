# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-lnl.c

Purpose: PCI binding module for Lunar Lake SOF HDA devices.

Important APIs: local static `sof_lnl_ops` is initialized by `sof_lnl_ops_init()` through `sof_lnl_set_ops()`. `lnl_desc` enables ACPI target states, LNL/SDW machine tables, LNL chip info, IPC4-only support, dspless and on-demand DSP boot, SOF IPC4 firmware/library/topology paths, and nocodec topology. PCI IDs currently map `HDA_LNL_P`.

Control flow: PCI probe selects `lnl_desc`; ops init creates an MTL-derived ops table with LNL overrides; common HDA probe handles on-demand boot/dspless branches.

State and persistence: static ops, descriptor, and ID table only.

Dependencies and integration: imports `lnl.h`, HDA generic/common, SOF PCI, and ACPI match tables.

Risks and test signals: risks include static ops shared across devices, on-demand DSP boot interactions with BPT/PCM, and descriptor firmware path mismatch. Test LNL PCI match, on-demand firmware boot, dspless mode, SoundWire machine matching, nocodec, and PM resume.
