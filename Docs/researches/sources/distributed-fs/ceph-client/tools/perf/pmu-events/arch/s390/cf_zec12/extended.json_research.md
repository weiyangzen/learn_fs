# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_zec12/extended.json

## Purpose
Defines zEC12 extended CPU-M-CF aliases for TLB, cache sourcing, and transactional-execution counters. It expands z196-style cache/TLB events with zEC12 L2I/L2D sourcing, intervention variants, and transaction begin/end/abort counters.

## APIs, Types, and Functions
The file contains 35 records with `Unit: CPU-M-CF`. It includes first-level TLB misses/writes, huge-page and second-level TLB writes, L1 data/instruction sourcing from L2I/L2D/local memory/L3/L4, invalid/intervention variants, and transaction counters `TX_NC_TEND`, `TX_C_TEND`, `TX_NC_TABORT`, `TX_C_TABORT_NO_SPECIAL`, and `TX_C_TABORT_SPECIAL`.

## Control Flow, State, and Persistence
The JSON is static input to `jevents.py`, which emits zEC12 generated event tables. Runtime perf flow is alias resolution followed by `cpum_cf` event programming. No file-level mutable state exists.

## Dependencies and Integration
Depends on zEC12 CPU matching and kernel extended counter support. `transaction.json` in the same directory references the transaction aliases from this file, while basic metrics rely on sibling `basic.json`.

## Risks and Test Signals
Risks include metrics silently becoming wrong if any transaction alias is renamed, topology naming differences between z196/zEC12/z17, and invalid/intervention suffix confusion. Test signals include successful metric parsing, `perf list` coverage, and `perf stat -M transaction` plus direct transaction alias tests on zEC12 hardware.
