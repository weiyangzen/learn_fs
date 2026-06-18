# sources/distributed-fs/ceph-client/sound/soc/intel/avs/apl.c

## Purpose
This file implements Apollo Lake/Goldmont-class platform-specific AVS DSP operations. It handles IPC interrupt recognition, debug-log enablement, log buffer draining, firmware coredump collection, and D0ix low-power policy for cAVS 1.5/1.8 style firmware.

## Important APIs, types, and functions
`avs_apl_dsp_interrupt()` checks `AVS_ADSP_REG_ADSPIS` and dispatches IPC interrupts to `avs_skl_ipc_interrupt()`. Under debugfs, `avs_apl_enable_logs()` builds `avs_apl_log_state_info` and sends `avs_ipc_set_enable_logs()`. Log handling is `avs_apl_log_buffer_status()` and `avs_apl_wait_log_entry()`. Crash collection is `avs_apl_coredump()`, using firmware register windows and log payload buffers. Power policy is `avs_apl_lp_streaming()`, `avs_apl_d0ix_toggle()`, and `avs_apl_set_d0ix()`. The exported operation table is `avs_apl_dsp_ops`.

## Control flow
On interrupt, the handler reads ADSPIS, ignores invalid `UINT_MAX` reads, and services IPC when the IPC bit is set. Log-buffer notifications read firmware log layout, optionally dump wrapped and linear payload regions to the tracing FIFO, and always advance the firmware-visible read pointer. Coredump captures the firmware register window, optionally drains pre-stack logs, waits up to 10 ms for stack-dump log entries, copies wrapped log payload data until the requested stack size is gathered, updates read pointers, and submits the dump through `dev_coredumpv()`.

D0ix policy wakes unconditionally when requested. When considering sleep, it permits D0ix if no paths are active or if every gateway copier in every active path has `lp_buffer_alloc` set. `avs_apl_set_d0ix()` tells firmware whether D0ix is being entered with active low-power streaming.

## State and persistence behavior
This file does not own long-lived state, but it reads and updates firmware log-buffer read pointers, consumes trace data into AVS logging infrastructure, and walks `adev->path_list` under `path_list_lock`. Coredumps are handed to the kernel devcoredump facility.

## Dependencies and integration points
It depends on HD-audio extended register access, AVS messages, path/topology models, log-buffer helpers, debugfs logging infrastructure, devcoredump, and generic HDA firmware load operations. Its operation table is referenced by AVS platform descriptors for APL/GLK-class devices.

## Risks and edge cases
Log pointer handling must handle wraparound correctly and avoid reading stale data. Coredump stack collection may be incomplete if stack entries do not arrive before timeout, but register data is still dumped. D0ix traversal assumes copier modules with gateway attributes are represented in active paths and that `lp_buffer_alloc` correctly models low-power buffer placement. `resource_mask` validation in log enablement depends on `fls_long()` versus actual DSP core count.

## Test signals
Test IPC interrupt recognition, log enable/disable per core, log buffer wraparound draining, behavior with no log consumer, coredump with and without stack dump, coredump timeout, D0ix allow/deny for no paths, all-LP gateways, and any non-LP gateway, plus firmware return-code conversion through `AVS_IPC_RET()`.
