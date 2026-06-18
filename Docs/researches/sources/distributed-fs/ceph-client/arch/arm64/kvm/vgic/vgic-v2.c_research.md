# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-v2.c

## Purpose
`vgic-v2.c` implements the runtime interaction between KVM VGIC state and a GICv2-compatible hardware virtual CPU interface. It computes and folds list-register state, manages VMCR/APR save/restore, handles DIR deactivation, maps v2 resources, and probes/registers VGICv2 support.

## Important APIs, Types, And Functions
Runtime entry points include `vgic_v2_init_lrs()`, `vgic_v2_configure_hcr()`, `vgic_v2_fold_lr_state()`, `vgic_v2_deactivate()`, `vgic_v2_populate_lr()`, `vgic_v2_clear_lr()`, `vgic_v2_set_vmcr()`, `vgic_v2_get_vmcr()`, `vgic_v2_reset()`, `vgic_v2_map_resources()`, `vgic_v2_probe()`, `vgic_v2_save_state()`, `vgic_v2_restore_state()`, `vgic_v2_load()`, and `vgic_v2_put()`. `vgic_v2_compute_lr()` is the core private encoder for GICH_LR values.

## Control Flow
Before guest entry, VGIC core selects pending/active IRQs and calls `vgic_v2_populate_lr()` under the IRQ lock. The function encodes virtual INTID, group, active/pending bits, source CPU for SGIs, EOI/resampling hints, HW physical ID if applicable, and five-bit priority. It clears edge pending state once consumed and lowers mapped-level line state to detect later edges. On guest exit, `vgic_v2_save_state()` reads VMCR/HCR/LRs from GICH registers, then `vgic_v2_fold_lr_state()` folds each LR back into `struct vgic_irq`, preserving active state, pending edge state, SGI source bits, and resampling effects.

`vgic_v2_configure_hcr()` enables the virtual interface and requests maintenance interrupts for pending/active work outside LRs. `vgic_v2_deactivate()` handles guest DIR writes in EOImode 1; it either synthesizes a deactivated LR and folds it or falls back to common active-clear MMIO when the IRQ is still resident in an LR.

## State And Persistence
Per-VCPU persistent state includes `vgic_hcr`, `vgic_vmcr`, `vgic_lr[]`, `used_lrs`, and `vgic_apr`. Per-IRQ state folded through this file includes active, pending latch, active source, SGI source bitmap, line level, on-LR marker, and physical resampling state. `vgic_v2_reset()` zeros VMCR so hardware reset behavior supplies default binary points.

## Dependencies And Integration Points
It depends on GICH/GICV MMIO mappings in `kvm_vgic_global_state`, VGIC core ap_list scheduling, common MMIO active-clear fallback, physical IRQ resampling helpers, KVM MMU remapping for GICV, and KVM device registration through `kvm_register_vgic_device()`. GICv3 hosts can still emulate v2, so some v2 MMIO paths may delegate deactivation to v3 runtime code.

## Risks
LR folding must not lose edge pending state, SGI source identity, or hardware resampling transitions. GICv2 SGI active-source state is partially unobservable and can be lossy across migration. Resource mapping must reject overlapping distributor/CPU frames and handle unsafe GICV alignment by trapping. EOICOUNT replay depends on ap_list priority ordering and active interrupt accounting.

## Test Signals
Exercise v2 guest IRQ injection for edge/level/SGI/SPI/HW-mapped cases, LR fold/populate round trips, EOImode 0 and 1 deactivation, maintenance interrupt generation with IRQs outside LRs, save/restore of VMCR/APR/LRs, GICV trap fallback on unsafe firmware resources, and migration tests around SGI active-source behavior.
