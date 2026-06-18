<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke.c

Purpose: Provides the generic PowerPC BookE KVM core for vCPU state management, exception prioritization and delivery, guest run/exit handling, timer/watchdog emulation, register ioctls, debug support, memory-slot hooks, and subarchitecture delegation.

Important APIs/types/functions: Defines BookE VM/vCPU stats descriptors, `kvmppc_dump_vcpu()`, `kvmppc_set_msr()`, exception queue helpers, `kvmppc_core_prepare_to_enter()`, `kvmppc_core_check_requests()`, `kvmppc_vcpu_run()`, `kvmppc_handle_exit()`, get/set regs and sregs ioctls, one-reg get/set, timer setters `kvmppc_set_tcr()`, `kvmppc_set_tsr_bits()`, `kvmppc_clr_tsr_bits()`, decrementer/watchdog functions, `kvmppc_xlate()`, guest-debug ioctl support, vCPU load/put wrappers, VM/vCPU lifecycle wrappers, and `kvmppc_booke_init()/exit()`.

Control flow: The run path prepares entry, loads guest FP/AltiVec/debug context, calls assembly `__kvmppc_vcpu_run()`, then restores host context. Low-level assembly returns to `kvmppc_handle_exit()`, which restarts host-owned interrupts, fetches faulting instructions when needed, accounts guest exit time, dispatches by BookE interrupt number, either queues a guest exception, handles MMIO/TLB misses, emulates privileged instructions, exits to userspace, or resumes the guest. Before entry, pending exception bits are scanned in priority order and delivered only when the guest MSR allows the relevant class.

State and persistence: Owns `vcpu->arch.pending_exceptions`, queued DEAR/ESR, IVPR/IVORs, CSRR/DSRR/MCSRR, MSR/shadow MSR, timer TSR/TCR/DEC/DECAR, watchdog timer and lock, FP/SPE/AltiVec/debug state, guest debug registers, EPR state, shared page registers, and timing/stat counters. VM memory-slot hooks are mostly no-ops for this nohash BookE path.

Dependencies and integration points: Depends on BookE assembly handlers, subarch `kvmppc_ops` for e500/e500mc-specific MMU and SPR behavior, PowerPC timebase and interrupt APIs, KVM generic request/exit machinery, KVM user ABI structs, `trace_booke`, FPU/SPE/AltiVec helpers, MPIC/EPR integration, and host exception handlers for restarted host interrupts.

Risks: Exception delivery depends on correct priority masks, critical-section detection, and MSR class gating. Guest/host FP, AltiVec, SPE, debug, PID, and interrupt state transitions are sensitive to preemption and interrupt state. Watchdog arithmetic can flood timers if final expiry is mishandled. Exit dispatch has many architecture-specific cases where a wrong resume flag can corrupt nonvolatile registers or lose a userspace exit.

Test signals: BookE/e500 KVM boot tests, TLB miss and MMIO tests, timer/decrementer/watchdog tests, guest debug break/watch/singlestep tests, FP/SPE/AltiVec context switching, signal-interrupted `KVM_RUN`, register ioctl round trips, and KVM selftests/QEMU e500 guests are the strongest signals.

Source read size: 2242 lines, 58285 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke.c -->
