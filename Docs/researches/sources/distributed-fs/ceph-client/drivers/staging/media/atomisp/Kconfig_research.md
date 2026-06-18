# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/Kconfig

## Purpose
Defines Kconfig for Intel Atom ISP staging support and its sensor subdrivers.

## Important Entries and Integration
`INTEL_ATOMISP` is a bool depending on X86, EFI, PCI, ACPI, and COMMON_CLK, and selects IOSF_MBI and MEDIA_CONTROLLER. `VIDEO_ATOMISP` is tristate and depends on the AtomISP platform plus VIDEO_DEV, INT3472, IPU bridge, media PCI support, PMIC opregion, and I2C; it selects V4L2 fwnode, IOSF_MBI, videobuf2 vmalloc, and V4L2 subdev API. When `VIDEO_ATOMISP` is enabled, the i2c sensor Kconfig is sourced.

## Risks and Test Signals
This staging driver has many platform dependencies, so build coverage must use an x86 ACPI PCI configuration. Test signals include Kconfig dependency resolution and sensor submenu visibility only when `VIDEO_ATOMISP` is enabled.
