# sources/distributed-fs/coda/coda-src/venus/venusrecov.cc

## Purpose
This file implements Venus recoverable storage management over RVM/RDS or VM mode. It validates and initializes persistent globals, creates/loads RVM log and data segments, manages transaction boundaries and no-flush persistence bounds, flushes/truncates logs, records clean shutdown, copies recoverable strings, starts the recovery daemon, and generates store ids for mutating operations.

## Important APIs, Types, and Functions
Globals include `RecovInited`, `rvg`, transaction counters, `MapPrivate`, initialization flags, RVM path/size/config parameters, and flush/truncate thresholds. `RecovVenusGlobals::validate/print` check persistent root integrity. `RecovInit()` drives VM or RVM initialization. Private helpers include `Recov_CheckParms`, `Recov_InitRVM`, `Recov_InitRDS`, `Recov_LoadRDS`, and `Recov_GetStatistics`. Public operations include `_Recov_BeginTrans`, `Recov_EndTrans`, `Recov_SetBound`, `RecovFlush`, `RecovTruncate`, `RecovTerminate`, `RecovPrint`, `Copy_RPC2_String`, `Free_RPC2_String`, `RECOVD_Init`, `RecovDaemon`, and `Recov_GenerateStoreId`.

## Control Flow
Startup calls `RecovInit()`, which fills defaults, handles VM mode as fresh in-memory metadata, or initializes RVM/RDS and loads the data segment. Fresh metadata zeroes and initializes `RecovVenusGlobals`; existing metadata validates heap bounds, magic/version, persistent roots, clean-shutdown state, and resets `recov_CleanShutDown` to dirty. Store identity is regenerated on init/new-instance or when replay-detection mode changes. The recovery daemon wakes every five seconds, observes worker idle time and RVM statistics, then truncates or flushes when thresholds are met.

## State and Persistence Behavior
Persistent root state lives in `RecovVenusGlobals`: magic/version, last init, clean shutdown, FSDB/VDB/REALMDB/HDB roots, heap bounds, UUID, and store id. Transactions are begun with `no_restore` and ended with `no_flush`; `Recov_SetBound()` bounds how long committed no-flush data may remain unflushed. `RecovTerminate()` writes a clean-shutdown marker only when there are no uncommitted transactions.

## Dependencies and Integration Points
It depends on RVM/RDS libraries, recovery annotations/macros, FSDB/VDB/HDB/RealmDB types, worker idle-time reporting, mariner/logging, RPC2 random generation for store identity, and Venus configuration from `venus.private.h`. Many persistent modules depend on `Recov_BeginTrans`/`Recov_EndTrans` and `RVMLIB_REC_OBJECT` semantics.

## Risks and Test Signals
Risks include RVM address assumptions per platform, data/log size calculations, dirty-shutdown validation, unflushed transaction windows, signal-handler use of RVM primitives, store-id overflow/replay detection behavior, and VM mode bypassing persistence. Tests should cover fresh init, restart validation, version/magic mismatch, clean versus dirty shutdown, explicit `-init`, private mapping, flush/truncate thresholds, recoverable string copy/free, and monotonic store id generation.
