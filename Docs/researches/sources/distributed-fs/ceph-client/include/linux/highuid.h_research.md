# sources/distributed-fs/ceph-client/include/linux/highuid.h

## Purpose
`highuid.h` provides compatibility conversion helpers for systems or filesystems that need to represent UIDs/GIDs in old 16-bit forms. It defines overflow values for old user APIs and filesystem on-disk formats while keeping kernel-private code on full `uid_t`/`gid_t`.

## Important APIs, Types, And Functions
The key external variables are `overflowuid`, `overflowgid`, `fs_overflowuid`, and `fs_overflowgid`, with defaults set to 65534. Under `CONFIG_UID16`, `high2lowuid()`, `high2lowgid()`, `low2highuid()`, and `low2highgid()` perform old syscall compatibility conversion. `SET_UID()` and `SET_GID()` assign to possibly narrower fields through `__convert_uid()`/`__convert_gid()`. Filesystem helpers include `fs_high2lowuid()`, `fs_high2lowgid()`, `low_16_bits()`, and `high_16_bits()`.

## Control Flow And State
There is no runtime control flow beyond macro expansion. State is global overflow UID/GID policy, configurable elsewhere, and on-disk or userspace fields receiving converted IDs. High UIDs written to 16-bit filesystems are mapped to filesystem overflow IDs rather than truncated.

## Dependencies And Integration Points
It depends on kernel type definitions. It integrates with old system calls, architecture compatibility code, filesystem on-disk encoding, and UID/GID assignment sites that need field-width-aware conversion.

## Risks
Incorrect use can silently truncate or misrepresent ownership. Callers must use filesystem overflow helpers for 16-bit disk formats and old syscall helpers only for legacy userspace interfaces. The special `-1` handling in low-to-high conversion is required for chown/setreuid semantics.

## Test Signals
Test high UID/GID stat/chown behavior through old 16-bit APIs, filesystem write/read of high IDs on 16-bit formats, overflow sysctl/default behavior, and builds with `CONFIG_UID16` enabled and disabled.
