# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_z17/extended.json

## Purpose
Defines the z17 extended CPU-M-CF event aliases used for cache/TLB sourcing, transactional execution, multithreading diagnostics, branch prediction, decimal/vector/deflate operations, and NNPA integrated-accelerator activity. It is the main z17 counter-facility event table beyond basic and crypto counters.

## APIs, Types, and Functions
The file contains 77 event records with `Unit: CPU-M-CF`, decimal `EventCode`, `EventName`, and descriptions. Important groups include TLB2 events (`DTLB2_*`, `ITLB2_*`, `TLB2_*`), transaction events (`TX_C_TEND`, `TX_NC_TEND`, `TX_*_TABORT`), data/instruction directory-write sourcing (`DCW_*`, `IDCW_*`, `ICW_*`), SMT accounting (`CYCLES_*THRD`, `INST_*THRD`, `MT_DIAG_CYCLES_*`), and accelerator counters (`DFLT_*`, `NNPA_*`). `jevents.py` maps these records to `cpum_cf` aliases and encodes the event code as the PMU config.

## Control Flow, State, and Persistence
Build-time flow is declarative: the JSON is parsed into generated `pmu-events.c` tables for z17. Runtime flow depends on perf CPU matching; once z17 is selected, these names become available for `perf stat` and metric expressions. The file itself stores no state, but its names form a persistent ABI-like catalog for users, scripts, and sibling z17 metrics.

## Dependencies and Integration
Integrates with `arch/s390/mapfile.csv` entries for IBM 9175/9176 and with `transaction.json`, whose z17 metric expressions reference many symbols from this file. It also relies on the kernel `cpum_cf` PMU supporting the listed extended set counters and on perf's event parser accepting the generated aliases.

## Risks and Test Signals
The largest risk is cross-file consistency: if a metric references `DCW_REQ`, `L1C_TLB2_MISSES`, or transaction abort counters absent from this table, `has_event()` guards may mask the error by returning zero. Counter semantics are hardware-specific and several names are similar, so wrong codes would produce plausible but misleading performance data. Test signals are successful jevents generation, `perf list` coverage for all 77 names, metric validation for z17 `transaction.json`, and hardware smoke tests for representative TLB, cache-sourcing, transaction, NNPA, and MT diagnostic counters.
