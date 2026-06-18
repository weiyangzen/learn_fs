# subset-b-000892 Research

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/hyperv.h -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/hyperv.h

### Purpose
`hyperv.h` is the internal interface for KVM's x86 Hyper-V emulation. It exposes TLFS-related constants, accessor helpers for VM/vCPU Hyper-V state, declarations for Hyper-V MSR, SynIC, stimer, CPUID, eventfd, TSC page, and nested TLB-flush services, plus no-op stubs when `CONFIG_KVM_HYPERV` is disabled.

### Important APIs, Types, And Functions
The header defines the Hyper-V CPUID signature, synthetic debugger CPUID leaves/MSRs, and debugger capability bits. Inline accessors include `to_kvm_hv()`, `to_hv_vcpu()`, `to_hv_synic()`, `hv_synic_to_vcpu()`, `to_hv_syndbg()`, `kvm_hv_get_vpindex()`, `to_hv_stimer()`, and `hv_stimer_to_vcpu()`. It declares `kvm_hv_set_msr_common()`, `kvm_hv_get_msr_common()`, `kvm_hv_hypercall()`, `kvm_hv_synic_set_irq()`, `kvm_hv_synic_send_eoi()`, `kvm_hv_process_stimers()`, `kvm_hv_setup_tsc_page()`, `kvm_hv_set_cpuid()`, `kvm_get_hv_cpuid()`, and `kvm_hv_vcpu_flush_tlb()`.

### Control Flow
Most helpers are simple accessors or feature gates. `kvm_hv_hypercall_enabled()` requires both vCPU Hyper-V enablement and a nonzero guest OS ID. `kvm_hv_synic_has_vector()` and `kvm_hv_synic_auto_eoi_set()` query bitmaps maintained by `hyperv.c`. `kvm_hv_invtsc_suppressed()` hides invariant TSC when the Hyper-V invariant-TSC control is exposed but not enabled. TLB helpers select the L1 or L2 flush FIFO based on guest mode, purge pending flushes on request consumption, detect Hyper-V TLB flush hypercalls from guest registers, and request FIFO re-checking on nested transitions.

### State, Persistence, And Dependencies
The header does not own storage, but its helpers directly expose fields in `kvm->arch.hyperv` and `vcpu->arch.hyperv`. It depends on `linux/kvm_host.h`, KVM x86 state from `x86.h`, Hyper-V TLFS constants from included kernel headers, kfifo-backed TLB flush FIFOs, and the vCPU request mechanism.

### Integration Points
Consumers include x86 MSR/hypercall handling, APIC EOI paths, CPUID setup, nested VMX/SVM paths, TSC page updates, IRQ routing, and timer processing. The stubs allow callers outside `CONFIG_KVM_HYPERV` blocks to compile while making Hyper-V features appear absent.

### Risks
The inline helpers assume `vcpu->arch.hyperv` is allocated before dereferencing except where explicitly guarded. Misusing `to_hv_synic()` or `to_hv_stimer()` before `kvm_hv_vcpu_init()` would fault. The invariant-TSC suppression logic must stay aligned with CPUID exposure, and TLB FIFO selection must match L1/L2 transitions or stale flush requests can be lost.

### Test Signals
Build both with and without `CONFIG_KVM_HYPERV`. Exercise Hyper-V disabled guests, CPUID enforcement, invariant TSC control, SynIC vector/AutoEOI queries, nested TLB flush request purging, and callers that use the no-op stubs under non-Hyper-V configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/hyperv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/i8254.c -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/i8254.c

### Purpose
`i8254.c` emulates the legacy 8253/8254 programmable interval timer for in-kernel KVM irqchip mode. It provides PIT channel state, port `0x40`-`0x43` and optional speaker port `0x61` emulation, hrtimer-backed channel 0 interrupts, PIT state ioctls, reinjection support, and integration with PIC/IOAPIC routing.

### Important APIs, Types, And Functions
Public entry points are `kvm_create_pit()`, `kvm_free_pit()`, `__kvm_migrate_pit_timer()`, `kvm_vm_ioctl_get_pit()`, `kvm_vm_ioctl_set_pit()`, `kvm_vm_ioctl_get_pit2()`, `kvm_vm_ioctl_set_pit2()`, and `kvm_vm_ioctl_reinject()`. Important internal routines include `pit_get_count()`, `pit_get_out()`, `pit_latch_count()`, `pit_latch_status()`, `pit_ioport_read()`, `pit_ioport_write()`, `create_pit_timer()`, `pit_timer_fn()`, `pit_do_work()`, `kvm_pit_ack_irq()`, and `kvm_pit_set_reinject()`.

### Control Flow
Guest command writes latch counts/status or configure channel mode, access size, and BCD flag. Count writes load the current channel, convert count zero to `0x10000`, and for channel 0 start a one-shot or periodic hrtimer depending on mode. The hrtimer callback marks pending reinjection ticks, queues a kthread worker, and re-arms itself for periodic mode. The worker pulses GSI 0 through `kvm_set_irq()` and optionally delivers NMI watchdog NMIs in virtual wire mode. Read paths return latched status/count first, otherwise calculate current count from elapsed host time and mode-specific wrap behavior. Speaker I/O controls channel 2 gate and reports speaker, OUT2, and refresh-clock bits.

### State, Persistence, And Dependencies
Persistent state is `struct kvm_pit`, which embeds three `struct kvm_kpit_channel_state` entries, flags, period, hrtimer, mutex, reinjection atomics, IRQ ack notifier, mask notifier, worker, and I/O devices. Channel fields preserve count, latches, read/write sequencing, mode, gate, BCD flag, and load time. Dependencies include KVM I/O bus registration, hrtimers, kthread workers, `kvm_set_irq()`, IOAPIC availability, PIC/IOAPIC ack and mask notifiers, APICv inhibit control, and HPET legacy mode flags.

### Integration Points
The PIT is created during irqchip setup, registered on the PIO bus, and routed by default to both PIC and IOAPIC GSI 0. `irq.c` calls `__kvm_migrate_pit_timer()` during vCPU timer migration. Userspace can migrate state through `KVM_GET_PIT`, `KVM_SET_PIT`, `KVM_GET_PIT2`, and `KVM_SET_PIT2`, and can toggle reinjection with `KVM_REINJECT_CONTROL`.

### Risks
Timer reinjection relies on ack ordering between atomics, the hrtimer callback, and the worker; lost ordering can drop or duplicate PIT ticks. Reinjection disables APICv because accelerated EOI writes can bypass ack notifiers. Very small guest periods are clamped to protect the host. State restore must restart timers without incorrectly firing during HPET legacy mode. Mode 3 odd-count handling and mode 4 precision are explicitly approximate.

### Test Signals
Test PIT command/readback behavior, LSB/MSB/word access sequencing, modes 0/2/3/4, count zero semantics, channel 2 speaker port behavior, periodic tick delivery to PIC and IOAPIC, reinjection on masked/unmasked IRQ0, APICv inhibit toggling, HPET legacy handoff, migration get/set ioctls, and tiny-period clamping logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/i8254.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/i8254.h -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/i8254.h

### Purpose
`i8254.h` declares the in-kernel PIT model used by KVM's x86 irqchip. It defines channel and device state, PIT I/O addresses and frequency constants, and ioctl/create/destroy prototypes under `CONFIG_KVM_IOAPIC`.

### Important APIs, Types, And Functions
Key types are `struct kvm_kpit_channel_state`, `struct kvm_kpit_state`, and `struct kvm_pit`. The channel state records count, latched count/status, read/write sequencing, mode, BCD flag, gate, and load time. The PIT state adds the three channels, flags, periodic/period fields, hrtimer, mutex, reinjection atomics, and IRQ ack notifier. `struct kvm_pit` wraps I/O devices, the owning `struct kvm`, mask notifier, worker, and pending work item. Prototypes expose PIT state ioctls, reinjection control, `kvm_create_pit()`, and `kvm_free_pit()`.

### Control Flow
The header itself has no executable control flow. It establishes the data layout consumed by `i8254.c`, userspace PIT state copies, the KVM I/O bus, and irq ack/mask notification code.

### State, Persistence, And Dependencies
All fields before `struct mutex lock` in `struct kvm_kpit_state` are documented as protected by that lock. The atomics after the lock coordinate reinjection with interrupt acknowledgement. Dependencies include `linux/kthread.h`, `kvm/iodev.h`, UAPI KVM PIT structs, and `ioapic.h`.

### Integration Points
`irq.c`, `i8254.c`, VM ioctl handlers, and irqchip setup/teardown use this header. Constants define the PIO registration ranges for PIT channels and speaker, and `KVM_PIT_FREQ` drives time/count conversion.

### Risks
The ioctl paths depend on the kernel channel-state layout matching the UAPI PIT state size. Locking comments are part of the correctness contract; adding fields on the wrong side of the mutex can create unsafely copied state. `KVM_PIT_FREQ` changes would alter guest-visible time.

### Test Signals
Build with and without `CONFIG_KVM_IOAPIC`, check UAPI size assertions in `i8254.c`, run PIT get/set migration tests, and verify PIO ranges and frequency-dependent timer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/i8254.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/i8259.c -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/i8259.c

### Purpose
`i8259.c` emulates the legacy dual 8259 programmable interrupt controller for KVM's in-kernel irqchip. It models master/slave PIC state, PIO ports `0x20/0x21`, `0xa0/0xa1`, ELCR ports `0x4d0/0x4d1`, interrupt priority/acknowledge behavior, mask notification, and wakeup of vCPUs that accept PIC external interrupts.

### Important APIs, Types, And Functions
Public functions are `kvm_pic_init()`, `kvm_pic_destroy()`, `kvm_pic_set_irq()`, `kvm_pic_read_irq()`, and `kvm_pic_update_irq()`. Key internal helpers include `pic_set_irq1()`, `pic_get_irq()`, `pic_update_irq()`, `pic_intack()`, `pic_clear_isr()`, `kvm_pic_reset()`, `pic_ioport_write()`, `pic_ioport_read()`, `pic_poll_read()`, `elcr_ioport_write()`, and `pic_irq_request()`.

### Control Flow
IRQ line changes update per-GSI source aggregation with `__kvm_irq_line_state()`, then set or clear IRR based on edge/level mode and `last_irr`. `pic_update_irq()` checks the slave first, pulses cascade IRQ2 on the master if needed, then updates the master output line. `kvm_pic_read_irq()` performs interrupt acknowledge, handles cascaded slave interrupts, returns spurious IRQ7 when needed, and updates ISR/IRR according to trigger mode and AutoEOI. Command writes implement initialization control words, operation control words, priority rotation, EOI variants, polling, read-register selection, and interrupt masks. ELCR writes select level-triggered lines subject to hardware masks.

### State, Persistence, And Dependencies
State lives in `struct kvm_pic` and two `struct kvm_kpic_state` instances. Each PIC tracks IRR, IMR, ISR, `last_irr`, priority base, interrupt vector base, read/poll modes, special mask mode, init phase, AutoEOI, rotation, special fully nested mode, ICW4 presence, and ELCR. The top-level PIC tracks output level, wakeup-needed flag, IRQ source state, lock, KVM pointer, and I/O devices. Dependencies include KVM I/O bus registration, APIC acceptance checks, ack/mask notifier infrastructure, tracing, and `kvm_notify_acked_irq()`.

### Integration Points
`irq.c` routes `KVM_IRQ_ROUTING_IRQCHIP` entries for master/slave PIC pins to `kvm_pic_set_irq()` and uses `kvm_pic_read_irq()` for external interrupt intack. PIT, legacy devices, and userspace IRQ line ioctls can feed PIC pins through routing. PIC masking changes notify irqfd resamplers and other mask notifiers.

### Risks
PIC correctness is dominated by subtle edge/level transitions, cascade IRQ2 behavior, EOI ordering, and lock dropping around ack notifiers, which can re-enter PIC code. Spurious interrupts and special fully nested mode must match guest expectations. Incorrect mask notifier firing can break resampling devices. `pic_unlock()` wakes only the first vCPU currently accepting PIC interrupts, so stale acceptance state can delay delivery.

### Test Signals
Test ICW/OCW programming sequences, vector base changes, mask/unmask notification, edge and level ELCR behavior, cascade delivery through IRQ2, spurious master/slave IRQ7/IRQ15 behavior, AutoEOI and rotate-on-EOI modes, polling reads, migration get/set of PIC state, PIT IRQ0 delivery, and split/no irqchip rejection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/i8259.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/ioapic.c -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/ioapic.c

### Purpose
`ioapic.c` emulates the x86 I/O APIC for KVM's in-kernel irqchip. It owns MMIO register emulation, redirection table state, IRQ assertion and LAPIC delivery, level-triggered remote-IRR/EOI handling, RTC EOI coalescing tracking, mask notifier lists, migration get/set, and I/O APIC creation/destruction.

### Important APIs, Types, And Functions
Public entry points include `kvm_ioapic_init()`, `kvm_ioapic_destroy()`, `kvm_ioapic_set_irq()`, `kvm_ioapic_update_eoi()`, `kvm_ioapic_scan_entry()`, `kvm_get_ioapic()`, `kvm_set_ioapic()`, `kvm_register_irq_mask_notifier()`, `kvm_unregister_irq_mask_notifier()`, `kvm_fire_mask_notifiers()`, and `kvm_rtc_eoi_tracking_restore_one()`. Internal helpers include `ioapic_read_indirect()`, `ioapic_write_indirect()`, `ioapic_set_irq()`, `ioapic_service()`, `ioapic_lazy_update_eoi()`, `kvm_ioapic_eoi_inject_work()`, and RTC tracking helpers.

### Control Flow
MMIO reads/writes access the select register and indirect window. Redirection-table writes preserve read-only fields, clear remote IRR for edge mode, fire mask notifiers on mask changes, and may re-inject pending level interrupts when unmasked. IRQ assertion updates per-source line state, coalesces already-pending edge/RTC interrupts, sets IRR, and calls `ioapic_service()`. Service builds a `struct kvm_lapic_irq`, delivers it to matching LAPICs, records edge delivery, and sets remote IRR for delivered level interrupts. EOI updates clear RTC tracking, notify ack listeners outside the lock, clear remote IRR, and reinject still-asserted level IRQs; repeated immediate EOIs are delayed through workqueue throttling.

### State, Persistence, And Dependencies
`struct kvm_ioapic` persists base address, selected register, ID, IRR, redirection table, per-pin source states, spinlock, RTC status bitmap/vector array, delayed EOI work, per-pin EOI storm counters, delivered-edge IRR mask, and mask notifier hlist. Dependencies include LAPIC destination matching and delivery, KVM MMIO bus registration, SRCU-protected IRQ routing, irqfd resampler notification, workqueues, tracepoints, and APICv pending-EOI checks.

### Integration Points
`irq.c` routes IOAPIC pins to `kvm_ioapic_set_irq()` and scans IOAPIC/MSI routes for EOI exit bitmaps. LAPIC EOI paths call `kvm_ioapic_update_eoi()`. PIT and other legacy routes target IOAPIC pins through default routing. Userspace migrates IOAPIC state through `KVM_GET_IRQCHIP` and `KVM_SET_IRQCHIP`.

### Risks
Level-triggered correctness depends on remote IRR, IRR, EOI, and mask-notifier ordering. Unmasking a level interrupt can inject stale IRR unless irqfd resampling is used correctly. RTC interrupt coalescing is special and guest-visible for Windows timekeeping. The code drops the IOAPIC lock around ack notifiers, so state must be updated before callbacks re-enter. Migration intentionally clears internal delivered IRR state and reinjects saved IRR, which can affect pending edge semantics.

### Test Signals
Exercise MMIO access sizes, redirection-table high/low writes, invalid register indices, mask/unmask with irqfd resampler, edge and level delivery, remote IRR clearing on EOI, EOI storm delay, RTC coalescing and pending EOI restore, APIC destination changes and EOI bitmap scanning, migration get/set, and APICv lazy EOI update paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/ioapic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/ioapic.h -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/ioapic.h

### Purpose
`ioapic.h` defines KVM's internal I/O APIC data structures, register constants, redirection entry layout, RTC EOI tracking state, mask notifier API, and helper prototypes.

### Important APIs, Types, And Functions
Important definitions include `IOAPIC_NUM_PINS`, `IOAPIC_DEFAULT_BASE_ADDRESS`, MMIO register offsets, indirect register numbers, delivery modes, trigger modes, and `RTC_GSI`. Key types are `struct rtc_status`, `union kvm_ioapic_redirect_entry`, `struct kvm_ioapic`, and `struct kvm_irq_mask_notifier`. Declared APIs include IOAPIC init/destroy, set irq, get/set state, update EOI, scan redirection entries, register/unregister/fire mask notifiers, and route scanning helpers. `ioapic_in_kernel()` maps to full in-kernel irqchip mode.

### Control Flow
The header provides declarations and one mode helper; behavior is implemented in `ioapic.c` and `irq.c`. The redirection entry bitfield defines how MMIO writes map to vector, delivery mode, destination mode, polarity, remote IRR, trigger mode, mask, and destination ID.

### State, Persistence, And Dependencies
`struct kvm_ioapic` persists guest-visible state plus internal delivery bookkeeping. The mask notifier list is documented as read under `irq_srcu` and written under `irq_lock`. Dependencies include KVM host state, KVM I/O devices, and `irq.h`.

### Integration Points
This header is shared by IOAPIC emulation, IRQ routing, PIT, PIC, irqfd resampling, LAPIC EOI scanning, and VM irqchip ioctls. It also gives non-IOAPIC code a stable way to test whether a full in-kernel IOAPIC exists.

### Risks
Bitfield layout in `union kvm_ioapic_redirect_entry` is guest ABI sensitive because it is copied to/from UAPI state. The notifier locking contract must be preserved to avoid use-after-free or missed mask transitions. `ioapic_in_kernel()` means full irqchip only; using it for split irqchip would incorrectly enable PIT/IOAPIC assumptions.

### Test Signals
Compile both `CONFIG_KVM_IOAPIC` modes, validate IOAPIC UAPI state layout through migration tests, exercise mask notifier registration/removal under IRQ routing changes, and verify full/split/none irqchip mode decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/ioapic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/irq.c -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/irq.c

### Purpose
`irq.c` is the x86 KVM interrupt-controller coordination layer. It queries and consumes pending external interrupts, timer interrupts, and LAPIC interrupts; validates and installs IRQ routing entries; handles MSI delivery and fast in-atomic routes; coordinates IOAPIC route scanning; supports posted-interrupt IRQ bypass; and implements default PIC/IOAPIC routing plus irqchip state ioctls.

### Important APIs, Types, And Functions
Important functions include `kvm_cpu_has_pending_timer()`, `kvm_cpu_has_extint()`, `kvm_cpu_has_injectable_intr()`, `kvm_cpu_has_interrupt()`, `kvm_cpu_get_extint()`, `kvm_cpu_get_interrupt()`, `kvm_inject_pending_timer_irqs()`, `__kvm_migrate_timers()`, `kvm_set_msi()`, `kvm_arch_set_irq_inatomic()`, `kvm_vm_ioctl_irq_line()`, `kvm_set_routing_entry()`, `kvm_scan_ioapic_irq()`, `kvm_scan_ioapic_routes()`, `kvm_arch_irq_routing_update()`, IRQ bypass add/delete/update hooks, `kvm_setup_default_ioapic_and_pic_routing()`, `kvm_vm_ioctl_get_irqchip()`, and `kvm_vm_ioctl_set_irqchip()`.

### Control Flow
Interrupt queries first consider non-APIC external sources: userspace pending vector, Xen upcall, and PIC output when LAPIC accepts PIC interrupts. Injectable checks then account for APICv, protected APIC, and LAPIC pending vectors. MSI routing converts KVM route fields into `struct kvm_lapic_irq` using x86 MSI decoding, validates x2APIC address-high bits, and delivers through LAPIC helpers. Routing entry setup maps IRQCHIP routes to PIC or IOAPIC callbacks, MSI routes to `kvm_set_msi()`, Hyper-V SINT routes to SynIC, and Xen event channels to Xen helpers. IOAPIC scans build EOI interception bitmaps for level-triggered MSI/IOAPIC vectors and stale pending EOIs.

### State, Persistence, And Dependencies
The file manipulates vCPU pending external vector state, KVM IRQ routing tables under SRCU, irqfd bypass state, irqchip mode, PIC/IOAPIC state, LAPIC interrupt state, Xen timer/upcall state, Hyper-V SINT routing, and posted-interrupt IRTE state. Dependencies include `hyperv.h`, `ioapic.h`, `irq.h`, Xen hooks, x86 MSI helpers, irqfd/irq bypass infrastructure, APICv/posted interrupt x86 ops, and tracepoints.

### Integration Points
This is the bridge between userspace irq ioctls, irqfd, in-kernel PIC/IOAPIC, LAPIC, Hyper-V, Xen, MSI routing, and hardware posted interrupts. It is used by the vCPU run loop to decide whether to inject, acknowledge, or migrate interrupt/timer events.

### Risks
Pending interrupt semantics differ between userspace LAPIC, in-kernel LAPIC, APICv, nested guests, PIC extints, and Xen upcalls. Route validation must reject unsupported split irqchip PIC routes and invalid x2APIC MSI encodings. Posted-interrupt bypass must safely fall back for multicast, non-postable delivery modes, or producer removal. IOAPIC EOI scanning must include stale pending EOIs for routes that changed destination.

### Test Signals
Test full/split/no irqchip modes, IRQ_LINE ioctls, default PIC/IOAPIC routes, MSI and x2APIC MSI routing, in-atomic MSI fast path, Hyper-V SINT and Xen event channel routes, APICv active/inactive injectable checks, userspace external interrupt delivery, IOAPIC EOI bitmap scans after route changes, IRQ bypass producer add/delete/update, and irqchip get/set migration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/irq.h -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/irq.h

### Purpose
`irq.h` defines x86 KVM in-kernel interrupt-controller structures and shared helpers for PIC, irqchip mode checks, timer injection, and timer migration.

### Important APIs, Types, And Functions
Under `CONFIG_KVM_IOAPIC`, it defines `PIC_NUM_PINS`, `SELECT_PIC()`, `struct kvm_kpic_state`, and `struct kvm_pic`, plus prototypes for PIC init/destroy, set/read/update IRQ, default routing, and irqchip get/set ioctls. Common helpers include `irqchip_full()`, `pic_in_kernel()`, `irqchip_split()`, and `irqchip_in_kernel()`. It declares timer-related functions such as `kvm_inject_pending_timer_irqs()`, `kvm_inject_apic_timer_irqs()`, `kvm_apic_nmi_wd_deliver()`, `__kvm_migrate_apic_timer()`, `__kvm_migrate_pit_timer()`, `__kvm_migrate_timers()`, and `apic_has_pending_timer()`.

### Control Flow
The mode helpers read `kvm->arch.irqchip_mode` with an `smp_rmb()` paired with irqchip mode publication. `SELECT_PIC()` maps global legacy IRQ numbers to master or slave PIC identifiers. Other control flow is implemented in the corresponding `.c` files.

### State, Persistence, And Dependencies
PIC state includes edge detection, request/mask/service registers, priority rotation, vector base, read/poll modes, initialization state, AutoEOI, special fully nested mode, ELCR, and top-level output/wakeup/IRQ source arrays. Dependencies include KVM host state, hrtimer declarations, spinlocks, KVM I/O devices, and LAPIC declarations.

### Integration Points
Included by PIC, PIT, IOAPIC, IRQ routing, and vCPU interrupt injection paths. Its irqchip mode helpers gate whether in-kernel PIC/IOAPIC/PIT behavior is available and whether userspace IRQ injection is legal.

### Risks
The irqchip mode helpers are small but widely used; a stale or incorrectly ordered mode read can send callers down full, split, or none irqchip paths incorrectly. PIC structure layout is copied to UAPI irqchip state, so incompatible changes affect migration. `__kvm_migrate_pit_timer()` is declared unconditionally but implemented only with IOAPIC support, so config guards matter.

### Test Signals
Build all irqchip configurations, validate full/split/none mode behavior, migrate PIC state through irqchip ioctls, and exercise callers that compile against PIT migration and APIC timer declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/irq.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm-asm-offsets.c -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/kvm-asm-offsets.c

### Purpose
`kvm-asm-offsets.c` generates assembly-visible offsets for KVM x86 VMX and SVM structures. The build compiles this file as offset-generation input and post-processes the raw assembler output for inclusion by assembly code.

### Important APIs, Types, And Functions
The single `common()` function emits offsets using `OFFSET()` and separators using `BLANK()`. When `CONFIG_KVM_AMD` is enabled it emits `SVM_vcpu_arch_regs`, `SVM_current_vmcb`, `SVM_spec_ctrl`, `SVM_vmcb01`, `KVM_VMCB_pa`, and `SD_save_area_pa`. When `CONFIG_KVM_INTEL` is enabled it emits `VMX_spec_ctrl`. It includes `vmx/vmx.h` and `svm/svm.h` under `COMPILE_OFFSETS`.

### Control Flow
There is no runtime control flow. Compile-time `IS_ENABLED()` conditionals determine which offsets are emitted for the configured build.

### State, Persistence, And Dependencies
The file persists no state. It depends on exact definitions of `struct vcpu_svm`, `struct kvm_vmcb_info`, `struct svm_cpu_data`, and `struct vcpu_vmx`; any structure layout change is reflected in regenerated offsets.

### Integration Points
Generated offsets are consumed by low-level VM entry/exit and speculation-control assembly that cannot use C field access. The file participates in the kernel asm-offsets build pipeline.

### Risks
Missing or stale offsets can break assembly at build time or, worse, cause runtime corruption if assembly and C disagree. Conditional emission must match assembly use under Intel/AMD config combinations.

### Test Signals
Build KVM with AMD-only, Intel-only, and combined configurations. Verify generated asm offsets change when relevant struct fields move and that low-level VMX/SVM assembly still assembles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm-asm-offsets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_cache_regs.h -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_cache_regs.h

### Purpose
`kvm_cache_regs.h` provides inline helpers for KVM's x86 vCPU register cache. It centralizes direct GPR accessors, lazy caching and dirty tracking for special registers, CR0/CR3/CR4/PDPTR reads, RIP/RSP helpers, EDX:EAX composition, and guest-mode state transitions.

### Important APIs, Types, And Functions
The `BUILD_KVM_GPR_ACCESSORS()` macro creates raw array accessors for RAX, RBX, RCX, RDX, RBP, RSI, RDI, and on x86-64 R8-R15. Cache helpers include `kvm_register_is_available()`, `kvm_register_is_dirty()`, `kvm_register_mark_available()`, `kvm_register_mark_dirty()`, `kvm_register_test_and_mark_available()`, `kvm_register_read_raw()`, and `kvm_register_write_raw()`. Control-register helpers include `kvm_read_cr0_bits()`, `kvm_is_cr0_bit_set()`, `kvm_read_cr0()`, `kvm_read_cr3()`, `kvm_read_cr4_bits()`, `kvm_is_cr4_bit_set()`, and `kvm_read_cr4()`. Mode helpers are `enter_guest_mode()`, `leave_guest_mode()`, and `is_guest_mode()`.

### Control Flow
Reads check availability bits and call `kvm_x86_call(cache_reg)` on demand. Writes update cached fields and mark the register dirty so VMX/SVM code can write back before guest entry. CR0/CR4 bit reads only force a cache fill for guest-owned bits that can reside in hardware state. `leave_guest_mode()` also converts a pending EOI-exitmap load into a KVM request. Assertions restrict register-cache use from interrupt context except for bounded PMI/NMI VM-exit handling.

### State, Persistence, And Dependencies
State is stored in `vcpu->arch.regs`, `regs_avail`, `regs_dirty`, `cr0`, `cr3`, `cr4`, guest-owned bit masks, PDPTR arrays in the active MMU, `hflags`, and statistics. Dependencies include KVM x86 ops, lockdep, bit operations, CR bit definitions, guest-mode flags, and PMI-in-guest checks.

### Integration Points
This header is used across x86 KVM instruction emulation, MSR/hypercall handling, VMX/SVM run paths, nested virtualization, MMU code, and event injection. Hyper-V code relies on GPR helpers for hypercall ABI decoding and result return.

### Risks
The cache availability/dirty invariant is critical: unavailable+dirty is invalid, and writes must mark dirty. Interrupt-context misuse can read stale state or clobber pending writes. Raw register helpers ignore current guest mode operand width, so using them where architectural truncation is required can be wrong. Guest-mode transitions must preserve EOI-exitmap reloads for nested/APIC behavior.

### Test Signals
Exercise register caching through instruction emulation, hypercalls, CR reads/writes with guest-owned bits, PDPTR reads on SVM, nested guest entry/exit, PMI/NMI exits, `leave_guest_mode()` EOI-exitmap requests, and debug assertions under lockdep.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_cache_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_emulate.h -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_emulate.h

### Purpose
`kvm_emulate.h` is the public internal interface for KVM's generic x86 instruction decoder and emulator. It defines exception reporting, memory/register operation callbacks, operand and decode-cache structures, emulation modes, intercept metadata, return codes, and register-cache helpers used by the emulator implementation and KVM x86 callers.

### Important APIs, Types, And Functions
Major types include `struct x86_exception`, `struct x86_instruction_info`, `struct x86_emulate_ops`, `struct operand`, `struct fetch_cache`, `struct read_cache`, `enum x86emul_mode`, `struct x86_emulate_ctxt`, `enum x86_intercept_stage`, and `enum x86_intercept`. Public functions include `x86_decode_insn()`, `x86_page_table_writing_insn()`, `init_decode_cache()`, `x86_emulate_insn()`, `emulator_task_switch()`, `emulate_int_real()`, `emulator_invalidate_register_cache()`, `emulator_writeback_register_cache()`, and `emulator_can_use_gpa()`. Inline helpers `reg_read()`, `reg_write()`, and `reg_rmw()` cache GPR operands inside the emulator context.

### Control Flow
The emulator calls back through `x86_emulate_ops` for GPR access, standard memory, emulated memory, atomic cmpxchg, PIO, segment/table access, CR/DR/MSR/PMC access, halt, wbinvd, hypercall fixup, nested intercept checks, CPUID, mode checks, NMI masking, SMM exit, triple fault, XCR access, address untagging, canonicality, and page validity. Decode state tracks prefixes, opcode bytes, ModRM/SIB fields, operands, fetch cache, memory read cache, and dirty/valid GPR bitmaps. Return codes distinguish continue, unhandleable, propagate fault, retry, cmpxchg failure, I/O needed, nested intercept, and vectoring failure.

### State, Persistence, And Dependencies
The context persists only for one emulated instruction or restartable I/O operation. It stores eflags, eip, mode, interruptibility, exception state, GPA availability, decoded operands, cached registers, and small fetch/read caches. Dependencies include x86 descriptor definitions, FPU vector types, CPUID vendor constants, KVM callback implementations, and nested virtualization intercept enums.

### Integration Points
KVM x86 calls the decoder/emulator for MMIO, PIO, instruction interception, nested intercept reflection, task switches, real-mode interrupts, SMM transitions, and page-table-writing detection. The ops table is the boundary between generic decode logic and VMX/SVM/KVM architectural state.

### Risks
The emulator assumes only one emulated memory location per instruction and that instruction fetch/stack accesses are standard memory; violating this in callbacks can mis-handle faults. Usercopy-sensitive fields begin at `src`, so structure layout matters. Register-cache dirty writeback must happen after emulation. Intercept stage ordering is subtle for nested virtualization. Vector and MM/XMM/YMM operand storage requires proper alignment and size handling.

### Test Signals
Run KVM emulator tests for ModRM/SIB decoding, string I/O/MMIO, page faults during standard and emulated accesses, LOCK cmpxchg, CR/DR/MSR intercepts, nested intercept stages, real/protected/long mode instructions, task switch and interrupt emulation, vendor CPUID paths, vector operands, and emulator restart after `X86EMUL_IO_NEEDED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_emulate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_onhyperv.c -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_onhyperv.c

### Purpose
`kvm_onhyperv.c` implements optimizations for KVM running as an L1 hypervisor on a Hyper-V L0 host. Its main function is to use Hyper-V guest-mapping flush hypercalls for KVM remote TLB flushes and to track common root TDP values for faster flushes.

### Important APIs, Types, And Functions
Exported internal APIs are `hv_flush_remote_tlbs_range()`, `hv_flush_remote_tlbs()`, and `hv_track_root_tdp()`. Internal helpers include `kvm_fill_hv_flush_list_func()`, `hv_remote_flush_root_tdp()`, and `__hv_flush_remote_tlbs_range()`. `struct kvm_hv_tlb_range` carries start GFN and page count for range flushes.

### Control Flow
Range and full flush wrappers call `__hv_flush_remote_tlbs_range()` with or without a range descriptor. The common helper locks `hv_root_tdp_lock`. If no single valid root is cached, it iterates vCPUs, flushes each unique valid `vcpu->arch.hv_root_tdp`, and detects whether all vCPUs converged on one root for future fast flushes. If a common root is cached, it flushes that root directly. Range flushes build Hyper-V flush lists through `hyperv_fill_flush_guest_mapping_list()`, while full flushes use `hyperv_flush_guest_mapping()`. `hv_track_root_tdp()` updates per-vCPU and common-root tracking when KVM's active remote flush op is the Hyper-V implementation.

### State, Persistence, And Dependencies
State lives in `kvm->arch.hv_root_tdp`, `kvm->arch.hv_root_tdp_lock`, and each `vcpu->arch.hv_root_tdp`. Dependencies include host Hyper-V APIs from `asm/mshyperv.h`, KVM vCPU iteration, root HPA validity checks, and `kvm_x86_ops.flush_remote_tlbs` dispatch.

### Integration Points
This file plugs into KVM's remote TLB flush hooks when KVM detects it is running on Hyper-V. MMU/root changes call `hv_track_root_tdp()` so future flushes can target the right L0 guest mapping root.

### Risks
Incorrect common-root caching can miss a root and leave stale L0 mappings. The code deliberately stops early on some error/multiple-root cases, so return handling must preserve conservative flushing behavior. Range list construction must match Hyper-V's expected guest mapping format.

### Test Signals
Test KVM-on-Hyper-V with single and multiple vCPUs, root convergence and divergence, full and range remote TLB flushes, invalid root transitions, failures from Hyper-V flush hypercalls, and switching away from the Hyper-V flush op.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_onhyperv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_onhyperv.h -->
## sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_onhyperv.h

### Purpose
`kvm_onhyperv.h` declares KVM-on-Hyper-V optimization hooks and provides config-dependent stubs. It also supplies allocation of the Hyper-V partition assist page required by L0 Hyper-V for direct TLB flush support of nested guests.

### Important APIs, Types, And Functions
When `CONFIG_HYPERV` is enabled, it declares `hv_flush_remote_tlbs_range()`, `hv_flush_remote_tlbs()`, and `hv_track_root_tdp()`, and defines `hv_get_partition_assist_page()`. The assist-page helper lazily allocates one zeroed page in `vcpu->kvm->arch.hv_pa_pg` and returns its physical address, or `INVALID_PAGE` on allocation failure. Without Hyper-V support, `hv_flush_remote_tlbs()` returns `-EOPNOTSUPP` and `hv_track_root_tdp()` is a no-op.

### Control Flow
The only inline control flow is lazy allocation of the shared partition assist page. The helper intentionally allocates one page for the VM, not per vCPU, because KVM does not currently use the page contents but must provide it to satisfy Hyper-V TLFS requirements.

### State, Persistence, And Dependencies
Persistent state is `kvm->arch.hv_pa_pg`, which remains allocated for the VM lifetime. Dependencies include `CONFIG_HYPERV`, KVM vCPU/KVM structures, page allocation, physical address conversion, and `INVALID_PAGE`.

### Integration Points
Nested virtualization setup uses the assist-page helper when exposing Hyper-V direct TLB flush support. KVM MMU code and x86 ops use the flush declarations when replacing standard remote TLB flushes with Hyper-V hypercalls.

### Risks
Allocation failure disables the assist page by returning `INVALID_PAGE`, so callers must handle that path. Sharing one page is intentional but relies on the current contract that KVM does not store per-vCPU data there. Missing stubs for range flush in the non-Hyper-V branch would need care if callers are added outside config guards.

### Test Signals
Build with and without `CONFIG_HYPERV`, test assist-page lazy allocation and reuse across vCPUs, verify failure handling under allocation fault injection, and exercise nested Hyper-V direct TLB flush setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/kvm/kvm_onhyperv.h -->
