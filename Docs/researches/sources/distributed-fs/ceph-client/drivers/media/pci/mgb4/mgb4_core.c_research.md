# sources/distributed-fs/ceph-client/drivers/media/pci/mgb4/mgb4_core.c

- Purpose: Main MGB4 PCI driver: enables the device, creates XDMA/I2C/SPI child devices, maps registers, detects module/firmware type, and creates V4L2/IIO/sysfs/debugfs endpoints.
- Important APIs/types/functions: `mgb4_probe`, `mgb4_remove`, `init_xdma/free_xdma`, `init_i2c/free_i2c`, `init_spi/free_spi`, module-version and serial helpers, hwmon callbacks, and PCI ID table.
- Control flow: Probe enables PCIe features, allocates MSI-X vectors, sets 64-bit DMA mask, registers XDMA and DMA channels, maps video/CMT BAR windows, initializes SPI flash and xiic I2C, adds PCI sysfs and optional hwmon/debugfs, reads serial from MTD, detects module version through I2C and validates firmware type, then creates input/output V4L2 devices and trigger. Remove unwinds devices, groups, maps, channels, IRQs, and PCI state.
- State and persistence: `struct mgb4_dev` holds all live device resources; persistent hardware data includes SPI NOR partitions and serial-number MTD contents. Module version is mirrored into FPGA register 0xD4.
- Dependencies and integration points: Integrates PCI/MSI-X, AMD XDMA platform device, DMAengine, xiic-i2c, Xilinx SPI, SPI NOR/MTD, hwmon, debugfs, V4L2 vin/vout, IIO trigger, and sysfs modules.
- Risks: Probe tolerates missing expansion module to allow flashing, so later code must handle absent video devices. Partial failures in vin/vout creation are not fatal and may leave fewer endpoints. Error paths must match ownership exactly; `pci_disable_msix` is used after vector allocation.
- Test signals: Build and probe on T100/T200 IDs, no-module flashing mode, module/firmware mismatch, MTD serial read, hwmon temperature read, and remove after partially created endpoints.
