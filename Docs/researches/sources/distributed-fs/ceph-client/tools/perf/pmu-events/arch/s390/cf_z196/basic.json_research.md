# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z196/basic.json

## Purpose
Defines the basic IBM z196 CPU-M-CF perf aliases for cycles, instructions, L1 instruction/data directory writes, L1 penalty cycles, and their problem-state variants.

## APIs, Types, and Functions
The file has 12 records using `Unit: CPU-M-CF`, event codes 0-5 and 32-37, names such as `CPU_CYCLES`, `INSTRUCTIONS`, `L1I_DIR_WRITES`, and `PROBLEM_STATE_INSTRUCTIONS`, plus brief/public descriptions. `jevents.py` maps these to the `cpum_cf` PMU and generates standard perf aliases.

## Control Flow, State, and Persistence
The JSON is parsed during perf build for the z196 table selected by the s390 mapfile IBM 2817/2818 pattern. At runtime perf exposes the aliases for matching machines and reads kernel `cpum_cf` counters. No mutable state is stored in the JSON.

## Dependencies and Integration
These names are foundational for z196 metrics and for user scripts that rely on stable s390 CPU-M-CF aliases. They share the same schema and event-code layout as zEC12 `basic.json`, which indicates continuity across generations.

## Risks and Test Signals
Risks are low but include wrong problem-state code ranges and mismatch with kernel counter-set authorization. Test signals include JSON syntax checks, generated `pmu-events.c` inspection, `perf list` on z196, and smoke tests for `CPU_CYCLES` and `INSTRUCTIONS`.
