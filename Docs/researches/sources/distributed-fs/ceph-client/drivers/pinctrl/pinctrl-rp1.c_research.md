# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-rp1.c

## Purpose
This driver supports the Raspberry Pi RP1 GPIO unit as a combined pinctrl, pinmux, pinconf, GPIO, and GPIO-IRQ provider. It exposes 54 GPIOs split across three RP1 IO banks, supports both modern generic pinctrl bindings and legacy Broadcom-style `brcm,pins` bindings, maps RP1 alternate functions to Linux pinctrl functions/groups, and programs GPIO, RIO, interrupt-enable, and pad-control register blocks through regmap fields.

## Important APIs, Types, And Functions
`struct rp1_pinctrl` is the controller state: three MMIO bases, parent IRQs, per-pin `struct rp1_pin_info`, registered `pinctrl_dev`, embedded `gpio_chip`, GPIO range, and one raw spinlock per IO bank. `struct rp1_pin_info` stores the logical GPIO number, bank, bank-local offset, current IRQ type, and arrays of `regmap_field` handles for GPIO control, RIO value/direction, interrupt enable, and pad controls. Static tables define pins, peripheral groups, functions, per-pin function-select mappings, legacy function maps, and the three IO-bank register-offset descriptions.

Core helpers are `rp1_get_fsel()`, `rp1_set_fsel()`, `rp1_get_dir()`, `rp1_set_dir()`, `rp1_get_value()`, and `rp1_set_value()`. GPIO callbacks wrap these helpers. IRQ support is implemented by `rp1_gpio_irq_handler()`, `rp1_gpio_irq_config()`, `rp1_irq_set_type()`, `rp1_gpio_irq_set_type()`, `rp1_gpio_irq_ack()`, and `rp1_gpio_irq_set_affinity()`. Pin parsing and muxing use `rp1_pctl_dt_node_to_map()`, `rp1_pctl_legacy_map_func()`, `rp1_pctl_legacy_map_pull()`, `rp1_pmx_set()`, and `rp1_pmx_free()`. Pinconf operations are `rp1_pinconf_set()`, `rp1_pinconf_get()`, and group wrappers.

## Control Flow
Probe maps GPIO, RIO, and PADS resources, creates regmaps with explicit readable/writable ranges, and for each bank/pin allocates the needed `regmap_field` objects with `rp1_gen_regfield()`. It registers the pinctrl device, configures the embedded `gpio_irq_chip` with up to three parent IRQs parsed from DT, registers the GPIO chip, and adds a pinctrl GPIO range.

GPIO direction output writes the value, sets RIO output enable, and selects GPIO function. Direction input clears output enable and selects GPIO function. `rp1_set_fsel()` enables pad input and output by default, selects peripheral output overrides for normal functions, disables output-enable override for `none`, and writes the hardware function-select value. Pinctrl muxing translates abstract function names back to the FSEL slot supported by each pin, then programs every pin in the selected group.

The IRQ parent handler determines which IO bank fired, reads the bank interrupt status register, clears the per-pin latched event, and dispatches mapped child IRQs. Type configuration clears all interrupt flags, sets the requested edge/level bits, records `pin->irq_type`, and installs edge or level handlers under the bank raw spinlock. Legacy DT parsing converts `brcm,function` and `brcm,pull` arrays into mux and config maps, with scalar-or-per-pin validation.

## State And Persistence
Software state includes allocated regmap fields, the parent IRQ array, per-pin IRQ type, and the module parameter `persist_gpio_outputs`. Pin mux, GPIO direction/value, interrupt type/enable, and pad configuration persist in RP1 registers. When a pin is freed, `rp1_pmx_free()` normally returns it to GPIO input; if `persist_gpio_outputs` is true and the pin is already GPIO, it leaves outputs in place. There are no explicit suspend/resume callbacks in this file.

## Dependencies And Integration Points
The driver depends on platform MMIO resources, OF IRQ parsing, regmap and regmap-field APIs, pinctrl/pinmux/pinconf core APIs, gpiolib with hierarchical parent IRQ support, and Raspberry Pi RP1 DT compatible `raspberrypi,rp1-gpio`. It integrates with both modern function/group-based pinctrl consumers and older Raspberry Pi/Broadcom overlays using `brcm,pins`, `brcm,function`, and `brcm,pull`.

## Risks And Test Signals
Risk centers on table correctness and bank-local indexing. The parent IRQ handler reads a 32-bit bank status and iterates set bits as bank-local offsets, so mapping must match `rp1_iobanks`. Legacy mapping has strict array-length rules and can reject overlays with mismatched `brcm,function` or `brcm,pull` counts. The static `rp1_pinctrl_data` means the driver expects one controller instance. `rp1_pinconf_get()` relies on all pad drive encodings being known; invalid hardware values would leave `arg` undefined. Test signals include probe with one, two, and three parent IRQs, GPIO value/direction on all banks, mux selection for direct FSEL functions and named peripheral functions, legacy DT mappings, all IRQ trigger types and affinity delegation, pad pull/drive/slew/Schmitt get/set, `persist_gpio_outputs` free behavior, and invalid pin/function rejection.
