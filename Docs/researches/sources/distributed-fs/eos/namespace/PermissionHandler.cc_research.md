## sources/distributed-fs/eos/namespace/PermissionHandler.cc

Purpose: Implements utility functions for translating POSIX permission bits and `access(2)` request masks into EOS internal permission flags, plus filtering modes with `sys.mask`.

Important APIs and functions: `convertModetUser`, `convertModetGroup`, `convertModetOther`, `convertRequested`, `checkPerms`, `parseOctalMask`, and `filterWithSysMask`.

Control flow: conversion functions map read/write/execute or read/write/enter bits into `CANREAD`, `CANWRITE`, and `CANENTER`. `checkPerms` verifies every requested bit is present. `parseOctalMask` uses base-8 `stol` and rejects partial parses. `filterWithSysMask` applies `mode & mask` when parsing succeeds.

State and persistence: stateless; `sys.mask` itself is stored in metadata xattrs and interpreted here.

Dependencies and integration: depends on sys/stat/access constants and the header template overload for xattr maps. Used by file/container metadata access logic and callers applying xattr permission masks.

Risks: invalid masks are silently ignored, preserving original mode; this is permissive and should be documented in admin behavior. Internal flags are macros, not scoped enum values.

Test signals: cover all user/group/other bit combinations, requested `R_OK/W_OK/X_OK`, missing-bit denial, octal parsing failures, and `sys.mask` map filtering.
