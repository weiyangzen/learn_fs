<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/unistd.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/unistd.h

**Purpose:** Kernel syscall-number wrapper and Alpha syscall implementation request list.

**Important APIs/types/functions:** `NR_syscalls`, `__ARCH_WANT_NEW_STAT`, `__ARCH_WANT_OLD_READDIR`, `__ARCH_WANT_STAT64`, `__ARCH_WANT_SYS_*` flags for legacy syscall implementations.

**Control flow:** Generic syscall table/build code uses the `__ARCH_WANT_*` macros to include compatibility or legacy syscall handlers needed by Alpha.

**State and persistence behavior:** No runtime state; shapes compiled syscall surface.

**Dependencies and integration points:** Depends on UAPI syscall numbers generated from Alpha syscall table and generic syscall implementation selection.

**Risks:** Removing a wanted syscall breaks Alpha userspace ABI. Wrong `NR_syscalls` affects seccomp and bounds checks.

**Test signals:** Syscall table build checks, LTP syscall coverage, legacy stat/readdir/umount/fork/vfork tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/unistd.h -->
