# sources/distributed-fs/ceph-client/arch/x86/kvm/svm/avic.c

## Purpose
`avic.c` implements AMD SVM AVIC/x2AVIC support for KVM: hardware-accelerated local APIC register virtualization, IPI delivery, posted interrupt integration with AMD IOMMU, and runtime APICv activation/deactivation. It owns the per-VM AVIC logical/physical ID tables, VM IDs used in IOMMU GA log tags, x2APIC MSR pass-through policy, and vCPU load/put transitions that publish the host physical CPU to AVIC hardware.

## Important APIs, types, and functions
- Module parameters: `avic`, `enable_ipiv`, and unsafe `force_avic` control feature enablement. `avic_param_set()` accepts `auto`; `avic_want_avic_enabled()` turns auto into the Zen4+/x2AVIC default.
- VM lifecycle: `avic_vm_init()`, `avic_alloc_physical_id_table()`, and `avic_vm_destroy()` allocate/free the logical ID table, physical ID table, assign a nonzero `avic_vm_id`, and maintain `svm_vm_data_hash`.
- vCPU lifecycle and VMCB setup: `avic_init_vcpu()`, `avic_init_backing_page()`, `avic_init_vmcb()`, `avic_activate_vmcb()`, and `avic_deactivate_vmcb()` program VMCB AVIC fields, APIC access page requirements, APICv inhibit state, CR8 intercepts, and x2APIC MSR intercepts.
- Interrupt delivery: `avic_incomplete_ipi_interception()`, `avic_ring_doorbell()`, `avic_kick_target_vcpus_fast()`, `avic_kick_target_vcpus()`, and physical/logical kick helpers emulate or complete IPIs that hardware cannot deliver.
- APIC register synchronization: `avic_unaccelerated_access_interception()`, `avic_unaccel_trap_write()`, `avic_handle_ldr_update()`, `avic_handle_dfr_update()`, and `avic_apicv_post_state_restore()` keep the AVIC logical table aligned with guest APIC state.
- IOMMU posted interrupts: `avic_pi_update_irte()`, `avic_update_iommu_vcpu_affinity()`, `__avic_vcpu_load()`, `__avic_vcpu_put()`, `avic_vcpu_blocking()`, and `avic_vcpu_unblocking()` update AMD IOMMU IRTE state and per-vCPU AVIC physical entries.
- Hardware registration: `avic_hardware_setup()` and `avic_hardware_unsetup()` enable AVIC/x2AVIC and register/unregister the AMD IOMMU GA log notifier.

## Control flow
Initialization starts at hardware setup, which validates NPT, AVIC CPUID, SNP-host constraints, x2AVIC support, and erratum-driven `enable_ipiv` policy before registering `avic_ga_log_notifier()`. VM initialization allocates logical and physical APIC ID tables and inserts the VM into the VM-ID hash. vCPU initialization creates a valid AVIC backing page entry indexed by vCPU ID unless the ID exceeds the hardware maximum, in which case it inhibits APICv immediately.

On VMCB initialization or APICv refresh, KVM toggles VMCB control bits, CR8 intercepts, and x2APIC MSR interception according to `kvm_vcpu_apicv_active()` and current APIC mode. Running vCPUs go through `avic_vcpu_load()` and `avic_vcpu_put()`; these publish or clear `AVIC_PHYSICAL_ID_ENTRY_IS_RUNNING`, record host APIC IDs, and update IOMMU posted-interrupt affinity under `ir_list_lock`. Blocking vCPUs clear `IsRunning` and set synthetic GA-log behavior so external interrupts wake them through the GA log path.

IPI VM exits enter `avic_incomplete_ipi_interception()`. Invalid target or unsupported interrupt type exits are emulated through the local APIC. Target-not-running exits rely on hardware-populated IRR bits and only wake affected vCPUs. Fast path matching avoids scanning all vCPUs when destination APIC IDs map directly; slow path uses `kvm_apic_match_dest()`.

## State and persistence behavior
Persistent VM state includes `avic_vm_id`, `avic_logical_id_table`, and `avic_physical_id_table`. Per-vCPU state includes cached physical ID entry, saved LDR/DFR values, `x2avic_msrs_intercepted`, and the per-vCPU `ir_list` of IRQ bypass entries. The VM-ID hash is global and protected by `svm_vm_data_hash_lock`; per-vCPU IRTE metadata is protected by `ir_list_lock`. The backing page address is derived from the local APIC register page and tagged through `__sme_set()`.

AVIC physical table entries are updated on scheduling and blocking transitions, not just on APICv enablement. Logical table entries are invalidated and rewritten as LDR/DFR changes are trapped. Hardware state in VMCB control fields is marked dirty via `vmcb_mark_dirty()` where needed.

## Dependencies and integration points
This file integrates with KVM LAPIC/APICv (`lapic.h`, `kvm_apic_*`, `kvm_set_apicv_inhibit()`), AMD SVM VMCB management (`svm.h`, intercept helpers), AMD IOMMU IRQ remapping (`irq_set_vcpu_affinity()`, `amd_iommu_*`, GA log notifier), IRQ bypass/irqfd, CPU feature probing, SEV-ES/SNP constraints, and KVM request handling (`KVM_REQ_TLB_FLUSH_CURRENT`, `KVM_REQ_APICV_UPDATE`). It also emits AVIC tracepoints for GA log, doorbell, incomplete IPI, and slow-path wake decisions.

## Risks and edge cases
- Correctness depends on vCPU ID/APIC ID identity; oversized IDs inhibit APICv, and x2AVIC sizing must match table allocation.
- Doorbell signaling can race with migration; the code intentionally tolerates stale CPU signaling because a migrated vCPU will process interrupts on next VMRUN.
- IOMMU IRTE metadata must be synchronized with schedule-in/out and blocking transitions; missed `ir_list_lock` ordering could leave stale pCPU or GA-log state.
- Family 17h IPI virtualization is disabled for erratum 1235, showing sensitivity to memory ordering around `IsRunning`.
- Nested virtualization inhibits APICv, and nested MSR bitmap ownership can prevent x2APIC intercept updates from being applied.
- SNP hosts without `HvInUseWrAllowed` disable AVIC to avoid unsafe host/guest hypervisor-in-use writes.

## Test signals
Useful tests include KVM selftests for APICv/AVIC inhibit reasons, xAPIC and x2APIC IPI delivery, blocking vCPU wakeups, irqfd/posted interrupt affinity migration, nested virtualization APICv disablement, CPU hotplug or vCPU migration stress, and boot-time parameter combinations (`avic=auto`, disabled NPT, forced AVIC, SNP host). Tracepoints `kvm_avic_*` and IOMMU posted interrupt behavior provide runtime evidence.
