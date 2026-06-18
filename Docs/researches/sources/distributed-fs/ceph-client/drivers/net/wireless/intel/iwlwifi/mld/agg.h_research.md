# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/agg.h

## Purpose

`agg.h` declares the MLD RX aggregation/reorder data structures and APIs used by RX, station, and mac80211 operation code.

## Important APIs, Types, and Functions

It defines `struct iwl_mld_reorder_buffer`, `struct iwl_mld_reorder_buf_entry`, `struct iwl_mld_baid_data`, `struct iwl_mld_delba_data`, and `enum iwl_mld_reorder_result`. Prototypes expose BA session start/stop, reorder processing, firmware release notification handlers, internal DELBA release, and station BAID mask update.

## Control Flow

Callers use `iwl_mld_ampdu_rx_start()` and `iwl_mld_ampdu_rx_stop()` from mac80211 AMPDU callbacks. RX uses `iwl_mld_reorder()` per MPDU and follows the returned pass/buffer/drop decision. Notification dispatch calls the frame/BAR release handlers, while RX queue synchronization uses `iwl_mld_del_ba()` to drain buffers during teardown.

## State and Persistence Behavior

The structures are stateful: reorder buffers track head sequence numbers and stored-frame counts per RX queue, entries hold skb lists, BAID data owns session timers and RCU lifetime, and `sta_mask` ties a BAID to one or more firmware station IDs for MLO.

## Dependencies and Integration Points

The header depends on `mld.h`, firmware RX API definitions, skb queues, timers, and RCU conventions. Its exported prototypes are implemented in `agg.c`.

## Risks and Edge Cases

`IWL_MAX_RX_HW_QUEUES` sizes the inline reorder-buffer array, while entries are flex-allocated per actual RX queue count; mismatches must remain bounded. Cacheline alignment and sparse workarounds should be preserved because RX reordering is hot-path and cross-queue cache sharing matters.

## Test Signals

Compile with sparse and normal builds, run aggregation KUnit, and validate struct layout assumptions under different cacheline sizes and RX queue counts.
