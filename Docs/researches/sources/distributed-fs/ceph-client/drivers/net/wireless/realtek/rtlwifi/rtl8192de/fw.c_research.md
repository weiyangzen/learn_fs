# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192de/fw.c

Purpose: Implements rtl8192de PCI firmware download coordination and reserved-page packet upload for firmware power-save/offload features.

Important APIs/functions: `rtl92d_download_fw()` strips a firmware header, coordinates dual-MAC firmware download through global locks and a register in-progress bit, resets running 8051 firmware when needed, downloads firmware, and waits for common firmware init. `_rtl92d_cmd_send_packet()` sends a command/reserved packet through the beacon queue. `rtl92d_set_fw_rsvdpagepkt()` builds beacon, PS-Poll, null data, and probe response reserved pages and reports page locations to firmware.

Control flow: Firmware download checks firmware buffer availability, parses version/subversion, skips a 32-byte header when recognized, then under `globalmutex_for_fwdownload` checks whether firmware is already downloaded or another MAC is downloading. It waits up to 5000 500-us intervals for the other MAC, otherwise marks download in progress via register `0x1f[5]`. It self-resets RAM firmware if `REG_MCUFWDL[7]`, enables download, writes firmware pages, disables download, runs checksum/ready, clears the in-progress bit, and finally calls `rtl92d_fw_init()`. Reserved page setup patches static packet templates with current MAC/BSSID/AID, allocates an skb, queues it through the beacon TX descriptor, polls beacon queue, and sends `H2C_RSVDPAGE`.

State and persistence: Uses `rtlhal->pfirmware`, `fwsize`, `fw_version`, `fw_subversion`, global firmware-download mutexes, register `0x1f[5]`, beacon TX ring queue/descriptors, and static `reserved_page_packet`. Runtime firmware receives reserved page locations; no disk state.

Dependencies and integration: Depends on common firmware helpers, PCI rings/descriptors, rtlwifi skb/queue helpers, mac80211 MAC/BSSID state, and H2C command IDs. Called from rtl8192de hardware initialization and join-BSS handling.

Risks: Static `reserved_page_packet` is modified in place for the current interface, so concurrent dual-interface calls could race unless higher-level sequencing prevents it. `_rtl92d_cmd_send_packet()` dequeues and frees an existing beacon skb unconditionally. Firmware download relies on magic register `0x1f[5]` for inter-MAC arbitration. Returning `1` when firmware buffer is absent blends normal errno and boolean-style errors.

Test signals: Firmware load on cold boot and second MAC, timeout when firmware missing/hung, join/reserved-page H2C traces, suspend/resume, beacon queue integrity, and power-save null/PS-Poll offload behavior.
