# sources/distributed-fs/openafs/src/xstat/xstat_fs_test.c

## Purpose
`xstat_fs_test.c` is a command-line test client for the `xstat_fs` File Server statistics module. It resolves file-server hosts, requests specified xstat collection IDs, and prints raw call information, overall performance counters, full detailed RPC/transfer timings, and callback counters.

## Important APIs, Types, And Functions
Important functions include `main`, `RunTheTest`, `FS_Handler`, `PrintCallInfo`, `PrintPerfInfo`, `PrintFullPerfInfo`, `PrintOverallPerfInfo`, `PrintDetailedPerfInfo`, `PrintOpTiming`, `PrintXferTiming`, `PrintCbCounters`, and `CountListItems`. The file uses `xstat_fs_Init`, `xstat_fs_Wait`, `xstat_fs_Cleanup`, `xstat_fs_DecodeFullPerfStats`, `xstat_fs_Results`, OpenAFS command parsing, host utilities, Rx finalization, and xstat collection constants such as `AFS_XSTATSCOLL_CALL_INFO`, `AFS_XSTATSCOLL_PERF_INFO`, `AFS_XSTATSCOLL_FULL_PERF_INFO`, and `AFS_XSTATSCOLL_CBSTATS`.

## Control Flow
`main` registers command parameters for file-server names, collection IDs, one-shot mode, frequency, period, and debug mode. `RunTheTest` initializes signal handling, parses flags and defaults, builds a fixed local array of up to twenty file-server socket addresses on port 7000, parses collection IDs, and starts `xstat_fs_Init` with `FS_Handler`. The handler checks `probeOK`, dumps raw entries in debug mode, and dispatches by collection ID. `PrintFullPerfInfo` calls `xstat_fs_DecodeFullPerfStats` before printing platform-neutral detailed timings; `PrintPerfInfo` directly casts the buffer to `struct afs_PerfStats` after a size check.

## State And Persistence
The test maintains only process-local flags, static display-name tables, parsed sockets, collection IDs, and the shared `xstat_fs_Results` populated by the xstat module. It does not persist data. The fixed `FSSktArray[20]` and process-lifetime allocation of `collIDP` are notable state choices.

## Dependencies And Integration Points
It integrates with the file-server xstat library, AFS file-server statistics structures, Rx, OpenAFS command parsing, host name utilities, and the generated component-version include. Its output is a human-facing validation surface for the xstat wire format and `xstat_fs_DecodeFullPerfStats`.

## Risks And Test Signals
Risks include the fixed twenty-server socket array, struct-size assumptions for direct perf casts, little validation of collection IDs, process exits inside command handling, and potential mismatch between `CbCounterStrings` and returned callback-stat count. Useful tests include one-shot and continuous runs, multiple collection IDs per server, debug raw dumps, full-perf decoding from different server architectures, callback counter collection, and failure paths for host resolution and failed probes.
