# sources/distributed-fs/ceph-client/arch/mips/alchemy/board-mtx1.c

## Purpose
`board-mtx1.c` implements board support for the 4G Systems MTX-1 Au1500 platform. It sets board identity, early UART output, reset/power hooks, GPIO and pinmux defaults, flash partitions, PCI/CardBus helper behavior, GPIO LEDs, watchdog, button input, and Ethernet platform-data overrides.

## Important APIs, Types, And Functions
`get_system_type()` returns `"MTX-1"`, and `prom_putchar()` writes to UART0. `board_setup()` configures USB power if OHCI is enabled, sets `SYS_PINFUNC`, drives board GPIO defaults, sets LED state, and installs reboot/power hooks. `mtx1_reset()` jumps to reset vector `0xbfc00000`; `mtx1_power_off()` waits forever.

Device setup uses software nodes and property entries: `mtx1_gpiochip_node`, `mtx1_gpio_keys_node`, `mtx1_button_node`, `mtx1_gpio_leds_node`, `mtx1_green_led_node`, `mtx1_red_led_node`, and watchdog GPIO properties. Initializer helpers `mtx1_keys_init()`, `mtx1_wdt_init()`, and `mtx1_leds_init()` create `gpio-keys`, `mtx1-wdt`, and `leds-gpio` platform devices. `mtx1_mtd` exposes physmap flash partitions. PCI support uses `mtx1_pci_idsel()`, `mtx1_irqtab`, `mtx1_map_pci_irq()`, `mtx1_pci_pd`, and `mtx1_pci_host`. `mtx1_register_devices()` is an `arch_initcall`.

## Control Flow
`board_setup()` runs during early memory/platform setup and establishes power/reset behavior plus pin states. At arch initcall time, `mtx1_register_devices()` sets IRQ trigger types for GPIO/PCI-related lines, overrides MAC0 Ethernet platform data with `phy_search_highest_addr` and `phy1_search_mac0`, registers the `"alchemy-gpio2"` software node, registers PCI and MTD devices, then creates LED, watchdog, and key devices.

During PCI configuration, `mtx1_pci_idsel()` toggles GPIO1/EXT_IO3 to suppress IDSEL signals for a proprietary CardBus adapter except for device select 0, and `mtx1_map_pci_irq()` indexes a fixed slot/pin table. The reset path simply jumps to firmware reset, while power off is an infinite MIPS `wait` loop.

## State And Persistence
The file mutates pinmux, GPIO direction/value, board LEDs, USB power switch state, reboot hooks, platform-device registrations, software-node registrations, and MAC0 platform data before generic Alchemy Ethernet registration. Flash partition layout is fixed and includes read-only bootloader protection. IRQ trigger configuration persists in the interrupt controller for the lifetime of the boot unless changed later.

## Dependencies And Integration Points
It depends on Alchemy GPIO, `alchemy_wrsys()`, IRQ type APIs, platform device core, software node/property APIs, GPIO LEDs, GPIO keys, MTD physmap, Alchemy PCI platform data, and Au1000 Ethernet platform data. It integrates with `au1xxx_override_eth_cfg()` in `platform.c`, with `setup.c` via `board_setup()`, with early console via `prom_putchar()`, and with Kconfig/Makefile via `CONFIG_MIPS_MTX1`.

## Risks
`mtx1_map_pci_irq()` indexes `mtx1_irqtab[slot][pin]` without local bounds checks, relying on PCI core inputs matching expected IDSEL/pin ranges. GPIO setup is order-sensitive for PCI/CardBus, USB power, LED state, and PHY TX_ER. Software-node registration errors are logged but not always fatal, so missing LEDs/keys/watchdog may not stop boot. The reset-vector jump assumes boot flash/fardware is mapped at `0xbfc00000`. The watchdog error log says "gpio-keys" on watchdog registration failure, which can mislead diagnostics.

## Test Signals
Build and boot `CONFIG_MIPS_MTX1=y`; logs should include `"4G Systems MTX-1 Board"`. Confirm GPIO2 software node, `gpio-keys`, `leds-gpio`, `mtx1-wdt`, physmap flash, and Alchemy PCI host devices are registered. Check `au1000-eth` MAC0 probes with the overridden PHY search policy. Hardware tests should cover USB power switch, LED polarity, system button input, watchdog GPIO, flash partition protection, PCI/CardBus enumeration, and reset-vector reboot.
