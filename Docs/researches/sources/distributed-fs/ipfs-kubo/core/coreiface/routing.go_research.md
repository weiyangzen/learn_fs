# sources/distributed-fs/ipfs-kubo/core/coreiface/routing.go

## Purpose
Defines CoreAPI routing operations over value records, peers, and providers.

## Important APIs, Types, and Functions
Declares `RoutingAPI` with `Get`, `Put`, `FindPeer`, `FindProviders`, and `Provide`.

## Control Flow and State
No implementation flow is present. The contract covers DHT/delegated routing state: value records, peer address discovery, provider records, and explicit provider announcements.

## Dependencies and Integration Points
Depends on context, Boxo path, routing options, and libp2p peer address info. Implementations use node routing/DHT subsystems.

## Risks and Test Signals
Risks include offline write semantics, provider channel closure, stale addresses, and recursive provide behavior. Tests cover IPNS record get/put, offline put option, peer finding, provider finding, and explicit provide propagation.
