# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vgic-v3-sr.c

## Purpose
This file implements hyp-side save/restore and trap emulation for the GICv3 virtual CPU interface. It manages list registers, active priority registers, VMCR/HCR state, SRE/v2 compatibility mode, GIC configuration probing, and emulation of trapped ICC_* system registers, including nested-virtualization forwarding rules.

## Important APIs, Types, and Functions
- `__gic_v3_get_lr()` and `__gic_v3_set_lr()` read/write the 16 possible `ICH_LR<n>_EL2` registers.
- `__vgic_v3_save_state()`, `__vgic_v3_restore_state()`, `__vgic_v3_activate_traps()`, and `__vgic_v3_deactivate_traps()` are the world-switch core.
- `__vgic_v3_save_aprs()`, `__vgic_v3_restore_vmcr_aprs()`, and APR helpers preserve priority state.
- `__vgic_v3_init_lrs()` and `__vgic_v3_get_gic_config()` initialize/probe CPU-interface capability.
- `__vgic_v3_perform_cpuif_access()` dispatches trapped ICC_* sysreg accesses to local emulation helpers.
- Trap emulation covers IAR, EOIR, DIR, IGRPEN, BPR, APxR, HPPIR, PMR, RPR, and CTLR views.

## Control Flow
Save state first synchronizes memory-mapped and sysreg GIC views when needed, snapshots non-empty LRs, clears hardware LRs, saves VMCR, merges EOIcount from HCR when LRENPIE is active, disables ICH_HCR, and reads MISR to force nested effects. Restore writes HCR with trap bits, restores LRs, and synchronizes for non-SRE guests.

Trap activation programs `ICC_SRE_EL1`/`ICC_SRE_EL2` according to whether the guest uses the system-register interface, whether v2 compatibility is present, and whether global CPU-interface trapping or ITS VPE state requires ICH_HCR enablement. Deactivation reverses this and clears HCR when traps were enabled only for emulation.

The CPU-interface access handler rejects non-VGICv3 models, decodes AArch32 or AArch64 sysreg ISS, checks nested forwarding through HFGRTR/HFGWTR/HCR trap bits, chooses a register-specific handler, reads VMCR, invokes the handler, skips the instruction, and returns whether EL2 handled it. IAR emulation selects the highest-priority pending LR, checks group enable and PMR/HAP priority, transitions LR state to active, sets APR priority, and returns the virtual INTID. EOIR/DIR drop active priority and deactivate LRs or bump EOIcount when deactivation cannot be represented locally.

## State and Persistence
State is persisted in `struct vgic_v3_cpu_if`: `vgic_lr[]`, `used_lrs`, `vgic_vmcr`, `vgic_hcr`, `vgic_sre`, APR arrays, and ITS VPE state. Hardware state lives in ICH/ICC sysregs and is transferred across guest entry/exit. Priority and active state are encoded both in LRs and APR registers; misordering can cause lost interrupts or wrong priority masking.

## Dependencies and Integration Points
The file depends on GICv3 sysreg accessors, `vgic_ich_hcr_trap_bits()`, `static_branch` feature keys for v2 compatibility and CPU-interface trapping, KVM sysreg/fault helpers, nested-virtualization sysregs, and VGIC data structures from `../../vgic/vgic.h`. It is compiled into VHE hyp via the VHE Makefile and is also shared by other hyp build variants.

## Risks and Edge Cases
Risks include failing to clear stale LRs, violating required barriers between memory-mapped and sysreg GIC views, wrong APR count derived from VTR priority bits, incorrect group/BPR priority comparisons, and mishandling nested forwarding. GICv2 compatibility is especially sensitive because SRE programming changes whether Group0 interrupts appear as FIQs. DIR/EOIR behavior also must distinguish LPIs, EOImode, and hardware-backed physical interrupts.

## Test Signals
Use KVM VGIC selftests and guest stress tests covering GICv3, GICv2-on-v3 compatibility, nested VGIC traps, LPI and non-LPI interrupts, EOImode 0/1, priority masking, big LR counts, and live migration state save/restore. Useful symptoms include stuck interrupts, spurious IAR reads, EOIcount overflow exits, and mismatched interrupt priority after nested transitions.
