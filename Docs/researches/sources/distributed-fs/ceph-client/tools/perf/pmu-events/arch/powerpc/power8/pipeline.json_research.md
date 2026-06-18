# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power8/pipeline.json

## Purpose
`pipeline.json` defines 58 POWER8 raw PMU events focused on pipeline progress, stalls, dispatch, completion, run cycles, flushes, transactional run cycles, synchronization, frequency slewing, and load/store completion. It supplies core aliases used directly by users and heavily by CPI and throughput metrics.

Representative events include `PM_CYC`, `PM_RUN_CYC`, `PM_RUN_INST_CMPL`, `PM_CMPLU_STALL`, `PM_CMPLU_STALL_LSU`, `PM_CMPLU_STALL_DCACHE_MISS`, `PM_1PLUS_PPC_CMPL`, `PM_1PLUS_PPC_DISP`, `PM_FLUSH`, `PM_DISP_HELD`, `PM_LD_CMPL`, and SMT mode run-cycle counters.

## Important schema and data surface
- Schema: array of objects with `EventCode`, `EventName`, `BriefDescription`, and `PublicDescription`.
- Count: 58 raw event rows.
- Main families: 19 completion-stall events, 6 LSU events, 5 run-cycle events, 3 store events, 2 transactional-memory events, 2 load-linked/store-conditional related events, dispatch-held events, flush events, power-management frequency events, hypervisor cycles, interrupts, and tablewalk cycles.
- Event codes are POWER8 PMU hex encodings such as `0x100f2`, `0x4000a`, `0x600f4`, and `0x500fa`.

## Control flow and integration
Build-time flow mirrors other PMU event files: `jevents.py` scans the file, emits generated PMU event records, and links them into perf for POWER8 CPU mappings from `arch/powerpc/mapfile.csv`.

Runtime integration is central for derived metrics. `metrics.json` uses these pipeline events as denominators and accounting buckets for IPC, CPI, run-cycle percentages, completion stalls, GCT and dispatch analyses, SMT mode percentages, sync stalls, LSU stalls, dcache-miss stall attribution, and transactional memory cycle accounting.

## State and persistence behavior
The file has no runtime mutation. It persists canonical symbolic names and event encodings for pipeline counters. Because many metrics divide by `PM_RUN_INST_CMPL`, `PM_CYC`, or `PM_RUN_CYC`, changing these event definitions has broad generated-metric impact.

## Dependencies
- Depends on perf's PMU event generator and the POWER8 PMU driver.
- Feeds `metrics.json` for high-level formulas such as `cpi`, `ipc`, `run_cpi`, `stall_cpi`, `thread_block_stall_cpi`, `lsu_stall_*_cpi`, and SMT cycle percentages.
- Complements `other.json`, which contains additional GCT, dispatch, branch, and stall subcauses used to build richer pipeline breakdowns.

## Risks and edge cases
- Pipeline counters are common denominators. Bad event codes or renamed aliases here can invalidate many unrelated-looking metrics.
- Some `PublicDescription` values intentionally clarify or correct short descriptions; losing them would reduce `perf list --details` quality.
- Several stall categories overlap or are used in subtractive "other" metrics. In multiplexed runs or short sampling windows, derived values can look inconsistent even when raw event definitions are correct.
- Events such as frequency up/down and SMT mode cycles are sensitive to platform state and may be absent or low-count depending on firmware and workload.

## Test signals
- JSON/schema validation for 58 rows.
- Full-directory uniqueness validation for all `EventName` values.
- Cross-file metric dependency validation, emphasizing that `PM_CYC`, `PM_RUN_CYC`, `PM_RUN_INST_CMPL`, `PM_CMPLU_STALL*`, `PM_1PLUS_PPC_*`, and `PM_FLUSH` resolve.
- Generator/build validation through `jevents.py` or a perf build.
- Runtime smoke tests: `perf stat -e pm_cyc,pm_run_cyc,pm_run_inst_cmpl,pm_cmplu_stall sleep 1`; metric smoke tests for `cpi`, `ipc`, `run_cpi`, and representative `cpi_breakdown` metrics.
