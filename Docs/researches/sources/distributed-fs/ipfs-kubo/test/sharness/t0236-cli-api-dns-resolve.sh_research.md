## sources/distributed-fs/ipfs-kubo/test/sharness/t0236-cli-api-dns-resolve.sh

Purpose: verifies CLI API dialing resolves `/dns4/localhost` multiaddrs correctly while preserving the HTTP request target.

Important APIs and helpers: requires `SOCAT`, uses fake API server on port 5006, FIFOs, `ipfs cat --api /dns4/localhost/tcp/5006`, manual HTTP responses, and `grep`.

Control flow and state: starts a fake API server, runs an `ipfs cat` command against a DNS multiaddr, responds to version and cat requests, captures headers, stops the server, and verifies a POST to `/api/v0/cat` was sent. State is transient socket/FIFO state only.

Dependencies and integration points: covers DNS multiaddr resolution, CLI API HTTP transport, version probing, and request path construction.

Risks and test signals: catches failures to resolve DNS API addresses or attempts to use the unresolved multiaddr as an invalid network endpoint. Passing is the fake server seeing the expected API request.
