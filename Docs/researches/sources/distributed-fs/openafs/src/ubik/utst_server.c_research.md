
# sources/distributed-fs/openafs/src/ubik/utst_server.c

`utst_server.c` is the matching sample Ubik server. It creates a replicated test database under the system temp directory, exports sample RPC handlers, and demonstrates basic read/write transactions, locking, abort, truncate, and read-any behavior.

Important RPC handlers are `SSAMPLE_Inc`, `SSAMPLE_Get`, `SSAMPLE_QGet`, `SSAMPLE_Trun`, and `SSAMPLE_Test`. `SSAMPLE_Inc` starts a write transaction, obtains a whole-database write lock by convention at position 1, optionally sleeps, reads an integer with `UEOF` treated as zero, increments it, seeks to offset 0, writes it, and commits. `SSAMPLE_Get` starts a read transaction and read lock; `SSAMPLE_QGet` uses `ubik_BeginTransReadAny`; `SSAMPLE_Trun` truncates the database to zero; `SSAMPLE_Test` starts and locks a write transaction, reads, then deliberately aborts.

The `main` path parses `-sleep`, uses `ubik_ParseServerList`, initializes Ubik with `/tmp/testdb` equivalent and port 3000, registers a null-security SAMPLE service, sets min/max Rx procs, and starts the Rx server. Persistence is the Ubik database files with prefix `testdb`; the logical payload is a single 32-bit integer.

Dependencies are the Ubik public API, generated `utst_int.h`/SAMPLE service, Rx null server security, and temp-directory utilities. Risks are appropriate for a sample: hard-coded port and database naming, null security, no cleanup, no endian conversion for stored integer, and coarse locking convention. Test signals are direct: increment/get cycles, abort not changing state, truncate resetting to `UEOF`/zero, sleep-induced lock contention, and multi-server quorum behavior.
