# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_zec12/basic.json

## Purpose
Defines the basic zEC12 CPU-M-CF perf aliases for core execution and L1 cache accounting, mirroring the z196 basic event layout.

## APIs, Types, and Functions
The file has 12 records with `Unit: CPU-M-CF`, event codes 0-5 and 32-37, and names for cycles, instructions, L1 I/D directory writes, L1 I/D penalty cycles, and problem-state versions. `jevents.py` converts these records into `cpum_cf` aliases.

## Control Flow, State, and Persistence
At build time the perf event generator includes this file in the zEC12 generated event table selected for IBM 2827/2828 models. At runtime perf resolves the aliases and asks the kernel CPU-M-CF PMU to count the selected hardware events.

## Dependencies and Integration
Depends on the s390 mapfile, perf PMU event generation, and kernel `cpum_cf` support. The names are used by zEC12 metrics such as `transaction.json` and are intentionally stable across z196 and later s390 tables.

## Risks and Test Signals
Risks are primarily source-of-truth drift from the hardware manual and missing counter authorization on target systems. Test signals include JSON generation, `perf list`, and `perf stat` for `CPU_CYCLES`, `INSTRUCTIONS`, and problem-state counters.
