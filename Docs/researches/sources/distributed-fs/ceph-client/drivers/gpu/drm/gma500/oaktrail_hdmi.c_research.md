# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/oaktrail_hdmi.c

## Purpose
This file implements Oaktrail HDMI support for the separate HDMI PCI controller. It handles HDMI device discovery/MMIO mapping, TMDS connector/encoder registration, HDMI PLL and pipe-B mode programming, audio enable/disable, hotplug detection, EDID mode reporting, DPMS, and HDMI register save/restore.

## Important APIs, Types, and Functions
Exported functions are `oaktrail_hdmi_setup()`, `oaktrail_hdmi_teardown()`, `oaktrail_hdmi_init()`, `oaktrail_crtc_hdmi_mode_set()`, `oaktrail_crtc_hdmi_dpms()`, `oaktrail_hdmi_save()`, and `oaktrail_hdmi_restore()`. Internal helpers include `oaktrail_hdmi_find_dpll()`, `oaktrail_hdmi_reset()`, `scu_busy_loop()`, `oaktrail_hdmi_detect()`, `oaktrail_hdmi_get_modes()`, and audio toggles.

## Control Flow
Setup locates PCI device 8086:080d, enables it, maps BAR0, initializes the HDMI I2C controller, stores `dev_priv->hdmi_priv`, and disables audio. Connector init creates a DVID connector and TMDS encoder. HDMI CRTC mode set powers the device, disables VGA/DPLL, resets the controller through SCU IPC MMIO, computes DPLL divisors from a 25 MHz ref clock, programs both core and PCH-style pipe-B timings, calls base programming, enables pipe/plane, and waits for vblank. DPMS toggles DPLL, pipe B, PCH pipe B, and plane B.

## State and Persistence Behavior
Persistent state is `struct oaktrail_hdmi_dev`: PCI device, MMIO mapping, I2C device, and saved DPLL/pipe/plane/PCH registers. `oaktrail_hdmi_dpms()` also keeps a static last DPMS mode. Save/restore copies pipe B timing, plane, cursor, palette, and HDMI DPLL/PCH state into driver-private structures.

## Dependencies and Integration Points
The file integrates with Oaktrail chip setup, Oaktrail CRTC helpers, HDMI I2C init/exit, DRM connector helpers, DRM EDID helpers, and GMA500 power/register macros. It uses hardcoded SCU IPC and HDMI MMIO offsets specific to this platform.

## Risks
EDID support is incomplete and currently uses a hardcoded raw EDID even if adapter 3 exists. SCU reset uses fixed physical addresses and magic values. HDMI mode set forces pipe B and contains many hardware constants. `oaktrail_hdmi_destroy()` is empty, so connector cleanup relies on broader DRM teardown. DPMS register access lacks an explicit power wrapper in the CRTC DPMS helper.

## Test Signals
Signals include detecting the HDMI PCI function, successful BAR mapping and I2C IRQ registration, hotplug status changing with `HDMI_HSR`, valid modes from the fallback EDID, stable HDMI output at 20-165 MHz pixel clocks, audio enable during mode set, and correct HDMI register restoration after suspend/resume.
