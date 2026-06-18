# sources/distributed-fs/ceph-client/include/trace/events/csd.h

## Purpose
`csd.h` traces call-single-data and smp-call-function activity.

## Important APIs, types, and functions
Events are `csd_queue_cpu`, `csd_function_entry`, and `csd_function_exit`. `csd_function` is the shared class for callback entry and exit.

## Control flow
The queue event records the target CPU, callsite, callback function, and CSD pointer when work is queued to another CPU. Entry and exit events bracket the callback execution on the receiving CPU.

## State and persistence behavior
The header has no state. Records snapshot pointers and CPU id; ordering and timestamps come from trace infrastructure.

## Dependencies and integration points
It depends on SMP call function types (`smp_call_func_t`, `call_single_data_t`) and tracepoint support. It integrates with inter-processor-call debugging and latency analysis.

## Risks and test signals
Risks include pointer/symbol exposure and very high volume on IPI-heavy systems. Test signals are smp_call_function workloads where queue, entry, and exit can be correlated by CSD pointer and function symbol.
