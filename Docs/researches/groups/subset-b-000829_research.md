# subset-b-000829 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/interrupt.c -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/interrupt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/kvm-s390.c -->
# sources/distributed-fs/ceph-client/arch/s390/kvm/kvm-s390.c

## Purpose

`kvm-s390.c` is the main s390 architecture implementation for KVM. It wires the IBM Z/SIE execution engine into the generic KVM framework, exposes s390-specific VM and vCPU ioctls, initializes CPU models and facilities, manages VM/vCPU creation and destruction, implements protected virtualization command dispatch, controls memory-slot/gmap behavior, synchronizes guest-visible registers, and runs the SIE enter/exit loop.

The file owns the architecture-wide lifecycle: module init registers debug facilities, the FLIC device, PCI/GIB support, and the KVM core; VM init allocates SCA/SIE/GISA/gmap/crypto state; vCPU init allocates SIE pages and configures SIE control bits; `KVM_RUN` synchronizes userspace state, enters SIE, handles intercepts/faults, and stores state back.

## Important APIs, Types, and Functions

Module and feature setup:

- Module parameters: `nested`, `hpage`, `halt_poll_max_steal`, `use_gisa`, `diag9c_forwarding_hz`, and `async_destroy`.
- Stats descriptors `kvm_vm_stats_desc` and `kvm_vcpu_stats_desc` define VM/vCPU counters used by KVM stats ABI.
- `kvm_s390_cpu_feat_init()` detects host CPU subfunctions/facilities for PLO, PTFF, CPACF/MSA, SORTL, DFLTCC, PFCR, nested SIE-related features, and stores available CPU features in `kvm_s390_available_cpu_feat` and `kvm_s390_available_subfunc`.
- `__kvm_s390_init()` registers debug views, FLIC ops, optional PCI state, GIB alert support, and the TOD epoch notifier.
- `kvm_s390_init()` checks SIE availability, augments base facility masks with non-hypervisor-managed facilities, calls architecture init, and registers with generic `kvm_init()`.

Capability and VM attribute APIs:

- `kvm_vm_ioctl_check_extension()` reports s390 capabilities and capability values, including IRQCHIP, memory operations, CPU model/topology, protected virtualization, protected dump, zPCI, vector/RI/GS/BPB facilities, hpage support, and max vCPU IDs.
- `kvm_vm_ioctl_enable_cap()` enables VM-level capabilities such as IRQCHIP, user SIGP/STSI/instr0/operexc, vector registers, RI, AIS, GS, huge pages, CPU topology, and VSIE ESA mode.
- `kvm_s390_vm_set_attr()`, `kvm_s390_vm_get_attr()`, and `kvm_s390_vm_has_attr()` dispatch KVM device-attribute groups for memory control, TOD, CPU model, crypto, migration, and CPU topology.
- CPU model helpers set/get processor IDs, IBC, facility masks/lists, CPU feature bitmaps, subfunction blocks, and UV guest feature exposure.
- TOD helpers set/get guest epoch and epoch index, while `kvm_clock_sync()` tracks host TOD adjustments across all VMs/vCPUs.

Memory, keys, migration, and protected virtualization:

- `kvm_s390_get_skeys()`/`kvm_s390_set_skeys()` get/set storage keys through DAT/gmap helpers.
- `kvm_s390_get_cmma_bits()`/`kvm_s390_set_cmma_bits()` expose CMMA state for migration and use dirty-page accounting.
- `kvm_s390_vm_start_migration()` and `kvm_s390_vm_stop_migration()` switch CMMA migration mode and broadcast vCPU requests.
- `kvm_s390_handle_pv()` dispatches VM-level protected virtualization commands such as enable, disable, async cleanup prepare/perform, set secure parameters, unpack, verify, prepare reset, unshare all, info, and dump.
- `kvm_s390_cpus_to_pv()` and `kvm_s390_cpus_from_pv()` convert vCPUs into or out of protected mode and coordinate GISA use depending on UV AIV support.
- `kvm_s390_pv_dmp()` and `kvm_s390_handle_pv_vcpu_dump()` implement protected VM/CPU dump subcommands.
- `kvm_s390_vm_mem_op_abs()`, `kvm_s390_vm_mem_op_cmpxchg()`, `kvm_s390_vcpu_mem_op()`, and `kvm_s390_vcpu_sida_op()` implement VM and vCPU memory operation ABI variants.

VM/vCPU lifecycle:

- `kvm_arch_init_vm()` allocates SCA, per-VM debug state, `sie_page2`, facility masks, crypto block, floating-interrupt lists, gmap, optional ucontrol fake memslot, VSIE state, GISA, and protected-VM cleanup lists.
- `kvm_arch_destroy_vm()` destroys vCPUs, SCA, GISA, protected VM state, mmu notifier, debug state, adapters, floating IRQs, VSIE state, and gmap.
- `kvm_arch_vcpu_create()` allocates an MMU cache and SIE page, initializes low-level SIE fields, KVM sync-reg masks, optional ucontrol child gmap, then calls `kvm_s390_vcpu_setup()`.
- `kvm_s390_vcpu_setup()` sets initial CPUSTAT bits, guest model fields, SIE control bits for host/guest facilities, prefix-notification and interrupt behavior, CMMA, timers, crypto, zPCI, and PV CPU creation.
- `kvm_arch_vcpu_destroy()` clears local IRQs and async-pf queues, removes the vCPU from SCA/gmap, destroys PV CPU state, frees CMMA/SIE/MMU-cache state, and reports topology changes.
- SCA helpers `sca_add_vcpu()`, `sca_del_vcpu()`, and `sca_can_add_vcpu()` manage ESCA/SCA references and max vCPU ID limits.

Run loop and register synchronization:

- `kvm_arch_vcpu_ioctl_run()` implements `KVM_RUN`: validates sync fields, loads the vCPU, activates signal masks, starts the vCPU if KVM controls CPU state, syncs userspace registers into SIE state, enables CPU-timer accounting, runs `__vcpu_run()`, handles signals/debug/userspace exits, stores registers back, and unloads the vCPU.
- `__vcpu_run()` loops with SRCU held outside guest execution, calls `vcpu_pre_run()`, prepares guest-mode entry, disables CPU timer accounting while the guest runs, enters SIE via `kvm_s390_enter_exit_sie()`, reenables accounting, then calls `vcpu_post_run()`.
- `vcpu_pre_run()` checks async page completions, refreshes GPR14/GPR15, delivers pending interrupts, handles KVM requests, patches PER debug state, clears GISA kicked state, and emits SIE enter traces.
- `vcpu_post_run()` restores debug PER state, handles machine-check SIE returns, dispatches SIE intercepts via `kvm_handle_sie_intercept()`, or handles DAT/protected-storage faults.
- `sync_regs()`, `sync_regs_fmt2()`, `store_regs()`, and `store_regs_fmt2()` transfer PSW, prefix, control/access/general/floating/vector registers, CPU timer, clock comparator, pfault controls, runtime instrumentation, guarded storage, branch prediction control, etoken, and diag318 state between `struct kvm_run` and the SIE block.

vCPU control and ioctl APIs:

- `kvm_s390_vcpu_start()`/`kvm_s390_vcpu_stop()` transition STOPPED/OPERATING state with start-stop serialization, UV state changes for protected CPUs, IBS enable/disable policy, TLB flush requests, and stop IRQ clearing.
- Reset helpers implement normal, initial, and clear resets, including PV reset UVC calls.
- `kvm_arch_vcpu_ioctl()` handles store-status, initial PSW, resets, one-reg access, ucontrol mapping/faulting, vCPU capability enable, vCPU mem/SIDA ops, local IRQ state get/set, and protected CPU dump commands.
- `kvm_arch_vcpu_unlocked_ioctl()` handles unlocked injection ioctls and clears a pending single-step debug exit when userspace injects an interrupt after emulation.

Memory-slot integration:

- `kvm_arch_prepare_memory_region()` rejects invalid ucontrol slots, protected-VM slot changes, unaligned/out-of-limit memory, and stops CMMA migration mode if dirty logging assumptions are invalidated.
- `kvm_arch_commit_memory_region()` creates/deletes/moves DAT slot mappings under the MMU write lock.
- `kvm_test_age_gfn()`, `kvm_age_gfn()`, and `kvm_unmap_gfn_range()` delegate age/unmap operations to DAT/gmap helpers.

## Control Flow

### Module and VM Creation

`kvm_s390_init()` refuses to load without SIE facility support, adjusts base facility masks for non-hypervisor-managed facilities, initializes s390-specific global state, then registers KVM. Global init sets up debug buffers, detects feature/subfunction availability, registers the FLIC device, initializes optional zPCI state, initializes GIB alert support, and registers a TOD epoch notifier.

VM creation in `kvm_arch_init_vm()` validates VM type and privileges, allocates SCA and `sie_page2`, initializes the guest CPU model from host facilities and KVM policy, sets default emulated facilities, initializes crypto state, optional PCI interpretation, floating interrupt state, gmap, ucontrol fake memory when requested, memory feature flags, start/stop lock, VSIE state, optional GISA, and protected-VM cleanup lists. Error paths free partially initialized SIE/debug/SCA resources.

vCPU creation allocates a SIE page and MMU cache, initializes SIE block addresses and memory-size limits, sets sync-register validity based on available facilities, optionally creates a ucontrol child gmap, and configures SIE execution controls in `kvm_s390_vcpu_setup()`. Post-create synchronizes TOD epoch, attaches the vCPU to the VM gmap/SCA, and enables operation-exception interception if needed.

### VM Configuration and Migration

Most VM configuration flows are userspace ioctls routed through `kvm_arch_vm_ioctl()` or generic device attributes. Capability enables generally take `kvm->lock`, reject changes after vCPU creation when the ABI requires a stable CPU model, and update facility masks/lists or VM behavior flags. Memory-control attributes manage CMMA, memory limits, and dirty CMMA reset. CPU-model attributes allow userspace to select guest-visible CPU/facility/subfunction/UV-feature state before vCPU creation.

Migration mode requires memslots and, when CMMA is active, dirty bitmaps for all slots. Starting migration marks all CMMA pages dirty and disables direct CMMA virtualization on vCPUs via requests. Stopping migration reenables CMMA virtualization when possible. Memory-slot changes that invalidate dirty logging assumptions force migration mode off.

### Protected Virtualization

Protected virtualization command handling is centralized in `kvm_s390_handle_pv()`. `KVM_PV_ENABLE` disables THP creation, sets export-on-unmap, disables COW sharing, initializes the protected VM through UV, converts all vCPUs to protected mode, and masks service interrupts. Disable and async cleanup convert CPUs back from PV, deinitialize or set aside protected VM state, and clear service-interrupt masking. PV page faults in the run loop distinguish secure/non-secure storage exceptions, destroy stale secure pages after async teardown, or import pages into the protected guest.

Protected guests change several normal flows: many ioctls such as one-reg and memory operations are rejected, run-loop GPRs are copied through `sie_page->pv_grregs`, interrupts may be fenced in the internal PSW after certain PV intercepts, and reset/state changes use UV commands.

### KVM_RUN and SIE

`kvm_arch_vcpu_ioctl_run()` is the userspace-facing entry point. It rejects running while a protected dump is active, validates sync-reg masks, loads the vCPU, starts it if KVM owns CPU state, syncs userspace registers, enables CPU timer accounting, and calls `__vcpu_run()`.

`__vcpu_run()` repeatedly:

- Holds SRCU while preparing and post-processing host-side state.
- Calls `vcpu_pre_run()` to process async-pf completions, deliver pending interrupts, handle requests, patch guest debug PER state, and prepare trace state.
- Drops SRCU, prepares guest mode, disables CPU timer accounting because hardware/SIE accounts the running guest, enters SIE through `sie64a()`, reenables timer accounting, and reacquires SRCU.
- Copies PV GPRs back if needed and calls `vcpu_post_run()` to handle machine checks, SIE intercepts, or DAT/protected-storage faults.

Userspace exits are represented by `-EREMOTE` internally after `kvm_run` has been prepared; `kvm_arch_vcpu_ioctl_run()` converts that to a successful ioctl return. Signals become `KVM_EXIT_INTR` and `-EINTR`. Debug exits are prepared after interrupt delivery or SIE exits when single-step/PER requires userspace notification.

### Requests, Faults, and Async Page Faults

`kvm_s390_handle_requests()` drains architecture requests by clearing the SIE request bit, refreshing prefix notification pages, flushing TLBs via `ihcpu`, toggling IBS, enabling operation-exception interception, switching CMMA virtualization for migration, and consuming VSIE restart requests. Prefix refresh can return errors and requeue itself.

Fault handling after SIE uses `current->thread.gmap_int_code` and TEID. Translation/protection faults call `vcpu_dat_fault_handler()`, which can translate ucontrol addresses and fault in the relevant gfn. Secure-storage faults are PV-specific and either destroy stale secure pages or import pages into the protected VM. Async page faults inject pfault-init and pfault-done interrupts through the interrupt file rather than using a separate completion queue semantics.

## State and Persistence Behavior

Important per-VM state includes:

- `kvm->arch.sca`, `sie_page2`, `gmap`, `mem_limit`, facility model, CPU feature bitmaps, subfunction blocks, CPUID/IBC, TOD epoch/epoch-index, crypto CRYCB state, floating interrupt state, adapter list, GISA state, VSIE state, PV state, migration flags, CMMA dirty count, topology change bit, and debug buffer.
- `kvm->arch.model.fac_mask` and `fac_list` are userspace-visible CPU model state and are copied into vCPU SIE setup.
- `kvm->arch.pv` tracks protected VM handles, dumping state, cleanup lists, import locks, and notifier state.

Important per-vCPU state includes:

- `vcpu->arch.sie_block`, `gmap`, MMU cache, local interrupt state, CPU timer seqcount/start/enabled fields, pfault token/select/compare, debug/PER state, guarded-storage host backup, host access registers, local hrtimer, diag318 state, and PV CPU handle/state.
- `vcpu->run->s.regs` is the userspace synchronization area. `kvm_valid_regs` advertises which fields are supported and `kvm_dirty_regs` controls inbound synchronization.

State persists across userspace exits via explicit sync in `store_regs()`, VM/vCPU ioctls, migration APIs, and KVM device attributes. Runtime-only state such as host ACRS/FPU/GS controls is lazily loaded and restored around `KVM_RUN`. CPU timer accounting uses a seqcount plus preemption disabling to coordinate host TOD changes, vCPU load/put, and cross-vCPU reads.

## Dependencies and Integration Points

The file integrates with:

- Generic KVM core: module registration, VM/vCPU lifecycle hooks, ioctls, dirty logging, memslots, requests, SRCU, stats, halt polling, signal masks, and guest-mode entry helpers.
- s390 SIE assembly (`sie64a`) and SIE block format, including CPUSTAT/prog20 request bits, SCA/ESCA, facility controls, and interception fields.
- s390 memory translation (`gmap`, DAT helpers, storage keys, CMMA, prefix notification, ucontrol child gmappings).
- s390 protected virtualization (`uv.h` and KVM PV helpers) for VM/CPU create/destroy, secure page import/export, dump, reset, and UV feature reporting.
- Interrupt handling in `interrupt.c` for FLIC registration, IRQ injection/delivery, local/floating IRQ state, GISA/GIB, async page fault interrupt injection, and stop IRQ clearing.
- Optional zPCI and AP crypto integration through `pci.h`, AP instruction availability, CRYCB masks, and exported crypto mask functions.
- Debug/perf/trace infrastructure through debug feature buffers, `trace-s390.h`, and KVM event macros.

## Risks and Edge Cases

- The run loop depends on precise ordering of SRCU, guest-mode entry work, interrupt delivery, request handling, CPU timer accounting, FPU/ACR/GS state, and local IRQ state. Reordering can produce host state leaks, lost requests, or invalid guest timing.
- Protected virtualization introduces split behavior for memory slots, register access, interrupt injection, PV faults, dumping, and reset. Normal code paths must be fenced when a PV handle exists.
- VM configuration APIs often require no vCPUs to exist. Missing `kvm->lock` checks or allowing late CPU model changes can break migration ABI and SIE setup consistency.
- TOD/epoch changes are synchronized with preemption disabled and vCPU blocking. Races with vCPU load/put or CPU timer accounting can corrupt guest timer state.
- Memory operations intentionally reject protected VMs only heuristically in VM-level paths; concurrent PV transitions are considered userspace misuse but still must fail safely at access time.
- CMMA migration depends on dirty logging being active for every slot. Slot changes can silently force migration mode off via warning path.
- SCA/ESCA limits differ depending on SCA entry support, affecting max vCPU ID and external-call interpretation behavior.
- ucontrol mode uses fake memslots and child gmappings; normal VM assumptions about memory slots and address translation do not always apply.
- `exit_sie()` busy-waits until SIE leaves `PROG_IN_SIE`; misuse in contexts where the vCPU cannot make progress would deadlock.

## Test Signals

Useful validation signals include:

- KVM s390 selftests for capability probing, CPU model get/set, subfunction filtering, VM attributes, TOD set/get, topology change reporting, memory limits, and huge-page/CMMA incompatibilities.
- QEMU boot, reset, hotplug, migration, and protected-virtualization scenarios that exercise VM/vCPU creation, SCA/ESCA limits, IRQCHIP, FLIC, GISA, and CPU model ABI.
- `KVM_RUN` tests covering stopped/runnable state, signal exits, userspace SIE intercept exits, single-step/debug exits, operation-exception interception, and register sync masks.
- Storage key, CMMA, MEM_OP, CMPXCHG, SIDA, and ucontrol fault tests with boundary sizes, invalid flags, protected-VM rejection, and injected exception behavior.
- Protected virtualization tests for enable/disable, async cleanup, secure parameter import, unpack, verify, reset, unshare, dump init/config/cpu/complete, and secure/non-secure storage fault handling.
- Timer tests for CPU timer seqcount correctness, host TOD delta notifier handling, halt polling with steal-time cap, and migration of timer-related registers.
- Memory-slot tests that create/delete/move slots under normal, migration, ucontrol, and protected-VM states.
- Trace/stat counters from `kvm_vm_stats_desc`, `kvm_vcpu_stats_desc`, `trace_kvm_s390_sie_enter/exit`, vCPU start/stop traces, PV event logs, and debug feature buffers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/kvm/kvm-s390.c -->
