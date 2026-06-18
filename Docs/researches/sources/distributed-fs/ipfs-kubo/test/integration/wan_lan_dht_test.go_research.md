## sources/distributed-fs/ipfs-kubo/test/integration/wan_lan_dht_test.go

Purpose: validates Kubo's split LAN/WAN DHT behavior in mocknet with synthetic LAN and WAN IPv6 listen addresses.

Important APIs and control flow: `makeAddr` derives LAN or WAN multiaddrs from `lanPrefix`/`wanPrefix`; `RunDHTConnectivity` creates a test peer plus WAN server peers and LAN peers, links peers within their domains, listens on synthetic addresses, connects the test peer to LAN first, refreshes the LAN routing table, verifies provider discovery for a LAN-provided CID, then connects WAN peers, refreshes WAN routing, verifies WAN provider discovery, and finally checks merged provider results when a WAN peer also provides the LAN CID. Tests include fast and epic slow network/routing profiles.

State and dependencies: in-memory mocknet peer connections, DHT routing tables, provider records, and peerstore addresses. Dependencies include Kubo DHT options, libp2p core network/mocknet, multiaddr, and cid.

Risks: uses real-looking WAN prefix for peer diversity behavior and timeout loops up to 60s; random peer selection can expose connectivity edge cases. Test signals are non-empty LAN/WAN routing tables and expected provider IDs/counts from `FindProvidersAsync`.
