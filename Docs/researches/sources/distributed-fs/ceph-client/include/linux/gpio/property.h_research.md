<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/property.h -->
# sources/distributed-fs/ceph-client/include/linux/gpio/property.h

Purpose: This small header declares helper APIs for firmware-property backed GPIO lookups.

Important APIs/types/functions: It forward-declares `struct fwnode_handle` and `struct gpio_desc`, and declares `fwnode_gpiod_get_index()` for fetching a GPIO descriptor from a firmware node by property name/index plus descriptor flags and label.

Control flow, state, and persistence: The implementation performs firmware property parsing and returns a referenced GPIO descriptor according to the requested index and flags. The header itself holds no state.

Dependencies/integration: It bridges the generic firmware-node property API and gpiolib descriptor API, covering device tree, ACPI, or software nodes through `fwnode_handle`.

Risks and test signals: Callers must handle `ERR_PTR` failures, missing properties, and index bounds. Tests should cover active-low/open-drain flags, absent properties, named and indexed GPIO lists, and descriptor release by the consumer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/gpio/property.h -->
