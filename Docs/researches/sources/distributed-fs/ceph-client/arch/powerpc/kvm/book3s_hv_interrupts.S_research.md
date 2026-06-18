# sources/distributed-fs/ceph-client/arch/powerpc/kvm/book3s_hv_interrupts.S

## Purpose

`book3s_hv_interrupts.S` contains the module-memory assembly entry point for Book3S HV virtual-core execution and a local helper for saving host PMU state. It bridges C scheduling code and the lower-level HV partition-switch trampoline by saving host nonvolatile state, preparing hypervisor decrementer/LPCR state, calling `kvmppc_hv_entry_trampoline`, and restoring the host frame after a guest exit that must return to virtual mode.

## Important APIs, Types, And Labels

`__kvmppc_vcore_entry` is the global entry label called from `kvmppc_run_core()` on pre-POWER9 paths. It uses PACA (`r13`) `HSTATE_*` offsets, vcore/KVM offsets, switch-frame offsets, and feature-fixup sections. `kvmhv_save_host_pmu` is a local function that freezes counters and saves host PMU registers into PACA host-state fields when the host has PMU state in use.

The assembly uses `SAVE_NVGPRS`, `REST_NVGPRS`, `PPC_MSGSND`-related register conventions indirectly through included headers, `SPRN_DSCR`, `SPRN_DABR`, `SPRN_LPCR`, `SPRN_DEC`, `SPRN_HDEC`, `SPRN_MMCR*`, `SPRN_MMCRA`, `SPRN_SIAR`, `SPRN_SDAR`, `SPRN_SIER`, and PMC SPRs.

## Control Flow

`__kvmppc_vcore_entry` saves LR into the caller stack frame, creates a switch frame, saves nonvolatile GPRs and CR, stores host DSCR in PACA, conditionally saves DABR on CPUs before ISA 2.07S, and calls `kvmhv_save_host_pmu()`. It then loads the current vcore and KVM, reads the host LPCR, sets LPCR[HDICE], copies the current DEC value into HDEC, records the resulting decrementer expiry in PACA, and branches to `kvmppc_hv_entry_trampoline`.

When the trampoline returns in virtual mode after a guest exit that cannot be handled in real mode, the code assumes hard interrupts remain disabled and that registers carry the trap number and handler ID conventions documented in comments. It restores nonvolatile GPRs and CR, tears down the switch frame, restores LR, and returns to C.

`kvmhv_save_host_pmu` freezes counters first. On POWER8-class CPUs it applies the MMCR2 freeze-all workaround, then freezes MMCR0 and clears MMCRA to stop SDAR updates. If `PACA_PMCINUSE` is clear, it returns after freezing. Otherwise it saves MMCR0/MMCR1/MMCRA, SIAR, SDAR, optional MMCR2/SIER, and PMC1 through PMC6 into PACA host-state slots.

## State And Persistence Behavior

The file saves transient host CPU state into the current PACA so guest entry can use PMU, decrementer, LPCR, DABR, and DSCR resources. It does not persist data beyond the guest-entry/exit interval. The saved HDEC expiry and PMU register state are later consumed by HV return/restoration paths outside this file.

## Dependencies And Integration Points

It is tightly coupled to `book3s_hv.c`'s call into `__kvmppc_vcore_entry`, the external `kvmppc_hv_entry_trampoline`, PACA layout generated in `asm-offsets.h`, `struct kvmppc_vcore` and KVM offset definitions, CPU feature fixup sections, PMU ownership tracking, and the real-mode HV handlers that return to this virtual-mode epilogue.

## Risks

Offset drift between C structures and assembly constants can corrupt host or guest state. PMU save ordering is delicate: counters must be frozen before reading event registers, and POWER8 errata require MMCR2 handling. LPCR[HDICE] must be set before writing HDEC on affected hardware. The entry/exit register convention must match the trampoline and C post-processing paths. Because the code runs with hard interrupts disabled, any missed restore can destabilize the host.

## Test Signals

Signals include pre-POWER9 KVM-HV guests entering and exiting reliably through `__kvmppc_vcore_entry`, host nonvolatile registers and CR preserved across guest runs, decrementer exits firing through HDEC, host PMU counts preserved when `PACA_PMCINUSE` is set, correct behavior on POWER8 errata-sensitive PMU paths, and no crashes from PACA offset mismatches under guest exit stress.
