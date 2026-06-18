<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_regs.h

## Purpose
`arc_farm_kdma_ctx_regs.h` is the generated address map for the `ARC_FARM_KDMA_CTX` DMA context register bank in the `0x4E8B860-0x4E8B8EC` range. It defines 36 context registers for rate limiting, power behavior, tensor/linear DMA dimensions, strides, source/destination bases and offsets, write-completion metadata, and the final context commit trigger.

## Important APIs, types, and functions
The file exports `mm...` constants only. Key programming registers are `RATE_LIM_TKN`, `PWRLP`, `TE_NUMROWS`, `IDX`, `IDX_INC`, `CTRL`, source `TSIZE` and `STRIDE` registers for dimensions 0-4, destination `TSIZE` and `STRIDE` registers, `WR_COMP_ADDR_HI/LO`, `WR_COMP_WDATA`, `SRC_OFFSET`, `DST_OFFSET`, `SRC_BASE`, `DST_BASE`, `DST_TSIZE_0`, and `COMMIT`. These addresses pair with the corresponding `*_CTX_MASKS_H_` header, where `CTRL` selects transpose, dtype, compression/decompression, and read-uncacheable behavior and `COMMIT` selects which context fields are latched.

## Control flow
There is no executable code. Driver or firmware code writes a context in dependency order: set rate/power and index controls, program tensor sizes and strides, install source and destination address components, optionally configure write-completion data, and finally write `COMMIT` to latch the descriptor into the DMA engine. Status/error observation happens through the sibling DMA core register bank rather than this context map.

## State and persistence behavior
The programmed context is hardware state. It persists until overwritten, reset, or superseded by a later commit. Because the commit register can selectively source stride/offset/base values, partial context updates can intentionally reuse earlier fields; the same behavior is risky if software assumes a clean context after reset without actually initializing every relevant field.

## Dependencies and integration points
This header integrates with the matching DMA context mask header, the associated DMA core address/mask headers, Gaudi2 queue command generation, and firmware routines that prepare DMA descriptors. The register sequence also depends on AXUSER context programming when ASID, MMU bypass, or snoop attributes must match the programmed source and destination ranges.

## Risks and edge cases
The high-risk cases are stale context fields, high/low address halves programmed in the wrong order, tensor stride/size mismatches, and writing `COMMIT` before all selected fields are valid. Compression/decompression, transpose, and dtype bits are compactly encoded and can corrupt data if masks are mismatched or if callers treat this generated file as self-describing behavior rather than address data.

## Test signals
Validation should include linear and tensor DMA copies, 64-bit source/destination addresses, compression and decompression paths when supported, write-completion generation, reset/reinitialize cycles, and error injection for invalid size/stride combinations. Useful debug evidence is matching DMA core status context ids, idle/busy transitions, and no HB/LB read/write errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_regs.h -->
