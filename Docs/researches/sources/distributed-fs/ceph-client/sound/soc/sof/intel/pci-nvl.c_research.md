# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-nvl.c

Purpose: PCI binding module for Nova Lake and Nova Lake-S SOF HDA devices.

Important APIs: static `sof_nvl_ops` is initialized via `sof_nvl_set_ops()`. `nvl_desc` and `nvl_s_desc` define ACPI target states, NVL/SDW machine tables, NVL or NVL-S chip info, IPC4-only support, dspless and on-demand DSP boot, SOF IPC4 firmware/library/topology paths, and nocodec topology. PCI IDs map `HDA_NVL` and `HDA_NVL_S`.

Control flow: PCI match selects core-count/SKU descriptor; ops init delegates to PTL-derived ops through `nvl.c`; common HDA probe handles the rest.

State and persistence: static ops, descriptors, and PCI ID table.

Dependencies and integration: imports `nvl.h`, HDA common/generic, SOF PCI, and NVL ACPI match tables.

Risks and test signals: risks include descriptor comments/names drifting, PTL op compatibility, on-demand boot regressions, and NVL-S core count handling. Test both IDs, firmware path selection, SoundWire matching, dspless and on-demand boot, PM, and removal.
