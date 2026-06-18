# sources/distributed-fs/orangefs/src/client/windows/client-service/config.h

## Purpose
This header declares the config parser interface and internal data structures for Windows client-service configuration keywords and configured user entries.

## Important APIs, types, and functions
`CONFIG_USER_ENTRY` stores a username, PVFS UID/GID, and quicklist link. `CONFIG_KEYWORD_DEF` stores a keyword string, min/max argument counts, and callback pointer. Public functions are `get_config` and `add_users`.

## Control flow
Service startup calls `get_config` to fill `ORANGEFS_OPTIONS`, then calls `add_users` to transfer configured list-mode users into the credential cache.

## State and persistence behavior
The declared types support process-local parsed state only. Persistent data remains in the external config file.

## Dependencies and integration points
The header depends on OrangeFS types, quicklist, and `client-service.h`. It binds the parser to the service options struct and user-cache credential initialization path.

## Risks and edge cases
The callback type exposes parser internals and mutable `char **args` to callbacks. Fixed `STR_BUF_LEN` in `CONFIG_USER_ENTRY` caps usernames. The header does not expose `set_defaults`, so tests or alternate startup paths cannot call it directly without reaching into `config.c`.

## Test signals
Compile parser callbacks against this signature, run startup tests that call `get_config`/`add_users`, and validate long usernames are truncated safely and consistently.
