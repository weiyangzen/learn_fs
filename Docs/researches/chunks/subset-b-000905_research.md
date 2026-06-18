# sources/distributed-fs/ceph-client/arch/x86/kvm/x86.c lines 9625-14571

## Scope

This chunk covers the final third of `arch/x86/kvm/x86.c`, beginning in the writeback/return path of `x86_emulate_instruction()` and continuing through module exit. The visible code includes:

- Public instruction-emulation wrappers and fast PIO completion paths.
- KVM clock, pvclock, TSC frequency, Hyper-V TSC-change, and x86 capability setup.
- Vendor module initialization and teardown for VMX/SVM-provided `kvm_x86_ops`.
- KVM hypercall dispatch and userspace hypercall exits.
- APICv inhibit/update handling, IOAPIC scan/EOI-exitmap plumbing, and directed yield.
- Event injection, NMI/SMI/IRQ processing, nested-event coordination, and the main vCPU enter/exit loop.
- `KVM_RUN` handling, userspace register/FPU/sreg/mpstate/debug/translation ioctls, and sync-regs support.
- vCPU create/postcreate/destroy, reset/INIT/SIPI behavior, CPU virtualization enable/disable, VM init/destroy, internal memory slots, memslot metadata, and dirty-log flag application.
- Async page fault delivery, noncoherent DMA tracking, guest_memfd hooks, INVPCID emulation, SEV-ES MMIO/PIO completion, tracepoint exports, and module init/exit.

The source path is under a Ceph-client snapshot tree, but this file is Linux KVM x86 virtualization core code. It is not Ceph distributed-filesystem logic.

## Purpose

This section implements the runtime center of KVM/x86: it connects userspace ioctls and `struct kvm_run` exits to architecture-specific VM entry, exception/interrupt injection, emulated I/O completion, vCPU lifecycle, and VM memory-slot lifecycle. It also performs late module initialization for vendor backends, exposes common helpers to VMX/SVM code through `EXPORT_SYMBOL_FOR_KVM_INTERNAL`, and owns cross-cutting x86 state such as TSC/pvclock behavior, APICv inhibition, FPU/debug-register switching, and protected-guest visibility restrictions.

The code is deliberately split between common policy in `x86.c` and vendor hooks in `kvm_x86_ops`. Common code validates architectural state, chooses when to enter the guest, coordinates requests, updates KVM-visible state, and handles userspace ABI structures. Vendor code supplies low-level operations such as VM entry, intercept control, APICv refresh, CR/MSR programming, nested virtualization, page-fault injection, and SEV/TDX/VMX/SVM-specific behavior.

## Important APIs, Types, And Functions

The emulation completion APIs at the start of the chunk are `kvm_emulate_instruction()`, `kvm_emulate_instruction_from_buffer()`, `kvm_fast_pio()`, `complete_emulated_pio()`, and `complete_emulated_mmio()`. They rely on `vcpu->arch.complete_userspace_io`, `vcpu->arch.pio`, `vcpu->mmio_needed`, `vcpu->mmio_fragments`, and cached linear RIP checks to resume emulation after userspace handles PIO/MMIO exits. `kvm_fast_pio_in()` and `kvm_fast_pio_out()` optimize single-port PIO and preserve quirks such as `KVM_X86_QUIRK_OUT_7E_INC_RIP`.

Clock and capability setup is handled by `kvm_timer_init()`, `kvmclock_cpufreq_notifier()`, `__kvmclock_cpufreq_notifier()`, `kvm_hyperv_tsc_notifier()`, `pvclock_gtod_notify()`, `kvm_setup_xss_caps()`, and `kvm_setup_efer_caps()`. Important state includes per-CPU `cpu_tsc_khz`, global `kvm_caps`, `kvm_host`, `pvclock_gtod_data`, `kvm_guest_has_master_clock`, and per-VM pvclock copies guarded by `kvm_lock` and `kvm->arch.tsc_write_lock`.

`kvm_x86_vendor_init()` and `kvm_x86_vendor_exit()` are the common registration boundary for VMX/SVM modules. `kvm_x86_vendor_init()` validates host FPU/FXSR/PAT/CET conditions, allocates the emulator cache, initializes the MMU module, seeds `kvm_caps`, reads host XCR0/XSS/EFER/ARCH_CAPABILITIES, initializes PMU capability, calls vendor `hardware_setup()`, installs static calls through `kvm_ops_update()`, checks all online CPUs for compatibility, registers pvclock/cpufreq/perf callbacks, and builds MSR lists. Teardown reverses perf callbacks, Hyper-V callbacks, LAPIC/module resources, cpufreq and pvclock notifiers, vendor hardware setup, user-return MSRs, MMU module state, emulator cache, and Xen static-key state.

Hypercalls are dispatched by `____kvm_emulate_hypercall()` and `kvm_emulate_hypercall()`. Covered hypercalls include `KVM_HC_VAPIC_POLL_IRQ`, `KVM_HC_KICK_CPU`, `KVM_HC_CLOCK_PAIRING`, `KVM_HC_SEND_IPI`, `KVM_HC_SCHED_YIELD`, and `KVM_HC_MAP_GPA_RANGE`. The map-GPA-range hypercall exits to userspace via `KVM_EXIT_HYPERCALL` and resumes through `complete_hypercall_exit()`. `emulator_fix_hypercall()` patches legacy hypercall instructions or injects #UD depending on `KVM_X86_QUIRK_FIX_HYPERCALL_INSN`.

APICv control is centralized in `kvm_apicv_activated()`, `kvm_vcpu_apicv_activated()`, `kvm_apicv_init()`, `__kvm_vcpu_update_apicv()`, `kvm_vcpu_update_apicv()`, `__kvm_set_or_clear_apicv_inhibit()`, `kvm_set_or_clear_apicv_inhibit()`, and `kvm_inc_or_dec_irq_window_inhibit()`. These functions update `kvm->arch.apicv_inhibit_reasons`, `kvm->arch.apicv_nr_irq_window_req`, `vcpu->arch.apic->apicv_active`, and APIC access-page mappings while synchronizing with `apicv_update_lock`.

Event processing is dominated by `kvm_check_and_inject_events()`, with helpers `kvm_check_nested_events()`, `kvm_inject_exception()`, `process_nmi()`, `kvm_get_nr_pending_nmis()`, `vcpu_scan_ioapic()`, and `vcpu_load_eoi_exitmap()`. It prioritizes nested exits, reinjection, exceptions, SMIs, NMIs, and IRQs, and uses `KVM_REQ_EVENT`, `KVM_REQ_TRIPLE_FAULT`, `KVM_REQ_NMI`, `KVM_REQ_SMI`, IRQ-window requests, and vendor `*_allowed()`/`inject_*()` hooks.

The main execution path is `kvm_arch_vcpu_ioctl_run()` -> `kvm_x86_vcpu_pre_run()` -> `vcpu_run()` -> `vcpu_enter_guest()` or `vcpu_block()`. `vcpu_enter_guest()` drains pending KVM requests, handles clock/MMU/TLB/APIC/PMU/Hyper-V/APF state, injects events, reloads the MMU, switches FPU/xfeatures/debug/PKRU/PMU state, enters the vendor `vcpu_run()` loop, handles fast reentry, restores host state, accounts exits, and dispatches vendor `handle_exit()`.

The userspace ABI helpers are `kvm_arch_vcpu_ioctl_get_regs()`, `kvm_arch_vcpu_ioctl_set_regs()`, `kvm_arch_vcpu_ioctl_get_sregs()`, `kvm_arch_vcpu_ioctl_get_mpstate()`, `kvm_arch_vcpu_ioctl_set_mpstate()`, `kvm_arch_vcpu_ioctl_set_guest_debug()`, `kvm_arch_vcpu_ioctl_translate()`, `kvm_arch_vcpu_ioctl_get_fpu()`, `kvm_arch_vcpu_ioctl_set_fpu()`, `store_regs()`, and `sync_regs()`. They read and write `struct kvm_regs`, `struct kvm_sregs`, `struct kvm_sregs2`, `struct kvm_mp_state`, `struct kvm_guest_debug`, `struct kvm_translation`, `struct kvm_fpu`, and `struct kvm_sync_regs`, with restrictions for protected guest state.

Lifecycle APIs include `kvm_arch_vcpu_precreate()`, `kvm_arch_vcpu_create()`, `kvm_arch_vcpu_postcreate()`, `kvm_arch_vcpu_destroy()`, `kvm_vcpu_reset()`, `kvm_vcpu_deliver_sipi_vector()`, `kvm_arch_enable_virtualization_cpu()`, `kvm_arch_disable_virtualization_cpu()`, `kvm_arch_shutdown()`, `kvm_arch_init_vm()`, `kvm_arch_pre_destroy_vm()`, `kvm_arch_destroy_vm()`, and `kvm_arch_free_vm()`. They allocate and free MMU, LAPIC, emulator, FPU, PIO, MCE, PMU, Hyper-V, Xen, APIC map, and memslot/page-track resources.

Memory-slot and MMU metadata functions include `__x86_set_memory_region()`, `kvm_arch_free_memslot()`, `memslot_rmap_alloc()`, `kvm_alloc_memslot_metadata()`, `kvm_arch_memslots_updated()`, `kvm_arch_prepare_memory_region()`, `kvm_mmu_update_cpu_dirty_logging()`, `kvm_mmu_slot_apply_flags()`, and `kvm_arch_commit_memory_region()`. They own private internal slots, rmap/lpage metadata, page tracking, MMIO SPTE invalidation, dirty-log CPU assist updates, huge-page splitting/recovery, and remote TLB flushes.

The tail exposes helper families for runtime checks and fault handling: `kvm_arch_vcpu_in_kernel()`, `kvm_arch_vcpu_get_ip()`, `kvm_arch_vcpu_should_kick()`, `kvm_arch_interrupt_allowed()`, `kvm_get_linear_rip()`, `kvm_is_linear_rip()`, `kvm_get_rflags()`, `kvm_set_rflags()`, async-PF helpers, noncoherent DMA registration, guest_memfd hooks, `kvm_spec_ctrl_test_value()`, `kvm_fixup_and_inject_pf_error()`, `kvm_handle_memory_failure()`, `kvm_handle_invpcid()`, `kvm_sev_es_mmio()`, and `kvm_sev_es_string_io()`.

## Control Flow

Instruction emulation completion proceeds by preserving partially completed PIO/MMIO state across a userspace exit. The emulator records `complete_userspace_io`; on the next `KVM_RUN`, `kvm_arch_vcpu_ioctl_run()` clears the callback, invokes it, and either exits again, resumes the run loop, or returns an error. MMIO completion walks `mmio_fragments` in pieces of at most eight bytes, copying read data from `run->mmio.data`, issuing further exits with `kvm_prepare_emulated_mmio_exit()`, and finally reentering instruction emulation for reads.

Vendor module initialization has a staged control flow with explicit unwinds before the point of no return. It rejects unsupported host state, initializes shared KVM/x86 capability structures, calls vendor setup, installs static calls, validates every online CPU, then registers global notifiers and callbacks. After the point-of-no-return comment, new failure paths are intentionally avoided because cpufreq, pvclock, perf, Hyper-V, and MSR list state would require broader unwinding.

Hypercall dispatch first normalizes 32-bit guests by truncating the number and arguments, rejects nonzero CPL, then checks each hypercall's guest feature bit or userspace-exit enablement. Most handled hypercalls return synchronously through `vcpu->run->hypercall.ret`. `KVM_HC_MAP_GPA_RANGE` populates `struct kvm_run.hypercall`, sets `KVM_EXIT_HYPERCALL`, stores the completion callback, and returns 0 so userspace can process it.

The event path in `kvm_check_and_inject_events()` is priority-driven. Nested events are checked first. Previously injected exceptions/NMIs/IRQs are reinjected before new events. Pending exceptions then win over asynchronous events and may set RF, clear debug-register general-detect state, and mark the exception as injected. Guest-debug `BLOCKIRQ` suppresses interrupt injection. SMIs, NMIs, and IRQs are injected only if vendor hooks say the guest has an architectural window; otherwise KVM requests an immediate exit or arms an SMI/NMI/IRQ window.

`vcpu_enter_guest()` is the main state machine. Before guest entry it drains request bits in a carefully ordered sequence: VM death and dirty-ring exits, nested-state page fetching, MMU roots, timers, master/global/vCPU clock updates, MMU sync/load, TLB flushes, PMU/PMI, SMI/NMI, IOAPIC/EOI, APIC page reload, Hyper-V crash/reset/exit/stimer, APICv update, async PF completion, intercept recalculation, dirty logging, and protected-guest state reset. It then handles event injection, reloads the MMU, disables preemption/IRQs, marks `IN_GUEST_MODE`, leaves SRCU, loads guest CPU state, calls vendor `vcpu_run()`, restores host state, re-enters SRCU, and invokes vendor exit handling.

`vcpu_run()` loops until it must return to userspace or an error occurs. Runnable vCPUs call `vcpu_enter_guest()`, while halted or APF-halted vCPUs call `vcpu_block()`. After each handled iteration it clears unblock requests, injects pending Xen events and timers, exits for userspace IRQ-window injection if requested, and services generic work pending before guest mode.

`kvm_arch_vcpu_ioctl_run()` wraps the vCPU run with userspace ABI synchronization. It loads the vCPU, activates a temporary signal mask, loads guest FPU state, handles uninitialized vCPUs by blocking until INIT/SIPI or signal, validates and applies dirty sync-regs fields, syncs userspace APIC TPR when no in-kernel LAPIC exists, converts userspace exceptions to nested exception VM-exits when needed, completes pending userspace I/O, checks `wants_to_run`, calls the pre-run hook, and then invokes `vcpu_run()`. On exit it restores the user FPU, stores requested valid regs, fills `kvm_run` post-run fields, unlocks SRCU, deactivates signals, and puts the vCPU.

Register and sregister setters validate architectural consistency before mutating state. `__set_sregs_common()` checks long-mode invariants, legal CR0/CR4, legal CR3, and APIC base. It updates descriptor tables, CR2/CR3/CR8/EFER/CR0/CR4, segments, APIC intercepts, and MMU reset flags. `__set_sregs()` restores pending interrupts from the interrupt bitmap. `__set_sregs2()` optionally accepts userspace PDPTRs and marks them dirty.

VM/vCPU lifecycle is layered. VM init validates the VM type, sets private-memory/pre-fault/default quirk state, initializes page tracking, MMU, vendor VM state, clock locks/copies, default TSC/APIC/PMU policy, APICv, Hyper-V, and Xen. vCPU create initializes register dirtiness, PV time cache, MP state, MMU, LAPIC, PIO page, MCE banks, dirty mask, emulator context, FPU state, PMU, vendor vCPU state, CPUID-derived state, TSC frequency, reset state, and MMU mode. Destroy paths reverse these allocations and detach async PF, MMU, clock, vendor, Xen, Hyper-V, PMU, LAPIC, and CPUID state.

Memory-region control flow is split into prepare, commit, and destroy phases. Prepare rejects unsupported moves, bounds-checks GFNs and aliases, allocates rmaps/lpage/page-track metadata for create/move, or preserves metadata for flags-only changes. Commit deletes page-track slots on delete, recalculates default MMU page budget for create/delete, applies dirty-log flags, and frees old metadata after a move. Dirty-log enablement may eager-split huge pages, clear dirty state, remove write access, and unconditionally flush remote TLBs for correctness around MMU-writable SPTE semantics.

Async page fault flow tracks in-flight GFNs in an open-addressed per-vCPU hash table. A not-present event records the GFN, tries to write the paravirtual APF reason and inject an async #PF, or falls back to an artificial APF halt. A ready event deletes the GFN or broadcasts, writes the ready token, injects the APF vector through the LAPIC, clears APF halt, and makes the vCPU runnable. Queueing requests `KVM_REQ_APF_READY` and kicks the vCPU unless a ready notification is already pending.

SEV-ES I/O flow differs because guest register state is protected and data is routed through GHCB-related buffers. `kvm_sev_es_mmio()` first tries in-kernel MMIO, then stores one MMIO fragment and uses `complete_sev_es_emulated_mmio()` for userspace completion. `kvm_sev_es_string_io()` advances `sev_pio_data` and `sev_pio_count` across PAGE_SIZE-sized PIO batches, using completion callbacks for userspace-emulated IN/OUT string operations.

## State And Persistence Behavior

No disk persistence is implemented here. State is kernel-resident and scoped to module globals, per-VM `struct kvm_arch`, per-vCPU `struct kvm_vcpu_arch`, per-run `struct kvm_run`, per-CPU variables, and hardware MSRs/registers.

Important global/module state includes `kvm_x86_ops`, static-call targets, `kvm_pmu_ops`, `kvm_caps`, `kvm_host`, `x86_emulator_cache`, `cpu_tsc_khz`, `kvm_guest_has_master_clock`, `pvclock_gtod_work`, `pvclock_irq_work`, `virt_rebooting`, and exported tracepoints. Vendor init/exit changes these globals and must serialize through `vendor_module_lock` and `kvm_lock`.

Per-vCPU persistent state includes general registers, CRs, segments, EFER, APIC state, MP state, exception/interrupt queues, NMI/SMI counters, TSC offsets, FPU/xfeatures, debug registers, emulator context, PIO/MMIO in-progress fields, async PF state, PMU state, Hyper-V/Xen state, APICv active state, and cached `last_guest_tsc`/`last_vmentry_cpu`. `kvm_vcpu_reset()` reinitializes much of this state and preserves only architecturally preserved INIT fields such as CR0 CD/NW and selected XSTATE components.

Per-VM state includes VM type/private-memory policy, quirks, MMU/page-track structures, APICv inhibit bitmap and lock, pvclock seqlock/copy, default TSC frequency, APIC bus timing, PMU enablement, noncoherent DMA count, Hyper-V root TDP, Xen/Hyper-V VM state, APIC map, MSR filters, PMU event filters, internal memory slots, and memslot architecture metadata.

State handoff to userspace occurs through `struct kvm_run`: exit reasons, hypercall arguments/return, MMIO payloads, IRQ-window flags, TPR access, IOAPIC EOI vector, Hyper-V/system-event exits, sync-regs areas, and post-run `if_flag`, `cr8`, `apic_base`, SMM, guest-mode, and interrupt-injection readiness fields. Protected guest state deliberately hides or rejects many register and FPU accesses.

Hardware-visible state is transiently switched around VM entry. Guest FPU/xfeatures, PKRU, debug registers, DEBUGCTL, PMU state, XFD_ERR, and vendor VMCS/VMCB state are loaded before entry and restored or synchronized after exit. Ordering barriers around `vcpu->mode`, SRCU unlock/lock, IRQ state, and APICv posted interrupt state are part of the correctness contract.

## Dependencies And Integration Points

This chunk depends heavily on KVM common infrastructure (`struct kvm`, `struct kvm_vcpu`, request bits, SRCU, memslots, dirty ring, halt polling, async PF, generic guest memory helpers), x86 KVM headers and vendor hooks (`kvm_x86_ops`, nested ops, PMU ops, APIC/LAPIC helpers, MMU helpers, emulator helpers), Linux CPU/hotplug/cpufreq/timekeeping infrastructure, x86 FPU/debug/MSR helpers, Hyper-V and Xen optional integrations, and memory-management APIs such as `vm_mmap()`, `vm_munmap()`, `vcalloc`, and remote TLB flushing.

`kvm_x86_ops` is the most important integration surface. This chunk calls vendor hooks for processor compatibility, hardware setup/unsetup, vCPU create/free/pre-run/run/exit, virtualization enable/disable, CR/EFER/RFLAGS/IDT/GDT handling, APICv controls, interrupt/NMI/SMI injection and windowing, nested virtualization, MMU/dirty logging, protected guest state, guest memory preparation/invalidation, and SEV/TDX/VMX/SVM-specific operations.

Userspace integration is the KVM ioctl ABI. The functions here implement `KVM_RUN`, register get/set, special-register get/set, FPU get/set, MP state get/set, guest debug setup, address translation, hypercall exits, MMIO/PIO exits, system-event exits, IOAPIC EOI exits, and sync-regs. QEMU compatibility quirks are visible in the fast OUT 0x7e RIP behavior, hypercall return initialization, legacy SIPI_RECEIVED handling, and reset unhalting compatibility.

Timekeeping integration uses cpufreq notifiers, CPU hotplug callbacks, pvclock gtod notifiers, irq_work/workqueues, Hyper-V TSC-change callbacks, and all-VM clock-update requests. These paths coordinate with `vm_list` under `kvm_lock` and with per-VM pvclock seqlocks to prevent guest time from moving backward.

Interrupt integration spans LAPIC, IOAPIC, PIC, irq routing, posted interrupts, APICv/AVIC, Hyper-V SynIC, Xen pending events, PMU PMI delivery, SMI/NMI, and userspace IRQ-window injection. The code uses request bits and vendor hooks to reconcile in-kernel and userspace interrupt models.

Memory integration spans KVM memslots, private internal memslots, page tracking, shadow/TDP MMU, rmaps, large-page metadata, dirty logging, CPU dirty log assist, guest_memfd, noncoherent DMA, and MMIO SPTE invalidation. The memslot hooks are called from generic KVM memory-region update code.

## Risks And Edge Cases

The guest-entry path is extremely order-sensitive. Moving request handling, event injection, MMU reload, SRCU unlock, IRQ disable, `vcpu->mode` transitions, APICv synchronization, FPU/debug/PKRU switching, or exit accounting can create lost kicks, stale page-table use, missed posted interrupts, incorrect interrupt injection, host state leakage, or deadlocks.

Event injection has nuanced architectural priority rules. Reinjecting existing events, prioritizing pending exceptions over asynchronous events, setting RF for fault-class exceptions, clearing DR7.GD for #DB, suppressing IRQs under guest debug, and preserving nested VM-exit semantics are all correctness-sensitive. Incorrect `-EBUSY` handling can either lose events or cause excessive immediate exits.

Userspace I/O completion is fragile because it resumes partially completed emulator state after a separate `KVM_RUN`. Completion callbacks must be cleared exactly once, linear RIP must still match for fast PIO, `pio.count` and `mmio_needed` must be coherent, and read/write MMIO paths differ in whether instruction emulation must resume.

Protected guest state creates many conditional ABI differences. Register, sregister, FPU, RIP, CPL, and async-PF delivery paths either reject access, return masked values, or avoid reading hidden state. Missing these checks can leak confidential guest state or break protected VM execution.

APICv inhibit changes are concurrency-sensitive. The code must kick and wait for vCPUs before toggling VM-wide inhibit state, hold `apicv_update_lock`, avoid stale `apicv_active` observations, zap the APIC access page when needed, and handle IRQ-window inhibit counts without thrashing.

TSC and pvclock logic must avoid time going backward across cpufreq changes, CPU hotplug, Hyper-V TSC changes, suspend/hibernate TSC resets, and non-constant TSC hosts. The notifier ordering, synchronous IPIs, master-clock requests, and backwards-TSC compensation are high-risk paths.

Dirty logging and memslot metadata are correctness and performance sensitive. Incorrect large-page disallow bits, missing rmap/lpage allocation, stale MMIO SPTE generation, failed external page-track checks, or missing TLB flushes after write-protect changes can corrupt migration dirty bitmaps or allow guest writes to escape logging.

Reset and INIT behavior has many architectural exceptions. `kvm_vcpu_reset()` must leave nested mode, reset LAPIC/debug/event/APF/clock state, preserve INIT-specific CR0 CD/NW and selected XSTATE behavior, set RDX from CPUID or fallback FMS, and flush/reset MMU only under the right conditions.

SEV-ES MMIO/PIO uses caller-provided buffers that must not be stack-backed and advances raw data pointers over multiple userspace exits. Bad lifetime assumptions, page-split behavior, or missed completion callbacks can corrupt GHCB scratch data or stall encrypted guests.

Compatibility quirks are intentional ABI. Changing OUT 0x7e RIP advancement, hypercall ret initialization, `SIPI_RECEIVED` translation, old reset unhalting behavior, ignored-MSR warnings, or sync-regs validation can regress existing VMMs.

## Test Signals

High-signal build coverage starts with x86 KVM builds for VMX and SVM, with combinations of `CONFIG_X86_64`, `CONFIG_KVM_HYPERV`, `CONFIG_KVM_XEN`, `CONFIG_KVM_SMM`, `CONFIG_KVM_GUEST_MEMFD`, `CONFIG_KVM_GENERIC_MEMORY_ATTRIBUTES`, `CONFIG_CPU_FREQ`, and protected-VM options.

Runtime validation should include KVM selftests for `KVM_RUN`, sync-regs, register/sregister ioctls, MP state, guest debug, MMIO/PIO exits, hypercalls, APICv inhibition, nested virtualization, INVPCID, dirty logging, memslot create/move/delete/flags-only changes, async page faults, TSC scaling/offset synchronization, and protected guest state restrictions.

Event tests should exercise injected and pending exceptions, nested exception VM-exits, NMI reinjection, NMI windowing, SMI paths where enabled, IRQ-window exits with userspace irqchip, in-kernel LAPIC/IOAPIC/PIC configurations, APICv toggling, blocked IRQ debug mode, PMU PMI delivery, Xen pending events, and Hyper-V SynIC timer events.

Guest-entry tests should stress concurrent kicks, remote TLB flushes, APICv posted interrupts, dirty-ring full exits, clock-update requests, MMU root invalidation, FPU/xstate switching, debug-register switching, host breakpoints, XFD/XFD_ERR handling, and immediate-exit requests.

Userspace ABI compatibility tests should cover QEMU-visible quirks: fast PIO `OUT 0x7e`, userspace-handled `KVM_HC_MAP_GPA_RANGE`, `SIPI_RECEIVED` translation, reset-state register values, `KVM_EXIT_IRQ_WINDOW_OPEN`, `KVM_EXIT_IOAPIC_EOI`, Hyper-V crash/reset/exit events, and sync-regs dirty/valid masks.

Memory-slot tests should create, move, delete, and flags-toggle slots with aligned and misaligned GFNs/HVAs, dirty logging with and without manual protect/init-set, eager page splitting, CPU dirty logging enabled, external page trackers, guest_memfd/private memory, internal APIC/TSS/identity slots, and noncoherent DMA assignment toggles.

Async-PF tests should validate not-present injection versus artificial halt fallback, ready-token delivery through LAPIC, broadcast wakeups, page-ready slot backpressure, nested guest delivery-as-PF-VM-exit behavior, and protected/CPL/paging restrictions.

SEV-ES-specific tests should cover encrypted guest MMIO reads and writes, partial in-kernel MMIO handling followed by userspace completion, string INS/OUTS split across PAGE_SIZE batches, invalid stack data rejection, and repeated `complete_userspace_io` resumption.

Trace and observability checks should confirm exported KVM tracepoints still build and fire in representative paths: entry/exit, MMIO, page faults, MSRs/CRs, nested VM enter/exit, AVIC/APICv events, VMGEXIT, and RMP faults.
