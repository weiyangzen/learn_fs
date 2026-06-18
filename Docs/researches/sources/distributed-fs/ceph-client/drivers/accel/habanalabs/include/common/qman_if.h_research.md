# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/common/qman_if.h

## Purpose

`qman_if.h` defines the host-visible queue-manager data structures shared by HabanaLabs software and hardware queue managers. It describes the primary queue buffer descriptor (`struct hl_bd`) and completion queue entry (`struct hl_cq_entry`) layouts, along with the bit fields used by software and hardware in their control/status words.

## Important APIs, Types, and Constants

`struct hl_bd` contains a little-endian 64-bit pointer, 32-bit length, and 32-bit control word. `HL_BD_SIZE` exposes the descriptor size for queue allocation and hardware programming. The BD software control fields include `BD_CTL_REPEAT_VALID_*` and `BD_CTL_SHADOW_INDEX_*`; hardware completion-related fields include `BD_CTL_COMP_OFFSET_*` and `BD_CTL_COMP_DATA_*`.

`struct hl_cq_entry` contains one little-endian 32-bit data word. `HL_CQ_ENTRY_SIZE` exposes its size. Completion fields include `CQ_ENTRY_READY_*`, `CQ_ENTRY_SHADOW_INDEX_VALID_*`, and `CQ_ENTRY_SHADOW_INDEX_*`, with the shadow-index location deliberately matching the BD shadow-index field.

The use of `__le64` and `__le32` is part of the ABI: queue memory is little-endian regardless of host CPU representation, and driver code must use the corresponding conversion helpers when constructing or reading descriptors.

## Control Flow

This header has no executable control flow. Runtime behavior appears in users such as Gaudi queue setup and submission paths. For example, `gaudi_pqe_write()` treats a `struct hl_bd` as two 64-bit words and copies it into a primary queue entry because the queue lives in host memory. Producer code fills BD fields, rings a queue doorbell or writes a PI register, and hardware later consumes the BD. Completion consumers read `struct hl_cq_entry`, check the ready bit, optionally use the shadow-index-valid and shadow-index fields, and then advance queue state.

## State and Persistence Behavior

The structures define persistent queue memory content shared between the host driver, firmware/CP, and ASIC queue hardware. The header itself owns no state, but any layout change would alter the hardware ABI for in-memory descriptors. BD and CQ words persist in coherent DMA buffers or CPU-accessible memory until overwritten by producer/consumer queue logic.

## Dependencies and Integration Points

The file depends only on `<linux/types.h>`. It is integrated into device-specific queue code through the common HabanaLabs queue abstraction and is used by Gaudi/Goya-style queue managers that program PQ/CQ base addresses and sizes using ASIC register headers. The shadow-index fields tie software bookkeeping to hardware completions, while completion offset/data fields let command processors emit completion writes.

## Risks

The key risk is ABI mismatch. Structure packing, endianness, or bit-field constant changes can break descriptor parsing by hardware. The file intentionally avoids C bitfields, which is good for ABI stability, but callers must still mask and shift correctly. Because `gaudi_pqe_write()` copies the descriptor as raw 64-bit words, any future change to descriptor size or alignment would need coordinated updates.

## Test Signals

Queue-submission tests should verify that BD sizes match hardware expectations, descriptors are written little-endian, completions set `CQ_ENTRY_READY_MASK`, and shadow-index values round-trip correctly. Stress tests should cover queue wraparound, repeated BD handling when `BD_CTL_REPEAT_VALID_MASK` is set or clear, and mixed command streams that generate completion data.
