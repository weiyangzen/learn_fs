# sources/distributed-fs/ceph-client/arch/s390/include/asm/nmi.h

Purpose: This header defines s390 machine-check/NMI bit meanings, the machine-check extended save area layout, and machine-check handling entry points.

Important APIs/types/functions: `MCIC_SUBCLASS_MASK`, many `MCCK_CODE_*` bits, `union mci`, `MCESA_*` constants, `struct mcesa`, `nmi_alloc_mcesa_early()`, `nmi_alloc_mcesa()`, `nmi_free_mcesa()`, `s390_handle_mcck()`, and `s390_do_machine_check()` are exposed.

Control flow: Machine-check entry code decodes MCIC bits, uses MCESA storage for vector/guarded-storage state when valid, and dispatches low/high-level handlers with `pt_regs` context.

State and persistence: Persistent state includes per-CPU MCESA allocation referenced from lowcore `mcesad`; individual machine-check status is transient but may be saved for diagnostics.

Dependencies and integration points: It depends on Linux bit definitions, lowcore machine-check fields, ptrace context, vector and guarded-storage state, and KVM guest machine-check paths.

Risks and test signals: Machine-check validity bits determine which saved registers can be trusted; mishandling can corrupt recovery or dump data. Tests are mostly hardware/error-injection oriented: MCESA allocation, simulated machine checks, storage-error reporting, guest-running machine checks, and crash dump validation.
