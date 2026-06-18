# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/Kconfig

Purpose: Defines Kconfig menu entries for QLogic/Marvell Ethernet drivers under `NET_VENDOR_QLOGIC`, including NetXen, QLA3XXX, QLCNIC, QED core, QEDE, and related feature toggles.

Important options: `NET_VENDOR_QLOGIC` gates the vendor submenu and depends on PCI. `QLA3XXX`, `QLCNIC`, `NETXEN_NIC`, `QED`, and `QEDE` are driver tristates. `QLCNIC_SRIOV`, `QLCNIC_DCB`, `QLCNIC_HWMON`, and `QED_SRIOV` are feature bools with dependency/select logic. `QED` selects compression/checksum/devlink helpers; `QEDE` depends on `QED` and optional PTP support.

Control flow: Build configuration flow is hierarchical: disabling `NET_VENDOR_QLOGIC` hides all child prompts; enabling specific tristates controls whether subdirectories and modules are built by Makefiles.

State and persistence behavior: Kconfig state persists in kernel `.config`, not in the driver. Selected symbols determine compile-time feature inclusion.

Dependencies and integration points: Integrates with kernel PCI, firmware loader, DCB, HWMON, PCI_IOV, PTP, devlink, and Makefile `obj-$(CONFIG_...)` rules.

Risks: Dependency mistakes can expose drivers without required subsystems or hide valid hardware support. `default y` vendor/feature toggles influence distro kernel footprint.

Test signals: Kconfig matrix builds with QLogic vendor disabled, individual drivers built-in/module/disabled, and feature dependencies such as `QLCNIC=y` with `HWMON=m` to validate the explicit HWMON guard.
