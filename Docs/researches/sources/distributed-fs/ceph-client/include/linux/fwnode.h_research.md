<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fwnode.h -->
# sources/distributed-fs/ceph-client/include/linux/fwnode.h

Purpose: Defines the low-level firmware node abstraction used by ACPI, device tree, and software nodes to expose device properties, graph endpoints, references, DMA capabilities, IRQs, MMIO mapping, and supplier/consumer links.

Important APIs/types/functions: Core types are `fwnode_handle`, `fwnode_link`, `fwnode_endpoint`, `fwnode_reference_args`, and `fwnode_operations`. Flags include link initialization, not-a-device, initialized, child-bound requirements, best effort, and visited. Operation macros `fwnode_has_op()`, `fwnode_call_int_op()`, `fwnode_call_bool_op()`, `fwnode_call_ptr_op()`, and `fwnode_call_void_op()` safely dispatch to providers. Helpers initialize flags and links: `fwnode_init()`, flag setters/testers, `fwnode_dev_initialized()`, `fwnode_link_add()`, `fwnode_links_purge()`, `fw_devlink_purge_absent_suppliers()`, and `fw_devlink_is_strict()`.

Control flow: Provider backends fill `fwnode_operations`; consumer APIs call through the dispatch macros to read properties, walk children, parse graph endpoints, resolve references, map resources, and create device links. Link lists connect suppliers and consumers for probe ordering.

State and persistence behavior: `fwnode_handle` carries provider ops, optional secondary fwnode, associated device pointer, supplier/consumer lists, and flags. Persistence belongs to the firmware backend; link and initialization flags are runtime state.

Dependencies and integration points: Depends on bitops, lists, error-pointer helpers, and device core. Integrates with property APIs, graph APIs, DMA attribute discovery, IRQ/resource discovery, and fw_devlink probe ordering.

Risks: Callers must handle `NULL` and error fwnodes; missing ops return `-ENXIO`, `-EINVAL`, `false`, or `NULL` depending on macro. Supplier cycles and ignored links affect probe deferral. Flag misuse can break device population ordering.

Test signals: Property read tests across ACPI/OF/software nodes, graph endpoint traversal, supplier-cycle detection, device-link purge behavior, missing-op paths, DMA/IRQ/iomap provider tests, and probe ordering tests under strict fw_devlink.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fwnode.h -->
