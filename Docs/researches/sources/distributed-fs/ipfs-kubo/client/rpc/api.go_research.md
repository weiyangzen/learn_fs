# sources/distributed-fs/ipfs-kubo/client/rpc/api.go

## Purpose
This file implements the top-level HTTP CoreAPI client used to talk to a running Kubo daemon.

## Important APIs, Types, And Functions
`HttpApi` stores base URL, `http.Client`, headers, global request option hook, IPLD decoder, and cached remote version. Constructors include `NewLocalApi`, `NewPathApi`, `ApiAddr`, `NewApi`, `NewApiWithClient`, and `NewURLApiWithClient`. Interface accessors return `Unixfs`, `Block`, `Dag`, `Name`, `Key`, `Pin`, `Object`, `Swarm`, `PubSub`, and `Routing` sub-APIs.

## Control Flow
Local constructors resolve `$IPFS_PATH/api`; multiaddr constructors select Unix socket handling or HTTP/HTTPS based on protocols; URL constructor creates a decoder with dag-pb/raw support and disables redirects. `Request` copies headers into a request builder. `loadRemoteVersion` fetches `/version` once under a mutex.

## State And Persistence Behavior
State is client-side only: headers, cached semantic version, and decoder registry. It reads the local API file but does not write it.

## Dependencies And Integration Points
It integrates multiaddr dialing, fsutil home expansion, Kubo version response, go-ipld legacy decoder, dag-pb/raw codecs, and `coreiface`.

## Risks And Test Signals
Risks include URL scheme inference mistakes, redirect rejection breaking unusual proxies, global codec assumptions, and stale cached remote versions. Tests cover full CoreAPI behavior, header propagation, and TLS/HTTPS multiaddr conversion.
