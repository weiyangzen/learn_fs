<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-main.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-main.c

## Purpose
`hyp-main.c` is the C trap and hypercall dispatcher for nVHE. It handles host HVC/SMC/memory-abort traps, runs guest vCPUs, synchronizes host and hyp vCPU state, exposes pKVM memory/VM/tracing hypercalls, forwards PSCI/FF-A/unknown SMCs, and injects host exceptions when EL2 must reflect faults back to EL1.

## Important APIs, Types, and Functions
`handle_trap()` dispatches by ESR exception class. `handle_host_hcall()` decodes KVM host SMCCC ids and calls the `host_hcall[]` table. `handle_host_smc()` routes PSCI through `kvm_host_psci_handler()`, FF-A through `kvm_host_ffa_handler()`, and other calls through `__kvm_hyp_host_forward_smc()`. `handle___kvm_vcpu_run()` chooses direct unprotected guest run or protected hyp-vCPU run. `flush_hyp_vcpu()` and `sync_hyp_vcpu()` copy registers, debug state, VGIC state, FP/SVE ownership, HCR flags, faults, and iflags between host and hyp vCPU objects. Numerous `handle___pkvm_*` wrappers validate loaded handles/vCPUs, refill memcaches, and call `mem_protect.c`, `pkvm.c`, `mm.c`, and `trace.c`.

## Control Flow, State, and Persistence
The persistent state is mainly per-CPU `kvm_init_params` and transient host context register values. Early pKVM setup hypercalls are rejected after protected mode initialization except finalization; later hypercalls operate through published VM handles or the currently loaded hyp vCPU. Guest entry copies host vCPU state to hyp state before `__kvm_vcpu_run()` and copies it back after exit. SMC traps advance ELR after handling; host memory aborts are resolved by lazily mapping allowed host stage-2 regions or injecting aborts.

## Dependencies and Integration Points
It integrates host assembly entry/exit, pKVM VM lifecycle (`pkvm.c`), ownership transitions (`mem_protect.c`), TLB operations (`tlb.c`), timer and VGIC helpers, PSCI relay, FF-A proxy, tracing, protected VM sysreg/HVC handlers, and generic KVM ARM guest-run code.

## Risks and Test Signals
Risks include wrong hypercall gating before/after pKVM initialization, accepting stale or missing loaded hyp vCPUs, incomplete vCPU state synchronization, memcache refill failures propagating poorly, and host exception injection bugs. Tests should cover each host hypercall id, protected and non-protected vCPU runs, pKVM memory share/donate/unshare with empty memcaches, PSCI/FF-A passthrough interactions, host abort reinjection, tracing hypercalls, and invalid hypercall ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-main.c -->
