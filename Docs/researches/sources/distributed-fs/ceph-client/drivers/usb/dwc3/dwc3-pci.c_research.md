# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-pci.c

Purpose: PCI glue driver that turns Intel and AMD PCI DWC3 controllers into a child `dwc3` platform device with synthesized resources and software-node properties. It handles Intel/AMD quirks, Bay Trail GPIO/refclock setup, ACPI DSM power transitions, and runtime wake work.

Important APIs, types, and functions: `struct dwc3_pci` stores the child platform device, PCI device, DSM GUID, PM flag, and resume work. Software nodes provide properties such as `dr_mode`, `linux,sysdev_is_parent`, PHY charger detection, reserved endpoints, AMD link quirks, and role-switch defaults. `dwc3_byt_enable_ulpi_refclock()` clears Bay Trail ULPI refclock disable. `dwc3_pci_quirks()` applies vendor/device-specific setup. `dwc3_pci_probe()`, `_remove()`, `_dsm()`, and PM callbacks own lifecycle.

Control flow: probe enables the PCI function, sets bus mastering, allocates a `dwc3` platform device, maps BAR0 and PCI IRQ into platform resources, sets parent and ACPI companion, applies quirk software node and platform-specific GPIO/refclock handling, registers the child, enables wakeup, stores driver data, and initializes resume work. Runtime/system suspend invoke DSM D3 for selected Intel devices; resume invokes DSM D0 and queues work that runtime-resumes the child DWC3 device.

State and persistence: software node properties persist on the child until removal. `has_dsm_for_pm` and `guid` persist per PCI function. Bay Trail fallback GPIO lookup table may be globally added and is removed on device removal. Runtime PM state is split between the PCI parent and child platform device.

Dependencies and integration: depends on PCI, ACPI, DMI, GPIO lookup/descriptor APIs, workqueues, platform-device creation, and PM. It integrates with DWC3 core entirely through the child platform device and property injection rather than OF.

Risks: many device IDs share the same software node, so adding IDs can accidentally select wrong mode/quirks. Bay Trail GPIO fallbacks are board-sensitive and use global lookup table mutation. Runtime resume queues child PM work asynchronously, which can hide ordering bugs. DSM failures block PM transitions on affected Intel devices.

Test signals: enumerate supported Intel and AMD PCI IDs, verify child resources match BAR0/IRQ, confirm software-node properties in sysfs or debug, exercise Bay Trail refclock/GPIO paths, check AMD quirk application, and test runtime/system suspend with and without DSM-capable devices.
