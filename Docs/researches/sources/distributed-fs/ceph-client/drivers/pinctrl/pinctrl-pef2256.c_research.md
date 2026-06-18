# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pef2256.c

## Purpose
This is the pinctrl/pinmux driver for the Lantiq/Infineon PEF2256 FALC56 line interface. It exposes the four receive port pins and four transmit port pins as one-pin groups and programs their Port Configuration registers to select line-interface signals or, on newer silicon, GPIO-style functions.

## Important APIs, Types, And Functions
`struct pef2256_pinreg_desc` stores the register offset and field mask for one pin group. `struct pef2256_function_desc` maps a function name to allowed groups and the encoded register value. `struct pef2256_pinctrl` holds device, parent regmap, detected hardware version, local `pinctrl_desc`, and the version-specific function table. Pinctrl ops are `pef2256_get_groups_count()`, `pef2256_get_group_name()`, and `pef2256_get_group_pins()`. Pinmux ops are `pef2256_get_functions_count()`, `pef2256_get_function_name()`, `pef2256_get_function_groups()`, and `pef2256_set_mux()`.

Version-specific static tables define v1.2 and v2.x pin descriptors and functions. `pef2256_reset_pinmux()` writes a safe initial mux to PC1 through PC4, `pef2256_register_pinctrl()` selects the table for the detected version and registers pinctrl, and `pef2256_pinctrl_probe()` wires the driver to the parent PEF2256 MFD/framer device.

## Control Flow
Probe allocates driver state, assigns the child device fwnode from the parent, retrieves the parent `struct pef2256`, fetches its regmap and version through exported helpers, stores platform driver data, resets all port configuration registers to a safe non-conflicting mux, and registers pinctrl. Group enumeration is direct: one group equals one pin. Function enumeration is selected by hardware version; v2.x adds LOS and GPIO-like GPI/GPOH/GPOL choices that v1.2 lacks.

`pef2256_set_mux()` receives a function selector and group selector from pinctrl. It fetches the group's `pef2256_pinreg_desc` from `pinctrl_pin_desc.drv_data`, gets the selected function's pre-encoded value, and calls `regmap_update_bits()` on the relevant PC register field. For functions allowed on both RP and XP groups in v2.x, the encoded value combines both field positions; the group's mask ensures only the relevant nibble is written.

## State And Persistence
The driver has minimal software state: detected version and selected static tables. Pin mux state persists in PEF2256 PC1-PC4 hardware registers. The reset function intentionally overwrites reset defaults because the hardware reset values would mux all RP pins to SYPR and all XP pins to SYPX, while only one pin can validly drive each such signal. No runtime cache of mux state is kept.

## Dependencies And Integration Points
This driver depends on the parent PEF2256 framer/MFD object, `pef2256_get_regmap()`, `pef2256_get_version()`, Linux regmap, platform device registration, and the pinctrl/pinmux core. It uses `pinconf_generic_dt_node_to_map_pin()` for DT mapping despite implementing mux-only behavior; no pinconf ops are registered. The platform driver name is `lantiq-pef2256-pinctrl`.

## Risks And Test Signals
The safe reset writes ignore `regmap_write()` return values, so bus failures during reset are not reported before registration. Function value correctness is version-sensitive, especially because v1.2 RP and XP masks differ from v2.x masks. The compound GPIO function encodings rely on masks to discard irrelevant bits. There is no OF match table in this child driver; successful binding depends on the parent creating the platform device with the expected name and data.

Useful tests include probe for both PEF2256 v1.2 and v2.x, verification that PC1-PC4 are reset to the intended safe values, muxing every RP-only and XP-only function onto each legal group, confirming v2.x GPI/GPOH/GPOL work on all eight groups, checking unsupported function/group combinations are not emitted by pinctrl group lists, and forcing regmap failures to validate propagation from `set_mux()` and registration.
