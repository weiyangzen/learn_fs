
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/powerpc.c

## Purpose
Provides the common PowerPC KVM architecture layer. It selects HV vs PR backends, implements vCPU entry preparation, paravirtual hypercalls, MMIO emulation completion, arch ioctls, capability reporting, memory-slot hooks, vCPU lifecycle hooks, interrupt controller plumbing, LPID allocation, and debugfs dispatch.

## Important APIs, Types, And Functions
Key functions include `kvmppc_prepare_to_enter()`, `kvmppc_kvm_pv()`, `kvmppc_sanity_check()`, `kvmppc_emulate_mmio()`, `kvmppc_st()`, `kvmppc_ld()`, `kvm_arch_init_vm()`, `kvm_arch_destroy_vm()`, `kvm_vm_ioctl_check_extension()`, `kvm_arch_vcpu_create()`, `kvm_arch_vcpu_destroy()`, `kvm_arch_vcpu_ioctl_run()`, `kvm_vcpu_ioctl_interrupt()`, `kvm_arch_vcpu_ioctl()`, `kvm_arch_vm_ioctl()`, `kvm_vm_ioctl_enable_cap()`, `kvm_vm_ioctl_irq_line()`, `kvmppc_alloc_lpid()`, `kvmppc_free_lpid()`, and `kvmppc_init_lpid()`. It exports backend pointers `kvmppc_hv_ops` and `kvmppc_pr_ops`.

## Control Flow
VM creation picks a backend from requested VM type and loaded modules, gets the module reference, and calls backend init. Guest entry preparation loops with hard IRQs disabled, handling reschedule, signals, pending requests, backend readiness, and `guest_enter_irqoff()`. Run ioctl resumes outstanding userspace MMIO/OSI/hcall/EPR state, activates signal masks, runs the backend, and normalizes resume codes. MMIO load/store helpers first try in-kernel MMIO buses, otherwise set up `KVM_EXIT_MMIO`; completion writes values back into GPR/FPR/QPR/VSX/VMX/nested GPR targets with endian and precision handling.

## State And Persistence
Persistent state includes VM backend ops pointer, module reference, LPID allocator state, vCPU decrementer hrtimer, wait object, pending MMIO continuation fields, extension copy counters, interrupt-controller pointers, magic page addresses, paravirtual flags, and enabled capabilities. Memory-slot operations delegate to backend hooks.

## Dependencies And Integration Points
Depends on the generic KVM core, PowerPC backend ops, MMIO bus, irqfd/irqbypass, XICS/XIVE/MPIC optional backends, pseries hcalls, Open Firmware CPU-characteristic discovery, timing helpers, and tracepoint creation for `trace.h`.

## Risks
The file is a high-blast-radius ABI surface. Capability answers vary by loaded backend, CPU features, platform firmware, and config options. MMIO continuation across userspace exits is subtle for VSX/VMX repeated transfers. Endian conversion, magic page mapping, and nested GPR writes are fragile. Backend module references and vCPU lifecycle ordering must remain balanced to avoid use-after-free or leaked modules.

## Test Signals
Regression signals include KVM capability selftests, VM type selection, vCPU run with signals/requests, scalar and vector MMIO exits/resume, PV info/hypercall behavior, one-reg get/set for vector registers, interrupt controller enable caps, LPID allocation exhaustion, and debugfs creation.
