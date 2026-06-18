# sources/distributed-fs/ceph-client/drivers/media/platform/imagination/e5010-mmu-regs.h

## Purpose
This header is a generated-style register map for the Imagination E5010 JPEG encoder MMU block. It does not implement logic; it defines offsets, strides, entry counts, bit masks, shifts, repetition counts, and the byte size needed by the E5010 hardware code to program address translation, tiling, request policy, fault handling, statistics, and version discovery registers.

## Important APIs, Types, And Constants
There are no functions or types. The public surface is a collection of `MMU_*` macros. The key groups are directory base registers (`MMU_MMU_DIR_BASE_ADDR_*`), tile configuration and bounds (`MMU_MMU_TILE_CFG_*`, `MMU_MMU_TILE_MIN_ADDR_*`, `MMU_MMU_TILE_MAX_ADDR_*`), control registers (`MMU_MMU_CONTROL0_*`, `MMU_MMU_CONTROL1_*`), address mode (`MMU_MMU_ADDRESS_CONTROL_*`), hardware capability/status (`MMU_MMU_CONFIG0_*`, `MMU_MMU_CONFIG1_*`, `MMU_MMU_STATUS0_*`, `MMU_MMU_STATUS1_*`), request/protocol fault registers, bandwidth/stall/latency counters, statistics reset bits, version fields, and `MMU_BYTE_SIZE`.

## Control Flow And State
The file has no runtime control flow and no persistent software state. Its constants are consumed by MMIO read/write helpers elsewhere in the E5010 driver. The hardware state represented by the macros is persistent only in the device registers: MMU enable/bypass state, page directory addresses, tile windows, pause/reset/flush/invalidate commands, fault status, and performance counters.

## Dependencies And Integration Points
This header is intended to be included by E5010 JPEG encoder hardware code, alongside the core and encoder register headers in the same `imagination` platform directory. The only unusual symbol is `IMG_TRUE` in `MMU_MMU_ADDRESS_CONTROL_TRUSTED`, which must be provided by another included Imagination header or removed if unused. Register users must combine masks and shifts correctly and must respect array strides and entry counts for banks and tiles.

## Risks
Register maps are fragile: a wrong offset, bit mask, or shift silently programs hardware incorrectly. The repeated-bit fields on `CONTROL1`, `BANK_INDEX`, `REQUEST_PRIORITY_ENABLE`, and `MEM_REQ` expose array-like fields packed into one register, so callers must not assume a single bit. Fault clear, pause, flush, invalidate, and soft reset bits are write-command style fields and should be sequenced carefully to avoid losing diagnostic state.

## Test Signals
Build coverage should compile all E5010 files that include this header. Runtime validation should check that MMU enable/bypass configuration, directory base programming, cache invalidation/flush, and fault clear paths produce expected hardware behavior. Fault injection or malformed DMA address tests should verify that status and protocol fault fields decode correctly. Register dump tests can compare offsets against the E5010 hardware reference.
