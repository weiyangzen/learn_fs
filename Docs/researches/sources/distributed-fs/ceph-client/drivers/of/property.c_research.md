# sources/distributed-fs/ceph-client/drivers/of/property.c

## Purpose
Provides OF property readers, graph traversal helpers, fwnode operations for OF nodes, and fw_devlink supplier discovery.

## Important APIs, types, and functions
Exports typed property readers, string helpers, `of_prop_next_u32()`, `of_prop_next_string()`, graph helpers such as `of_graph_get_next_endpoint()` and remote endpoint helpers, and `of_fwnode_ops`. Supplier linking uses `struct supplier_bindings`, many `parse_*` helpers, and `of_link_property()`.

## Control flow
Typed readers validate property presence/value/size through `of_find_property_value_of_size()` and convert big-endian data. String helpers scan bounded NUL-terminated lists. Graph helpers normalize `ports` containers and iterate ports/endpoints with refcount handoff. Fwnode ops translate generic property, graph, IRQ, and I/O requests into OF APIs. Supplier linking scans properties, parses known phandle supplier bindings, and creates fwnode links.

## State and persistence behavior
Readers are mostly stateless over in-memory properties. Fwnode get/put mirrors OF node refcounting. Supplier link creation persists dependency edges in driver-core fwnode state. X86 add-links support is cached in a static variable.

## Dependencies and integration points
Depends on OF core lookup, phandle parsing, OF graph conventions, address and IRQ helpers, DMA coherency helpers, device matching, fw_devlink, and generic fwnode property APIs.

## Risks and edge cases
Boolean reads warn on valued properties; malformed byte lengths return `-EOVERFLOW`; unterminated strings return `-EILSEQ`; supplier parsing must avoid false GPIO matches and GPIO hogs; link creation continues across supplier failures.

## Test signals
`unittest.c` covers string helpers, phandle parsing, graph-adjacent behavior, address/IRQ integration, and platform/overlay side effects. Driver subsystems also exercise the exported property APIs.
