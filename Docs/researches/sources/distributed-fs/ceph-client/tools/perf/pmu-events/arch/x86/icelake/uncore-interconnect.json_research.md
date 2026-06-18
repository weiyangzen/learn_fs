# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/icelake/uncore-interconnect.json

## Purpose

This file defines two Ice Lake client uncore interconnect events for the ARB PMU. They count coherent tracker requests and tracker requests at package scope, giving perf aliases for basic uncore fabric/request-tracking activity.

## Important APIs, Types, And Data

Each record uses `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`. `UNC_ARB_COH_TRK_REQUESTS.ALL` uses event `0x84`, umask `0x1`, counter `1`; `UNC_ARB_TRK_REQUESTS.ALL` uses event `0x81`, umask `0x1`, counter `1`. `Unit` is `ARB`, which `jevents.py` maps to an uncore PMU table name, and `PerPkg` is `1`, marking package-scoped events.

## Control Flow

Build-time generation follows the same event path as core records, with the additional unit-to-PMU mapping for `ARB`. The generated aliases are emitted under an uncore PMU table rather than the default core table. At runtime, perf resolves the aliases against kernel-exposed uncore ARB PMU devices and programs the package-level counter.

## State And Persistence Behavior

The file persists static uncore alias metadata. Counter state is maintained by uncore hardware and read by perf during a command. Package aggregation and multi-socket behavior are runtime perf/kernel concerns; the JSON only declares `PerPkg` scope.

## Dependencies And Integration Points

Dependencies include the Ice Lake x86 mapfile row, `jevents.py` unit conversion, generated `pmu-events.c`, perf uncore PMU discovery, and kernel support for an ARB uncore PMU. These events integrate with uncore interconnect analysis and can support higher-level system or memory-traffic investigations, even though `icl-metrics.json` focuses more on core/offcore-derived metrics.

## Risks And Edge Cases

The main risk is PMU naming and scope. If `Unit` does not match perf's uncore naming convention for Ice Lake ARB devices, aliases can disappear from `perf list` or bind incorrectly. `PerPkg` mistakes can produce confusing aggregation on multi-package systems. Both events use counter `1`; tests should catch whether this is a hardware restriction and whether scheduling two aliases concurrently is possible.

## Test Signals

Validate the JSON, run x86 `jevents.py` generation, and inspect generated aliases for `unc_arb_coh_trk_requests.all` and `unc_arb_trk_requests.all` under the ARB uncore PMU. On hardware or a fixture, `perf list` should show package-scoped uncore aliases, and concurrent scheduling should respect the shared counter constraint.
