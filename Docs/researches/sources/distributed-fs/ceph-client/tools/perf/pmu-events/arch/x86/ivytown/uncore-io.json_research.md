# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/ivytown/uncore-io.json

## Purpose
This JSON file defines Ivy Town uncore I/O PMU events for perf's generated event tables. It covers the R2PCIe uncore block, exposing clockticks, IIO credit acquisition/rejection/usage, ring utilization on AD/AK/BL/IV rings, receive-ring occupancy and inserts, and transmit-ring full/not-empty/NACK conditions. The data lets `perf list` and `perf stat -e` present symbolic names such as `UNC_R2_RING_AD_USED.CW_VR0_EVEN` instead of requiring users to hand-code event select and unit-mask values.

## Important APIs, Types, And Functions
The file is declarative and has no functions or exported types. The important schema fields are `EventName`, `EventCode`, `UMask`, `BriefDescription`, `PublicDescription`, `Counter`, `PerPkg`, and `Unit`. All 61 entries use `Unit: R2PCIe` and `PerPkg: 1`, with most events available on counters `0,1,2,3`; credit events are limited to `0,1`, and `UNC_R2_RxR_OCCUPANCY.DRS` is restricted to counter `0`. The event families are `UNC_R2_IIO_CREDITS_*`, `UNC_R2_RING_*_USED`, `UNC_R2_RxR_*`, `UNC_R2_TxR_*`, and `UNC_R2_CLOCKTICKS`.

## Control Flow
There is no runtime control flow in the file. At build or runtime, perf's PMU event tooling parses the JSON array, validates known keys, and emits or loads event aliases for the Ivy Town model. User selection of an alias resolves to the relevant uncore PMU unit, event code, unit mask, and counter constraints. The repeated ring entries encode the matrix of ring type, direction, virtual ring, and odd/even polarity as separate aliases rather than computing them dynamically.

## State And Persistence
The file persists static hardware metadata only. No counters are allocated or mutated by this JSON until perf opens a corresponding hardware event through the kernel PMU interface. The `PerPkg` values indicate package-scoped uncore measurement semantics, while `Counter` constrains which programmable counters can host each event. Counter values observed at runtime live in kernel perf events, not in this repository data.

## Dependencies And Integration Points
The file integrates with Linux perf's `pmu-events` JSON parser and architecture map for `arch/x86/ivytown`. It depends on perf's accepted event-field vocabulary and on kernel uncore PMU support for the R2PCIe unit. It complements other Ivy Town uncore files for memory and power and is consumed together with CPU model matching metadata when perf chooses the correct event table.

## Risks And Edge Cases
Because this is hardware metadata, small encoding errors can silently produce misleading performance data. Risk areas include incorrect `UMask` combinations for clockwise/counterclockwise and virtual-ring polarity filters, wrong counter restrictions for credit and occupancy events, duplicate names, missing `EventCode`, and stale descriptions copied from vendor documentation. Ring aliases that aggregate masks, such as `.CW`, `.CCW`, or `.ANY`, need consistency with the more specific odd/even aliases.

## Test Signals
Useful validation includes `jq empty` for syntax, schema checks against perf's `jevents` parser, `perf list` on Ivy Town class systems or forced table generation, and spot checks that aliases resolve to the expected `event`, `umask`, unit, and counter masks. Runtime signals include sane nonzero clockticks, ring activity under PCIe traffic, IIO credit rejection rising under contention, and no parser warnings during `tools/perf` builds.
