# sources/distributed-fs/ceph-client/arch/powerpc/platforms/pasemi/gpio_mdio.c

Purpose: PHYLIB MDIO bus driver that bit-bangs MDIO/MDC over PA Semi GPIO registers.

Important APIs and control flow: GPIO helpers drive set/clear/direction/input registers. `bitbang_pre` sends a 40-bit preamble, start bits, opcode, PHY address, and register address. `gpio_mdio_read` tri-states MDIO for turnaround and samples 16 data bits; `gpio_mdio_write` emits turnaround and 16 data bits then tri-states. `gpio_mdio_probe` allocates `gpio_priv` and `mii_bus`, reads `reg`, `mdc-pin`, and `mdio-pin` from OF, registers with `of_mdiobus_register`, and stores drvdata. Module init maps a `1682m-gpio` or `pasemi,pwrficient-gpio` node before registering the platform driver.

State, dependencies, and risks: state includes global `gpio_regs`, per-bus pin numbers, and registered MII buses. Dependencies include OF GPIO/MDIO properties, PHYLIB, platform devices, and timing via `udelay(1)`. Risks include unchecked missing properties, a global GPIO mapping shared by all buses, manual MDIO timing without locking, and cleanup path using `kfree(new_bus)` instead of `mdiobus_free` on register failure. Test signals are MDIO scan, PHY reads/writes, module unload cleanup, and stable Ethernet PHY detection.
