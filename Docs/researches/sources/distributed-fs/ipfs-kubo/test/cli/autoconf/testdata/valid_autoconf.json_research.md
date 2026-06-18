# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/valid_autoconf.json

Purpose: baseline valid AutoConf fixture used across basic, expansion, fallback, cache, and consistency tests. It represents mainnet-like AminoDHT plus IPNI data in a small stable JSON payload.

Important fields: `AutoConfVersion` `2025072901`, schema `1`, TTL `86400`, `SystemRegistry.AminoDHT` with seven bootstrap multiaddrs and delegated read/write path capabilities, `SystemRegistry.IPNI` with provider-read capability, `DNSResolvers.eth.` with two DoH URLs, and `DelegatedEndpoints` for `https://ipni.example.com` and `https://delegated-ipfs.dev`.

Control flow is data-only. Tests serve it over `httptest`, use it to populate the daemon AutoConf cache, and assert that `Bootstrap`, `DNS.Resolvers`, `Routing.DelegatedRouters`, `Ipns.DelegatedPublishers`, and full config show can expand away from literal `auto`. State is remote AutoConf content that may be cached by the daemon. Dependencies are valid multiaddr parsing and HTTP/HTTPS URL validation. Risks include fixture duplication with fallback defaults and exact endpoint assumptions. Test signal is broad because many tests rely on this file as the canonical valid payload.
