## sources/distributed-fs/ceph-client/arch/arm64/include/asm/Kbuild

### Purpose
Declares ARM64 generated, syscall, and generic asm headers for Kbuild.

### Important APIs, Types, And Functions
Lists syscall-generated headers `syscall_table_32.h`, `syscall_table_64.h`, `unistd_32.h`, and `unistd_compat_32.h`; generic header fallbacks such as `early_ioremap.h`, `mcs_spinlock.h`, `qrwlock.h`, and `qspinlock.h`; and generated headers `cpucap-defs.h`, `kernel-hwcap.h`, and `sysreg-defs.h`.

### Control Flow
No runtime flow. Kbuild consumes `syscall-y`, `generic-y`, and `generated-y` variables to export or generate architecture include files.

### State, Persistence, And Dependencies
No runtime state. Build outputs are generated headers under the kernel build tree. Dependencies are syscall table generation, generic asm-generic headers, and ARM64 system register/capability generators.

### Integration Points
Supports userspace UAPI syscall constants, VDSO/seccomp/sigreturn includes, and generic architecture header resolution for ARM64.

### Risks
Missing generated headers break builds; wrong generic fallbacks can change locking or memory-management ABI; syscall header drift can break compat userspace.

### Test Signals
Run ARM64 `headers_install`, allmodconfig/defconfig builds, compat syscall table generation, and include-what-you-use style compile checks for generic-y headers.
