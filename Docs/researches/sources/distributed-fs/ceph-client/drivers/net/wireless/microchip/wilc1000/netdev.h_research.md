# sources/distributed-fs/ceph-client/drivers/net/wireless/microchip/wilc1000/netdev.h

Purpose: Defines shared WILC netdev/cfg80211 driver state, channel/rate/cipher tables, queue thresholds, TCP ACK filter structures, vif/global device objects, monitor private data, and core function prototypes.

Important APIs and types: `struct wilc_priv` embeds `wireless_dev`, scan/P2P/key/PMKID/cfg state, real monitor backing device, HIF pointer, and association information. `struct wilc_vif` represents one virtual interface with index, firmware iftype, BSSID, netdev stats, HIF state, timers, TCP ACK filter, cfg80211 private state, list node, BSS reference, and external auth parameters. `struct wilc` is the global device with wiphy, bus hooks, chip id, locks, completions, queues, firmware pointer, workqueue, bus data, monitor device, channels/rates/cipher suites, and NVMEM MAC. Static tables define 2.4 GHz channels, legacy bitrates, and cipher suites.

Control flow: The header supplies data structures used by `cfg80211.c`, `hif.c`, `netdev.c`, `mon.c`, and lower WLAN/bus files. The `wilc_for_each_vif` macro enforces SRCU-aware vif-list traversal. Function prototypes declare RX delivery, MAC indication, cleanup, management RX, BSSID setting, and interface creation.

State and persistence: Most WILC runtime state lives in these structs. Persistent fields include firmware/config state, queue heads, netdev stats, key caches, PMKIDs, associated stations, BSSID, per-vif timers, global lock/completion objects, firmware pointer, and copied channel/rate/cipher arrays registered with wiphy.

Dependencies and integration points: Includes cfg80211, radiotap, netdevice, GPIO, SRCU list, TCP, and WILC HIF/WLAN config headers. It is the common include for the WILC core and defines the contract with bus-independent WLAN queue/config code.

Risks: This header mixes static table definitions with struct declarations; because it is included in multiple C files, the static arrays are duplicated per translation unit, which is acceptable but worth noting for changes. The SRCU traversal macro requires callers to hold SRCU read lock. Queue thresholds and ACK filter sizes are fixed constants that influence flow control and memory use. Changing struct layouts affects driver-private data allocated by `alloc_etherdev()`.

Test signals: Multi-vif traversal under SRCU, interface allocation/free, cfg80211 wiphy band/cipher registration, TX/RX queue operation, ACK filter behavior, monitor interface state, and lockdep coverage around shared locks validate this header.
