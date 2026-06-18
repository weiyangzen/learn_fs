# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_iro_hsi.h

## Purpose
`qed_iro_hsi.h` is a generated-style HSI header that enumerates internal RAM offset entries and provides accessor macros for storm RAM/GTT structures. It lets C code compute firmware-memory offsets from `IRO[]` base, size, and multiplier fields installed from `iro_arr`.

## Important APIs, Types, and Functions
- The anonymous enum defines IRO indices for LL2, ETH, iSCSI, FCoE, RDMA/RoCE/iWARP, TOE, overlay buffers, assert levels, integration test data, queue zones, producer/consumer locations, and statistics blocks.
- Macros such as `TSTORM_ISCSI_RX_STATS_OFFSET()`, `MSTORM_SCSI_BDQ_EXT_PROD_GTT_OFFSET()`, `XSTORM_PQ_INFO_OFFSET()`, and `PSTORM_RDMA_QUEUE_STAT_OFFSET()` compute byte offsets from `IRO[index].base + argument * multiplier`.
- Companion `*_SIZE` macros expose the firmware-defined structure size for each IRO entry.
- `E4_IRO_ARR_OFFSET` selects the per-chip offset into the flat IRO array.

## Control Flow
There is no executable control flow. Callers include this header, ensure `IRO` points at the active chip's IRO triplets, and use macros to compute RAM offsets for `qed_memcpy_from()`, `qed_wr()`, DMAE writes, or GTT producer/consumer addresses.

## State and Persistence
The macros read the global/device `IRO` array, which is assigned during init. They do not own memory but are a key contract for firmware-visible RAM layout.

## Dependencies and Integration Points
The header depends on `struct iro`/`IRO` definitions from QED HSI/core headers. It is consumed by init firmware helpers, iSCSI stats and BDQ producer mapping, LL2, Ethernet, RDMA, overlay RAM initialization, and queue-manager PQ info writes.

## Risks
- Any mismatch between enum order and `iro_arr` triplets corrupts all computed firmware offsets.
- Macros do not validate arguments, so invalid PF ids, queue ids, BDQ ids, or stat ids compute invalid offsets.
- Size macros must match the structures copied by callers; stale firmware layout can cause short or overlarge RAM copies.

## Test Signals
Device bring-up, protocol stats reads, BDQ producer updates, overlay address programming, and queue producer/consumer accesses succeeding without GRC timeouts are practical validation. Firmware ABI changes should trigger regenerated enum and array updates together.
