# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-memory.json

## Purpose

This file is the BroadwellX integrated memory controller PMU event catalog for Linux `perf`. It contains 326 event records, all routed to `Unit: "iMC"` and marked `PerPkg: "1"`. `jevents.py` maps `iMC` to generated PMU name `uncore_imc`, making these aliases available for BroadwellX memory-controller PMU instances.

The table describes DRAM command traffic, CAS reads and writes, activates, precharges, refreshes, ECC corrections, major-mode residency, queue occupancy/inserts, memory-controller power states, throttling, partial-write underfills, VMSE write push behavior, and detailed read/write CAS breakdowns by rank, bank, and bank group. The first two aliases, `LLC_MISSES.MEM_READ` and `LLC_MISSES.MEM_WRITE`, are derived convenience aliases over memory-controller CAS events with `ScaleUnit: "64Bytes"`.

## Schema And Public API

Each object is a perf alias record. The common fields are `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and `PublicDescription`. The file also uses `ScaleUnit` for the two LLC miss memory-traffic aliases and `Deprecated: "1"` for `UNC_M_DCLOCKTICKS`.

Important event families include DRAM activate/precharge/bypass/refresh commands, CAS counts, fixed and programmable memory-controller clock ticks, major modes, memory-controller power states, read/write queue pressure, read CAS priority, VMSE behavior, and large generated-like rank/bank families for `UNC_M_RD_CAS_RANK*.*` and `UNC_M_WR_CAS_RANK*.*`. The rank/bank sections expand CAS accounting across rank 0, 1, 4, 5, 6, and 7, plus a structurally unusual lone `UNC_M_RD_CAS_RANK2.BANK0` entry.

## Control Flow And Integration

The file is parsed at build time by `jevents.py`. Each JSON object is converted into a `JsonEvent`; `EventName` becomes the alias name, descriptions become short and long descriptions, `Unit: "iMC"` becomes `uncore_imc`, `ScaleUnit` becomes the generated unit string, `Deprecated` is preserved, and `EventCode`/`UMask` are canonicalized into perf event terms.

At runtime, perf selects the BroadwellX PMU table through the x86 CPU map, then attaches the generated `uncore_imc` aliases to matching uncore memory-controller PMUs. User-facing integration points include `perf list`, `perf stat`, JSON event listing, metric expressions that reference memory bandwidth aliases, and Python helpers that expose PMU metadata.

## State And Persistence

The file has no runtime state. Its persistent behavior is generated metadata compiled into perf. Changing an alias name is an API change for scripts and metrics; changing event encodings changes which hardware condition is measured; changing `ScaleUnit` alters bandwidth-style presentation for the derived memory-read/write aliases.

All records are package-level uncore events. Hardware counter values are ephemeral, but the generated alias table persists until perf is rebuilt. `Deprecated: "1"` on `UNC_M_DCLOCKTICKS` is a compatibility state signal: consumers should prefer `UNC_M_CLOCKTICKS_P` while old scripts may still resolve the deprecated alias.

## Dependencies, Risks, And Test Signals

The table depends on BroadwellX iMC PMU support in the kernel, the perf PMU-events generator, the BroadwellX x86 mapfile, and sysfs PMU format definitions for memory-controller event and mask fields. Hardware meaning depends on DRAM channel/rank/bank topology, read-major/write-major mode behavior, ECC support, power-management states, and BroadwellX-specific queue and VMSE mechanisms.

The main risks are silent semantic drift and large generated-family maintenance errors. The rank/bank sections repeat similar encodings hundreds of times; a single wrong `UMask`, rank number, or event name can produce a plausible but incorrect alias. Missing `EventCode` on `UNC_M_CLOCKTICKS_P` and deprecated `UNC_M_DCLOCKTICKS` is accepted by the current generator but should be guarded if schema validation tightens. Useful checks are `jq empty`, `jq 'length'` returning 326, no duplicate `EventName` values, generator output containing `uncore_imc`, and runtime tests for `LLC_MISSES.MEM_READ`, `UNC_M_CAS_COUNT.RD`, `UNC_M_ECC_CORRECTABLE_ERRORS`, and a rank-bank CAS alias.
