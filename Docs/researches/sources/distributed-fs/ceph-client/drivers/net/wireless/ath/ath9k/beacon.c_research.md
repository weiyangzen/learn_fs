# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/beacon.c

Purpose: Implements ath9k beacon generation, beacon queue programming, per-vif beacon slot ownership, CSA completion, SWBA tasklet handling, and mode-specific beacon timer setup for AP, mesh, IBSS, and station operation.

Important APIs/functions: `ath9k_beacon_assign_slot()`, `ath9k_beacon_remove_slot()`, `ath9k_beacon_ensure_primary_slot()`, `ath9k_csa_is_finished()`, `ath9k_csa_update()`, `ath9k_beacon_tasklet()`, `ath9k_beacon_config()`, and `ath9k_set_beacon()` are the external integration points. Internal helpers configure the beacon TXQ (`ath9k_beaconq_config()`), build beacon descriptors (`ath9k_beacon_setup()`), fetch mac80211 beacons and buffered multicast frames (`ath9k_beacon_generate()`), choose staggered slots, calculate TSF adjustment, and cache `struct ath_beacon_config`.

Control flow: mac80211 configuration calls cache beacon interval/DTIM/BMISS settings, updates `ATH_OP_BEACONS`, and dispatches to AP/IBSS/STA timer programming through common beacon helpers. On each SWBA, `ath9k_beacon_tasklet()` skips during reset, checks whether the prior beacon is still pending, handles stuck-beacon recovery and NF calibration hints, chooses the current slot, handles CSA completion, notifies the channel-context scheduler, regenerates and DMA maps the beacon skb, updates deferred slot-time changes, and posts the descriptor to the beacon queue. AP/mesh use staggered slots across `ATH_BCBUF`; station mode programs BMISS timers and does not transmit beacons.

State/persistence: State is in `sc->beacon` (`bbuf`, `bslot[]`, beacon queue, CAB queue, `bmisscnt`, slot-time update state, TX status flags), `ath_vif` (`av_bcbuf`, `av_bslot`, `tsf_adjust`, `chanctx`), `sc->cur_chan->beacon`, `common->op_flags`, and hardware interrupt masks/TSF/beacon registers. Beacon skb DMA mappings persist until regenerated or slot removal.

Dependencies/integration: Uses mac80211 beacon APIs, DMA mapping, ath9k TX descriptor/queue helpers, hardware beacon timers, channel context NoA insertion, CSA callbacks, power-save synchronization for IBSS joiners, and noise-floor recalibration from `calib.c`.

Risks: DMA unmap/free ordering for old beacon skb must stay exact. Slot re-enumeration adjusts TSF and can perturb multi-vif timing if `tsf_adjust` math is wrong. Missed-beacon thresholds interact with `nbcnvifs`, EDMA completion behavior, and channel-context beacon events. Zero beacon intervals are sanitized to avoid timer loops. CABQ flushing for multi-vif DTIMs can drop buffered multicast traffic by design.

Test signals: Verify AP/mesh beacon emission, multi-BSS staggered slots, IBSS creator/joiner synchronization, station BMISS interrupts, CSA completion, CAB traffic at DTIM, stuck-beacon reset path, NF recalibration after repeated misses, channel-context NoA IEs in generated beacons, and absence of DMA mapping leaks under vif add/remove.
