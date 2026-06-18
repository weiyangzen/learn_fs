# sources/distributed-fs/ceph-client/tools/perf/pmu-events/arch/powerpc/power10/cache.json

## Purpose
This 4-entry POWER10 cache topic file defines a small set of cache and instruction-completion events: L1 reload for prefetch line miss, L1 I-cache miss, L1 I-cache reloaded by prefetch, and concurrent run instruction completion.

## Important Data Fields
Rows use `EventCode`, `EventName`, and `BriefDescription`. Encodings include `0x1002C` for `PM_LD_PREFETCH_CACHE_LINE_MISS` and `0x300F4` for `PM_RUN_INST_CMPL_CONC`.

## Control Flow And Integration
PowerPC `mapfile.csv` maps POWER10 PVR patterns `0x0080...` and `0x0082...` to the `power10` directory. `jevents.py` emits these rows into the POWER10 event table, and perf exposes them with other POWER10 topic files.

## State, Dependencies, Risks, And Tests
The file is static model metadata. Risks are limited in size but include event-code transcription errors and topic overlap with larger POWER10 files such as datasource, frontend, and pmc. Test signals include JSON validity, generated table inclusion, `perf list PM_L1_ICACHE_MISS`, and workload checks that exercise instruction-cache and prefetch behavior.
