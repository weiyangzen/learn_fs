# sources/distributed-fs/ceph-client/arch/s390/kvm/interrupt.c

## Purpose

`interrupt.c` implements the s390 KVM interrupt controller side of the architecture port. It manages local vCPU interrupt state, VM-wide floating interrupts, the floating interrupt controller device (`kvm-flic`), adapter interrupt routing, migration serialization of pending IRQs, and the GISA/GIB alert mechanism used for adapter interruption virtualization. It is the point where KVM's generic injection APIs, s390 SIE state, lowcore interrupt save/new-PSW conventions, and userspace migration/ioctl interfaces meet.

The file handles two broad interrupt classes:

- Per-vCPU local interrupts: program, machine check, clock comparator, CPU timer, external call, emergency signal, restart, stop, set-prefix, and pfault-init interrupts stored in `vcpu->arch.local_int`.
- VM-wide floating interrupts: I/O, adapter I/O, virtio, service signal, pfault-done, and floating machine-check events stored in `kvm->arch.float_int` or, for adapter I/O, in a guest interruption status area (`kvm->arch.gisa_int.origin`) when AIV/GISA is active.

## Important APIs, Types, and Functions

Primary exported or externally visible entry points:

- `kvm_s390_deliver_pending_interrupts()` is called before entering SIE to refresh timer pending bits, deliver all currently deliverable interrupts in architecture priority order, and set interception indicators for blocked pending work.
- `kvm_s390_inject_vcpu()` injects a `struct kvm_s390_irq` into one vCPU under the local interrupt lock, then wakes the target.
- `kvm_s390_inject_vm()` injects a `struct kvm_s390_interrupt` as a VM/floating interrupt, converts it to an internal `struct kvm_s390_interrupt_info`, queues it, and kicks an eligible vCPU.
- `kvm_s390_get_io_int()` dequeues the top pending I/O interrupt for TPI-style consumption, arbitrating between queued classic I/O and GISA adapter pending bits.
- `kvm_s390_set_irq_state()` and `kvm_s390_get_irq_state()` serialize/restore local IRQ state for migration.
- `kvm_s390_clear_local_irqs()` and `kvm_s390_clear_float_irqs()` reset local or VM-wide interrupt state.
- `kvm_s390_gisa_init()`, `kvm_s390_gisa_enable()`, `kvm_s390_gisa_disable()`, `kvm_s390_gisa_destroy()`, `kvm_s390_gisa_clear()`, `kvm_s390_gisc_register()`, and `kvm_s390_gisc_unregister()` manage guest interruption status areas and exported guest ISC registration for adapter interrupt users.
- `kvm_s390_gib_init()` and `kvm_s390_gib_destroy()` create and tear down the global interruption block and its adapter interrupt handler.
- `kvm_flic_ops` exposes the `kvm-flic` device with get/set/has/create/destroy callbacks.
- `kvm_set_routing_entry()` validates and stores s390 adapter IRQ routing metadata; `set_adapter_int()` is the route callback used by generic irqfd/routing code.
- `kvm_s390_reinject_machine_check()` reinjects host volatile machine-check information into the guest.

Core local-delivery helpers:

- `deliverable_irqs()` merges local, floating, masked, and GISA pending state, then filters by PSW interrupt masks, CR0 submasks, CR6 ISC enablement, CR14 machine-check masks, protected-virtualization injection limits, and the fact that STOP is handled by intercept rather than normal delivery.
- `__deliver_cpu_timer()`, `__deliver_ckc()`, `__deliver_pfault_init()`, `__deliver_machine_check()`, `__deliver_restart()`, `__deliver_set_prefix()`, `__deliver_emergency_signal()`, `__deliver_external_call()`, `__deliver_prog()`, `__deliver_service()`, `__deliver_service_ev()`, `__deliver_pfault_done()`, `__deliver_virtio()`, and `__deliver_io()` materialize the pending condition into guest lowcore fields and old/new PSW transitions, or into SIE interception fields for protected guests.
- `write_sclp()` writes service-signal lowcore state or protected-guest SIE fields.
- `__write_machine_check()` saves guest register state and machine-check payloads into lowcore/extended save areas, with special protected-guest handling via SIE fields.

Core injection helpers:

- `do_inject_vcpu()` dispatches local injection by IRQ type.
- `__inject_prog()`, `__inject_pfault_init()`, `__inject_extcall()`, `__inject_set_prefix()`, `__inject_sigp_stop()`, `__inject_sigp_restart()`, `__inject_sigp_emergency()`, `__inject_mchk()`, `__inject_ckc()`, and `__inject_cpu_timer()` populate `local_int` payloads and set pending bits.
- `__inject_vm()` dispatches floating interrupt injection to `__inject_float_mchk()`, `__inject_virtio()`, `__inject_service()`, `__inject_pfault_done()`, or `__inject_io()`.
- `__floating_irq_kick()` chooses a non-stopped vCPU, uses `last_sleep_cpu` as a hint, sets the appropriate CPUSTAT bit, and wakes/kicks the vCPU.

FLIC and adapter APIs:

- `get_all_floating_irqs()` snapshots queued floating interrupts and GISA pending adapter ISCs for migration.
- `enqueue_floating_irq()` restores floating interrupts from userspace state.
- `register_io_adapter()`, `modify_io_adapter()`, `kvm_s390_mask_adapter()`, `kvm_s390_destroy_adapters()`, `flic_inject_airq()`, `modify_ais_mode()`, and `flic_ais_mode_set_all()` implement adapter registration, masking, adapter interrupt injection, and AIS single/all modes.
- `adapter_indicators_set()` pins guest indicator pages, sets indicator/summary bits, marks pages dirty, and returns whether a new adapter IRQ should be injected.

GISA/GIB helpers:

- `gisa_set_iam()`, `gisa_clear_ipm()`, `gisa_get_ipm_or_restore_iam()`, `gisa_set_ipm_gisc()`, `gisa_get_ipm()`, and `gisa_tac_ipm_gisc()` atomically manipulate the GISA interruption alert mask and pending-mask fields.
- `process_gib_alert_list()` detaches the global alert list built by millicode, restores the global alert origin, and starts per-VM timers to wake idle vCPUs.
- `gisa_vcpu_kicker()` and `__airqs_kick_single_vcpu()` repeatedly find an idle vCPU that enables one of the pending ISCs and wake it.
- `aen_host_forward()`, `aen_process_gait()`, and `gib_alert_irq_handler()` integrate PCI adapter event notification forwarding with the GIB alert path when zPCI interpretation is enabled.

## Control Flow

### Pending and Delivery Path

Before each SIE entry, `kvm_s390_deliver_pending_interrupts()` clears old intercept indicators, recomputes clock-comparator and CPU-timer pending bits from the current TOD/cpu-timer state, then loops while `deliverable_irqs()` returns nonzero. Interrupt priority is encoded in reverse bit order, so the loop uses `find_last_bit()` over `IRQ_PEND_COUNT`.

Each delivery helper follows the s390 architecture pattern: copy and clear the pending payload under the relevant spinlock, write the interrupt code and parameter fields to guest lowcore, save the old PSW, load the new PSW, update vCPU statistics, and trace the delivery. Protected guests cannot always receive lowcore writes from the hypervisor, so many delivery helpers set SIE fields such as `iictl`, `eic`, `mcic`, `faddr`, `edc`, `subchannel_id`, `io_int_word`, or `extcpuaddr` instead. Program interrupt delivery has additional payload-specific lowcore writes and may rewind/forward the PSW depending on nullifying/suppressing exception rules and `KVM_S390_PGM_FLAGS_NO_REWIND`.

After delivery, the function handles single-step debug semantics by forcing a pending debug exit when an interrupt changed the PC. It then calls `set_intercept_indicators()` so non-deliverable pending interrupts cause SIE exits or control-register interception when the guest later enables the relevant mask.

### Injection Path

Local injection enters through `kvm_s390_inject_vcpu()`, which serializes with `local_int.lock`, dispatches through `do_inject_vcpu()`, and wakes the vCPU on success. Helpers set payload structures in `li->irq`, pending bits in `li->pending_irqs`, and CPUSTAT request bits when the condition should pull the vCPU out of SIE. Several injection paths validate architecture constraints: external-call and emergency-signal source CPU IDs must resolve to existing vCPUs; set-prefix requires the target to be stopped; stop accepts only `KVM_S390_STOP_FLAG_STORE_STATUS`; duplicate external/stop pending conditions return `-EBUSY`.

Floating injection enters through `kvm_s390_inject_vm()`. It allocates `struct kvm_s390_interrupt_info`, copies type-specific payload from userspace ABI fields, calls `__inject_vm()`, and frees on error. Floating queues are list based and bounded by counters. Service interrupts coalesce SCCB event-pending bits and ignore duplicate SCCB parameters when one is already pending. Adapter I/O interrupts can bypass the classic floating queue by setting a GISA IPM bit when GISA is active and the interrupt is adapter-interpretation capable.

### Wait, Timer, and Wake Path

`kvm_s390_handle_wait()` handles guest wait-state exits. It immediately resumes if the vCPU is runnable, rejects disabled wait as `-EOPNOTSUPP`, checks GISA pending ISCs, and either puts the vCPU into idle state without a timer or arms `vcpu->arch.ckc_timer` using `__calculate_sltime()`. It drops the vCPU SRCU read lock before `kvm_vcpu_halt()` and reacquires it afterward. `kvm_s390_idle_wakeup()` recalculates sleep time to compensate monotonic/TOD clock drift and wakes the vCPU when a timer interrupt should become visible.

### Floating I/O and TPI Path

Queued I/O interrupts live on per-ISC lists. `kvm_s390_get_io_int()` first attempts to remove a classic queued interrupt matching the guest ISC mask and optional subchannel ID. It also checks GISA IPM bits if no subchannel-specific clear is requested. If both classic and GISA adapter interrupts are present, it compares priority by ISC and reinserts the lower-priority source. When GISA wins, it synthesizes a `KVM_S390_INT_IO(1,0,0,0)` interrupt with `io_int_word` generated from the ISC.

### FLIC and Migration Path

The FLIC device provides userspace with bulk get/enqueue/clear of floating interrupts and adapter control. `get_all_floating_irqs()` drains GISA IPM bits while materializing adapter IRQ records, then snapshots all queue lists plus pending service and machine-check state. If the buffer fills, it returns `-ENOMEM` as a retry-with-larger-buffer signal. Local IRQ migration uses `kvm_s390_get_irq_state()` to copy local pending bits and emergency-source bitmap, plus any SCA external call, into a userspace buffer. Restore via `kvm_s390_set_irq_state()` refuses to overwrite existing pending local interrupts.

### GISA/GIB Alert Flow

GISA use is initialized per VM when AIV is available and optionally enabled on vCPUs by storing a GISA descriptor in the SIE block and setting `ECA_AIV`. Adapter interrupts set GISA IPM bits. When millicode queues GISAs on the global GIB alert list, `gib_alert_irq_handler()` calls `process_gib_alert_list()`, which atomically detaches the alert list and starts the per-VM `gisa_vcpu_kicker()` timer for each listed GISA. The timer checks pending ISCs against alert masks and idle vCPU CR6 masks, waking one eligible vCPU at a time. `gisa_get_ipm_or_restore_iam()` restores IAM when no relevant IPM remains, reducing further alert traffic.

## State and Persistence Behavior

Persistent VM/vCPU state is held in:

- `vcpu->arch.local_int`: spinlock, `pending_irqs`, `sigp_emerg_pending`, and union payload `irq`.
- `kvm->arch.float_int`: spinlock, per-type lists, counters, service-signal payload, floating machine-check payload, `pending_irqs`, `masked_irqs`, `last_sleep_cpu`, AIS masks (`simm`, `nimm`), and `ais_lock`.
- `kvm->arch.gisa_int`: GISA origin pointer, alert mask/refcounts, kicked-idle bitmap, wake timer, and expiry interval.
- `kvm->arch.adapters[]`: registered I/O adapter descriptors.
- Global `gib`: one host-wide GIB page used by the alert-list mechanism.

The file has explicit migration surfaces for local IRQ state (`KVM_S390_GET_IRQ_STATE`/`SET_IRQ_STATE`, implemented here and dispatched from `kvm-s390.c`) and floating IRQ state (`KVM_DEV_FLIC_GET_ALL_IRQS`/`ENQUEUE`). It also clears all pending state during reset/destroy paths. GISA pending adapter interrupts are treated as migratable floating IRQs by converting IPM bits to synthetic adapter I/O records.

State is protected by spinlocks for hot interrupt data, mutexes for adapter/AIS and VM-level mutation, atomic bit operations for GISA fields, and SRCU around guest memory/indicator writes. Lowcore writes and SIE field updates are the durable guest-visible effects of delivery.

## Dependencies and Integration Points

This file depends on:

- s390 KVM core structures from `kvm-s390.h`, including SIE blocks, local/floating interrupt structures, CPUSTAT bits, PV helpers, and request/wakeup helpers.
- Guest memory helpers from `gaccess.h` and `gmap.h` for lowcore writes, absolute writes, prefix handling, and dirty marking.
- Generic Linux KVM APIs for vCPU wakeups, async page faults, IRQ routing, device attributes, SRCU, stats, and userspace copy helpers.
- s390 architecture headers for lowcore offsets, PSW masks, CR masks, interrupt subclass bits, machine-check fields, SCLP, adapter interrupts, TPI, and atomic inverse-bit operations.
- Optional zPCI support (`pci.h`, `CONFIG_VFIO_PCI_ZDEV_KVM`) for adapter event notification forwarding.

Major integration points include `kvm_arch_vcpu_ioctl_run()` via `kvm_s390_deliver_pending_interrupts()`, VM ioctls via `kvm_s390_inject_vm()`, vCPU ioctls via `kvm_s390_inject_vcpu()` and IRQ state get/set, KVM device framework via `kvm_flic_ops`, generic IRQ routing via `kvm_set_routing_entry()`, and module init/exit via `kvm_s390_gib_init()`/`destroy()`.

## Risks and Edge Cases

- Interrupt priority and mask filtering are architecture-sensitive. Bugs in `deliverable_irqs()`, ISC conversion, or pending-bit ordering can cause lost, delayed, or misprioritized guest interrupts.
- GISA operations rely on atomic manipulation of packed IAM/IPM/next-alert fields and special sentinel addresses. Incorrect compare/exchange handling could race with millicode alert-list updates.
- Service interrupts intentionally coalesce or suppress duplicate SCCB parameters for old QEMU behavior; changes can affect migration and firmware compatibility.
- `get_all_floating_irqs()` consumes GISA IPM bits while building migration state. Error handling must preserve or reinject state carefully, or adapter interrupts can be lost.
- Adapter indicator writes pin userspace pages with `get_user_pages_remote()`, set bits directly, and mark pages dirty. Address validation in routing setup is therefore critical.
- Protected virtualization paths diverge from normal lowcore delivery. Attempting normal lowcore writes for protected guests, or injecting while `iictl` already contains a protected interruption, can produce validity/interruption ordering failures.
- Stop/restart/set-prefix semantics depend on stopped state and CPUSTAT ordering. Races here can affect SIGP BUSY/SENSE behavior.
- Some functions return `-EBUSY` to represent full queues or already pending conditions; userspace and callers must be prepared to retry or serialize.

## Test Signals

Useful validation signals include:

- KVM selftests or QEMU migration tests that round-trip `KVM_S390_GET_IRQ_STATE`, `KVM_S390_SET_IRQ_STATE`, and FLIC get/enqueue for local, floating, service, virtio, pfault, I/O, and GISA-backed adapter interrupts.
- s390 interrupt delivery tests that toggle PSW masks, CR0 submasks, CR6 ISC masks, CR14 machine-check masks, and verify lowcore old/new PSW fields.
- Timer/wait tests covering clock-comparator sign mode, CPU timer expiration, wait without timer, and hrtimer wakeups.
- Protected-virtualization tests for external, I/O, machine-check, restart, program, and service delivery through SIE fields rather than lowcore writes.
- Adapter interrupt tests for FLIC adapter registration, mask/unmask, AIS single/all modes, indicator bit setting, summary coalescing, irqfd routing, and GISA/AIV operation.
- Concurrency tests around simultaneous injection/delivery/clear, full floating queues, duplicate external calls, and destroy/reset with pending interrupts.
- Tracepoints and stats counters such as `deliver_*`, `inject_*`, `trace_kvm_s390_deliver_interrupt`, `trace_kvm_s390_inject_vm`, `trace_kvm_s390_modify_ais_mode`, and `kvm->stat.aen_forward`.
