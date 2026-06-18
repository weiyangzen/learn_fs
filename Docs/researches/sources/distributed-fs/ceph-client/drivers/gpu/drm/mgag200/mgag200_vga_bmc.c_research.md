# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_vga_bmc.c

## Purpose
Initializes a VGA connector/encoder path for server G200 variants where a BMC may be present even without a monitor or EDID.

## Important APIs, types, and functions
- Encoder atomic helpers call `mgag200_bmc_stop_scanout()` and `mgag200_bmc_start_scanout()` when `sync_bmc` is set.
- Encoder atomic check stores `set_vidrst` in `mgag200_crtc_state`.
- Connector get_modes falls back to no-EDID modes and prefers 1024x768.
- Connector detect always returns connected while updating `epoch_counter` when EDID presence changes.
- `mgag200_vga_bmc_output_init()` creates the encoder, DDC bus, connector, polling, and attachment.

## Control flow
During atomic check, the encoder records whether CRTC mode programming should set video reset bits. During disable/enable, BMC scanout is stopped/started only for variants whose device info requests synchronization. Mode probing first uses DDC; if no EDID modes exist, it adds bounded no-EDID modes up to the chip max and marks 1024x768 preferred.

## State and persistence
Connector and encoder live in `mdev->output.vga`. `connector->epoch_counter` is incremented on EDID presence changes to refresh properties. BMC sync state persists in DAC GPIO/spare registers via `mgag200_bmc.c` during modesets.

## Dependencies and integration points
Used by most server G200 variant pipeline initializers. Integrates with mgag200 DDC, BMC handshake helpers, and shared mode register programming through `set_vidrst`.

## Risks
Always reporting connected is correct for BMC console availability but can surprise userspace expecting physical monitor status. Fallback modes depend on max_hdisplay/max_vdisplay being conservative. BMC synchronization adds hardware-protocol timing risk.

## Test signals
No-monitor boot should still expose a connected VGA connector with 1024x768 preferred. EDID attach/detach should update properties. BMC remote console should survive modesets on `sync_bmc` variants.
