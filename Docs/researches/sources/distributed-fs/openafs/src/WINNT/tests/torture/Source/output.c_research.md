# sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/output.c

Purpose: reporting and logging support for the Windows torture harness. It converts per-command `cmd_struct` counters into readable statistics, serializes thread/process log writes, dumps AFS client trace logs, and builds aggregate master statistics files.

Important APIs and functions: `LogStats` prints tabular command latency, count, cost, and error summaries. `LogMessage` appends timestamped messages to per-thread logs and optionally a chronological `Chron.log`. `DumpAFSLog` runs `fs trace -dump`, moves `%WINDIR%\TEMP\afsd.log` into the current run's log directory, and renames it with host/iteration context. `UpdateMasterLog` reads, merges, and rewrites a raw numeric accumulator file. `BuildMasterStatLog` rolls a numeric accumulator into a formatted statistics report.

Control flow: callers pass command counters from worker threads or processes. `LogStats` zeroes a temporary aggregate, folds supplied counters, emits headers, and prints one row per `cmd_names` entry. `LogMessage` conditionally guards chronological logging with `ChronMutexHandle`; master-log updates use `FileMutexHandle`.

State and persistence: writes under `log%05d` directories in the process working directory. The raw master log persists seven numeric lines per command entry, while the formatted stat log is rebuilt by `BuildMasterStatLog`.

Dependencies and integration: uses globals from the stress runner (`ChronLog`, `CurrentLoop`, mutex handles), command metadata from `common.h`, Win32 file/mutex APIs, and the OpenAFS `fs trace` command.

Risks and test signals: formatting uses fixed 512/1024 byte buffers and assumes log directories exist. Several `fopen` and `system` results are not fully checked. Correct operation is visible through stable chronological ordering, merged master counts, and generated `afsd_<host>_iterationN.log` trace files.
