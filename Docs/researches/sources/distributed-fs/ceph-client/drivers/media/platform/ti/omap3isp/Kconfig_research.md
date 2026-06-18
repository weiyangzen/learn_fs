# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/Kconfig


Purpose: Defines configuration symbols for the TI OMAP3 camera ISP driver.

Important APIs/types: `VIDEO_OMAP3` is a tristate option labeled "OMAP 3 Camera support". It depends on platform V4L2 drivers, `VIDEO_DEV`, `I2C`, OMAP3+IOMMU or compile testing, common clock, and OF. It selects ARM DMA/IOMMU support when applicable, Media Controller, V4L2 subdev API, DMA-contig vb2, `MFD_SYSCON`, and `V4L2_FWNODE`. `VIDEO_OMAP3_DEBUG` is a bool that enables debug messages and depends on the main driver.

Control flow: Kconfig selection controls whether the `omap3-isp.o` composite module is built and whether the Makefile adds `-DDEBUG`.

State and persistence: Build-time configuration only. No runtime state.

Dependencies/integration: Integrates the driver with the Linux media subsystem, device tree endpoint parsing, common clocks, IOMMU DMA mapping, syscon, I2C-attached camera sensors, and vb2 DMA-contig buffers.

Risks and test signals: `COMPILE_TEST` broadens build coverage, but runtime still needs OMAP3 hardware, IOMMU, clocks, regulators, syscon, and OF graph endpoints. Test allmodconfig/allyesconfig compile paths, `VIDEO_OMAP3_DEBUG`, and real DT probe with dependent sensor subdevices.
