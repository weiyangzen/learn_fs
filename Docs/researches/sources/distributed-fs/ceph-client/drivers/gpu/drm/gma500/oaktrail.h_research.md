# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail.h

## Purpose
This header collects Oaktrail/Moorestown-specific panel data structures and HDMI function declarations. It defines the GCT panel timing/descriptors consumed by MID BIOS parsing and the HDMI device state saved across modeset and suspend/resume.

## Important APIs, Types, and Functions
Important data types include `struct oaktrail_timing_info`, `struct gct_r10_timing_info`, `struct oaktrail_panel_descriptor_v1`, `struct oaktrail_panel_descriptor_v2`, `union oaktrail_panel_rx`, `struct gct_r0`, `struct gct_r1`, `struct gct_r10`, `struct oaktrail_gct_data`, and `struct oaktrail_hdmi_dev`. It also declares Oaktrail HDMI setup/teardown/save/restore/init, HDMI I2C init/exit, and CRTC HDMI mode-set/DPMS helpers.

## Control Flow
There is no executable flow. The structs shape how `mid_bios.c` copies firmware GCT data and how `oaktrail_device.c`, `oaktrail_lvds.c`, `oaktrail_hdmi.c`, and `oaktrail_hdmi_i2c.c` share Oaktrail-specific state.

## State and Persistence Behavior
`oaktrail_gct_data` is embedded in `drm_psb_private` and persists selected panel timing/descriptor data after firmware tables are unmapped. `oaktrail_hdmi_dev` is allocated when the HDMI PCI function is found and stores MMIO mapping, DPMS mode, HDMI I2C state, and register snapshots.

## Dependencies and Integration Points
The header integrates MID firmware parsing, LVDS fixed-mode generation, Oaktrail chip operations, and separate HDMI PCI controller handling. It depends on DRM mode types, PCI device types, and register definitions indirectly through implementation files.

## Risks
The packed bitfield layouts are firmware ABI contracts; compiler layout and endian assumptions must match the platform. GCT revision variants use similar but not identical timing layouts, so copying fields incorrectly can produce bad panel modes. HDMI state is shared between display and I2C files through an opaque `hdmi_i2c_dev` pointer.

## Test Signals
Signals include correct compile-time struct packing, GCT-derived LVDS modes matching panel native resolution, HDMI setup resolving all declarations, and suspend/resume preserving the register fields listed in `oaktrail_hdmi_dev`.
