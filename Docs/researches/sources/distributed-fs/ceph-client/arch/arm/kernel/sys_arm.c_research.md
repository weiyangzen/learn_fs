# sources/distributed-fs/ceph-client/arch/arm/kernel/sys_arm.c

Purpose: contains ARM-specific syscall glue for calls whose register ABI differs from generic Linux argument order. The only function here is `sys_arm_fadvise64_64`, which reorders `fd, advice, offset, len` into the `ksys_fadvise64_64(fd, offset, len, advice)` convention.

Control flow is deliberately thin: syscall entry lands in this wrapper and immediately delegates to the common kernel implementation. There is no local persistent state, locking, or memory ownership. Dependencies are syscall linkage, ARM syscall tables, and the generic fadvise implementation. The main risk is ABI ordering regression, because userspace depends on this nonstandard ARM calling sequence for 64-bit arguments. Test signals are syscall ABI tests that pass nonzero offset/length/advice combinations and compare behavior to expected `posix_fadvise` semantics.
