<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm.h

Purpose: Defines the x86-specific KVM userspace ABI for VM and vCPU state, interrupt chips, registers, CPUID, MSRs, PIT, debug state, XSAVE/XCRS, sync regs, quirks, nested VMX/SVM migration state, PMU filters, MCE injection, Xen HVM emulation, SEV/SNP, Hyper-V eventfds, x2APIC API, hypercall exits, protected VM types, and TDX subcommands.

Important APIs/types/functions: `struct kvm_regs`, `kvm_sregs`, `kvm_sregs2`, `kvm_fpu`, `kvm_msr_entry`, `kvm_msrs`, `kvm_msr_filter`, `kvm_cpuid_entry*`, `kvm_lapic_state`, `kvm_vcpu_events`, `kvm_debugregs`, `kvm_xsave`, `kvm_xcrs`, `kvm_sync_regs`, `kvm_nested_state`, `kvm_pmu_event_filter`, `kvm_x86_mce`, `kvm_xen_hvm_config`, `kvm_xen_hvm_attr`, `kvm_xen_vcpu_attr`, SEV/SNP command structs, `kvm_tdx_cmd`, `kvm_tdx_capabilities`, and `kvm_tdx_init_*`; feature flags such as `__KVM_HAVE_*`, `KVM_STATE_NESTED_*`, `KVM_XEN_HVM_CONFIG_*`, `KVM_SEV_*`, `KVM_X86_*_VM`, and PMU masked-entry helpers.

Control flow: Userspace VMMs exchange these structures through KVM ioctls. They create vCPUs, set CPUID/MSRs/registers, snapshot interrupt chips and timers, filter MSR/PMU access, migrate nested virtualization state, configure Xen compatibility, launch encrypted VMs, and initialize TDX VMs. Kernel KVM validates userspace-supplied state before loading it into vCPU or VM structures.

State and persistence behavior: These structures are the persistent migration and runtime ABI between userspace and KVM. They carry guest CPU state, interrupt-controller state, event injection state, nested VMCS/VMCB state, encryption launch state, Xen shared info/runstate/timer metadata, and protected-VM measurement inputs.

Dependencies and integration points: Depends on Linux UAPI types/ioctl/bit helpers and is consumed by QEMU, cloud hypervisors, test frameworks, migration tooling, and KVM kernel code. Integrates with VMX, SVM, Xen HVM emulation, Hyper-V emulation, SEV/SNP firmware, TDX module, PMU, LAPIC/IOAPIC/PIC, PIT, MCE, MSR, XSAVE, and ptrace-like debug facilities.

Risks and test signals: Risks are ABI layout drift, insufficient padding validation, migration incompatibility, malicious userspace state, nested-state size errors, protected-VM launch mismatch, and 32-bit userspace pointer handling. Test KVM selftests, QEMU boot/migration, nested VMX/SVM migration, Xen HVM tests, SEV/SNP/TDX launch paths, MSR filter tests, PMU event filters, XSAVE dynamic-size tests, MCE injection, and ioctl ABI size assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/uapi/asm/kvm.h -->
