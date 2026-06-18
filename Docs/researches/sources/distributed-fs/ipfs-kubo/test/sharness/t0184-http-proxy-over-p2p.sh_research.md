## sources/distributed-fs/ipfs-kubo/test/sharness/t0184-http-proxy-over-p2p.sh

Purpose: tests HTTP gateway proxying over `ipfs p2p`, including error propagation, multipart requests, protocol parsing, and `/p2p` subdomain gateway routing.

Important APIs and helpers: requires `socat`, uses IPTB nodes, `ipfsi p2p listen`, gateway config with `/p2p` path whitelisted, local HTTP server fixtures, `curl`, Host headers, receiver/sender peer IDs, and daemon stop/start helpers.

Control flow and state: configures two nodes and a subdomain gateway, connects them, registers a p2p listener on the receiver for HTTP, sets sender gateway environment, checks bad gateway when the remote server is absent, starts a local HTTP server, verifies remote error propagation and successful HTTP content, rejects invalid requests and unknown/invalid peers, tests custom and missing protocols, rejects missing `/http`, sends multipart/form-data, and checks subdomain gateway behavior for `/p2p/<peer>/http` including full-path rejection and path-to-subdomain redirect.

Dependencies and integration points: covers gateway `/p2p` router, p2p stream forwarding, HTTP proxy request mapping, multipart body transfer, peer ID CIDv1 subdomains, and public gateway path policy.

Risks and test signals: catches SSRF-like path confusion, bad peer validation, broken body streaming, and origin-isolation mistakes for p2p gateways. Signals are HTTP status lines, body text, redirect `Location`, and expected failures for malformed paths.
