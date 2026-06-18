# sources/distributed-fs/coda/coda-src/vicedep/voltypes.h

## Purpose

`sources/distributed-fs/coda/coda-src/vicedep/voltypes.h` provides small fixed-width type aliases and boolean/null compatibility definitions used by the Coda volume and server code.

## Important APIs, Types, and Functions

It defines `NULL`, `TRUE`, and `FALSE` if absent, includes RPC2 and `stdint.h`, and aliases `bit32`, `bit16`, `byte`, `Device`, `Inode`, and `Error`.

## Control Flow

There is no runtime control flow.

## State and Persistence Behavior

The header owns no state, but its aliases are used in persistent volume/vnode structures and inode identifiers. `Device`, `Inode`, and `Error` are 32-bit values here, which constrains ABI and on-disk/RVM layout expectations.

## Dependencies and Integration Points

It is included throughout `vicedep`, `vice`, and `vol` code to stabilize integer types across platforms and generated RPC2 bindings.

## Risks and Edge Cases

The 32-bit `Device` and `Inode` aliases can be risky on platforms with wider native device or inode numbers. Redefining `NULL`/boolean constants may conflict with C++ or modern headers if include ordering changes.

## Test Signals

Compile on 32-bit and 64-bit platforms; add layout/size assertions for persistent structures that use these aliases; run inode/device integration tests on filesystems with large inode numbers if supported.
