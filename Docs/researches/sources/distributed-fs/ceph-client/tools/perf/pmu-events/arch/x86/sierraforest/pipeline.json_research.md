# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/sierraforest/pipeline.json

## Purpose

This 76-entry Sierra Forest pipeline table defines core PMU aliases for branch retirement and misprediction, clocks and instructions, load blocking, machine clears, miscellaneous retired operations, serialization, topdown slot categories, issued and retired uops, and arithmetic divider activity. It is the central event catalog for pipeline and topdown performance analysis on Sierra Forest.

## Important APIs, Types, and Data

Records use `EventName`, `EventCode`, `UMask`, `Counter`, `CounterMask`, `SampleAfterValue`, `BriefDescription`, optional `PublicDescription`, `Deprecated`, and `Errata`. Families include `BR_INST_RETIRED`, `BR_MISP_RETIRED`, `CPU_CLK_UNHALTED`, `INST_RETIRED`, `LD_BLOCKS`, `MACHINE_CLEARS`, `MISC_RETIRED*`, `SERIALIZATION`, `TOPDOWN_BAD_SPECULATION`, `TOPDOWN_BE_BOUND`, `TOPDOWN_FE_BOUND`, `TOPDOWN_RETIRING`, `UOPS_ISSUED`, and `UOPS_RETIRED`. Fixed-counter aliases use `Fixed counter 0/1/2`; programmable variants use counters `0-7`. Deprecated aliases include older indirect-call/ITLB/machine-clear names, and several topdown aliases intentionally mirror `_P` variants.

## Control Flow

Perf maps requested aliases to fixed or generic counters. Topdown events count issue or retirement slots for high-level categories, while branch and machine-clear events count retired instructions or clears. Pipeline investigation usually starts with clocks, instructions, and level-1 topdown categories, then drills into branch mispredict, frontend, backend, serialization, uop, and machine-clear subevents. The file itself is static data; perf's alias resolution and counter scheduling provide runtime behavior.

## State and Persistence Behavior

The persistent state is the model-specific alias, encoding, counter, deprecation, errata, and sampling metadata. Runtime state is PMU counter state during a perf session. Fixed counters are limited resources with special semantics, while programmable aliases consume generic counters. Topdown slot events require compatible normalization and should not be mixed directly with raw instruction counts without the intended formulas.

## Dependencies and Integration Points

This file integrates with perf's core PMU support, Sierra Forest metric expressions, `metricgroups.json` topdown group labels, frontend/cache/memory event files for drilldown, LBR-related miscellaneous events, and generated documentation. It depends on the kernel exposing Sierra Forest fixed and generic counters and honoring deprecation/errata metadata in user-facing listings.

## Risks

Topdown event semantics are easy to misuse: slot counts, cycle counts, retired instruction counts, and branch counts have different denominators. Alias pairs such as `CPU_CLK_UNHALTED.CORE`/`.THREAD` and `TOPDOWN_*`/`*_P` must remain consistent without creating duplicate metric contributions. Deprecated aliases should remain for compatibility but not become preferred names. Errata-bearing events require caution in metric formulas and tests. Fixed-counter events can create scheduling conflicts if grouped with assumptions that all aliases use generic counters.

## Test Signals

Validation should include schema parsing, fixed versus generic counter handling, alias listing, deprecation/errata metadata checks, and generated encoding comparisons. Runtime smoke tests should cover branch-heavy code, misprediction patterns, divide-heavy code, serializing instructions, self-modifying-code or page-fault machine clears where feasible, and topdown level-1 breakdowns. Metric tests should verify topdown formulas sum and normalize as expected and that deprecated aliases do not appear in new preferred metric expressions.
