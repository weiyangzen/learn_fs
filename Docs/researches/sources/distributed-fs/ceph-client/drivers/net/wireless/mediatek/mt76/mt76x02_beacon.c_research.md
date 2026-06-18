<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_beacon.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_beacon.c

Purpose: shared beacon SRAM and buffered broadcast/multicast handling for mt76x02 devices. It writes beacon frames into hardware memory, manages beacon masks, updates TBTT timer drift, and collects buffered PS frames.

Important APIs/types/functions: `mt76x02_init_beacon_config()`, `mt76x02_mac_set_beacon()`, `mt76x02_mac_set_beacon_enable()`, `mt76x02_resync_beacon_timer()`, `mt76x02_update_beacon_iter()`, and `mt76x02_enqueue_buffered_bc()`.

Control flow: init disables beacon/TBTT timers, enables sync mode, writes bypass mask, and programs slot offsets. Beacon update gathers active VIF beacons from mac80211, writes TXWI plus frame into each slot, updates `beacon_data_count`, and later releases bypass bits for populated slots. Enable/disable toggles per-VIF bits and starts/stops bus-specific beacon ops. Buffered BC frames are pulled per active VIF until a frame limit is reached, with only the tail frame clearing More Data.

State and persistence: uses device beacon mask, beacon interval, TBTT count, beacon hang counter, and per-update queued SKBs. Hardware beacon SRAM/register state persists until reset or reprogramming.

Dependencies/integration: called by MMIO pre-TBTT tasklet and USB hrtimer work, mac80211 beacon/buffered-BC APIs, mt76 CSA helpers, and `mt76x02_mac_write_txwi()`.

Risks: slot-size overflow, USB headroom assumptions, drift correction off by one, incorrect bypass masks, and More Data handling for buffered frames. Test signals include AP/multi-BSSID beacons, CSA completion, DTIM buffered multicast delivery, USB and PCI beacon paths, and small-slot ENOSPC warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_beacon.c -->
