<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mac.h

Purpose: shared MAC data structure and bitfield header. It defines TX status, VIF/station private data, RXWI/TXWI layouts, RX info/rate flags, and MAC helper prototypes.

Important APIs/types/functions: `struct mt76x02_tx_status`, `struct mt76x02_vif`, `struct mt76x02_sta`, `struct mt76x02_rxwi`, `struct mt76x02_txwi`, `MT_VIF_WCID()`, packet-id masks, RXINFO/RXWI/TXWI bitfields, and `mt76x02_wait_for_mac()`.

Control flow: declarative header. `mt76x02_wait_for_mac()` polls MAC CSR0 until the device is responsive or removed/timeout.

State and persistence: station/VIF structs are embedded in mac80211 drv_priv and persist while interfaces/stations exist. TXWI/RXWI structs describe hardware descriptors passed per packet.

Dependencies/integration: used by shared MAC/TXRX, mt76x0/mt76x2 bus drivers, and reset paths. It depends on mac80211 SKB/status semantics and mt76 register access.

Risks: packed/aligned descriptor layout must match hardware; WCID mapping reserves group WCIDs near 254; rate bitfields affect both RX and TX status interpretation. Test signals include descriptor size/alignment checks, TX/RX on all PHY modes, multi-VIF group traffic, and MAC readiness timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x02_mac.h -->
