# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76_connac3_mac.c

Purpose: Connac3 RX vector to radiotap decoder for HE and EHT metadata.

Important APIs and functions: `mt76_connac3_mac_decode_he_radiotap()` pushes and fills `ieee80211_radiotap_he` data, including BSS color, LDPC extra symbol, spatial reuse, LTF, TXBF, TXOP, Doppler, format, UL/DL, beam change, RU allocation, and MU metadata. `mt76_connac3_mac_decode_eht_radiotap()` pushes EHT and EHT-USIG TLVs and fills known fields, user info, NSS, beamforming, coding, STA ID, BSS color, TXOP, and bandwidth. Helpers decode HE RU allocation, HE MU data, and push radiotap TLVs.

Control flow: RX status code passes skb, rxv array, and PHY mode after basic RX rate parsing. The functions prepend radiotap metadata to the skb and update `mt76_rx_status` flags. EHT decoding requires `skb_mac_header(skb) == skb->data` because TLVs are pushed at the top of the MAC header and flagged with `RX_FLAG_RADIOTAP_TLV_AT_END`.

State and persistence: Mutates skb headroom and `skb->cb` receive status for monitor-mode reporting. No persistent state.

Dependencies: `mt76_connac3_mac.h` bitfields, `mt76_connac.h`, mac80211 radiotap HE/EHT structures, and skb push semantics.

Risks: skb headroom and ordering are critical; EHT warns and returns if the MAC header is not positioned as expected. Incorrect rxv indexes or bit masks produce misleading monitor captures. NSS is intentionally zero-based for radiotap compatibility, so changes can break userspace decoders.

Test signals: Monitor-mode captures in Wireshark/iw, HE SU/MU/TB radiotap fields, EHT TLV presence, no skb headroom corruption, and exported symbol use by Connac3 drivers.
