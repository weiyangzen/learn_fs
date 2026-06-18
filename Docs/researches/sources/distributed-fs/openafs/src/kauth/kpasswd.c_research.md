# sources/distributed-fs/openafs/src/kauth/kpasswd.c

## Purpose
Implements the `kpasswd` command for changing a user's KA password. It authenticates to the maintenance service with the old password, optionally validates the new password through `kpwvalid`, and submits a password-change RPC.

## Important APIs, Types, And Functions
Important functions are `main`, `getpipepass`, `read_pass`, optional `timedout`, and `CommandProc`. It uses `kkids` helpers, `ka_StringToKey`, `DES_string_to_key`, `ka_GetAdminToken`, `ka_AuthServerConn`, and `ka_ChangePassword`.

## Control Flow
`main` initializes the optional validator child and command syntax. `CommandProc` scrubs argv, initializes cell and Rx state, parses cell/server/principal/password/newpassword options, derives the local username if needed, reads old and new passwords from stdin or terminal, sends the old password to the validator, loops until the validator accepts an interactive new password, optionally truncates to eight characters, derives both AFS and MIT DES keys, gets a short-lived admin token with fallback between string-to-key styles and first-eight-character compatibility, connects to the maintenance service, calls `ka_ChangePassword`, scrubs keys/passwords, destroys the Ubik client, finalizes Rx, terminates the child, and exits.

## State And Persistence
Persistent state changes only if the server accepts the password change in the KA database. Runtime state includes password/key buffers, a possible child validator process, a Ubik client connection, and token material. Password buffers are explicitly zeroed in many paths.

## Dependencies And Integration Points
It depends on command parsing, hcrypto DES/UI helpers, kauth client APIs, `kkids.c`, ktc tokens, Ubik client connections, and platform-specific username discovery on Windows.

## Risks And Test Signals
Risks include password exposure before argv scrubbing, numerous direct `exit` paths, legacy DES string-to-key ambiguity, fallback behavior that may surprise users, validator child reliability, optional password truncation, and partial cleanup on early failures. Test signals include interactive and pipe password changes, explicit cell/server paths, wrong old password, AFS and MIT string-to-key fallback, validator accept/reject, mismatch handling, no-change paths, connection cleanup, and server-side reuse/min-hours rejection.
