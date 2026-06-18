# sources/distributed-fs/ipfs-kubo/core/corehttp/webui.go

## Purpose
Provides the `/webui/` API handler and records the current and historical WebUI IPFS paths.

## Important APIs, Types, and Functions
Exports `WebUIPath`, `WebUIPaths`, and `WebUIOption`; internal type `webUIHandler` implements `ServeHTTP`, `writeIncompatibleError`, and `writeNotAvailableError`.

## Control Flow and State
`WebUIOption` reads API headers and gateway flags from config, then mounts `/webui/`. Requests copy API headers, reject if deserialized gateway responses are disabled, optionally check the hardcoded WebUI CID is locally present when `Gateway.NoFetch` is true, and otherwise redirect to `WebUIPath`.

## Dependencies and Integration Points
Depends on Kubo config, node blockstore, CIDs, net/http, and gateway deserialized response semantics. It integrates API endpoint behavior with gateway content retrieval.

## Risks and Test Signals
Risks include stale `WebUIPath`, NoFetch availability checks only checking the root block, config combinations that make WebUI unusable, and user-facing error text drift. Tests should verify redirect, headers, incompatible deserialization mode, NoFetch missing/present block behavior, and path list maintenance.
