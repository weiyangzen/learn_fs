# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellde/uncore-memory.json

## Purpose

`uncore-memory.json` is the Broadwell-DE integrated memory-controller PMU event table for perf. It defines symbolic aliases for DRAM command counts, controller modes, queue occupancy, refresh/ECC/power behavior, priority classes, VMSE write behavior, and per-rank/per-bank read and write CAS counters. These aliases allow tools and users to measure memory-controller behavior through names such as `UNC_M_CAS_COUNT.RD`, `UNC_M_MAJOR_MODES.WRITE`, and `UNC_M_RD_CAS_RANK0.BANK0`.

The file contains 322 event records, all with `Unit: "iMC"` and `PerPkg: "1"`. It is the largest of this subset because it expands rank/bank matrices into individual aliases: read CAS counters for ranks 0, 1, 2, 4, 5, 6, and 7, and write CAS counters for ranks 0, 1, 4, 5, 6, and 7. The data is package-scoped uncore metadata, not executable logic.

## Important APIs, Types, and Data Shape

The records use perf's PMU event JSON schema: `EventName`, `EventCode`, optional `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and usually `PublicDescription`. `jevents.py` consumes these fields at build time and emits C event-table rows in generated `pmu-events.c`; `util/pmu.c`, `builtin-list.c`, metric code, and Python PMU export consume the generated tables.

Important event families include:

- `UNC_M_ACT_COUNT.*`, `UNC_M_PRE_COUNT.*`, `UNC_M_DRAM_PRE_ALL`, and `UNC_M_DRAM_REFRESH.*` for DRAM row activate, precharge, and refresh activity.
- `UNC_M_CAS_COUNT.*` for aggregate read/write CAS counts, including RMM/WMM split and underfill reads.
- `UNC_M_RD_CAS_RANK*.*` and `UNC_M_WR_CAS_RANK*.*` for rank/bank-specific read and write CAS attribution.
- `UNC_M_MAJOR_MODES.*`, `UNC_M_WMM_TO_RMM.*`, and `UNC_M_WRONG_MM` for memory-controller scheduling mode behavior.
- `UNC_M_RPQ_*`, `UNC_M_WPQ_*`, `UNC_M_WPQ_READ_HIT`, and `UNC_M_WPQ_WRITE_HIT` for read/write pending queue behavior.
- `UNC_M_POWER_*` for channel, rank, self-refresh, PCU throttling, critical throttling, and CKE/power-throttle cycles.
- `UNC_M_ECC_CORRECTABLE_ERRORS` for corrected ECC events.
- `UNC_M_VMSE_*` for VMSE write occupancy and push behavior.

The schema count shows one event without `EventCode` (`UNC_M_DCLOCKTICKS`) and 29 events without `UMask`, mostly clock or unfiltered single-selector events. The remaining records use masks to distinguish mode, rank, bank, priority, and command-type subevents.

## Control Flow

The JSON has no branches or functions, but it participates in perf's deterministic PMU-event generation flow:

1. `pmu-events/arch/x86/mapfile.csv` maps Broadwell-DE model 6-56 to the `broadwellde` directory.
2. `pmu-events/Build` feeds the architecture directory to `jevents.py`.
3. `jevents.py` parses this file, converts each memory-controller alias into generated C data, and preserves event encodings, counter constraints, descriptions, unit, and package scope.
4. Runtime PMU discovery matches generated `Unit: "iMC"` aliases against kernel iMC uncore PMUs.
5. `perf list`, `perf stat`, metrics, and user event parsing resolve symbolic names into raw uncore iMC events.

The rank/bank sections are effectively a generated-looking cross product encoded as literal JSON. That makes ordering important: list output and review diffs depend on stable grouping by rank and bank.

## State and Persistence Behavior

The file persists only static event metadata. Generated build artifacts persist a compiled representation until the next perf rebuild. Runtime state exists in perf's alias tables and in hardware iMC counters opened for a measurement interval. Because all records are package-scoped uncore events, measurements are shared by workloads on the package and cannot be attributed directly to a single process without additional experimental control.

There is no writeback path. Any change to event names can break user scripts, dashboards, or metric expressions that name these aliases. Any change to encodings changes hardware programming and therefore the meaning of collected data.

## Dependencies and Integration Points

This file depends on perf's x86 PMU-event generation, the Broadwell-DE CPU map, the Intel uncore iMC kernel PMU driver, and user-space PMU alias support. It integrates with `perf list --unit iMC`, `perf stat -e` on iMC aliases, JSON event listing, generated metric parsing where metrics refer to memory aliases, and perf tests that compare generated event tables with expected PMU-event rows.

It also has conceptual dependencies on memory-controller behavior: open-page versus closed-page policy, read major mode, write major mode, partial/underfill handling, rank CKE states, throttling, and ECC support. Some events are useful only on systems with matching DRAM configuration, ECC enabled, or ranks/banks that physically exist.

## Risks and Edge Cases

The large rank/bank matrix is vulnerable to copy/paste errors in event names, masks, and descriptions. `UNC_M_RD_CAS_RANK2.BANK0` is the only rank-2 read entry in this file, while rank 3 is absent and ranks 4-7 are populated; that asymmetry may reflect the Broadwell-DE source table but should be treated as a high-value regression check. Write CAS entries omit ranks 2 and 3 entirely. If those omissions are accidental, users lose aliases; if they are intentional, tests should not auto-generate nonexistent aliases.

`UNC_M_DCLOCKTICKS` lacks an `EventCode`, and many power or single-selector events lack `UMask`; generator validation must allow these forms when the upstream schema permits them. Some descriptions include known spelling/wording issues from source material. Correcting text is low risk, but changing encoded fields is high risk because the generator does not know the hardware truth.

Interpretation risks are also significant: CAS counts are per channel/controller, power states may count cycles when all ranks are in a state, and rank filters can count only configured ranks. Users can easily derive misleading bandwidth or page-hit metrics if they ignore clock domains, channel count, package scope, or unavailable rank/bank topology.

## Test Signals

Validation should include JSON parsing, duplicate-name checks, required-field checks, generator rebuild, and perf PMU-event unit tests. Event-family tests should verify that aggregate CAS, major-mode, queue, power, and rank/bank aliases appear in `perf list --unit iMC`. Hardware smoke tests on Broadwell-DE should include `UNC_M_DCLOCKTICKS`, `UNC_M_CAS_COUNT.RD`, `UNC_M_CAS_COUNT.WR`, one rank/bank read CAS event, one write CAS event, and one power/throttle event. Review tests should flag unexpected changes to the rank/bank inventory, especially absent or newly added rank-2/rank-3 aliases.
