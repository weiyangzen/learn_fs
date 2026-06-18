
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/sor507d.c

## Purpose
Implements SOR output-resource control for NV507D-era display core channels. SORs drive LVDS, TMDS, DisplayPort, and related serial display links.

## Important APIs, types, and functions
- `sor507d_ctrl()` writes `SOR_SET_CONTROL(or)` with optional hsync/vsync polarity and pixel depth from the head atom.
- `sor507d_get_caps()` sets `outp->caps.dp_interlace = true`.
- `const struct nv50_outp_func sor507d` exports the backend callbacks.

## Control flow
The output manager passes prebuilt owner/protocol bits in `ctrl`. This implementation augments those bits when a target head atom is available, reserves two push words, and emits the SOR control method. Capability initialization is static.

## State and persistence
No private state exists. SOR ownership, protocol, polarity, and depth persist in the display core until a later modeset rewrites them.

## Dependencies and integration points
Depends on `core.h`, `nvif/push507c.h`, `cl507d.h`, and `cl837d.h`. It integrates with NV50 core display resource assignment and the encoder capability model.

## Risks
Incorrect control bit composition can route an output to the wrong head or program an invalid protocol/depth combination. The static interlace capability should remain aligned with SOR class behavior.

## Test signals
Useful tests are SOR-backed HDMI/DVI/DP modesets, polarity-sensitive modes, bpc/depth changes, and interlaced DP mode validation.
