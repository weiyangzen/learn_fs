# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z196/extended.json

## Purpose
Defines z196 extended CPU-M-CF aliases for cache sourcing and translation activity. The table covers L1 directory writes sourced from L2/L3/L4/local memory, first-level TLB misses/writes, huge-page TLB writes, and second-level translation-table writes.

## APIs, Types, and Functions
The JSON array has 24 `CPU-M-CF` records. Important names include `L1D_L2_SOURCED_WRITES`, `L1I_L2_SOURCED_WRITES`, `DTLB1_MISSES`, `ITLB1_MISSES`, `L2C_STORES_SENT`, `L1D_*_L3_SOURCED_WRITES`, `L1*_ONBOOK_L4_SOURCED_WRITES`, `L1*_OFFBOOK_L4_SOURCED_WRITES`, `DTLB1_HPAGE_WRITES`, and `TLB2_*_WRITES`.

## Control Flow, State, and Persistence
The file is consumed at perf build time and materialized into the generated z196 PMU event table. At runtime perf maps names to event codes for the `cpum_cf` PMU. Counter values are hardware state; the JSON does not persist runtime values.

## Dependencies and Integration
Depends on IBM z196 CPU matching in `arch/s390/mapfile.csv`, `jevents.py`, and kernel support for the extended counter set. It forms the generation-specific event catalog that later zEC12/z17 tables expand and rename around newer cache topology terms.

## Risks and Test Signals
Risks include topology-specific naming mistakes (`onbook`, `offbook`, `onchip`, `offchip`) and incorrect code reuse across CPU generations. Test signals are generated-table validation, `perf list` on z196 hardware, and comparing alias names/codes against IBM counter-set documentation.
