<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/cnl.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/cnl.c

Purpose: Cannon Lake-class DSP interrupt handling and DSP operation table.

Important APIs, types, and functions: `avs_cnl_dsp_interrupt()` is exported; internal `avs_cnl_ipc_interrupt()` handles CNL HIPC registers; `avs_cnl_dsp_ops` wires generic power/reset/stall, CNL interrupting, HDA firmware loading, APL log/status/coredump/D0ix helpers, and APL log enabling.

Control flow: DSP interrupt reads ADSPIS and, if IPC is pending, calls the IPC handler. The handler masks DONE/BUSY interrupts, reads ack and response registers, completes `done_completion` when DSP acknowledges a host request, processes response/notification payloads via `avs_dsp_process_response()`, acknowledges response registers, waits briefly for DONE clearing, then re-enables DONE/BUSY interrupts.

State and persistence: updates IPC completions and relies on `adev->ipc` state. No file-local persistent state.

Dependencies and integration points: used by `core.c` CNL/CML/RKL platform specs and by ICL/TGL-derived ops through reuse. Integrates with `ipc.c` response parsing and register constants in `registers.h`.

Risks: incorrect ack ordering can wedge IPC. The poll after response ack ignores return value, so hardware clock-gating propagation failures are not fatal but can affect later interrupts.

Test signals: IPC request/reply completions occur without timeouts on CNL-class devices, notifications are processed, and no interrupt storms occur after ack/re-enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/cnl.c -->
