# sources/distributed-fs/ceph-client/drivers/pinctrl/renesas/pinctrl-rzn1.c

## Purpose

`pinctrl-rzn1.c` implements the pinctrl and pinconf driver for Renesas RZ/N1 SoCs. The hardware has 170 configurable `PL_GPIO` pins and a multi-level mux model. Level 1 functions are encoded directly in each pin's level-1 config register; selecting level-2 muxing is represented by level-1 function `0xf` and a separate level-2 register. A third logical level selects MDIO sources for two MDIO channels and two MDIO-related level-2 functions. The driver exposes this as a normal Linux pinctrl device whose functions and groups are built entirely from device tree children.

## Important APIs, Types, And Functions

`struct rzn1_pinctrl_regs` models both level-1 and level-2 register banks: 170 per-pin `conf[]` words, a `status_protect` write-protect register at offset `0x400`, and two level-2 MDIO mux registers. `struct rzn1_pinctrl` stores the device, clock, pinctrl handle, mapped level-1/level-2 banks, physical addresses used by the write-protect protocol, current MDIO selections, and dynamically parsed function/group tables.

`rzn1_hw_set_lock()` implements the unusual lock protocol, writing the physical address of `status_protect` to itself, with bit 0 controlling unlock. `rzn1_set_hw_pin_func()` is the core mux writer. It recognizes compound MDIO function IDs from the DT binding, translates them into level-2 function numbers plus an MDIO source write, validates pin/function ranges, and updates level-1 and level-2 registers. `rzn1_set_mux()` wraps group programming by unlocking both levels, applying every pin's mux ID, then relocking.

Group and function discovery is device-tree-driven. `rzn1_pinctrl_parse_functions()` and `rzn1_pinctrl_parse_groups()` allocate arrays with `devm_kmalloc_array()`, parse `pinmux` cells into pin numbers and 7-bit function IDs, and assign group names and owning function names from DT node names. Runtime pinctrl ops are implemented by `rzn1_get_groups_count()`, `rzn1_get_group_name()`, `rzn1_get_group_pins()`, `rzn1_pmx_get_*()`, and `rzn1_dt_node_to_map()`.

Pin configuration support is in `rzn1_pinconf_get()`, `rzn1_pinconf_set()`, and group wrappers. Supported generic configs are pull-up, pull-down, bias-disable, drive-strength in mA, and high-impedance.

## Control Flow

Probe allocates state, initializes MDIO selections to `-1`, maps two MMIO resources for level 1 and level 2, calculates both write-protect physical addresses, enables the clock, assigns the descriptor name, parses DT functions/groups, registers/enables pinctrl, and leaves the clock enabled until remove. The driver does not register a GPIO chip; pin names are provided as pinctrl descriptors only.

DT parsing treats each direct child of the controller as a function. A function may contain a `pinmux` property directly, child groups with `pinmux`, or both. Each `pinmux` cell encodes the low 8 bits as the pin number and bits `[14:8]` as the mux/function selector. `rzn1_dt_node_to_map()` creates mux maps by looking up group names already parsed from DT and optionally attaches generic config maps to each group. Applying a state calls `rzn1_set_mux()` for the group and then pinconf group operations if present.

Pinconf get reads level-1 config bits for pull and drive strength, optionally level-2 config for high-impedance. Set modifies only the level-1 register bits it owns and unlocks level 1 around the write. High-impedance is represented as level-1 function `RZN1_FUNC_HIGHZ`.

## State And Persistence

Persistent runtime state is limited to hardware registers, parsed DT metadata, clock state, and software MDIO conflict tracking. `mdio_func[2]` records the selected source per MDIO channel and warns on conflicting settings, but the later write still occurs. There is no suspend/resume cache and no explicit register lock other than hardware write-protect. The comments state that `rzn1_set_hw_pin_func()` assumes serialization by callers; pinctrl core state application is expected to provide that serialization.

## Dependencies And Integration Points

The driver depends on `dt-bindings/pinctrl/rzn1-pinctrl.h` for compound function ID constants, platform MMIO resources for two banks, a clock, and OF child nodes describing all functions/groups. It integrates with pinctrl generic maps through `pinctrl-utils` helpers and with pinconf-generic parsing. It registers as compatible `renesas,rzn1-pinctrl` using `subsys_initcall`.

## Risks

Because all mux topology comes from DT, malformed group names, missing `pinmux`, or wrong pin/function cell encoding can make the driver register incomplete or incorrect functions. There is no spinlock around pinconf and mux writes beyond the hardware lock protocol; concurrent calls outside pinctrl's normal serialization would race. MDIO conflicts produce warnings instead of hard failure. Function ID range checks prevent values past the MDIO compound range, but DT can still request legal IDs that are electrically invalid for a board. Clock disable only occurs on remove or probe failure; no system PM handling is present.

## Test Signals

Test with representative DT nodes covering direct-function groups and child group nodes, level-1 functions, level-2 functions, MDIO compound functions, high-impedance, each pull mode, and drive strengths 4/6/8/12 mA. Negative tests should include missing `pinmux`, empty `pinmux`, unknown group names in pinctrl states, invalid pin numbers, unsupported drive strength, and conflicting MDIO selections.
