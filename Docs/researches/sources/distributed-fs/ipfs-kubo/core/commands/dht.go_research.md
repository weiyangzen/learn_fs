<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dht.go -->
# sources/distributed-fs/ipfs-kubo/core/commands/dht.go

## Purpose

Defines deprecated `ipfs dht` compatibility commands, keeping only direct DHT closest-peer query while routing users to `ipfs routing` for removed operations.

## Important APIs, Types, and Functions

`DhtCmd` registers deprecated subcommands. `ErrNotDHT` reports missing active DHT. `kademlia` is a local interface requiring `GetClosestPeers`. `queryDhtCmd` performs the query. `RemovedDHTCmd` returns a removed-command error for findprovs/findpeer/get/put/provide.

## Control Flow

`queryDhtCmd` gets the node, checks active DHT, decodes the input peer ID, registers routing query events, selects WAN or LAN DHT client when the dual DHT is present, runs `GetClosestPeers` in a goroutine, publishes final peer events, streams query events until the event channel closes, and returns the goroutine error.

## State and Persistence Behavior

Read-only relative to repo state. It performs DHT network queries and emits routing events.

## Dependencies and Integration Points

Depends on libp2p routing query events, peer IDs, Kubo node DHT fields, and event printers such as `printEvent`/`pfuncMap` defined elsewhere.

## Risks and Edge Cases

The command is deprecated, so behavior must remain compatible while steering users elsewhere. DHT client selection falls back to LAN if WAN is inactive. If the client does not implement `GetClosestPeers`, it fails explicitly.

## Test Signals

`dht_test.go` covers key-translation helper behavior from related DHT/routing code, not this query path. Command tree tests verify deprecated subcommand registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/core/commands/dht.go -->
