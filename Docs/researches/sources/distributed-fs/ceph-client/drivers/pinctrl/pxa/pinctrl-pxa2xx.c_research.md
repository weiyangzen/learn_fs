# sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/pinctrl-pxa2xx.c

## Purpose
Implements the common Marvell PXA2xx pinctrl, pinmux, and pinconf logic used by PXA25x and PXA27x table drivers.

## Important APIs, Types, And Functions
Important operations include group callbacks `pxa2xx_pctrl_get_*`, mux callbacks `pxa2xx_pmx_set_mux()` and `pxa2xx_pmx_gpio_set_direction()`, pinconf callbacks `pxa2xx_pconf_group_get/set()`, state builders `pxa2xx_build_functions()`, `pxa2xx_build_groups()`, `pxa2xx_build_state()`, and exported initializer `pxa2xx_pinctrl_init()`.

## Control Flow
Initialization allocates driver state, copies register base arrays, builds one group per pin, derives a unique function list by scanning all chip-specific pin descriptors, builds each function's group list by matching names, and registers the pinctrl device. Mux selection finds the descriptor for the requested pin/function, writes alternate-function bits in the GAFR bank, and updates direction in GPDR. GPIO direction changes only update GPDR. Low-power pinconf reads/writes per-pin sleep-state bits in PGSR.

## State And Persistence
State persists in PXA hardware registers: GAFR for alternate functions, GPDR for direction, and PGSR for sleep GPIO state. Driver-built state includes devm-managed pin descriptors, groups, functions, group lists, base register arrays, and a spinlock protecting register updates.

## Dependencies And Integration Points
Integrates with pinctrl, pinmux, generic pinconf, optional OF DT parsing via `pinconf_generic_dt_node_to_map_all`, and chip-specific PXA25x/PXA27x wrappers. Exports `pxa2xx_pinctrl_init()` for those wrappers.

## Risks
Function identity is string-based and per-pin descriptors can include duplicate names with different mux values. Groups are single-pin only, so multi-pin peripheral states rely on selecting the same function on multiple pin groups. Register-bank array sizing uses `roundup(maxpin, 16/32)` as a count driver, which overallocates but relies on chip wrappers filling enough base pointers.

## Test Signals
Signals include generated function/group listings, mux writes to GAFR/GPDR for representative pins, GPIO direction calls, PGSR low-power config set/get, DT map parsing, and concurrent mux operations under spinlock/lockdep.
