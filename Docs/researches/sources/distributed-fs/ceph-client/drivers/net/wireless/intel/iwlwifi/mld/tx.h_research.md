# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tx.h

## Purpose

Defines the MLD TXQ private-data contract and declares MLD transmit, queue, flush, response, BA, antenna, and rate helper APIs implemented by `mld/tx.c`.

## Important APIs, Types, and Functions

`struct iwl_mld_txq` is stored in `ieee80211_txq::drv_priv`. Its restart-zeroed group contains `fw_id`, `status.allocated`, and `status.stop_full`; `list` links into `mld->txqs_to_add`; `tx_request` serializes TXQ drainers. `IWL_MLD_INVALID_QUEUE` and `IWL_MLD_INVALID_DROP_TX` distinguish invalid state from intentional drop. Inline helpers initialize TXQ state and cast mac80211 private storage.

## Control Flow

Callers initialize TXQ private data, add or ensure firmware queues, drain with `iwl_mld_tx_from_txq()`, remove/free queues on teardown, and route firmware notifications through the declared response handlers.

## State and Persistence Behavior

The `zeroed_on_hw_restart` group documents firmware-derived state that must be cleared on restart. List membership and `tx_request` survive that zeroing and need separate initialization/handling.

## Dependencies and Integration Points

Depends on `mld.h`, mac80211 TXQ/SKB/VIF/STA structures, and iwl RX packet types. Included by MLD code that needs TX queue lifecycle or notification hooks.

## Risks

The TXQ cast assumes correct mac80211 private allocation. Moving persistent fields into the restart-zeroed group could corrupt restart behavior. Callers must handle the two invalid queue sentinels differently.

## Test Signals

Build catches declaration drift. Runtime restart and TXQ allocation/removal tests should verify queue state is reset, re-added, and not wedged by `tx_request` or `stop_full`.
