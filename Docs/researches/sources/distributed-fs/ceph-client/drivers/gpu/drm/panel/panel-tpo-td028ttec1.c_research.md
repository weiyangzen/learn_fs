# sources/distributed-fs/ceph-client/drivers/gpu/drm/panel/panel-tpo-td028ttec1.c

## Purpose
This SPI/DPI DRM panel driver supports the Toppoly TD028TTEC1 panel and backward-compatible `toppoly,td028ttec1` device tree name. It configures a JBT6K74-like controller through 9-bit SPI register writes and exposes a fixed 480x640 DPI mode.

## Important APIs, Types, And Functions
`struct td028ttec1_panel` stores the DRM panel and SPI device. `jbt_ret_write_0()`, `jbt_reg_write_1()`, and `jbt_reg_write_2()` send command-only, one-byte, and two-byte register writes, using an optional shared error pointer to stop subsequent writes after the first failure. Panel ops are prepare, enable, disable, unprepare, and get_modes.

## Control Flow
Probe allocates the panel, configures SPI mode 3 and 9 bits per word, binds OF backlight, and adds the panel. Prepare sends a long register initialization sequence: wake/deep-standby exit, RGB interface setup, power rails, output control, sleep-out, display mode, booster, voltage, gamma, blanking, and timing registers. Enable sends display-on. Disable sends display-off. Unprepare sets output control, enters sleep, and powers off. Remove removes the panel and calls disable/unprepare.

## State And Persistence
There is no stored mutable panel configuration beyond the SPI pointer. Controller register state is programmed every prepare. Backlight state is managed externally through DRM panel OF backlight.

## Dependencies And Integration Points
The driver uses DRM panel, SPI, OF/SPI match tables, MIPI-like command constants encoded locally, and OF backlight. It presents a DPI connector and fixed bus flags.

## Risks
The SPI command format depends on 9-bit transfers and host support. The source contains a FIXME that sync signals should be sampled on a datasheet-rising edge, while legacy code indicates falling edge; bus flags therefore need real-hardware validation. Disable/unprepare ignore errors. The initialization sequence is legacy and magic-value heavy.

## Test Signals
Confirm SPI 9-bit setup, fixed mode and bus flags, backlight binding, command error propagation during prepare, and real hardware visual behavior, especially sync polarity and color/flicker. Regression tests should cover both compatible strings.
