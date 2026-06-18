# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/interrupt.c

## Purpose
`interrupt.c` implements virtual interrupt register semantics for Intel GVT-g. It maps guest-visible events to virtual ISR/IIR/IMR/IER groups, propagates downstream group bits to upstream master bits, and injects MSI notifications through VFIO/KVM eventfd.

## Important APIs, Types, And Functions
Public functions are `intel_gvt_init_irq`, `intel_vgpu_trigger_virtual_event`, `intel_vgpu_reg_imr_handler`, `intel_vgpu_reg_master_irq_handler`, `intel_vgpu_reg_ier_handler`, and `intel_vgpu_reg_iir_handler`. Private structures `intel_gvt_irq_info` and `intel_gvt_irq_map` describe register groups and hierarchy. Gen8+ behavior is encoded by `gen8_irq_map`, `gen8_init_irq`, `gen8_check_pending_irq`, and `gen8_irq_ops`.

## Control Flow
Initialization installs Gen8 ops, initializes default virtual event handlers, fills event-to-bit/group mappings, and marks upstream/downstream relationships. Guest writes to IMR/IER/IIR/master registers update virtual registers and call `check_pending_irq`. Event injection sets the IIR bit if unmasked, updates upstream state, checks `GEN8_MASTER_IRQ_CONTROL`, and signals `vgpu->msi_trigger` when MSI is enabled and the vGPU is attached.

## State And Persistence
Per-GVT state is `gvt->irq`: ops, event metadata, group table, and IRQ map. Per-vGPU state lives in virtual MMIO registers, `irq_warn_once`, and MSI eventfd state. IIR is write-one-to-clear; IMR/IER control masking/enabling; master bits are derived from downstream `IIR & IER`.

## Dependencies And Integration Points
The file depends on i915 interrupt/display register definitions, event enums from `interrupt.h`, MMIO handler installation from `handlers.c`, and eventfd state managed by KVMGT. Display, AUX, vblank, flip, and workload code trigger events through `intel_vgpu_trigger_virtual_event`.

## Risks
Incorrect bit maps cause stuck, missing, or excess guest interrupts. The single-vector MSI assumption and attached-state guard are intentional but sensitive to VM teardown/reuse sequencing. Register handlers assume validated 32-bit MMIO paths.

## Test Signals
MSI should arrive only after guest MSI/master enablement; IIR writes should clear bits; masks should block propagation; downstream groups should set master bits; display and workload events should reach the guest; and stale MSI eventfds should not fire after close.
