## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_sideband.c

### Purpose

`vlv_sideband.c` implements DPIO sideband read/write routing for VLV/CHV display PHY access. It maps logical `enum dpio_phy` values to IOSF sideband units and wraps raw sideband access with a warning for suspicious all-ones reads.

### Important APIs, types, and functions

The public functions are `vlv_dpio_read(struct drm_device *drm, enum dpio_phy phy, int reg)` and `vlv_dpio_write(struct drm_device *drm, enum dpio_phy phy, int reg, u32 val)`. The private helper `vlv_dpio_phy_to_unit()` selects `VLV_IOSF_SB_DPIO` or `VLV_IOSF_SB_DPIO_2` based on platform and PHY.

### Control flow

For Cherryview, `DPIO_PHY0` maps to `VLV_IOSF_SB_DPIO_2` and the other PHY maps to `VLV_IOSF_SB_DPIO`; on Valleyview all DPIO PHY accesses route to `VLV_IOSF_SB_DPIO`. Reads call `vlv_iosf_sb_read()`, warn if the result is `0xffffffff`, and return the value. Writes call `vlv_iosf_sb_write()`.

### State and persistence behavior

The file owns no persistent state. It mutates hardware sideband registers selected by callers, and those values persist in the DPIO PHY until reprogramming or reset.

### Dependencies

It depends on `intel_display_core.h`, `intel_display_types.h`, `intel_dpio_phy.h`, and `vlv_sideband.h`. The underlying IOSF sideband implementation supplies locking and actual access.

### Integration points

The functions are used by DPIO PHY programming code and any caller using VLV/CHV DPIO register definitions. Access should be bracketed with `vlv_dpio_get()`/`vlv_dpio_put()` from the header to acquire the relevant sideband units.

### Risks

The all-ones read warning is heuristic; the comment notes some registers may validly return all ones. A wrong PHY-to-unit mapping can write the wrong PHY on CHV. Callers must avoid unbracketed sideband access if the IOSF layer requires mutual exclusion or power/forcewake handling.

### Test signals

PHY register readback on VLV/CHV, no unexpected all-ones warnings during link training, and successful HDMI/DP DPIO programming on both Cherryview PHYs.
