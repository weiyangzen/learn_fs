# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/Kconfig

- Purpose: Kconfig entry for the Digiteq Automotive MGB4 V4L2 PCIe grabber/output driver.
- Important APIs/types/functions: `config VIDEO_MGB4` tristate with dependencies on V4L2, PCI, I2C, DMA, SPI, MTD, IIO, COMMON_CLK, and selects vb2 DMA-SG, IIO buffer support, Xilinx I2C/SPI, SPI NOR, and XDMA.
- Control flow: When enabled, Kbuild can build the module and automatically pull required support drivers.
- State and persistence: No runtime state; controls build-time configuration.
- Dependencies and integration points: Integrates media, DMAengine/XDMA, IIO, SPI NOR, MTD, and common clock subsystems.
- Risks: Missing dependencies would produce unresolved symbols or a module that probes without required child controllers. Broad selects increase kernel footprint.
- Test signals: Kconfig dependency resolution, `modpost`, and build tests with `VIDEO_MGB4=m/y`.
