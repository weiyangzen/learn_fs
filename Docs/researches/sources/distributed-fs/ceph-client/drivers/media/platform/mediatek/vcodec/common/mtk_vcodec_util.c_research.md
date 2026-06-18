# sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/common/mtk_vcodec_util.c

## Purpose
This file implements shared utility functions for vcodec register access, DMA buffer allocation, VDEC_SYS writes, hardware subdevice lookup, and current decoder context tracking.

## Important APIs, Types, And Functions
`mtk_vcodec_get_reg_addr()` bounds-checks register-base indexes. `mtk_vcodec_write_vdecsys()` writes through regmap when present or MMIO otherwise. `mtk_vcodec_mem_alloc()` and `mtk_vcodec_mem_free()` allocate/free DMA memory for decoder or encoder contexts. `mtk_vcodec_get_hw_dev()` returns decoder hardware subdevice state. `mtk_vcodec_set_curr_ctx()` and `mtk_vcodec_get_curr_ctx()` update/read the current context either on the main device or per subdevice under `irqlock`. Debug globals are exported under `CONFIG_DEBUG_FS`.

## Control Flow
Workers allocate firmware buffers and set current context before hardware execution. Interrupt handlers use current context lookup to wake the right waitqueue. PM and codec-specific code use VDEC_SYS writes and register access during hardware setup.

## State, Persistence, And Dependencies
It mutates DMA memory descriptors and decoder current-context pointers. No persistence. Dependencies include decoder/encoder private structs, regmap, DMA APIs, subdevice hardware structs, and debugfs globals.

## Integration Points
Common to decoder, encoder, interrupt handlers, firmware codec implementations, and debugfs controls.

## Risks
Like other common helpers, instance type is inferred from the first context field. Allocation uses `dma_alloc_attrs(... DMA_ATTR_ALLOC_SINGLE_PAGES)` but free uses `dma_free_coherent()`, which may be intentional API compatibility or a review point. `mtk_vcodec_get_hw_dev()` logs and returns NULL for invalid/missing subdevices; callers must handle it.

## Test Signals
DMA alloc/free fault injection, register index bounds tests, regmap and MMIO VDEC_SYS paths, multi-hardware current-context lookup, and debugfs variable changes.
