# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/core.c

Purpose: Implements the main brcmfmac lifecycle and network data path. It allocates driver/wiphy state, attaches firmware vendor/protocol/FWEH/cfg80211/netdevs, registers IP notifiers/debugfs, and handles TX/RX, interfaces, carrier/flow blocking, monitor/P2P netdevs, reset, crash, detach, and free.

Important APIs/types/functions: `brcmf_alloc()`, `brcmf_attach()`, `brcmf_detach()`, `brcmf_free()`, `brcmf_core_init()/exit()`, `brcmf_add_if()`, `brcmf_remove_interface()`, `brcmf_net_attach()/detach()`, `brcmf_rx_frame()`, `brcmf_rx_event()`, `brcmf_netif_rx()`, `brcmf_txfinalize()`, `brcmf_txflowblock_if()`, and `brcmf_bus_change_state()`.

Control flow: Attach initializes maps and mutexes, attaches fwvid/proto/FWEH, registers watchdog handler, lets vendor override cfg80211 ops, then starts the bus path. Bus start creates primary ifp, marks bus UP, runs bus and firmware preinit, detects features, finalizes protocol, attaches cfg80211/netdevs/P2P, registers IP notifiers, and creates debugfs. TX validates bus, filters IAPP unless enabled, ensures headroom, tracks EAPOL, classifies priority, and queues to protocol. RX pulls protocol headers, handles reorder/events, and delivers to netif.

State and persistence behavior: `brcmf_pub` owns driver runtime state; `brcmf_if` owns per-interface netdev/work/queue/MAC/IP-offload state. Firmware receives ARP/ND, multicast, promisc, monitor, TOE, and termination commands.

Dependencies and integration points: Linux netdev/cfg80211/inet/debugfs/ethtool plus brcmf bus, proto, fwil, feature, fwvid, P2P, PNO, and PCIe/SDIO/USB registration.

Risks: Failure unwind and dynamic IF events are race-prone. TX always consumes SKBs. IAPP filtering is security-relevant. Notifier and reset work ordering can matter on attach failure or crash.

Test signals: Probe creates wlan/debugfs; test bus-down TX, EAPOL wait, multicast/promisc, IAPP filtering, monitor RX formats, firmware crash coredump/reset, IF add/del, P2P, and IP offload notifiers.
