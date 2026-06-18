# sources/distributed-fs/ceph-client/arch/x86/kvm/xen.h

Purpose: declares the KVM Xen emulation interface and provides fast inline predicates/stubs used by the wider x86 KVM core. It hides `CONFIG_KVM_XEN` differences while exposing event injection, attribute handling, hypercall-page configuration, VM/vCPU lifecycle, event-channel routing, and runstate helpers.

Important APIs/types/functions: under `CONFIG_KVM_XEN`, the header declares `kvm_xen_enabled`, `__kvm_xen_has_interrupt`, `kvm_xen_inject_pending_events`, `kvm_xen_inject_vcpu_vector`, VM/vCPU attr get/set functions, HVM attr get/set functions, event-channel send/setup functions, hypercall-page write/config functions, and lifecycle hooks. Inline helpers include `kvm_xen_sw_enable_lapic`, `kvm_xen_is_tsc_leaf`, `kvm_xen_msr_enabled`, `kvm_xen_is_hypercall_page_msr`, `kvm_xen_hypercall_enabled`, `kvm_xen_has_interrupt`, `kvm_xen_has_pending_events`, `kvm_xen_timer_enabled`, and `kvm_xen_has_pending_timer`. Stubs for disabled builds return false, zero, or success-compatible defaults. It also defines compatibility Xen vCPU info structures and runstate state-transition wrappers.

Control flow: most inline predicates first check the deferred static key to avoid overhead when no Xen VM is active. Interrupt detection requires active `vcpu_info_cache` and a configured upcall vector before calling the slow helper. LAPIC software-enable paths inject a pending Xen upcall if the vCPU becomes able to receive it. Runstate helpers call `kvm_xen_update_runstate()` with Xen `RUNSTATE_running` or `RUNSTATE_runnable`, with a warning if preemption state is inconsistent.

State and persistence behavior: the header itself persists nothing, but reads and mutates `vcpu->arch.xen` and `kvm->arch.xen` fields via inline helpers. When Xen is compiled out, callers get no-op behavior without changing state.

Dependencies/integration points: includes Xen CPUID/hypervisor ABI, pvclock ABI, Xen interface structures, jump-label ratelimit support, and KVM host structures. It is used by x86 KVM interrupt, MSR, CPUID, run loop, LAPIC, and hypercall code.

Risks: static-key gating must remain consistent with VM config refcounting in `xen.c`; otherwise Xen paths can be skipped or enabled unnecessarily. Stub return values are ABI-visible through KVM behavior, so disabled-config semantics must remain conservative. `kvm_xen_is_tsc_leaf()` must match Xen CPUID base/limit logic exactly.

Test signals: compile both `CONFIG_KVM_XEN=y` and `n`. Exercise CPUID Xen TSC leaf detection, hypercall-page MSR checks, LAPIC enable delivery, pending timer checks, and non-Xen VM fast paths.
