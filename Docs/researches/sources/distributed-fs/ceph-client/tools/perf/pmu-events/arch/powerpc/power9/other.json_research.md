# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power9/other.json

## Purpose

This is the largest POWER9 raw-event shard in the work item, defining 467 PMU events. It acts as a broad catch-all catalog for events not placed in the more focused topic files: issue-unit rejects, snoops, instruction-cache demand requests, transactional-memory instructions, queue occupancy, IERAT reloads, L3 retries, dispatch holds, branch predictors, prefetch streams, many marked events, translation events, memory hierarchy sources, and assorted pipeline or nest-adjacent counters.

## APIs, types, and schema

Every entry follows the raw PMU event schema with `EventName`, `EventCode`, and `BriefDescription`. `jevents.py` converts each entry into a compact generated event row under the default core PMU unless a `Unit` field says otherwise; this file uses the simple core-event shape. The generated names are lower-case, while metric formulas and source JSON retain the original `PM_*` names.

## Control flow and integration

The file is loaded with the rest of the POWER9 directory and contributes a large share of the generated POWER9 event table. It is also a dependency surface for `metrics.json`: many formulas rely on raw event names defined here rather than in the smaller topic files. Build flow is `pmu-events/Build` to `jevents.py` to generated `pmu-events.c`, then runtime lookup through perf's PMU event and metric APIs.

## State, persistence, and dependencies

The JSON is static metadata. It depends on POWER9 PMU encoding correctness, consistent event naming, valid descriptions, and the generator's ability to reject duplicate event names. Because it contains a wide semantic mix, users and metrics depend on the event name and description more than on the topic filename.

## Risks and test signals

The main risks are catalog sprawl and hidden coupling: a rename or deletion can break metric formulas far from this file, and a wrong event code can affect many user workflows. The catch-all topic also makes semantic review harder. Strong test signals include `jq empty`, full `jevents.py` generation, duplicate-name assertions, cross-checking `metrics.json` event references, and representative `perf list` or `perf stat -e` checks for issue, branch, transactional-memory, translation, and cache-source events.
