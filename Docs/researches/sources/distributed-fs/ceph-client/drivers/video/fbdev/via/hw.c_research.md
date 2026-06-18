# sources/distributed-fs/ceph-client/drivers/video/fbdev/via/hw.c

## Purpose
`hw.c` is the central VIA framebuffer hardware programming file. It manages chip initialization, output routing, display device state, palette setup, FIFO/fetch timing, PLL clock selection, CRTC timing, full modeset sequencing, and several user-facing output-device parse/format helpers.

## Important APIs, Types, And Functions
Externally used functions include `viafb_lock_crt()`, `viafb_unlock_crt()`, `viafb_set_iga_path()`, `via_set_source()`, `via_set_state()`, `via_set_sync_polarity()`, `via_parse_odev()`, `via_odev_to_seq()`, `viafb_load_reg()`, `viafb_write_regx()`, `viafb_load_fetch_count_reg()`, `viafb_load_FIFO_reg()`, `viafb_set_vclock()`, `var_to_timing()`, `viafb_fill_crtc_timing()`, `viafb_init_chip_info()`, `viafb_update_device_setting()`, `viafb_init_dac()`, `viafb_setmode()`, `viafb_get_refresh()`, `viafb_set_dpa_gfx()`, and `viafb_fill_var_timing_info()`. Static tables define PLL limits, common VGA registers, FIFO register bitfields, palette LUT values, and output-device name mappings.

## Control Flow
Chip initialization sets clock operations, identifies graphics revision and 2D engine, detects TMDS/LVDS, initializes display sizes/interfaces, assigns IGA paths, and copies LCD display-method defaults. A full modeset powers screens/devices off, disables outputs, initializes common VGA and chip-specific extended registers, applies patches, sets primary/secondary pitch and depth, routes output devices to IGA1/IGA2, prepares second-channel state, fills CRTC timing for CRT/DVI/LCD outputs, applies CX700 display-channel selection, records hotplug defaults, re-enables outputs, sets sync polarity, enables PLL/clock state for active IGAs, powers devices back on, and unblanks the screen.

## State And Persistence
The file mutates shared global VIA state through `viaparinfo`, `viafbinfo`, `viafbinfo1`, output enable flags, hotplug fields, chip info, TMDS/LVDS setting structures, and clock function state. Hardware state persists in sequencer/CRTC/graphics/attribute registers, DAC LUTs, PLL registers, and output pad state.

## Dependencies And Integration Points
It depends on `global.h`, `via_clock.h`, mode/register tables from VIA headers, DVI and LCD helper modules, OLPC detection, fbdev timing structures, and low-level VIA register helpers. It is the integration hub between user-selected fb modes, chip detection, DVI/LCD modules, acceleration clock requirements, and actual register programming.

## Risks
The code is register-table and magic-number heavy, with many chip-family branches and global flags. Multiple output configurations interact through IGA assignment, SAMM/dual-fb state, and primary-device selection. Invalid global state can route outputs to the wrong IGA or write inappropriate registers. PLL calculation selects nearest limits but depends on correct per-chip tables. Several helpers silently ignore unsupported states after logging or returning, which can leave partial hardware state.

## Test Signals
Signals include chip/revision detection for each supported family, correct 2D engine enum selection, output-device parsing/printing, IGA assignment for CRT/DVI/LCD/LCD2 combinations, FIFO/fetch register programming for representative resolutions, PLL frequency accuracy, mode setting for single and SAMM/dual-fb configurations, DVI/LCD enable ordering, sync polarity correctness, hotplug field updates, and visual/panel tests across CLE266 through VX900 families.
