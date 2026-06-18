<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/tm.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/tm.h

Purpose: Defines PowerPC transactional memory abort cause codes used by kernel and virtualization.

Important APIs/types/functions: `TM_CAUSE_PERSISTENT`, KVM/PAPR causes, and kernel causes for reschedule, TLB invalidation, facility unavailable, syscall, misc, signal, alignment, and emulation aborts.

Control flow: When the kernel aborts a transaction, it records an encoded cause that can be reflected into transactional state such as TEXASR conventions.

State and persistence: No state owned; constants describe abort state persisted in TM registers/signal context.

Dependencies and integration points: Integrated by transactional memory exception, signal, and KVM code.

Risks: Cause values are ABI/diagnostic-visible and overlap PAPR-reserved ranges intentionally.

Test signals: TM selftests for abort causes, signal context validation, and KVM TM tests where supported.

Source read size: 21 lines, 734 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/tm.h -->
