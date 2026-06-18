# sources/distributed-fs/ceph-client/drivers/platform/mellanox/nvsw-sn2201.c

## Purpose
Nvidia SN2201 switch platform driver. It constructs the CPLD-backed I2C topology, registers IO, LED, watchdog, and hotplug children, creates static board devices behind muxes, and selects a busbar/external-power variant when DMI SKU `HI168` is detected.

## Important APIs, Types, And Functions
`struct nvsw_sn2201` stores child platform devices, hotplug/I2C/IO/LED/watchdog platform data, static I2C device lists, CPLD/main mux device lists, and power-source mode. Register callbacks constrain the 8-bit CPLD regmap. Static tables describe hotplug groups for PSU, power, fan, and system/ASIC events; static I2C inventory; LEDs; `mlxreg-io` attributes; and watchdog data. Main helpers are `nvsw_sn2201_i2c_completion_notify()`, `nvsw_sn2201_config_pre_init()`, `nvsw_sn2201_config_init()`, and static device create/destroy functions.

## Control Flow
Probe allocates state, checks DMI SKU, adds LPC I/O resources, selects static and hotplug tables, and registers the `i2c_mlxcpld` controller with a completion callback. Completion creates the main mux, creates a dummy CPLD client, initializes regmap/defaults, syncs cache, registers `mlxreg-io`, `leds-mlxreg`, `mlx-wdt`, and `mlxreg-hotplug`, then waits for deferred mux adapters and creates remaining static devices.

## State, Dependencies, Integration, Risks, Tests
State includes regmap cache/defaults, child platform handles, I2C clients/adapters, selected power-source tables, and hotplug-managed dynamic devices. Dependencies include ACPI `NVSN2201`, DMI, LPC resources, `i2c_mlxcpld`, I2C muxes, regmap, `mlxreg-io`, `leds-mlxreg`, `mlx-wdt`, and `mlxreg-hotplug`. Risks include adapter reference leaks on partial failures, static global platform data mutation, SKU-dependent missing PSU/power hotplug coverage, IRQ/resource assumptions, typo-like `ASIC_MAKS` naming consistency, and complex cleanup ordering. Test signals include ACPI probe, DMI SKU branch, LPC resource addition, completion callback ordering, static device creation behind muxes, regmap default writes, child platform registration, hotplug events, and removal cleanup.
