<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_utility.c -->
# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_utility.c

Purpose: Miscellaneous utility implementation for device support/connection reporting, LCD expansion support reporting, and gamma table access used by viafb ioctls.

Important APIs/types/functions: `viafb_get_device_support_state()` reports CRT plus DVI when VT1632 TMDS is known and LCD when VT1631 LVDS is known. `viafb_get_device_connect_state()` reports CRT, DVI when `viafb_dvi_sense()` succeeds, and LCD when `viafb_lcd_get_mobile_state()` reports a mobile panel. `viafb_lcd_get_support_expand_state()` maps panel IDs to native sizes and checks whether the current mode is smaller. Gamma APIs are `viafb_set_gamma_table()`, `viafb_get_gamma_table()`, and `viafb_get_gamma_support_state()`.

Control flow and state: Gamma set enables the chip-specific gamma bit, saves SR1A, selects IGA1 gamma, writes 256 RGB LUT entries through DAC ports, optionally selects IGA2 and writes the same table when multiple devices are active and the chip supports it, then restores SR1A. Gamma get reads 256 entries from IGA1. Support/connect queries synthesize bitmasks from global chip/output state and hardware sense helpers.

Dependencies and integration points: Called by `viafb_ioctl()` in `viafbdev.c`. Depends on global `viaparinfo`, `viafb_DeviceStatus`, DVI sense, LCD mobile BIOS probe, DAC I/O ports, and register helpers. Risks include direct port I/O with no locking, active-device counting over a global bitmask, no gamma support for some later chips listed elsewhere, 8-bpp no-op behavior, and LCD support tied narrowly to VT1631. Test signals are ioctl gamma set/get round trips, SAMM gamma on both IGAs, DVI sense/connect state, mobile BIOS detection, and panel expansion query for every panel ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/video/fbdev/via/via_utility.c -->
