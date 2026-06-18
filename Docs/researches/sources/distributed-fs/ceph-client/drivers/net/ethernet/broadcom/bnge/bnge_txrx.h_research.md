# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/bnge_txrx.h

## Purpose

`bnge_txrx.h` is the shared TX/RX hot-path interface for the `bnge` netdev driver. It exposes the functions implemented in `bnge_txrx.c`, defines inline doorbell and TX-space helpers, and centralizes the ring indexing, descriptor-validity, opaque TX completion encoding, and descriptor-count constants used by the TX/RX data path.

The header is included by the TX/RX implementation and other driver modules that need to register interrupt/NAPI/netdev operations or reuse RX buffers. It includes `<linux/bnge/hsi.h>` for hardware completion/descriptor constants and `bnge_netdev.h` for driver ring structures, doorbell metadata, and descriptor arrays.

## Important APIs, macros, and declarations

- `bnge_tx_avail(struct bnge_net *bn, const struct bnge_tx_ring_info *txr)` computes free TX descriptors from `tx_prod - tx_cons`, using `READ_ONCE()` and `tx_ring_mask` to tolerate concurrent NAPI cleanup versus transmit checks.
- `bnge_writeq_relaxed(struct bnge_dev *bd, u64 val, void __iomem *addr)` writes 64-bit MMIO doorbells. On 32-bit platforms it serializes split low/high writes with `bd->db_lock`; on 64-bit it uses `writeq_relaxed()`.
- `bnge_db_write_relaxed(struct bnge_net *bn, struct bnge_db_info *db, u32 idx)` writes TX/RX doorbells without ordering guarantees by combining `db_key64`, `DB_RING_IDX()`, and the doorbell MMIO address.
- TX opaque encoding:
  - `SET_TX_OPAQUE()` packs TX NAPI/ring index, BD count, and descriptor index into the opaque field returned by TX completions.
  - `TX_OPAQUE_IDX()`, `TX_OPAQUE_RING()`, `TX_OPAQUE_BDS()`, and `TX_OPAQUE_PROD()` decode completion ownership and derive the completed producer.
  - `TX_BD_CNT(n)` formats a descriptor count into TX BD flags.
- TX sizing constants:
  - `TX_MAX_BD_CNT` is 32.
  - `TX_MAX_FRAGS` is `TX_MAX_BD_CNT - 2`, because the TX path always needs a long BD and an extension BD before fragment BDs.
  - `BNGE_MIN_TX_DESC_CNT` is `MAX_SKB_FRAGS + 2`, mirroring that descriptor requirement.
- Ring/page indexing macros:
  - `RX_RING()`, `RX_AGG_RING()`, `TX_RING()`, and `CP_RING()` choose the descriptor page for a masked index.
  - `RX_IDX()`, `TX_IDX()`, and `CP_IDX()` choose the descriptor offset within a page.
  - `RING_RX()`, `RING_RX_AGG()`, `SW_TX_RING()`, and `RING_CMP()` mask raw producer/consumer values into ring ranges.
  - `NEXT_RX()`, `NEXT_RX_AGG()`, `NEXT_TX()`, `ADV_RAW_CMP()`, `NEXT_RAW_CMP()`, and `NEXT_CMP()` advance producer/consumer values.
- Completion-validity and type macros:
  - `TX_CMP_VALID()`, `RX_CMP_VALID()`, `RX_AGG_CMP_VALID()`, and `NQ_CMP_VALID()` compare descriptor valid bits against the ring polarity bit `bn->cp_bit`.
  - `TX_CMP_TYPE()` and `RX_CMP_TYPE()` extract hardware completion types.
  - `RX_CMP_ITYPES()` extracts RX packet type/hash hint bits.
  - `RX_CMP_CFA_CODE()` extracts the CFA code from an RX completion extension.
- Exported function prototypes:
  - `bnge_msix()` for IRQ registration.
  - `bnge_start_xmit()` for `ndo_start_xmit`.
  - `bnge_reuse_rx_data()` for RX buffer recycling helpers.
  - `bnge_napi_poll()` for NAPI registration.
  - `bnge_features_check()` for `ndo_features_check`.

## Control flow role

The header does not implement packet processing control flow itself, but its macros define how `bnge_txrx.c` moves through all rings. TX submission uses `TX_RING()`, `TX_IDX()`, `SW_TX_RING()`, `NEXT_TX()`, `SET_TX_OPAQUE()`, and `TX_BD_CNT()` to construct descriptors and later correlate completions. TX cleanup uses `bnge_tx_avail()` to decide queue wake behavior.

RX and completion polling use the completion-validity macros before dereferencing descriptor contents, then use `NEXT_RAW_CMP()`/`RING_CMP()` to handle raw consumer advancement separately from masked descriptor indexing. RX buffer replenishment uses `RX_RING()`, `RX_AGG_RING()`, and index macros to write descriptor addresses into the correct hardware page.

Doorbell helpers establish the final device notification step. `bnge_db_write_relaxed()` is available for ring doorbells where the caller has no ordering requirement; ordered doorbells are provided separately by `bnge_db_write()` in `bnge.h` and are used by the C file where descriptor visibility matters.

## State and persistence behavior

This header defines no standalone storage. Its inline helpers read and encode state owned by `struct bnge_net`, `struct bnge_dev`, `struct bnge_tx_ring_info`, and `struct bnge_db_info`:

- Ring sizes and masks (`tx_ring_size`, `tx_ring_mask`, `rx_ring_mask`, `rx_agg_ring_mask`, `cp_ring_mask`, `cp_bit`) control wrapping and completion valid-bit polarity.
- TX ring counters (`tx_prod`, `tx_cons`) are read with `READ_ONCE()` in `bnge_tx_avail()` because producer and consumer can be updated by different execution contexts.
- Doorbell state (`db_key64`, `doorbell`, ring mask, epoch shift/mask) is supplied by `struct bnge_db_info` and encoded through `DB_RING_IDX()`.
- On 32-bit builds, `bd->db_lock` is a serialization dependency for split 64-bit MMIO writes.

## Dependencies and integration points

- Depends on hardware ABI constants and completion structures from `<linux/bnge/hsi.h>`.
- Depends on ring, descriptor, doorbell, and netdev-private structures from `bnge_netdev.h`.
- Uses Linux MMIO helpers `writeq_relaxed()`/`lo_hi_writeq_relaxed()` and spinlocks through included driver/kernel headers.
- The exported prototypes are consumed by driver registration code in `bnge_netdev.c`: IRQ table setup uses `bnge_msix()`, NAPI setup uses `bnge_napi_poll()`, and netdev ops use `bnge_start_xmit()` plus `bnge_features_check()`.
- `bnge_reuse_rx_data()` is exposed because buffer recycling can be needed outside local static RX helpers, while its implementation remains in `bnge_txrx.c`.

## Risks and edge cases

- The valid-bit macros are polarity-sensitive. If `cp_bit` or raw consumer advancement is wrong, valid completions may be skipped or stale descriptors may be processed as new work.
- `bnge_tx_avail()` relies on unsigned wraparound and the configured `tx_ring_mask`; invalid ring sizing or a non-mask ring size would corrupt free-space accounting.
- `SET_TX_OPAQUE()` packs the NAPI/ring index into eight bits and BD count into eight bits. The surrounding driver must keep TX ring indices and BD counts within those fields; `TX_MAX_BD_CNT` protects the descriptor count side.
- The page-selection macros assume descriptor page sizing based on `BNGE_PAGE_SHIFT - 4` and descriptor counts that match 16-byte hardware descriptors. Changes to descriptor sizes or page layout must update these macros together with allocation code.
- `bnge_writeq_relaxed()` protects split 64-bit writes on 32-bit systems with a shared lock, but relaxed writes still need caller-provided memory ordering when descriptors must be visible before a doorbell.
- `TX_MAX_FRAGS` is lower than theoretical `MAX_SKB_FRAGS` when the hardware BD count is the limit; `bnge_features_check()` and queue setup must preserve that invariant.

## Test signals

- Compile coverage for both 32-bit and 64-bit configurations to exercise `lo_hi_writeq_relaxed()` with `db_lock` and native `writeq_relaxed()`.
- Unit/static assertions or build-time review that ring sizes remain mask-compatible and descriptor sizes match `RX_DESC_CNT`, `TX_DESC_CNT`, and `CP_DESC_CNT` assumptions.
- TX wraparound tests that advance `tx_prod` and `tx_cons` across the mask boundary and verify `bnge_tx_avail()` and `TX_OPAQUE_PROD()` results.
- Completion polarity tests for TX, RX, aggregate RX, and NQ descriptors across `cp_bit` transitions.
- Feature-path tests where SKBs exceed `TX_MAX_FRAGS` or the length-hint table limit, confirming the stack disables unsupported SG/GSO/checksum paths before `bnge_start_xmit()` indexes TX hint data.
- Doorbell ordering tests or DMA/MMIO tracing to confirm callers use relaxed versus ordered writes appropriately for their ring update sequence.
