# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-equilibrium.h

## Purpose
This private header defines the register offsets, constants, and shared data structures used by the Equilibrium/LGM pinctrl implementation. It is tightly coupled to `pinctrl-equilibrium.c` and describes both the pinpad register block and per-bank GPIO register block.

## Important APIs, Types, and Definitions
Pinpad offsets include mux base, pull-up/down enable, slew, drive-current registers, open-drain, and availability. GPIO offsets include input/output, direction, external interrupt control, interrupt capture/control/enable/configuration, and set/clear direction/output registers. Constants define drive-current packing, GPIO interrupt trigger encodings, and `EQBR_GPIO_MODE`. `funcs_util_ops` enumerates phases of dynamic function construction. Structs are `gpio_irq_type`, `eqbr_pin_bank`, `eqbr_gpio_ctrl`, and `eqbr_pinctrl_drv_data`.

## Control Flow and State
The header contains no executable control flow. It defines the state layout consumed by the C file. `eqbr_pin_bank` persists per-bank pinpad base, ID, global pin base, pin count, and availability bitmap. `eqbr_gpio_ctrl` connects a generic gpiochip to a firmware node, pin bank, GPIO MMIO base, parent IRQ, and raw spinlock. `eqbr_pinctrl_drv_data` aggregates the pinctrl descriptor/device, parent base, bank array, GPIO controller array, and pinpad lock.

## Dependencies and Integration Points
The header assumes Linux kernel types from gpio, pinctrl, fwnode, and I/O headers included by the C file. It is not a public UAPI. The register macros are used directly by IRQ, GPIO, mux, pinconf, and bank-discovery paths in `pinctrl-equilibrium.c`.

## Risks
Because register offsets and structure fields are shared across all Equilibrium operations, any incorrect offset affects muxing, pad configuration, GPIO, and IRQ behavior. `PARSE_DRV_CURRENT` assumes two bits per pin and must stay aligned with `DRV_CUR_PINS` and `REG_DRCC`. Comments contain minor typos but no semantic issue. Structure layout changes must remain synchronized with generic gpiochip and pinctrl registration code.

## Test Signals
The header is validated indirectly by building and running `pinctrl-equilibrium.c`. Useful signals include correct pin bank discovery, availability bitmap enforcement, pinconf drive-current get/set, GPIO generic chip operation, IRQ trigger programming, and no sparse/compiler warnings for type use.
