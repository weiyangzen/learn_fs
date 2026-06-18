# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/hif_tx_mib.c

Purpose: Implements typed wrappers around HIF read/write MIB commands for WFx firmware configuration.

Important APIs and functions: Wrappers include output power, beacon wakeup period, RCPI/RSSI thresholds, counters table, MAC address, RX filter, beacon filter table/control, global operational power mode, template frame upload, PMF policy, block-ack policy, association mode, TX retry policy, keep-alive, ARP IPv4 filter, multi-TX confirmation enable, U-APSD information, ERP protection, slot time, WEP default key ID, and RTS threshold.

Control flow and integration: Station/AP/scan/data/debug paths call these helpers rather than constructing raw MIB payloads. Each helper fills a specific packed MIB structure, handles local conversions and bounds, and calls `wfx_hif_write_mib()` or `wfx_hif_read_mib()`. Older firmware uses the shorter counters table and leaves extended fields initialized to `0xFF`.

State and persistence: Each write persists in firmware until interface reset/removal or global shutdown. Counter reads and generic stats expose firmware-maintained state but do not mutate driver state by themselves.

Dependencies: Depends on HIF MIB ABI, HIF TX command wrappers, mac80211 SKBs/templates, WFx API-version helper, and Ethernet address helpers.

Risks and test signals: Risks include wrong RSSI-to-RCPI conversion, wake interval bounds, template SKB headroom manipulation, flexible-array allocation sizes, old firmware counters compatibility, U-APSD bit mapping, and policy index limits. Tests should exercise each wrapper, invalid wake periods, template frames at/over 700 bytes, counters on old/new APIs, beacon filter table lengths, ARP filter clearing, and multi-TX confirmation enable.

Test signals: Source read size: 307 lines, 8953 bytes.
