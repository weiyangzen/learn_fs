# sources/distributed-fs/ceph-client/drivers/mfd/mfd-core.c

Purpose: Generic Linux MFD child-device registration core. It converts `struct mfd_cell` arrays into platform devices, translates resources, attaches OF/ACPI/software nodes, registers regulator supply aliases, and provides managed and unmanaged removal APIs.

Important APIs, types, and functions: public exports are `mfd_add_devices()`, `mfd_remove_devices_late()`, `mfd_remove_devices()`, and `devm_mfd_add_devices()`. Internal `mfd_add_device()` allocates a platform device, duplicates cell data, copies/translates resources, handles OF node allocation via `mfd_match_of_node_to_dev()`, attaches ACPI fwnodes via `mfd_acpi_add_device()`, adds platform data/software nodes, and registers the platform device. `mfd_of_node_list` tracks allocated OF child nodes to avoid multiple children claiming the same node.

Control flow: parent drivers call `mfd_add_devices()` with cells and optional memory/IRQ bases or an IRQ domain. Each cell is added in order; any failure removes already-added children. Removal walks child devices in reverse order and honors dependency levels. `devm_mfd_add_devices()` registers a devres release action that calls `mfd_remove_devices()`.

State and persistence: global state consists of the protected OF node allocation list. Child platform devices persist until explicit or devm removal. Regulator supply aliases and software nodes are installed per child and removed on teardown.

Dependencies and integration points: integrates with platform bus, OF, ACPI, property/fwnode APIs, regulator aliases, IRQ domains, PM runtime, and resource conflict checking. Almost every other MFD driver in this subset relies on this file.

Risks: global OF node tracking must be cleaned on all failure paths or stale entries can block future probes. Resource IRQ translation assumes single IRQ ranges when using domains and warns on ranges. Disabled OF children are silently skipped. `pm_runtime_no_callbacks()` is called only after successful platform-device add. Test signals include OF compatible/reg matching, ACPI HID/ADR matching, resource translation with mem base and irqdomain, rollback on mid-array failure, regulator alias cleanup, and managed removal ordering.
