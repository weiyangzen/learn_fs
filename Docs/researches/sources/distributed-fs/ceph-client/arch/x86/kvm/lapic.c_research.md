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
