## sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/rx.h

Purpose: declares the common RX descriptor ABI and exported receive helpers for rtw88 transports.

Important APIs/types: `enum rtw_rx_desc_enc` maps hardware encryption codes; `struct rtw_rx_desc` is a packed six-word descriptor; `RTW_RX_DESC_W*` masks define packet length, CRC/ICV, driver-info size, encryption type, shift, PHY status, SW-decrypt bit, MAC ID, C2H marker, PPDU count, rate, bandwidth, and TSF. Function prototypes expose `rtw_rx_stats`, `rtw_rx_query_rx_desc`, and `rtw_update_rx_freq_from_ie`.

Control flow and state: no runtime code except `rtw_update_rx_freq_for_invalid()`, which calls IE-based channel correction only when `pkt_stat->channel_invalid` is set. State is carried by caller-owned `struct rtw_rx_pkt_stat` and `ieee80211_rx_status`.

Dependencies and integration: included by USB, SDIO, PCI, and core receive paths. Its masks must match firmware/hardware descriptor format and the parser in `rx.c`.

Risks and test signals: any bit-mask or descriptor-size mismatch causes corrupted packet length, wrong C2H routing, bogus rates, or memory overrun in HCI RX loops. Test by validating RX descriptor dumps against expected fields, running encrypted and C2H traffic, and checking aggregated packet parsing.
