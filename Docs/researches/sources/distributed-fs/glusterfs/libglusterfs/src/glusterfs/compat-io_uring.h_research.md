# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/compat-io_uring.h

## Purpose
`compat-io_uring.h` provides compile-time compatibility definitions for `io_uring` setup flags, feature bits, and operation codes that may be missing from older kernel headers.

## Important APIs, Types, and Functions
- Includes `<linux/io_uring.h>`.
- Defines missing `IORING_SETUP_*` flags through `IORING_SETUP_R_DISABLED`.
- Defines missing `IORING_FEAT_*` feature bits through `IORING_FEAT_NATIVE_WORKERS`.
- Defines missing `IORING_OP_*` opcodes from `NOP` through `UNLINKAT`.

## Control Flow
The header uses `#ifndef` guards around each macro. If the system kernel headers already define a value, that definition is used; otherwise Gluster supplies the expected numeric value.

## State and Persistence
No runtime state. It affects compile-time availability of constants used by `gf-io-uring.c`.

## Dependencies and Integration Points
Directly integrated with `gf-io-uring.c` setup, feature logging, opcode probing, and SQE construction. It shields Gluster from older development headers while still requiring runtime kernel support.

## Risks and Edge Cases
- The comment notes io_uring operations are usually enum constants, so `#ifndef` may not detect every header/version condition cleanly.
- Supplying constants at compile time does not mean the running kernel supports the feature or opcode; runtime probing remains mandatory.
- Numeric values must match Linux UAPI exactly.

## Test Signals
Build against old and new kernel headers, compile `gf-io-uring.c`, and run setup/probe tests on kernels with and without the declared features. Verify all fallback numeric constants against Linux UAPI.
