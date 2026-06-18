<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/ipc.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/ipc.c

Purpose: AVS host-DSP IPC transport, response/notification handling, D0ix transition orchestration, timeout recovery, and IPC context lifecycle.

Important APIs, types, and functions: `avs_ipc_init()`, `avs_ipc_block()`, `avs_dsp_process_response()`, send variants `avs_dsp_send_msg*_timeout()`, ROM send variants, PM send variants, `avs_dsp_interrupt_control()`, D0ix helpers, and recovery work.

Control flow: send path optionally wakes DSP to D0i0 based on platform `d0ix_toggle`, serializes requests with `msg_mutex`, initializes RX/completions under `rx_lock`, writes payload to downlink SRAM and HIPC request registers, waits for BUSY/reply completion while tolerating interleaved notifications, copies reply payload back, and schedules delayed D0ix when allowed. ROM send path writes request while the main core is stalled and then unstalls it before waiting for DONE. Interrupt processing classifies headers as replies or notifications; replies fill `ipc->rx`, notifications handle FW_READY, log-buffer status, exception caught, and other payload types. Timeouts synthesize exception handling, disconnect streams, disable DSP cores, reboot firmware, and re-enable runtime PM.

State and persistence: `struct avs_ipc` tracks readiness, RX buffer, completions, recovery work, D0ix delayed work, disable depth, and current D0ix state. Firmware ready completion lives in `avs_dev`.

Dependencies and integration points: depends on platform HIPC register specs, DSP ops for D0ix/coredump/log handling, mailbox SRAM helpers, ALSA PCM stop paths, component list, firmware boot in `loader.c`, and tracepoints.

Risks: IPC readiness gates most operations with `-EPERM`; callers must distinguish blocked recovery from real failures. Notification interleaving retry loop is bounded but complex. `avs_dsp_enable_d0ix()` uses `atomic_dec_and_test`; unbalanced enable/disable calls can underflow policy. Recovery forcibly disconnects streams, so userspace sees PCM disconnects on firmware faults.

Test signals: ordinary IPCs complete within 300 ms, payload replies are copied for large config gets, FW_READY completes first boot, log notifications drain buffers, IPC timeout triggers recovery once, and runtime D0ix transitions occur after idle delay but not while disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/ipc.c -->
