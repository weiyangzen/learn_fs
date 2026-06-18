<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-hha.json -->
# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-hha.json

## Purpose
Hip08 uncore HHA home-agent PMU event table. It tracks received operations from outer/SCCL/CCIX paths, write-back and stash traffic, DDR read/write transactions, spill behavior, broadcast/invalidation and snoop traffic, snoop responses, directory lookup/hit counts, and home migration.

## APIs, Types, and Functions
Records use `EventName`, `ConfigCode`, `BriefDescription`, and `Unit`. Important aliases include `rx_ops_num`, `rx_outer`, `rx_sccl`, `rx_ccix`, `rx_wbi`, `rd_ddr_64b`, `wr_ddr_128b`, `spill_num`, `spill_success`, `bi_num`, `tx_snp_num`, `rx_snprspdata`, `sdir-lookup`, `edir-lookup`, `sdir-hit`, `edir-hit`, and home-migrate events.

## Control Flow, State, and Persistence
The file is compiled into perf uncore event metadata. Runtime perf programs HHA unit counters by config code; the JSON stores no mutable state and no aggregation policy.

## Dependencies and Integration
Depends on the Hip08 HHA uncore PMU driver exposing matching unit names and config codes. It integrates with DDRC and L3C uncore events plus core cache-miss and memory-bound metrics to analyze coherence and memory-routing behavior.

## Risks and Test Signals
Risks include event names containing hyphens needing correct perf alias handling, topology-specific SCCL/CCIX semantics, multi-agent aggregation errors, and directory counters not matching simple cache-hit expectations. Test signals are alias generation, socket-local versus remote/coherent workloads, CCIX traffic tests where available, and consistency among HHA DDR transaction counts and DDRC flux counters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/arm64/hisilicon/hip08/uncore-hha.json -->
