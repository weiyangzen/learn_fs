# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/haswellx/uncore-io.json

## Purpose

`haswellx/uncore-io.json` defines 59 Intel Haswell Xeon R2PCIe uncore PMU event aliases for perf. The file is static source data used by the perf PMU event generator, not executable code. Its entries describe R2PCIe clock, IIO credit, ring utilization, ring bounce, receive/transmit queue, and S-box credit pressure events that allow `perf list` and event lookup to expose hardware encodings for Haswell-EP/Haswell-EX style server I/O uncore monitoring.

## Important APIs, types, and schema

The effective API is the perf PMU JSON schema consumed by `tools/perf/pmu-events/jevents.py`. Each object uses `EventName`, `EventCode`, optional `UMask`, `BriefDescription`, optional `PublicDescription`, `Counter`, `Unit`, and `PerPkg`. All records have `Unit: R2PCIe`, which `jevents.py` maps through `unit_to_pmu()` to the Linux PMU name `uncore_r2pcie`. `PerPkg: 1` marks package-scoped uncore events. `Counter` constrains which unit counters can program each event: 24 records allow `0,1,2,3`, 26 allow only `0,1`, and 9 allow only counter `0`.

The major event families are `UNC_R2_CLOCKTICKS`; IIO credit availability and acquisition events such as `UNC_R2_IIO_CREDIT.*`, `UNC_R2_IIO_CREDITS_ACQUIRED.*`, and `UNC_R2_IIO_CREDITS_USED.*`; ring activity families `UNC_R2_RING_AD_USED.*`, `UNC_R2_RING_AK_USED.*`, `UNC_R2_RING_BL_USED.*`, and `UNC_R2_RING_IV_USED.*`; queue occupancy and insert events for RxR and TxR; `UNC_R2_TxR_NACK_CW.*`; and S-box credit families `UNC_R2_SBO0_CREDITS_ACQUIRED.*`, `UNC_R2_SBO0_CREDIT_OCCUPANCY.*`, and `UNC_R2_STALL_NO_SBO_CREDIT.*`.

## Control flow and integration

There is no runtime control flow inside the JSON. Build and lookup flow is: `arch/x86/mapfile.csv` maps CPUID pattern `GenuineIntel-6-3F` to the `haswellx` model directory; the perf build invokes `jevents.py`; `JsonEvent` lowercases `EventName`, converts `Unit` into a PMU selector, combines `EventCode` and `UMask` into an event string, and emits generated PMU tables in `pmu-events.c`; perf runtime code uses those tables for `perf list`, alias lookup, and event programming. The R2PCIe `Unit` is the key integration point because a wrong or missing unit would route these aliases to the wrong PMU.

## State and persistence behavior

The file has no mutable process state. The persistent state is the source-controlled mapping from public alias names to event select values, unit masks, counter constraints, and package scope. Renaming an alias changes the user-visible perf interface. Changing `EventCode`, `UMask`, `Counter`, or `Unit` changes the hardware register programming or scheduling constraints.

## Dependencies

The file depends on Intel Haswell uncore R2PCIe event definitions, the perf PMU JSON schema, the x86 model map, `jevents.py` unit conversion, and kernel exposure of matching `uncore_r2pcie` PMU devices. Its descriptions also depend on Intel terminology for IIO, QPI, BL/AD/AK/IV rings, S-box credits, and message classes such as DRS, NCB, and NCS.

## Risks

The main risk is silent mismeasurement: event aliases will still parse if a mask or code is wrong, but perf would program the wrong counter. Counter restrictions are also important because some R2PCIe events are limited to two counters or a single counter; relaxing them can make perf accept impossible schedules. Some `PublicDescription` text combines generic family descriptions with suffix-specific notes, so bulk editing can accidentally attach the wrong message class or polarity. Because all records are `PerPkg`, using these aliases as if they were per-core events can mislead higher-level analysis.

## Test signals

Useful checks are `python3 -m json.tool` or `jq empty` for syntax, perf's PMU event generation tests, `perf list` on Haswell Xeon hardware showing `uncore_r2pcie` aliases, and controlled workloads that exercise PCIe/IIO traffic while comparing ring used, credit used, and credit acquired relationships. Hardware validation should confirm package-level aggregation and counter scheduling limits for events restricted to `0,1` or `0`.
