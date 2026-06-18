# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswell/counter.json

## Purpose
This JSON file declares counter inventory metadata for Intel Haswell PMU units in perf. Unlike event files, it does not define event aliases or encodings; it tells the PMU event tooling how many fixed and generic counters exist for selected units. The source was read as a complete 21-line JSON array.

## Important APIs, Types, and Functions
The schema fields are `Unit`, `CountersNumFixed`, and `CountersNumGeneric`. The four rows are `core` with 3 fixed and 4 generic counters, `CBOX` with 0 fixed and 2 generic counters, `ARB` with 0 fixed and 2 generic counters, and `cbox_0` with 1 fixed and 0 generic counters. The first three rows store counter counts as strings, while `cbox_0` stores `CountersNumFixed` as a numeric JSON value, so consumers must tolerate both string and numeric forms.

There are no `EventName`, `EventCode`, unit masks, descriptions, metrics, functions, or classes in this file. Its public contract is PMU unit capacity metadata.

## Control Flow, State, and Persistence
The file has no control flow. Build-time perf tooling parses it with the rest of the Haswell model directory and incorporates counter-count metadata into generated tables or lookup structures used by perf. Runtime perf uses PMU driver capabilities and event metadata for scheduling; this file provides model-specific counter inventory context.

Static state is the declared counter capacity by unit. The generated perf artifacts persist this metadata. Runtime counter allocation remains dynamic and depends on active events, grouping, pinned/exclusive requests, kernel constraints, and PMU driver behavior.

## Dependencies and Integration Points
Dependencies include perf's PMU event JSON support for counter metadata, Haswell unit naming, and `jevents.py` or related generation code that recognizes counter inventory rows. It integrates with Haswell event files that reference `core`, CBOX-like, and ARB units, and with perf scheduling diagnostics where available counter counts affect whether event groups can be placed together.

The file is especially relevant for uncore or box PMUs whose counter counts differ from core PMU defaults. Incorrect counts can lead to misleading scheduling expectations even if event encodings are correct.

## Risks and Test Signals
Risks include mixed numeric/string count representation, stale unit names, and mismatches between declared counts and kernel PMU driver capabilities. Because `cbox_0` differs from `CBOX`, tooling must not normalize unit names in a way that collapses distinct rows accidentally. This file also has no descriptions, so the meaning of each unit depends on external Haswell PMU knowledge.

Test signals include JSON validation, successful event-table generation, generated metadata inspection for counter counts, and perf grouping tests that attempt to schedule more events than available counters on core, CBOX, and ARB units. A parser regression test should cover both string and numeric counter-count values.
