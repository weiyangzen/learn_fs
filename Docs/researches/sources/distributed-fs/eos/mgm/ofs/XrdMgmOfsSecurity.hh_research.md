# Research: sources/distributed-fs/eos/mgm/ofs/XrdMgmOfsSecurity.hh

## Purpose

`XrdMgmOfsSecurity.hh` centralizes small authorization and identity-environment macros used by the MGM OFS command implementations. It adapts XRootD authorization callbacks to EOS-style early returns and provides a helper for putting authenticated user/host information into `XrdOucEnv`.

## Important APIs, Types, and Functions

- `AUTHORIZE(usr, env, optype, action, pathp, edata)` calls `gOFS->mExtAuthz->Access()` when a client and external authorizer exist; on denial it writes an EOS error with `EACCES` and returns `SFS_ERROR`.
- `AUTHORIZE2(...)` applies `AUTHORIZE` to two path/env/operation tuples, used by two-path operations.
- `OOIDENTENV(usr, env)` stores `SEC_USER` and `SEC_HOST` in an `XrdOucEnv` when available.

## Control Flow

The macros are meant to be invoked early in high-level XRootD command wrappers, before the lower-level EOS operation runs. `AUTHORIZE` is an inline guard: success falls through, while failure returns immediately from the containing function. Because it is a macro, it depends on local variables such as `epname` and the caller's return type.

## State and Persistence Behavior

This file stores no state and performs no persistence. Its only side effect is to call the configured external authorizer and populate `XrdOucErrInfo` on denial. `OOIDENTENV` mutates an environment object with authentication details.

## Dependencies and Integration Points

The macros depend on `XrdAccAuthorize.hh`, global `gOFS`, `mExtAuthz`, XRootD access-operation constants such as `AOP_Stat`, and `XrdOucErrInfo`. They are used throughout command `.inc` files before identity mapping, namespace access checks, or metadata mutation.

## Risks and Edge Cases

- Macro early returns are easy to misuse in functions that do not return `int`/`SFS_ERROR`.
- Authorization operation types must match the real operation. Passing `AOP_Stat` for a mutation would weaken external authorization.
- `env` may be null depending on caller construction; authorizer implementations must tolerate the pointer contracts used here.
- Because the macro checks only external authorization, callers still need EOS ACL/POSIX/token checks.

## Test Signals

Tests should exercise allow/deny external authorizer paths for representative read, update, create, delete, chmod, and two-path operations; verify `EACCES` text is set on denial; and confirm operations still apply internal EOS ACL checks after external authorization succeeds.
