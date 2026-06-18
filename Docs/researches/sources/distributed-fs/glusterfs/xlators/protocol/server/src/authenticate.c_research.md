# sources/distributed-fs/glusterfs/xlators/protocol/server/src/authenticate.c

## Purpose

`authenticate.c` implements protocol/server authentication module lifecycle and evaluation. It dynamically loads configured auth modules from `LIBDIR`, records their `gf_auth` functions and optional volume option definitions, validates their options, runs all modules against a client handshake, and unloads modules during cleanup.

## Important APIs, types, and functions

`gf_auth_init(xlator_t *xl, dict_t *auth_modules)` iterates an auth-module dictionary through `init()`, then validates each module's options with `_gf_auth_option_validate()`. `init()` maps legacy `auth.ip` to `addr`, builds `LIBDIR/<key>.so`, opens it with `dlopen()`, resolves `gf_auth`, optionally resolves `options`, stores an `auth_handle_t` in the dictionary, and records errors through the caller-supplied integer. `gf_authenticate()` evaluates loaded modules using `gf_auth_one_method()`. It returns accept if at least one module accepts and none reject, rejects immediately on `AUTH_REJECT`, and rejects if every module returns `AUTH_DONT_CARE`. `gf_auth_fini()` closes loaded module handles.

## Control flow

During server initialization, configured auth keys are converted to loaded module handles. During `SETVOLUME`, server handshake passes client input params and volume config params to `gf_authenticate()`. Each module gets the same input/config dictionaries. A rejecting module terminates the loop; accepting modules set the result only if no earlier reject occurred; uninterested modules leave the result unchanged. If no module accepts, the connection is refused.

## State and persistence behavior

Loaded module state is stored in the `auth_modules` dict as dynamically allocated `auth_handle_t` values. The dynamic library handles stay open until `gf_auth_fini()`. Option validation state is also appended to the xlator's `volume_options` list, with duplicate `given_opt` pointers avoided by scanning the list.

## Dependencies and integration points

This file depends on `dlopen`, `dlsym`, `dlclose`, dict iteration, xlator option validation, GlusterFS allocation helpers, and message IDs from `server-messages.h`. It integrates directly with `server-handshake.c`, which calls `auth_set_username_passwd()` first and then `gf_authenticate()`.

## Risks and test signals

Authentication is sensitive to module path correctness, dictionary key names, and module return semantics. A malformed module without `gf_auth` causes init failure. If every module is uninterested, clients are rejected, which is secure but can surprise misconfigured volumes. Tests should cover legacy `auth.ip`, missing modules, missing `gf_auth`, option validation failure, accept/reject/dont-care combinations, `ssl-name` handling via params, and cleanup after partial init failure.
