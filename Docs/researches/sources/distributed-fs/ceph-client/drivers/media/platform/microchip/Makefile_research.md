# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/Makefile

## Purpose
This Makefile maps the Microchip media Kconfig symbols to kernel objects and composes the product-specific modules from common and per-SoC source files.

## Important APIs, Types, and Functions
`microchip-isc-objs` contains `microchip-sama5d2-isc.o`, `microchip-xisc-objs` contains `microchip-sama7g5-isc.o`, and `microchip-isc-common-objs` contains `microchip-isc-base.o`, `microchip-isc-clk.o`, and `microchip-isc-scaler.o`. `obj-$(CONFIG_VIDEO_MICROCHIP_*)` lines select the common, product, and CSI2DC objects.

## Control Flow
When `VIDEO_MICROCHIP_ISC_BASE` is selected, the common support module is built. The SAMA5D2 and SAMA7G5 front-end modules link against exported common symbols. CSI2DC is built as its own module when configured.

## State and Persistence
This file only influences build-time object aggregation. It does not define runtime state.

## Dependencies and Integration Points
The object layout matches the split between common exported ISC helpers and product-specific platform drivers. It integrates with Linux kbuild and the Kconfig symbols in the same directory.

## Risks and Edge Cases
The product modules depend on common exports such as `microchip_isc_interrupt`, `microchip_isc_pipeline_init`, and `isc_mc_init`; mismatched Kconfig selects or object naming changes would produce unresolved symbols.

## Test Signals
Build logs should show `microchip-isc-common.o` built when ISC or XISC is enabled, and module link should include the correct product object for `microchip-isc.ko` and `microchip-xisc.ko`.
