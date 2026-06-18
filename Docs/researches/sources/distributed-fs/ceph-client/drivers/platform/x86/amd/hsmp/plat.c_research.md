# sources/distributed-fs/ceph-client/drivers/platform/x86/amd/hsmp/plat.c

Purpose: `plat.c` is the legacy non-ACPI HSMP front end. It creates a synthetic platform device on supported AMD families, accesses HSMP mailboxes through AMD SMN/PCI helpers, registers `/dev/hsmp`, and exposes per-socket metrics binary attributes.

Important APIs, types, and functions: `amd_hsmp_pci_rdwr()` bridges common mailbox access to `amd_smn_hsmp_rdwr()`. `init_platform_device()` initializes all sockets with hardcoded SMN offsets, tests each socket, caches protocol version, optionally maps protocol-v6 metrics DRAM, and registers hwmon sensors. `legacy_hsmp_support()` gates supported CPU families/models. `hsmp_plt_init()` rejects systems with the ACPI HSMP device, checks legacy support, obtains `amd_num_nodes()`, registers the platform driver, and creates the platform device.

Control flow: `device_initcall()` runs at boot/module init. On legacy supported systems without ACPI `AMDI0097`, it registers `amd_hsmp` and probes the synthetic device. Probe allocates socket array, initializes mailboxes for each node/socket, and registers the misc device. Remove deregisters misc. Module exit unregisters platform device and driver.

State and persistence: shared `hsmp_pdev`, socket array, mapped metric-table addresses, protocol version, and static platform device pointer are runtime-only. Mailbox writes can affect firmware/runtime power-management settings.

Dependencies and integration points: depends on AMD node/SMN support, PCI/platform driver core, sysfs binary attributes, common HSMP exports, optional hwmon, and CPU family/model data. The static sysfs groups cover `socket0` through `socket7`, guarded by `MAX_AMD_NUM_NODES == 8`.

Risks: hardcoded SMN offsets must match CPU family/model, with a special case for family 0x1A model <= 0x0F. The global `proto_ver` is shared even though initialization loops all sockets. Metrics sysfs groups are statically sized to eight sockets. The ACPI-present check is essential to prevent duplicate front ends.

Test signals: boot on legacy supported family/model without ACPI object, socket count from `amd_num_nodes()`, successful TEST per socket, `/dev/hsmp`, `socketN/metrics_bin` visibility only for protocol v6 and valid sockets, hwmon registration, and refusal when ACPI HSMP is present.
