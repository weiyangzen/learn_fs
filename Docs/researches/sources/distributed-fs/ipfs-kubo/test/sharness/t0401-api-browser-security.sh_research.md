## sources/distributed-fs/ipfs-kubo/test/sharness/t0401-api-browser-security.sh

Purpose: validates browser-origin protections for the RPC API, including localhost origins, known IPFS Companion extension IDs, and custom CORS allowlists.

Important commands and control flow: after daemon launch, browser-like POSTs without `Origin` or with invalid origin must return 403. Localhost origins for IPv4, IPv6, and hostname must return 200 and include the peer ID. Random extension origins are rejected, while production/beta Companion extension origins are allowed. The script then configures `API.HTTPHeaders.Access-Control-Allow-*`, restarts, confirms Companion still works, validates an OPTIONS preflight response, and checks valid custom origin POST access.

State and persistence: persists API CORS headers in repo config and observes daemon HTTP response headers/status codes.

Dependencies and integration points: depends on API origin security middleware, config header overrides, extension allowlist, HTTP preflight handling, `curl`, and peer identity.

Risks and test signals: high security value. Sensitive to header casing/text, HTTP protocol formatting, and changes to extension allowlist. Failures can indicate either overly permissive browser API access or broken legitimate localhost/Companion access.
