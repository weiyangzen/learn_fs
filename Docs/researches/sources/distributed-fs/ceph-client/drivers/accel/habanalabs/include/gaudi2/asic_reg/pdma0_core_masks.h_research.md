<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_masks.h

## Purpose
`pdma0_core_masks.h` provides generated bit shifts and masks for PDMA0 core registers. It is the bitfield companion for `pdma0_core_regs.h`.

## Important APIs, types, and functions
The file exports `PDMA0_CORE_*_SHIFT` and `*_MASK` macros. Field groups cover core enable, halt, flush, protection value, clock gating, read/write global controls, HBW/LBW max outstanding and max transfer size, ARCACHE/AWCACHE and inflight limits, memory-init busy/done/status, error message address/write data, status registers, and selected read-context status fields.

## Control flow
There is no executable control flow. Driver code uses these masks for read-modify-write programming of PDMA enable/halt/flush, tuning outstanding transactions, setting cache/protection metadata, checking memory initialization, and decoding error/status registers.

## State and persistence
The masks are stateless; the underlying PDMA core registers contain persistent enable/halt, outstanding, cache, error, and status state until reset or reprogramming.

## Dependencies and integration points
Included by `gaudi2_regs.h`, this header pairs with `pdma0_core_regs.h` and is used by PDMA init/reset/error handling. It also relates to `pdma0_core_special_masks.h` for special/global error and security fields.

## Risks and test signals
Mask drift can corrupt adjacent control fields and cause hard-to-debug DMA hangs. Test signals include successful enable/halt/flush cycles, correct max outstanding/size behavior under stress, decoded error-message addresses matching injected faults, and status masks reporting active/idle context accurately.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/pdma0_core_masks.h -->
