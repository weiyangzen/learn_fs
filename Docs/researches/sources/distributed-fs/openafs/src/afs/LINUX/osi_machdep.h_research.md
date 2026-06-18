# sources/distributed-fs/openafs/src/afs/LINUX/osi_machdep.h

## Purpose
This Linux machine-dependent header maps portable OpenAFS OS abstractions to Linux task, signal, time, inode, credential, user-copy, vnode, uid/gid, and syscall-compatibility APIs.

## Important APIs, types, and functions
- Process/signal macros: `getpid`, `getppid`, `RECALC_SIGPENDING`, `SIG_LOCK`, `SIG_UNLOCK`, `TASK_STRUCT_RLIM`.
- Time helpers: `osi_Time`, `osi_GetTime`, inode timestamp accessors.
- Vnode/inode macros: `VN_HOLD`, `VN_RELE`, `vType`, `vSetType`, `IsAfsVnode`, `afs_suser`, and `wakeup`.
- User-copy helpers: `copyin`, `copyinstr`, and `copyout`.
- `afs_in_compat_syscall` detects 32-bit syscall mode on supported 64-bit architectures.
- Kernel print aliases: `printf` and `uprintf` to `printk`.
- Group/credential compatibility types and macros such as `GROUP_AT`, `afs_proc_t`, `afs_kuid_t`, `afs_kgid_t`, and namespace globals.

## Control flow and behavior
Most behavior is compile-time selection. The header chooses parent PID fields based on `task_struct`, signal lock locations based on kernel structure variants, time APIs based on available `ktime`/legacy calls, and compatibility syscall detection by architecture-specific thread flags or helpers. User-copy wrappers convert Linux copy return conventions into AFS-style error codes.

## State and persistence
The header owns no standalone state, but it references and mutates process signal masks, inode timestamps, and namespace/idmap globals initialized elsewhere. It affects all Linux AFS code that uses portable vnode/credential/time macros.

## Dependencies and integration points
It depends on Linux scheduler, credential, uaccess, uidgid, and time headers plus OpenAFS sysincludes. It is foundational for Linux platform code and is included before many portable AFS sources are compiled for Linux.

## Risks
Kernel structure drift is the main risk. Incorrect branch selection for signal locks, parent PID fields, rlimit location, or compat syscall detection can cause compile failures or runtime corruption. Macros such as `vSetType` directly mutate inode mode bits and must remain aligned with Linux inode rules. User namespace handling uses NULL when `current_user_ns` would require GPL-only `init_user_ns`, so uid/gid conversion behavior depends on configuration.

## Test signals
Build matrix coverage across old/new task credential models, signal structures, uid/gid namespace support, and 64-bit compat architectures is essential. Runtime signals include correct PID/PPID reporting, signal mask blocking/unblocking in sleeps, user-copy error propagation, time/timestamp updates, and `afs_in_compat_syscall` behavior for 32-bit userspace on 64-bit kernels.
