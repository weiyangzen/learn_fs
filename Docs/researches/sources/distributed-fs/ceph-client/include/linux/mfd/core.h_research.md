## sources/distributed-fs/ceph-client/include/linux/mfd/core.h

Purpose: This is the generic Linux MFD core public header. It defines how an MFD parent describes child devices/cells and declares the APIs that register and remove those children.

Important APIs, types, and constants: `MFD_RES_SIZE()` and `MFD_CELL_*` macros construct common `struct mfd_cell` initializers for OF, OF-with-reg, ACPI, basic resource, and name-only cells. Dependency levels are `MFD_DEP_LEVEL_NORMAL` and `MFD_DEP_LEVEL_HIGH`. `struct mfd_cell_acpi_match` matches ACPI IDs or ADRs. `struct mfd_cell` includes child name/id/level, suspend/resume callbacks, platform data and size, ACPI/software-node/OF matching data, optional `of_reg`, resource arrays, resource-conflict behavior, runtime-PM callback suppression, and parent-supply mappings. `mfd_get_cell()` fetches the creating cell from a platform device. Public APIs include `mfd_add_devices()`, `mfd_add_hotplug_devices()`, `mfd_remove_devices()`, `mfd_remove_devices_late()`, and devres-managed `devm_mfd_add_devices()`.

Control flow: Parent drivers build `mfd_cell` arrays and call add APIs. The MFD core creates platform devices, attaches copied cell metadata/platform data/resources, maps IRQ domains/bases, and later removes devices through explicit or managed cleanup.

State and persistence: State is runtime platform-device and resource metadata. Platform data is copied into child devices; no persistent storage is involved.

Dependencies and integration points: Includes `linux/platform_device.h`; integrates with platform bus, OF/ACPI matching, software nodes, IRQ domains, resources, runtime PM, regulators, and devres.

Risks: Incorrect `pdata_size` or resource arrays can produce child memory corruption or invalid resources. `ignore_resource_conflicts` weakens safety. Matching duplicate OF compatibles without `of_reg` can bind the wrong child node. Parent supply mapping affects regulator lookup ownership.

Test signals: Build and probe tests for MFD parents, child platform-device creation count, OF/ACPI matching, resource and IRQ assignment, devm cleanup on probe failure, suspend/resume callback dispatch, and duplicate resource conflict handling.
