# sources/distributed-fs/openafs/src/WINNT/afsd/fs.h

## Purpose

`fs.h` is a minimal include guard and shared declaration header for the Windows `fs` command family. It exposes `Die(int code, char *filename)` to translation units that need the command's common error-reporting routine.

## Important APIs, Types, and Functions

The only API is `Die()`. In this source subset, `fs.c` primarily uses `fs_Die()` from `fs_utils.h`, but the header remains part of the command-line utility interface and may support other build variants or older users.

## Control Flow

There is no runtime control flow in the header. Including it provides the prototype before command handlers call error-reporting code.

## State and Persistence Behavior

The header declares no state and has no persistence behavior.

## Dependencies and Integration Points

It depends only on C linkage compatibility from the including compilation unit. It is included by `fs.c` alongside `fs_utils.h`, `fs_acl.h`, command parsing, AFSD, and pioctl headers.

## Risks and Edge Cases

The risk is interface drift: if `Die()` is removed, renamed, or made incompatible while some platform-specific object still expects this prototype, builds can fail or silently pick an unintended declaration. The sparse header also suggests legacy API overlap with `fs_Die()`.

## Test Signals

Build all Windows and non-Windows variants that include `fs.h`, and check for warnings about missing or conflicting `Die()` declarations.
