<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_stlb_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_stlb_regs.h

## Purpose
`dcore0_hmmu0_stlb_regs.h` is the generated address map for the DCORE0 HMMU0 STLB bank, prototype `STLB`. It defines 59 register addresses in the 0x4081000-0x408114C range for STLB status, ASID/root page table setup, invalidation, feature/cache/hop configuration, thresholds, interrupts, range invalidation, and ASID scrambler polynomial rows.

## Important APIs, types, and functions
The exported constants include `BUSY`, `ASID`, root `HOP0` PA low/high registers, cache invalidation command and base registers, `STLB_FEATURE_EN`, `STLB_AXI_CACHE`, `HOP_CONFIGURATION`, lookup masks, invalidate-all/page-size/consumer/hit/set registers, SRAM init, memory cache invalidation/status/base/config, per-hop threshold registers, multi-hit interrupt clear/mask, L0 cache and ARPROT registers, range invalidation start/end controls, ASID scrambler control, and polynomial matrix registers 0-18.

## Control flow
There is no code in the file. MMU setup writes root table, ASID, feature, hop, cache, and scrambler registers. Page-table update paths use the invalidation and range invalidation addresses, then poll status/busy registers before allowing engines to rely on new translations. Fault/recovery code may read busy and cache status during MMU reset.

## State and persistence behavior
The STLB keeps persistent translation-cache configuration and live invalidation state. Root-hop addresses, ASID, feature bits, thresholds, cache config, and scrambler settings persist until reset/reprogramming. Invalidation status is transient but must be observed to avoid stale translations.

## Dependencies and integration points
This address map integrates with `dcore0_hmmu0_stlb_masks.h`, HMMU MMU registers, page-table allocation, ASID management, cache invalidation routines, and memory fault recovery.

## Risks and edge cases
Risks include using the wrong DCORE/HMMU STLB instance, writing invalidation ranges with mismatched MSB/LSB values, enabling lookup before root-hop setup, and failing to wait for invalidation completion. Address drift would cause memory-translation bugs that may first appear as engine DMA faults.

## Test signals
Tests should cover STLB enable and lookup, full/range/ASID invalidation, root table changes, page remap/unmap stress, busy/done polling, multi-hit interrupt behavior, and reset reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_hmmu0_stlb_regs.h -->
