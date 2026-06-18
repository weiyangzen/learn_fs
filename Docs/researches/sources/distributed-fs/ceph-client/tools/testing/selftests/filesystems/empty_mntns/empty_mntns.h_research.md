# sources/distributed-fs/ceph-client/tools/testing/selftests/filesystems/empty_mntns/empty_mntns.h

## Purpose
Shared header for empty mount namespace tests, defining missing UAPI constants and a helper to count mounts.

## Important APIs, Types, And Functions
Includes `statmount.h`, defines `UNSHARE_EMPTY_MNTNS` as `0x00100000` and `CLONE_EMPTY_MNTNS` as `1ULL << 37` if absent, and implements `count_mounts()` using `listmount(LSMT_ROOT, ...)` into a fixed `uint64_t list[4096]`.

## Control Flow
Header-only helper is included by test programs. `count_mounts()` returns the `listmount` syscall result.

## State And Persistence
No persistent state; uses stack buffer per call.

## Dependencies And Integration Points
Depends on statmount/listmount wrappers from the adjacent selftest infrastructure.

## Risks
The fixed 4096 mount buffer can undercount/fail on very large mount namespaces; empty namespace tests expect one mount, but parent-copy regression tests only need lower-bound checks.

## Test Signals
`count_mounts() == 1` is the central assertion signal for empty namespace creation.
