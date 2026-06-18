## sources/distributed-fs/ipfs-kubo/test/sharness/t0115-gateway-dir-listing.sh

Purpose: verifies generated gateway directory listing HTML for path, subdomain, and DNSLink gateway modes.

Important APIs and helpers: uses `ipfs dag import` fixtures, gateway `curl` requests, `Gateway.PublicGateways`, `IPFS_NS_MAP`, daemon restarts, and HTML substring assertions.

Control flow and state: initializes a repo, imports a test directory, serves it through path gateway, subdomain gateway, and DNSLink gateway variants. For each mode it checks root backlink hiding, trailing-slash redirects, ETag presence, parent links, breadcrumb construction, name-column links, and hash-column CID links. It cleans up the repo at the end.

Dependencies and integration points: covers UnixFS directory listing generation, gateway mode-specific URL construction, DNSLink content roots, `filename` query linking, and cache validators.

Risks and test signals: catches broken relative links that can escape content roots or fail behind subdomains, missing ETags, and invalid breadcrumbs. Passing signals are expected HTML anchor fragments and redirect/header presence for all gateway modes.
