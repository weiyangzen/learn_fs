# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/graniterapids/uncore-interconnect.json

## Purpose
This JSON file defines 203 Intel Granite Rapids uncore interconnect PMU events for perf's `pmu-events` database. It covers mesh/interconnect and socket fabric units including B2CMI, B2HOT, B2UPI, IRP/`UNC_I`, MDF, UBOX, and UPI. The data is declarative input to perf's event-table generation path, not executable code. The source was read as a complete 1,979-line JSON array.

## Important APIs, Types, and Functions
The schema is the perf x86 PMU event JSON schema. Every row has `EventName`, `EventCode`, `BriefDescription`, `Counter`, `PerPkg`, and `Unit`; 192 rows also carry `UMask`, 11 rows include `PublicDescription`, and many rows mark `Experimental: "1"`. There are 203 unique event names and 35 unique event codes, with encodings differentiated primarily by unit masks and uncore units. Unit coverage is `B2CMI` 79 events, `UPI` 67, `MDF` 37, `IRP` 13, `UBOX` 5, and one clock event each for `B2HOT` and `B2UPI`.

Important event families include `UNC_B2CMI_DIRECTORY_*`, `UNC_B2CMI_IMC_READS/WRITES`, `UNC_B2CMI_TAG_*`, `UNC_I_*`, `UNC_MDF_RxR/TxR_*`, `UNC_UPI_RxL/TxL_*`, and `UNC_U_EVENT_MSG.*`. The `Counter` field limits events to uncore programmable counters, usually `0,1,2,3` or `0,1`; `PerPkg: "1"` tells perf these events are package scoped. There are no local functions, classes, or runtime APIs in the file; the effective API is the event-name and encoding contract consumed by perf.

## Control Flow, State, and Persistence
There is no in-file control flow. Build-time control flow comes from `tools/perf/pmu-events/jevents.py`, which walks model directories, parses each JSON object, validates and normalizes fields, and emits generated C event tables. At runtime, perf resolves aliases such as `UNC_UPI_RxL_FLITS.DATA` into raw uncore PMU selectors and passes the event attributes to the kernel perf PMU driver.

The only state in this file is static event metadata: event code, unit mask, counter constraints, package scope, unit selection, and descriptions. Persistence happens through generated `pmu-events.c` tables built into perf; runtime counter values are transient perf session data. Because these are uncore events, runtime state is package- or unit-wide rather than per-thread, so consumers must interpret counts against the topology and active socket/unit selection.

## Dependencies and Integration Points
The file depends on the perf PMU event JSON schema, Granite Rapids CPU model mapping, Intel uncore PMU event semantics, `jevents.py`, and kernel uncore PMU drivers exposing matching units. It integrates with `perf list` for discoverability and `perf stat -e` for measurement. The unit names are critical integration points because perf maps JSON `Unit` values to PMU names; a mismatch would make an otherwise valid event unreachable or misleading.

This file also integrates with other Granite Rapids event tables in the same model directory. Memory and I/O events can be correlated with B2CMI/UPI traffic, while power events can contextualize throttling or low-power link behavior. There are no metric expressions in this file, so derived ratios are expected to be defined elsewhere or by users.

## Risks and Test Signals
Risks include event encoding drift against Intel documentation, broad `Experimental` coverage, uncore unit-name mismatches, and incorrect interpretation of package-scoped counts as core-local values. Duplicate event codes are intentional but make `UMask` correctness essential. Some events represent occupancy or cycles rather than simple transaction counts, so downstream metrics must avoid mixing incompatible semantics.

Test signals include JSON syntax validation with `jq`, successful `jevents.py` generation, generated-table diffs, `perf list` visibility for representative `UNC_B2CMI`, `UNC_MDF`, `UNC_UPI`, and `UNC_U` names, and smoke tests on Granite Rapids hardware using package-scoped `perf stat` runs. Counter scheduling tests should verify `Counter` constraints and that multiple events from the same uncore unit can be grouped only when hardware counter availability permits.
