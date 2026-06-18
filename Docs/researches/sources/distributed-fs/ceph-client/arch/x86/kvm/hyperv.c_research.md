<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/hyperv.c -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/hyperv.c

### Purpose
`hyperv.c` implements KVM's Microsoft Hyper-V enlightenment surface for x86 guests. It covers Hyper-V MSR emulation, SynIC and synthetic timers, Hyper-V hypercall dispatch, eventfd-backed signal events, guest crash/reset exits, reference TSC page updates, CPUID helper output, nested-Hyper-V TLB flush support, and synthetic debugger exits to userspace.

### Important APIs, Types, And Functions
Public entry points include `kvm_hv_set_msr_common()`, `kvm_hv_get_msr_common()`, `kvm_hv_hypercall()`, `kvm_hv_process_stimers()`, `kvm_hv_activate_synic()`, `kvm_hv_vcpu_init()`, `kvm_hv_vcpu_uninit()`, `kvm_hv_setup_tsc_page()`, `kvm_hv_request_tsc_page_update()`, `kvm_hv_set_cpuid()`, `kvm_get_hv_cpuid()`, `kvm_vm_ioctl_hv_eventfd()`, and `kvm_hv_vcpu_flush_tlb()`. Important internal helpers are the SynIC `synic_*()` routines, stimer `stimer_*()` routines, `kvm_hv_flush_tlb()`, `kvm_hv_send_ipi()`, `compute_tsc_page_parameters()`, and synthetic debugger `syndbg_*()` handlers. Core state is split between VM-wide `struct kvm_hv`, per-vCPU `struct kvm_vcpu_hv`, `struct kvm_vcpu_hv_synic`, and `struct kvm_vcpu_hv_stimer`.

### Control Flow
Hyper-V MSR access first checks whether Hyper-V is enabled and whether CPUID enforcement permits the requested register. Partition-wide MSRs are serialized by `hv_lock`; vCPU-local MSRs update VP index, VP assist page, virtual APIC MSRs, SynIC, stimer config/count, and runtime. Hypercall handling decodes the 32-bit or 64-bit ABI registers, validates reserved fields and CPUID access, optionally reads XMM fast-call inputs, and then handles spin-wait, signal event, TLB flush, send IPI, debugger, and extended calls. Calls that KVM cannot complete in kernel are converted to `KVM_EXIT_HYPERV` and completed through `complete_userspace_io`. SynIC delivery writes guest message pages and injects LAPIC vectors. Stimers use host hrtimers to mark pending work, then vCPU context delivers messages or direct APIC interrupts and re-arms periodic timers.

### State, Persistence, And Dependencies
Persistent VM state includes guest OS ID, hypercall page MSR, reference TSC page MSR/status, crash parameters, reenlightenment/TSC emulation controls, invariant-TSC control, synthetic debugger state, and an IDR of connection IDs to eventfds. Per-vCPU state includes CPUID cache, VP index, assist-page MSR, SynIC registers and bitmaps, stimer hrtimers/messages, TLB flush FIFOs, nested VP/VM identifiers, and scratch masks. Dependencies include KVM x86 ops, LAPIC, IOAPIC routing, MMU nested GPA translation, pvclock, FPU/SSE register access, eventfd, SRCU/RCU, hrtimer, kfifo, Hyper-V TLFS constants, and KVM userspace exit ABI.

### Integration Points
This file is called from KVM MSR paths, CPUID ioctls, hypercall emulation, vCPU request processing, APIC EOI paths, IRQ routing updates, masterclock updates, nested virtualization paths, and VM teardown. It integrates with `irq.c` for `KVM_IRQ_ROUTING_HV_SINT`, with LAPIC for direct stimer/IPI delivery and virtual APIC MSRs, with userspace through `KVM_EXIT_HYPERV`, `KVM_EXIT_HYPERV_SYNIC`, `KVM_EXIT_HYPERV_SYNDBG`, crash/reset requests, and `KVM_HYPERV_EVENTFD`.

### Risks
The riskiest contracts are guest-visible ABI validation, CPUID feature enforcement, TSC page sequence ordering, message-page write ordering, eventfd lifetime under RCU/SRCU, nested TLB flush FIFO overflow fallback, VP-index mismatches, and APICv inhibition when SynIC AutoEOI is used. Hypercall input offsets differ between slow memory calls and XMM fast calls, making sparse VP sets and rep-count validation easy to break. Stimer delivery is also sensitive to lost-tick policy, immediate one-shot expiry, and retry behavior when SynIC message slots are occupied.

### Test Signals
Useful tests include Hyper-V CPUID enumeration, guest/host MSR save-restore, hypercall page patching, signal-event eventfd delivery, userspace POST_MESSAGE exits, SynIC SINT routing and EOI notification, AutoEOI APICv inhibition, stimer one-shot/periodic/direct/SynIC modes, TSC reference page migration/update behavior, crash and reset exits, synthetic debugger exits, TLB flush hypercalls with sparse/all VP sets and XMM fast input, nested direct flush behavior, send-IPI vector validation, and CPUID enforcement denial paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/hyperv.c -->
