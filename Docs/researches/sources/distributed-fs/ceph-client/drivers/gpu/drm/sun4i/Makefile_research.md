# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/Makefile

## Purpose
The sun4i Makefile groups source objects into modules for the Allwinner display-engine DRM stack and maps each group to the corresponding Kconfig symbol.

## Important Build Rules
- `sun4i-drm-y`: master driver and framebuffer/mode-config setup.
- `sun4i-tcon-y`: CRTC, TCON pixel clock, LVDS, TCON, and RGB encoder support.
- `sun4i-backend-y` and `sun4i-frontend-y`: original Display Engine backend/layer and frontend scaler/CSC modules.
- `sun4i-drm-hdmi-y`: original HDMI DDC, encoder, I2C, and TMDS clock support.
- `sun8i-drm-hdmi-y`, `sun8i-mixer-y`, and `sun8i_tcon_top.o`: later-generation HDMI/mixer/routing objects.

## Control Flow, State, and Persistence
The Makefile has no runtime behavior. It defines module composition and makes the frontend object conditional on `CONFIG_DRM_SUN4I_BACKEND` so frontend code is only built when the original backend pipeline can use it.

## Dependencies and Integration Points
It integrates directly with `drivers/gpu/drm/sun4i/Kconfig` and with cross-file symbols among the display-engine components, including CRTC creation, backend engine ops, frontend exported helpers, HDMI clocks, and TCON routing.

## Risks and Test Signals
Risks include unresolved symbols when optional modules are split differently and missing objects when Kconfig defaults change. Build tests should compile built-in and modular combinations for core, backend/frontend, HDMI, DSI, mixer, and TCON TOP.
