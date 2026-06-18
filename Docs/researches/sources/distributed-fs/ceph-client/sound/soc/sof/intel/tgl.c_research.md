<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/tgl.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/intel/tgl.c

## Purpose
Tiger Lake-family HDA DSP ops and hardware descriptors. It adapts common HDA SOF operations for IPC3 or IPC4, firmware boot, debug regions, core power management, SoundWire handling, and chip metadata for TGL, TGL-H, EHL, and ADL-S.

## Important APIs, Types, and Functions
`sof_tgl_ops_init()` copies `sof_hda_common_ops` into global `sof_tgl_ops` and selects IPC3 or IPC4 callbacks based on `sdev->pdata->ipc_type`. IPC3 uses CNL IRQ/send/dump handlers and IPC3 power-state handling. IPC4 allocates `sof_ipc4_fw_data`, sets manifest offset, mtrace type, context-save support, external library loader, CNL IPC4 IRQ/send/dump handlers, IPC4 DSP dump, and IPC4 power-state handling. `tgl_dsp_core_get()` and `tgl_dsp_core_put()` manage primary and secondary core power through HDA or IPC PM ops. Descriptors include `tgl_chip_info`, `tglh_chip_info`, `ehl_chip_info`, and `adls_chip_info`.

## Control Flow, State, and Persistence
Ops initialization mutates the global ops table and optionally stores IPC4 private data on `sdev->private`. Runtime core-get powers primary core locally and secondary cores via firmware IPC when available; core-put asks firmware to disable a core before resetting/powering down the primary core. Static chip descriptors define core counts, IPC registers, ROM status, SSP and SoundWire bases, D0i3 offset, code-loader init, power-down, and interrupt-disable callbacks.

## Dependencies and Integration
Depends on HDA common ops, CNL IPC3/IPC4 helpers, IPC4 private data, HDA IPC4 library loading, SoundWire common helpers, CL boot with ICCMAX, and DAI driver setup. It is consumed by PCI descriptor files such as `pci-tgl.c`.

## Risks and Test Signals
Risks include global ops mutation across devices, IPC type conditionals leaving required callbacks unset, secondary-core state relying on IPC PM ops availability, and descriptor differences being subtle across related platforms. Test signals are IPC3 and IPC4 boot on TGL-class hardware, external IPC4 library loading, core enable/disable on primary and secondary cores, SoundWire IRQ/wake processing, D0i3 transitions, and debugfs region accessibility including IPC4 `fw_regs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/intel/tgl.c -->
