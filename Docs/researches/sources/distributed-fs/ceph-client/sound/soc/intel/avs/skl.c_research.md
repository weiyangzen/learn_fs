# sources/distributed-fs/ceph-client/sound/soc/intel/avs/skl.c

Purpose: Implements Skylake/cAVS 1.5 platform DSP operations, including IPC/CLDMA interrupts, debug log handling, coredump capture, and unsupported D0ix stubs.

Important APIs/functions: `avs_skl_ipc_interrupt()`, internal `avs_skl_dsp_interrupt()`, `avs_skl_enable_logs()`, `avs_skl_log_buffer_offset()`, `avs_skl_log_buffer_status()`, `avs_skl_coredump()`, and `const struct avs_dsp_ops avs_skl_dsp_ops`.

Control flow: DSP interrupt reads ADSPIS, dispatches CLDMA interrupts to the code loader and IPC interrupts to `avs_skl_ipc_interrupt()`. IPC handler clears HIPC control, completes host acknowledgements, reads HIPCT/HIPCTE responses, calls `avs_dsp_process_response()`, acknowledges firmware busy, and re-enables control bits. Log status reads firmware write pointer to dump the active half-buffer. Coredump copies firmware register SRAM to devcoredump.

State and persistence: Uses IPC completion state, CLDMA code-loader state, firmware log buffers in SRAM, and devcoredump artifacts. D0ix state is intentionally unsupported/no-op.

Dependencies and integration: Integrates `cldma.h`, `debug.h`, `messages.h`, `registers.h`, firmware logging helpers, and generic core power/reset/stall ops.

Risks: Half-buffer log selection assumes firmware write pointer semantics. Coredump copies a fixed 4 KiB firmware register window. D0ix no-op behavior must not be mistaken for real low-power support. Interrupt acknowledgement order is critical.

Test signals: SKL firmware load via CLDMA, IPC request/reply interrupts, CLDMA interrupt during module transfer, debug log wakeups, forced firmware exception coredumps, and D0ix policy callers on SKL.
