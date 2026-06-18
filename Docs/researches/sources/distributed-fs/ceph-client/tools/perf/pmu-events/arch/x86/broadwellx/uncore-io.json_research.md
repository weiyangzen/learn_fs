# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/broadwellx/uncore-io.json

## Purpose

This file is a declarative Linux `perf` PMU event catalog for BroadwellX R2PCIe uncore I/O fabric events. It contains 62 JSON event records, all with `Unit: "R2PCIe"` and `PerPkg: "1"`. The records expose package-level aliases for R2PCIe clock ticks, IIO credit use, ring use, ring bounces, RxR and TxR queue pressure, SBO credit acquisition/occupancy, credit stalls, and clockwise TxR NACK causes.

The file is not executable code. Its source-level role is to feed `tools/perf/pmu-events/jevents.py`, which converts each JSON object into generated `pmu-events.c` metadata. `jevents.py` maps the `R2PCIe` unit through its generic `unit_to_pmu()` fallback to the runtime PMU name `uncore_r2pcie`, so the aliases are matched to Linux uncore R2PCIe PMU instances.

## Schema And Public API

Each JSON object is a public perf event alias. The important fields are `EventName`, `EventCode`, `UMask`, `Counter`, `Unit`, `PerPkg`, `BriefDescription`, and usually `PublicDescription`. `EventName` is lowercased by `jevents.py` for alias lookup; `EventCode` becomes `event=<hex>`; non-zero `UMask` becomes `umask=<hex>`; `Unit` selects the PMU; `PerPkg` records package aggregation semantics; descriptions are surfaced through `perf list`, JSON list output, and perf Python helpers.

The event families are `UNC_R2_CLOCKTICKS`, IIO credit events, AD/AK/BL/IV ring-use events, AK bounce events, RxR and TxR queue events, SBO0 credit events, no-SBO-credit stalls, and TxR clockwise NACK events. These families describe R2PCIe fabric utilization, queue pressure, and message-credit behavior at package scope.

## Control Flow And Integration

Build-time control flow is data-driven. The perf PMU build traverses `tools/perf/pmu-events/arch`, and `jevents.py` loads this file with `json.load(..., object_hook=JsonEvent)`. For each object, `JsonEvent.__init__` captures the name, descriptions, PMU unit, package flag, and encoding terms. The generated event string is built from `EventCode` plus supported fields such as `UMask`; this file does not use `Filter`, `ScaleUnit`, `Errata`, or metric expression fields.

At runtime, perf selects the BroadwellX table through the x86 mapfile entry for family/model `GenuineIntel-6-4F`. PMU matching code can ignore uncore instance suffixes and wildcard PMU names, allowing one generated `uncore_r2pcie` table to attach to the concrete R2PCIe PMU devices exposed under sysfs. User commands such as `perf list`, `perf stat -e unc_r2_ring_ad_used.all`, and JSON listing paths consume these aliases.

## State And Persistence

The JSON has no mutable runtime state and performs no I/O by itself. Its persistent effect is the generated perf event table compiled into the perf binary. Edits to event names, selectors, unit masks, counter constraints, units, or descriptions change the public alias API and the raw hardware event programming emitted by perf.

All records are package scoped through `PerPkg: "1"`, so they describe socket/package uncore activity rather than per-thread core activity. Counter availability is declarative: most ring-use events allow counters 0-3, while credit and queue families often use only counters 0-1 or a narrower subset.

## Dependencies, Risks, And Test Signals

The file depends on the PMU JSON schema accepted by `jevents.py`, the x86 BroadwellX mapfile selection, and kernel/sysfs support for Intel BroadwellX R2PCIe uncore PMUs. Hardware interpretation depends on BroadwellX ring topology, R2PCIe uclk timing, IIO message classes, QPI links, NCB/NCS/DRS credit behavior, SBO credit paths, and TxR/RxR queue semantics.

The highest-risk fields are `Unit`, `EventCode`, `UMask`, and `Counter`. A `Unit` typo changes PMU routing or hides events. A wrong mask can silently count a different ring direction, queue class, or credit type. Useful checks are `jq empty`, `jq 'length'` returning 62, generator output containing `uncore_r2pcie`, and runtime smoke tests for `UNC_R2_CLOCKTICKS`, `UNC_R2_IIO_CREDITS_USED.NCB`, `UNC_R2_RING_AD_USED.ALL`, `UNC_R2_STALL_NO_SBO_CREDIT.SBO0_AD`, and `UNC_R2_TxR_NACK_CW.UP_BL`.
