<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/s390/include/asm/Kbuild

Purpose: Controls generated asm-generic wrapper headers exported for s390 asm includes.

Important APIs/types/functions: `generic-y` entries for `early_ioremap.h`, `mcs_spinlock.h`, `qspinlock.h`, `qspinlock_types.h`, `qrwlock.h`, `qrwlock_types.h`, `user.h`, and `vmlinux.lds.h`. Source-visible declarations include: no direct declarations beyond include guards or build directives.

Control flow: Kbuild reads this file during header generation and emits wrappers for generic asm headers that s390 does not override locally.

State and persistence behavior: No runtime state; it shapes the generated include tree and therefore build-time ABI surface.

Dependencies and integration points: Direct includes are no direct includes. Integrated with Integrates with the Linux Kbuild asm-generic wrapper mechanism and any source including the listed asm headers..

Risks: Removing or renaming entries can break architecture builds or silently switch code away from generic lock/header implementations.

Test signals: Primary signals are s390 defconfig/allmodconfig or targeted cross-builds, sparse/objtool-style checks for packed layouts and inline assembly constraints, subsystem tests for users of the API, and runtime validation on s390x LPAR, z/VM, or QEMU where the relevant facility is available.

Source read size: 9 lines, 228 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/include/asm/Kbuild -->
