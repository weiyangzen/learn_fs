# sources/distributed-fs/ceph-client/include/linux/sizes.h

## Purpose

`sizes.h` defines standard binary size constants from bytes through terabytes for kernel code and device descriptions. It improves readability and avoids repeated literal hex constants.

## Important APIs, Types, And Functions

The header exports `SZ_1` through `SZ_512`, kilobyte constants from `SZ_1K` through `SZ_512K`, megabyte constants from `SZ_1M` through `SZ_512M`, gigabyte constants from `SZ_1G` through `SZ_512G`, and terabyte constants from `SZ_1T` through `SZ_128T`. Values larger than 32 bits use `_AC(..., ULL)` from `linux/const.h`.

## Control Flow

There is no control flow. The macros are compile-time constants for array sizing, resource lengths, alignment, register windows, memory-region descriptions, and limit checks.

## State And Persistence

No state is stored. The constants become compile-time numeric values in users.

## Dependencies And Integration Points

The only dependency is `linux/const.h`. Integration points include architecture memory maps, drivers, firmware resource parsing, allocator limits, block sizes, and MM code.

## Risks And Test Signals

Risks are type width mistakes if large constants are used in 32-bit contexts, accidental decimal-vs-binary assumptions, and overflow in expressions that combine size constants before widening. Test signals include build coverage on 32-bit and 64-bit targets, sparse/compiler overflow warnings, and resource-size tests using constants above 4 GiB.
