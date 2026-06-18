<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/bos.c -->
# sources/distributed-fs/openafs/src/libadmin/test/bos.c

## Purpose
Implements the BOS-related `afscp` subcommands. It wraps libadmin BOS APIs for process management, admins, keys, cell/host configuration, executable deployment, restart schedules, logs, auth mode, arbitrary commands, and salvage operations.

## Important APIs, Types, And Functions
Utility helpers include `GetIntFromString`, local token parsing helpers, `ktime_ParsePeriodic`, print helpers for process state/type/info, key info, and restart time. Command handlers include `DoBosProcessCreate`, `DoBosFSProcessCreate`, `DoBosProcessDelete`, `DoBosProcessExecutionStateGet/Set/SetTemporary`, `DoBosProcessNameList`, `DoBosProcessInfoGet`, `DoBosProcessParameterList`, `DoBosProcessNotifierGet`, `DoBosProcessRestart`, `DoBosProcessAllStop/Start/WaitStop/WaitTransition/StopAndRestart`, `DoBosAdminCreate/Delete/List`, `DoBosKeyCreate/Delete/List`, `DoBosCellSet/Get`, `DoBosHostCreate/Delete/List`, `DoBosExecutableCreate/Revert/TimestampGet/Prune/RestartTimeSet/RestartTimeGet`, `DoBosLogGet`, `DoBosAuthSet`, `DoBosCommandExecute`, `DoBosSalvage`, and `SetupBosAdminCmd`.

## Control Flow
Every command opens a BOS server handle with `bos_ServerOpen(cellHandle, -server, &bos_server, &st)`, validates command-specific options, calls one libadmin BOS operation, prints output for getters/listers, and usually closes the server. List commands use `Begin/Next/Done` iterators and verify `ADMITERATORDONE`. Restart-time commands parse human-readable time tokens into `bos_RestartTime_t`. Key creation derives a key from the current cell name and a string through `kas_StringToKey`.

## State And Persistence
Most handlers mutate persistent BOS server state: `BosConfig`, `UserList`, `KeyFile`, `CellServDB`, executable files, restart schedules, auth requirement, or salvager side effects. `DoBosLogGet` dynamically grows a local buffer while reading remote log contents. The command module itself stores only stack-local state.

## Dependencies And Integration Points
It depends on `bos.h`, `common.h`, `afs_bosAdmin.h`, `afs_clientAdmin.h`, `afs_utilAdmin.h`, `kas_StringToKey`, `cmd`, pthread/RX headers, and global `cellHandle` from `afscp.c`. It is registered by `SetupBosAdminCmd`.

## Risks And Test Signals
Several bugs are visible: `DoBosCellSet` reads `as->parms[SERVER]` into `cell` instead of the `CELL` parameter, `Print_bos_ProcessState_p` tests `BOS_PROCESS_OK` as a bit even though the comment says it is zero, `Print_bos_RestartTime_p` contains duplicated `NOW` condition text in this checkout, and some getter paths do not close `bos_server` before returning. The time parser has fixed 256-byte token buffers. Tests should cover every command syntax, server open/close, iterator completion, cell-set correctness, key conversion, restart time parse/format round trips, log growth on `ADMMOREDATA`, and high-risk mutating operations in a disposable test cell.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/libadmin/test/bos.c -->
