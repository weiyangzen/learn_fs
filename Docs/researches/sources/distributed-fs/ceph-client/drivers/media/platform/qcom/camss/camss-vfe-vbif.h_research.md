<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-vbif.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-vbif.h

## Purpose
Declares the VBIF helper interface used by VFE hardware code that needs to program a separate VFE bus interface block.

## Important APIs, Types, And Functions
- Declares `vfe_vbif_write_reg(struct vfe_device *vfe, u32 reg, u32 val)`.
- Declares `vfe_vbif_apply_settings(struct vfe_device *vfe)`.
- Includes `camss-vfe.h` for the `struct vfe_device` definition.

## Control Flow
No runtime logic is implemented here. The header exposes the write and apply helpers to hardware-specific VFE source files.

## State And Persistence
No owned state. Functions declared here operate on the `vbif_base` MMIO mapping stored in `struct vfe_device`.

## Dependencies And Integration Points
Integrated with VFE initialization in `camss-vfe.c`, which maps the VBIF resource when the SoC resource table advertises `has_vbif`. Hardware-specific VFE modules include this header when they apply VBIF policy.

## Risks And Edge Cases
Because the header exposes raw register writes, callers must provide valid offsets and ensure the hardware block is powered and mapped. There is no type-level separation between VBIF register offsets and other VFE offsets.

## Test Signals
Compile coverage ensures callers include the correct declarations. Runtime test signals mirror `camss-vfe-vbif.c`: successful probe with VBIF resources and stable streaming after settings are applied.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-vbif.h -->
