<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_masks.h

## Purpose
`arc_farm_kdma_ctx_masks.h` is the generated bitfield map for the `ARC_FARM_KDMA_CTX` `DMA_CORE_CTX` register bank. It defines 126 shift/mask macros used to compose DMA context descriptors for rate limits, power-low behavior, tensor/linear dimensions, control flags, address offsets, base addresses, write completion, and commit selection.

## Important APIs, types, and functions
The macro namespace covers `RATE_LIM_TKN` read/write token fields, `PWRLP` data/enable, full-width tensor sizes and strides, context index and increment, `CTRL` bits for transpose, dtype, compression, decompression, and read-uncacheable mode, source/destination offset and base fields, write-completion address/data fields, destination size 0, and `COMMIT` bits that select which context components are latched, including variants that source offsets/strides from corresponding destination fields and the `LIN` linear-DMA selector.

## Control flow
The header is not executable. Software uses these masks while building context writes before the final commit register access. The control-flow dependency is important: fields named in `COMMIT` determine which earlier context registers are consumed, so programming code must update all selected registers first and then write a commit value assembled with these masks.

## State and persistence behavior
No software state is stored here. The masks define hardware state layout for the DMA context registers. Context state can persist across operations, and selective commit semantics mean a new descriptor can inherit fields from previous state if the commit mask omits them or if software fails to initialize them.

## Dependencies and integration points
This header is coupled to the matching `*_CTX_REGS_H_` file, the `DMA_CORE` status/error bank, AXUSER attributes, and any descriptor-generation code in the Gaudi2 driver or firmware. It is also tied to hardware packet formats when queue commands write context registers indirectly.

## Risks and edge cases
The main risks are data corruption from size/stride/address-field mismatch, accidental carryover of stale context fields, using compression/decompression/dtype combinations unsupported by the current engine mode, and writing high/low address halves with values beyond hardware-accepted address width. Since all masks are numeric constants, compile success does not prove semantic correctness.

## Test signals
Tests should exercise full context programming for linear and tensor DMA, partial commit behavior, boundary sizes and strides, 64-bit addresses, compression/decompression controls, and reset paths that guarantee context fields start from expected defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/arc_farm_kdma_ctx_masks.h -->
