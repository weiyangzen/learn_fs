# sources/distributed-fs/openafs/src/afs/afs_osi_pag.c

## Purpose
`afs_osi_pag.c` implements Process Authentication Group generation, group encoding/decoding, credential installation, and request initialization. PAGs provide an authentication-token handle that is more specific than Unix uid, reducing token sharing between unrelated sessions with the same uid.

## Important APIs, types, and functions
Global PAG state is `pag_epoch`, `pagCounter`, `afs_pag_sleepcnt`, and `afs_pag_timewarn`. PAG generation APIs include `afs_genpag`, internal `genpagval`, `getpag`, `afs_pag_sleep`, and `afs_pag_wait`. Credential APIs include platform-specific `afs_setpag`, UKERNEL `afs_setpag_val`, `AddPag`, `PagInCred`, `afs_get_pag_from_groups`, `afs_get_groups_from_pag`, and `afs_IsPagId`. Request helpers are `afs_InitReq`, `afs_CreateReq`, and `afs_DestroyReq`.

## Control flow
Kernel PAG values normally encode an ASCII `A` in the high byte and a 24-bit counter, with Linux adding `pag_epoch` so PAGs remain unique after module reloads for roughly the wrap window. `afs_pag_wait` throttles non-superuser PAG creation if elapsed time since epoch is less than the counter, enforcing an average one PAG per second to reduce wraparound risk. `afs_setpag` generates a PAG and delegates to platform `AddPag`/`setpag` logic to clone and update credentials.

PAGs are represented in Unix group lists by one or two special groups near `0x3f00`. `afs_get_groups_from_pag` encodes a PAG into group ids, and `afs_get_pag_from_groups` reverses it, validating kernel PAG ids outside UKERNEL. `PagInCred` extracts the PAG from Linux keyrings, AIX kernel credential PAGs, or encoded groups depending on platform.

`afs_InitReq` initializes a `vrequest`, aborts during shutdown, lets Linux NFS translator code override request setup, sets `av->uid` to the PAG if present, otherwise uses a real uid or nobody fallback. `afs_CreateReq` allocates a small-space request and `afs_DestroyReq` frees it.

## State and persistence behavior
PAG state is runtime-only and resets with cache shutdown or module reload. Credentials carry encoded PAG groups or keyring/AIX PAG metadata. `vrequest` objects are transient per operation.

## Dependencies and integration points
The file depends on platform credential cloning/group APIs, Linux keyring helpers, NFS translator request handling, user/token tables via `vrequest->uid`, OSI wait/sleep, and small-space allocation. It is central to pioctl, NFS translator, token lookup, and request authorization.

## Risks and edge cases
PAG wraparound is security-sensitive; throttling protects non-superusers but clock rollback disables throttling with a warning. Group-list layouts differ by platform and one-group builds. Some platforms cannot infer PAGs on newer Darwin variants. `PagInCred` returns `NOPAG` for the global AFS credential and null credentials. Request allocation requires a non-null credential and can fail with `EINVAL` or `ENOMEM`.

## Test signals
Test PAG creation throttling, clock rollback behavior, group encode/decode round trips, Linux keyring fallback, request uid selection with and without PAGs, shutdown rejection, UKERNEL explicit PAG set/get, and NFS translator request initialization.
