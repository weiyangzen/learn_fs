# sources/distributed-fs/openafs/src/libadmin/kas/afs_kasAdmin.c

## Purpose
This file implements the OpenAFS KAS admin API over KAuth/Ubik RPCs. It manages KAS server handles, principal creation/deletion/query/iteration, password/key updates, lock status/unlock operations, principal field updates, server stats/debug queries, random key retrieval, and string-to-key/checksum utilities.

## Important APIs, Types, and Functions
- Private `kas_server_t` stores magic, validity, `struct ubik_client *servers`, and cell name.
- Validation/selection helpers: `IsValidServerHandle`, `IsValidCellHandle`, and `ChooseValidServer` enforce that callers use either a cell handle or a KAS server handle, not both.
- Conversion helper `kaentryinfo_to_kas_principalEntry_t` maps KAuth `kaentryinfo` flags, dates, key fields, and packed auth bytes into public `kas_principalEntry_t`.
- Server handle APIs: `kas_ServerOpen` and `kas_ServerClose`.
- Principal APIs: `kas_PrincipalCreate`, `kas_PrincipalDelete`, `kas_PrincipalGet`, iterator trio `kas_PrincipalGetBegin`/`Next`/`Done`, `kas_PrincipalKeySet`, `kas_PrincipalLockStatusGet`, `kas_PrincipalUnlock`, and `kas_PrincipalFieldsSet`.
- Server/crypto APIs: `kas_ServerStatsGet`, `kas_ServerDebugGet`, `kas_ServerRandomKeyGet`, `kas_StringToKey`, and `kas_KeyCheckSum`.

## Control Flow and State
Most exported functions validate arguments, call `ChooseValidServer`, issue a `ubik_KAM_*` RPC, translate/copy output structures, then return `rc` plus `afs_status_t`. `kas_ServerOpen` resolves an explicit server list into KAuth ports and creates a ubik client with `ka_AuthSpecificServersConn`. Principal iteration uses the common admin iterator with `ubik_KAM_ListEntry`, cached `kas_identity_t` slots, and a cleanup callback. Lock status and unlock use `ubik_CallIter` because the lock state is not synchronized like the normal Ubik database.

## Persistence and Side Effects
Principal create/delete, password/key set, unlock, and field-set operations mutate the KAS database or per-server lock state. Server open/close allocate and destroy ubik client state. Stats/debug/random-key/string-to-key/checksum operations are read-only from the database perspective, except for network/RPC activity.

## Dependencies and Integration Points
The implementation depends on `afs_kasAdmin.h`, admin internals, client admin cell handles, KAuth headers/RPC stubs, Ubik, RX, pthread-related build config, and utility address resolution. It is built with the KAuth support objects declared in `kas/Makefile.in`. cfg server setup uses KAS readiness/quorum indirectly, and client admin token creation supplies KAS tokens used by cell handles.

## Risks
The API permits either a cell handle or an explicit server handle; misuse is detected at runtime. `kas_ServerOpen` assumes the given server list belongs to the cell and notes this is not verified. Some public output string copies use `strcpy` into fixed-size fields. `kas_PrincipalUnlock` records `save_tst` but returns the final `tst`, so the first non-terminal failure may be lost. `kas_StringToKey` does not validate null inputs before passing them to KAuth. `kas_KeyCheckSum` does not check `key` or `cksumP` for null. Packed password-policy fields have 255-value limits and lock-time rounding that must match legacy KAS behavior.

## Test Signals
Tests should cover handle selection errors, server-list empty/too-long/name-resolution failures, create/delete/get flows against a disposable KAS database, iterator termination and cleanup, field updates for each optional setting, password-policy bounds, lock status across multiple servers, unlock partial failures, stats/debug structure copying, random key retrieval, and null-input robustness for utility functions.
