# Research: sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/processor.h

# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/include/x86/processor.h

Purpose: broad x86 processor support header for KVM selftests. It defines CPUID feature/property descriptors, CPU/PMU feature probes, x86 state structs, low-level instruction helpers, MSR/XSAVE/CPUID ioctl wrappers, exception handling/fixup machinery, KVM module parameter probes, hypercall helpers, interrupt helpers, and page-table/TDP utilities.

Important APIs/types/functions: host globals `host_cpu_is_*`, `guest_tsc_khz`; `struct xstate`, `struct kvm_x86_cpu_feature`, `struct kvm_x86_cpu_property`, `struct kvm_x86_pmu_feature`, many `X86_FEATURE_*` and `X86_PROPERTY_*` constants, `struct gpr64_regs`, `struct desc64`, `struct desc_ptr`, `struct kvm_x86_state`, register/MSR helpers (`rdtsc`, `rdmsr`, `wrmsr`, CR getters/setters, `xgetbv`, `xsetbv`, `wrpkru`), CPUID helpers, SSE read/write helpers, `udelay`, state save/load/cleanup, MSR list helpers, vCPU MSR/debug/xsave/xcrs wrappers, CPUID mutation helpers, exception structs and `vm_install_exception_handler`, `KVM_ASM_SAFE` families, safe `rdmsr/rdpmc/xgetbv/wrmsr/xsetbv`, KVM module parameter probes, `kvm_hypercall`, `xen_hypercall`, `safe_halt`, STI/CLI helpers, `vm_xsave_require_permission`, page-level/PTE predicates, TDP/EPT mapping declarations, CR0/PFERR constants, and `sys_clocksource_is_based_on_tsc`.

Control flow and state: host-side tests query KVM-supported CPUID/MSRs, configure vCPUs, save/load x86 state, and install guest exception handlers. Guest-side inline assembly reads/writes CPU state, executes fault-safe instructions through register-based fixup, and triggers hypercalls. Page-table helpers inspect and build guest and TDP/EPT mappings using masks stored in `kvm_mmu_arch`.

Dependencies and integration: depends on Linux MSR/KVM para headers, `kvm_util.h`, and `ucall_common.h`. It is the root dependency for x86 APIC, Hyper-V, VMX, SVM, SEV, PMU, MCE, and SMM helpers.

Risks: this header is dense and ABI-sensitive. CPUID descriptor packing, safe-assembly register conventions, MSR durability checks, XSAVE sizing, and page-table masks must all match KVM and CPU behavior. Tests must use feature/property probes before executing optional instructions.

Test signals: almost all x86 KVM selftests validate this header. Strong signals include CPUID/MSR tests, xsave tests, exception-fixup tests, nested VMX/SVM tests, hypercall tests, TDP/EPT mapping tests, APIC/interrupt tests, and PMU tests.
