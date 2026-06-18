# sources/distributed-fs/ceph-client/include/linux/resource_ext.h

Purpose: this header provides common resource-window and resource-list helpers used by ACPI, PNP, PCI host bridge, and related bus enumeration code.

Important APIs/types/functions: `struct resource_win` stores a CPU-address-space `struct resource` plus bridge translation offset. `struct resource_entry` stores a list node, resource pointer, translation offset, and embedded default resource storage. APIs include `resource_list_create_entry()`, `resource_list_free()`, list add/add_tail/del/free/destroy helpers, iteration macros, and `resource_list_first_type()`.

Control flow: enumeration code creates entries for discovered I/O or memory windows, appends them to a list, searches by `resource_type()`, consumes them to configure bridges/devices, and frees/destroys the list on teardown.

State and persistence: list entries persist during bus/resource discovery. `res` may point at embedded `__res` or externally owned resources, so ownership must be clear.

Dependencies and integration points: depends on lists, I/O port resources, slab allocation, and resource type helpers. Integrates with ACPI resource parsing, PNP resource lists, PCI host bridge windows, and address translation logic.

Risks: confusing ownership of `res` versus `__res` can leak or free the wrong object. Translation `offset` must be consistently applied between bus and CPU address spaces. Test signals include ACPI/PCI host bridge enumeration, resource window translation, list free under failure unwinding, and type-filtered lookup.
