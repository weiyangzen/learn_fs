# sources/distributed-fs/ceph-client/sound/soc/sof/intel/pci-ptl.c

Purpose: PCI binding module for Panther Lake and Wildcat Lake SOF HDA devices.

Important APIs: static `sof_ptl_ops` is initialized by `sof_ptl_set_ops()`. `ptl_desc` and `wcl_desc` provide ACPI target states, PTL/SDW machine tables, PTL/WCL chip info, IPC4-only support, dspless and on-demand DSP boot, SOF IPC4 firmware/library/topology paths, and nocodec topology. PCI IDs map PTL, PTL-H, and WCL.

Control flow: device ID selects PTL or WCL descriptor; ops init installs PTL platform ops; common HDA PCI probe and SOF core consume descriptor data.

State and persistence: static ops, descriptors, and ID table.

Dependencies and integration: imports `ptl.h`, HDA generic/common, SOF PCI, and Intel ACPI match tables. NVL reuses PTL ops via `nvl.c`.

Risks and test signals: risks include WCL using PTL machine/nocodec topology, PTL-H descriptor coverage, on-demand boot, and ops reuse by NVL. Test all IDs, firmware path selection, SoundWire, dspless, on-demand boot, and PM/remove.
