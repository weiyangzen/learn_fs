# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwell/uncore-interconnect.json

## Purpose

`uncore-interconnect.json` defines seven Broadwell uncore ARB events for coherence tracker and interconnect request tracking. It measures allocated tracker entries, tracker occupancy, cycles with outstanding requests waiting for memory-controller data return, direct data-read occupancy, and write/request allocations.

## Important APIs, Types, and Data Fields

The file is a JSON event array with uncore fields. All rows use `Unit: ARB` and `PerPkg: 1`. The families are `UNC_ARB_COH_TRK_REQUESTS.ALL`, `UNC_ARB_TRK_OCCUPANCY.*`, and `UNC_ARB_TRK_REQUESTS.*`. Occupancy rows use event code `0x80`, request allocation rows use `0x81`, and coherence tracker requests use `0x84`. Some occupancy rows are constrained to counter `0`; request rows typically use counters `0,1`. `UNC_ARB_TRK_OCCUPANCY.CYCLES_WITH_ANY_REQUEST` uses `CounterMask: 1` to count cycles with at least one qualifying outstanding request.

## Control Flow and Data Flow

There is no executable control flow. Perf's generator emits uncore ARB event metadata; runtime perf commands resolve the event name to an ARB PMU instance and program package-level uncore counters. Occupancy events count cycle-weighted tracker residency, while request events count allocations, so downstream analysis must treat them as different units.

## State and Persistence Behavior

The file stores static metadata only. It does not persist interconnect queues or request state. Package-level aggregation is declared through `PerPkg: 1`.

## Dependencies and Integration Points

The file depends on Broadwell uncore ARB PMU support in the kernel and the platform exposing ARB units. It integrates with uncore perf stat workflows, memory-controller latency investigation, coherence pressure analysis, and package-level traffic profiling that complements CBOX and offcore core events.

## Risks and Edge Cases

The main risk is unit confusion: occupancy rows count cycle residency, while request rows count allocations. Counter constraints are narrower than many core events, especially for occupancy rows limited to counter `0`. Platform/kernel uncore support may vary across Broadwell client/server derivatives. The descriptions mention coherent and non-coherent traffic from IA cores, graphics, LLC, and memory controller interactions, so attribution to one requester requires additional events or workload control.

## Test Signals

Smoke-test `perf list` and `perf stat` for ARB events on a Broadwell system with uncore PMUs. Memory-intensive workloads should move occupancy and request counters. A consistency check should ensure occupancy rows keep their counter restrictions and request rows keep `PerPkg` package semantics.
