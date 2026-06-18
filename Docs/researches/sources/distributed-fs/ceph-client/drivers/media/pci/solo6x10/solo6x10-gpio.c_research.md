<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-gpio.c

## Purpose
`solo6x10-gpio.c` configures board GPIO lines for video reset, internal video functions, relay outputs, and sensor inputs, optionally exporting a 24-line gpiolib chip.

## Important APIs, Types, and Functions
`solo_gpio_mode()` programs the two SOLO GPIO configuration registers, handling low GPIOs as two-bit modes and high GPIOs as one-bit sensor direction plus enable bits. `solo_gpio_set()` and `solo_gpio_clear()` update `SOLO_GPIO_DATA_OUT`. `solo_gpio_config()` applies the board default reset/relay/input layout. Under `CONFIG_GPIOLIB`, `solo_gpiochip_get_direction()`, `solo_gpiochip_get()`, and `solo_gpiochip_set()` implement a `gpio_chip` whose logical offset 0 maps to hardware GPIO8.

## Control Flow
Initialization always calls `solo_gpio_config()`: pulse GPIO4/5 for video reset, set GPIO0-3 to internal video mode, set GPIO8-15 as relay outputs cleared low, and set GPIO16-31 as inputs. If gpiolib is enabled, a dynamic-base chip named `solo6x10_gpio` is registered with 24 exported lines. Exit removes the chip, clears reset lines, and reapplies the default hardware configuration.

## State and Persistence
State lives in the SOLO GPIO registers and the embedded `gpio_chip` inside `struct solo_dev`. There is no persistent storage. Output levels are reset by init/exit and otherwise reflect hardware register state.

## Dependencies and Integration Points
The file integrates with the PCI device via `solo_dev`, kernel gpiolib when enabled, and the rest of the driver through board reset sequencing before TW28 decoder initialization.

## Risks and Edge Cases
The first eight hardware GPIOs are intentionally hidden because GPIO0-3 and reset lines are board-internal. There is no explicit lock around read-modify-write register updates, so concurrent gpiolib set operations could race if multiple callers manipulate relays at once. `solo_gpiochip_get_direction()` returns `-1` for unsupported modes rather than a conventional errno.

## Test Signals
Verify video decoders reset during probe, relay GPIO offsets 0-7 drive hardware GPIO8-15, input offsets 8-23 read GPIO16-31, gpiolib registration/removal succeeds, and exit leaves board-internal lines in a known reset/default state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-gpio.c -->
