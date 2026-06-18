# sources/distributed-fs/ipfs-kubo/core/corehttp/p2p_proxy.go

## Purpose
Exposes `/p2p/` HTTP reverse proxying to HTTP services advertised over libp2p peers.

## Important APIs, Types, and Functions
Exports `P2PProxyOption`; internal pieces are `proxyRequest`, `parseRequest`, and `handleError`.

## Control Flow and State
The handler parses paths of the form `/p2p/$peer/http/$path` or `/p2p/$peer/x/$protocol/http/$path`, validates the peer ID, rewrites the request path, builds a `libp2p://$peer` target, creates a go-libp2p-http transport with the selected protocol ID, and delegates to `httputil.ReverseProxy`.

## Dependencies and Integration Points
Depends on `core.IpfsNode.PeerHost`, libp2p peer/protocol types, go-libp2p-http, net/http reverse proxy, and URL parsing. It integrates with API HTTP serving as a proxy bridge from HTTP clients to libp2p services.

## Risks and Test Signals
Risks include path parsing edge cases, per-request transport/proxy allocation, forwarding headers to untrusted peers, and broad protocol exposure. Tests cover valid/invalid parser cases; integration coverage should verify proxy transport behavior, forwarded path/query semantics, and cancellation.
