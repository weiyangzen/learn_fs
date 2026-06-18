# sources/distributed-fs/coda/coda-src/auth2/cpasswd.c

## Purpose
Interactive `cpasswd` client for changing a Coda password through auth2 servers. It resolves the target `user[@realm]`, prompts for the old and new passwords, applies local strength checks, and calls the auth RPC helper to update `auth2.pw`.

## APIs, Types, and Functions
The only function is `main()`. It uses `SplitRealmFromName()`, `codaconf_init()`, `CODACONF_STR()`, `U_InitRPC()`, `U_GetAuthServers()`, `U_ChangePassword()`, `RPC2_freeaddrinfo()`, `getpwuid()`, `geteuid()`, and `getpass()`. RPC/auth return codes include `AUTH_SUCCESS`, `AUTH_DENIED`, `AUTH_BADKEY`, `AUTH_READONLY`, `AUTH_FAILED`, `RPC2_DEAD`, and `RPC2_NOTAUTHENTICATED`.

## Control Flow, State, and Persistence
Command parsing optionally accepts `-h SCM-host-name`, then extracts username and realm or falls back to the effective uid's passwd entry. It initializes `venus.conf` and `auth2.conf`, prompts once for the old password, then retries weak new passwords up to two times before accepting the user's insistence. After confirmation it fetches auth servers for the realm/host, sends the change request, prints a human-readable result, and exits. Persistent state is modified remotely by the auth server; this program only keeps stack password buffers.

## Dependencies and Integration
Integrates the auth2 user tools with RPC2/LWP, Coda config, realm parsing, and auth-server discovery. It depends on auth2 client helper functions and server-side `PWChangePasswd()` behavior in `pwsupport.c`.

## Risks and Test Signals
Risks include fixed 128-byte password buffers, `strncpy()` without explicit terminator on exact-size input, `getpass()` limitations, username length capped at 20, weak local policy, and returning success even for failed auth outcomes because it always exits `EXIT_SUCCESS` after the switch. Test signals are prompt/validation behavior, realm fallback, auth return-code mapping, and server-side password-file update.
