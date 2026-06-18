# sources/distributed-fs/ceph-client/drivers/iommu/irq_remapping.h

## Purpose
`irq_remapping.h` is the private IOMMU-layer interface shared by x86 interrupt-remapping backends and the common orchestration code. It keeps backend hooks internal to the IOMMU implementation rather than exposing them as public kernel API.

## Important APIs, Types, and Functions
When `CONFIG_IRQ_REMAP` is enabled, the header declares global policy/status variables and `struct irq_remap_ops`. The ops structure contains a capability bitmask and callbacks for `prepare`, `enable`, `disable`, `reenable`, and `enable_faulting`. It declares backend instances `intel_irq_remap_ops`, `amd_iommu_irq_ops`, and `hyperv_irq_remap_ops`.

When `CONFIG_IRQ_REMAP` is disabled, it supplies constant macro fallbacks for `irq_remapping_enabled`, `irq_remap_broken`, and `disable_irq_post`, allowing code to compile away remapping checks.

## Control Flow and State
There is no executable control flow in the header. Its main state effect is compile-time: enabled builds share mutable global variables across backend/common files; disabled builds collapse state into constants.

## Dependencies and Integration Points
The header forward-declares IRQ/MSI-related types and is included by `irq_remapping.c` and backend implementations. It relies on Kconfig to select the real declarations. The capability bit positions are defined by the wider x86 IRQ remapping interfaces, while the ops objects are provided by Intel, AMD, and Hyper-V code.

## Risks and Test Signals
Risks are ABI-like drift between the common code and backend ops, misuse outside the intended IOMMU layer, and subtle differences between disabled-build constants and enabled-build globals. Test signals include building with `CONFIG_IRQ_REMAP=y/n`, each backend enabled independently, and verifying that capability and enable paths compile and link with all callback combinations.
