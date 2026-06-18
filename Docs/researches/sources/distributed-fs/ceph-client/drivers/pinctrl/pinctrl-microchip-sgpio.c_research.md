# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-microchip-sgpio.c

## Purpose
Implements Microchip/Microsemi serial GPIO pinctrl and GPIO support for Luton, Ocelot, and Sparx5-family SoCs. It registers separate input and output banks, configures the serial bitstream and clock, maps two-cell port/bit GPIO specifiers to linear pins, and optionally exposes input-bank IRQs on Sparx5.

## Important APIs, Types, and Functions
Key types are `struct sgpio_properties`, `struct sgpio_priv`, `struct sgpio_bank`, and `struct sgpio_port_addr`. Hardware helpers include `sgpio_pin_to_addr`, `sgpio_addr_to_pin`, `sgpio_get_addr`, `sgpio_readl`, `sgpio_writel`, `sgpio_clrsetbits`, `sgpio_configure_bitstream`, `sgpio_configure_clock`, and `sgpio_single_shot`. GPIO/pinconf paths include `sgpio_output_set`, `sgpio_output_get`, `sgpio_input_get`, `sgpio_pinconf_get`, `sgpio_pinconf_set`, `microchip_sgpio_direction_input`, `microchip_sgpio_direction_output`, `microchip_sgpio_get_value`, and `microchip_sgpio_of_xlate`. IRQ logic is in `microchip_sgpio_irq_set_type`, mask/unmask/ack helpers, and `sgpio_irq_handler`.

## Control Flow and State
Probe resets the switch block if available, reads the input clock and desired bus frequency, creates an Ocelot regmap, reads enabled port ranges from `microchip,sgpio-port-ranges`, requires exactly two child banks, registers each bank as both pinctrl and gpiochip, validates matching bank sizes, then programs bitstream width, clock divider, clears all port config registers, and enables the selected ports. Output changes update a three-bit source field for the selected port/bit and trigger a single-shot burst on architectures that need manual refresh. Input values are read from `REG_INPUT_DATA` indexed by bit. IRQ state is hardware-resident in polarity, trigger, ack, enable, and ident registers and protected by a spinlock while reprogramming type.

## Dependencies and Integration Points
Depends on platform resources, clocks, optional reset controls, Ocelot regmap helper, firmware child nodes for input/output banks, generic pinconf DT parsing, gpiolib, and IRQ chaining for Sparx5. OF compatibles select architecture-specific register offsets and bitfield layouts: `microchip,sparx5-sgpio`, `mscc,luton-sgpio`, and `mscc,ocelot-sgpio`.

## Risks and Test Signals
Risks include architecture-specific bitfield mistakes, invalid port-range parsing, bank child ordering assumptions, output single-shot timeout at slow bus frequencies, off-by-one validation in OF GPIO translation, and IRQ enable/type races. Test signals include input/output bank registration with expected names and GPIO counts, GPIO specifier translation for boundary ports/bits, output readback plus visible serial update, clock divider validation, Sparx5 IRQ tests for rising/falling/both/high/low, and boot tests on all three architecture property sets.
