## sources/distributed-fs/ceph-client/drivers/pci/controller/pci-host-common.h

Purpose: Public declarations for the common PCI host controller helper library.

Important APIs, types, and functions: forward declares `struct pci_ecam_ops` and declares `pci_host_common_probe()`, `pci_host_common_init()`, `pci_host_common_remove()`, and `pci_host_common_ecam_create()`.

Control flow: no runtime flow; it is included by generic host drivers and the implementation file.

State and persistence: no state. It exposes functions that manage host bridge and ECAM runtime state elsewhere.

Dependencies and integration points: platform PCI host drivers use this header to share the ECAM creation/probe/remove path. The header relies on standard kernel struct declarations being visible from including translation units.

Risks: Function prototypes mention `struct platform_device`, `struct pci_host_bridge`, `struct device`, and `struct pci_config_window` without local forward declarations for all of them; current includes in users satisfy this. ABI changes in the common implementation require updating this header.

Test signals: compile users such as `pci-host-generic.c`, module symbol availability for exported helpers, and type-checking under different include orders.
