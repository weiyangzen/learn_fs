# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/hyp/switch.h

## Purpose

This header contains most inline hyp world-switch logic: trap activation/deactivation, FP/SVE lazy handling, fast sysreg/MMIO exits, fault population, exit fixup, and unexpected EL2 exception recovery.

## Important APIs, Types, And Functions

Important helpers include `__activate_cptr_traps_*()`, `__activate_traps_common()`, `___activate_traps()`, `___deactivate_traps()`, `kvm_hyp_handle_fpsimd()`, `kvm_hyp_handle_sysreg()`, `kvm_hyp_handle_dabt_low()`, `kvm_hyp_handle_exit()`, `synchronize_vcpu_pstate()`, `__fixup_guest_exit()`, and `__kvm_unexpected_el2_exception()`.

## Control Flow

Before guest entry, KVM programs CPTR/CPACR, PMU user traps, HCRX, FGT/ICH-FGT registers, MPAM traps, and optional vSError ESR. Hyp exit fixup records ESR, adjusts HVC ELR when SError is pending, gives fast handlers a chance to resolve FP/SVE, VGIC, timer counter, CPU erratum, or memory-fault cases, and otherwise returns to host. FP traps lazily disable traps, save protected-host FP if needed, restore guest FP/SVE, and re-enable the correct trap mask.

## State And Persistence Behavior

The header saves and restores host sysregs in `host_ctxt`, mutates live CPTR/CPACR/HCR/HCRX/FGT/MPAM/PMUSERENR/VSESR state, updates vCPU fault info, FP owner, SVE ZCR, PC/PSTATE, and vCPU flags.

## Dependencies And Integration Points

It integrates with VGIC v2/v3 CPU-interface emulation, timer offsets, nested virtualization, pKVM, PMU, SVE/FPSIMD assembly helpers, CPU errata, MPAM, HCRX/FGT features, and exception tables.

## Risks And Test Signals

Risks are wrong trap masks under VHE/nVHE/nested modes, lost host sysregs, unhandled CPU errata, stale SVE VL, incorrect vSError preservation, and returning to guest after incomplete fixup. Test signals include first FP/SVE access, nested trap layering, PMU user access, CNTxCT fast reads, VGIC CPUif traps, Cavium/Ampere errata, memory abort HPFAR population, and unexpected EL2 exception-table fixups.
