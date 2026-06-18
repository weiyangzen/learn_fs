# sources/distributed-fs/ipfs-kubo/core/corehttp/p2p_proxy_test.go

## Purpose
Tests URL path parsing for the p2p HTTP proxy.

## Important APIs, Types, and Functions
Defines `TestCase`, `validtestCases`, `invalidtestCases`, `TestParseRequest`, and `TestParseRequestInvalidPath`.

## Control Flow and State
Valid cases build URLs for default `/http` and namespaced `/x/custom/http` protocols, then assert target peer, protocol ID, and proxied path. Invalid cases assert parser errors for missing/incorrect protocol path segments.

## Dependencies and Integration Points
Depends on net/http request construction, libp2p protocol IDs, and testify `require`. It validates the parsing helper used by `P2PProxyOption`.

## Risks and Test Signals
The test does not instantiate a libp2p HTTP transport or reverse proxy. It is a parser regression signal for path structure and PeerID validation only.
