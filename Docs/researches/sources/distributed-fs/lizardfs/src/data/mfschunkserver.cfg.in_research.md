# sources/distributed-fs/lizardfs/src/data/mfschunkserver.cfg.in

Purpose: configured sample chunkserver daemon configuration.

Important settings: daemon identity/user/group, memory lock/nice level, data path, master connection (`MASTER_HOST`, `MASTER_PORT`, timeouts), client listen host/port, worker/thread counts, read-ahead/read-behind, HDD config path, disk reserve threshold, chunk testing, no-cache and hole-punch options, load factor reporting, replication bandwidth/timeouts, chunk format and fsync policy.

Control flow: CMake substitutes install defaults like `@DEFAULT_USER@`, `@DATA_PATH@`, and `@ETC_PATH@`; the chunkserver config parser reads active uncommented settings at daemon startup/reload.

State and persistence: persistent local daemon config; controls data path and runtime behavior but stores no chunk data itself.

Dependencies and integration: installed as a chunkserver example; references `mfshdd.cfg`, master ports, chunkserver networking, disk I/O workers, and replication protocols.

Risks: duplicated settings such as `NR_OF_NETWORK_WORKERS` and `REPLICATION_BANDWIDTH_LIMIT_KBPS` appear in the sample comments with different example/default contexts, which can confuse edits. Disk, fsync, and worker settings have direct durability/performance impact.

Test signals: no direct tests; configuration names line up with chunkserver runtime modules and packaging generation.
