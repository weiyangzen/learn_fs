# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/Kbuild

Purpose: declares generated and generic PowerPC UAPI/asm header exports for Kbuild.

Important APIs/types/functions: `generated-y += syscall_table_32.h` and `generated-y += syscall_table_64.h` mark generated syscall tables. `generic-y += kvm_para.h`, `mcs_spinlock.h`, `early_ioremap.h`, `irq_regs.h`, and `export.h` select generic headers.

Control flow: Kbuild consumes this metadata during header generation and installation. The file has no C control flow.

State and persistence: it affects generated build artifacts and exported include trees, not runtime state.

Dependencies and integration points: depends on Linux Kbuild's `generated-y` and `generic-y` conventions. It integrates architecture-specific syscall table generation with generic asm header fallbacks.

Risks: removing an entry can break userspace header export or kernel compilation for includes that expect generic fallbacks. Adding architecture-specific headers with the same names requires adjusting this file to avoid conflicts.

Test signals: run PowerPC `headers_install`, allmodconfig/defconfig builds, and include smoke tests for the generic headers named here.
