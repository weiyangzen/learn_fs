# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/displays/panel-tpo-td043mtea1.c

## Purpose

`panel-tpo-td043mtea1.c` is a SPI-controlled TPO TD043MTEA1 800x480 DPI panel driver. The complete 611-line source was read. It manages panel regulator/reset power sequencing, SPI register programming, gamma/mode/mirror sysfs controls, DSS DPI callbacks, and SPI device PM.

## Important APIs, Types, and Functions

`struct panel_drv_data` tracks the embedded `omap_dss_device`, upstream DPI source, video timings, data lines, SPI device, VCC regulator, reset GPIO, 12-entry gamma table, mode, mirror flags, and PM booleans. `tpo_td043_write()` encodes 16-bit SPI writes. Higher-level helpers are `tpo_td043_write_gamma()`, `tpo_td043_write_mirror()`, `tpo_td043_power_on()`, and `tpo_td043_power_off()`. Sysfs attributes expose `vmirror`, `mode`, and `gamma`. DSS callbacks in `tpo_td043_ops` handle connect, enable, disable, timing, and horizontal mirror operations. PM callbacks are `tpo_td043_spi_suspend()` and `tpo_td043_spi_resume()`.

## Control Flow

Probe configures SPI mode 0/16-bit words, allocates state, finds the endpoint source, loads default 800x480 mode and gamma table, obtains the `vcc` regulator and reset GPIO, creates panel sysfs attributes, initializes the DSS device, and registers the display. Enable programs optional DPI data lines and timings, enables the upstream DPI output, and powers/programs the panel unless the SPI device is suspended. Power-on enables the regulator, waits 160 ms, releases reset, writes mode, normal power register, PWM-related registers, mirror state, and gamma table. Disable turns off the upstream DPI output and powers the panel off unless SPI is suspended.

## State and Persistence Behavior

Gamma, mode, mirror flags, `powered_on`, `spi_suspended`, and `power_on_resume` are volatile runtime state. Sysfs writes update the in-memory desired state and immediately program hardware. Suspend records whether the panel was powered, powers it off, and restores it in SPI resume when needed. There is no persistent storage beyond hardware registers while powered.

## Dependencies and Integration Points

The file depends on SPI, regulator, GPIO descriptor, sysfs, PM sleep helpers, and OMAP DSS DPI operations. It integrates with DSS through `omapdss_register_display()`, `in->ops.dpi`, `set_mirror`/`get_mirror` callbacks, and DT compatible `omapdss,tpo,td043mtea1`.

## Risks and Edge Cases

The sysfs gamma parser accepts 12 unsigned integers but does not bound them to 10-bit values before truncating during SPI writes. Sysfs mode validates only three bits. Several SPI writes in power-on are not checked after the regulator is enabled, so partial programming can still set `powered_on`. Suspend/resume carefully handles the case where DSS enable happens before SPI clocks are available, but races with sysfs writes are not serialized by a mutex.

## Test Signals

Signals include regulator/reset sequencing, sysfs read/write for `vmirror`, `mode`, and `gamma`, SPI write failure paths, DPI enable/disable with visible output, suspend/resume while active and inactive, mirror callback behavior through DSS, and cleanup verifying sysfs group removal and upstream DSS reference release.
