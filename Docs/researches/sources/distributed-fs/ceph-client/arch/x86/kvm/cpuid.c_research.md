# sources/distributed-fs/ceph-client/arch/x86/kvm/cpuid.c

## Purpose

`cpuid.c` owns x86 KVM's CPUID model construction, userspace CPUID ioctl plumbing, vCPU CPUID installation, runtime CPUID adjustments, and CPUID instruction emulation. It bridges raw host CPUID, KVM's feature support policy, kernel feature state, vendor hooks, paravirtual leaves, and the guest-visible `struct kvm_cpuid_entry2` array stored on each vCPU.

## Important APIs, Types, And Functions

- Global state: `kvm_cpu_caps[]`, `kvm_is_configuring_cpu_caps`, and cached `xstate_sizes[]`.
- CPUID lookup and sizing: `kvm_find_cpuid_entry2()`, `kvm_init_xstate_sizes()`, `xstate_required_size()`.
- vCPU installation: `kvm_check_cpuid()`, `kvm_set_cpuid()`, `kvm_vcpu_after_set_cpuid()`.
- ABI handlers: `kvm_vcpu_ioctl_set_cpuid()`, `kvm_vcpu_ioctl_set_cpuid2()`, `kvm_vcpu_ioctl_get_cpuid2()`, `kvm_dev_ioctl_get_cpuid()`.
- Capability initialization: `kvm_initialize_cpu_caps()` with the `kvm_cpu_cap_init()` feature-class macros.
- Supported/emulated CPUID generation: `__do_cpuid_func()`, `do_cpuid_func()`, `get_cpuid_func()`.
- Guest CPUID execution: `kvm_cpuid()` and `kvm_emulate_cpuid()`.

## Control Flow

Global feature setup starts at `kvm_initialize_cpu_caps()`, which combines KVM policy, raw host CPUID, Linux feature state, synthesized mitigation bits, passthrough bits, and emulated bits. Follow-up policy clears or sets features based on TDP, OSPKE, shadow stacks, smaller MAXPHYADDR emulation, mitigation availability, PMU support, SEV/SGX/SVM vendor enablement, and MSR sanity checks.

Userspace supported-CPUID discovery enters through `kvm_dev_ioctl_get_cpuid()`. It allocates a bounded array, validates padding for emulated CPUID, walks the basic, extended, Centaur, and KVM hypervisor bases, and uses `__do_cpuid_func()` to pin to one CPU while reading and overriding host leaves. Indexed leaves append subleaf entries under architectural and KVM limits.

vCPU CPUID installation copies userspace entries, then `kvm_set_cpuid()` swaps the incoming array into `vcpu->arch.cpuid_entries`. If the vCPU can no longer change CPUID, the incoming model must compare equal after runtime updates. Otherwise KVM initializes vendor/paravirtual side state, validates dynamic xfeatures, and calls `kvm_vcpu_after_set_cpuid()`. Failures restore the previous CPUID array and cached capabilities.

Guest CPUID execution through `kvm_cpuid()` updates dirty dynamic bits, finds an exact function/index entry, optionally applies Intel-style out-of-range fallback, copies registers, and applies runtime adjustments for TSX masking, Hyper-V invariant TSC suppression, and Xen TSC leaves. `kvm_emulate_cpuid()` adds CPUID-fault checks and writes guest GPRs.

## State And Persistence

Persistent global state is `kvm_cpu_caps[]` and init-only xstate size metadata. Persistent per-vCPU state includes the CPUID entry array, `cpu_caps`, dynamic-bit dirty flag, supported XCR0/XSS masks, paravirtual feature cache, AMD-compatible flag, max physical address, and reserved GPA bit mask.

Runtime CPUID bits are KVM-owned even though they live in the vCPU CPUID entries. `kvm_update_cpuid_runtime()` rewrites OSXSAVE, APIC, MWAIT, OSPKE, and XSAVE size fields from CR4, APIC base, `IA32_MISC_ENABLE`, XCR0, and IA32_XSS.

## Dependencies And Integration Points

The file integrates with FPU xstate code, LAPIC, MMU, PMU, Hyper-V, Xen, SGX, vendor KVM x86 ops, tracepoints, and user-copy allocation helpers. Major downstream effects include `kvm_pmu_refresh()`, `kvm_hv_set_cpuid()`, `kvm_x86_call(vcpu_after_set_cpuid)`, `kvm_mmu_after_set_cpuid()`, and `KVM_REQ_RECALC_INTERCEPTS`.

## Risks And Maintenance Notes

- CPUID feature masks are ABI policy; advertising a feature before all virtualization support exists can expose unusable guest state.
- Dynamic bits must be refreshed before comparing, copying, or emulating CPUID.
- `kvm_find_cpuid_entry2()` is linear and guarded against IRQ-disabled hotpath use.
- Post-run CPUID changes are only tolerated when effectively equal; changing MAXPHYADDR, GBPAGES, topology, or nested behavior after run is unsafe.
- XSTATE correctness depends on consistency among CPUID.0xD, filtered xcr0/xss masks, and guest FPU sizing.

## Test Signals

KVM selftests should cover supported/emulated CPUID ioctls, set/get CPUID, post-run equality behavior, indexed and out-of-range leaves, CPUID faulting, TSX/invariant-TSC runtime masking, XSAVE/XFD sizing, MAXPHYADDR/GBPAGES/LA57 behavior, PMU leaves, and mitigation feature exposure.
