# sources/distributed-fs/openafs/src/auth/ktc.c

## Purpose
Implements Unix-like OpenAFS token cache APIs. It bridges application-facing `ktc_*` calls to kernel/cache-manager pioctls, a small local token cache for non-`afs` services, optional Kerberos ticket-file compatibility, and new XDR token-set pioctls.

## Important APIs, Types, and Functions
Primary APIs are `ktc_SetToken`, `ktc_SetTokenEx`, `ktc_GetToken`, `ktc_GetTokenEx`, `ktc_ListTokens`, `ktc_ListTokensEx`, `ktc_ForgetToken`, `ktc_ForgetAllTokens`, `ktc_curpag`, `ktc_newpag`, `ktc_tkt_string`, and `ktc_set_tkt_string`. Static `SetToken`, `GetToken`, and `ForgetAll` encode/decode old pioctl buffers. Under `AFS_KERBEROS_ENV`, `afs_tf_*` functions implement ticket-file I/O.

## Control Flow
Set-token operations first optionally write Kerberos ticket-file credentials, then encode a `VIOCSETTOK` buffer for old pioctl or an XDR `VIOC_SETTOK2` buffer for the new API. If new pioctls return `EINVAL`, code extracts rxkad data and falls back to old pioctls. Get/list paths similarly prefer new pioctls where available, then iterate old token slots or ticket-file/local-token slots.

## State and Persistence
Runtime state includes `local_tokens[MAXLOCALTOKENS]`, cached local cell `lcell`, the global `krb_ticket_string`, and ticket-file read buffering. Persistent state can be kernel/cache-manager tokens, optional Kerberos ticket files such as `/tmp/tkt<uid>`, and environment variables adjusted by `ktc_newpag`.

## Dependencies and Integration Points
Uses `pioctl`/`call_syscall`, `ViceIoctl`, `venus` ioctl constants, `token.c` XDR helpers, `rxkad` token structures, PAG/keyring behavior on Linux, `afsconf_Open` for local cell discovery, and global auth mutexes.

## Risks and Test Signals
PIOCTL buffer parsing is size-sensitive and partly trusts kernel output. Ticket-file code has legacy locking, uid, and truncation semantics. The local non-AFS cache holds only four entries. Tests should exercise new-pioctl fallback, large ticket rejection, PAG propagation, ticket-file duplicate replacement, token listing index transitions, and error mapping for `ESRCH`, `EINVAL`, `EIO`, and `EDOM`.
