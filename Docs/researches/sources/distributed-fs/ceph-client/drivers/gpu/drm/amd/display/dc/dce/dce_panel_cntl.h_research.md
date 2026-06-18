# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_panel_cntl.h

## Purpose
This header defines the DCE panel-control register schema and concrete `struct dce_panel_cntl`. It maps LVTMA power sequencing, PWM control, PWM period, PWM group lock, PWM reference divider, and BIOS scratch registers used by the panel control implementation.

## Important APIs, Types, and Macros
`DCE_PANEL_CNTL_REG_LIST()` maps DCE-style LVTMA and global PWM registers. `DCN_PANEL_CNTL_REG_LIST()` provides a DCN address form using base-indexed LVTMA and NBIO BIOS scratch access. `DCE_PANEL_CNTL_MASK_SH_LIST()` and `DCE_PANEL_CNTL_REG_FIELD_LIST()` define fields for BLON/DIGON overrides, target state, PWM reference divider, active duty, fractional enable, PWM enable, and group lock/update status. The header declares `struct dce_panel_cntl_registers`, `struct dce_panel_cntl_shift`, `struct dce_panel_cntl_mask`, `struct dce_panel_cntl`, and `dce_panel_cntl_construct()`.

## Control Flow and State
No behavior is implemented here. The declared object embeds `struct panel_cntl` and stores pointers to register, shift, and mask metadata consumed by `dce_panel_cntl.c`.

## Dependencies and Integration Points
It depends on `panel_cntl.h` and generated register macros such as `SR`, `NBIO_SR`, and MMIO symbols. It is used by DCE/DCN resource construction and panel control implementation code.

## Risks and Test Signals
The DCE and DCN register-list alternatives must match the caller's register namespace. A wrong BIOS scratch accessor or LVTMA base calculation can break backlight ownership or power state reads. Compile coverage for DCE and DCN users plus embedded panel backlight tests are the key signals.
