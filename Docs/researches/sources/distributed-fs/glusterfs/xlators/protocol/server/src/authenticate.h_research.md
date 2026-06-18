# sources/distributed-fs/glusterfs/xlators/protocol/server/src/authenticate.h

## Purpose

`authenticate.h` declares the protocol/server authentication interface and the runtime handle used for dynamically loaded auth modules.

## Important APIs, types, and functions

`auth_result_t` has three possible outcomes: `AUTH_ACCEPT`, `AUTH_REJECT`, and `AUTH_DONT_CARE`. `auth_fn_t` is the module function signature, taking client input params and server config params. `auth_handle_t` stores the dynamic library handle, resolved `authenticate` function, and optional `given_opt` volume option array. The exported functions are `gf_auth_init()`, `gf_auth_fini()`, and `gf_authenticate()`.

## Control flow

The header defines the contract modules must satisfy: an auth shared object must expose `gf_auth` with the `auth_fn_t` signature and may expose `options` for validation. Server initialization loads modules and handshake calls the authenticate function set.

## State and persistence behavior

The only state shape declared here is `auth_handle_t`; actual ownership is in the auth modules dictionary managed by `authenticate.c`.

## Dependencies and integration points

The header includes dict, compat, list, xlator, stdio, and fnmatch related headers. It is consumed by `authenticate.c` and `server-handshake.c`.

## Risks and test signals

The ABI between auth modules and server is string/symbol based, so symbol names and function signatures must remain stable. Tests should compile a minimal auth module, validate `options`, and run `gf_authenticate()` against all three return values.
