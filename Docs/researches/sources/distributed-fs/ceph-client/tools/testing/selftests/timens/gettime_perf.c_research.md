# sources/distributed-fs/ceph-client/tools/testing/selftests/timens/gettime_perf.c

## Purpose
Extended benchmark comparing `clock_gettime()` performance inside and outside a time namespace, including vDSO function paths.

## Important APIs, Types, and Functions
Functions are `fill_function_pointers()`, `test(clockid, clockstr, in_ns)`, and `main()`. It uses `dlopen`/`dlsym`-style resolution for vDSO symbols and clock APIs.

## Control Flow
The program resolves clock function pointers, measures repeated gettime calls for selected clocks outside a namespace, enters a time namespace, applies offsets if needed, and measures again. Results are printed rather than strict pass/fail functional assertions.

## State and Persistence Behavior
No persistent state. Runtime state includes loaded symbol pointers, namespace membership, and measured timing loops.

## Dependencies and Integration Points
Depends on `-ldl`, vDSO availability, `clock_gettime`, time namespaces, and shared timens helpers. It integrates with performance regression tracking rather than functional gating.

## Risks and Edge Cases
Benchmarks are noisy and scheduler/CPU-frequency dependent. vDSO symbol availability differs by architecture/libc. Root/time namespace support is still required for in-namespace measurements.

## Test Signals
Signals are printed latency/performance numbers for supported clocks in host and namespace contexts.
