# sources/distributed-fs/coda/coda-src/auth2/auth2.c

Purpose: Coda auth2 server daemon. It authenticates users against the password database, issues Coda tokens, and exposes RPCs for password/user administration.

Important APIs/functions: Startup helpers `ReadConfigFile`, `InitGlobals`, `ReopenLog`, `InitSignals`, `InitRPC`, `CheckTokenKey`; RPC/auth callbacks `GetKeys`, `LogFailures`; service routines `S_AuthNewConn`, `S_AuthQuit`, `S_AuthGetTokens`, `S_AuthChangePasswd`, `S_AuthNewUser`, `S_AuthDeleteUser`, `S_AuthChangeUser`, `S_AuthNameToId`; helper `GetViceId`.

Control flow: Main reads server config, sets token-key path, changes to auth2 directory, daemonizes unless debugging, initializes logging/signals/RPC/AL/password support, then loops on `RPC2_GetRequest`. It rejects unauthenticated requests, dispatches generated RPC handlers, and handles RPC errors. `GetKeys` accepts only `AUTH_METHOD_CODAUSERNAME` and verifies the identity maps to a Vice ID. Token issuance refreshes the auth2 key when the key file mtime changes and creates a 25-hour token.

State and persistence: Reads `db/auth2.tk`, password files via pwsupport, `/vice/db/scm` and `/vice/hostname` to decide read-only mode, writes `AuthLog` and `pid`, and stores per-connection `UserInfo` in a fixed ring of 10 client slots. Mutating RPCs update password/user database through pwsupport.

Dependencies and integration: Uses RPC2/LWP, generated auth2 RPC stubs, AL/PRS identity lookup, pwsupport, `codatoken`, Coda config and service lookup. Server-side deletion checks administrator status through pwsupport helpers.

Risks and test signals: `readoneline` checks `buf[len] == '\n'` instead of `buf[len - 1]`, so newline stripping is wrong. Client slot eviction unbinds older connections in a ring. `S_AuthNewUser` and `S_AuthChangeUser` do not check `CheckOnly` in this file. Token key reload is mtime-based and fatal if the file is missing. Sensitive keys and passwords are not explicitly wiped.
