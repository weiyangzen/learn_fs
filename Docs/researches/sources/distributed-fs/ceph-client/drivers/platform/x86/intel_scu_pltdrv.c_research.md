<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_pltdrv.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_pltdrv.c

Purpose: ACPI/platform instantiator for the Intel SCU IPC core. It binds ACPI ID `INTC1026`, obtains memory and optional IRQ resources from a platform device, and registers a managed SCU IPC provider.

Important APIs/functions: `intel_scu_platform_probe()` calls `platform_get_irq_optional()`, `platform_get_resource(IORESOURCE_MEM, 0)`, copies the resource into `struct intel_scu_ipc_data`, and calls `devm_intel_scu_ipc_register()`. It stores the returned SCU handle as platform driver data.

Control flow: module platform driver registration handles ACPI matching. Probe fails with `-ENOMEM` when no memory resource is present, propagates managed core registration errors, and otherwise relies on devres for cleanup at device detach.

State/persistence: no custom persistent state beyond platform driver data. The core owns SCU IPC device state and hardware command handling.

Dependencies/integration: integrates ACPI platform discovery, resource APIs, and the SCU IPC core. This is the non-PCI path for platforms that describe SCU through ACPI.

Risks: optional IRQ may be negative, causing the core to use polling mode. Returning `-ENOMEM` for missing memory resource is semantically odd but preserved. The module author string for Mika is missing a closing `>`.

Test signals: ACPI `INTC1026` platform devices with memory resources should create a managed `intel_scu_ipc` core device; detach should unregister automatically via devres.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_pltdrv.c -->
