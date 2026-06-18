<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_dbg.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_dbg.c

Purpose: provides debugfs observability and control hooks for Amphion cores and instances, including queue state, driver buffer state, format/crop data, stream-buffer usage, firmware ring pointers, firmware log extraction, command/event flow history, and manual debug/reset triggers.

Important APIs/functions: `vpu_inst_create_dbgfs_file()`, `vpu_inst_remove_dbgfs_file()`, `vpu_core_create_dbgfs_file()`, `vpu_core_remove_dbgfs_file()`, and `vpu_inst_record_flow()`. Seqfile readers are `vpu_dbg_instance()`, `vpu_dbg_core()`, and `vpu_dbg_fwlog()`. Write handlers trigger `vpu_session_debug()` for instances and a core software reset attempt for idle powered cores.

Control flow: core and instance registration create debugfs files under `amphion_vpu`. Reading an instance file reports V4L2 queues, per-buffer vb2 and VPU states, crop, stream ring usage, message FIFO length, recent command/message flow, and codec-specific debug lines through `get_debug_info`. Reading a core file reports reserved regions, power/state, firmware version, instance count, core FIFO length, and command/message ring pointers. Reading firmware log drains the firmware print ring by advancing its read pointer.

State and persistence: debugfs dentries are stored on `vpu_dev`, `vpu_core`, and `vpu_inst`. Flow history is a 16-entry ring in `struct vpu_inst`. Firmware log reads mutate firmware log read offset; otherwise no durable persistence.

Dependencies and integration: depends on V4L2/vb2 queue internals, kfifo, pm_runtime, command/reset helpers, iface power state, and codec `get_debug_info` callbacks.

Risks: debug output indexes `vb2_stat_name[vb->state]` without a local bounds check. Firmware log read mutates shared firmware memory and may race with firmware writes. Core debug write can reset an idle powered core from userspace if debugfs permissions allow it. `to_vpu_stat_name()` treats `VPU_BUF_STATE_CHANGED` as unknown because it checks `<= VPU_BUF_STATE_ERROR`.

Test signals: inspect debugfs during idle, active decode, active encode, EOS drain, source change, and firmware-log generation; write instance/core debug files; verify removal on stream close and driver remove; run with unusual vb2 buffer states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_dbg.c -->
