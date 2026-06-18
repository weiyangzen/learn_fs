# sources/distributed-fs/ipfs-kubo/core/coreiface/tests/routing.go

## Purpose
Conformance tests for routing value, peer, provider, and provide operations.

## Important APIs, Types, and Functions
Defines helper `testRoutingPublishKey` and tests `TestRoutingGet`, `TestRoutingPut`, `TestRoutingPutOffline`, `TestRoutingFindPeer`, `TestRoutingFindProviders`, and `TestRoutingProvide`.

## Control Flow and State
Tests create online swarms, publish IPNS records, retrieve and put routing values, enforce offline put failure unless `AllowOffline`, find peers and compare swarm local addresses, find providers for pinned content, and explicitly provide content added through an offline API view.

## Dependencies and Integration Points
Depends on Name, Routing, Unixfs, Pin, Swarm, Key APIs, IPNS record marshaling, and routing options.

## Risks and Test Signals
Signals cover DHT propagation and provider discovery but use sleeps/retries because routing is asynchronous. Risks include timing flakes, provider strategy assumptions, and only checking first provider/address.
