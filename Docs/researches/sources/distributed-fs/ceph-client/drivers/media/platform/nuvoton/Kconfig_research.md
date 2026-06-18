# sources/distributed-fs/ceph-client/drivers/media/platform/nuvoton/Kconfig

## Purpose
This Kconfig file adds the Nuvoton media platform driver menu and the switch for the NPCM video capture/encode engine.

## Important APIs, Types, and Functions
`VIDEO_NPCM_VCD_ECE` is a tristate option for the NPCM Video Capture/Differentiation Engine and Encoding Compression Engine driver. It depends on `V4L_PLATFORM_DRIVERS`, `VIDEO_DEV`, and `ARCH_NPCM || COMPILE_TEST`, and selects `VIDEOBUF2_DMA_CONTIG`.

## Control Flow
When enabled, the build includes `npcm-video.o` and exposes a V4L2 capture driver for NPCM VCD/ECE hardware. No other options are selected here, so media-controller integration is not required by this driver.

## State and Persistence
Kconfig state is persisted in the kernel configuration and determines whether the driver is compiled as built-in, module, or not at all.

## Dependencies and Integration Points
The option integrates the Nuvoton BMC capture engine into the Linux media platform driver menu and gates it to NPCM SoCs or compile-test builds.

## Risks and Edge Cases
The driver also uses controls, DV timings, reserved memory, syscon regmaps, reset controls, and optional ECE resources; those are resolved through broader kernel dependencies and DT at build/runtime rather than all being explicit Kconfig selects.

## Test Signals
Build with `ARCH_NPCM`, with `COMPILE_TEST`, as module and built-in, and with the option disabled to ensure no stale object references remain.
