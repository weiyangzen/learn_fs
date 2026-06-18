# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/addr-map.h

Purpose: Address-map helper definitions for MMP/PXA APB/AXI static mappings.

Important APIs/types/functions: Defines `APB_PHYS_BASE`, `AXI_PHYS_BASE`, sizes, virtual bases, `APB_VIRT_BASE`, `AXI_VIRT_BASE`, `APB_PHYS_BASE`, `AXI_PHYS_BASE`, `APBC_REG()`, `APMU_REG()`, `MPMU_REG()`, and `CIU_REG()` helpers.

Control flow: No executable flow; consumers expand macros into MMIO pointers.

State and persistence: No mutable state. Encodes static virtual mapping offsets and physical register windows.

Dependencies and integration points: Used by MMP common/time/platform code for early register access before full drivers bind.

Risks: Static mapping constants must match `iotable_init` descriptors. Wrong macros route clock/power writes to invalid addresses.

Test signals: Build and boot MMP/PXA boards, checking early timer/clock/interrupt setup.
