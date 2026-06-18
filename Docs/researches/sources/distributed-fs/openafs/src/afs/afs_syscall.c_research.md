# sources/distributed-fs/openafs/src/afs/afs_syscall.c

## Purpose

`afs_syscall.c` implements the platform-specific AFS system-call entry layer. It translates user-mode syscall arguments into kernel Cache Manager calls, handles 32-bit compatibility layouts on 64-bit kernels, dispatches AFS syscall numbers such as `AFSCALL_CALL`, `AFSCALL_SETPAG`, `AFSCALL_PIOCTL`, inode-server calls, and `AFSCALL_ICL`, and normalizes platform return conventions. It is primarily glue, but it is security-sensitive because it copies user pointers and bridges user requests into privileged kernel state.

## Important APIs, Types, and Functions

Shared helpers include `copyin_afs_ioctl`, which imports `struct afs_ioctl` or `struct afs_ioctl32`, and `copyin_iparam`, which imports inode-call parameters through `struct iparam` or `struct iparam32`. Conversion helpers `afs_ioctl32_to_afs_ioctl` and `iparam32_to_iparam` preserve pointer values through platform-appropriate casts. Entry points vary by platform: AIX has `syscall`, `lsetpag`, and `lpioctl`; SGI has `Afs_syscall(struct afsargs *, rval_t *)`; Solaris, Darwin, BSD, Linux, UKERNEL, and generic Unix builds each expose `Afs_syscall`, `afs3_syscall`, or `afs_syscall` with local argument structures.

## Control Flow and Dispatch

The generic dispatcher increments `AFS_STATCNT(afs_syscall)` and switches on the syscall number. `AFSCALL_CALL` delegates to `afs_syscall_call` or `afs_syscall64_call`; `AFSCALL_SETPAG` enters `AFS_GLOCK`, calls `afs_setpag`, and releases the lock; `AFSCALL_PIOCTL` similarly calls `afs_syscall_pioctl` with platform credentials and return-value handles; inode operations call `afs_syscall_icreate`, `afs_syscall_iopen`, or `afs_syscall_iincdec`; `AFSCALL_ICL` calls `Afscall_icl` or `Afscall64_icl`. Linux has only five syscall arguments, so `AFSCALL_ICL` and `AFSCALL_CALL` unpack folded parameters from a user array; SPARC64 has additional 32-bit argument cleanup.

## Dependencies and Integration Points

This file integrates with pioctl handling, PAG management, inode file-server support, fstrace/ICL tracing, kernel credential APIs, user-copy macros (`AFS_COPYIN`), Rx globals, and platform process/context helpers. It also includes network interface headers for platform builds that need shared AFS kernel definitions. The code uses `AFS_GLOCK` around Cache Manager operations that require global serialization, while some inode operations run outside it depending on platform conventions.

## Persistence and Side Effects

The file does not own persistent data structures, but every dispatched operation may mutate Cache Manager state: PAG credentials, tokens, pioctl-controlled configuration, inode cache state, or trace buffers. Failed user copies return errors before dispatch. Some platforms store errors in `uerror` or return negative Linux errno values; Darwin may pass negative `AFSCALL_CALL` results back as syscall return values with `code` reset to zero.

## Risks and Test Signals

Risks include pointer truncation in compat paths, incorrect credential passing, missing `AFS_GLOCK` coverage, mismatched platform return semantics, and unsafe user-copy lengths. `copyin_afs_ioctl` and `copyin_iparam` must stay in sync because both encode user pointer compatibility policy. Test signals include 32-bit userland on 64-bit kernels, Linux folded-argument syscalls, pioctl/setpag smoke tests, invalid pointer copyin failures, ICL return-value behavior, and platform-specific syscall registration tests.
