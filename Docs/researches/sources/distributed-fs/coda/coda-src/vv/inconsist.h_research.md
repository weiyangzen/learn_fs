# sources/distributed-fs/coda/coda-src/vv/inconsist.h

## Purpose

`inconsist.h` declares Coda version-vector consistency APIs and flag macros.

## Important APIs, Types, and Functions

It defines `VV_Cmp_Result` values `VV_EQ`, `VV_DOM`, `VV_SUB`, and `VV_INC`. It defines flags `VV_INCON`, `VV_LOCAL`, `VV_BARREN`, and `VV_COP2PENDING`, plus macros to test, set, and clear each flag. `SID_EQ()` compares `ViceStoreId` values. It declares `NullSid`, comparison/check APIs, vector arithmetic/init/invalidate/max APIs, and print helpers.

## Control Flow

There is no runtime control flow in the header. Macros directly mutate the `Flags` member of a passed version-vector lvalue.

## State and Persistence Behavior

The macros mutate caller-owned `ViceVersionVector` values. No persistence exists in the header.

## Dependencies and Integration Points

It includes `vice.h` and `vcrcommon.h` for Coda version-vector and store-id types and is wrapped for C++ linkage compatibility.

## Risks and Test Signals

Macros evaluate their argument once syntactically as `(vv).Flags`, so callers must pass lvalues and understand mutation. Flag values are ABI-visible. Tests should compile from C and C++, verify flag operations, `SID_EQ`, and API linkage against `inconsist.cc`.
