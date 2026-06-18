# sources/distributed-fs/ipfs-kubo/core/node/dns.go

Purpose: constructs the multiaddr DNS resolver used by node networking and gateway-style DNS resolution. The central API is `DNSResolver(cfg *config.Config)`.

Control flow: it builds optional DoH settings from `DNS.MaxCacheTTL`, resolves `auto` placeholders through `DNSResolversWithAutoConf`, and asks `gateway.NewDNSResolver` for the base resolver. If `AutoTLS.SkipDNSLookup` is false, the base resolver is returned. Otherwise it builds a local `p2pForgeResolver` for `libp2p.direct` plus any custom AutoTLS suffix and registers it as a domain resolver while retaining the base resolver as fallback.

State and persistence: no durable state is written. Runtime behavior depends on config values and the in-memory resolver chain.

Dependencies and integration: depends on boxo gateway DNS, libp2p DoH resolver, multiformats multiaddr-dns, and `NewP2PForgeResolver`. It integrates with `Online` and `Offline` node graphs via `fx.Provide(DNSResolver)`, feeding namesys and multiaddr resolution.

Risks: incorrect `MaxCacheTTL` changes cache lifetime; local p2p-forge short-circuiting must still delegate TXT lookups for ACME; custom suffix handling must include trailing-dot domain registration. Test signal comes from the compile-time `madns.BasicResolver` assertion and dedicated p2p-forge resolver tests.
