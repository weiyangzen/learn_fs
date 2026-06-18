
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/skylake/uncore-interconnect.json

## Purpose

This file defines 8 Skylake client uncore interconnect/arbitration events. The event set covers arbitration tracker request counts and occupancy, including all requests, data reads, direct DRD requests, writes, coherent tracker requests, and cycles with any request.

The public aliases are `UNC_ARB_COH_TRK_REQUESTS.ALL`, `UNC_ARB_TRK_OCCUPANCY.*`, and `UNC_ARB_TRK_REQUESTS.*`. They allow perf users to observe uncore arbitration pressure and request mix without specifying raw codes.

## Important Schema Fields and APIs

The JSON objects use the perf event descriptor schema:

- `EventName`: symbolic alias exposed by perf.
- `EventCode`: uncore arbitration event selector.
- `UMask`: request/occupancy subtype selector.
- `CounterMask`: present on occupancy cycle-style rows to require a minimum condition before counting.
- `Unit`: the uncore arbitration/interconnect PMU unit.
- `Counter`: allowed uncore counter selector.
- `PerPkg`: package-scoped accounting flag.
- `BriefDescription`: surfaced by `perf list`.

`CounterMask` maps through `jevents.py` to `cmask=...`, which changes the event from simple occurrence counting to thresholded cycle counting for the relevant rows.

## Control Flow and Data Flow

The generation flow is the standard perf PMU path: JSON -> `jevents.py` parsing -> generated PMU event table -> runtime alias lookup. At runtime, selecting an `UNC_ARB_*` alias programs the uncore arbitration unit with the given event code, mask, and optional counter mask.

These raw counters can feed manual performance investigations or higher-level metrics that need interconnect occupancy/request rates. There is no internal branching or call graph inside the file.

## State and Persistence

The file is immutable source metadata. Persistent generated state exists only in build artifacts and the perf binary. Live counter state is held in package uncore PMU registers and perf aggregation structures during a profiling run.

## Dependencies and Integration Points

Dependencies are the Skylake uncore arbitration PMU model, kernel support for the listed unit, and perf's JSON event parser. Integration points are `arch/x86/mapfile.csv`, `jevents.py`, generated `pmu-events.c`, `perf list`, and `perf stat` event scheduling. Because all events are package-scoped uncore events, they integrate differently from core PMU events and may require system-wide permissions or root/kernel `perf_event_paranoid` settings.

## Risks

The main risk is semantic ambiguity between request counts and occupancy/cycle counts. `CounterMask` rows are especially easy to misread because they count cycles satisfying a condition rather than requests. Uncore availability varies by SKU, firmware, kernel driver, and virtualization environment; aliases may list but fail to run if the PMU is absent or blocked. Incorrect `PerPkg` handling can lead to double-counting or undercounting in aggregate reports.

## Test Signals

Build-time signals are valid JSON and successful `jevents.py` generation. Runtime signals include `perf list UNC_ARB`, `perf stat -a -e` for each alias on Skylake hardware, and sanity checks that request events increase under memory/interconnect load while occupancy cycle events respond to sustained traffic.
