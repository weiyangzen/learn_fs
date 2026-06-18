# sources/distributed-fs/ceph-client/drivers/misc/ti_fpc202.c

## Purpose
`ti_fpc202.c` drives the TI FPC202 dual-port controller. It combines I2C address translation for two downstream ports, a 28-line GPIO controller, optional LED class devices on LED-capable GPIO outputs, and an optional enable GPIO.

## Important APIs, Types, and Functions
`struct fpc202_priv` stores the I2C client, ATR object, enable GPIO, gpiochip, LED objects, mutexes, address caches, and probed-port bitmap. `struct fpc202_led` wraps LED class state and the GPIO line claimed for LED ownership. I2C helpers are `fpc202_read()`, `fpc202_write()`, and `fpc202_write_dev_addr()`. GPIO callbacks are `fpc202_gpio_get()`, `fpc202_gpio_set()`, `fpc202_gpio_direction_input()`, and `fpc202_gpio_direction_output()`. ATR hooks are `fpc202_attach_addr()` and `fpc202_detach_addr()`. LED hooks include `fpc202_led_blink_set()`, `fpc202_led_brightness_get()`, `fpc202_led_brightness_set()`, and registration helpers. Probe/remove are `fpc202_probe()` and `fpc202_remove()`.

## Control Flow
Probe allocates private data, initializes mutexes, enables the chip, registers the gpiochip, creates an I2C ATR, registers child LED nodes, then iterates child nodes with `reg` values for FPC202 ports. Each port gets two aliases derived from the FPC202 self address and port ID, is added as an ATR adapter, and has both translation entries reset to invalid. ATR attach writes the target address into MOD and AUX registers for the device number implied by alias parity; detach scans the address cache and invalidates matching entries. GPIO writes either program simple output bits or switch LED-capable lines between on/off LED modes. LED brightness and blink operations program mode, PWM, and blink timing registers.

## State and Persistence
Runtime state includes cached translated addresses per port/device, probed port bitmap, LED modes, claimed GPIO descriptors for LED lines, and device registers. `reg_dev_lock` serializes translation register/cache updates and `led_mode_lock` serializes shared LED mode register updates. Hardware register state is not restored after driver removal except translation invalidation during probe and enable GPIO deassertion during remove.

## Dependencies and Integration Points
The driver depends on SMBus byte data access, the Linux I2C ATR framework, gpiolib, LED classdev registration, OF child nodes, devres groups, and optional enable GPIO. It imports the `I2C_ATR` namespace and matches `ti,fpc202`.

## Risks and Edge Cases
The LED child offset validation allows `offset == FPC202_GPIO_COUNT`, which is one past the valid 0..27 GPIO range and can index beyond the eight LED entries. Error unwinding after `gpiochip_add_data()` may call `gpiochip_remove()` even when ATR creation failed after the chip was added, which is intended, but the `disable_gpio` label name obscures ownership. GPIO get is unsupported on LED-capable outputs. The AUX register write is empirical, so hardware variants may need confirmation.

## Test Signals
Validate two downstream ATR adapters, alias assignment by I2C address and port, attach/detach register writes and cache invalidation, all GPIO direction/value paths, LED brightness/PWM/blink timing including rounding and saturation, invalid LED offsets, enable GPIO behavior, and remove/unwind freeing own GPIO descriptors and ATR adapters.
