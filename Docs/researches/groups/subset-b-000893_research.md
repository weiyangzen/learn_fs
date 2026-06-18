# subset-b-000893 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/lapic.c -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/lapic.c

Purpose: Implements KVM's in-kernel x86 local APIC model. It emulates the guest-visible LAPIC register page, interrupt request/in-service state, APIC ID and logical destination routing, xAPIC/x2APIC MMIO and MSR accesses, local vector delivery, APIC timer backends, PV EOI/vAPIC synchronization, INIT/SIPI handling, APICv metadata updates, and migration-facing APIC state save/restore. It is the main runtime implementation behind the `lapic.h` API and is central to vCPU interrupt injection and guest timer behavior.

Important APIs/types/functions:

- APIC map maintenance: `kvm_recalculate_apic_map()`, `kvm_recalculate_phys_map()`, `kvm_recalculate_logical_map()`, and `kvm_apic_map_get_logical_dest()` build and publish an RCU-protected optimized map from physical/logical APIC destinations to `struct kvm_lapic *`. The map is disabled when aliasing or mixed logical modes make fast routing unsafe, and APICv inhibit reasons are updated to match.
- Destination matching and routing: `kvm_apic_match_dest()`, `kvm_irq_delivery_to_apic_fast()`, `__kvm_irq_delivery_to_apic()`, `kvm_intr_is_single_vcpu()`, `kvm_bitmap_or_dest_vcpus()`, `kvm_apic_send_ipi()`, and `kvm_pv_send_ipi()` convert APIC message fields into target vCPUs. The fast path uses the optimized APIC map; fallback scans all vCPUs and handles broadcasts, shorthand destinations, and lowest-priority arbitration.
- Interrupt state: `__kvm_apic_update_irr()`, `kvm_apic_update_irr()`, `kvm_apic_clear_irr()`, `apic_set_isr()`, `apic_clear_isr()`, `apic_find_highest_irr()`, `apic_find_highest_isr()`, and `kvm_apic_ack_interrupt()` maintain IRR/ISR/TMR bitmaps, highest ISR caches, pending IRR hints, and APICv hardware ISR updates.
- Acceptance/delivery: `__apic_accept_irq()` handles fixed, lowest-priority, remote-read, SMI, NMI, INIT, SIPI, and ExtINT modes. `kvm_apic_set_irq()` wraps it for generic LAPIC delivery, and `kvm_apic_local_deliver()` delivers LVT events such as timer, LINT, performance counter, and NMI watchdog events.
- Register emulation: `kvm_lapic_reg_read()`, `kvm_lapic_reg_write()`, `apic_mmio_read()`, `apic_mmio_write()`, `kvm_lapic_readable_reg_mask()`, `kvm_x2apic_msr_read()`, `kvm_x2apic_msr_write()`, `kvm_hv_vapic_msr_read()`, and `kvm_hv_vapic_msr_write()` implement APIC MMIO, x2APIC MSR, and Hyper-V vAPIC register semantics.
- Timer implementation: `start_apic_timer()`, `restart_apic_timer()`, `start_sw_tscdeadline()`, `start_sw_period()`, `start_hv_timer()`, `cancel_apic_timer()`, `apic_timer_expired()`, `kvm_inject_apic_timer_irqs()`, `kvm_wait_lapic_expire()`, `kvm_lapic_expired_hv_timer()`, and switch/restart helpers coordinate hrtimer, hardware VMX/SVM timer, posted timer interrupt, one-shot, periodic, and TSC-deadline modes.
- Lifecycle/state: `kvm_create_lapic()`, `kvm_free_lapic()`, `kvm_lapic_reset()`, `kvm_apic_set_base()`, `kvm_apic_get_state()`, `kvm_apic_set_state()`, `kvm_apic_update_apicv()`, `kvm_alloc_apic_access_page()`, and `kvm_inhibit_apic_access_page()` allocate APIC structures, reset architectural registers, expose migration state, and coordinate APIC access page behavior.
- PV/vAPIC integration: `kvm_lapic_set_vapic_addr()`, `kvm_lapic_sync_from_vapic()`, `kvm_lapic_sync_to_vapic()`, `kvm_lapic_set_pv_eoi()`, and internal PV EOI helpers synchronize guest memory caches with APIC TPR/EOI state.

Control flow:

Interrupt routing begins with an APIC message, either from an IPI, IOAPIC/MSI path, paravirtual IPI, local LVT source, or timer expiry. For external routing, `kvm_irq_delivery_to_apic()` first tries `__kvm_irq_delivery_to_apic_fast()`, which reads the RCU APIC map and resolves a bitmap/array of destination LAPICs. If the optimized map cannot represent the request, the slow path scans every present vCPU, applies `kvm_apic_match_dest()`, and either injects all fixed targets or selects a lowest-priority target through vector hashing or arbitration priority. A selected target reaches `kvm_apic_set_irq()` and `__apic_accept_irq()`, which updates TMR for trigger mode and delegates actual fixed/lowest delivery to the architecture backend through `kvm_x86_call(deliver_interrupt)`, or queues special events such as INIT/SIPI/NMI/SMI.

APIC map control flow is output-driven by register/base changes. Writes to APIC ID, LDR, DFR, SPIV software-enable, or APIC base set `kvm->arch.apic_map_dirty` to `DIRTY`. `kvm_recalculate_apic_map()` serializes updates with `apic_map_lock`, allocates a map large enough for xAPIC IDs and current x2APIC IDs, populates physical and logical maps, disables fast maps on aliasing, publishes through RCU, and requests IOAPIC rescans. APICv inhibit reasons are kept in sync with physical ID aliasing, logical ID aliasing, and guest-modified xAPIC IDs.

Register accesses split by mode. Legacy xAPIC MMIO is accepted only when the APIC is hardware-enabled and not in x2APIC mode; otherwise KVM either returns `-EOPNOTSUPP` or, for the LAPIC MMIO hole quirk, returns all ones on reads and ignores writes. x2APIC access uses MSR helpers that map APIC MSR numbers to register offsets. Most registers are 32-bit; ICR is handled as 64-bit in x2APIC and may be stored internally as split or combined depending on `kvm_x86_ops.x2apic_icr_is_split`.

Timer control flow starts when LVTT, TMICT, TDCR, or TSC-deadline MSR state changes. KVM computes nanosecond periods from APIC bus cycles and divide count, clamps too-fast periodic timers, computes host hrtimer expiration and guest TSC deadline, and attempts to program a hardware virtualization timer if available. If hardware timer setup is unavailable or unsuitable, it falls back to hrtimer. Expiration either injects immediately for in-guest APICv/posting cases or increments `lapic_timer.pending`, requests unblock/event work, and kicks the vCPU. Periodic timers advance the target expiration without trying to catch up for long pauses.

State and persistence behavior:

- The emulated APIC register page lives in `apic->regs`, a page laid out like guest LAPIC MMIO state because hardware virtualization may directly consume selected fields.
- Per-vCPU persistent LAPIC software state includes `base_address`, `sw_enabled`, `apicv_active`, `irr_pending`, `lvt0_in_nmi_mode`, `guest_apic_protected`, `isr_count`, `highest_isr_cache`, `pending_events`, `sipi_vector`, `nr_lvt_entries`, and timer state in `struct kvm_timer`.
- Per-VM derived state includes `kvm->arch.apic_map`, dirty state, APICv inhibit reasons, disabled LAPIC detection, APIC access page memslot flags, `vapics_in_nmi_mode`, and APIC bus cycle timing.
- Migration-visible state is mostly the APIC register page plus derived timer current count. `kvm_apic_get_state()` copies registers and synthesizes `APIC_TMCCT`; `kvm_apic_set_state()` restores registers, fixes x2APIC ID/LDR/ICR representation, rebuilds maps, restarts timers from `APIC_TMCCT`, refreshes APICv metadata, and restores RTC EOI tracking when needed.
- PV EOI and vAPIC state persist via guest memory caches initialized through `kvm_gfn_to_hva_cache_init()`. Host-side attention bits decide when to sync TPR and EOI state from/to guest memory.

Dependencies and integration points:

- Architecture backends enter through `kvm_x86_ops` and `kvm_x86_call()` for interrupt delivery, APICv state restore, hardware APIC ISR updates, virtual APIC mode changes, MMU/access page behavior, hardware timers, nested-event checks, and SIPI vector delivery.
- IRQ chip integration uses `irq.h`, `ioapic.h`, IOAPIC EOI update paths, split irqchip exits to userspace, RTC EOI tracking, MSI/IRQ routing helpers, and `ioapic_in_kernel()`/`irqchip_split()` mode checks.
- Hypervisor enlightenments include Hyper-V SynIC EOI handling, Hyper-V vAPIC MSR access, KVM PV EOI, paravirtual IPI, and Xen software LAPIC enable notification.
- APICv and posted interrupts integrate with posted-interrupt PIR harvesting, APICv inhibit state, `pi_inject_timer`, APIC access page allocation/inhibition, and guest protected APIC behavior.
- Scheduler/timer dependencies include hrtimer, preemption disabling around hardware timer programming, vCPU kick/unblock requests, TSC scaling/conversion helpers, and monotonic host time.

Risks:

- Destination aliasing and xAPIC/x2APIC compatibility are subtle. Wrong APIC map invalidation or alias handling can drop interrupts, deliver to the wrong vCPU, or leave APICv enabled when hardware acceleration cannot match architectural behavior.
- Concurrency is high risk: APIC maps are RCU-published, dirty transitions use atomics with acquire/release ordering, IRR/PIR updates use atomic compare/exchange, SIPI vector handoff uses barriers, and timer paths run from hrtimer callbacks, vCPU run context, and preemption-disabled hardware timer programming.
- Timer advancement and TSC scaling can affect guest-visible latency. Incorrect advance adjustment, missed cancellation, or expired deadline handling can make guest timers early, late, duplicated, or lost.
- State restore has many derived fields. Failing to recompute PPR, divide count, APICv state, NMI-watchdog counts, APIC maps, or timers after migration can create bugs that only appear after live migration or userspace `KVM_SET_LAPIC`.
- MMIO/MSR access rules are architectural. x2APIC reserved bits, read-only ID/LDR, ICR layout, APIC base transition constraints, and legacy LAPIC MMIO hole quirks need exact behavior for guest OS compatibility.
- PV EOI is intentionally opportunistic. Enabling it when IRR/ISR/IOAPIC conditions are unsafe can lose level-triggered EOIs; disabling it too aggressively hurts performance but is safer.

Test signals:

- KVM selftests for APIC/x2APIC state, APIC base mode transitions, APIC ID aliasing, PV IPI, INIT/SIPI, nested virtualization interrupt acknowledgement, and `KVM_GET/SET_LAPIC`.
- Guest OS boot and SMP bring-up with xAPIC, x2APIC, CPU hotplug, broadcast IPIs, logical destination modes, and disabled/reenabled APICs.
- Timer tests covering one-shot, periodic, TSC-deadline, TSC scaling, halted guest timer delivery, posted timer interrupts, hardware timer fallback, migration while timers are active, and minimum periodic timer clamping.
- IOAPIC/MSI tests for level-triggered EOI, split irqchip userspace EOI exits, directed EOI/suppress-broadcast behavior, RTC interrupt tracking, and Hyper-V SynIC auto EOI vectors.
- Tracepoints such as `trace_kvm_apic_accept_irq`, `trace_kvm_apic_ipi`, `trace_kvm_apic_read/write`, `trace_kvm_eoi`, `trace_kvm_hv_timer_state`, `trace_kvm_wait_lapic_expire`, and `trace_kvm_pv_eoi` are useful runtime diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/lapic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/lapic.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/lapic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu.h -->
# sources/distributed-fs/ceph-client/arch/x86/kvm/mmu.h

Purpose: Declares shared KVM x86 MMU constants, helpers, and entry points used by paging, shadow paging, TDP/NPT/EPT, page-fault handling, nested translation, MMIO SPTE encoding, and memory-slot accounting. The file is a compact contract between the MMU implementation and vCPU/core x86 code rather than a full implementation.

Important APIs/types/functions:

- Page table bit definitions: `PT_PRESENT_MASK`, writable/user/PWT/PCD/accessed/dirty/page-size/PAT/global/NX masks and shifts, root-level constants for 5-level, 4-level, 32-bit, and PAE paging, and role-bit masks for CR0, CR4, and EFER define the guest paging metadata that feeds MMU roles and permissions.
- `rsvd_bits()` builds inclusive reserved-bit masks while compile-time checking constant ranges. It is used by paging code that validates guest entries and constructs reserved-bit masks.
- `kvm_mmu_max_gfn()` returns the maximum GFN KVM should map, based on host MAXPHYADDR for TDP or 52-bit GPAs for non-TDP shadow paging.
- MMU setup declarations include `kvm_mmu_get_max_tdp_level()`, MMIO/SPTE mask setters, memory encryption SPTE mask setup, EPT mask setup, `kvm_init_mmu()`, `kvm_init_shadow_npt_mmu()`, and `kvm_init_shadow_ept_mmu()`.
- Fault and root lifecycle APIs include `kvm_can_do_async_pf()`, `kvm_handle_page_fault()`, `kvm_mmu_load()`, `kvm_mmu_unload()`, `kvm_mmu_reload()`, `kvm_mmu_free_obsolete_roots()`, `kvm_mmu_sync_roots()`, `kvm_mmu_sync_prev_roots()`, and `kvm_mmu_track_write()`.
- Permission helpers include `kvm_get_pcid()`, `kvm_get_active_pcid()`, `kvm_get_active_cr3_lam_bits()`, `kvm_mmu_load_pgd()`, `kvm_mmu_refresh_passthrough_bits()`, and `permission_fault()`.
- VM/MMU lifecycle and accounting declarations include `kvm_mmu_post_init_vm()`, `kvm_mmu_pre_destroy_vm()`, `kvm_shadow_root_allocated()`, `kvm_memslots_have_rmaps()`, `gfn_to_index()`, `kvm_mmu_slot_lpages()`, and `kvm_update_page_stats()`.
- Nested/direct-private helpers include `translate_nested_gpa()`, `kvm_translate_gpa()`, `kvm_tdp_mmu_map_private_pfn()`, `kvm_has_mirrored_tdp()`, `kvm_gfn_direct_bits()`, `kvm_is_addr_direct()`, and `kvm_is_gfn_alias()`.

Control flow:

The common vCPU run path calls `kvm_mmu_reload()` before entering the guest when requests or invalid roots require reload. That helper first handles `KVM_REQ_MMU_FREE_OBSOLETE_ROOTS`, then checks `vcpu->arch.mmu->root.hpa`; if no valid root exists, it calls `kvm_mmu_load()`. When a guest memory access faults, x86 fault handling enters `kvm_handle_page_fault()`, which relies on the role/permission helpers and implementation functions declared here.

Permission checking flows through `permission_fault()`. The caller supplies a page table access mask, pkey, and page-fault access bits. The helper strips nested paging details, reads guest RFLAGS for SMAP override state, refreshes passthrough CR0.WP-derived metadata when TDP may have stale state, indexes the MMU permissions table, then layers PKRU checks if `mmu->pkru_mask` is active. It returns zero for allowed access or a synthesized page-fault error code for denied access.

Nested translation flows through `kvm_translate_gpa()`. Normal MMUs return the GPA unchanged; the nested MMU path calls `translate_nested_gpa()` to translate L2 GPA through L1-controlled nested paging and fill an exception if translation fails. Direct-bit helpers support private/shared memory encodings, including TDX mirrored TDP handling.

State and persistence behavior:

- The header itself stores no state, but it defines access to persistent per-vCPU MMU roots (`vcpu->arch.mmu->root.hpa`, root role, guest/nested MMU pointers), per-VM shadow-root allocation state, page stats, memory-slot sizes, private/direct GFN bits, and global MMU feature booleans such as `enable_mmio_caching`, `tdp_enabled`, and `tdp_mmu_enabled`.
- `kvm_shadow_root_allocated()` uses acquire ordering so readers that observe the flag also observe related shadow-root pointers, paired with release storage in the allocator.
- `kvm_memslots_have_rmaps()` encodes whether reverse maps must exist, depending on TDP MMU enablement and whether shadow roots have ever been allocated.
- Page statistics are updated through `kvm_update_page_stats()` with atomic64 counters indexed by page level.

Dependencies and integration points:

- Includes `linux/kvm_host.h`, `kvm_cache_regs.h`, `x86.h`, and `cpuid.h`; depends on common x86 state helpers such as `kvm_read_cr3()`, `kvm_is_cr4_bit_set()`, `guest_cpu_cap_has()`, `kvm_x86_call()`, and host capability metadata.
- Integrates with EPT/NPT/TDP MMU implementations, legacy shadow paging, nested virtualization, async page faults, MMIO emulation, memory encryption, TDX private memory mapping, PKU/PKRU, SMAP/SMEP/WP permission modeling, large page accounting, and VM init/destroy paths.
- Uses Linux/KVM memory-slot structures and KVM hugepage level macros for reverse-map and large-page indexing.

Risks:

- Permission modeling is security-sensitive. Mistakes in `permission_fault()` or its inputs can allow illegal guest access or inject incorrect page faults, especially with SMAP, CR0.WP passthrough, PKU, nested MMU, or implicit supervisor accesses.
- `kvm_mmu_max_gfn()` intentionally uses host MAXPHYADDR for TDP. Changing that contract can cause KVM to install SPTEs for GPAs hardware cannot represent, or reject valid non-TDP shadow translations.
- Root reload logic assumes `root.hpa` validity is sufficient even with mirror roots. Any future root representation changes must preserve the documented invariant.
- Memory ordering around `shadow_root_allocated` prevents readers from seeing uninitialized shadow-root state; weakening it could create rare races in memslot/rmap decisions.
- Direct/private GFN helpers are small but important for confidential-computing guests. Misclassifying direct bits or aliases can map private/shared pages incorrectly.

Test signals:

- KVM unit/selftests for page faults, MMIO SPTEs, reserved-bit faults, CR0.WP, CR4.SMAP/SMEP/PKE, PKRU, NX, PCID, LAM CR3 bits, and async page faults.
- Nested virtualization tests for EPT/NPT shadow MMUs and `translate_nested_gpa()` exception behavior.
- TDP MMU and non-TDP builds/runs, including 5-level paging, huge pages, rmap allocation, obsolete-root freeing, root reload after invalidation, and memory-slot resizing.
- Confidential-computing/private-memory tests for mirrored TDP, direct GFN bits, aliases, and `kvm_tdp_mmu_map_private_pfn()`.
- Runtime signals include correct `kvm->stat.pages[]` accounting, absence of reserved-bit fault regressions, successful VM init/destroy, and stable guest boot under memory pressure and migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/mmu.h -->
