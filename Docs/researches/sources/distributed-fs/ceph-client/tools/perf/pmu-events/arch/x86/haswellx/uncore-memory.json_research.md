# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-memory.json

## Purpose

`haswellx/uncore-memory.json` defines 325 Intel Haswell Xeon integrated memory controller (`iMC`) uncore PMU event aliases for perf. It covers DRAM command counts, major controller modes, priority and preemption behavior, power and CKE state cycles, rank-level CAS events, write/read mode transitions, refresh and ECC events, and two scaled aliases for memory read/write volume. It is the largest file in this work item and provides the primary HaswellX memory-channel event catalog.

## Important APIs, types, and schema

Entries use the perf JSON event schema with `EventName`, `EventCode` on most records, optional `UMask`, `BriefDescription`, optional `PublicDescription`, `Counter`, `PerPkg`, `Unit`, and occasional `ScaleUnit`. All records use `Unit: iMC`; `jevents.py` maps that by default to `uncore_imc`. All records are package scoped and allow counters `0,1,2,3`.

Important families include `LLC_MISSES.MEM_READ` and `LLC_MISSES.MEM_WRITE`, which are derived from `UNC_M_CAS_COUNT` masks and carry `ScaleUnit: 64Bytes`; `UNC_M_ACT_COUNT.*`, `UNC_M_PRE_COUNT.*`, `UNC_M_CAS_COUNT.*`, and `UNC_M_DRAM_REFRESH.*` for DRAM command accounting; `UNC_M_MAJOR_MODES.*`, `UNC_M_PREEMPTION.*`, `UNC_M_WMM_TO_RMM.*`, and `UNC_M_RD_CAS_PRIO.*` for controller scheduling modes; `UNC_M_POWER_CKE_CYCLES.*`, `UNC_M_POWER_THROTTLE_CYCLES.*`, and `UNC_M_POWER_CHANNEL_DLLOFF` for channel power behavior; `UNC_M_ECC_CORRECTABLE_ERRORS`; and large rank matrices such as `UNC_M_RD_CAS_RANK{0,1,4,5,6,7}.*` and `UNC_M_WR_CAS_RANK{0,1,4,5,6,7}.*`.

## Control flow and integration

The file is parsed during perf's PMU table generation after `arch/x86/mapfile.csv` selects the `haswellx` model for CPUID `GenuineIntel-6-3F`. `jevents.py` turns each JSON object into a generated table entry, preserving the alias name, event code, umask, description, scale unit, unit/PMU routing, and package flag. Runtime perf lookup then exposes these aliases under the generated HaswellX event table and routes them to the memory-controller PMU rather than the core PMU.

There is no internal control flow, but there are structural patterns that matter. The rank-level families repeat the same mask vocabulary across rank-specific event codes from `0xB0` through `0xBF`; the aggregate `UNC_M_CAS_COUNT` aliases use a shared event code `0x4` with different masks; and the memory bandwidth aliases depend on the same read/write CAS encodings plus `ScaleUnit`.

## State and persistence behavior

The file is immutable source data. Its durable contract is the hardware encoding of every memory-controller alias. The `ScaleUnit: 64Bytes` fields persist semantic unit conversion for bandwidth-like aliases; removing them would not necessarily break event parsing, but it would change how perf describes and scales those events. The rank naming and masks are also persistent external identifiers used in scripts and dashboards that call `perf stat -e`.

## Dependencies

Dependencies include Intel HaswellX iMC uncore event definitions, perf's JSON schema, `jevents.py`, the x86 mapfile, generated `pmu-events.c`, and availability of `uncore_imc` PMUs in the running kernel. The file also depends on architectural assumptions about channel/rank topology, read-major/write-major modes, underfills, page policy, CKE states, and DRAM command granularity.

## Risks

The repeated rank matrices are error-prone: a copied mask or event code for the wrong rank would silently attribute traffic to the wrong rank. `LLC_MISSES.MEM_READ` and `.MEM_WRITE` are named like cache events but are derived from iMC CAS counts; consumers may overinterpret them as LLC-only misses instead of memory-controller read/write commands. Some records intentionally lack `EventCode` or `UMask` for clock tick style events, so validators must distinguish missing optional fields from accidental omissions. Package scope and channel PMU routing are critical for interpreting counts on multi-socket systems.

## Test signals

Syntax validation with `python3 -m json.tool` is the first gate. Build-time test signals are successful `jevents.py` generation and perf PMU event tests. Runtime checks include `perf list` exposing `uncore_imc` HaswellX aliases, `perf stat` on memory bandwidth workloads showing read/write CAS changes, ECC counters remaining zero on healthy systems, and consistency checks where `UNC_M_CAS_COUNT.RD` roughly aligns with rank read CAS sums for populated ranks and known channel topology.
