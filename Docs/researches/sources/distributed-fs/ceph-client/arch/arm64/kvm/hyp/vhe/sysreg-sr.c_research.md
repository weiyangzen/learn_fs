# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vhe/sysreg-sr.c

## Purpose
This file implements VHE system-register save/restore for host, guest EL1, and virtual EL2 contexts. It lets KVM avoid saving all EL1-visible state on every exit while still handling nested virtualization cases where the guest runs a virtual hypervisor.

## Important APIs, Types, and Functions
- `__sysreg_save_vel2_state()` and `__sysreg_restore_vel2_state()` translate between the CPU's EL1 register view and the vCPU's virtual EL2 sysreg array.
- `sysreg_save_host_state_vhe()`, `sysreg_save_guest_state_vhe()`, `sysreg_restore_host_state_vhe()`, and `sysreg_restore_guest_state_vhe()` wrap common and return-state helpers.
- `__vcpu_load_switch_sysregs()` loads guest/user/EL1 or virtual EL2 state on vCPU load.
- `__vcpu_put_switch_sysregs()` saves guest state and restores host user state on vCPU put.
- `__mpam_guest_load()` maps host EL0 MPAM partition state into guest MPAM1 when supported.

## Control Flow
On load, the host user state is saved, nested guests receive a DSB to complete speculative walks, AArch32 state is restored before sysregs for CPU errata, guest user state and MPAM state are restored, and either virtual EL2 or EL1 state is written to hardware. On put, virtual EL2 or EL1 state is saved, guest user and AArch32 state are saved, host user state is restored, and `SYSREGS_ON_CPU` is cleared.

Virtual EL2 save stores common EL1-compatible registers into their EL2 slots and, when E2H is set, saves compatible SCTLR/TTBR/TCR/CNTHCTL-style state directly from EL1-named sysregs. Restore reverses the process, translating SCTLR/CPTR/TTBR/TCR from EL2 to EL1 format when the virtual EL2 is not in E2H mode.

## State and Persistence
State persists in `struct kvm_cpu_context` and the vCPU sysreg array. The file handles PAR, TPIDR, ESR/AFSR/FAR, MAIR/AMAIR, VBAR, CONTEXTIDR, SCTLR/TTBR/TCR/TCR2, PIRE/PIR/POR, CNTHCTL/CNTKCTL, SP/ELR/SPSR, SCTLR2, VPIDR/VMPIDR, user registers, and AArch32 state. It marks whether sysregs are currently on CPU with `SYSREGS_ON_CPU`.

## Dependencies and Integration Points
It depends on common hyp sysreg helpers, nested virtualization translation helpers, MPAM support, feature predicates for TCR2/S1PIE/S1POE/SCTLR2, and the VHE run/load/put flow in `switch.c`.

## Risks and Edge Cases
Ordering is critical: AArch32 restore must precede sysregs for affected CPUs, speculative walks must complete before NV context switches, and CPACR/CPTR are special because CPACR_EL1 is trapped to keep CPTR_EL2's memory copy current. Incorrect E2H translation can corrupt a nested hypervisor's view of EL2 state.

## Test Signals
Run nested virtualization sysreg tests, VHE load/put stress, AArch32 guest tests, MPAM-enabled configurations, TCR2/S1PIE/S1POE/SCTLR2 feature combinations, and migration tests that compare sysreg state before and after repeated exits.
