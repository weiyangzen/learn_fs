# sources/distributed-fs/glusterfs/xlators/protocol/auth/login/src/login.c

## Purpose
Implements login-based authentication for protocol/server. It authorizes either SSL-authenticated names through `auth.login.<brick>.ssl-allow` or username/password credentials through `auth.login.<brick>.allow` and `auth.login.<user>.password`, with optional strict rejection when credentials are missing or unmatched.

## Important APIs, Types, And Functions
`gf_auth()` is the module entry point. It reads `ssl-name`, `username`, `password`, `remote-subvolume`, `strict-auth-accept`, allow lists, and per-user password entries. It uses `fnmatch()` for allow-list patterns. `options[]` documents `auth.login.*.allow` and `auth.login.*.password`.

## Control Flow
SSL identity takes precedence and is treated as already authenticated. Non-SSL mode optionally enables strict auth, then requires username/password only when strict mode is set. The code builds an allow-list key for the remote brick, sets default reject for SSL or strict auth when a list exists, tokenizes the allow list by spaces/commas, and accepts on SSL name match or username match plus password match. Without SSL/strict auth, missing credentials or nonmatching allow list can leave the result as `AUTH_DONT_CARE`.

## State And Persistence
No persistent module state. Credentials and policy live in dictionaries supplied per call.

## Dependencies And Integration Points
Uses Gluster dict/data helpers, logging, `gf_asprintf`, `gf_strdup`, `fnmatch`, and the protocol server auth interface. The module is loaded from the auth directory built by its Makefile.

## Risks
The expression assigning username/password result is hard to read and depends on enum truth values. Non-strict non-SSL behavior intentionally allows unauthenticated clients to fall through as `AUTH_DONT_CARE` for compatibility. Password lookup is keyed by username, not brick+username, so per-user password namespace is global in the config dict. Logs can expose connecting usernames and allowed-user lists.

## Test Signals
Cover SSL names with and without `ssl-allow`, wildcard allow patterns, strict and non-strict missing credentials, correct and incorrect passwords, absent remote subvolume, multiple allow-list delimiters, no allow list, and password entries for users with overlapping names.
