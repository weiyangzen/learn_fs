# sources/distributed-fs/ceph-client/drivers/pinctrl/berlin/berlin.c

Purpose: Shared Marvell Berlin pinctrl core that turns static per-SoC group/function descriptors into a Linux pinctrl/pinmux device.

Important APIs/types/functions: `struct berlin_pinctrl` stores regmap, descriptor, generated `struct pinfunction` array, and `pinctrl_dev`. `berlin_pinctrl_probe()` obtains a parent syscon regmap; `berlin_pinctrl_probe_regmap()` accepts a caller-supplied regmap. `berlin_pinctrl_build_state()` builds unique functions and group membership. `berlin_pinmux_set()` writes selected mux values.

Control flow: DT parsing requires `function` and `groups` properties, reserves maps, and adds one mux map per group. During probe, the core allocates state, stores match descriptor, synthesizes function tables, registers the pinctrl device, and then services pinmux requests by finding the function in the selected group and updating a masked regmap field.

State and persistence: generated function tables are heap/devm allocated for the device lifetime. Hardware state persists in regmap-backed syscon/MMIO registers. No separate conflict tracking or pinconf state exists.

Dependencies/integration: relies on Linux pinctrl, pinmux, pinctrl-utils, regmap, OF, syscon parent nodes, and per-SoC descriptors from `berlin.h`.

Risks: `max_functions += 1 << (bit_width + 1)` is an over-allocation heuristic; very large bit widths would waste memory but tables use small widths. `krealloc(... nfunctions * sizeof(...))` with zero functions would be fragile, though descriptors contain valid functions. No get_group_pins callback is implemented, matching group-name-only Berlin binding style.

Test signals: unit-style DT parsing with missing properties should return `-EINVAL`; boot any Berlin SoC and validate generated function counts, function-to-group lists, and regmap bit updates for a sample group.
