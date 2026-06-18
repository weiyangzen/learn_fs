# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/lunarlake/uncore-memory.json

## Purpose

`uncore-memory.json` defines five Lunar Lake integrated-memory-controller events for DRAM command and data movement analysis. `UNC_M_CAS_COUNT_RD` and `UNC_M_CAS_COUNT_WR` count read and write CAS commands, `UNC_M_DRAM_THERMAL_HOT` and `UNC_M_DRAM_THERMAL_WARM` count thermal state indications, and `UNC_M_TOTAL_DATA` counts read/write data transfers in 32-byte chunks per DDR channel. All entries use `Unit: "iMC"` and are package scoped.

## Important APIs, Types, And Data Shape

The file is a JSON array of five uncore event objects. Shared fields include `BriefDescription`, `Counter`, `EventCode`, `EventName`, `PerPkg`, and `Unit`. The thermal events additionally carry `Experimental: "1"`, signaling that callers should treat them as less stable. Counters are programmable uncore counters `0,1,2,3,4`; event codes are `0x22`, `0x23`, `0x19`, `0x1A`, and `0x3C`.

## Control Flow

`jevents.py` parses the file as normal event metadata with topic `uncore-memory`. The generated alias table is available to perf list/stat, but runtime collection depends on matching uncore iMC devices exposed by the kernel. The data-transfer event can be scaled by tooling or humans using its 32-byte chunk description.

## State And Persistence

This is static declarative metadata. Generated perf tables persist event codes, package scope, and experimental markers. Runtime state is in uncore iMC counters; collection is package or memory-controller scoped rather than per task.

## Dependencies And Integration Points

Dependencies include Lunar Lake iMC PMU support, perf uncore PMU matching, and generated PMU event tables. Integration points include `perf list uncore-memory`, `perf stat` package aggregation, memory bandwidth metrics, and any dashboards that translate `UNC_M_TOTAL_DATA` counts into bytes.

## Risks

Thermal events are explicitly experimental and may change or be unavailable on some systems. `UNC_M_TOTAL_DATA` counts 32-byte chunks rather than bytes, so consumers can be off by a factor of 32 if they assume raw bytes. Per-package aggregation can surprise users expecting per-core or per-thread attribution. A unit spelling mismatch (`iMC`) would prevent alias matching.

## Test Signals

Useful checks are JSON validity, length 5, all entries `PerPkg: "1"`, and generator success. Runtime testing on Lunar Lake should confirm iMC PMUs under sysfs, `perf list uncore-memory`, read/write CAS counts under memory traffic, and expected scaling behavior for `UNC_M_TOTAL_DATA`.
