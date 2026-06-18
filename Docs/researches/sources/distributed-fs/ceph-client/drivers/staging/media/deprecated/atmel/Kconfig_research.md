# sources/distributed-fs/ceph-client/drivers/staging/media/deprecated/atmel/Kconfig

## Purpose
This Kconfig fragment declares deprecated Atmel/Microchip Image Sensor Controller staging drivers: SAMA5D2 ISC, SAMA7G5 XISC, and their hidden shared base.

## Important Options
`VIDEO_ATMEL_ISC` is a tristate for the deprecated SAMA5D2-style Image Sensor Controller. It depends on V4L platform drivers, video device and common clock support, `ARCH_AT91 || COMPILE_TEST`, and excludes `VIDEO_MICROCHIP_ISC_BASE` unless compile-testing. It selects media controller, V4L2 subdev API, DMA-contig vb2, regmap MMIO, V4L2 fwnode, and `VIDEO_ATMEL_ISC_BASE`.

`VIDEO_ATMEL_XISC` is the analogous deprecated eXtended ISC option for SAMA7G5. `VIDEO_ATMEL_ISC_BASE` is a hidden tristate defaulting to `n` and selected by both public options.

## Control Flow and State
Kconfig has no runtime flow. It controls which objects from the Atmel staging media directory are built and ensures the shared base is included when either SoC-specific driver is enabled.

## Dependencies and Integration Points
It integrates with the Linux media platform driver menu, V4L2/media controller subsystems, common clock framework, regmap MMIO, and the newer non-staging Microchip ISC base through the conflict dependency.

## Risks and Test Signals
Risks include deprecation/removal timing, configuration conflicts with the newer Microchip driver, and missing selected dependencies leading to link failures if symbols move. Test signals are `allyesconfig`/`COMPILE_TEST` builds, ARCH_AT91 builds, disabled conflict with `VIDEO_MICROCHIP_ISC_BASE`, and object inclusion matching the Makefile.
