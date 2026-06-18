# sources/distributed-fs/ceph-client/drivers/pinctrl/bcm/pinctrl-nsp-mux.c

Purpose: Broadcom Northstar Plus IOMUX pinctrl driver for group-based muxing and GPIO request/free handoff on muxable NSP pins.

Important APIs/types/functions: `struct nsp_pinctrl`, `nsp_pin`, `nsp_pin_group`, `nsp_pin_function`, and `nsp_mux_log` model controller data. `nsp_pinmux_set()` performs conflict-checked masked register writes. `nsp_gpio_request_enable()` and `nsp_gpio_disable_free()` switch individual mux bits for gpiolib users.

Control flow: probe maps three register resources, initializes mux logs from static group descriptors, creates pin descriptors with `gpio_select` in `drv_data`, binds static groups/functions, and registers `nsp-pinmux`. DT states map at group granularity via `pinconf_generic_dt_node_to_map_group`. `set_mux` validates selectors, logs first use of a mux field, rejects incompatible double configuration, and writes base0/base1/base2 under spinlock.

State and persistence: mux state is persisted in hardware registers. `mux_log` is runtime-only and initialized as unconfigured, so bootloader-configured mux state is not considered. GPIO request/free toggles base0 bits using each pin's `gpio_select` value.

Dependencies/integration: integrates with Linux pinctrl and pinmux cores, Broadcom NSP DT compatible `brcm,nsp-pinmux`, and the companion NSP GPIO driver. Functions cover SPI, I2C, MDIO, PWM, GPIO_B, UART, SATA LEDs, SDIO, switch LEDs, NAND, and eMMC.

Risks: shared PWM/GPIO_B fields require DT to request paired groups correctly. Double-configuration detection is per running driver instance and cannot protect against external firmware changes. Base1 mapping uses `devm_ioremap()` from a resource instead of `devm_platform_ioremap_resource()`, so resource validation differs.

Test signals: list functions/groups in debugfs, apply conflicting mux states to confirm `-EINVAL`, request GPIOs through gpiolib and verify base0 changes, and validate NAND/eMMC mutual exclusion on the shared base2 field.
