# sources/distributed-fs/openafs/src/afs/LINUX/osi_inode.c

## Purpose
This Linux file provides stubs for legacy inode syscalls that OpenAFS exposes on some platforms: create, open, and increment/decrement.

## Important APIs, types, and functions
- `afs_syscall_icreate(long a, long b, long c, long d, long e, long f)`
- `afs_syscall_iopen(int a, int b, int c)`
- `afs_syscall_iincdec(int a, int v, int c, int d)`

## Control flow and behavior
All three functions ignore their arguments and return `0`. There is no actual inode manipulation in this Linux implementation.

## State and persistence
No state is read or written. No persistent inode changes occur through these stubs.

## Dependencies and integration points
The file includes OpenAFS inode/stat headers so the symbols satisfy portable syscall dispatch references. It prevents link failures where the common syscall layer expects these platform hooks.

## Risks
Returning success for no-op inode operations can mislead callers if any Linux path still expects real side effects. The risk is mitigated if these syscalls are obsolete or unreachable for Linux cache configurations.

## Test signals
Build/link tests are the primary signal. If ioctl/syscall dispatch exposes these calls, smoke tests should verify expected user-visible behavior and ensure no caller relies on real inode creation/open/increment semantics.
