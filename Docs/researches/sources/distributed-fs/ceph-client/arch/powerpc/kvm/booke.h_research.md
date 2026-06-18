<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke.h

Purpose: Declares the common BookE KVM interrupt-priority model, public helper interfaces, and low-level assembly hooks shared by BookE core, e500 code, and BookE PR/HV interrupt handlers.

Important APIs/types/functions: Defines `BOOKE_IRQPRIO_*` priority constants, `BOOKE_IRQMASK_EE`, `BOOKE_IRQMASK_CE`, external handler symbols `kvmppc_booke_handlers` and `kvmppc_booke_handler_addr`, MSR/timer setters, BookE instruction and SPR emulation entry points, SPE save/load assembly routines, vCPU load/put helpers, `enum int_class`, `kvmppc_set_pending_interrupt()`, e500-specific emulation dispatch declarations, `kvmppc_clear_dbsr()`, and `kvmppc_handle_exit()`.

Control flow: The header has no runtime control flow beyond `kvmppc_clear_dbsr()`. It defines the numeric priority ordering consumed by `booke.c` when scanning `pending_exceptions` and by assembly/C handlers when converting hardware exception numbers into guest exception classes.

State and persistence: It names state rather than storing it. The priority constants map pending-exception bit positions in `vcpu->arch.pending_exceptions`; masks summarize exceptions gated by MSR[EE] and MSR[CE]. Assembly symbols point to copied PR-mode handlers or linked HV handlers.

Dependencies and integration points: Includes KVM host types, PowerPC KVM arch state, `switch_to.h`, and `timing.h`. Used by `booke.c`, `booke_emulate.c`, both BookE assembly files, and e500/e500mc code.

Risks: Priority values are ABI-like inside this implementation; reordering can change exception delivery semantics. Conditional SPE and AltiVec priority definitions overlap intentionally by platform and must stay consistent with IVOR mapping code. The duplicate e500 SPR declarations are harmless but brittle for cleanup.

Test signals: BookE builds across `CONFIG_SPE_POSSIBLE`, `CONFIG_PPC_E500MC`, `CONFIG_KVM_BOOKE_HV`, and PR-mode configs, plus runtime interrupt-priority tests, are the main signals.

Source read size: 115 lines, 3757 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kvm/booke.h -->
