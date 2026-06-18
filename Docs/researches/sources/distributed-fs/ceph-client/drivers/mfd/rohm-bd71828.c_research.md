# sources/distributed-fs/ceph-client/drivers/mfd/rohm-bd71828.c

### Purpose
`rohm-bd71828.c` is the MFD parent driver for ROHM BD71815, BD71828, and BD72720 PMIC families. It selects chip-specific regmap, IRQ, clock, power-key, RTC, power-supply, regulator, GPIO, LED, and clock child devices from device-tree match data, then exposes those children through Linux MFD. It also handles the unusual BD72720 register topology, where one logical PMIC spans two I2C slave addresses.

### Important APIs, Types, And Functions
Key entry points are `bd71828_i2c_probe()`, `bd72720_do_regmaps()`, `set_clk_mode()`, `bd71828_power_off()`, and `bd72720_set_type_config()`. Static data includes `bd71815_mfd_cells[]`, `bd71828_mfd_cells[]`, `bd72720_mfd_cells[]`, `struct resource` IRQ arrays for power and RTC children, regmap configs for BD71815/BD71828/BD72720, and regmap IRQ chips `bd71815_irq_chip`, `bd71828_irq_chip`, and `bd72720_irq_chip`. `struct bd72720_regmaps` stores the real 0x4b and 0x4c regmaps behind the wrapper map.

### Control Flow
Probe requires an I2C IRQ, derives the ROHM chip type from `of_device_get_match_data()`, chooses the MFD cells, regmap config, IRQ chip, clock-mode register, and optional power-key IRQ, then creates a regmap. BD72720 takes the special path through `bd72720_do_regmaps()`, which creates a dummy secondary I2C client at address `0x4c`, initializes real cached regmaps for the 0x4b and 0x4c register banks, and returns an uncached wrapper regmap with custom read/write callbacks that unwrap addresses at `0x100` and above. Probe registers the regmap IRQ chip, optionally enables the BD72720 main IRQ mask, maps the power-key virtual IRQ into the shared `gpio_keys_button`, applies the optional `rohm,clkout-open-drain` clock output mode, adds MFD children, and for BD71828 system-power-controller nodes installs `pm_power_off`.

### State, Persistence, And Dependencies
Runtime state is mostly device-managed regmaps, IRQ chip data, MFD children, and the global `bd71828_dev`/`pm_power_off` hook. Persistent hardware effects include interrupt mask/unmask programming, output clock mode updates, and BD71828 hibernate-state writes during poweroff. Regmap cache state is maple-cached for direct maps; the BD72720 wrapper intentionally has no cache to avoid duplicating the real cached regmaps. Dependencies include I2C, regmap, regmap-irq, MFD core, gpio-keys, input event constants, OF matching, and ROHM chip register headers.

### Integration Points
Children consume named IRQ resources and the regmap exposed by the MFD parent: regulator/PMIC, power-supply, RTC, GPIO, LED, clock, and gpio-keys children all depend on this file's IRQ numbering and regmap topology. The regmap IRQ domain is passed to `devm_mfd_add_devices()` so child resources can resolve virtual IRQs. The BD72720 wrapper lets child drivers use one logical register address space while still reaching the charger registers on the secondary I2C address.

### Risks
The file relies on large static IRQ maps and sub-IRQ offset tables; wrong offsets silently route fault, charger, RTC, or power-button events to the wrong child. `button` is a static mutable object shared across probed instances, so multi-instance systems could overwrite `button.irq`. The BD72720 wrapper requires all secondary-bank register constants to include the `0x100` offset; direct access to the secondary real regmap with wrapped addresses would hit the wrong hardware register. The poweroff loop intentionally never returns and uses raw SMBus because regmap may sleep; failures only retry after `mdelay(500)`. Clock mode accepts only `0` or `1`, so binding mistakes fail probe.

### Test Signals
Useful tests include DT probe for all three compatibles with a valid IRQ, regmap read/write checks on BD72720 registers below and above `0x100`, IRQ delivery for RTC, power, charger, GPIO, and short-push events, and verification that `gpio-keys` receives the mapped power-button IRQ. Suspend/resume should exercise regcache behavior for volatile IRQ/status ranges. A BD71828 system-power-controller test should confirm `pm_power_off` writes hibernate state using SMBus. Bad DT tests should cover missing IRQ, invalid `rohm,clkout-open-drain`, unavailable secondary I2C address, and MFD child creation failures.
