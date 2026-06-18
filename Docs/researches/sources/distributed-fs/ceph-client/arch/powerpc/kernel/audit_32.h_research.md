<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/audit_32.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/audit_32.h

Purpose: Declares the 32-bit PowerPC audit syscall classifier.

Important APIs/types/functions: `ppc32_classify_syscall(unsigned)`.

Control flow: Audit code can call the classifier to map a 32-bit syscall number into an audit class.

State and persistence: No state owned; classification derives from syscall number tables elsewhere.

Dependencies and integration points: Integrated by PowerPC audit implementation for compat/32-bit syscall auditing.

Risks: A missing or mismatched prototype breaks audit builds; wrong classifier behavior can mislabel audited syscalls.

Test signals: CONFIG_AUDIT PPC32/compat builds and audit syscall classification tests.

Source read size: 7 lines, 136 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/audit_32.h -->
