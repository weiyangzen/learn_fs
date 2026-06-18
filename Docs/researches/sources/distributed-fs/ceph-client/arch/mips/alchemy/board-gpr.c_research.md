# sources/distributed-fs/ceph-client/arch/mips/alchemy/board-gpr.c

## Purpose
`board-gpr.c` contains board support for the Trapeze ITS GPR Au1550 platform. It provides the system-type string, early UART output, board setup, watchdog-based reset/power hooks, static flash layout, GPIO LED devices, bit-banged I2C with an LM83 sensor, and Alchemy PCI host platform data.

## Important APIs, Types, And Functions
`get_system_type()` returns `"GPR"`. `prom_putchar()` writes through `alchemy_uart_putchar()` on UART0. `board_setup()` installs `pm_power_off`, `_machine_halt`, and `_machine_restart`, enables UART1/UART3, and releases the UMTS-card reset GPIO. `gpr_reset()` drives LEDs orange, toggles GPIO1 to trigger an ADM6320 watchdog reset, disables local IRQs, and waits. `gpr_power_off()` waits forever.

Static data includes `gpr_wdt_device`, `gpr_mtd_partitions`, `gpr_flash_data`, `gpr_mtd_device`, `gpr_gpio_leds`, `gpr_led_devices`, `gpr_i2c_gpiod_table`, `gpr_i2c_data`, `gpr_i2c_device`, `gpr_i2c_info`, `alchemy_pci_host_res`, `gpr_pci_pd`, `gpr_pci_host_dev`, and `gpr_devices`. `gpr_map_pci_irq()` maps slot 0 INTA/INTB to Au1550 PCI IRQs. `gpr_pci_init()` is an `arch_initcall`, and `gpr_dev_init()` is a `device_initcall`.

## Control Flow
Early platform setup calls `board_setup()`, which configures restart/power hooks and minimal UART/UMTS GPIO state. Later, `gpr_pci_init()` registers the `"alchemy-pci"` host before MIPS PCI bus scanning, and `gpr_dev_init()` registers the GPIO descriptor lookup table, I2C board info, watchdog, physmap flash, I2C-GPIO adapter, and LEDs.

Reset control enters `gpr_reset()`: GPIOs 4 and 5 assert both active-low LED colors, local interrupts are disabled, GPIO1 is pulsed to reset the external watchdog circuit, and the CPU waits for the board reset. Normal power off has no board power controller and simply idles indefinitely.

## State And Persistence
The file persists hardware state through GPIO direction/value changes, UART enable registers, and PCI configuration bits. It registers platform devices that persist for driver binding. Flash partitions are fixed board policy and include read-only rootfs/yamon regions through `mask_flags`. The I2C GPIO lookup table persists in gpiolib so the `i2c-gpio` platform device can resolve SCL/SDA offsets on `"alchemy-gpio2"`.

## Dependencies And Integration Points
It depends on Alchemy GPIO/UART helpers, MIPS reboot hooks, platform device core, physmap MTD, GPIO LEDs, I2C-GPIO, gpiod lookup tables, PCI platform data, and Au1550 PCI IRQ definitions. It integrates with `setup.c` through `board_setup()`, with early printk through `prom_putchar()`, with `arch/mips/alchemy/Makefile` via `CONFIG_MIPS_GPR`, and with PCI scanning through the arch initcall ordering.

## Risks
GPIO numbers and active-low semantics are board-specific; wrong values can hold the UMTS card in reset, fail to trigger the watchdog, or invert LEDs. The watchdog reset path assumes the external ADM6320 circuit is wired to GPIO1 and resets after about 200 ms. Flash partition offsets overlap intentionally for aggregate views (`kernel+rootfs`) but can be dangerous if exposed writable. `gpr_map_pci_irq()` returns `0xff` for unsupported pins, so PCI devices outside the expected slot/pin wiring may fail. Endian-specific PCI config flags must match the CPU endian build.

## Test Signals
Build `CONFIG_MIPS_GPR=y` and confirm `board-gpr.o` links. Boot logs should include `"Trapeze ITS GPR board"` and `get_system_type()` should report `GPR`. Device enumeration should show `adm6320-wdt`, `physmap-flash` with six partitions, `leds-gpio`, `i2c-gpio`, and LM83 board info. PCI probe should see the Alchemy PCI host before bus scanning. Hardware tests should verify watchdog reset, UART1/UART3 enablement, UMTS reset release, LED polarity, I2C sensor probing, and PCI INT routing.
