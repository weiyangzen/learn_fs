# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7925/mac.h

Purpose: MT7925 MAC header constants and WTBL address helper.

Important APIs/types/functions: defines WTBL rate/airtime offsets (`MT_WTBL_TXRX_CAP_RATE_OFFSET`, `MT_WTBL_TXRX_RATE_G2_HE`, `MT_WTBL_TXRX_RATE_G2`, `MT_WTBL_AC0_CTT_OFFSET`) and inline `mt7925_mac_wtbl_lmac_addr()`.

Control flow: `mt7925_mac_wtbl_lmac_addr()` writes `MT_WTBLON_TOP_WDUCR` with the WCID group selected from `wcid >> 7`, then returns the LMAC WTBL offset for the requested doubleword. MAC code uses it before reading/writing per-WCID WTBL counters/rate fields.

State/persistence: changes the WTBL-on top group selector register as a side effect before returning an address. No local state is stored.

Dependencies/integration: includes `mt76_connac3_mac.h` and depends on MT7925 register macros from the broader driver. It is used by `mac.c` station polling and WTBL update paths.

Risks: the helper has an implicit register side effect, so callers must serialize access through the same locking discipline used for other WTBL operations. Incorrect WCID or doubleword values can address unrelated WTBL state.

Test signals: station polling across WCID group boundaries, concurrent WTBL reads under mutex/driver serialization, and TX/RX rate/airtime updates for WCIDs above 127.
