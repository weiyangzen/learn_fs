<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/char/xillybus/Kconfig

Purpose: Kconfig menu for Xillybus PCIe/OF and XillyUSB FPGA interfaces.

Important APIs/types/functions: Defines `XILLYBUS_CLASS` as an internal tristate, `XILLYBUS` as the generic FPGA interface depending on PCI or OF, transport options `XILLYBUS_PCIE` and `XILLYBUS_OF`, and independent USB option `XILLYUSB`.

Control flow: no runtime flow; configuration selects which modules are built and which shared pieces are selected.

State and persistence: no runtime state. Build state is persisted in the kernel `.config`.

Dependencies and integration: `XILLYBUS` selects `CRC32` and `XILLYBUS_CLASS`; PCIe depends on `PCI_MSI`; OF depends on `OF`, `HAS_DMA`, and `HAS_IOMEM`; XillyUSB depends on `USB` and also selects `CRC32` and the class module.

Risks: `XILLYUSB` intentionally does not depend on `XILLYBUS`, so class/core assumptions must remain separated. Missing `XILLYBUS_CLASS` selection would break device-node lookup. PCIe requires MSI support; systems without MSI cannot use that transport.

Test signals: build matrix for built-in/module/disabled combinations of class, core, PCIe, OF, and USB; confirm dependencies prevent invalid configs and that module names match help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/Kconfig -->
