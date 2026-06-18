# sources/distributed-fs/ceph-client/sound/soc/sof/intel/apl.c

Purpose: `apl.c` specializes the shared HDA SOF operations for Apollolake and Geminilake, which use cAVS 1.5+ HDA DSP hardware. It exports `sof_apl_ops_init()` and `apl_chip_info`, letting PCI discovery code clone common HDA behavior and install APL-specific IPC, debug, boot, and descriptor data.

Important APIs and types: `sof_apl_ops_init(struct snd_sof_dev *sdev)` copies `sof_hda_common_ops` into the global `sof_apl_ops`, then selects IPC3 or IPC4 handlers depending on `sdev->pdata->ipc_type`. IPC3 uses `hda_dsp_ipc_irq_thread`, `hda_dsp_ipc_send_msg`, `hda_ipc_dump`, and `hda_dsp_set_power_state_ipc3`. IPC4 allocates `struct sof_ipc4_fw_data`, sets the manifest offset, mtrace type, library-loader callback, `hda_dsp_ipc4_irq_thread`, `hda_dsp_ipc4_send_msg`, `hda_ipc4_dump`, and IPC4 power-state callback.

Control flow: initialization is table-driven. The function starts from common ops, installs protocol-specific hooks, calls `hda_set_dai_drv_ops()` to bind DAI callbacks, sets the APL debug map, and points firmware execution to `hda_dsp_cl_boot_firmware` with `hda_dsp_post_fw_run` and `hda_dsp_core_get`. `apl_chip_info` supplies the register layout, IPC request/ack masks, ROM status register, SSP count/base, D0I3 offset, cAVS quirk, and callbacks for boot, power-down, interrupts, and IPC IRQ detection.

State and persistence behavior: IPC4 setup stores heap-allocated private firmware data in `sdev->private` and relies on later HDA cleanup to free it. The descriptor is constant and shared. Runtime state is primarily held by the common HDA layer.

Dependencies, risks, and test signals: this file depends on `hda.h`, IPC4 private data, SOF extended manifest v4, and common HDA exports. Risks include leaking or misconfiguring `sdev->private` for IPC4, selecting the wrong mtrace type, or mismatching IPC registers in `apl_chip_info`. Test signals include successful IPC3 and IPC4 firmware boot, external IPC4 library load, DAI ops assignment, and debugfs region visibility for `hda`, `pp`, and `dsp`.
