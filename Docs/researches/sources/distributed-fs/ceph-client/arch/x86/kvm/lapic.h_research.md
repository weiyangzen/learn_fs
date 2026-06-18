# sources/distributed-fs/ceph-client/arch/x86/kvm/lapic.h

Purpose: Declares KVM's x86 local APIC interface and core LAPIC data structures. It is the contract shared by the LAPIC implementation, vCPU run loop, irqchip/IOAPIC code, architecture backends, Hyper-V/Xen/PV paths, migration state handling, and APIC timer code.

Important APIs/types/functions:

- Constants and modes: `KVM_APIC_INIT`, `KVM_APIC_SIPI`, destination shorthand masks, `APIC_BUS_CYCLE_NS_DEFAULT`, broadcast IDs, and `X2APIC_MSR()` encode APIC event bits, routing encodings, timing defaults, and x2APIC MSR mapping.
- `enum lapic_mode` models disabled, invalid, xAPIC, and x2APIC APIC base combinations using `MSR_IA32_APICBASE_ENABLE` and `X2APIC_ENABLE`.
- `enum lapic_lvt_entry` plus `APIC_LVTx()` provide stable indexing for timer, thermal, performance counter, LINT0, LINT1, error, and CMCI LVT entries.
- `struct kvm_timer` holds LAPIC timer runtime state: host hrtimer, nanosecond period, target expiration, LVTT timer mode, allowed timer mode mask, TSC deadline, expired deadline for advance/wait logic, adaptive timer advance, pending expiration count, and whether a hardware virtualization timer is active.
- `struct kvm_lapic` holds the complete per-vCPU LAPIC software object: MMIO base, `kvm_io_device`, embedded `kvm_timer`, divide count, owning vCPU, APICv/protection flags, software-enable state, pending IRR hint, LVT0 NMI-watchdog state, ISR caches, guest register page, vAPIC address/cache, pending INIT/SIPI bits, SIPI vector, and LVT count.
- Public lifecycle and state APIs include `kvm_create_lapic()`, `kvm_free_lapic()`, `kvm_lapic_reset()`, `kvm_apic_set_base()`, `kvm_apic_get_state()`, `kvm_apic_set_state()`, `kvm_apic_set_version()`, and `kvm_apic_after_set_mcg_cap()`.
- Public interrupt APIs include `kvm_apic_has_interrupt()`, `kvm_apic_ack_interrupt()`, `kvm_apic_accept_pic_intr()`, `kvm_apic_accept_events()`, `kvm_apic_set_irq()`, `kvm_apic_local_deliver()`, `kvm_irq_delivery_to_apic_fast()`, `__kvm_irq_delivery_to_apic()`, `kvm_apic_send_ipi()`, `kvm_intr_is_single_vcpu()`, and `kvm_bitmap_or_dest_vcpus()`.
- Register/timer/enlightenment APIs include CR8/TPR/EOI helpers, x2APIC and Hyper-V vAPIC MSR read/write helpers, vAPIC sync helpers, PV EOI setup, TSC-deadline helpers, APIC access page helpers, APICv update, and LAPIC timer backend switch/restart helpers.

Control flow:

Most consumers treat this header as the front door to LAPIC behavior. vCPU creation calls `kvm_create_lapic()`, reset flows call `kvm_lapic_reset()`, the vCPU entry path asks `kvm_apic_has_interrupt()` and acknowledges with `kvm_apic_ack_interrupt()`, IOAPIC/MSI/IPI paths call the delivery functions, and userspace migration calls `kvm_apic_get_state()`/`kvm_apic_set_state()`. Inline predicates short-circuit common hot paths by using static keys for no-APIC, hardware-disabled APIC, and software-disabled APIC cases.

The header's inline state helpers define the layering used elsewhere: `lapic_in_kernel()` checks whether this vCPU has an in-kernel LAPIC, `kvm_apic_hw_enabled()` checks the APIC base enable bit only when the deferred static key says some APICs are disabled, `kvm_apic_sw_enabled()` checks `sw_enabled` only when needed, `kvm_apic_present()` combines in-kernel and hardware-enabled state, and `kvm_lapic_enabled()` adds software enable. `apic_x2apic_mode()` and `kvm_get_apic_mode()` derive mode directly from `vcpu->arch.apic_base`.

State and persistence behavior:

- `struct kvm_lapic` is per-vCPU state allocated by KVM when the irqchip is in kernel. The `regs` page persists the guest-visible APIC register file and is the main migration payload.
- `struct kvm_timer` persists guest timer programming across run-loop entries and migration restoration, but its host hrtimer/hardware timer backend is runtime state that must be restarted from guest-visible APIC registers.
- `pending_events` and `sipi_vector` persist INIT/SIPI events until `kvm_apic_accept_events()` consumes them. The header exposes helpers to test latched events while respecting SMM and architecture-specific blocking.
- Static keys declared here are global performance state. They let hot paths assume APICs are present/enabled unless some vCPU creates an exception.

Dependencies and integration points:

- Includes `kvm/iodev.h` for APIC MMIO registration, `linux/kvm_host.h` for vCPU/KVM core structures, `asm/apic.h` for APIC register constants, and local `hyperv.h`/`smm.h` for enlightenment and INIT/SIPI blocking integration.
- Used by LAPIC implementation, x86 vCPU event injection, IOAPIC, irq routing, posted interrupt/APICv code, nested virtualization, Hyper-V SynIC/vAPIC paths, Xen compatibility, and migration ioctls.
- The declarations depend on types such as `struct kvm_lapic_irq`, `struct kvm_lapic_state`, `struct rtc_status`, `gpa_t`, and `struct kvm_vcpu` that are defined in surrounding KVM headers.

Risks:

- Inline predicates are hot-path correctness gates. If static key accounting in the implementation drifts from these helpers, KVM can incorrectly assume an APIC is present, enabled, or accelerated.
- `struct kvm_lapic` layout and fields are consumed by architecture backends and APICv code; changing semantics without updating backend hooks can corrupt interrupt virtualization state.
- The register page layout comment matters: hardware virtualization can access selected fields directly, so `regs` must remain APIC-register-layout compatible.
- Timer fields mix guest state, host hrtimer state, and hardware timer state. Callers must use the implementation helpers rather than modifying fields directly.
- x2APIC mode helpers derive from APIC base state. Callers that cache mode across `kvm_apic_set_base()` transitions risk stale behavior.

Test signals:

- Build coverage across KVM, Hyper-V, Xen, APICv, 32-bit/64-bit x86, and machine-check CMCI configurations validates declarations and conditional LVT sizing.
- KVM selftests and guest tests should exercise all public APIs indirectly: LAPIC creation/free, APIC base changes, xAPIC/x2APIC MSRs, interrupt delivery, CR8/TPR, EOI, vAPIC sync, PV EOI, timer switching, and INIT/SIPI handling.
- Static-key edge cases need tests with in-kernel irqchip disabled, APIC hardware disabled, APIC software disabled, and APIC re-enabled after reset or APIC base writes.
