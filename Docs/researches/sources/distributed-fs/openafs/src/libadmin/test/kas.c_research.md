# sources/distributed-fs/openafs/src/libadmin/test/kas.c

## Purpose

`kas.c` implements the KAS-related commands for the `afscp` libadmin test client. It is not the KAS library itself; it is a command-line adapter around `afs_kasAdmin` APIs. Each `DoKas*` function reads parsed `cmd_syndesc` parameters, maps them into libadmin structs such as `kas_identity_t`, calls a `kas_*` API through the global `cellHandle`, and prints returned structures for manual inspection.

## Important APIs, Types, and Functions

The file exposes command handlers for principal lifecycle (`DoKasPrincipalCreate`, `DoKasPrincipalDelete`, `DoKasPrincipalGet`, `DoKasPrincipalList`), credential/key management (`DoKasPrincipalKeySet`, `DoKasPrincipalLockStatusGet`, `DoKasPrincipalUnlock`, `DoKasPrincipalFieldsSet`), and server inspection (`DoKasServerStatsGet`, `DoKasServerDebugGet`, `DoKasServerRandomKeyGet`). `SetupKasAdminCmd` registers the user-facing command names and their parameters with the AFS command package.

Important local helpers are `GetIntFromString`, `Print_kas_principalEntry_p`, `Print_kas_serverStats_p`, and `Print_kas_serverDebugInfo_p`. They convert text arguments and serialize libadmin return structures to stdout. The command handlers rely on `ERR_EXT` and `ERR_ST_EXT` from `common.h` for fatal error reporting.

## Control Flow

All KAS command handlers first reject `existing_tokens`, because the test client records that tokens came from `afsclient_TokenGetExisting`, which this wrapper treats as incompatible with KAS operations. Principal commands populate a `kas_identity_t` from `-principal` and optional `-instance`, call the matching `kas_Principal*` API, and return zero on success. List commands follow the begin/next/done iterator convention and treat `ADMITERATORDONE` as normal termination. Server stats/debug commands open a KAS server handle with `kas_ServerOpen`, query it, print the result, and close the handle.

`DoKasPrincipalFieldsSet` is the densest path. It parses mutually exclusive flag pairs into optional pointer arguments for `kas_PrincipalFieldsSet`. The API contract is pointer-based: a null pointer means no update, and a non-null pointer carries the new setting.

## State and Persistence Behavior

This test wrapper has no local persistence. It mutates remote KAS database state through libadmin calls: creating/deleting principals, setting keys, unlocking accounts, and changing account policy fields. Server stats/debug/random-key commands are read-only except for the remote RPC work they trigger.

## Dependencies and Integration Points

The file includes `kas.h`, which pulls in OpenAFS admin, KAS, util, client, RX, and command headers. Runtime integration depends on globals from the larger test program: `cellHandle` and `existing_tokens`. The registered commands become part of `afscp` via `SetupKasAdminCmd`.

## Risks and Edge Cases

Several command-adapter defects are visible. `DoKasPrincipalDelete` and `DoKasPrincipalGet` copy `as->parms[PRINCIPAL]` into `user.instance` when `-instance` is present, so instance-qualified operations can target the wrong identity. `DoKasPrincipalFieldsSet` has repeated conflict-check mistakes: the `-noencrypt` and `-nochangepassword` paths check `have_tgs` instead of the corresponding setting, and the second reuse-password block tests `REUSEPASSWORD` instead of `NOREUSEPASSWORD`, making `-noreusepassword` unreachable and making `-reusepassword` immediately conflict with itself. The code uses `strcpy` into fixed-size KAS fields, so it relies on upstream command/API limits rather than local bounds checks.

`GetIntFromString` returns from `ERR_EXT` paths only if the macro exits nonlocally; as plain C it has no final return after the error path. Numeric parsing uses `strtoul` into `int`, so negative and overflow handling is weak.

## Test Signals

Useful tests are command-level integration tests that create principals with and without instances, list them, fetch them, set keys, and exercise each mutually exclusive field pair. A focused regression should verify that `-instance` reaches `kas_identity_t.instance` and that `-noreusepassword`, `-noencrypt`, and `-nochangepassword` reject only their true opposites. Manual server tests can validate iterator completion on `KasPrincipalList` and handle closure for server stats/debug queries.
