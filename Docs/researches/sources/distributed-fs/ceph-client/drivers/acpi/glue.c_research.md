# sources/distributed-fs/ceph-client/drivers/acpi/glue.c

Purpose: `glue.c` links Linux physical devices with ACPI namespace devices. It lets bus integrations register matching logic, finds ACPI child devices by address, binds/unbinds `struct device` instances to `struct acpi_device`, creates sysfs firmware/physical-node links, and invokes bus-specific setup or ACPI scan-handler bind callbacks.

Important APIs, types, and functions: exported bus registration APIs are `register_acpi_bus_type()` and `unregister_acpi_bus_type()`. Child lookup exports are `acpi_find_child_device()` and `acpi_find_child_by_adr()`. Binding exports are `acpi_bind_one()` and `acpi_unbind_one()`. Device core entry points are `acpi_device_notify()` and `acpi_device_notify_remove()`.

Control flow: bus types are stored in a global list under an rwsem. Child lookup walks ACPI children matching `_ADR`, optionally requiring children and `_STA`, and scores ambiguous matches. Binding takes references on both devices, allocates a physical-node record, assigns the first free node id, optionally sets `ACPI_COMPANION`, creates `physical_node*` and `firmware_node` sysfs links, and propagates wake capability. Device notification first tries to bind an already-known companion; if none, it asks registered bus types to find one. It then performs PCI ACPI setup, platform MSI setup, custom bus setup, or scan-handler bind. Removal performs matching cleanup and unbinds.

State and persistence: state is in-memory: the registered bus-type list and each ACPI device's physical-node list. Sysfs links persist only while the binding exists.

Dependencies and integration: this file sits at the boundary of the generic device core, ACPI scan core, PCI ACPI support, platform MSI configuration, wakeup capability, sysfs, and custom ACPI scan handlers.

Risks: binding has multiple side effects and partial sysfs link failures are logged but do not abort the bind. Duplicate or ambiguous `_ADR` namespace entries are handled by heuristics, so firmware violations can still attach the wrong companion. Reference counting must remain paired across duplicate-bind and error paths. Bus-type registration order can affect matching if multiple types match one device.

Test signals: cover duplicate bind attempts, unbind with and without a companion, sysfs link failure injection, ambiguous child `_ADR` scoring, PCI and platform-device paths, handler bind/unbind callbacks, wake-capable propagation, and bus registration while ACPI is disabled.
