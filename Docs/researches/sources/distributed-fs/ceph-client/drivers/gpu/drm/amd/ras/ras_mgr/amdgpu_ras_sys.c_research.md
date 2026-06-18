# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_sys.c

## Purpose

`amdgpu_ras_sys.c` implements the AMDGPU `ras_sys_func` callback table consumed by rascore. It provides event notification, timestamps, sequence numbers, GPU status, device identity, reset locking, interrupt detection, and PSP/TA memory lookup.

## Important APIs, Types, And Functions

The exported table is `amdgpu_ras_sys_fn`. Callback implementations include fatal event detection, poison-consumption notification, sequence number generation with XGMI hive sharing, event notifier dispatch, UTC timestamp, GPU status checks, device/system info, reset-domain lock control, RAS interrupt detection, and GPU memory block lookup for PSP ring/command/fence/firmware/RAS TA command memory.

## Control Flow, State, And Persistence

Event notification switches on rascore event IDs: bad pages schedule retirement work; poison consumption invokes PASID notification; reserve page calls AMDGPU page reservation; fatal errors call the global RAS ISR, generate UE seqno, and reset; update events notify DPM; RMA logs and reports reasons; reset events call manager reset; begin/end events bracket processing. Sequence generation uses the XGMI hive event manager when present, reuses fatal seqno during recovery, otherwise increments atomic sequence counters and event counts. Memory lookup maps logical rascore memory types to existing PSP BOs and validates addresses.

## Dependencies And Integration Points

It depends on AMDGPU RAS, reset, XGMI hive event state, DPM bad-page/RMA notifications, ras_log_ring, PSP memory fields, and manager process hooks. It is the rascore-to-driver boundary for side effects.

## Risks And Test Signals

Risks include null hive handling, event-notifier data type mismatches, fatal seqno reuse bugs, reset-lock imbalance, stale PSP memory pointers, and unimplemented put-memory semantics. Test signals include each notifier event, XGMI and non-XGMI sequence numbering, reset lock try/block paths, PSP memory validation, RMA logging, PASID callback invocation, and fatal interrupt handling.
