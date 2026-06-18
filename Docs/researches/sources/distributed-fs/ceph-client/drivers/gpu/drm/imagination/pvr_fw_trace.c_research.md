# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw_trace.c

## Purpose
Implements firmware trace buffer allocation, initial/module/debugfs trace-mask control, KCCB logtype updates, trace snapshot parsing, and debugfs files for per-thread firmware logs.

## Important APIs, types, and functions
- `pvr_fw_trace_init()` allocates per-thread FW trace buffers and a trace-buffer control structure.
- `pvr_fw_trace_fini()` destroys those objects.
- `pvr_fw_trace_debugfs_init()` creates `trace_N` files and `trace_mask`.
- `validate_group_mask()`, `build_log_type()`, and `update_logtype()` validate and apply enabled trace groups.
- Seq-file helpers `fw_trace_open()`, `fw_trace_seq_start()`, `fw_trace_seq_next()`, `fw_trace_seq_show()`, and `fw_trace_release()` expose a stable snapshot while firmware may keep writing.

## Control flow
Initialization allocates an uncached no-clear FW object for each firmware thread trace ring, reads the initial mask from the optional `init_fw_trace_mask` module parameter, allocates the no-clear control object with `tracebuf_ctrl_init()`, fills firmware addresses and host pointers for each ring, and records pointers to each thread's control-space entry.

Changing `trace_mask` validates that the requested groups are a subset of `ROGUE_FWIF_LOG_TYPE_GROUP_MASK`, updates local `group_mask` and firmware control `log_type`, then under `reset_sem` and `drm_dev_enter()` sends `ROGUE_FWIF_KCCB_CMD_LOGTYPE_UPDATE` and waits for completion. Opening a trace file copies the ring and assertion info, records the firmware write pointer as start offset, and uses seq iteration to decode valid IDs through `stid_fmts`.

## State and persistence
`struct pvr_fw_trace` stores the control FW object/mapping, per-thread buffer objects/mappings, current group mask, and FW tracebuf-space pointers. Trace buffers and control structures use `PVR_BO_FW_NO_CLEAR_ON_RESET`, so they persist across hard reset instead of being zeroed by common FW object reset.

## Dependencies and integration points
Depends on common FW object helpers, KCCB command submission, reset semaphore/device-enter lifetime protection, debugfs, module parameters, Rogue firmware trace ABI, string-format table `stid_fmts`, and FWIF trace structures. `pvr_fw_create_structures()` wires the trace control address into SYSINIT.

## Risks
Trace parsing trusts firmware-produced IDs and format table parameter counts, stopping on corrupt or unknown IDs. `update_logtype()` mutates local state before KCCB completion, so a failed update can leave host state ahead of firmware. Buffers are copied without locking against firmware writes by design, producing consistent snapshots only after the copy.

## Test signals
Validate debugfs file creation, module parameter validation, mask set/get, KCCB logtype update success/failure, trace output formatting, assertion formatting, corrupt trace IDs, no-clear behavior across hard reset, and teardown after partial init failure.
