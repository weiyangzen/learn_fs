# sources/distributed-fs/ceph-client/sound/soc/sof/trace.c

Purpose: thin IPC-version-neutral wrapper around firmware tracing operations.

Important APIs/functions: `sof_fw_trace_init()` gets `fw_tracing` ops from `sof_ipc_get_ops()` and disables trace support when absent. `sof_fw_trace_free()`, `sof_fw_trace_fw_crashed()`, `sof_fw_trace_suspend()`, and `sof_fw_trace_resume()` gate calls on `sdev->fw_trace_is_supported` and then invoke optional or mandatory IPC tracing callbacks.

Control flow/state: persistent state is `sdev->fw_trace_is_supported` and IPC-specific `sdev->fw_trace_data`. Suspend/resume and crash notifications are no-ops when tracing is unsupported.

Dependencies/integration: depends on `sof-priv.h` IPC ops and is called by SOF core PM/crash paths. IPC3/IPC4 implementations provide the actual trace buffer, DMA, or mtrace mechanics.

Risks/test signals: `sof_fw_trace_suspend()` and `resume()` assume the `suspend`/`resume` callbacks are present when tracing is supported; IPC ops must honor that contract. Tests should cover tracing disabled by missing ops, init failure behavior, crash notification, runtime/system suspend-resume, and cleanup ordering after IPC teardown.
