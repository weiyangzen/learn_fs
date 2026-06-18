<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/debug.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/debug.h

Purpose: debug/logging interface declarations and log buffer helpers for AVS.

Important APIs, types, and functions: log buffer macros `avs_log_buffer_size()`, `avs_log_buffer_addr()`, APL log layout helpers, locked status helper `avs_log_buffer_status_locked()`, debugfs/probe function declarations under `CONFIG_DEBUG_FS`, and no-op stubs when debugfs is disabled. `AVS_SET_ENABLE_LOGS_OP(name)` populates DSP ops conditionally.

Control flow: platform DSP ops call through enable-log hooks only when debugfs is compiled. Log buffer address computation asks the platform op for a per-core offset and maps it into the debug SRAM window.

State and persistence: no state owned by the header; it coordinates access to `adev->trace_lock`, firmware config, and debug window.

Dependencies and integration points: used by platform ops, `debugfs.c`, `board_selection.c` probe-board registration, and firmware notification handling.

Risks: `avs_log_buffer_size()` divides by `adev->hw_cfg.dsp_cores`; callers need valid hardware config. Stubs make debug-only registration return `-EOPNOTSUPP`, so callers should treat that as optional.

Test signals: debugfs-disabled builds compile with stubs, debugfs-enabled builds expose trace/probe APIs, and log buffer offset failures return NULL rather than invalid SRAM pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/debug.h -->
