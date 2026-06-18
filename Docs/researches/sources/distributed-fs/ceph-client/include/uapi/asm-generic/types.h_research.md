# sources/distributed-fs/ceph-client/include/uapi/asm-generic/types.h

## Purpose
Selects the generic fixed-width integer ABI type model.

## Important APIs, Types, And Functions
This header exports the type definitions from `<asm-generic/int-ll64.h>`, including the `__s*` and `__u*` integer types used by UAPI headers.

## Control Flow
No branching beyond the include guard.

## State, Persistence, And Dependencies
No state. It establishes the integer widths used in all dependent user/kernel ABI structs.

## Integration Points
Included by architecture `asm/types.h` and widely by Linux UAPI headers, including signal, statfs, CXL, and DRM headers in this work item.

## Risks
Changing the included type model would alter ABI layout for nearly every structure using `__u64`, `__u32`, and related types.

## Test Signals
Compile-time type-width checks, UAPI structure size checks, libc header compatibility, and cross-architecture build tests.
