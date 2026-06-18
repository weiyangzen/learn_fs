# sources/distributed-fs/ceph-client/drivers/net/can/ctucanfd/Kconfig

Purpose: Kconfig entries for the CTU CAN FD open-source IP core and its PCI and platform bindings.

Important symbols: `CAN_CTUCANFD` builds the common base driver and is visible mainly for `COMPILE_TEST`. `CAN_CTUCANFD_PCI` depends on `PCI` and selects the common core. `CAN_CTUCANFD_PLATFORM` depends on `HAS_IOMEM && OF` and also selects the common core.

Control flow and state: this file has no runtime control flow; it controls which objects are compiled by the Makefile and enforces that bus-specific drivers pull in `ctucanfd_base.o`. Integration points are the kernel Kconfig dependency graph, PCI, OF platform probing, and SocketCAN. Risks are build coverage gaps if the base symbol is not selected, and hardware support being split across bus-specific symbols. Test signals are configuration matrix builds: common-only compile testing, PCI module builds with `CONFIG_PCI`, and platform builds with OF and I/O memory enabled.
