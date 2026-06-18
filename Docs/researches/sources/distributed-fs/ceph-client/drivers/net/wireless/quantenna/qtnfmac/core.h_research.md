# sources/distributed-fs/ceph-client/drivers/net/wireless/quantenna/qtnfmac/core.h

Purpose: defines the main qtnfmac runtime data model shared by command, event, cfg80211, transport, and bus-specific code. It also declares core lifecycle, netdev, scan, and utility APIs.

Important APIs/types/functions: constants include `QTNF_MAX_VSIE_LEN`, `QTNF_MAX_INTF`, `QTNF_MAX_EVENT_QUEUE_LEN`, `QTNF_SCAN_TIMEOUT_SEC`, default BSS/watchdog settings, and TX-timeout threshold. Key structs are `qtnf_sta_node`, `qtnf_sta_list`, `qtnf_vif`, `qtnf_mac_info`, `qtnf_wmac`, and `qtnf_hw_info`. Prototypes expose VIF lookup, capability cleanup, module parameter getters, wiphy allocation, net attach, main/event work, MAC lookup, skb classification, queue wake, VIF cleanup, netdev up/down, scan completion, debugfs root access, and qtn netdev identification.

Control flow: bus drivers allocate `qtnf_bus` and call core attach; core allocates `qtnf_wmac` via wiphy private data and fills the `iflist`. cfg80211 and netdev code use inline `qtnf_netdev_get_priv` to recover the `qtnf_vif` from `netdev_priv`. Hardware capability checks use `qtnf_hwcap_is_set` over the firmware capability bitmap.

State and persistence: all structs describe in-memory runtime state. `qtnf_vif` holds per-interface cfg80211 wireless_dev, BSSID/MAC, status/priority, management frame mask, netdev, station list, reset/high-priority work, high-priority SKB queue, timeout count, and generation. `qtnf_wmac` holds per-radio MAC id, bus pointer, capabilities, VIF array, active scan request, lock, scan timeout work, regulatory domain, and optional platform device. `qtnf_hw_info` caches protocol/firmware/hardware versions, MAC bitmap, chain counts, and hardware capabilities.

Dependencies and integration points: includes Linux kernel, netdevice/skbuff, cfg80211, firmware, workqueue, platform-device, `qlink.h`, `trans.h`, and `qlink_util.h`. The header is central to almost every qtnfmac file, so it defines the coupling between upper cfg80211 logic and lower transport implementations.

Risks: structure layout and lifetime are critical because bus code, workqueues, and cfg80211 callbacks hold pointers into these objects. `qtnf_netdev_get_priv` assumes netdev private storage contains a valid `struct qtnf_vif *`. Any change to constants such as `QTNF_MAX_INTF` affects firmware addressing and array bounds. Capability cleanup APIs must stay paired with allocation paths in `commands.c` and `core.c`.

Test signals: compile coverage across all qtnfmac objects, KASAN for VIF/MAC lifetime, lockdep around `mac_lock` and RTNL, attach/detach with multiple radios, scan timeout completion, netdev private pointer access, and capability bitmap checks for hardware bridge/DFS/WoWLAN paths.
