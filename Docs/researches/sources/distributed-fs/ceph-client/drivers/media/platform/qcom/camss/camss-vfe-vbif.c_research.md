<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-vbif.c -->
# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-vbif.c

## Purpose
Provides a tiny helper layer for programming the VFE VBIF bus interface on CAMSS platforms that expose a separate VBIF register region.

## Important APIs, Types, And Functions
- `vfe_vbif_write_reg()` writes a value to a VBIF offset relative to `vfe->vbif_base`.
- `vfe_vbif_apply_settings()` programs fixed sort enable and select registers with hard-coded values.

## Control Flow
Callers first map `vfe->vbif_base` during VFE subdevice initialization when `has_vbif` is set in resources. A hardware-specific VFE path can then call `vfe_vbif_apply_settings()`, which writes `VBIF_FIXED_SORT_EN` and `VBIF_FIXED_SORT_SEL0` and returns success.

## State And Persistence
The only state change is MMIO register state in the VBIF block. There is no cached software state and no persistent storage.

## Dependencies And Integration Points
Depends on `struct vfe_device` from the VFE core and `writel_relaxed()` from Linux I/O APIs. Resource metadata in `camss.c` controls whether the VBIF region is mapped.

## Risks And Edge Cases
The settings are unconditional and hard-coded, so they assume the VBIF layout and desired sorting policy match all callers. There is no guard against a NULL or invalid `vbif_base`; correct use depends on resource setup. The helper returns `0` without readback or error detection.

## Test Signals
Boot/probe should map the named VBIF resource on platforms that set `has_vbif`. Runtime capture should show no bus ordering or memory write issues after applying settings; hardware debug or trace readback can verify the programmed registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/qcom/camss/camss-vfe-vbif.c -->
