# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/encoder-tpd12s015.c

## Purpose
`encoder-tpd12s015.c` models the TPD12S015 HDMI ESD protection and level-shifter chip as an OMAP DSS HDMI output. It forwards HDMI operations upstream and controls GPIOs for charge pump/HPD, level shifter output enable, and HPD detection.

## Important APIs, Types, And Functions
- `struct panel_drv_data` stores DSS output, upstream HDMI source, `ct_cp_hpd_gpio`, `ls_oe_gpio`, `hpd_gpio`, and timings.
- `tpd_hdmi_ops` implements HDMI connect/disconnect, enable/disable, timing operations, EDID read, detect, AVI infoframe, and HDMI mode forwarding.
- `tpd_read_edid()` gates EDID reads on HPD and temporarily enables the level shifter.

## Control Flow
Probe requires OF, finds the upstream source, acquires three indexed GPIOs, fills an HDMI output DSS device, and registers it. Connect forwards upstream HDMI connect, links downstream source pointers, asserts charge-pump/HPD GPIO, and waits 300 us for 5V. Disconnect clears charge-pump GPIO, unlinks pointers, and forwards disconnect. Enable sets timings and enables upstream HDMI. EDID read returns `-ENODEV` without HPD, otherwise asserts `ls_oe_gpio`, reads upstream EDID, and deasserts it.

## State And Persistence
Per-device state is runtime-only. GPIO values carry hardware state for HPD supply/level shifting.

## Dependencies And Integration Points
The file depends on GPIO descriptors, OF graph helpers, OMAP DSS HDMI output ops, and downstream HDMI connector chaining.

## Risks
`tpd_disconnect()` calls `gpiod_set_value_cansleep()` on `ct_cp_hpd_gpio` without a null guard even though the GPIO was requested optional. Connect lacks an already-connected guard unlike other encoders. EDID depends on correct HPD polarity and upstream read behavior. Error paths share labels and release the upstream source for GPIO acquisition failures.

## Test Signals
Test HPD-driven detect, EDID read only when HPD is asserted, level-shifter GPIO toggling around EDID, charge-pump GPIO assertion after connect, and HDMI mode/infoframe forwarding.
