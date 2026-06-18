# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-tpo-td028ttec1.c

## Purpose

`panel-tpo-td028ttec1.c` is a SPI-initialized Toppoly TD028TTEC1 DPI panel driver for the legacy OMAP DSS/fbdev stack. The complete 476-line source was read. It provides fixed 480x640 timings, sends the JBT controller initialization sequence over 9-bit SPI, and registers a DPI `omap_dss_device`.

## Important APIs, Types, and Functions

`struct panel_drv_data` stores the embedded DSS device, upstream DPI source, data-line count, current timings, and SPI device. SPI programming helpers are `jbt_ret_write_0()`, `jbt_reg_write_1()`, and `jbt_reg_write_2()`, using `JBT_COMMAND` and `JBT_DATA` framing plus `enum jbt_register` register IDs. DSS driver callbacks are `td028ttec1_panel_connect()`, `disconnect()`, `enable()`, `disable()`, `set_timings()`, `get_timings()`, and `check_timings()`. Probe helpers are `td028ttec1_probe_of()` and `td028ttec1_panel_probe()`.

## Control Flow

Probe requires DT, configures SPI as 9 bits per word and mode 3, allocates state, finds the first endpoint source, sets default timings, fills an `omap_dss_device` with DPI type, and registers it. Enable validates connection and current state, programs optional DPI data lines and timings on the upstream source, enables the upstream DPI output, then sends the panel wake and register initialization sequence: three zero commands, deep standby exit, display interface setup, booster/power/gamma/timing registers, and finally `DISPLAY_ON`. Disable sends `DISPLAY_OFF`, output control and sleep/power-off commands, disables upstream DPI, and marks the DSS device disabled.

## State and Persistence Behavior

State is volatile and minimal: timings and SPI/upstream pointers live in `panel_drv_data`, while panel controller register state is reprogrammed on each enable. There is no sysfs state and no persistence across driver unbind or power loss.

## Dependencies and Integration Points

The driver depends on SPI and the OMAP DSS DPI operation table. It integrates with DT endpoint routing through `omapdss_of_find_source_for_first_ep()`, with DSS display enumeration via `omapdss_register_display()`, and with the SPI core via `module_spi_driver()`. It keeps old compatible strings and SPI IDs for DTB/module compatibility.

## Risks and Edge Cases

Initialization accumulates return values with `r |= ...`, so the final error is collapsed to `-EIO` and later SPI commands may still be attempted after an earlier failure. There is no local mutex around enable/disable or timing changes. `data_lines` is never populated from DT in this file, so it remains zero unless future code extends probe. The panel programming sequence is timing-sensitive and mostly fixed magic values.

## Test Signals

Signals include successful `spi_setup()` with 9-bit transfers, DT endpoint discovery, display registration, DPI enable followed by a visible image, error injection in SPI writes, disable/enable cycling, timing check delegation to the upstream DPI source, and compatibility matching for both `omapdss,tpo,td028ttec1` and older `omapdss,toppoly,td028ttec1`.
