# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic.h

Purpose: provides the private VGIC interface shared by KVM ARM64 VGIC implementation files. It defines register encodings, ITS table layouts, helper predicates, VMCR/AP-list structures, v2/v3/v4/v5/nested prototypes, and direct interrupt capability helpers.

Important APIs/types/functions: affinity and userspace CPU-reg macros, `kvm_get_guest_vtr_el2`, ITS CTE/ITE/DTE/L1E masks, `vgic_vmcr`, `vgic_reg_attr`, ITS device/collection/ITE structures, `ap_list_summary`, `irq_is_pending`, `vgic_irq_get_lr_count`, `vgic_write_guest_lock`, `vgic_ich_hcr_trap_bits`, `vgic_try_get_irq_ref`, `vgic_v3_max_apr_idx`, redistributor region helpers, `kvm_has_gicv3`, `kvm_has_gicv5`, and `vgic_supports_direct_irqs`.

Control flow: implementation files call the inline helpers to normalize GIC state: VMCR is the backend-neutral CPU interface representation, pending state derives from edge latch or level line, SGI LR count reflects source bits plus active state, and VTR_EL2 is masked to expose only supported guest-visible fields. The prototype set routes operations to v2, v3, v4, v5, ITS, nested, and debug code.

State and persistence: this header owns no storage except type layout contracts. It encodes transient KVM VGIC state carried in `struct vgic_irq`, `struct vgic_dist`, `struct vgic_cpu`, and ITS lists. `vgic_write_guest_lock` toggles `table_write_in_progress` around guest-memory writes so ITS table persistence into guest RAM is observable to related code.

Dependencies/integration: depends on Linux IRQ/GIC common definitions, KVM MMU definitions, KVM device ABI encodings, ARM system register encodings, ITS userspace documentation contracts, and `kvm_vgic_global_state`.

Risks: ABI bit masks and shifts must stay synchronized with KVM device documentation and userspace save/restore tooling. Helper predicates such as `irq_is_pending` and `vgic_irq_get_lr_count` directly affect LR packing and interrupt visibility. Direct IRQ capability checks combine host and guest model state, so a wrong predicate can expose unsupported acceleration.

Test signals: compile coverage for all VGIC models/configs, userspace register attr encode/decode round trips, ITS table serialization/deserialization, pending-state helpers for edge/level SGI/LPI cases, redistributor overlap/size checks, and direct IRQ capability decisions on GICv3, GICv4.1, and GICv5 hosts.
