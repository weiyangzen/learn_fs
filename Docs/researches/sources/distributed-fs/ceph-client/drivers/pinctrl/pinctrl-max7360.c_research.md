# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-max7360.c

## Purpose
Provides pinctrl/pinmux support for the MAX7360 MFD GPIO ports. It exposes eight port pins plus a two-pin rotary group and controls whether ports 6/7 are assigned to the rotary encoder function.

## Important APIs, Types, and Functions
The state container is `struct max7360_pinctrl`. Static data includes `max7360_pins`, single-port groups, `rotary_pins`, `max7360_groups`, and `max7360_functions` for `gpio`, `pwm`, and `rotary`. Pinctrl callbacks enumerate groups, and pinmux callbacks include `max7360_get_functions_count`, `max7360_get_function_name`, `max7360_get_function_groups`, and `max7360_set_mux`.

## Control Flow and State
Probe obtains the parent MFD regmap, allocates state, fills a `pinctrl_desc`, reuses the parent OF node for pinctrl phandles, and registers the controller. `max7360_set_mux` treats GPIO and PWM as equivalent for pinctrl purposes, only touching hardware when a group starts at port 6 or 7; selecting `rotary` sets `MAX7360_GPIO_CFG_RTR_EN`, while selecting other functions clears it. Persistent state is the parent regmap's `MAX7360_REG_GPIOCFG` bit.

## Dependencies and Integration Points
Depends on the MAX7360 MFD parent, `linux/mfd/max7360.h` register definitions, the parent regmap, platform-device MFD topology, and pinctrl generic OF parsing. `.strict = true` asks pinctrl to avoid conflicting mux/GPIO ownership.

## Risks and Test Signals
Risks include parent-node reuse confusing consumers if the MFD topology changes, GPIO/PWM equivalence hiding PWM ownership conflicts outside this driver, and rotary enable affecting both ports 6 and 7 as a pair. Test signals include selecting rotary and GPIO/PWM states through pinctrl, regmap readback of `MAX7360_GPIO_CFG_RTR_EN`, DT phandle resolution through the parent node, and integration tests with the MAX7360 GPIO/PWM/rotary users.
