# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_vpp.h

## Purpose
Declares VPP mux values and initialization/scaler APIs for the Meson post-processing block.

## Important APIs, types, and functions
- Defines mux values for ENCL (`0x0`), ENCI (`0x5`), and ENCP (`0xA`).
- Declares `meson_vpp_setup_mux()`, interlace OSD1 vertical scaler enable/disable helpers, and `meson_vpp_init()`.

## Control flow
No runtime control flow exists in the header. It provides constants and function declarations used by VENC and display initialization paths.

## State and persistence
No state is stored. Mux constants represent persistent hardware routing values once written.

## Dependencies and integration points
Forward declares `struct drm_rect` and `struct meson_drm`. It is included by VPP implementation and by VENC code to switch output routing.

## Risks
Wrong mux constants route VIU output to the wrong encoder. The interlace scaler declarations create a link-time contract that must be satisfied elsewhere in the full driver.

## Test signals
Build/link coverage and runtime validation that HDMI, CVBS, and DSI modes select the expected encoder path.
