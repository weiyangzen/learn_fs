# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/other.json

## Purpose
`other.json` is the broad catch-all POWER8 raw PMU event table for perf. It defines 574 event aliases that do not fit cleanly into the smaller topic files. The events cover LPAR cycle modes, pump prediction, branch prediction internals, dispatch and flush causes, data and instruction reload sources, marked events, LSU queues, VSU/FPU/DFU execution, L2/L3 machines, transactional memory, interrupts, prefetch behavior, and assorted microarchitectural signals.

This file lets users and metrics refer to names like `PM_BR_MPRED_CCACHE`, `PM_DATA_ALL_FROM_L3`, `PM_GCT_NOSLOT_CYC`, or `PM_VSU1_VECTOR_SP_ISSUED` rather than raw event encodings.

## Important schema and data surface
- Schema: array of objects with `EventCode`, `EventName`, `BriefDescription`, and `PublicDescription`.
- Count: 574 raw event rows.
- Dominant event-name families include marked events (`PM_MRK_*`), instruction-source events (`PM_INST_*`), data-source events (`PM_DATA_*`), LSU events, VSU0/VSU1 events, branch events, L3 events, GCT events, dispatch/flush events, transactional-memory events, and pump prediction events.
- Event codes are hex strings, including simple encodings such as `0x5084` and wider encodings such as `0x61c050`.
- Many `PublicDescription` fields are empty, while some contain longer hardware notes about demand-only versus prefetch-included counting controlled by MMCR bits.

## Control flow and integration
Build-time flow:
1. `jevents.py` treats `other.json` as one PMU topic file because it has a `.json` extension inside the POWER8 model directory.
2. The generator lowercases event names for perf aliases and converts event codes into generated table entries such as `event=0x...`.
3. POWER8 PVR patterns in `arch/powerpc/mapfile.csv` select the whole `power8` directory, so these aliases are available together with the other topic files.
4. Higher-level metrics in `metrics.json` consume many of these event names, especially branch, GCT, data-source, marked-latency, and machine-usage signals.

At runtime, perf exposes these aliases through `perf list` and accepts them in event selectors such as `perf stat -e pm_br_bc_8_conv`. The kernel PMU driver owns actual counter scheduling and sampling.

## State and persistence behavior
`other.json` is static source metadata. It persists symbolic event definitions in the repository and contributes to generated perf tables at build time. It has no runtime state, but changing an `EventCode` changes what hardware signal an alias measures, and changing an `EventName` can break metrics and user scripts.

## Dependencies
- Depends on perf PMU-events JSON schema and `jevents.py`.
- Depends on POWER8 PMU hardware encodings and the powerpc PMU driver understanding the encoded event values.
- Integrates with `metrics.json`; several derived metrics use event families defined here, including branch-prediction and GCT signals.
- Integrates with sibling topic files by sharing one CPU directory selected by `arch/powerpc/mapfile.csv`.

## Risks and edge cases
- The file is a large catch-all table, so duplicate names, mistyped codes, or stale descriptions are easy to miss without automated checks.
- Some descriptions are truncated, typo-heavy, or conflict with `BriefDescription`; downstream help text quality depends on preserving or improving these strings.
- Empty `PublicDescription` fields are accepted but reduce discoverability in `perf list --details`.
- Several events describe mode-dependent semantics, such as prefetch inclusion controlled by MMCR bits. Users can misinterpret counts unless descriptions remain precise.
- Event aliases can be referenced by metrics in other files. Renames require full-directory dependency checks.

## Test signals
- JSON parse and schema validation for all 574 rows.
- Uniqueness checks for `EventName` within the full `power8` directory.
- Event-code format checks for hex strings.
- Build `tools/perf` or at least run the PMU-events generator path to ensure `jevents.py` accepts the file.
- Cross-file metric dependency check should include this file when resolving `MetricExpr` event names.
- Runtime smoke checks on POWER8 should verify a representative set from major families: branch prediction, data source, marked latency, GCT, LSU, VSU, transactional memory, and pump prediction.
