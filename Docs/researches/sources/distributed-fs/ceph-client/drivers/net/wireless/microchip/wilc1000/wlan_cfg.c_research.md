<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_cfg.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_cfg.c

## Purpose
This file serializes WILC WID configuration requests and parses firmware configuration, status, network-info, and scan-complete responses. It maintains a small cache of queried WID values for byte, halfword, word, and string responses and dispatches asynchronous firmware notifications into the higher host-interface/cfg80211 layer.

## Important APIs, Types, And Functions
Static WID cache templates are `g_cfg_byte`, `g_cfg_hword`, `g_cfg_word`, and `g_cfg_str`. Encoding helpers are `wilc_wlan_cfg_set_byte()`, `wilc_wlan_cfg_set_hword()`, `wilc_wlan_cfg_set_word()`, `wilc_wlan_cfg_set_str()`, and `wilc_wlan_cfg_set_bin()`. Parsing helpers are `wilc_wlan_parse_response_frame()` and `wilc_wlan_parse_info_frame()`.

Public functions are `wilc_wlan_cfg_set_wid()`, `wilc_wlan_cfg_get_wid()`, `wilc_wlan_cfg_get_val()`, `wilc_wlan_cfg_indicate_rx()`, `wilc_wlan_cfg_init()`, and `wilc_wlan_cfg_deinit()`.

## Control Flow
Set WID serialization chooses an encoder from the WID type nibble, writes id and little-endian length, copies payload, and for binary WIDs appends an additive checksum. Get serialization writes only the WID id. Firmware config replies arrive through `wilc_wlan_cfg_indicate_rx()`, which strips the four-byte response header and switches on message type. Config replies update cached values by walking the matching cache table. Status info updates `WID_STATUS`, marks the response as a status packet, and also calls `wilc_gnrl_async_info_received()`. Network and scan messages are forwarded to `wilc_network_info_received()` and `wilc_scan_complete_received()`.

Initialization duplicates the static cache templates, allocates one `struct wilc_cfg_str_vals`, and wires string cache entries for firmware version, MAC address, and association response. Deinit frees all duplicated arrays and string storage.

## State And Persistence
The persistent state is `wl->cfg`, which owns dynamically duplicated cache arrays and backing buffers for string WIDs. Cached byte/word/string values persist until overwritten by a later response or freed. The actual firmware configuration is stored in firmware; this layer only constructs requests and caches selected replies.

## Dependencies And Integration Points
This file depends on WID ids and type encoding from `wlan_if.h`, packet/frame constants from `wlan.h`, and WILC async notification functions from the netdev/cfg80211 side. It is called by `wlan.c` when constructing config packets and when RX demux finds a config packet.

## Risks
Bounds checks are simple and return zero on oversized output; callers interpret zero as timeout/failure, so malformed WID sizes can look like transport failure. Halfword and word set functions cast `u8 *` to integer pointers, which assumes sufficient alignment from callers. String response parsing copies the length prefix plus payload into the cached string buffer and rejects oversize responses. The binary checksum is additive and not strong. Unknown WIDs are silently ignored unless callers expect a cached value.

## Test Signals
Exercise byte, word, string, and binary WID set/get operations; firmware-version, MAC-address, RSSI, status, link-speed, and association-response queries; scan complete and network info notifications; malformed response lengths; and config packet timeout behavior. Memory-leak checks should cover init/deinit failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/wlan_cfg.c -->
