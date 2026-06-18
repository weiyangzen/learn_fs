# sources/distributed-fs/ceph-client/tools/include/nolibc/byteswap.h

## Purpose
Provides glibc-like byte-swap macro names for nolibc programs.

## APIs, Types, and Functions
Defines `bswap_16`, `bswap_32`, and `bswap_64` as wrappers around Linux `__swab16`, `__swab32`, and `__swab64`.

## Control Flow, State, and Persistence
There is no runtime state; macros expand into constant or inline byte-swap operations. Control flow is purely expression evaluation by callers.

## Dependencies and Integration
Depends on `stdint.h` for fixed-width types and `<linux/swab.h>` for implementation. It integrates with tools code expecting `<byteswap.h>` style names under the nolibc include surface.

## Risks and Test Signals
Risks are multiple evaluation if callers pass expressions with side effects and divergence from libc feature macros. Test signals are compile-time constant swaps, runtime round trips for all widths, and builds on big- and little-endian targets.
