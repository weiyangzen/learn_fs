## sources/distributed-fs/ipfs-kubo/test/sharness/t0114-gateway-subdomains.sh

Purpose: comprehensive gateway subdomain support test for localhost defaults, custom public gateways, IPFS/IPNS subdomain routing, DNSLink inlining, proxy headers, wildcard gateway config, and path whitelist enforcement.

Important APIs and helpers: defines `test_localhost_gateway_response_should_contain` to test direct HTTP plus proxy, proxy1.0, and CONNECT modes, and `test_hostname_gateway_response_should_contain` for Host-header routing. It uses fixture CAR import, `ipfs routing put --allow-offline` for IPNS records, `Gateway.PublicGateways`, `Gateway.NoDNSLink`, `IPFS_NS_MAP`, `curl`, and daemon restarts.

Control flow and state: starts with empty public gateway config and validates implicit localhost subdomain redirects from `/ipfs` and `/ipns`, CIDv0-to-CIDv1 conversion, payload serving from `{cid}.ipfs.localhost`, directory-listing links, and IPNS key forms. It then enables DNSLink inlining, configures `example.com` with subdomains, checks redirects, invalid CID errors, `X-Forwarded-Proto`, protocol-handler `uri=` redirects, directory breadcrumb generation, long CID DNS label rejection, path whitelist 404s, path-gateway mode, DNSLink-only hosts, wildcard DNSLink, `X-Forwarded-Host`, wildcard public gateway host patterns, and explicit disabling of localhost defaults.

Dependencies and integration points: spans gateway router host matching, subdomain origin isolation, DNS label encoding, CID and PeerID codec conversion, DNSLink resolver injection, reverse proxy headers, directory listing HTML, public gateway policy, and HTTP proxy behavior.

Risks and test signals: protects many security and compatibility edges: origin isolation bypass, unsafe long DNS labels, wrong redirect schemes behind proxies, wildcard host misrouting, and DNSLink exposure when disabled. Signals are exact `Location` headers, HTTP 400/404/301/200 statuses, expected payload text, and directory listing link fragments.
