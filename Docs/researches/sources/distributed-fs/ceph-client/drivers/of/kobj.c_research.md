# sources/distributed-fs/ceph-client/drivers/of/kobj.c

## Purpose
`kobj.c` mirrors live devicetree nodes and properties into sysfs under `/sys/firmware/devicetree`. It provides kobject type glue, binary property attributes, safe name handling, and attach/detach helpers used by core and dynamic OF code.

## Important APIs, types, and functions
Key functions are `of_node_is_attached()`, `__of_add_property_sysfs()`, `__of_sysfs_remove_bin_file()`, `__of_remove_property_sysfs()`, `__of_update_property_sysfs()`, `__of_attach_node_sysfs()`, and `__of_detach_node_sysfs()`. `of_node_ktype` binds node kobject release to `of_node_release()` when dynamic OF is enabled, or a no-op without dynamic freeing.

## Control flow and state
Node attach sets the node kset, chooses a name (`base` for root-like nodes, basename for children), adds the kobject under the parent, creates bin attributes for existing properties, and takes a node reference for sysfs lifetime. Property add initializes a bin attribute, masks `security-*` properties to mode `0400` and size zero, and creates the sysfs file. Removal deletes the bin file and frees the duplicated sysfs attribute name. Detach removes properties, deletes the kobject, and drops the sysfs-held node reference.

## Dependencies and integration
The file depends on `of_kset` from `base.c`, `of_node_release()` from `dynamic.c` when configured, kernfs/sysfs APIs, and property lists maintained by OF core.

## Risks and test signals
Risks include duplicate property or node names, sysfs name allocation failures, leaking property attribute names, exposing sensitive property values, and attach/detach imbalance. Signals are sysfs tree shape, duplicate-name warnings, property file permissions, kobject lifetime warnings, and dynamic overlay sysfs updates.
