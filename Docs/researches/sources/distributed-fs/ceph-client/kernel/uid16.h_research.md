<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/uid16.h -->
# sources/distributed-fs/ceph-client/kernel/uid16.h

Purpose: declares internal modern credential helper syscalls used by the legacy 16-bit UID/GID syscall wrappers.

Important APIs: prototypes include `__sys_setuid()`, `__sys_setgid()`, `__sys_setreuid()`, `__sys_setregid()`, `__sys_setresuid()`, `__sys_setresgid()`, `__sys_setfsuid()`, and `__sys_setfsgid()`.

Control flow and integration: `uid16.c` translates 16-bit ABI arguments and delegates to these helpers so policy, capability checks, credential allocation, and LSM hooks stay centralized in the normal credential implementation.

State and persistence: the header stores no state. It defines a compile-time contract between compatibility wrappers and shared credential code.

Dependencies: depends on the standard Linux uid/gid typedefs being visible to including C files.

Risks and tests: signature drift between this header and the helper implementations would break builds or worse, call ABI expectations. Test signals are compile coverage for configurations enabling UID16 syscalls and runtime credential tests that compare old and modern syscall behavior after conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/uid16.h -->
