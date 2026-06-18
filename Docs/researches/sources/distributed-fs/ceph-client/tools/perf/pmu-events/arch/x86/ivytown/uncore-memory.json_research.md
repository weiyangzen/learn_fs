# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/uncore-memory.json

## Purpose
This JSON file defines Ivy Town integrated memory controller uncore PMU events for perf. Its 198 entries expose DRAM activate, precharge, CAS, refresh, ECC, major-mode, queue occupancy, throttling, rank/bank read CAS, rank/bank write CAS, and memory power-management counters. It provides symbolic iMC event aliases that help diagnose memory bandwidth, page policy, write-drain behavior, rank/bank distribution, refresh pressure, throttling, and ECC activity.

## Important APIs, Types, And Functions
The file is a static array of event descriptors, not executable code. Important fields are `EventName`, `EventCode`, `UMask`, `Counter`, `PerPkg`, `Unit`, `BriefDescription`, and `PublicDescription`. Every entry uses `Unit: iMC`, `PerPkg: 1`, and counters `0,1,2,3`. Major families include `UNC_M_ACT_COUNT`, `UNC_M_CAS_COUNT`, `UNC_M_PRE_COUNT`, `UNC_M_MAJOR_MODES`, `UNC_M_POWER_*`, `UNC_M_RD_CAS_RANK{0..7}.BANK{0..7}`, `UNC_M_WR_CAS_RANK{0..7}.BANK{0..7}`, `UNC_M_RPQ_*`, `UNC_M_WPQ_*`, `UNC_M_WMM_TO_RMM`, and `UNC_M_VMSE_*`.

## Control Flow
There is no control flow in the JSON itself. Perf parses the array into model-specific iMC aliases, and a selected alias becomes a hardware event programmed on the appropriate uncore memory-controller PMU. The rank/bank sections are intentionally expanded into one descriptor per rank and bank so users can select a specific physical dimension directly. Aggregate aliases such as CAS read/write totals use broader unit masks than the rank/bank entries.

## State And Persistence
The persisted state is the metadata mapping from human-readable event names to hardware encodings and descriptions. Runtime memory-controller counter state is created by perf and the kernel uncore driver when a user opens an event. The file records package-scoped semantics through `PerPkg` and allows any iMC generic counter through `Counter: 0,1,2,3`; it does not store current memory-controller mode, rank population, or platform topology.

## Dependencies And Integration Points
This file depends on perf's x86 `pmu-events` parser and Ivy Town CPU model matching. It integrates with the Linux uncore iMC PMU driver, with perf alias generation, and with higher-level perf metric expressions that may reference memory event names. It also overlaps conceptually with Ivy Town power metadata because some `UNC_M_POWER_*` events live on the iMC unit rather than the package PCU unit.

## Risks And Edge Cases
The file is large and regular, making copy/paste or generated-table mistakes plausible. Rank/bank aliases must maintain correct mask progression for all eight ranks and eight banks. Some descriptions contain vendor terminology and minor textual issues, so tests should focus on encoding correctness rather than prose alone. Hardware may not expose all ranks, banks, or modes on every platform, so zero counts are not necessarily parser failures. Incorrect aggregate masks for `.ALL`, `.RD`, or `.WR` could mislead bandwidth calculations.

## Test Signals
Validation signals include JSON syntax checks, successful `jevents` generation, no duplicate event-name diagnostics, and `perf list` showing iMC aliases under Ivy Town. Runtime smoke tests should compare `UNC_M_CAS_COUNT.RD` and `.WR` against known memory bandwidth workloads, verify rank/bank events concentrate on populated channels, observe refresh and power-state counters during idle, and check ECC events only on ECC-capable systems.
