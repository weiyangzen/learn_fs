# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-mtrace.c

## Purpose
Implements IPC4 firmware mtrace debug logging for CAVS 2 platforms. It enables firmware logs, maps per-core log slots from the debug window, exposes one debugfs file per core, supports log-priority mask tuning, updates log positions from firmware notifications, and drains logs on crash.

## APIs, Types, and Functions
The exported tracing ops object is `ipc4_mtrace_ops`. Cross-file API `sof_ipc4_mtrace_update_pos()` updates a core write pointer and wakes readers. Important internal functions are `ipc4_mtrace_init()`, `ipc4_mtrace_enable()`, `ipc4_mtrace_disable()`, `sof_mtrace_find_core_slots()`, `sof_ipc4_mtrace_dfs_open/read/release()`, priority-mask debugfs handlers, `ipc4_mtrace_fw_crashed()`, suspend and resume handlers. State is held in `struct sof_mtrace_priv`, `struct sof_mtrace_core_data`, and `struct sof_log_state_info`.

## Control Flow, State, and Persistence
Initialization checks firmware-reported log size and IPC4 mtrace type, allocates per-core state, seeds timer periods and base firmware log priorities, sends system time for log alignment, enables logs with `SOF_IPC4_FW_PARAM_ENABLE_LOGS`, scans debug-slot descriptors, and creates debugfs nodes. Each core debugfs file is exclusive-open, allocates a temporary read buffer, waits on a waitqueue for `host_read_ptr != dsp_write_ptr`, reads circular log data from the mailbox debug slot, prefixes the user buffer with available byte count, writes the new host read pointer back to firmware, and advances local state only while enabled. Position updates read the DSP write pointer from the core slot, align it to 4 bytes, and wake readers; early updates are delayed until slot discovery.

## Dependencies and Integration
Depends on SOF debug box layout, IPC4 debug-slot constants, SOF mailbox read/write, debugfs, wait queues, runtime tracing hooks, and firmware configuration parsed by `ipc4-loader.c`. It integrates with crash handling because a crashed DSP may stop sending log-buffer notifications.

## Risks and Test Signals
Risks include debug-window layout mismatch, lost log data on circular-buffer wrap, reads returning 0 while slot discovery is delayed, unchecked disable IPC result, priority masks changed while tracing is active, and tracing disabled silently to avoid blocking audio stack bring-up. Test signals are debugfs `mtrace/coreN` open/read/release behavior, logs waking after position notifications, crash-time drain, suspend disable/resume enable, invalid core update rejection, priority mask parse errors, and operation with unsupported mtrace type or zero log bytes.
