# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/jaketown/other.json

## Purpose

This file defines five miscellaneous Jaketown core PMU events that do not fit the larger memory, pipeline, cache, floating point, or frontend/backend topic files. The covered event families are `CPL_CYCLES`, `HW_PRE_REQ`, and `LOCK_CYCLES`.

The events expose privilege-level cycle accounting, ring-transition intervals, L1D hardware prefetch misses, and split/uncacheable lock duration. This is build-time data for perf's event table, not executable logic.

## Important APIs, Types, And Data Contracts

The file is a JSON array consumed by `jevents.py` through the standard `JsonEvent` path. It uses `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, `CounterMask`, `EdgeDetect`, and `BriefDescription`.

`CPL_CYCLES.RING0` and `CPL_CYCLES.RING123` count unhalted cycles by current privilege level. `CPL_CYCLES.RING0_TRANS` adds `CounterMask: "1"` and `EdgeDetect: "1"` to count intervals/transitions rather than raw cycles. `HW_PRE_REQ.DL1_MISS` counts L1D hardware prefetch requests that miss. `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION` counts cycles where L1/L2 are locked by UC or split-lock behavior.

`CounterMask` and `EdgeDetect` are translated by the generator to `cmask=` and `edge=` config terms. These modifiers are semantically important for the transition event.

## Control Flow And Generation Behavior

The perf PMU event generator infers the topic `other` from the filename, then emits one generated event row per array element. The events become discoverable through `perf list other` and selectable by their lower-cased names.

There is no control flow inside the file. Runtime behavior is the standard perf event path: user selection resolves the generated event name, perf programs the event select/umask plus modifiers, and the kernel reads counts from the allowed programmable counters.

## State And Persistence

The file is static persistent metadata. Runtime state is limited to hardware counter values while perf sessions are active. All five entries allow counters `0,1,2,3`, so they are more schedulable than events restricted to a fixed counter or counter 3.

The transition event's edge-detect state is implemented by hardware PMU configuration derived from the JSON fields.

## Dependencies And Integration Points

Dependencies include `jevents.py`, the x86 PMU event generator, generated C PMU tables, and perf's event parser. The hardware dependency is Intel Jaketown PMU support for event codes `0x5C`, `0x4E`, and `0x63`.

The file integrates with broader profiling workflows by filling gaps: privilege-cycle data helps separate kernel/user execution, prefetch misses complement memory/cache analysis, and lock cycles can diagnose split-lock or UC access behavior.

## Risks And Edge Cases

The terse file can be overlooked in schema or documentation updates. The most sensitive record is `CPL_CYCLES.RING0_TRANS`; removing `CounterMask` or `EdgeDetect` would silently convert interval counting into a different measurement.

Privilege-level counters depend on accurate hardware CPL classification and may be affected by virtualization or kernel/hypervisor restrictions. Lock-cycle counts can be rare or workload-specific, so zero counts do not necessarily indicate a broken event.

## Test Signals

Static tests should run `jq empty other.json` and verify all five entries include non-empty `EventName`, `EventCode`, and `Counter` fields. Generated output should include lower-case names such as `cpl_cycles.ring0_trans` with `cmask=1,edge=1`.

Runtime validation on compatible hardware can compare `CPL_CYCLES.RING0` and `CPL_CYCLES.RING123` under kernel-heavy and user-heavy workloads. A microbenchmark that triggers split locks or UC accesses can validate `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION`, though such tests may need elevated privileges or platform-specific setup.
