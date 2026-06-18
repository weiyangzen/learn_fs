# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_tx.c

## Purpose
Implements libipw transmit-side conversion from Ethernet SKBs to one or more 802.11 SKBs wrapped in a `libipw_txb`. It handles SNAP encapsulation, infrastructure/adhoc addressing, QoS classification, optional MSDU/MPDU host encryption, fragmentation, optional RTS frame insertion, FCS reservation, and handoff to the hardware driver callback.

## Important APIs, Types, and Functions
Exported functions are `libipw_xmit` and `libipw_txb_free`. Internal helpers include `libipw_copy_snap`, `libipw_encrypt_fragment`, `libipw_alloc_txb`, and `libipw_classify`. Static OUIs select RFC1042 or 802.1H bridge-tunnel SNAP encapsulation based on EtherType.

## Control Flow
`libipw_xmit()` first checks queue-full callback and enters `ieee->lock`. It rejects missing hardware transmit callback or too-small SKBs as successful consumption, chooses the active crypto key, decides whether encryption applies while exempting 802.1X EAPOL, drops unencrypted payloads when policy requires, builds a 3-address 802.11 data header for infrastructure or adhoc, optionally adds QoS control and maps IP TOS to TID, strips the Ethernet header, and computes payload bytes including SNAP. If MSDU crypto is needed, it builds a temporary full-frame SKB, adds SNAP and payload, invokes `encrypt_msdu`, and then fragments that encrypted MSDU. It computes fragment size from FTS/RTS/FCS/crypto overhead, allocates a `libipw_txb`, optionally creates an RTS frame, fills each fragment with header/SNAP/payload, encrypts each MPDU if needed, adds FCS reservation, unlocks, frees the original SKB, and invokes `hard_start_xmit`.

## State and Persistence Behavior
TX updates netdev TX packet/byte/error/drop stats, reads `ieee->sec`, `crypt_info.tx_keyidx`, host crypto booleans, `fts`, `rts`, `config`, `tx_headroom`, `bssid`, mode, and callbacks. Crypto contexts mutate per-key IV/PN/TSC state. The produced `libipw_txb` owns fragment SKBs until the hardware driver accepts and later frees it, or until libipw frees it on callback failure.

## Dependencies and Integration Points
Depends on SKB allocation/mutation, netdevice TX API, Ethernet/IP headers, IEEE 802.11 frame constants, libipw crypto ops, and driver callbacks. ipw2100/ipw2200 install `libipw_xmit` as `ndo_start_xmit` and implement `hard_start_xmit` to map `libipw_txb` fragments to firmware TX descriptors.

## Risks
The function consumes or mutates the input SKB even across some no-op success paths, so error semantics are delicate. Fragment-size arithmetic must account for header, FCS, and crypto prefix/postfix or it can overrun fragment buffers. `libipw_alloc_txb()` failure stops the netdev queue and returns busy. Host encryption requires crypto headroom/tailroom and assumes callbacks are synchronous. QoS header layout uses `struct libipw_hdr_3addrqos`, whose payload/qos positioning is unusual and must match existing consumers.

## Test Signals
TX in infrastructure and adhoc modes, queue-full behavior, EAPOL exemption, WEP/TKIP/CCMP host encryption, TKIP MSDU MIC, fragmented unicast, multicast/broadcast no-fragment path, RTS insertion, QoS TID mapping, FCS reserve/compute modes, hard_start_xmit busy/failure, allocation failure, and stats accounting are key validation points.
