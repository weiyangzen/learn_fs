# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-cy8c95x0.c

## Purpose
This I2C driver supports Cypress CY8C95x0 GPIO expander variants with 20, 40, or 60 pins. It provides gpiolib, pinctrl, pinmux between GPIO and PWM, generic pinconf drive/bias/output/input controls, optional reset and regulator handling, ACPI/DMI IRQ quirks, regmap-backed access to paged registers, and nested interrupt delivery.

## Important APIs, Types, and Functions
`struct cy8c95x0_pinctrl` is the central state: regmap, IRQ and I2C mutexes, interrupt trigger/mask bitmaps, push-pull bitmap, hardware pin map bitmap, port count, gpio chip, pinctrl descriptor, total pin count, and reset GPIO. Register helper families include `cy8c95x0_regmap_update_bits_base`, `cy8c95x0_regmap_write_bits`, `cy8c95x0_regmap_update_bits`, `cy8c95x0_regmap_read_bits`, plus bitmap multi-register helpers `cy8c95x0_write_regs_mask` and `cy8c95x0_read_regs_mask`. GPIO callbacks cover direction, value, multiple get/set, pin ranges, and pinconf. IRQ callbacks include mask/unmask, bus lock/sync, type, shutdown, `cy8c95x0_irq_pending`, and `cy8c95x0_irq_handler`. Probe and detection are `cy8c95x0_probe` and `cy8c95x0_detect`.

## Control Flow and State
Probe allocates state, derives pin count from match data, configures a runtime regmap range sized for the variant, enables `vdd`, toggles optional reset, initializes regmap, clears the push-pull bitmap, builds a bitmap map that skips the four-bit gap in GPort2, initializes the I2C mutex, applies the Galileo ACPI IRQ quirk if matched, optionally initializes IRQ handling, registers pinctrl, and registers the gpiochip. Regmap virtual ranges map muxed registers behind `PORTSEL` into a flat address space; accessors serialize I2C and translate direct, quick-path, and muxed registers. Write-clear drive mode registers update regcache manually to mirror hardware clearing of conflicting modes.

## State and Persistence Behavior
Persistent hardware state is in direct and port-selected CY8C95x0 registers. Driver-side persistent state includes regcache, IRQ masks and trigger bitmaps, the `push_pull` bitmap used to force High-Z when returning push-pull pins to input, and the `map` bitmap used for scatter/gather around the GPort2 gap. IRQ bus sync writes the mask bitmap, forces newly unmasked IRQ lines to input, and unlocks. Level IRQ emulation loops nested IRQ handling while the GPIO remains active.

## Dependencies and Integration Points
The driver integrates with I2C, SMBus detection, regmap ranges/cache, regulator, optional reset GPIO, ACPI, DMI, OF, gpiolib, pinctrl, pinmux, pinconf, and IRQ domains. Compatible strings include `cypress,cy8c9520`, `cypress,cy8c9540`, and `cypress,cy8c9560`; ACPI ID `INT3490` maps to 40 pins.

## Risks
Paged register handling is complex; direct `PORTSEL` writes outside the helpers would desynchronize cache and hardware. Interrupt status registers are precious, so debug or cache reads can clear events. Level-trigger emulation uses while loops that can spin if the input remains asserted and nested handlers do not clear the source. `cy8c95x0_gpio_get_value` returns 0 on read error after logging elsewhere, which can hide I2C failures. The GPort2 gap requires every multi-line bitmap path to use scatter/gather correctly.

## Test Signals
Tests should cover all variants and pin counts, regmap range sizing, reset/regulator sequencing, GPIO single and multiple operations across the GPort2 gap, PWM muxing side effects, pinconf drive/bias/input/output state including push-pull-to-input High-Z behavior, IRQ edge and level delivery, ACPI Galileo IRQ mapping, and SMBus detect names.
