<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/debugfs.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/debugfs.c

Purpose: debugfs support for AVS firmware trace collection, SRAM/register dumps, and runtime probe-point control.

Important APIs, types, and functions: `avs_debugfs_init()/exit()`, `avs_logging_fw()`, `avs_dump_fw_log()`, `avs_dump_fw_log_wakeup()`, file operations for `strace`, `trace_control`, `fw_regs`, `debug_window`, `probe_points`, and `probe_points_disconnect`.

Control flow: init creates `avs` debugfs directory, default trace timer periods, trace/probe files, and dump files. `strace_open()` pins the module and allocates a PAGE_SIZE kfifo, `strace_read()` blocks until data is available then copies FIFO data to userspace, and release flushes remaining firmware log buffers before freeing. `trace_control_write()` parses integer arrays: one mask disables resources, mask plus priorities enables logging after forcing DSP out of D0ix and setting firmware time. Probe files query, connect, and disconnect firmware probe points via IPC. Register/window reads copy SRAM windows to temporary buffers for userspace.

State and persistence: trace FIFO, waitqueue, spinlock, aging/full timer periods, and `logged_resources` live in `avs_dev`. Logging keeps runtime PM active and D0ix disabled until all resources are disabled. Probe point connections are firmware state controlled through IPC.

Dependencies and integration points: depends on debugfs, kfifo, AVS IPC probe/log messages, platform `enable_logs` and `log_buffer_status` ops, runtime PM, and firmware notification `AVS_NOTIFY_LOG_BUFFER_STATUS`.

Risks: `strace_open()` returns `-EBUSY` if already initialized but does not drop the module reference on that path, which is a subtle resource-risk signal. User input for probe point arrays is binary-layout-sensitive and must align with descriptor sizes. Logging power-state bookkeeping must unwind on IPC failures.

Test signals: reading `strace` receives firmware log bytes after enabling `trace_control`; disabling last resource allows autosuspend; `fw_regs` and `debug_window` return expected sizes; `probe_points` lists and modifies firmware probe state; open/close cycles do not leak module refs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/debugfs.c -->
