# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl1251/acx.h

Purpose: Defines the wl1251 ACX firmware information-element ABI: ACX header, element IDs, packed payload structs, default constants, interrupt bits, statistics layouts, and prototypes implemented by `acx.c`.

Important APIs, types, and functions: `struct acx_header` embeds `wl1251_cmd_header` plus ACX id/length. Major structs cover revision, sleep auth, data path params, RX config/filter flags, QoS queues, slot, multicast, service period timeouts, low RSSI, beacon filter, connection monitor, BT/WLAN coexistence, event mask, frame rates, station ID, TSF, wake conditions, preamble/CTS, statistics, memory config/map, TBTT/DTIM, BET, ARP filtering, AC config, and TID config. The ACX ID enum maps firmware element numbers, and interrupt defines map host interrupt bits.

Control flow: The header enables `cmd.c` to wrap ACX payloads in `CMD_CONFIGURE`/`CMD_INTERROGATE` and lets init/debugfs/event code share exact firmware struct layouts.

State and persistence: No runtime state is stored here, but the packed structures define firmware state that can be written or read. Statistics structs are cached by debugfs in `wl->stats.fw_stats`.

Dependencies and integration points: Includes `wl1251.h` and `cmd.h`; uses kernel integer/endian types and `ETH_ALEN`. It is a central dependency for boot, init, command, event, debugfs, RX/TX config, and power-save code.

Risks: ABI correctness is critical: packing, field widths, endian annotations, and ACX IDs must match firmware. Some fields are host pointers in `wl1251_acx_mem_map`, which are really firmware addresses and can be confusing. A few comments mark undocumented or unused firmware elements.

Test signals: Compile-time packed layout checks where possible, runtime ACX interrogate/configure success, firmware statistics sanity, and interrupt mask behavior during boot.
