## sources/distributed-fs/ipfs-kubo/test/sharness/t0109-gateway-web-_redirects.sh

Purpose: end-to-end coverage for HTTP gateway `_redirects` files, including redirects, rewrites, custom errors, validation failures, DNSLink, and origin-isolation boundaries.

Important APIs and helpers: uses `ipfs dag import --pin-roots` with fixture CARs, `curl -sD - --resolve`, gateway hostnames, `IPFS_NS_MAP`, `ipfs resolve`, `Gateway.NoDNSLink`, and daemon launch/kill helpers.

Control flow and state: imports multiple fixture directories, requests subdomain gateway URLs whose content roots include `_redirects`, and checks default 301 redirects, explicit 301/302, 200 rewrites, placeholder and splat expansion, custom 404/410/451 responses, catch-all behavior, CRLF parsing, accepted and rejected status codes, invalid file diagnostics, and too-large file rejection. It also verifies path gateway requests do not apply custom `_redirects` without origin isolation, and tests DNSLink-enabled vs DNSLink-disabled hosts.

Dependencies and integration points: covers Boxo gateway web routing, `_redirects` parser limits, subdomain origin isolation, DNSLink resolution, public gateway config, and HTTP status/header semantics.

Risks and test signals: catches security-sensitive redirect leakage across origins, bad parser acceptance, incorrect status codes, and DNSLink policy regressions. Signals are HTTP status lines, `Location` headers, response bodies, and absence of redirects when disabled.
