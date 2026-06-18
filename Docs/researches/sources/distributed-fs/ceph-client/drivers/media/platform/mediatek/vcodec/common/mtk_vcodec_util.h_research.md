# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_util.h

## Purpose
This header defines shared vcodec memory structs, logging/debug macros, and utility function declarations.

## Important APIs, Types, And Functions
`struct mtk_vcodec_mem` holds size, virtual address, and DMA address. `struct mtk_vcodec_fb` holds framebuffer size and DMA address. Logging macros produce V4L2 and vcodec scoped messages, with debug-level gating under `CONFIG_DEBUG_FS`. Declarations expose register-base lookup, VDEC_SYS write, DMA allocation/free, current decoder context setters/getters, and hardware subdevice lookup.

## Control Flow
No direct execution. Macros and function declarations are used throughout worker, firmware, interrupt, and probe code.

## State, Persistence, And Dependencies
Debug state is held in exported globals when debugfs is enabled. Memory descriptors are caller-owned. Dependencies include Linux types and DMA direction plus decoder forward declarations.

## Integration Points
Included by decoder/encoder drivers, firmware backends, debugfs, and codec interface implementations.

## Risks
Macros evaluate arguments in logging contexts and assume valid platform devices. Debug macros change behavior depending on debugfs config. Function APIs use `void *priv` for encoder/decoder polymorphism.

## Test Signals
Builds with debugfs enabled/disabled, logging at different levels, DMA helper users from decoder and encoder, and current-context helper coverage.
