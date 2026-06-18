# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/s390/cf_zec12/crypto.json

## Purpose
Defines zEC12 CPU-M-CF crypto aliases for PRNG, SHA, DEA, and AES activity. It preserves the z196 crypto event layout for the zEC12 PMU table.

## APIs, Types, and Functions
The JSON contains 16 `CPU-M-CF` records with event codes 64-79. Each crypto family has counters for total functions, busy cycles, blocked functions, and blocked cycles. `jevents.py` turns the records into lower-case perf aliases on `cpum_cf`.

## Control Flow, State, and Persistence
The table is parsed only during perf build. Runtime state resides in CPU-M-CF hardware counters and is read through perf when users select these aliases.

## Dependencies and Integration
Depends on zEC12 model matching, the `CPU-M-CF` unit mapping, and kernel support for the crypto counter set. It sits beside zEC12 `basic.json`, `extended.json`, and `transaction.json`.

## Risks and Test Signals
Risks are incorrect code assignment, unsupported counter-set access on a given LPAR, and confusion between function counts and cycle counts. Test signals are valid JSON generation, generated alias checks, `perf list`, and representative hardware `perf stat` runs.
