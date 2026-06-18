# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/x86/pantherlake/uncore-memory.json

## Purpose

`uncore-memory.json` is the Panther Lake integrated memory-controller event catalog for perf. It contains three package-scoped `iMC` events: `UNC_M_CAS_COUNT_RD`, `UNC_M_CAS_COUNT_WR`, and `UNC_M_TOTAL_DATA`. These rows expose DRAM read CAS commands, write CAS commands, and total 32-byte data transfers per DDR channel.

## Important APIs, Types, and Data Fields

The file is a JSON event array using `EventName`, `EventCode`, `Counter`, `Unit`, `PerPkg`, and `BriefDescription`. All rows use `Unit: iMC`, `PerPkg: 1`, and programmable counters `0,1,2,3,4`. The read and write CAS events use event codes `0x22` and `0x23`; total data uses event code `0x3C` and documents that the counter increments per 32-byte data chunk.

## Control Flow and Data Flow

The file has no executable flow. At build time, perf's `jevents.py` reads the rows and maps `Unit: iMC` to an uncore PMU table. At runtime, perf resolves the alias, programs the package-level iMC counter on the relevant memory-controller instance, and reports aggregate counts for the measurement interval. Data flows from memory-controller transaction accounting into perf counts, usually consumed as bandwidth or read/write traffic ratios.

## State and Persistence Behavior

The static JSON metadata is persistent. Counter values are interval-local hardware state and are not persisted by this file. `PerPkg: 1` means counts are package-scoped rather than task-scoped; any workload on the package can contribute. The 32-byte transfer granularity on `UNC_M_TOTAL_DATA` is part of the event's semantic state and must be preserved when converting counts to bytes.

## Dependencies and Integration Points

This file depends on Panther Lake iMC PMU support in the kernel and perf. It integrates with `perf list`, `perf stat`, memory bandwidth tools, and any higher-level Intel metrics that estimate DRAM traffic. It complements Panther Lake core cache, memory, and virtual-memory events by measuring traffic after requests reach the memory controller.

## Risks and Edge Cases

The package scope can mislead process-level analysis because unrelated activity contributes to counts. Per-channel interpretation depends on how perf exposes iMC instances and how users aggregate them. CAS counts and total data counts are not interchangeable: CAS rows count commands, while total data counts 32-byte chunks. Counter scheduling can be constrained by the five iMC counters. Systems without exposed Panther Lake iMC PMUs may list no usable aliases even though the generated table exists.

## Test Signals

Validation should include JSON parse success, generated event-table build success, and `perf list` visibility for `UNC_M_CAS_COUNT_RD`, `UNC_M_CAS_COUNT_WR`, and `UNC_M_TOTAL_DATA` on matching hardware. Streaming read workloads should raise read CAS and total data; streaming stores should raise write CAS and total data; idle baselines should remain low apart from background traffic. Bandwidth checks should convert `UNC_M_TOTAL_DATA` using the documented 32-byte granularity.
