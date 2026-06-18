# sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci_zdev.c

This file provides IBM s390 zPCI-specific VFIO PCI integration. It adds zPCI capability records to `VFIO_DEVICE_GET_INFO` and registers/unregisters zPCI devices with KVM when a VFIO device is opened with a KVM context.

Important functions are `zpci_base_cap()`, `zpci_group_cap()`, `zpci_util_cap()`, `zpci_pfip_cap()`, `vfio_pci_info_zdev_add_caps()`, `vfio_pci_zdev_open_device()`, and `vfio_pci_zdev_close_device()`. The capability structures come from `linux/vfio_zdev.h`; platform data comes from `struct zpci_dev`.

Control flow for info capability creation converts the PCI device to `zpci_dev`, then appends base function, function group, optional utility string, and function path capabilities to the VFIO info capability chain. Open-device flow is no-op without KVM, but when `vdev->vdev.kvm` exists it invokes `zpci_kvm_hook.kvm_register` if available. Close mirrors this through `kvm_unregister`.

State is not owned here beyond KVM hook registration side effects. Capability data is copied out of the live zPCI device into temporary VFIO capability buffers. KVM registration persists during the VFIO device open interval and is unwound at close.

Dependencies include s390 zPCI headers, CLP data sizes, VFIO info capability helpers, KVM host hooks, and core open/info paths. Risks include missing zPCI conversion, unavailable KVM hooks, stale utility/path strings if platform data changes, and capability version/size mismatches. Test signals include zPCI and non-zPCI devices, KVM and non-KVM opens, absent hook callbacks, info buffer sizing with optional capabilities, and open/close ordering during core enable failure unwind.
