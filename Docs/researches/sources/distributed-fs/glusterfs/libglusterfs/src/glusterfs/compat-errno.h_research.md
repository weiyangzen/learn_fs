# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/compat-errno.h

## Purpose
`compat-errno.h` defines GlusterFS' stable cross-platform error-code namespace and declares conversion functions between platform `errno` values and Gluster error codes. It also supplies missing errno aliases for portability.

## Important APIs, Types, and Functions
- `GF_ERROR_CODE_*`: numeric error constants for common POSIX/Linux errors, NFSv3 errors, Darwin, Solaris, and BSD-specific cases.
- `GF_ERROR_CODE_UNKNOWN` and `GF_ERRNO_UNKNOWN`: fallback unknown value 1024.
- Portability aliases: `ENOATTR`/`ENODATA`, `EBADFD`, `ETIME` when absent.
- `gf_errno_to_error(int32_t op_errno)`, `gf_error_to_errno(int32_t error)`: conversion declarations implemented per OS.

## Control Flow
The header is macro-only except conversion declarations. Compile-time conditionals define aliases when the platform lacks a symbol. Runtime conversion functions map native errno to/from the stable Gluster numeric namespace.

## State and Persistence
No state. The constants are part of wire/protocol/logging compatibility and must remain stable.

## Dependencies and Integration Points
Depends on `<errno.h>`. Used anywhere Gluster serializes, logs, or translates errors across nodes or platforms, including RPC, FOP callbacks, and translator error handling.

## Risks and Edge Cases
- Duplicate `GF_ERROR_CODE_ALREADY` and `GF_ERROR_CODE_INPROGRESS` definitions appear with identical values.
- Some fallback aliases depend on other platform-specific symbols being available.
- Changing numeric constants can break cross-version or cross-platform interoperability.
- Conversion implementations must handle unknown/unsupported codes without leaking host-specific surprises.

## Test Signals
Test bidirectional conversion for common errors, unknown values, platform aliases, NFS-specific codes, and robust mutex codes. Cross-platform CI is especially valuable.
