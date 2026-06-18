# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/arrowlake/uncore-interconnect.json

## Purpose

This file defines five Arrow Lake uncore interconnect events for the HAC ARB PMU. The events count coherent data-read request tracking and CMI transaction totals, reads, and writes.

## Important APIs, Types, And Data

Each entry uses `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`. `Unit` is `HAC_ARB`, mapping to an uncore PMU table. Event names include `UNC_HAC_ARB_REQ_TRK_REQUEST.DRD`, `UNC_HAC_ARB_TRANSACTIONS.ALL`, `.READS`, `.WRITES`, and `UNC_HAC_ARB_TRK_REQUESTS.ALL`.

## Control Flow

During generation, `jevents.py` canonicalizes the event and umask fields into perf config strings and emits aliases under the generated Arrow Lake uncore PMU event table. Runtime control then moves through perf alias lookup, PMU wildcard matching, and hardware counter programming for matching HAC ARB devices.

## State And Persistence Behavior

The JSON is a persistent event-definition table. Per-package counter readings and accumulation happen in perf and the kernel PMU driver. The file has no local state transitions and no persistence beyond generated C tables.

## Dependencies And Integration Points

The file depends on Arrow Lake model selection in `arch/x86/mapfile.csv`, `jevents.py` schema conversion, generated PMU event tables, perf uncore alias matching, and kernel uncore PMU naming. It integrates with `perf list` and `perf stat` workflows that inspect socket/package interconnect traffic.

## Risks And Edge Cases

Read/write/all masks must remain mutually meaningful; otherwise users can derive impossible traffic ratios. PMU unit spelling is the primary discoverability risk. Since these are uncore package events, tests must account for systems with multiple packages or absent HAC ARB PMUs.

## Test Signals

Run JSON validation and PMU event generation. Check generated aliases for `unc_hac_arb_transactions.all`, `.reads`, `.writes`, and request-tracker aliases. On hardware or a PMU fixture, `perf list` should place them under the uncore HAC ARB PMU and not under core PMUs.
