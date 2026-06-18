# sources/distributed-fs/ceph-client/drivers/virt/vboxguest/vboxguest_linux.c

## Purpose
`vboxguest_linux.c` is the Linux-specific VirtualBox guest driver wrapper. It probes the VirtualBox VMMDev PCI device, maps resources, registers `/dev/vboxguest` and `/dev/vboxuser`, exposes host version/features through sysfs, creates the absolute mouse input device, and connects the generic core to Linux IRQ, PCI, miscdevice, and input subsystems.

## Important APIs, types, and functions
Important functions are `vbg_pci_probe`, `vbg_pci_remove`, `vbg_misc_device_ioctl`, `vbg_misc_device_open`, `vbg_misc_device_user_open`, `vbg_create_input_device`, `vbg_input_open`, `vbg_input_close`, `vbg_linux_mouse_event`, `vbg_get_gdev`, and `vbg_put_gdev`. The driver registers a `pci_driver` matching vendor `0x80ee` and device `0xcafe`, sysfs attributes `host_version` and `host_features`, and two file operation tables.

## Control flow
Probe enables PCI, claims I/O and MMIO resources, maps VMMDev memory, validates the MMIO version/size, initializes `vbg_dev`, calls `vbg_core_init`, registers input, IRQ, and misc devices, and publishes the singleton `vbg_gdev`. Opens create sessions with requestor flags derived from uid/gid and whether the public `vboxuser` node was used. Ioctl copies and sizes the user buffer, allocates a DMA32 VMMDev request buffer for raw VMMDev requests or normal kernel memory otherwise, delegates to `vbg_core_ioctl`, then copies back the bounded output.

## State and persistence
Runtime state is devm-managed `vbg_dev`, the singleton `vbg_gdev` protected by `vbg_gdev_mutex`, per-open sessions in `file->private_data`, and input-device state. No persistent storage is used. `vbg_get_gdev` intentionally returns with the global mutex held until `vbg_put_gdev` so short-lived external users cannot race removal.

## Dependencies and integration points
The file depends on PCI, miscdevice, usercopy, credentials, input, IRQ, and the core header. It integrates with userspace device nodes, Linux input reporting, sysfs, VirtualBox shared-folder style in-kernel consumers through exported `vbg_get_gdev`, and the host VMMDev interrupt line.

## Risks and test signals
Risks include usercopy size mistakes, `_IOC_SIZE` compatibility, more than one VMMDev PCI function, stale singleton locking, IRQ teardown ordering, input registration failure unwind, unprivileged access through `vboxuser`, and MMIO validation against hostile or broken virtual hardware. Test signals include PCI probe/remove fault injection, misc ioctl fuzzing, compat ioctl calls, sysfs reads, mouse open/close and absolute events, vboxsf load/unload while removing the PCI device, and udev-created permissions for both nodes.
