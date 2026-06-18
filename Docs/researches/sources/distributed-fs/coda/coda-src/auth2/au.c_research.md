# sources/distributed-fs/coda/coda-src/auth2/au.c

Purpose: Interactive administrative auth client for changing passwords, changing user records, creating users, and deleting users via the auth2 server.

Important APIs/functions: `main`, `SetGlobals`, and `GetVid`. It calls generated RPC stubs such as `AuthChangePasswd`, `AuthDeleteUser`, `AuthChangeUser`, `AuthNewUser`, and `AuthNameToId`.

Control flow: Parses flags (`-x`, `-h`, `-p`) and one command (`cp`, `cu`, `nu`, `du`), initializes RPC, prompts for administrator Vice name/password, resolves realm/auth servers, binds, then prompts for target user data and invokes the selected RPC.

State and persistence: Local state is input buffers and the RPC binding `AuthCid`. Persistent changes happen on the auth server's password/user database.

Dependencies and integration: Uses `auser` client library, generated `auth2.h`, RPC2, realm parsing, `codaconf`, and PRS naming constants.

Risks and test signals: Password and metadata prompts use fixed-size buffers. `AuthPortal` is parsed but not used in current server resolution path. `strncpy` into RPC key may omit NUL but keys are fixed binary buffers. It relies on server-side authorization for privileged changes.
