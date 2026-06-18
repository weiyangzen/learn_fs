# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/snowridgex/pipeline.json

## Purpose

`pipeline.json` is the Snow Ridge X86 perf PMU event catalog for pipeline, retirement, branch, topdown, clock, load-block, machine-clear, and uop events. It supplies the symbolic event aliases used by Linux `perf` for high-level pipeline analysis on the `snowridgex` CPU model.

This is static metadata rather than executable code. The important behavior is how perf's PMU event parser maps these event descriptions into user-visible aliases and raw PMU encodings.

## Important APIs, Types, and Data Shape

The top-level JSON array contains 60 event objects. Key schema fields include:

- `EventName`: the user-facing perf alias, for example `BR_INST_RETIRED.ALL_BRANCHES`, `CPU_CLK_UNHALTED.CORE`, or `TOPDOWN_FE_BOUND.ITLB`.
- `EventCode` and `UMask`: programmable counter encodings for most non-fixed events.
- `Counter`: either general counters `0,1,2,3` or fixed counter labels for fixed events.
- `PEBS`: marks precise-event support; 26 entries include `PEBS: "1"`.
- `Deprecated`: marks compatibility aliases, present on three entries.
- `BriefDescription`, `PublicDescription`, and `SampleAfterValue`: user-facing descriptions and default sampling periods.

Fixed-counter aliases include `CPU_CLK_UNHALTED.CORE`, `CPU_CLK_UNHALTED.REF_TSC`, and `INST_RETIRED.ANY`. Programmable alternatives include `CPU_CLK_UNHALTED.CORE_P`, `CPU_CLK_UNHALTED.REF`, `CPU_CLK_UNHALTED.REF_TSC_P`, and `INST_RETIRED.ANY_P`.

## Event Coverage

The file covers these major groups:

- Branch retirement and misprediction: `BR_INST_RETIRED.*`, `BR_MISP_RETIRED.*`, and `BTCLEAR.ANY`.
- Clock and instruction retirement: `CPU_CLK_UNHALTED.*` and `INST_RETIRED.*`.
- Divider and load-block behavior: `CYCLES_DIV_BUSY.*` and `LD_BLOCKS.*`.
- Machine clears: `MACHINE_CLEARS.ANY`, `DISAMBIGUATION`, `PAGE_FAULT`, and `SMC`.
- Topdown slots: `TOPDOWN_BAD_SPECULATION.*`, `TOPDOWN_BE_BOUND.*`, `TOPDOWN_FE_BOUND.*`, and `TOPDOWN_RETIRING.ALL`.
- Uop issue/retirement: `UOPS_ISSUED.ANY` and `UOPS_RETIRED.*`.

Deprecated entries are `CYCLES_DIV_BUSY.ANY`, `TOPDOWN_BAD_SPECULATION.MONUKE`, and `TOPDOWN_BE_BOUND.STORE_BUFFER`.

## Control Flow and Integration

There is no direct control flow. The integration path is:

1. Perf discovers the file in the Snow Ridge event directory.
2. The PMU event parser or generator loads each object into the model-specific event table.
3. `perf list` displays aliases and descriptions.
4. `perf stat`, `perf record`, and related commands resolve aliases to fixed counters or programmable event selectors.
5. Topdown analysis tooling can consume the `TOPDOWN_*` events to classify issue slots into retiring, bad speculation, frontend-bound, and backend-bound categories.

Events sharing `EventCode` are differentiated by `UMask` and sometimes by fixed-counter designation. For example, many branch-retired events use `0xc4`, branch-mispredict events use `0xc5`, and topdown categories use `0x71`, `0x73`, or `0x74`.

## State and Persistence Behavior

The file stores static PMU metadata. It has no runtime state, locks, or persistence of its own. Once included in perf, its event names and encodings become persistent user-facing interfaces. The fixed-counter aliases are especially sensitive because users may choose them to avoid consuming programmable counters.

## Dependencies and Coupling

Dependencies include:

- Linux perf's PMU event JSON schema and table generator/parser.
- Snow Ridge CPU support for fixed counters 0, 1, and 2 and programmable counters `0,1,2,3`.
- PEBS handling for precise-capable retired-branch, retired-instruction, load-block, topdown-retiring, and uop-retired events.
- Topdown metric consumers that interpret slot-counting events.

The file is related to `memory.json` through machine-clear coverage: `pipeline.json` contains broad machine-clear and disambiguation/page-fault/SMC events, while `memory.json` adds `MACHINE_CLEARS.MEMORY_ORDERING`.

## Risks

- Fixed-counter entries do not include `EventCode`, relying on `Counter` and `EventName` conventions. Validators must not require `EventCode` on fixed events.
- Several programmable and fixed aliases describe similar clock or instruction counts. Incorrect alias selection can consume a different counter class.
- `PEBS` metadata is widespread and user-visible; losing it would degrade precise sampling workflows.
- Topdown events count issue slots, not raw cycles or instructions. Consumers must not compare them directly to non-slot events without the proper topdown model.
- Deprecated aliases should remain resolvable for compatibility but should not be used as preferred names.
- `SampleAfterValue` varies by category; changing it can alter default sampling behavior.

## Test Signals

Useful validation signals include:

- `jq` parse and length checks; this file contains 60 event objects.
- Perf table generation for `snowridgex`.
- `perf list` checks for representative fixed, programmable, PEBS, topdown, and deprecated names: `CPU_CLK_UNHALTED.CORE`, `CPU_CLK_UNHALTED.CORE_P`, `INST_RETIRED.ANY`, `BR_MISP_RETIRED.ALL_BRANCHES`, `TOPDOWN_FE_BOUND.ITLB`, and `TOPDOWN_BAD_SPECULATION.MONUKE`.
- Checks that 26 entries retain `PEBS: "1"`.
- Checks that fixed counter entries are accepted without `EventCode`.
- Tests that topdown event umasks remain distinct and are not collapsed by shared `EventCode`.
