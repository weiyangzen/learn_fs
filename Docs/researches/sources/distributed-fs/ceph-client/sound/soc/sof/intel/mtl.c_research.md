# sources/distributed-fs/ceph-client/sound/soc/sof/intel/mtl.c

Purpose: implements Meteor Lake/ACE IPC4 HDA DSP operations, interrupt control, firmware boot preparation, core power management, IPC send/thread handling, debug dump support, and MTL/ARL chip descriptors.

Important APIs: `sof_mtl_set_ops()` copies common HDA ops, installs MTL IPC thread/send/mailbox/window/debug/pre-post-fw/core ops, allocates `sof_ipc4_fw_data`, enables context save/library loading, and sets DAI ops. `mtl_enable_interrupts()`, `mtl_enable_ipc_interrupts()`, and `mtl_disable_ipc_interrupts()` manage host IPC/SoundWire interrupt masks. `mtl_dsp_pre_fw_run()` powers DSP subsystem/gated domains and ungates SoundWire I/O. `mtl_dsp_cl_init()` sends ROM purge/boot IPC, powers primary core, waits for ROM status, enables interrupts, and dumps on final failure. `mtl_ipc_irq_thread()` handles DONE replies, BUSY target messages, notifications, and delayed IPC resend. `mtl_power_down_dsp()` powers down core and subsystem.

Control flow: boot calls pre_fw_run, then code loader `cl_init`, then post_fw_run. IPC send writes mailbox payload, extension, then primary|BUSY unless TX is busy, in which case the message is stored in `hdev->delayed_ipc_tx_msg`. The IPC IRQ thread acknowledges DSP replies, processes FW/host messages, and retries delayed sends after ACK. Core_get/put powers primary core locally and delegates secondary core state to IPC PM ops.

State and persistence: persistent runtime state includes `sdev->private` IPC4 data, `delayed_ipc_tx_msg`, core masks/refcounts, IMR flags, and interrupt mask registers. Debugfs map exposes HDA/PP/DSP/fw_regs regions.

Dependencies and integration: used by PCI MTL/ARL and inherited by LNL/NVL/PTL layers. Depends on HDA common ops, IPC4 helpers, telemetry dump, SoundWire callbacks, and MTL register definitions in `mtl.h`.

Risks and test signals: risks include delayed IPC pointer lifetime, interrupt mask ordering, primary core ownership/power polling, ROM status timing workaround, dspless early returns, and final-attempt dump gating. Test firmware boot cold/IMR, IPC request/reply/notification/delayed send, PM core_get/put, SoundWire IRQ, ARL-S descriptor selection, and probe failure unwind.
