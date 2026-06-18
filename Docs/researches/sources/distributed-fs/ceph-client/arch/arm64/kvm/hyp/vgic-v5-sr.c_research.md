# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/vgic-v5-sr.c

## Purpose
This file adds hyp-side GICv5 CPU-interface save/restore helpers. It handles VMCR/APR, ICSR, and private interrupt state for architected and implementation-defined PPIs, including direct virtual interrupt state.

## Important APIs, Types, and Functions
- `__vgic_v5_save_apr()` saves `ICH_APR_EL2`.
- `__vgic_v5_restore_vmcr_apr()` disables v3 compatibility mode and restores VMCR/APR.
- `__vgic_v5_save_ppi_state()` saves PPI active/pending snapshots and priority registers.
- `__vgic_v5_restore_ppi_state()` restores DVI, active, enable, pending, and priority state.
- `__vgic_v5_save_state()` and `__vgic_v5_restore_state()` save/restore VMCR and ICSR-level state.

## Control Flow
Save reads PPI active and pending registers into per-host hyp data, copies priority registers into the vCPU interface state, handles a 64- or 128-private-IRQ layout, and disables DVI after the snapshot. Restore enables guest DVI bits, restores active and enable state, computes pending state for non-DVI PPIs from host-saved state, restores priority registers, and clears the high bank when the implementation exposes only 64 private IRQs.

## State and Persistence
Persistent state is split between `struct vgic_v5_cpu_if` fields and per-CPU `vgic_v5_ppi_state` host data. The code assumes `VGIC_V5_NR_PRIVATE_IRQS` is divisible by 64 and only supports 64 or 128 private IRQ storage shapes. Compatibility mode is controlled through `SYS_ICH_VCTLR_EL2`.

## Dependencies and Integration Points
It depends on GICv5 sysreg definitions from `linux/irqchip/arm-gic-v5.h`, hyp data accessors, bitmap helpers, and the broader VGIC world-switch sequence that calls these helpers around guest entry/exit. The VHE Makefile includes it with other hyp VGIC code.

## Risks and Edge Cases
The sensitive areas are bitmap bank alignment, clearing high-bank registers on 64-PPI systems, and preserving host pending state only for PPIs not delegated through DVI. Incorrect ordering can leak host PPI state into guests or lose virtual pending state.

## Test Signals
GICv5-capable test coverage should exercise 64- and 128-PPI configurations, DVI-enabled and non-DVI PPIs, priority migration, save/restore across vCPU preemption, and compatibility transitions between GICv3 and GICv5 CPU-interface modes.
