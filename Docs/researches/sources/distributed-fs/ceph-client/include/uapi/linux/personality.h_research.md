# sources/distributed-fs/ceph-client/include/uapi/linux/personality.h

Purpose: Defines process personality flags and personality type constants used by the `personality(2)` syscall and exec compatibility behavior.

Important APIs/types/functions: Exports bug-emulation/security flags such as `ADDR_NO_RANDOMIZE`, `FDPIC_FUNCPTRS`, `MMAP_PAGE_ZERO`, `ADDR_COMPAT_LAYOUT`, `READ_IMPLIES_EXEC`, address limit flags, `STICKY_TIMEOUTS`, `PER_CLEAR_ON_SETID`, personality constants such as `PER_LINUX`, `PER_LINUX32`, SVR/IRIX/Solaris/HPUX variants, and `PER_MASK`.

Control flow: Userspace calls `personality()` to query or set the low personality byte plus high compatibility flags. The kernel consults these bits during exec, memory layout selection, mmap permissions, signal/function-pointer interpretation, uname behavior, and timeout restart behavior.

State and persistence behavior: Personality is per-task state inherited across fork and modified/reset across exec according to kernel rules. `PER_CLEAR_ON_SETID` identifies security-sensitive flags cleared on setuid/setgid exec.

Dependencies and integration points: No external dependencies. Integrates with libc, compatibility loaders, binfmt handlers, ASLR policy, and old UNIX binary emulation.

Risks: Flags such as `READ_IMPLIES_EXEC`, `ADDR_NO_RANDOMIZE`, and `MMAP_PAGE_ZERO` are security-relevant. Personality low byte avoids the top bit to prevent confusion with negative syscall returns. Setid clearing must stay aligned with `PER_CLEAR_ON_SETID`.

Test signals: Use `personality(2)` to set each supported flag, verify ASLR and mmap behavior, test setuid exec clearing, run 32-bit/compat binary loaders, and confirm legacy personality types preserve expected timeout and uname semantics.
