# sources/distributed-fs/ceph-client/drivers/media/pci/pt3/Makefile

Purpose: Kbuild metadata for the Earthsoft PT3 PCIe driver.

Important APIs, types, and functions: `earth-pt3-objs += pt3.o pt3_i2c.o pt3_dma.o` defines the composite object. `obj-$(CONFIG_DVB_PT3) += earth-pt3.o` attaches it to Kconfig. Include flags add DVB frontend and tuner headers.

Control flow: Build-time only. Kbuild compiles the main, I2C, and DMA helper source files into one module/object.

State and persistence: No runtime state.

Dependencies and integration points: Mirrors the source split in `pt3.h`: main frontend/probe code, I2C command translator, and DMA descriptor/ring handling.

Risks: Any source split or helper removal must keep `earth-pt3-objs` synchronized. Include paths assume the media tree's frontend/tuner header layout.

Test signals: Build tests should verify all three objects are linked, both module and built-in modes work, and missing helper objects cause obvious link failures rather than silent feature loss.
