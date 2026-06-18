# sources/distributed-fs/ceph-client/sound/soc/intel/avs/mtl.c

Purpose: Provides Meteor Lake/ACE 1.x DSP operations for power, stall, IPC interrupt handling, and interrupt enable/disable.

Important APIs/functions: `avs_mtl_core_power()`, `avs_mtl_core_reset()`, `avs_mtl_core_stall()`, `avs_mtl_dsp_interrupt()`, and `avs_mtl_interrupt_control()`. Internal helpers power the DSP domain via HfDSSCS/HfPWRCTL and process IPC acknowledgements/responses through MTL host IPC registers.

Control flow: Power-on sets DSP domain SPA, waits for CPA, prevents power gating, waits for power-gate status, and assigns ownership to host. Power-off allows power gating, clears SPA, and waits CPA clear. IPC interrupt handling disables DONE/BUSY interrupts, completes host request acknowledgements, reads response primary/extension registers, calls `avs_dsp_process_response()`, acknowledges firmware, then reenables IPC control bits.

State and persistence: State lives in device registers and IPC completions. No persistent driver-owned objects are created.

Dependencies and integration: Uses `registers.h` MMIO helpers, `trace_avs_dsp_core_op()`, `avs_dsp_process_response()`, completion in `adev->ipc`, and platform ops tables elsewhere.

Risks: Register ordering is hardware-sensitive. Failure to restore HIPC control bits can wedge IPC. `avs_mtl_core_reset()` is a no-op because ACE 1.x lacks a logical equivalent, so reset assumptions must be platform-aware. Only main core mask is honored.

Test signals: Boot/resume on MTL hardware, IPC round-trip under interrupts, power-gating transitions, timeout paths from `readl_poll_timeout`, and tracepoint validation for core operations.
