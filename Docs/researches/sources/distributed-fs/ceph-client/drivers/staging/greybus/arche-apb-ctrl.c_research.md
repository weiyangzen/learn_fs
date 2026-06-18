# sources/distributed-fs/ceph-client/drivers/staging/greybus/arche-apb-ctrl.c

## Purpose

`arche-apb-ctrl.c` is the child APB controller driver for the Greybus Arche platform. It controls AP bridge reset, boot-retention, optional SPI-enable, clocks, regulators, and sysfs-visible APB state transitions.

## Important APIs, Types, and Functions

`struct arche_apb_ctrl_drvdata` stores APB GPIOs, regulators, clock pins, pinctrl, SPI enable polarity, and `enum arche_platform_state`. Exported cross-file operations are `apb_ctrl_coldboot()`, `apb_ctrl_fw_flashing()`, `apb_ctrl_standby_boot()`, and `apb_ctrl_poweroff()`. Key sequences are `coldboot_seq()`, `fw_flashing_seq()`, `standby_boot_seq()`, and `poweroff_seq()`.

## Control Flow

Probe allocates driver data, requests firmware-described GPIO/regulator/pinctrl resources, initializes APB state to off, honors `arche,init-disable`, stores drvdata, and creates a `state` sysfs file. Parent platform code calls the exported APB operations for cold boot or poweroff, while users can write `off`, `active`, `standby`, or `fw_flashing` to sysfs. Cold boot asserts reset, enables regulators and clock, deasserts boot-retention, delays, deasserts reset, and marks active. Firmware flashing powers rails, optionally requests SPI-enable GPIO, holds reset, and marks flashing.

## State and Persistence Behavior

State is volatile in `apb->state` and `init_disabled`; hardware side effects include GPIO levels, regulator enables, and APB reset/power state. No file-backed persistence exists.

## Dependencies and Integration Points

The file integrates with platform devices, gpiod, regulators, pinctrl, optional clock-enable GPIO, device properties, and the parent Arche platform through `arche_platform.h`. It registers an OF platform driver for compatible `usbffff,2`.

## Risks and Edge Cases

`fw_flashing_seq()` unconditionally calls `regulator_enable()` on `vcore` and `vio`, even though probe treats missing regulators as optional and stores error pointers; this can dereference error pointers. `spi_en` is used both as an optional descriptor and as a flag for whether to request the descriptor, but probe never obtains it initially, so the conditional may never run unless external state sets it. `devm_gpiod_put()` inside state transitions interacts awkwardly with devm lifetime. State transitions are not protected by a mutex in this child driver, so concurrent sysfs and parent calls can race.

## Test Signals

Test with and without regulators, clock-enable, SPI-enable polarity, and `arche,init-disable`. Exercise sysfs transitions in all orders, parent-triggered cold boot/poweroff, remove/shutdown, missing GPIO failures, and concurrent state writes.
