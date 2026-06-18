# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/goya/asic_reg/mmu_masks.h

## Purpose

`mmu_masks.h` defines generated field masks and shifts for the Goya MMU control block. It describes input FIFO thresholds, MMU enable, ordering controls, feature enable bits, virtual-address ordering masks, DDR-size/scrambler setup, memory-initialization busy state, SPI mask/cause, and page/access error capture fields.

## Important APIs, types, and data

The exported macros are `MMU_*_SHIFT` and `MMU_*_MASK`. `MMU_INPUT_FIFO_THRESHOLD` has separate 3-bit thresholds for PCI, PSOC, DMA, CPU, MME, TPC, and other clients. `MMU_MMU_ENABLE` has a single enable bit. `MMU_FORCE_ORDERING` has weak and strong ordering bits for DMA, PSOC, PCI, CPU, MME, TPC, and default traffic. `MMU_FEATURE_ENABLE` covers VA ordering, clean linked-list behavior, hop-offset enable, OBI ordering, strong-ordering reads, and trace enable. Ordering masks cover VA bits 31:7 and 49:32. Scrambler fields select address bit and single-DDR mode/ID. Error capture fields combine VA high bits and an entry-valid bit, with separate low-VA registers.

## Control flow

The file has no control flow. Driver MMU initialization composes values with these masks to set thresholds, ordering, feature, scrambler, and enable registers. Fault-handling paths read page/access capture fields, test `ENTRY_VALID`, combine high and low VA pieces, report the fault, and clear or rearm capture state according to device policy.

## State and persistence behavior

The described registers are persistent MMU hardware configuration until reset or reprogramming. Enabling the MMU and setting ordering/scrambler behavior affects all translated client traffic, including MME and TPC. Page/access error capture registers hold latched fault addresses until cleared. The header itself is stateless.

## Dependencies and integration points

This header pairs with `mmu_regs.h` for offsets and with common HabanaLabs MMU code for page-table management. Goya platform constants define reserved page-table/cache/default-page memory, while the common driver provides hop shifts/masks, mapping operations, debugfs access, and fault reporting. MME/QMAN ASID fields depend on the MMU configuration described here.

## Risks and edge cases

Ordering and scrambler bits affect correctness beyond the MMU block; wrong values can cause subtle memory consistency or address-placement failures. Fault addresses are split across two registers and only valid when the valid bit is set. Threshold fields are narrow and can silently truncate. Page/access captures use VA bits 49:32 and 31:0, so callers must reconstruct addresses with correct width and shifting.

## Test signals

Build coverage should catch missing macros. Runtime signals include successful MMU enable during Goya initialization, correct mapping/unmapping behavior, no unexpected page/access errors during normal MME/TPC/DMA traffic, deliberate invalid-access tests that produce accurate captured VAs, and stable behavior under ordering-sensitive workloads.
