
# sources/distributed-fs/openafs/src/uss/uss_kauth.h

Purpose: `uss_kauth.h` declares authentication-server operations for `uss`.

Important APIs: `uss_kauth_InitAccountCreator()` prepares administrator identity, `uss_kauth_AddUser()` creates a KAS user from a cleartext password, `uss_kauth_DelUser()` deletes one, `uss_kauth_CheckUserName()` validates and normalizes `uss_User`, and `uss_kauth_SetFields()` changes expiry/reuse/failure/lockout fields.

Control flow and integration: `uss.c` calls initialization before add/delete/bulk processing and uses `CheckUserName()` before persistent changes. Template grammar code can call `SetFields()` for security options.

State and persistence: implementation uses process-global KAS connection and global user/cell/admin state. Persistent effects are KAS database mutations unless `-skipauth` or dry-run is active.

Risks and test signals: API parameters are weakly typed strings, especially for security fields. Tests should verify validation before PTS/KAS mutations, skipauth behavior, and field-boundary handling.
