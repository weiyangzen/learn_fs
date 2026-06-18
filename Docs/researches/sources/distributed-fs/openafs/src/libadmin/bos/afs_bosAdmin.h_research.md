# sources/distributed-fs/openafs/src/libadmin/bos/afs_bosAdmin.h

## Purpose
Declares the public BOS administration API and BOS-facing types used by libadmin clients. It describes process types/states, authentication/prune/restart/salvage options, process/key/restart-time result structures, and all exported BOS operations.

## Important APIs, Types, And Functions
Constants include `BOS_MAX_NAME_LEN`, `BOS_MAX_PROCESS_PARAMETERS`, and `BOS_ENCRYPTION_KEY_LEN`. Public enums model process type (`simple`, `fs`, `cron`), execution state, error state flags, noauth policy, prune flags, restart schedule type, restart-BOS choice, and salvage flags. Important structures are `bos_ProcessInfo_t`, `bos_encryptionKeyStatus_t`, `bos_KeyInfo_t`, and `bos_RestartTime_t`.

The function surface includes server open/close, process lifecycle and enumeration, admin list mutation/enumeration, key mutation/enumeration, cell/host list mutation/enumeration, executable upload/revert/timestamp/prune/restart schedule, log retrieval, auth policy, command execution, and `bos_Salvage`. `kas_to_bozoptr` casts a KAS encryption key to the bozo key structure expected by generated RPC stubs.

## Control Flow
The header establishes common begin/next/done patterns for process names, parameters, admins, keys, and hosts. Most other functions are synchronous one-shot operations against a BOS server handle.

## State And Persistence
The header stores no state itself. Its API represents persistent BOS server state: BosConfig process definitions, process goals, administrator list, KeyFile keys, CellServDB host list, server cell name, executable revisions, logs, restart schedules, and noauth mode.

## Dependencies And Integration Points
It includes `afs_Admin.h`, `afs_vosAdmin.h`, and `afs_kasAdmin.h`, tying BOS salvage options to VOS force flags and BOS key APIs to KAS encryption key types. It must remain layout-compatible with the bozo RPC implementation because enums and structures are cast or mapped directly in `afs_bosAdmin.c`.

## Risks And Test Signals
The comment notes that `bos_ProcessExecutionState_t` values must match bozo `BSTAT_*` values; enum drift would silently corrupt state mapping. Public fixed-size buffer assumptions require consumer compile/runtime tests. ABI tests should cover structure sizes, enum values, and all exported prototypes on Windows and Unix.
