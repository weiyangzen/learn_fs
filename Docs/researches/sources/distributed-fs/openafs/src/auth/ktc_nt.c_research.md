# sources/distributed-fs/openafs/src/auth/ktc_nt.c

## Purpose
Windows implementation of OpenAFS token cache APIs. It uses SMB pioctls plus a DCE/RPC side channel so session keys are not sent in cleartext through SMB on NT-class systems.

## Important APIs, Types, and Functions
Exports Windows versions of `ktc_SetToken`, `ktc_GetToken`, `ktc_GetTokenEx`, `ktc_SetTokenEx`, `ktc_ListTokens`, `ktc_ListTokensEx`, `ktc_ForgetToken`, `ktc_ForgetAllTokens`, and `ktc_OldPioctl`. Local helpers include `send_key`, `receive_key`, `getservername`, MIDL allocators, and local-token cache functions.

## Control Flow
For `afs` service tokens, `ktc_SetToken` builds an old token buffer with a zeroed session key, sends the real session key through authenticated RPC keyed by a generated UUID, then calls `VIOCSETTOK` while holding a named mutex. `ktc_GetToken` performs `VIOCNEWGETTOK`, then retrieves the session key through RPC using the UUID. Non-`afs` service tokens use the local in-process cache.

## State and Persistence
Maintains `local_tokens[MAXLOCALTOKENS]`, global RPC error text, registry-derived gateway configuration, and named mutexes `Global\AFS_KTC_Mutex`/`AFS_KTC_Mutex`. Persistent token state lives in the Windows AFS cache manager, not this file.

## Dependencies and Integration Points
Depends on Windows registry APIs, RPC runtime, generated `afsrpc` stubs, SMB pioctl headers, `ViceIoctl`, token XDR helpers, and OpenAFS global mutexes. Environment variables `AFS_RPC_ENCRYPT` and `AFS_RPC_PROTSEQ` alter RPC security/transport.

## Risks and Test Signals
`ktc_SetTokenEx` and new `VIOC_GETTOK2` paths are explicitly unimplemented and fall back or fail. `ktc_GetTokenEx` calls `strcpy(server.cell, cellName)` even though the API permits NULL cell names, a null-pointer risk. Tests should cover RPC unavailable paths, mutex acquisition failure, buffer bound checks, integrated logon `smbname`, local token zeroization on forget, and fallback behavior for Ex APIs.
