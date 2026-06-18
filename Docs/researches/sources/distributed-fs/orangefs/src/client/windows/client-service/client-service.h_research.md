# sources/distributed-fs/orangefs/src/client/windows/client-service/client-service.h

## Purpose
This header defines shared Windows client-service configuration constants, the central `ORANGEFS_OPTIONS` struct, and logging/error-reporting declarations.

## Important APIs, types, and functions
- Constants: `STR_BUF_LEN`, user modes (`USER_MODE_NONE`, `LIST`, `CERT`, `LDAP`, `SERVER`), and security modes (`DEFAULT`, `KEY`, `CERT`).
- `ORANGEFS_OPTIONS`: mount point, thread count, new file/dir permissions, write-time behavior, debug settings, user/security mode, security timeout, key/private-key/certificate/CA paths.
- Functions/macros: `client_debug`, `report_error`, `_report_error`.

## Control flow
Configuration parsing fills an `ORANGEFS_OPTIONS`; service startup passes it into Dokan loop and other subsystems. Credential code reads security fields from global options. Debug helpers route messages to the configured logging mechanism.

## State and persistence behavior
This header defines the in-memory service options shape. Persistent values come from `orangefs.cfg` or environment-selected config files parsed by `config.c`.

## Dependencies and integration points
It includes `wincommon.h` for Windows types and is included by config, credential, certificate, Dokan, and other service files. The struct is an integration point between config parsing, credential creation, filesystem operations, and Dokan mount setup.

## Risks and edge cases
- Some modes are defined here but disabled or partially unsupported in `config.c`, so consumers must not assume every enum value is reachable.
- `private_key` is a `void *`, hiding OpenSSL ownership and type from the struct definition.
- Fixed `MAX_PATH` and `STR_BUF_LEN` arrays limit path and debug-mask length.
- No defaults are encoded in the type; callers must remember to call `set_defaults`/`get_config`.

## Test signals
Compile all service modules after changes to `ORANGEFS_OPTIONS`, validate config defaults populate every field consumed by Dokan/cert/cred code, and test unsupported mode values are rejected or handled consistently.
