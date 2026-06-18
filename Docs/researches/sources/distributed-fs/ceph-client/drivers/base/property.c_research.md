# sources/distributed-fs/ceph-client/drivers/base/property.c

## Purpose
This file implements the unified firmware-node/device-property API. It lets drivers read properties, references, child nodes, DMA attributes, PHY modes, IRQs, graph endpoints, match data, and device connections without caring whether the backing firmware description is Device Tree, ACPI, software node, or a secondary fwnode.

## Important APIs, Types, And Functions
Exports include `__dev_fwnode()`, `device_property_present()`, typed `device_property_read_*()` and `fwnode_property_read_*()` helpers, string matching helpers, `fwnode_property_get_reference_args()`, `fwnode_find_reference()`, node naming/parent/child iteration helpers, `fwnode_handle_get()`, `fwnode_device_is_available()`, child count helpers, `device_dma_supported()`, `device_get_dma_attr()`, PHY helpers, `fwnode_iomap()`, IRQ helpers, graph endpoint helpers, `device_get_match_data()`, and connection matching helpers.

## Control Flow And State
Most device helpers are thin wrappers around `dev_fwnode(dev)` and the fwnode operation table. Property lookups first call the primary fwnode operation and often fall back to `fwnode->secondary` when the primary returns false or `-EINVAL`. Typed integer reads funnel through `fwnode_property_read_int_array()`. String matching counts strings, allocates a temporary array, reads values, then uses `match_string()`. Reference helpers return fwnode handles that callers must put.

Child and graph traversal helpers manage references carefully: `fwnode_get_next_parent()` and `fwnode_get_next_child_node()` consume the previous handle, endpoint iteration can continue into secondary fwnodes, and graph lookup can filter disabled/unconnected remotes unless flags request otherwise. Connection matching first checks graph endpoints and then named reference properties.

## Dependencies And Integration Points
The file depends on `linux/property.h` fwnode ops, optional OF support, PHY string tables, IRQ and iomap fwnode ops, ACPI/DT/software-node implementations behind the operation table, and driver subsystems that consume graph endpoints or named references.

## Risks And Test Signals
Risks include inconsistent primary/secondary fallback semantics, reference leaks or double puts, wrong error-code propagation (`-EINVAL`, `-ENOENT`, `-ENODATA`, `-ENOTCONN`), disabled remote endpoint filtering surprises, and string allocation failures. Test signals include firmware-agnostic driver tests with DT/ACPI/software nodes, property count/read/match error cases, reference lifetime checks, graph endpoint selection with `FWNODE_GRAPH_ENDPOINT_NEXT`, IRQ name lookup, PHY mode parsing, and connection matching across graph and property references.
