# sources/distributed-fs/ceph-client/arch/loongarch/kvm/exit.c

Purpose: decodes and handles guest exits for LoongArch KVM, covering CPUCFG/CSR/IOCSR emulation, MMIO fallback, page faults, auxiliary-unit traps, hypercalls, and exception dispatch.

Important APIs, types, and functions: key entry points are `kvm_handle_fault()`, `kvm_emu_iocsr()`, `kvm_complete_iocsr_read()`, `kvm_emu_mmio_read()`, `kvm_complete_mmio_read()`, `kvm_emu_mmio_write()`, and `kvm_complete_user_service()`. It uses `larch_inst`, `struct kvm_run`, `struct kvm_vcpu`, emulation result constants, `kvm_fault_tables[]`, and tracepoints.

Control flow: GSPR exits fetch `vcpu->arch.badi`, advance PC optimistically, decode CPUCFG, CSR, cache, idle, and IOCSR operations, then either resume guest, exit to userspace, or inject illegal instruction. GPA read/write faults first call `kvm_handle_mm_fault()`; failures are decoded as MMIO reads/writes and either handled in-kernel via KVM I/O buses or returned to userspace. Auxiliary-unit disabled exits request FPU/LSX/LASX/LBT loading. Hypercalls implement PV IPI, PV steal-time notification, user-service exits, and software debug.

State and persistence: mutates GPRs, guest PC, CSR state, `run->mmio`, `run->iocsr_io`, `run->hypercall`, `vcpu->mmio_needed`, `io_gpr`, stats counters, pending requests, and PV steal-time address state. No storage persists beyond VM/vCPU state.

Dependencies and integration points: integrates with `mmu.c` for GPA mappings, KVM MMIO/IOCSR buses, interrupt injection, CSR helpers, PMU request handling, timer/idle halt logic, PV feature flags, userspace `KVM_EXIT_MMIO`, `KVM_EXIT_LOONGARCH_IOCSR`, `KVM_EXIT_HYPERCALL`, and trace events.

Risks: PC update/rollback rules are subtle for emulation failures and userspace completions. Signed versus unsigned MMIO reads depend on `mmio_needed`. Unsupported CSR behavior must match architecture expectations. MMIO instruction decoder coverage affects device emulation correctness. Hypercall feature checks gate ABI exposure.

Test signals: KVM unit tests for CPUCFG/CSR, userspace MMIO and IOCSR exits, in-kernel irqchip accesses, dirty memory faults, FPU/LSX/LASX traps, PV IPI and steal time, and tracepoint coverage.
