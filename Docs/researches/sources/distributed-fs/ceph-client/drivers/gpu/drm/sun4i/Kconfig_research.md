# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/Kconfig

## Purpose
This Kconfig file defines the Allwinner sun4i DRM display-engine feature set, including the master display-engine driver, HDMI, HDMI CEC, original backend/frontend pipeline, MIPI DSI, DesignWare HDMI for DE2, mixer, and TCON TOP support.

## Important Options
- `DRM_SUN4I`: core Allwinner display engine DRM driver, selecting DRM client selection, DMA GEM, KMS helper, panel support, regmap MMIO, and videomode helpers.
- `DRM_SUN4I_HDMI` and `DRM_SUN4I_HDMI_CEC`: original HDMI controller and optional CEC support.
- `DRM_SUN4I_BACKEND`: original display backend; when enabled the Makefile also builds the frontend helper module for compatible pipelines.
- `DRM_SUN6I_DSI`, `DRM_SUN8I_DW_HDMI`, `DRM_SUN8I_MIXER`, and `DRM_SUN8I_TCON_TOP`: later display blocks and routing support.

## Control Flow, State, and Persistence
There is no runtime state, but the selected options determine which platform drivers and component drivers participate in display-engine binding. Defaults tie many options to `DRM_SUN4I` so typical SoC builds get a broad display stack unless disabled.

## Dependencies and Integration Points
The file gates the objects built by the sun4i Makefile and selects external subsystems such as CEC, reset controller, MIPI DSI, DW HDMI, display helpers, and the Allwinner MIPI D-PHY.

## Risks and Test Signals
Risk is in Kconfig dependency drift and unexpected module combinations, especially `ifdef CONFIG_DRM_SUN4I_BACKEND` behavior for frontend objects. Build tests should cover ARM and `COMPILE_TEST`, backend disabled/enabled, HDMI with and without CEC, DSI, DE2 mixer/HDMI, and TCON TOP.
