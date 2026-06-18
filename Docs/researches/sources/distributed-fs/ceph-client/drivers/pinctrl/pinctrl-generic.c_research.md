# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-generic.c

## Purpose

This file provides a helper for pinctrl drivers that do not predefine pin groups and functions in C. It parses device-tree pin nodes that provide numeric `pins` and a `function`, dynamically creates generic pin groups and pinmux functions, and adds pinmux plus optional pinconf mappings for the pinctrl core.

The exported API is `pinctrl_generic_pins_function_dt_node_to_map()`.

## Important APIs, Types, and Data

- `pinctrl_generic_pins_function_dt_subnode_to_map()` handles one DT node containing a `pins` array and `function` string.
- `pinctrl_generic_pins_function_dt_node_to_map()` handles either a single pins node or a parent node with multiple child pins nodes.
- It uses `pinctrl_utils_reserve_map()`, `pinctrl_utils_add_map_mux()`, and `pinctrl_utils_add_map_configs()` to build `struct pinctrl_map` entries.
- It uses `pinctrl_generic_add_group()` to create groups and `pinmux_generic_add_function()` to create functions.
- It uses `pinconf_generic_parse_dt_config()` to parse generic pin configuration properties.

## Control Flow

The top-level function initializes `*maps = NULL` and `*num_maps = 0`. If the node itself has a `pins` property, it allocates a one-entry `group_names` array, parses the node as a single group, then adds one generic function named after the node.

If the node lacks `pins`, it is treated as a parent. The function first counts available children, allocates `group_names` for that count, then iterates children with `for_each_available_child_of_node_scoped()`. Each child is parsed into a group and map entries, and the group name is appended. Finally, one generic function named after the parent is registered with all collected groups.

The subnode parser validates that `pins` contains at least one u32, builds a group name from `parent.child`, allocates arrays for pin numbers and per-pin function pointers, reads each pin index, reads the node's `function` string, reserves and adds one mux map, registers the group with the pins and function array, parses optional pin configs, and adds a group config map if any configs exist.

On errors after maps have been allocated, the top-level function frees the map array with `pinctrl_utils_free_map()` before returning `dev_err_probe()`.

## State and Persistence Behavior

The helper creates persistent generic groups and functions inside the pinctrl device's generic pinctrl/pinmux data structures. Allocations for group names, pin arrays, function arrays, and parent group-name arrays are device-managed through `devm_*`, while parsed pinconf configs are freed after being copied into pinctrl maps.

There is no hardware state in this file. Hardware effects occur later when the pinctrl core applies the maps through the consuming driver's pinmux and pinconf operations.

## Dependencies and Integration Points

- Device tree nodes must provide `pins` as u32 pin numbers and `function` as a string.
- Drivers using this helper must use generic pinctrl/pinmux infrastructure capable of storing dynamically added groups and functions.
- Generic pinconf properties are parsed by `pinconf_generic_parse_dt_config()`.
- The helper is exported with `EXPORT_SYMBOL_GPL`, so GPL-compatible pinctrl drivers can use it as their `.dt_node_to_map` implementation.

## Risks and Edge Cases

- `reserve` is always `1`, and the helper calls `pinctrl_utils_reserve_map()` separately for mux and config maps. That is correct but relies on the utility growing the map array incrementally.
- The same `function` string is read once per pin into every slot of the `functions` array. This matches the generic group API shape but does not support per-pin alternate function strings inside one group.
- If a parent node has no available children, the function adds a generic function with zero groups. That may be accepted by the generic pinmux core but is likely not useful.
- The single-node path names the group as `np.np` because parent and child arguments are the same node in the helper call. That is intentional from current formatting but can surprise binding authors inspecting debug output.
- The helper expects numeric pin IDs rather than named pins, so it depends on stable pin numbering in the consuming driver.

## Test Signals

- DT states with one node containing `pins` and `function` should create one mux map and optional group config map.
- DT states with a parent and multiple available children should create one generic function named after the parent and one group per child.
- Invalid or missing `pins` should log `invalid pinctrl group` and fail.
- Missing `function`, malformed `pins`, or unsupported pinconf properties should return errors and free any already allocated maps.
- Drivers using the helper should show dynamically added group/function names in pinctrl debugfs and should apply configs through their own pinconf ops.
