<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/getrandom.h -->
# sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/getrandom.h

Purpose: supplies LoongArch hooks for vDSO getrandom support.
Important APIs and types: defines architecture eligibility and includes generic vDSO getrandom support when configured.
Control flow: userspace vDSO getrandom uses shared random-state pages where supported, falling back to syscalls when unavailable.
State and persistence: random state lives in kernel-managed vvar/getrandom pages, not in this header.
Dependencies and integration: integrates with generic vDSO getrandom code, random subsystem, mm vDSO mapping, and libc wrappers.
Risks and test signals: ABI or feature mismatches can produce weak randomness or syscall fallback failures. Signals include getrandom selftests and vDSO mapping tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/loongarch/include/asm/vdso/getrandom.h -->
