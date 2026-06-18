# sources/distributed-fs/lizardfs/src/mount/fuse/lock_conversion.h

## Purpose
`lock_conversion.h` converts FUSE/POSIX lock operation representations to and from LizardFS internal `FlockWrapper` flags.

## Important APIs, Types, And Functions
- `flockOpConv(int op)` maps `LOCK_UN`, `LOCK_EX`, `LOCK_SH`, and optional `LOCK_NB` to internal lock flags.
- `posixOpConv(int op, bool sleep)` maps `F_UNLCK`, `F_RDLCK`, and `F_WRLCK` plus nonblocking behavior.
- `flockOpValid(int op)` and `posixOpValid(int op)` validate operation inputs.
- `convertPLock(struct flock&, bool sleep)` builds an internal `FlockWrapper` from POSIX `flock`.
- `convertToFlock(FlockWrapper&)` builds a POSIX `struct flock` from internal flags.

## Control Flow
Conversion functions are inline and branch on lock operation bits or `flock.l_type`. Internal flags include `kUnlock`, `kShared`, `kExclusive`, `kNonblock`, and `kInvalid`. `convertToFlock` asserts on unknown internal lock types.

## State And Persistence
No state or persistence. These are pure conversion helpers.

## Dependencies And Integration Points
It includes `<fcntl.h>`, `<sys/file.h>`, serialization macros, and `protocol/lock_info.h`. It is used by FUSE lock handling to translate kernel lock requests into LizardFS protocol structures.

## Risks
- `flockOpValid` accepts any op with `LOCK_UN`, `LOCK_SH`, or `LOCK_EX` bits set, even with unrelated extra bits; conversion also prioritizes unlock over exclusive/shared if multiple bits are set.
- `convertToFlock` takes non-const `FlockWrapper&` though it does not modify it.
- Assertions catch invalid internal types only in debug builds.

## Test Signals
Tests should cover valid/invalid flock and POSIX combinations, nonblocking flag preservation, multi-bit ambiguous flock inputs, and round-trip conversion for shared/exclusive/unlock locks.
