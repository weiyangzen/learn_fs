# sources/distributed-fs/ceph-client/drivers/of/base.c

## Purpose
`base.c` is the main live devicetree access layer. It exposes global OF roots (`of_root`, `of_chosen`, `of_aliases`, `of_stdout`), implements node/property lookup and matching, parses phandle argument lists, mutates live node properties, scans `/aliases`, resolves stdout, discovers cache topology, and translates requester IDs through `iommu-map`/`msi-map` style bindings.

## Important APIs, types, and functions
Key globals are `of_mutex`, `devtree_lock`, `aliases_lookup`, `of_kset`, and the `phandle_cache`. Public APIs include `of_find_property()`, `of_get_property()`, `of_find_all_nodes()`, `of_find_node_by_path()`, `of_find_node_by_name()`, `of_find_compatible_node()`, `of_match_node()`, `of_find_node_by_phandle()`, `of_parse_phandle_with_args_map()`, `of_count_phandle_with_args()`, `of_add_property()`, `of_remove_property()`, `of_update_property()`, `of_alias_scan()`, `of_alias_get_id()`, `of_console_check()`, `of_find_next_cache_node()`, `of_find_last_cache_level()`, and `of_map_id()`. Internal helpers prefixed `__of_` assume locking or detached-tree ownership.

## Control flow and state
`of_core_init()` registers OF reconfiguration notifiers, creates `/sys/firmware/devicetree`, attaches all existing nodes to sysfs, seeds the phandle cache, and creates the legacy `/proc/device-tree` symlink. Traversal APIs walk child/sibling/parent pointers under `devtree_lock` and pair returned nodes with reference increments. Matching computes scores from compatible order, type, and name. Phandle parsing uses `of_phandle_iterator` to walk packed `__be32` lists, resolve providers, read `#*-cells`, and fill `struct of_phandle_args`.

Property updates are serialized by `of_mutex`, alter the linked property lists under `devtree_lock`, update sysfs mirrors, and emit dynamic-tree notifications. Removed and replaced properties are moved to `deadprops` because callers may hold raw pointers returned by `of_get_property()`.

## Dependencies and integration
This file depends on `of_private.h` declarations, sysfs helpers from `kobj.c`, dynamic notifier glue from `dynamic.c`, FDT-created globals from `fdt.c`, console registration, CPU/cache helpers, and device-core fwnode flags. It is consumed by most OF subsystems and driver buses.

## Risks and test signals
Risk centers on reference counting, raw property pointer lifetime, lock ordering between `of_mutex` and `devtree_lock`, phandle cache invalidation on detach, malformed phandle lists, and alias/stdout parsing. KUnit coverage in this subset checks root lookup indirectly, while broader kernel OF tests exercise phandle, address, overlay, and dynamic update behavior.
