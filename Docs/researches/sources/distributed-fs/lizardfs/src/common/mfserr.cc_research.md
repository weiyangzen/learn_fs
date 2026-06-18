<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/mfserr.cc -->
# sources/distributed-fs/lizardfs/src/common/mfserr.cc

## Purpose
Converts LizardFS status codes to POSIX errno values and provides a thread-safe stable `strerror` wrapper. The source was read completely for this report.

## Important APIs, Types, And Functions
`lizardfs_error_conv(uint8_t)` maps selected protocol codes; `strerr(int)` caches `strerror` strings in a mutex-protected unordered map.

## Control Flow
Error conversion is a switch with default `EINVAL`. `strerr` checks the cache, calls `strerror`, stores a copy, and returns the stored C string.

## State And Persistence Behavior
State is the static error-description cache and mutex. No persistence.

## Dependencies And Integration Points
Depends on `errno_defs.h`, `lizardfs_error_codes.h`, and platform errno definitions.

## Risks And Edge Cases
Returned pointers remain valid unless the unordered_map rehash invalidates string objects; because strings are stored as values, rehash moves them and can invalidate previous `c_str()` pointers. Callers should not keep pointers long-term.

## Test Signals
Needs tests for representative status-to-errno mappings and concurrent `strerr` calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/mfserr.cc -->
