# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-lynxpoint.c

## Purpose

`pinctrl-lynxpoint.c` is a legacy Intel Lynxpoint PCH GPIO/pinctrl driver. It reuses some common data structures and helper exports from `pinctrl-intel.h`, but implements its own IO-port register access, pinctrl ops, pinconf ops, gpiochip, IRQ handling, and resume behavior because Lynxpoint's register layout differs from modern PADCFG-based controllers.

## Important APIs, Types, And Functions

Static topology is `lptlp_pins`, `lptlp_gpps`, `lptlp_communities`, and `lptlp_soc_data`. Register helpers include `lp_gpio_reg()`, `lp_gpio_acpi_use()`, and `lp_gpio_ioxapic_use()`. Runtime operations are implemented by `lp_pinmux_set_mux()`, `lp_gpio_request_enable()`, `lp_gpio_disable_free()`, `lp_gpio_set_direction()`, `lp_pin_config_get()`, `lp_pin_config_set()`, GPIO get/set/direction functions, IRQ functions (`lp_gpio_irq_handler()`, `lp_irq_ack()`, `lp_irq_enable()`, `lp_irq_disable()`, `lp_irq_set_type()`), `lp_gpio_probe()`, and `lp_gpio_resume()`.

## Control Flow

The driver registers at subsystem init under name `lp_gpio` and matches ACPI IDs `INT33C7` and `INT3437`. Probe allocates `struct intel_pinctrl`, registers a pinctrl device, maps an IORESOURCE_IO region through `devm_ioport_map()`, copies the single community template, initializes the gpiochip for 95 GPIOs, optionally wires a parent IRQ with chained handling, and registers the gpiochip. IRQ dispatch scans bitmapped interrupt status/enable registers in 32-bit chunks and forwards pending bits to the gpiochip IRQ domain.

## State And Persistence

Lynxpoint has 95 GPIOs, bitmapped ownership/IRQ/status/enable registers, and per-pin CONFIG1/CONFIG2 registers. Runtime state is stored in `struct intel_pinctrl`, but no common `intel_pinctrl_pm_ops` context is used. Resume only re-enables input sensing for requested GPIOs because some hardware clears that bit across suspend.

## Dependencies And Integration Points

The file integrates with ACPI, platform IO resources, pinctrl, pinmux, pinconf, gpiolib, irqchip, and the common `intel_gpio_add_pin_ranges()`/`intel_get_community()` helpers. It uses firmware ownership bits to reject IRQ use of ACPI-reserved pins. It also handles IOxAPIC redirection constraints for specific GPIO ranges.

## Risks

This path is easy to confuse with the modern Intel core, but it does not use PADCFG register definitions or common probe/PM code. `lp_gpio_request_enable()` appears to write `(value & USE_SEL_MASK) | USE_SEL_GPIO`, preserving only mode bits and potentially dropping unrelated CONFIG1 bits when forcing GPIO mode; that behavior is existing code and should be reviewed carefully before changes. IRQ mask/unmask are empty because enable/disable control the hardware, so irqchip semantics must remain consistent with gpiolib expectations.

## Test Signals

Probe should succeed with an IO port resource and ACPI match. Debugfs should show Lynxpoint CONFIG1/CONFIG2 values and ACPI ownership. GPIO request/free should enable/disable input sensing. IRQ tests should reject ACPI-owned pins, program rising/falling/level trigger bits, and dispatch chained parent interrupts. Resume tests should confirm requested GPIO input sensing is restored.
