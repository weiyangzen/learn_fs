# sources/distributed-fs/ipfs-kubo/core/corehttp/routing.go

## Purpose
Serves the HTTP delegated routing v1 API backed by the node's routing, peerstore, and DHT client.

## Important APIs, Types, and Functions
Exports `RoutingOption`; implements `contentRouter` methods `FindProviders`, `ProvideBitswap`, `FindPeers`, `GetIPNS`, `PutIPNS`, and `GetClosestPeers`; defines `peerChanIter`.

## Control Flow and State
`RoutingOption` wraps the Boxo routing HTTP server with gateway headers/CORS and mounts `/routing/v1/`. Provider lookup converts the async libp2p provider channel into a result iterator with cancellation. Peer/IPNS methods call routing interfaces directly. Closest-peer lookup rejects undefined CIDs, chooses WAN DHT for dual DHT, supports fullrt and IpfsDHT, then maps peerstore addresses into HTTP records.

## Dependencies and Integration Points
Depends on Boxo routing HTTP server/types, gateway headers, Kubo node routing/DHT fields, libp2p DHT implementations, peerstore, CIDs, and IPNS records. It is a public delegated-routing surface.

## Risks and Test Signals
Risks include exposing LAN peers from the wrong DHT, stale peerstore addresses, unsupported DHT types, iterator cancellation leaks, and lack of Bitswap write-provide support. Tests should cover HTTP routing endpoints, WAN-only selection, IPNS marshal/unmarshal errors, and provider iterator cancellation.
