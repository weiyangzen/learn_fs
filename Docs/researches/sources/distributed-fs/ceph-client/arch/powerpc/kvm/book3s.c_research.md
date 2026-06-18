# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s.c

## Purpose
Provides shared Book3S KVM glue for both PR and HV implementations: statistics descriptors, interrupt queuing and delivery, address translation wrappers, register ioctls, vCPU and VM operation dispatch, dirty-log/memslot delegation, logical cache-inhibited hypercalls, IRQ routing, and module initialization.

## Important APIs, Types, And Functions
Important exported or core functions include `kvmppc_inject_interrupt`, `kvmppc_book3s_queue_irqprio`, `kvmppc_core_queue_*`, `kvmppc_core_prepare_to_enter`, `kvmppc_gpa_to_pfn`, `kvmppc_xlate`, `kvmppc_load_last_inst`, `kvm_arch_vcpu_ioctl_get_regs`, `kvm_arch_vcpu_ioctl_set_regs`, `kvmppc_get_one_reg`, `kvmppc_set_one_reg`, `kvmppc_set_msr`, `kvmppc_vcpu_run`, `kvmppc_core_init_vm`, `kvmppc_core_destroy_vm`, `kvmppc_h_logical_ci_load`, `kvmppc_h_logical_ci_store`, and `kvmppc_book3s_init`. It relies heavily on `kvm->arch.kvm_ops` for mode-specific behavior.

## Control Flow
Interrupt requests are translated from vectors to priority bits, queued in `pending_exceptions`, and delivered by `kvmppc_core_prepare_to_enter` in priority order if guest MSR and critical-section checks permit. Register ioctls first delegate mode-specific registers through `kvm_ops`, then handle common DAR/DSISR/FPR/VSX/debug/interrupt-controller/FSCR/TAR/EBB/BESCR/IC cases. Memory and VM lifecycle functions mostly delegate through `kvm_ops`, with shared PPC64 setup and teardown for RTAS tokens and SPAPR TCE tables. Logical CI hcalls perform MMIO bus reads/writes with big-endian size conversion. Module init calls `kvm_init`, PR init for 32-bit handler builds, and XICS/XIVE device registration.

## State And Persistence
Per-vCPU state includes pending exception bitmaps, one-shot external interrupt state, guest registers, FPU/VSX state, magic page addresses, and statistics counters. Per-VM state includes mode-specific operations, RTAS token lists, SPAPR TCE table lists, XICS/XIVE device pointers, and memory-slot/MMU state delegated to HV or PR code. No filesystem persistence is involved.

## Dependencies And Integration Points
Depends on generic KVM core, PPC register helpers, Book3S PR/HV ops, MMU code, XICS/XIVE, RTAS, MMIO buses, SRCU, and module infrastructure. It is the main user-visible `/dev/kvm` Book3S module entry for common ioctls and mode-independent hypercall support.

## Risks And Edge Cases
Interrupt delivery must respect guest critical sections, MSR[EE], nestedv2 behavior, and one-shot external interrupts. Magic-page PFN override must keep page references and 32-bit truncation correct. Register ioctl fallbacks must not expose unavailable VSX/XIVE/XICS state. The source snapshot contains duplicated braces/preprocessor lines in sensitive areas, which would be compile-time risks if active. Logical CI hcalls depend on exact endian conversion and MMIO bus behavior.

## Test Signals
Use KVM selftests/QEMU guest boot for Book3S PR and HV, interrupt injection tests, decrementer and external IRQ tests, register get/set ABI tests, MMIO load/store hypercalls, XICS/XIVE device creation, migration register save/restore, dirty-log ioctls, and 32-bit guest-on-64-bit host cases.
