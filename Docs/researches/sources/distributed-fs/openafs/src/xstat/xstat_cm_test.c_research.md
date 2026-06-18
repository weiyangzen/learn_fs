# sources/distributed-fs/openafs/src/xstat/xstat_cm_test.c

## Purpose
`xstat_cm_test.c` is a command-line exerciser for the OpenAFS Cache Manager extended-statistics client. It resolves one or more Cache Manager hosts, asks `xstat_cm` to collect selected AFSCB xstat collections, and prints human-readable summaries of call counters, cache-manager performance state, server up/down distributions, RPC timings, transfer buckets, authentication, and access statistics.

## Important APIs, Types, And Functions
The main entry points are `main`, `RunTheTest`, `CM_Handler`, `print_cmCallStats`, `PrintPerfInfo`, `PrintFullPerfInfo`, `PrintOverallPerfInfo`, `PrintRPCPerfInfo`, `PrintOpTiming`, `PrintXferTiming`, `PrintErrInfo`, and `CountListItems`. The file uses `xstat_cm_Init`, `xstat_cm_Wait`, `xstat_cm_Cleanup`, `xstat_cm_Results`, AFS command parser types (`cmd_syndesc`, `cmd_item`), `hostutil_GetHostByName`, `opr_softsig_Init`, and Rx finalization.

## Control Flow
`main` registers `-cmname`, `-collID`, `-onceonly`, `-frequency`, `-period`, and `-debug` options through the OpenAFS `cmd` framework. `RunTheTest` initializes soft signal handling, derives one-shot/debug flags, counts command-list items, resolves CM hostnames to port 7001 socket addresses, parses collection IDs into an `afs_int32` array, and starts `xstat_cm_Init` with `CM_Handler`. `xstat_cm_Wait` then blocks for one collection in one-shot mode or for the requested period in continuous mode. `CM_Handler` checks `probeOK`, optionally dumps raw words, and switches on the collection number: call-info prints macro-expanded `AFS_CM_CALL_STATS`, perf-info is intentionally suppressed, and full-perf decodes and prints overall, RPC, authentication, and access groups.

## State And Persistence
The file keeps only process-local state: `debugging_on`, `one_shot`, static operation-name arrays, parsed socket and collection arrays, and the global `xstat_cm_Results` maintained by the xstat module. It writes no persistent state. It does allocate `CMSktArray` and `collIDP`; cleanup focuses on `xstat_cm_Cleanup` and `rx_Finalize`, so command-side allocations are process-lifetime allocations.

## Dependencies And Integration Points
It integrates with the `xstat_cm` library, the AFSCB/cache-manager xstat wire structures, Rx, host utilities, OpenAFS command parsing, and the generated `AFS_component_version_number.c`. The printed structure sizes must match the Cache Manager that serves the statistics, so this test is both a sample client and a compatibility probe for xstat collection layouts.

## Risks And Test Signals
Risks include strict struct-size assumptions for perf/full-perf collections, no bounds guard on operation-name arrays beyond constants, process exits from inside `RunTheTest`, and memory not freed before normal process termination. Useful test signals are successful host resolution, one-shot collection completion, expected output for `AFSCB_XSTATSCOLL_CALL_INFO` and `AFSCB_XSTATSCOLL_FULL_PERF_INFO`, size-mismatch messages against incompatible CMs, and error reporting when a CM probe fails.
