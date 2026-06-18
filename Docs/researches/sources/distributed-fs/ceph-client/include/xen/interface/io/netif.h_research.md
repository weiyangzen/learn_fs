# sources/distributed-fs/ceph-client/include/xen/interface/io/netif.h

Purpose: defines the Xen virtual network frontend/backend ABI: TX/RX ring records, offload and extra-info descriptors, multi-queue negotiation, control ring messages for hashing, and status codes.

Important APIs/types/functions: `XEN_NETIF_NR_SLOTS_MIN`, `XEN_NETIF_MAX_XDP_HEADROOM`, hash flags/algorithms, optional `xen_netif_toeplitz_hash` helper when `XEN_NETIF_DEFINE_TOEPLITZ` is set, control request/response structs and `DEFINE_RING_TYPES(xen_netif_ctrl, ...)`, TX/RX structs `xen_netif_tx_request`, `xen_netif_tx_response`, `xen_netif_rx_request`, `xen_netif_rx_response`, `xen_netif_extra_info`, `DEFINE_RING_TYPES(xen_netif_tx, ...)`, `DEFINE_RING_TYPES(xen_netif_rx, ...)`, and `XEN_NETIF_RSP_*`.

Control flow: frontends grant TX/RX rings and optional control rings through XenStore. TX packets flow frontend to backend as one or more grant-backed fragments plus optional extra descriptors. RX buffers are posted by the frontend and completed by the backend. Control messages configure hash algorithm, hash flags, key, and queue mapping.

State and persistence: queue topology, split event channels, checksum/GSO/multicast/XDP/hash capabilities, and control-ring grants persist in XenStore. In-flight packet state lives in rings and grant references.

Dependencies and integration points: includes `ring.h` and `grant_table.h`. Integrates with netfront/netback, event channels, checksum offload, GSO, multicast filtering, XDP headroom, RSS-like queue steering, and legacy Linux slot assumptions.

Risks: TX and RX multi-fragment packet size semantics differ. Extra-info overlays normal ring slots, and legacy Linux RX assumes response slot matching. Feature negotiation defaults are asymmetric for IPv4 and IPv6 checksum offload. Hash grants must remain valid until responses are processed.

Test signals: TX/RX packet integrity, checksum offload matrix, GSO IPv4/IPv6, multicast filter add/delete, split event channels, multi-queue steering, hash control ring operations, XDP headroom, and malformed ring overflow detection.
