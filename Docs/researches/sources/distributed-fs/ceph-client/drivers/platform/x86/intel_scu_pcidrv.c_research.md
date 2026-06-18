<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_pcidrv.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_pcidrv.c

Purpose: built-in PCI instantiator for the Intel SCU IPC core. It binds known Intel SCU PCI device IDs, extracts BAR0 and IRQ resources, and registers the core IPC provider.

Important APIs/functions: `intel_scu_pci_probe()` enables the PCI device with `pcim_enable_device()`, fills `struct intel_scu_ipc_data` from `pdev->resource[0]` and `pdev->irq`, then calls `intel_scu_ipc_register()`. The PCI ID table lists several Intel device IDs including `0x080e`, `0x082a`, `0x08ea`, `0x0a94`, `0x11a0`, `0x1a94`, and `0x5a94`.

Control flow: `builtin_pci_driver()` registers the driver during boot. Probe is minimal and relies on the SCU IPC core for resource reservation, mapping, IRQ request, device registration, and cleanup.

State/persistence: no private state is stored by this wrapper; the core owns the resulting singleton IPC device.

Dependencies/integration: depends on PCI core and `linux/platform_data/x86/intel_scu_ipc.h`. Suppresses bind attributes to avoid manual userspace binding/unbinding for this low-level provider.

Risks: BAR0/IRQ assumptions must match hardware. Since the core supports one IPC instance, multiple matching PCI devices would cause later registration to return `-EBUSY`.

Test signals: matching PCI hardware should register `intel_scu_ipc`; probe should fail cleanly on PCI enable or core registration errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel_scu_pcidrv.c -->
