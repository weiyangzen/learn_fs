# sources/distributed-fs/openafs/src/kauth/kaport.h

## Purpose
Defines portable packing helpers for four one-byte KA password-control fields stored or transported as a single 32-bit value.

## Important APIs, Types, And Functions
The macros are `unpack_long(src, dst)` and `pack_long(src)`. They map bytes 0..3 to big-endian positions in an `afs_uint32`.

## Control Flow
There is no function control flow. Macro expansion performs direct byte extraction or composition.

## State And Persistence
The header stores no state. It defines the encoding used by `kaprocs.c` for `misc_auth_bytes` in set-fields/get-entry paths.

## Dependencies And Integration Points
It assumes `afs_int32`/`afs_uint32` are available and that 32-bit words are four bytes. It integrates with `kaentry.misc_auth_bytes` fields for expiration, reuse, attempts, and locktime.

## Risks And Test Signals
Risks are macro side effects if arguments have expressions with side effects and implicit assumptions about field order. Tests should cover round-trip packing/unpacking and compatibility with `kamSetFields` and `kamGetEntry`.
