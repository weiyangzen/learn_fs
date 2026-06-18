# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-aw9523.c

## Purpose
This driver supports the Awinic AW9523B I2C GPIO expander as a combined pinctrl, pinmux, pinconf, GPIO, and optional nested interrupt controller. It exposes 16 pins arranged as two 8-bit ports, with GPIO/PWM muxing, input/output direction and level control, port 0 open-drain versus push-pull configuration, register caching, reset handling, and safe hardware defaults.

## Important APIs, Types, and Functions
`struct aw9523` is the main device state: device pointer, regmap, I2C mutex, reset GPIO, optional `vio` regulator status, pinctrl device, gpio chip, and optional `struct aw9523_irq`. Register macros map port-relative input, output, config, interrupt-disable, chip ID, global control, port mode, and reset registers. Pinctrl callbacks are `aw9523_pinctrl_get_groups_count`, `aw9523_pinctrl_get_group_name`, and `aw9523_pinctrl_get_group_pins`; pinmux callbacks are `aw9523_pmx_get_funcs_count`, `aw9523_pmx_get_fname`, `aw9523_pmx_get_groups`, and `aw9523_pmx_set_mux`. Pinconf is implemented by `aw9523_pconf_get` and `aw9523_pconf_set`. GPIO behavior is provided by direction, get, set, get/set-multiple helpers. IRQ behavior is handled by `aw9523_irq_mask`, `aw9523_irq_unmask`, `aw9523_irq_thread_func`, bus lock/sync, and `aw9523_gpio_irq_type`. Probe/remove are `aw9523_probe` and `aw9523_remove`.

## Control Flow and State
Probe allocates state, obtains the mandatory reset GPIO, creates the I2C regmap, enables optional `vio`, initializes the I2C mutex, calls `aw9523_hw_init`, fills a pinctrl descriptor, initializes the gpiochip, optionally wires IRQ support if `client->irq` is present, registers pinctrl, and finally registers the gpiochip. Hardware initialization bypasses cache, tries soft reset then hardware reset with retries, verifies chip ID `0x23`, sets all pins to GPIO, sets port 0 open-drain, sets all pins input, disables interrupts, reads port state to clear setup interrupts, and reinitializes the flat regcache. Remove reinitializes hardware when no controllable regulator exists, leaving pins in defaults.

## State and Persistence Behavior
Persistent state is split between hardware registers and regcache. `i2c_lock` serializes register access because regmap locking is disabled. IRQ bus lock puts regmap in cache-only mode, updates mask bits through irq callbacks, then syncs cache on unlock. `cached_gpio` stores the previous 16-bit input snapshot to synthesize edge handling from changed bits. The `vio_vreg` integer records whether the optional regulator is controllable or absent.

## Dependencies and Integration Points
The driver integrates with the I2C core (`module_i2c_driver`), regmap, regulator, gpiod reset, pinctrl/pinmux/pinconf, gpiolib, and IRQ domains. Firmware binding uses compatible `awinic,aw9523-pinctrl`; optional `interrupt-controller` enables nested GPIO IRQs.

## Risks
Reading input state is precious because it clears interrupt status; wrong regcache policy can lose events. Only port 0 supports open-drain mode, while port 1 is always push-pull, so pinconf must reject unsupported requests. `aw9523_pmx_set_mux` computes the register pin as modulo port width; mux changes depend on matching port-mode register selection. IRQs support only `IRQ_TYPE_NONE` and both-edge semantics, with software change detection rather than hardware per-edge programming. Any missed mutex coverage can race slow I2C operations.

## Test Signals
Build coverage should include I2C, GPIO, pinctrl, pinconf, and IRQ configurations. Runtime signals include successful chip ID read, reset fallback behavior, GPIO get/set and get/set-multiple across both ports, pinconf rejection on unsupported drive modes, PWM/GPIO mux switching, interrupt delivery on input changes, and remove-time reinitialization when `vio` is not controllable.
