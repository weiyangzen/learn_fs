# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/dma_macro_masks.h

Purpose: auto-generated bitfield definitions for the Goya DMA macro block. It describes field shifts and masks for address range routing, read/write enable and credit throttling, SRAM busy status, and RAZWI transaction capture fields.

Important APIs/types/functions: the API is the `DMA_MACRO_*_SHIFT` and `DMA_MACRO_*_MASK` macro set. Key fields include low-bandwidth range hit/mask/base with 16 entries and 26-bit values, high-bandwidth range hit/mask/base with 8 entries and 50-bit address split into `49_32` and `31_0`, `WRITE_EN`, `WRITE_CREDIT`, `READ_EN`, `READ_CREDIT`, and RAZWI valid/id fields for LBW and HBW reads/writes.

Control flow: there is no executable flow. Driver code combines these masks with `dma_macro_regs.h` addresses to configure the DMA macro's routing windows and credits or to decode captured RAZWI status.

State and persistence: bitfields describe hardware register state. Range tables and credit enables remain in the DMA macro registers until changed or reset. RAZWI valid/id fields persist as hardware diagnostic state until cleared by the device-specific procedure.

Dependencies and integration: pulled into `goya_regs.h`, then `goya_masks.h`. Register addresses live in `dma_macro_regs.h`, block bases in `goya_blocks.h`, and CoreSight/debug visibility for the DMA macro is listed in `goya_coresight.c`.

Risks: masks encode hardware contract width. A wrong high-address split, range mask, or hit-block field could route requests to an unintended target or fail to catch forbidden access. RAZWI IDs are diagnostic/security-relevant; decoding them with the wrong mask can misidentify the offending initiator.

Test signals: compile-time use in DMA setup code, register readback of configured HBW/LBW ranges, successful DMA routing across expected memory windows, RAZWI/error-injection diagnostics, and no unexpected SRAM-busy or credit starvation during stress tests.
