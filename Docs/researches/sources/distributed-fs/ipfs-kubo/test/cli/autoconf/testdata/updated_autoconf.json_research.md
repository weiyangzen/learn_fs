# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/updated_autoconf.json

Purpose: updated AutoConf fixture used by refresh/cache tests to simulate a newer remote configuration. It expands the bootstrap set, adds DNS resolver data, and includes more delegated endpoints than the baseline fixture.

Important fields: `AutoConfVersion` is `2025072902`, distinguishing it from `valid_autoconf.json`. `AminoDHT.NativeConfig.Bootstrap` contains seven bootstrap multiaddrs, including DNS, TCP, and QUIC variants. `IPNI` points to `https://ipni.example.com`. `DNSResolvers` includes two `eth.` DoH URLs and `test.`. `DelegatedEndpoints` includes IPNI, routing.example.com, delegated-ipfs.dev with providers/peers/IPNS read plus IPNS write, and ipns.example.com for IPNS read/write.

Control flow is fixture-only: servers switch from initial to updated content or serve it for post-refresh tests. State represented is a remote versioned config and cache replacement candidate. Dependencies are schema compatibility and validation of multiaddrs/URLs. Risks include hard-coded public bootstrap peers and example endpoints becoming inconsistent with validation policy. Test signal is request-count and expansion behavior when remote AutoConf changes.
