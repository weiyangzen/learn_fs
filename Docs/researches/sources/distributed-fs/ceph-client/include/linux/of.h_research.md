<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of.h -->
# sources/distributed-fs/ceph-client/include/linux/of.h

## Purpose
This is the central Open Firmware / Devicetree API header. It defines the in-memory device-tree object model (`struct device_node`, `struct property`, phandles, iterators, reconfiguration records), root/chosen/alias globals, node/property lookup helpers, property decoding helpers, phandle parsing, dynamic changesets, machine matching, overlays, and config-disabled stubs.

## Important APIs, types, and functions
Key types are `phandle`, `ihandle`, `struct property`, `struct device_node`, `struct of_phandle_args`, `struct of_phandle_iterator`, `struct of_reconfig_data`, `struct of_changeset_entry`, `struct of_changeset`, and overlay notification types. Node APIs include `of_node_init()`, `of_node_get()/of_node_put()`, `of_find_node_by_*()`, `of_get_parent()`, child iterators, CPU node helpers, alias helpers, `of_match_node()`, `of_device_get_match_data()`, and `of_machine_*()` helpers. Property APIs include `of_find_property()`, `of_get_property()`, typed scalar/array readers, string readers, count helpers, `of_property_present()`, and property iterators. Phandle APIs include `__of_parse_phandle_with_args()`, `of_parse_phandle_with_args()`, fixed/optional variants, mapped arguments, count helpers, `of_for_each_phandle()`, and `of_phandle_args_equal()`. Dynamic APIs expose reconfig notifiers, node attach/detach, property add/remove/update, changeset apply/revert/destroy, and helper constructors. Overlay APIs expose FDT apply/remove and overlay notifiers.

## Control flow
With `CONFIG_OF`, callers search or iterate the live tree with reference-returning APIs, decode big-endian property cells, parse phandle lists into node plus argument arrays, and use `_OF_DECLARE()` section entries for early OF init tables. Dynamic updates are collected in an `of_changeset`, applied atomically enough to roll back partial failures, and optionally reverted later. Overlay apply parses an overlay FDT into changesets and notifies subscribers before and after apply/remove. With `CONFIG_OF` or dynamic overlay support disabled, inline stubs return neutral values such as `NULL`, `false`, `-ENOSYS`, `-EINVAL`, or `-ENOTSUPP`.

## State and persistence
The header exposes global tree state (`of_root`, `of_chosen`, `of_aliases`, `of_stdout`) and per-node/per-property runtime state: child/sibling links, dead property lists, flags, kobjects, fwnodes, data pointers, and reference counts. Dynamic nodes/properties are marked with `OF_DYNAMIC`; detached, populated, overlay, and overlay-free states are flag bits. Changesets persist a reversible log of node/property mutations until destroyed. The tree is memory-resident kernel state derived from firmware DTB/PROM and can be changed by overlays or dynamic code.

## Dependencies and integration points
It depends on Linux types, bitops, cleanup/free annotations, kobjects, mod_devicetable, property/fwnode APIs, lists, byteorder, optional SPARC PROM interfaces, NUMA, module autoloading, kexec FDT setup, and notifiers. It is foundational for OF address, IRQ, platform, DMA, IOMMU, clock, graph, reserved-memory, network, PCI, and driver matching layers.

## Risks and test signals
Risks include leaked node references when iterator loops exit early, property length/endian mistakes, phandle argument count mismatches, stale pointers after detach/overlay removal, duplicate aliases, incorrect disabled-config assumptions, and notifier rollback bugs. Test signals include DT-enabled and `!CONFIG_OF` builds, dtc/schema boot tests, phandle parsing with fixed/optional/mapped args, overlay apply/remove/revert, dynamic property update notifiers, CPU/NUMA node lookup, module modalias generation, and reference-leak detection around scoped and non-scoped iterators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/of.h -->
