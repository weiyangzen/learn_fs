# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/css_2401_system/host/isys_dma_private.h

Purpose: implements private ISYS DMA register load/store helpers.

Important APIs/types/functions: `isys2401_dma_reg_store()` computes `ISYS2401_DMA_BASE[dma_id] + reg * sizeof(hrt_data)` and stores a 32-bit value. `isys2401_dma_reg_load()` computes the same address, loads a 32-bit value, and prints diagnostics.

Control flow: both helpers assert valid DMA ID and base address, calculate a word-indexed MMIO address, then call `ia_css_device_store_uint32()` or `ia_css_device_load_uint32()`.

State and persistence: store mutates hardware registers; load has no software state except debug output.

Dependencies and integration: depends on ISYS DMA public declarations, `device_access`, assertions, DMA register definitions, and print support.

Risks and test signals: functions are defined in a header, so include/storage-class discipline matters. Register IDs are not range checked beyond the caller's use. Tests should validate address arithmetic, base-address invalid assertions, and noisy print behavior in hot paths.
