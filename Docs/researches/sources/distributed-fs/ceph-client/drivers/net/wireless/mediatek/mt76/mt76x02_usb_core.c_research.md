<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb_core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb_core.c

Purpose: shared mt76x02 USB core for TX preparation/completion, MAC start, and software pre-TBTT beacon timing. It adapts common txwi/beacon code to USB bulk transport.

Important APIs/types/functions: `mt76x02u_mac_start()`, `mt76x02u_skb_dma_info()`, `mt76x02u_tx_prepare_skb()`, `mt76x02u_tx_complete_skb()`, `mt76x02u_init_beacon_config()`, `mt76x02u_exit_beacon_config()`, and pre-TBTT hrtimer/work helpers.

Control flow: TX prep inserts header padding, writes txwi in skb headroom, assigns pktid, chooses qsel, adds DMA info/padding, and releases pktid on failure. Completion removes DMA/txwi/pad before mt76 status completion. MAC start enables TX then RX after WPDMA idle polling. Beacon config uses an hrtimer to run work about 8 ms before TBTT, writes beacons and buffered BC frames into limited beacon SRAM, updates CSA, then re-arms based on TSF/TBTT.

State and persistence: skb layout, pktid maps, station EWMA length, USB beacon hrtimer/work, beacon slot count, and MAC/RX filter registers.

Dependencies/integration: mt76 USB bulk queues, common MAC/beacon/TXRX helpers, hrtimer/workqueues, mac80211 beacon APIs, and DMA bitfields.

Risks: skb headroom/padding corruption, pktid cleanup on pad failure, beacon timer rearm races, USB limited beacon slots, and TBTT drift. Test signals include TX completion status, AMSDU/SG headroom, AP beacons with buffered multicast, CSA, stop/remove while timer active, and MAC start timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_usb_core.c -->
