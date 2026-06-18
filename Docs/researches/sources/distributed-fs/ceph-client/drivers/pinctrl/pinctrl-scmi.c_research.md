# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-scmi.c

## Purpose
This driver exposes pins, groups, functions, muxing, and pin configuration supplied by firmware through the ARM SCMI pinctrl protocol as a Linux pinctrl provider. Instead of programming local MMIO registers, it delegates all enumeration, mux, request/free, and configuration operations to `struct scmi_pinctrl_proto_ops` obtained from the SCMI core.

## Important APIs, Types, And Functions
`struct scmi_pinctrl` stores the device, SCMI protocol handle, registered pinctrl device, descriptor, lazily populated function cache, and function count. Pinctrl operations call SCMI protocol methods: `count_get()`, `name_get()`, `group_pins_get()`, and `function_groups_get()`. Pinmux operations are `pinctrl_scmi_func_set_mux()`, `pinctrl_scmi_request()`, and `pinctrl_scmi_free()`.

Pinconf translation is centralized in `pinctrl_scmi_map_pinconf_type()`, with get/set wrappers mapping `PIN_CONFIG_LEVEL` to input or output value. `pinctrl_scmi_pinconf_get()` and group get call `settings_get_one()`. `pinctrl_scmi_pinconf_set()` and group set build arrays of SCMI config types/values and call `settings_conf()`. `pinctrl_scmi_get_pins()` builds the pin descriptor table from SCMI pin names. `scmi_pinctrl_probe()` obtains protocol ops, initializes the descriptor, allocates function cache storage, registers, and enables the pinctrl device.

## Control Flow
Probe first rejects devices without an SCMI handle and blocklists several NXP machine compatibles. It obtains the SCMI pinctrl protocol and protocol handle with `devm_protocol_get()`, allocates driver state, fills pinctrl/pinmux/pinconf ops, reads all pin names from firmware, registers the pinctrl provider with `devm_pinctrl_register_and_init()`, allocates one `struct pinfunction` entry per SCMI function, and calls `pinctrl_enable()`.

Group and function names are fetched on demand from firmware. Function-to-group lists are cached the first time `get_function_groups` is called: SCMI returns group IDs, the driver resolves each ID to a group name, stores the allocated name pointer array in `pmx->functions[selector]`, and reuses it thereafter. Pin and group configs are mapped from Linux generic pinconf parameters to SCMI config IDs. For more than four configs, temporary arrays are heap allocated; four or fewer use stack arrays. `PIN_CONFIG_PERSIST_STATE` is silently skipped for per-pin set.

## State And Persistence
The driver keeps minimal software state: pin descriptors allocated at probe and lazily populated function group arrays. Hardware or firmware state is external to Linux and persists according to platform SCMI firmware policy. There are no local MMIO registers, no GPIO chip, and no suspend/resume hooks. Names returned by SCMI are treated as firmware-owned memory.

## Dependencies And Integration Points
It depends on the SCMI core, `SCMI_PROTOCOL_PINCTRL`, generic pinctrl/pinmux/pinconf infrastructure, optional OF mapping via `pinconf_generic_dt_node_to_map_all()`, and the SCMI device table entry `{ SCMI_PROTOCOL_PINCTRL, "pinctrl" }`. It is a firmware-mediated integration point for platforms where the secure or system controller owns pin programming.

## Risks And Test Signals
Correctness depends on firmware faithfully reporting counts, names, group IDs, and supported configuration types. The file uses a global `pinctrl_ops` pointer, so multiple SCMI pinctrl devices would share the last protocol-ops pointer even though protocol operations are expected to be common. Per-pin set skips `PIN_CONFIG_PERSIST_STATE`, but group set does not special-case it. Heap allocation paths for large config lists need cleanup on mapping failures. Test signals include probe with nonzero pin/function/group counts, function group caching, mux set calls reaching firmware, request/free calls, all mapped generic pinconf get/set types, `PIN_CONFIG_LEVEL` input/output mapping, conversion of `-EOPNOTSUPP` to `-ENOTSUPP`, large config arrays beyond four entries, OF pinconf map parsing, and machine blocklist rejection.
