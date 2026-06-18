# sources/distributed-fs/ceph-client/drivers/vfio/pci/xe/Kconfig

This Kconfig file defines the Intel Xe-specific VFIO PCI variant. `XE_VFIO_PCI` is a tristate option depending on `DRM_XE` and `PCI_IOV`, selecting `VFIO_PCI_CORE`. Its help text describes a device-specific VFIO driver for Intel Graphics SR-IOV virtual functions that adds VFIO migration uAPI support on top of generic VFIO PCI behavior.

Integration is build-time: enabling this option compiles the Xe VFIO PCI module from the sibling Makefile. It relies on the Xe DRM driver and PCI SR-IOV support, so it is intentionally scoped to platforms where Xe virtual functions and their migration hooks exist.

There is no runtime state in this file. Risks are configuration mismatch and user expectation: selecting the option without supported Xe SR-IOV hardware or migration-capable Xe driver paths will not produce useful runtime behavior. Test signals include Kconfig dependency resolution with and without `DRM_XE`/`PCI_IOV`, module and built-in builds, and runtime probe tests on supported Intel Graphics VFs.
