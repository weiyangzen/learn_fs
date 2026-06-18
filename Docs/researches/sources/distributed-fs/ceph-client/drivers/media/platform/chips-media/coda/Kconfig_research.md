# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/Kconfig

## Purpose
This Kconfig file declares the Chips&Media Coda mem2mem video codec driver and the related i.MX VDOA helper option.

## Important APIs, Types, and Functions
`VIDEO_CODA` is a tristate for Coda multi-standard codec IP. It depends on `V4L_MEM2MEM_DRIVERS`, `VIDEO_DEV`, `OF`, and `ARCH_MXC || COMPILE_TEST`. It selects `SRAM`, `VIDEOBUF2_DMA_CONTIG`, `VIDEOBUF2_VMALLOC`, `V4L2_JPEG_HELPER`, `V4L2_MEM2MEM_DEV`, and `GENERIC_ALLOCATOR`. `VIDEO_IMX_VDOA` defaults to `VIDEO_CODA` on `SOC_IMX6Q || COMPILE_TEST`.

## Control Flow
Selecting `VIDEO_CODA` causes the child Makefile to build the aggregate `coda-vpu.o`. `VIDEO_IMX_VDOA` controls the optional `imx-vdoa.o` helper used on i.MX6Q-style integrations.

## State and Persistence
Selections persist in the kernel configuration. Runtime codec contexts, queues, firmware, and SRAM allocation are handled by the Coda C sources.

## Dependencies and Integration Points
The option connects Coda to the V4L2 mem2mem framework, vb2 DMA/vmalloc allocators, SRAM/genalloc memory management, OF platform probing, and JPEG helper code.

## Risks and Edge Cases
The driver needs both DMA-contiguous and vmalloc vb2 allocators; dropping either selection can break supported queue paths. Architecture gating focuses normal visibility on i.MX while preserving compile-test coverage.

## Test Signals
Build with `CONFIG_VIDEO_CODA=m`, `CONFIG_VIDEO_IMX_VDOA=m`, i.MX configs, and `COMPILE_TEST`. Confirm codec modules link with mem2mem, SRAM, and JPEG helper dependencies.
