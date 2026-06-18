# sources/distributed-fs/ceph-client/drivers/gpu/drm/meson/meson_venc.h

## Purpose
Declares the Meson video encoder public interface shared by the Meson DRM encoder, CRTC, and mode-setting code.

## Important APIs, types, and functions
- Defines VENC mode tags: none, CVBS PAL, CVBS NTSC, HDMI, and MIPI DSI.
- Defines `struct meson_cvbs_enci_mode`, the PAL/NTSC ENCI timing and analog parameter structure consumed by CVBS setup.
- Declares external PAL/NTSC timing tables.
- Declares HDMI validation and setup APIs, ENCL gamma loading, CVBS setup and field readout, VSync control, and VENC initialization.

## Control flow
The header has no runtime control flow. It exposes a narrow API that lets output-specific encoder files request mode programming while keeping HDMI timing tables and register programming internals private to `meson_venc.c`.

## State and persistence
No state is stored here. The declared functions mutate `struct meson_drm` VENC state and VPU/HHI hardware registers.

## Dependencies and integration points
Forward references `struct drm_display_mode` and relies on `struct meson_drm` being visible to includers. It is an integration point for Meson HDMI, CVBS, DSI, and CRTC/IRQ code.

## Risks
The `struct meson_cvbs_enci_mode` layout is a direct contract with the implementation's register writes. Adding fields or reordering without updating all tables would silently corrupt CVBS programming.

## Test signals
Build coverage catches signature drift. Runtime coverage comes from callers successfully linking to HDMI/CVBS/DSI mode setup and VSync control.
