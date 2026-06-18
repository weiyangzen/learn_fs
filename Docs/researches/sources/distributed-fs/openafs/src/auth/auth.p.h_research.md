# sources/distributed-fs/openafs/src/auth/auth.p.h

## Purpose
`auth.p.h` is the template portion for generated `auth.h`. It defines token-related public types and ktc token APIs.

## Important APIs, types, and functions
It defines `AUTH_SUPERUSER` as `"afs"` and `struct ktc_token`, containing token start/end times, session key, kvno, ticket length, and ticket bytes. It declares `ktc_SetToken`, `ktc_GetToken`, extended token-set APIs (`ktc_SetTokenEx`, `ktc_GetTokenEx`, `ktc_ListTokensEx`), legacy list/forget APIs, `ktc_curpag`, and optionally `ktc_newpag`. It defines token flags `AFS_SETTOK_SETPAG`, `AFS_SETTOK_LOGON`, and Windows `PIOCTL_LOGON`.

## Control flow
No runtime control flow exists. The file is combined with generated error-table output to produce a public header.

## State and persistence
The types describe tokens stored in or retrieved from the cache manager/PAG. The header itself has no state.

## Dependencies and integration points
It includes `rx/rxkad.h` for ticket constants and encryption key types. `aklog.c`, `klog.c`, auth code, and cache-manager token code rely on these declarations.

## Risks
`struct ktc_token` contains legacy fixed-size buffers and an explicitly unaligned `short kvno`; ABI/layout compatibility is important. Ticket length must be validated by implementations before copying into `ticket`. Generated-header flow means direct edits to generated `auth.h` would be lost.

## Test signals
ABI/layout checks, token set/get round trips, extended token-set APIs, PAG behavior, Windows logon flags, and generated header regeneration from `ktc_errors.et`.
