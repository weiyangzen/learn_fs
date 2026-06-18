# Research: sources/distributed-fs/openafs/src/rx/rx_call.c

## sources/distributed-fs/openafs/src/rx/rx_call.c

### Purpose
`rx_call.c` implements lightweight public accessors and statistics recording for `struct rx_call`, keeping callers from directly depending on internal call layout.

### Important Functions
- `rx_ConnectionOf`, `rx_Error`, `rx_GetRemoteStatus`, `rx_GetLocalStatus`, `rx_SetLocalStatus`, `rx_GetCallAbortCode`, and `rx_SetCallAbortCode` expose simple fields.
- `rx_RecordCallStatistics` computes queue and execution durations and calls `rxi_IncrementTimeAndCount`.
- `rx_GetCallStatus` returns read sequence, transmit sequence, last send time, and last receive time for monitoring.

### Control Flow and State
The accessor functions read or write fields directly. `rx_RecordCallStatistics` takes current time, subtracts `call->startTime` to compute execution duration, subtracts `call->queueTime` from `startTime` for queue duration, and records bytes sent/received through the peer stats path. `rx_GetCallStatus` only writes non-NULL output pointers.

### Dependencies and Integration Points
Includes `rx.h`, `rx_call.h`, `rx_conn.h`, `rx_atomic.h`, and `rx_internal.h`. The statistics path integrates with `rxi_IncrementTimeAndCount` in `rx.c` and peer-level RPC stats. Monitoring tools such as VolMonitor use `rx_GetCallStatus`.

### Risks and Edge Cases
- Accessors do not lock the call. Callers must already be in a context where these fields are stable enough or accept a snapshot race.
- `rx_RecordCallStatistics` assumes `queueTime`, `startTime`, `conn`, `peer`, and application byte counters are initialized.
- Return targets in `rx_GetCallStatus` are signed while stored fields are unsigned, which can truncate large sequence values.

### Test Signals
Exercise RPC stats with known queue/execution timing and byte counts. Validate monitoring output during active calls and with NULL output pointer combinations. Race-focused tests should verify consumers tolerate snapshot values.
