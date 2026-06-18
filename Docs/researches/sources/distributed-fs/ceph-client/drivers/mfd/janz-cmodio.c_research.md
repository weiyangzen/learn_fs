# sources/distributed-fs/ceph-client/drivers/mfd/janz-cmodio.c

Purpose: PCI MFD driver for Janz CMOD-IO MODULbus carrier boards. It exposes the carrier hex switch through sysfs and creates child devices for module slots selected by the `modules=` kernel parameter.

Important APIs/types/functions: `cmodio_pci_probe()`, `cmodio_probe_submodules()`, `cmodio_setup_subdevice()`, `modulbus_number_show()`, and `struct cmodio_device`.

Control flow: probe enables PCI, requests regions, maps PLX control BAR4, reads the hex switch, creates sysfs attributes, disables all module interrupt lines, then builds MFD cells/resources for non-empty module parameter entries and calls `mfd_add_devices()`. Remove unregisters children, sysfs, mapping, regions, and PCI state.

State and persistence: global module parameters name up to four slot drivers; `cmodio_id` provides unique child IDs. Per-device state stores control mapping, hex switch, cells, resources, and platform data.

Dependencies and integration: depends on PLX PCI IDs with Janz subsystem IDs, BAR3 MODULbus memory, BAR4 control registers, `linux/mfd/janz.h`, and downstream platform drivers named by user-supplied module strings.

Risks: no autodetection of submodules; wrong module parameters create wrong children. Static `cmodio_id` monotonically increases. All children share one IRQ through resource offset semantics relative to `irq_base`.

Test signals: module parameter parsing, no-module `-ENODEV` path, sysfs `modulbus_number`, child BAR offsets per slot, shared IRQ routing, and PCI bind/unbind cleanup.
