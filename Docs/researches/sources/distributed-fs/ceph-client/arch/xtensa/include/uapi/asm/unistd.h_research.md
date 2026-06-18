<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/unistd.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/unistd.h

Purpose: includes generated 32-bit Xtensa syscall numbers and defines Xtensa-specific `sysxtensa` operation numbers. Important definitions are `__ARCH_WANT_SYS_OLDUMOUNT`, `SYS_XTENSA_RESERVED`, `SYS_XTENSA_ATOMIC_SET`, `SYS_XTENSA_ATOMIC_EXG_ADD`, `SYS_XTENSA_ATOMIC_ADD`, `SYS_XTENSA_ATOMIC_CMP_SWP`, and `SYS_XTENSA_COUNT`.

Control flow is executed in `entry.S` fast syscall handling when `__NR_xtensa` is invoked; operation number in `a6` selects atomic user memory operations using pointer/value registers. Persistent state affected is user memory targeted by atomic operations. Dependencies include generated `asm/unistd_32.h`, uaccess/fault handling, and syscall table generation. Integration points are libc/syscall wrappers, legacy Xtensa atomic ABI, seccomp, strace, and fast syscall path. Risks are atomicity/fault semantics, operation number ABI stability, and mismatch between header and fast handler. Test signals include generated syscall header checks, `sysxtensa` atomic operation tests, invalid op tests, user fault tests, and strace/seccomp decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/unistd.h -->
