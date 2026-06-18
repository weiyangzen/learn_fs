# sources/distributed-fs/ceph-client/arch/xtensa/platforms/xt2000/setup.c

Purpose: Initializes XT2000 board LEDs, serial ports, SONIC network device, heartbeat, restart, and power-off behavior.

Important APIs, types, and functions: `led_print()`, `xt2000_power_off()`, `xt2000_restart()`, `platform_setup()`, `xt2000_heartbeat()`, serial port table, `xt2000_serial8250_device`, `xt2000_sonic_device`, and `xt2000_setup_devinit()`.

Control flow: Early platform setup writes `LINUX` to the LED display. Device init registers 8250 platform serial ports and SONIC resources, starts a half-second LED heartbeat timer, and registers sys-off handlers. Poweroff writes `POWEROFF`, disables interrupts, and spins; restart calls `cpu_reset()`.

State and persistence: Heartbeat timer toggles LED position 7; platform devices persist; sys-off handlers persist. LED writes go to memory-mapped board registers.

Dependencies and integration: Board hardware/serial headers, platform device core, serial8250, `xtsonic` driver, timers, and generic reboot/sys-off paths.

Risks: `led_print()` assumes an 8-character non-NULL string; poweroff never returns; endian serial port offsets differ; platform_device_register return values are ignored.

Test signals: LED boot/power/heartbeat display, ttyS device probe, SONIC resource probe, reboot path, and poweroff spin behavior.
