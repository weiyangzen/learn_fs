# sources/distributed-fs/ceph-client/include/trace/events/cpuhp.h

## Purpose
`cpuhp.h` traces CPU hotplug state-machine callbacks and results.

## Important APIs, types, and functions
Events are `cpuhp_enter`, `cpuhp_multi_enter`, and `cpuhp_exit`. They record CPU id, target/state, step index, callback pointer, and return code.

## Control flow
The hotplug core emits enter events before invoking single-instance or multi-instance callbacks and emits exit after a step returns. Function pointers are printed symbolically via `%ps`.

## State and persistence behavior
The header stores no state. Records snapshot step and callback identity for one CPU hotplug transition.

## Dependencies and integration points
It depends on CPU hotplug internals and tracepoints. It integrates with CPU online/offline debugging, module hotplug callback validation, and latency analysis.

## Risks and test signals
Risks include pointer/symbol exposure, callbacks being unloaded after trace capture, and partial visibility if failures abort later steps. Test signals are CPU online/offline tests showing enter/exit pairs and nonzero returns on injected failures.
