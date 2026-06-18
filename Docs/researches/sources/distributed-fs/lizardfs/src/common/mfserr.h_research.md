<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/mfserr.h -->
# sources/distributed-fs/lizardfs/src/common/mfserr.h

## Purpose
Declares POSIX error conversion helpers for LizardFS status codes. The source was read completely for this report.

## Important APIs, Types, And Functions
`strerr(int)` and `lizardfs_error_conv(uint8_t)` are exported.

## Control Flow
No control flow in header.

## State And Persistence Behavior
No owned state in header; implementation owns the cache.

## Dependencies And Integration Points
Includes `lizardfs_error_codes.h` and protocol constants; used broadly by assertions, sockets, and user-facing errors.

## Risks And Edge Cases
Conversion coverage must track new protocol errors.

## Test Signals
Compile coverage plus mapping tests should protect callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/mfserr.h -->
