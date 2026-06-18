# sources/distributed-fs/openafs/src/aklog/aklog.c

## Purpose
`aklog.c` implements the `aklog` command that obtains Kerberos 5 credentials for AFS cells and installs AFS token sets into the cache manager. It supports direct cell login, path-based discovery of AFS mount points, linked cells, optional Zephyr/host reporting, optional PAG creation, weak-DES compatibility knobs, and a keytab/client-principal impersonation path.

## Important APIs, types, and functions
The local `cellinfo_t` carries a cell and realm pair for command-line batching. Global state tracks flags such as `dflag`, `noauth`, `noprdb`, `linked`, `afssetpag`, `force`, `do524`, plus `keytab`, `client`, `zsublist`, `hostlist`, and `authedcells`.

Core functions are `main`, `auth_to_cell`, `auth_to_path`, `rxkad_get_ticket`, `rxkad_get_token`, `rxkad_build_native_token`, `rxkad_get_converted_token`, `get_credv5`, `get_credv5_akimpersonate`, `get_user_realm`, `get_cellconfig`, `get_afs_mountpoint`, `next_path`, `add_hosts`, and `redirect_errors`. The file also provides a compatibility `krb5_encrypt_tkt_part` when libkrb5 lacks it but exposes lower-level encoding/encryption calls.

## Control flow
`main` initializes Kerberos, OpenAFS error tables, linked lists, and command-line state. It parses mode switches into either a cells list or paths list. With no explicit targets it authenticates to the local cell and optionally reads `$HOME/.xlog` for extra cells. In cell mode it calls `auth_to_cell`; in path mode it calls `auth_to_path`, which walks each path component through `next_path`, detects mount points through `pioctl(VIOC_AFS_STAT_MT_PT)`, derives the cell from the mountpoint, and authenticates to each encountered cell.

`auth_to_cell` resolves the target cell with `afsconf_Open`, `afsconf_GetCellInfo`, and `afsconf_GetLocalCell`, records the cell in `authedcells` before network work to avoid repeated failures, builds a `ktc_setTokenData` jar, obtains an rxkad token, optionally resolves the PTS id, writes the ViceId into the token, sets the PAG flag, and finally calls `ktc_SetTokenEx`. `rxkad_get_ticket` tries service principals in a deliberate order: command-line realm, user realm, host-realm from cell DB server, fallback uppercase DNS domain, and `afs@REALM` only when the cell/realm match. `get_credv5` either pulls service creds from the default ccache or synthesizes a ticket from a keytab through `get_credv5_akimpersonate`.

## State and persistence
Persistent effects are mostly outside the process: it reads AFS client config, Kerberos ccaches, optional `krb5-weak.conf`, optional `.xlog`, and stores tokens in the cache manager through `ktc_SetTokenEx`. It may set a PAG via token metadata. Process-local state includes the Kerberos ccache handle `_krb425_ccache`, static principal cache in `get_user_realm`, linked lists of already attempted cells, Zephyr subscriptions, and host addresses.

## Dependencies and integration points
The file bridges Kerberos libraries, OpenAFS auth/token APIs, PTS lookup, Venus pioctls, `cellconfig`, `linked_list`, rxkad ticket/token helpers, and platform compatibility macros for MIT/Heimdal differences. It depends on `afs_realm_of_cell` from `krb_util.c` and the linked-list helpers in `linked_list.c`.

## Risks
There is extensive legacy string and buffer handling with fixed-size arrays; most copies use `strlcpy`/`strlcat`, but some paths still use `strcpy`, `strncpy`, and manual concatenation. `ll_string` allocations are never reclaimed before exit, which is acceptable for a command but important for reuse. `Parse`-like command handling is interleaved with side effects, so option ordering is observable. Keytab impersonation constructs tickets locally and is security-sensitive; lifetime bounds, enctype compatibility, and keytab principal validation are critical. The path walker uses static buffers and is not reentrant. The code intentionally supports weak DES modes for old deployments, which must stay opt-in.

## Test signals
Useful tests cover no-argument local-cell login, explicit `-cell/-k`, path traversal across nested mount points, linked-cell behavior, duplicate-token skip versus `-force`, `-noprdb`, `-noauth`, `-setpag`, missing/ambiguous cell config, DNS/realm fallback, MIT and Heimdal builds, no-524 and 524 builds, keytab impersonation with bounded and unlimited lifetimes, and malformed symlink/path loops.
