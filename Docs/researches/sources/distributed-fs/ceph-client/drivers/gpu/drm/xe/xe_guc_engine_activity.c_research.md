# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guc_engine_activity.c

## Purpose
Implements GuC engine activity accounting. It allocates GGTT-visible buffers for GuC-written activity metadata and per-engine counters, enables GuC reporting, and exposes active and total tick queries for native and SR-IOV PF per-function views.

## Important APIs, Types, And Functions
Exports `xe_guc_engine_activity_init`, `xe_guc_engine_activity_supported`, `xe_guc_engine_activity_enable_stats`, `xe_guc_engine_activity_function_stats`, `xe_guc_engine_activity_active_ticks`, and `xe_guc_engine_activity_total_ticks`. Core helpers include `allocate_engine_activity_group`, `allocate_engine_activity_buffers`, `enable_engine_activity_stats`, `enable_function_engine_activity_stats`, `get_engine_active_ticks`, and `get_engine_total_ticks`.

## Control Flow
Initialization checks that the driver is not a VF and that the GuC submission interface is at least 1.14.1. It allocates software activity groups, allocates one device-level metadata buffer and one activity buffer, computes the GPM timestamp shift from `RPM_CONFIG0`, and registers teardown. Enabling sends a blocking GuC CT action with buffer GGTT addresses. Per-function stats allocate buffers for PF plus VFs, send the function-buffer action, and seed CPU timestamps for non-PF functions. Queries map the appropriate buffer slice, read metadata and activity fields, cache change counters, accumulate deltas, and derive running active ticks from `MISC_STATUS_0` when GuC says an engine is currently running.

## State And Persistence
Persistent state lives in `guc->engine_activity`: support flag, timestamp shift, allocated groups, BO pointers, function count, cached metadata/activity snapshots, CPU timestamps, accumulated active totals, and quanta totals. BOs are pinned/mapped until explicit disable for function stats or device-managed teardown for the global buffers.

## Dependencies And Integration Points
Depends on GuC CT actions `XE_GUC_ACTION_SET_DEVICE_ENGINE_ACTIVITY_BUFFER` and `XE_GUC_ACTION_SET_FUNCTION_ENGINE_ACTIVITY_BUFFER`, firmware ABI structs from `xe_guc_fwif.h`, engine class mapping, MMIO timestamp registers, Xe BO helpers, SR-IOV PF helpers, and tracepoints.

## Risks And Test Signals
Counter logic relies on GuC change numbers to avoid double counting. Function queries must be rejected for non-PF or out-of-range IDs. The active calculation uses lower 32 bits of the shifted GPM timestamp, so wrap behavior is implicit in unsigned arithmetic. Test signals include GuC interface version gating, trace output from `trace_xe_guc_engine_activity`, PF/VF enable-disable paths, and runtime validation that active ticks never regress across samples.
