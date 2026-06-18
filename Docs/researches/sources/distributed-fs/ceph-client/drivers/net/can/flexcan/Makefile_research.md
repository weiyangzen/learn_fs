# sources/distributed-fs/ceph-client/drivers/net/can/flexcan/Makefile

Purpose: build definition for the FlexCAN driver objects.

Important build targets: `obj-$(CONFIG_CAN_FLEXCAN) += flexcan.o` creates the FlexCAN module or built-in object. The composite object includes `flexcan-core.o` and `flexcan-ethtool.o`.

Control flow and state: no runtime code is present; the file declares the split between core controller behavior and ethtool support. Dependencies are the `CONFIG_CAN_FLEXCAN` Kconfig symbol and the kernel build system. Risks are minimal but include link failures if either object’s internal symbols drift, and missing ethtool support if object composition changes. Test signals are successful builds for built-in and module configurations and presence of FlexCAN ethtool operations after linking.
