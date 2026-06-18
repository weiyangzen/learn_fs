# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/pipeline.json

## Purpose

`pipeline.json` is the Panther Lake perf PMU event catalog for core pipeline, branch, retirement, topdown, execution, divider, stall, and uop-flow analysis. It contains 243 event rows: 155 for `cpu_core` and 88 for `cpu_atom`, reflecting Panther Lake's hybrid core/atom PMU split. The file is not executable code, but it is a direct input to perf's `pmu-events` generator and therefore becomes user-visible `perf list`, `perf stat`, and `perf record` event metadata.

## Important APIs, Types, and Data Fields

The file is a JSON array of event objects. The core schema fields are `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `SampleAfterValue`, `BriefDescription`, and often `PublicDescription`. Qualifier fields include `CounterMask`, `EdgeDetect`, `Invert`, `MSRIndex`, `MSRValue`, and `Deprecated`. `Unit` is critical because the same logical event name can appear twice with different encodings for `cpu_core` and `cpu_atom`, such as `ARITH.DIV_ACTIVE`, branch-retired rows, and TLB-adjacent pipeline rows.

Major event families are `ARITH`, `ASSISTS`, `BE_STALLS`, `BR_INST_RETIRED`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `CYCLE_ACTIVITY`, `EXE_ACTIVITY`, `INST_RETIRED`, `INT_MISC`, `INT_UOPS_EXECUTED`, `INT_VEC_RETIRED`, `LD_BLOCKS`, `LSD`, `MACHINE_CLEARS`, `MEMORY_STALLS`, `RS`, `SERIALIZATION`, `TOPDOWN*`, `UOPS_DECODED`, `UOPS_DISPATCHED`, `UOPS_EXECUTED`, `UOPS_ISSUED`, and `UOPS_RETIRED`. Four events use MSR selectors: `INT_MISC.BPCLEAR_CYCLES`, `INT_MISC.UNKNOWN_BRANCH_CYCLES`, `UOPS_RETIRED.MS`, and `UOPS_RETIRED.MS_SWITCHES`. Twenty-three branch cost or older near-branch aliases are marked `Deprecated`.

## Control Flow and Data Flow

There is no local runtime control flow. Build-time flow is handled by `tools/perf/pmu-events/jevents.py`: each JSON row becomes a generated PMU table entry, `EventName` is lowercased for alias matching, `Unit` is converted to the target PMU name, event and umask fields become config encodings, and optional MSR/filter fields are preserved in the generated C string. Runtime flow starts when a user requests an alias; perf resolves it against the generated Panther Lake table, chooses the correct PMU instance for `cpu_core` or `cpu_atom`, and programs the counter and any MSR selector.

The analysis flow is layered. Branch families count retired and mispredicted branch types. `CPU_CLK_UNHALTED`, `TOPDOWN`, and `TOPDOWN_*` rows feed top-down pipeline slots and bound categories. Uop families observe decode, dispatch, issue, execution, retirement, and microcode-sequencer behavior. `ARITH` and divider events expose long-latency arithmetic pressure. `LD_BLOCKS`, `MEMORY_STALLS`, `RS`, and `CYCLE_ACTIVITY` describe backend and memory-related stalls.

## State and Persistence Behavior

The only persistent state is static metadata in the repository. Runtime counter state lives in hardware PMU counters for the selected measurement interval and is not stored here. `SampleAfterValue` supplies default sampling periods but does not impose persistence semantics. Deprecated rows still persist as aliases, so compatibility is maintained while downstream tools should avoid treating them as preferred metric inputs. `CounterMask`, `EdgeDetect`, `Invert`, `MSRIndex`, and `MSRValue` are semantic state in the generated table; losing them changes what hardware condition is counted.

## Dependencies and Integration Points

This catalog depends on Panther Lake PMU encodings and Linux perf's `jevents.py` generator. It integrates with `perf list` for discoverability, `perf stat` for aggregate measurement, `perf record` for sampling, top-down analysis in `builtin-stat.c` and `util/metricgroup.c`, and any generated Intel metric expressions that refer to these event names. The file sits beside Panther Lake cache, memory, virtual-memory, and uncore catalogs, and its `cpu_core`/`cpu_atom` split must align with kernel hybrid PMU naming.

## Risks and Edge Cases

Hybrid duplication is the main risk: the same `EventName` can require different `EventCode`, `UMask`, counters, and descriptions depending on `Unit`. Tests must not deduplicate by name alone. Deprecated branch aliases may remain visible but should not be used for new metrics without checking replacements. Topdown events have special interpretation as pipeline-slot categories rather than simple event counts. MSR-qualified events can conflict with other events using the same programmable MSRs. Counter restrictions differ between core and atom rows, so oversubscribed event groups may fail or multiplex differently. Similar branch names such as `COND_TAKEN`, `COND_TAKEN_BWD`, cost, and TPEBS variants are easy to confuse.

## Test Signals

Useful validation includes JSON parse success, `jevents.py` generation success, and `perf list` exposure under both Panther Lake core PMUs. Runtime smoke tests should check that branch-heavy workloads move `BR_INST_RETIRED` and `BR_MISP_RETIRED`, divide-heavy code moves `ARITH.*`, microcode-heavy or assisted operations move `ASSISTS`/`UOPS_RETIRED.MS`, and frontend/backend pressure changes topdown categories. Hybrid systems should verify core-only and atom-only workload placement produces counts on the expected `cpu_core` or `cpu_atom` aliases. Regression tests should preserve the 23 `Deprecated` markers and the four MSR-qualified rows.
