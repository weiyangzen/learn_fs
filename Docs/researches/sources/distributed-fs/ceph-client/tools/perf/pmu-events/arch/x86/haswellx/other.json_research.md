<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/other.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/other.json

## Purpose

`other.json` defines four Haswell-X PMU events that do not fit the larger memory or pipeline categories: privilege-level cycle accounting and split/uncacheable lock duration. These aliases support OS/kernel-mode analysis and lock contention diagnostics.

The file is a JSON array of event records using the perf PMU event schema: `EventName`, `EventCode`, `UMask`, `Counter`, `SampleAfterValue`, optional `CounterMask`, `EdgeDetect`, `BriefDescription`, and `PublicDescription`.

## Important events

`CPL_CYCLES.RING0` counts unhalted core cycles while the thread is in ring 0. `CPL_CYCLES.RING123` counts unhalted cycles while the thread is outside ring 0, covering rings 1, 2, and 3. Both use event code `0x5C`, counters `0,1,2,3`, and different umasks.

`CPL_CYCLES.RING0_TRANS` counts intervals between processor halts while in ring 0. It adds `CounterMask: 1` and `EdgeDetect: 1` to the same `0x5C`/`0x1` base encoding and has a lower sample period.

`LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION` counts cycles in which L1D and L2 are locked because of an uncacheable lock or split lock. It uses event code `0x63`, umask `0x1`, and general counters `0,1,2,3`.

## Control flow and evaluation model

No local control flow exists. Perf converts the event records into encodings and schedules them on general-purpose counters. The ring events are separated by umask; the transition event uses edge-detection and counter-mask semantics to count transitions rather than raw cycles.

## State and persistence behavior

The file stores static aliases only. Runtime state is the PMU counter configuration and sampling state maintained by perf and the kernel. `SampleAfterValue` controls default sampling periods when these aliases are used for profiling.

## Dependencies and integration points

These aliases feed OS and lock-related metrics in `hsx-metrics.json`, including kernel utilization/CPI and lock-latency analysis. Their group descriptions are represented by metric groups such as `OS`, `LockCont`, and related TMA issue groups in `metricgroups.json`.

They integrate with the same Haswell-X PMU table generation path as `memory.json` and `pipeline.json`, but have no direct dependency on offcore MSRs or PEBS.

## Risks and maintenance notes

The primary risks are semantic. Privilege-level accounting depends on accurate CPL attribution and may be affected by virtualization or host/guest counting policy. The ring 0 transition event relies on edge-detect/cmask behavior; a parser or generator bug in those fields would change the event from transition counting to ordinary cycle counting.

Split-lock/uncacheable-lock cycles can be rare, workload-dependent, and platform-policy-sensitive. Measurements may be affected by split-lock detection or mitigation settings outside perf.

## Test signals

Validation should include JSON parsing, `perf list` visibility of all four aliases, and event encoding checks for `CounterMask` and `EdgeDetect` on `CPL_CYCLES.RING0_TRANS`. Runtime smoke tests can use `perf stat -e CPL_CYCLES.RING0,CPL_CYCLES.RING123` and a lock-heavy workload for `LOCK_CYCLES.SPLIT_LOCK_UC_LOCK_DURATION` on supported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/other.json -->
