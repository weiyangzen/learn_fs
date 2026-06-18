# sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/Makefile

Purpose: object composition for CTU CAN FD drivers.

Important build targets: `obj-$(CONFIG_CAN_CTUCANFD) := ctucanfd.o` creates the common module from `ctucanfd_base.o`. `obj-$(CONFIG_CAN_CTUCANFD_PCI) += ctucanfd_pci.o` and `obj-$(CONFIG_CAN_CTUCANFD_PLATFORM) += ctucanfd_platform.o` add bus wrappers when configured.

Control flow and state: no runtime behavior exists, but the build graph enforces the architecture seen in the sources: common CAN logic in `ctucanfd_base.c`, separate PCI enumeration in `ctucanfd_pci.c`, and separate OF platform binding in `ctucanfd_platform.c`. Dependencies are the Kconfig symbols and kernel module build system. Risks are link/export mismatches for `ctucan_probe_common()`, `ctucan_suspend()`, and `ctucan_resume()` if object membership changes. Test signals include successful modular and built-in builds for each symbol combination.
