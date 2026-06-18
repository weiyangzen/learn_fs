# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-utils.c

## Purpose
Provides small exported helper routines used by pinctrl drivers when building dynamic `struct pinctrl_map` arrays and config arrays from firmware or device-tree parsing.

## Important APIs, Types, And Functions
Exports `pinctrl_utils_reserve_map()`, `pinctrl_utils_add_map_mux()`, `pinctrl_utils_add_map_configs()`, `pinctrl_utils_add_config()`, and `pinctrl_utils_free_map()`. The functions operate on `struct pinctrl_map`, `enum pinctrl_map_type`, and packed pinconf config arrays.

## Control Flow
`pinctrl_utils_reserve_map()` grows a map allocation with `krealloc_array()` when the requested reserve exceeds the current capacity and zeroes new slots. Add helpers append mux or config entries and increment `num_maps`. Config map insertion duplicates the config array with `kmemdup_array()`. `pinctrl_utils_add_config()` appends one packed config to a resizable `unsigned long` array. `pinctrl_utils_free_map()` walks map entries and frees duplicated config arrays for group or pin config maps before freeing the map itself.

## State And Persistence
The helpers only manage caller-owned heap allocations. They do not persist state outside the returned map/config pointers and updated counters.

## Dependencies And Integration Points
Used by driver `.dt_free_map` callbacks and custom DT parsers. It depends on core pinctrl map types, `pinctrl_dev` only for device-scoped error logging, and slab allocation helpers.

## Risks
Callers must keep `reserved_maps`, `num_maps`, and ownership conventions consistent. `pinctrl_utils_add_map_mux()` stores group/function pointers without duplicating strings, so their lifetime must exceed map use. Only config maps get deep-freed by `pinctrl_utils_free_map()`.

## Test Signals
Compile coverage with drivers using dynamic map construction, DT parsing tests that allocate mux plus config maps, allocation-failure injection, and leak checking around `dt_free_map` paths are the best signals.
