# sources/distributed-fs/openafs/src/sys/syscall.s

## Purpose
`syscall.s` provides platform assembly syscall stubs or placeholders for legacy OpenAFS syscall entry points.

## Important APIs, types, and functions
It contains an AIX dummy csect placeholder, an HP PA-RISC `dummysysc` entry, an SGI/MIPS `afs_syscall` leaf routine, and a Linux ELF `.note.GNU-stack` marker.

## Control flow
On SGI, `afs_syscall` loads `AFS_SYSCALL`, executes the kernel syscall instruction, branches to `_cerror` on error, and returns on success. Other platform sections are placeholders or ABI-specific dummy entries selected by macros.

## State and persistence behavior
No persistent state is stored. Executed stubs cross into kernel syscall handling.

## Dependencies and integration points
It includes `afs/param.h` with `IGNORE_STDS_H`, uses assembler macros/register headers on SGI, and is built by `src/sys/Makefile.in` into `syscall.o` on selected platforms.

## Risks
Assembly is highly ABI-specific. Wrong preprocessing or assembler invocation can produce unusable syscall stubs, while missing `.note.GNU-stack` can affect executable stack metadata on Linux.

## Test signals
Build `syscall.lo` for SGI, AIX, HP-UX, and generic Linux. On SGI, run a simple `lpioctl` or inode syscall through `afs_syscall` and verify errno behavior.
