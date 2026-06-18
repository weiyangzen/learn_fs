# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/gpio.c

## Purpose
`gpio.c` adapts Renesas/SuperH PFC pin tables into Linux `gpio_chip` instances. It supports real pin GPIOs backed by PFC data registers and, when `CONFIG_PINCTRL_SH_FUNC_GPIO` is enabled, a deprecated legacy function-GPIO interface for old SH platforms.

## Important APIs, Types, And Functions
- `struct sh_pfc_gpio_data_reg` stores a `pinmux_data_reg` pointer and a `shadow` copy of the output register value.
- `struct sh_pfc_gpio_pin` stores the data-register index and bit number for one PFC pin.
- `struct sh_pfc_chip` combines a `struct sh_pfc *`, a `struct gpio_chip`, the memory window containing GPIO data registers, and the derived per-register/per-pin lookup tables.
- `gpio_setup_data_regs()` counts data registers, snapshots initial hardware values into shadows, and maps each PFC pin to a data register bit using `gpio_setup_data_reg()`.
- GPIO callbacks include request/free, direction input/output, get, set, and `to_irq`.
- `sh_pfc_register_gpiochip()` is the exported entry used by `core.c` after pinctrl registration.

## Control Flow
`sh_pfc_register_gpiochip()` first exits successfully if the SoC has no `data_regs`. It finds the MMIO window containing the first data register, exits successfully if no such window exists, validates IRQ resource count against `gpio_irq_size`, and registers a real GPIO chip through `sh_pfc_add_gpiochip()`. For non-DT legacy builds, it adds pin ranges and optionally registers a second function-GPIO chip.

For real GPIOs, `gpio_pin_request()` checks that the pin maps to a valid PFC pin with a nonzero enum ID, then delegates reservation to `pinctrl_gpio_request()`. Output direction sets the desired value in the shadow and writes the data register before asking pinctrl to switch direction. Input reads the hardware data register directly. `to_irq` scans the SoC `gpio_irq` tables and returns the platform IRQ associated with a GPIO.

For function GPIOs, `gpio_function_request()` warns once that the API is deprecated, then programs a function mux mark under `pfc->lock` by calling `sh_pfc_config_mux(mark, PINMUX_TYPE_FUNCTION)`.

## State And Persistence
The driver keeps a software shadow per data register to preserve unrelated output bits during GPIO writes. Initial shadow state is read from hardware at registration time. Direction and mux state persists in PFC hardware registers through the core pinctrl path. GPIO chip instances are device-managed and are cleaned up with the parent PFC device.

## Dependencies
It depends on Linux GPIO, pinctrl consumer, spinlock, device, slab, and module APIs. It relies on `core.h` for raw register access and pin-index/mux helpers, and on SoC data in `struct sh_pfc_soc_info`: `pins`, `data_regs`, `gpio_irq`, `func_gpios`, and range metadata initialized by `core.c`.

## Risks And Review Notes
- `gpio_get_data_reg()` indexes `chip->pins[idx]` after `sh_pfc_get_pin_index()`; normal request paths validate the index, but misuse from future paths could produce invalid indexing.
- `gpio_pin_set_value()` updates `shadow` without its own lock. Correctness relies on GPIO core serialization or external constraints; concurrent writes to different pins in the same register should be reviewed.
- `gpio_setup_data_reg()` calls `BUG()` if no data register bit matches a pin enum, so inconsistent SoC tables can crash during GPIO registration.
- If the GPIO data registers are not in the supplied memory resources, GPIO support silently stays disabled. This supports boards with separate GPIO devices but can hide resource mistakes.
- `gpio_pin_to_irq()` returns `0` on no match. Since IRQ 0 handling is architecture-dependent, callers should be checked for expectations; many modern GPIO drivers return negative errors for missing IRQs.

## Test Signals
Build with and without `CONFIG_PINCTRL_SH_PFC_GPIO` and `CONFIG_PINCTRL_SH_FUNC_GPIO`. Boot logs should show GPIO chip ranges when data registers and IRQ counts match. Use gpiolib tools or in-kernel consumers to request pins, toggle outputs, read inputs, and verify pinctrl direction transitions. IRQ mappings need board tests for every `gpio_irq` table entry. Legacy function-GPIO use should emit the deprecation notice once.
