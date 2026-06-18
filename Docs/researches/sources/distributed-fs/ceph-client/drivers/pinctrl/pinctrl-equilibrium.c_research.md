# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-equilibrium.c

## Purpose
This platform driver implements Intel LGM/Equilibrium SoC pinctrl, pinmux, pinconf, GPIO, and GPIO IRQ support. Unlike table-only SoC drivers, it discovers GPIO child nodes and pin groups/functions from firmware, builds generic pinctrl groups/functions dynamically, and registers generic gpiochips for each bank.

## Important APIs, Types, and Functions
The driver uses private types from `pinctrl-equilibrium.h`: pin banks, GPIO controllers, IRQ type descriptors, and driver data. IRQ helpers include mask/unmask/ack/mask_ack, `eqbr_irq_set_type`, and `eqbr_irq_handler`. GPIO setup is split across `gpiochip_setup` and `gpiolib_reg`. Pinctrl and mux helpers include `find_pinbank_via_pin`, `eqbr_set_pin_mux`, `eqbr_pinmux_set_mux`, and `eqbr_pinmux_gpio_request`. Pinconf is handled by `eqbr_pinconf_get`, `eqbr_pinconf_set`, and group wrappers. Dynamic DT construction uses `funcs_utils`, `eqbr_build_functions`, and `eqbr_build_groups`. Discovery/registration paths are `pinbank_init`, `pinbank_probe`, `pinctrl_reg`, and `eqbr_pinctrl_probe`.

## Control Flow and State
Probe allocates driver data, maps the parent pinctrl MMIO resource, discovers available GPIO nodes named `gpio`, initializes pin banks from each node's `gpio-ranges` and `REG_AVAIL`, registers the pinctrl device, builds groups from child node `groups`, `pins`, and `pinmux` properties, builds functions from child node `function` properties, enables pinctrl, registers each gpiochip, and stores drvdata. Muxing resolves each pin to a bank, validates availability using `aval_pinmap`, and writes the mux value to the per-pin register. GPIO request forces mux value `EQBR_GPIO_MODE`.

## State and Persistence Behavior
Pinctrl state persists in parent pinpad registers spaced by `PAD_REG_OFF`; GPIO state persists in each child GPIO MMIO block. Driver state records bank base pins, bank widths, availability bitmaps, GPIO controller mappings, and fwnodes. Raw spinlocks protect pinpad and GPIO register writes. Pinconf supports pull-up, pull-down, open-drain, drive strength, slew rate, and output enable. Output-enable pinconf delegates to the associated gpiochip direction-output callback.

## Dependencies and Integration Points
The driver depends on OF child nodes, `gpio-ranges`, MMIO resources, IRQ mapping, generic gpio-chip helpers, pinctrl generic group/function APIs, pinmux generic APIs, pinconf DT mapping, and compatible `intel,lgm-io`. GPIO child nodes can opt into interrupt-controller behavior.

## Risks
`pinbank_probe` ignores the return value from `pinbank_init`, so a malformed GPIO child can leave partially initialized bank data and fail later less clearly. It iterates all available nodes named `gpio` globally rather than restricting to children of the pinctrl node, which can over-count unrelated GPIO nodes in a broader DT. `eqbr_pinmux_set_mux` does not propagate errors from `eqbr_set_pin_mux` inside its loop. Group/function parsing stores property value pointers as names and assumes property lifetimes remain valid. Drive-strength set masks two-bit values but does not validate the requested argument range.

## Test Signals
Validation should include DTs with multiple GPIO child banks, correct `gpio-ranges`, unavailable pins in `REG_AVAIL`, dynamic group/function construction from child properties, GPIO request muxing, pinconf read/write for all supported configs, GPIO direction/output behavior through generic chips, chained IRQ delivery for edge and level types, and malformed DT cases for missing ranges or bad pin IDs.
