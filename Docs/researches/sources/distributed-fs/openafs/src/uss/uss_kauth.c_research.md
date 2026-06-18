
# sources/distributed-fs/openafs/src/uss/uss_kauth.c

Purpose: `uss_kauth.c` integrates `uss` with the legacy AFS Authentication Server. It identifies the administrator, obtains admin tokens, creates/deletes user auth entries, validates usernames using KAS parsing rules, and sets password/security fields.

Important APIs and state: exported `uconn_kauthP` is the Ubik client for KAS. `uss_kauth_InitAccountCreator()` sets `uss_AccountCreator` and `CreatorInstance` from `-admin` or local passwd data. `InitThisModule()` obtains or prompts for an admin token, handles piped passwords, establishes `ka_AuthServerConn()`, and may stage a local token for later unlog. `uss_kauth_AddUser()`, `uss_kauth_DelUser()`, `uss_kauth_CheckUserName()`, and `uss_kauth_SetFields()` perform the account operations.

Control flow: operations short-circuit successfully when `uss_SkipKaserver` is set. Otherwise they lazily initialize KAS state. Add converts the cleartext password to a key and calls `ubik_KAM_CreateUser()`. Delete calls `ubik_KAM_DeleteUser()` and treats missing users as success. Username validation parses principal/instance/cell, rejects instance/cell/colon, enforces the eight-character legacy limit, and rewrites `uss_User` to the parsed principal. `SetFields()` encodes password expiry, reuse policy, login failure count, and lockout duration into spare auth bytes before `ubik_KAM_SetFields()`.

State and persistence: module state includes `initDone`, parsed user principal buffers, creator instance, `Pipe`, and `doUnlog`. Persistent effects are KAS database entries, token cache changes, and auth field updates.

Dependencies and integration: uses KAS/kauth libraries, Ubik, token cache APIs, passwd lookups, global command flags, and `uss_common` identity buffers.

Risks: cleartext passwords are held in stack buffers and may be read from stdin. Several initialization failures call `exit(code)` instead of returning. The code preserves legacy DES/KAS limits and truncation behavior. `strncpy(longPassBuff, getpipepass(), sizeof(longPassBuff))` may omit explicit NUL if input fills the buffer. Test signals should include skipauth, pipe password, long admin password fallback, invalid username forms, dry-run KAS add/delete/setfields, and token cleanup.
