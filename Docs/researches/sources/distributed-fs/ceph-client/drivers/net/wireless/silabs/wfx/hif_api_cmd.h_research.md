# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_api_cmd.h

Purpose: Defines the WF200 host-interface command ABI for request, confirmation, and indication messages used by command TX/RX, data TX/RX, scanning, association, keys, AP start, and link mapping.

Important APIs and types: Request/confirmation IDs cover reset, read/write MIB, scan start/stop, TX, join, PM mode, BSS params, add/remove key, EDCA, AP start, beacon transmit, update IE, and map link. Indication IDs cover RX, scan complete, join complete, PM complete, suspend/resume TX, and events. Packed structures define each command body, TX request/confirm and multi-confirm format, RX indication metadata, scan channel/SSID list, join/start payloads, PM/BSS/EDCA settings, key material variants for WEP/TKIP/AES/WAPI/IGTK, event indications, and link IDs.

Control flow and integration: `hif_tx.c` allocates and fills these request structures; `hif_rx.c` validates confirmations and indications against IDs and dispatches them; `data_tx.c` writes `wfx_hif_req_tx` directly into SKBs; `key.c` fills `wfx_hif_req_add_key`; `scan.c` uses scan complete counts.

State and persistence: The ABI encodes firmware-persistent state such as key table entries, peer link map, BSS join/start configuration, PM mode, EDCA queue parameters, template updates, retry policy references, and per-packet TX status.

Dependencies: Depends on `hif_api_general.h`, Linux Ethernet/mac80211 constants, and firmware layout compatibility with packed LE fields and C bitfields.

Risks and test signals: Risks include C bitfield layout portability, endian mistakes, flexible-array size calculations, packet ID uniqueness assumptions, firmware API version changes, and key material ordering. Tests should validate structure sizes/offsets where possible, command/confirm ID matching, scan list bounds, key type fills, TX status parsing, RX metadata mapping, link ID limits, and event handling.

Test signals: Source read size: 553 lines, 13650 bytes.
