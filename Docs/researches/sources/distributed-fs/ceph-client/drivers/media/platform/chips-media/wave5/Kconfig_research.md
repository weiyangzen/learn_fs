# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/wave5/Kconfig

## Purpose
`wave5/Kconfig` declares the `VIDEO_WAVE_VPU` kernel configuration option for the Chips&Media Wave5 stateful codec driver. It controls whether the Wave5 encoder/decoder driver is built and states the dependency envelope needed by the source files in this directory.

## Important Configuration
`VIDEO_WAVE_VPU` is a tristate named "Chips&Media Wave Codec Driver". It depends on V4L mem2mem driver support, `VIDEO_DEV`, device tree (`OF`), and either TI K3 architecture (`ARCH_K3`) or `COMPILE_TEST`. It selects `VIDEOBUF2_DMA_CONTIG`, `VIDEOBUF2_VMALLOC`, `V4L2_MEM2MEM_DEV`, and `GENERIC_ALLOCATOR`.

## Control Flow and Integration
The option feeds the Wave5 Makefile via `obj-$(CONFIG_VIDEO_WAVE_VPU) += wave5.o`. Enabling it compiles the platform codec driver and causes module output named `wave5` when set to module. The selected dependencies match the driver's use of vb2 DMA-contiguous queues, vmalloc helpers, V4L2 mem2mem scheduling, and gen_pool SRAM allocation.

## State and Persistence
Kconfig has no runtime state. It persists as build configuration in `.config`, determines whether objects are present in the kernel or as a module, and gates runtime availability of Wave5 video devices.

## Dependencies and Risks
The architecture restriction limits normal builds to K3 unless compile-tested. Missing selected dependencies would break compilation or runtime queue setup. The help text says HEVC and H264 are supported; changes to actual format support should keep this text aligned.

## Test Signals
Signals are `allyesconfig`/`allmodconfig` compile coverage, `COMPILE_TEST` builds on non-K3 architectures, module build naming, and runtime probe on a DT platform with Wave5 hardware.
