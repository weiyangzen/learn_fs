# sources/distributed-fs/ceph-client/drivers/mfd/syscon.c

## Purpose
`syscon.c` provides shared regmap access to system-controller MMIO regions described by device tree. It lazily registers syscon regmaps, supports lookup by compatible or phandle, and allows external drivers to register a regmap for a node.

## Important APIs, Types, and Functions
`struct syscon` tracks a device node, regmap, optional reset, and list entry. Internal registration is `of_syscon_register()` and lookup is `device_node_get_regmap()`. Exported APIs include `of_syscon_register_regmap()`, `device_node_to_regmap()`, `syscon_node_to_regmap()`, `syscon_regmap_lookup_by_compatible()`, `syscon_regmap_lookup_by_phandle()`, `syscon_regmap_lookup_by_phandle_args()`, and `syscon_regmap_lookup_by_phandle_optional()`.

## Control Flow
Lookup functions find or parse a device node, then call `syscon_node_to_regmap()` or `device_node_to_regmap()`. `device_node_get_regmap()` searches the global list under `syscon_list_lock`; if absent and creation is allowed, `of_syscon_register()` maps the resource, configures endianness, IO width, optional hwspinlock, regmap name/stride/value width/max register, creates the regmap, optionally attaches clock/reset resources, deasserts reset, and appends it to the list.

## State and Persistence
Global state is `syscon_list` protected by `syscon_list_lock`. Created regmaps and MMIO mappings persist for system lifetime; there is no unregister path for lazily created syscons. Externally registered regmaps are also stored in the list.

## Dependencies and Integration Points
It depends on OF address/phandle parsing, MMIO regmap, clocks, reset controls, optional hardware spinlocks, and many platform drivers that use syscon phandles for shared control registers.

## Risks and Edge Cases
`syscon_node_to_regmap()` only creates a regmap automatically for nodes compatible with `"syscon"` and checks resources, while `device_node_to_regmap()` can create for any node without clock/reset management. Resource size must be at least `reg-io-width`. Optional hwspinlock errors other than missing lock can defer or fail registration. Lazy-created entries are singleton per `device_node *`.

## Test Signals
Validate lookup by compatible, direct node, phandle, phandle args, and optional phandle. Exercise endianness and `reg-io-width`, hwspinlock configuration, clock attach/reset deassert paths, duplicate external registration returning `-EEXIST`, and deferred creation for non-syscon nodes.
