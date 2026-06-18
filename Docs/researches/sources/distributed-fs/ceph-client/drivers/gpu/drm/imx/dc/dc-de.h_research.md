<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-de.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-de.h

Purpose: Declares the i.MX8 DC display-engine, frame generator, and timing-controller data structures and APIs.

Important APIs/types/functions: Defines `DC_DISPLAYS`, framegen limits, `struct dc_fg`, `struct dc_tc`, and `struct dc_de`. Declares framegen functions for mode setup, enable/disable, shadow token generation, timestamp reads, FIFO/sync checks, clock handling, and initialization, plus `dc_tc_init()`.

Control flow: Header only.

State and persistence behavior: Structures hold device/regmap/clock pointers and display-engine IRQ numbers used by CRTC and runtime PM paths.

Dependencies: Linux clk/device/regmap and DRM modes.

Integration points: Shared by display-engine, framegen, timing-controller, CRTC, KMS, and driver aggregate structs.

Risks: API changes ripple through most DC display-engine files. Constants such as `DC_FRAMEGEN_MAX_FRAME_INDEX` are exposed to KMS vblank configuration.

Test signals: Build coverage and modeset/vblank operation through the CRTC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dc/dc-de.h -->
