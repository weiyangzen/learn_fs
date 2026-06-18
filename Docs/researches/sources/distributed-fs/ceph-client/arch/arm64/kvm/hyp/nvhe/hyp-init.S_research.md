<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-init.S -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-init.S

## Purpose
`hyp-init.S` is the identity-mapped EL2 bootstrap for nVHE. It accepts the initial host HVC, initializes EL2 state and MMU registers from `kvm_nvhe_init_params`, installs host vectors, provides CPU_ON/resume entry points for PSCI relay, handles hyp-stub reset calls, and switches to rebuilt protected page tables during pKVM initialization.

## Important APIs, Types, and Functions
`__kvm_hyp_init` is an idmap vector whose lower-EL sync slot accepts `KVM_HOST_SMCCC_FUNC(__kvm_hyp_init)` or stub HVC calls. `___kvm_hyp_init` loads stack, MAIR, HCR, TPIDR_EL2, VTTBR, VTCR, TTBR0, TCR, SCTLR, and VBAR_EL2. `__kvm_init_el2_state` wraps common EL2 initialization macros. `kvm_hyp_cpu_entry` and `kvm_hyp_cpu_resume` initialize secondary/resumed CPUs and branch into PSCI C entry points. `__kvm_handle_stub_hvc` implements soft restart and vector reset. `__pkvm_init_switch_pgd` turns MMU off, installs a new TTBR0_EL2 and stack, re-enables MMU, and tail-calls a C finalizer.

## Control Flow, State, and Persistence
Initial HVCs arrive while executing in idmap text. The code validates the SMCCC function id, initializes EL2 state without clobbering callee-saved SMCCC registers, enables the EL2 MMU, and returns success. CPU_ON/resume paths verify the core is at EL2, replay EL2 setup, leave idmap through PSCI entry callbacks, or park forever on failure. `__pkvm_init_switch_pgd` is used once pKVM has built replacement page tables and must preserve architectural ordering with TLB invalidation and ISBs.

## Dependencies and Integration Points
It depends on `kvm_nvhe_init_params` layout constants, EL2 setup assembler macros, hyp host vectors from `host.S`, PSCI relay entry functions from `psci-relay.c`, and pKVM setup in `setup.c`. It integrates with the host stub ABI and architecture alternatives for CnP, pointer authentication, and BTI.

## Risks and Test Signals
Risks include incorrect ordering around MMU disable/enable, stale TLBs, bad hVHE E2H replay, wrong stack or VBAR setup on secondary CPUs, and kCFI-sensitive indirect calls to idmap code. Test signals are nVHE boot on primary and secondary CPUs, suspend/resume paths, protected-mode finalization, soft-restart/reset-vector behavior, and architectural feature combinations for CnP, ptrauth, BTI, and hVHE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/hyp-init.S -->
