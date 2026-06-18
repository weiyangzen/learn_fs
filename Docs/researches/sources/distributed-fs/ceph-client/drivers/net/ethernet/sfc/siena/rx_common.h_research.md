# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/rx_common.h

## Purpose

`rx_common.h` declares shared RX queue, buffer, refill, GRO, RSS, filter, and RFS helpers for the Siena driver. It is the public interface between NIC-specific event code, packet delivery, queue lifecycle, and filter management.

## Important APIs, Types, and Functions

Constants include `EFX_RX_PREFERRED_BATCH`, `EFX_RX_MAX_FRAGS`, and `EFX_RECYCLE_RING_SIZE_10G`. Inline helpers are `efx_rx_buf_va()` for page+offset virtual addresses, `efx_rx_buf_hash()` for reading the RX prefix hash with aligned or byte-wise access, and `efx_sync_rx_buffer()` for DMA sync before CPU access.

The declared API covers slow-fill events, page recycling/discard, RX queue probe/init/fini/remove, freeing RX buffers, page split configuration, fast descriptor pushing, GRO delivery, default RSS indirection setup, filter recipient/equality/hash helpers, optional RFS helpers, and filter table probe/remove.

## Control Flow and Integration

RX queue lifecycle code calls probe/init/fini/remove in order. Event processing calls packet completion in `rx.c`, then refill logic uses `efx_siena_fast_push_rx_descriptors()`. Delivery code calls recycle/free/GRO helpers. Filter table setup and optional RFS hooks use the filter helpers declared here.

## State and Persistence Behavior

The header itself has no storage but exposes helpers that mutate RX queue counters, buffer page ownership, DMA sync state, RSS context tables, and filter/RFS state. Inline hash reading depends on `efx->rx_packet_hash_offset` being valid for NICs that provide a prefix hash.

## Dependencies, Risks, and Test Signals

The header depends on `net_driver.h` definitions and compile-time unaligned access support. Risks include misuse of `efx_rx_buf_hash()` when no valid prefix hash exists, incorrect fragment-count assumptions from `EFX_RX_MAX_FRAGS`, and callers forgetting that descriptor refill needs external serialization. Tests should cover builds with and without efficient unaligned access, RX hash extraction, queue refill serialization, and `CONFIG_RFS_ACCEL` prototype coverage.
