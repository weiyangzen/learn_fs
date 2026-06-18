# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/autoconf_with_unsupported_paths.json

Purpose: AutoConf fixture for delegated-routing path filtering on an AminoDHT-associated endpoint set. It verifies that unsupported API paths are not exposed through `--expand-auto`.

Important fields: `AminoDHT` includes native bootstrap and delegated read/write declarations. `DNSResolvers.eth.` maps to `dns.eth.limo`. `DelegatedEndpoints` has `supported.example.com` with valid `/routing/v1/providers`, `/routing/v1/peers`, and `/routing/v1/ipns`; `unsupported.example.com` with nonstandard `/example/v0/*` and `/api/v1/custom`; and `mixed.example.com` with valid provider/peer/IPNS plus `/unsupported/path`.

Control flow is data-only and consumed by expansion tests after daemon cache prewarming. State is the remote capability description. Dependencies are AutoConf parser and supported-path filtering. Risks include differences between delegated routing mode and auto routing: AminoDHT can be native in auto mode but delegated in explicit delegated mode. Test signal is expected inclusion of valid supported/mixed URLs and exclusion of unsupported paths while preserving endpoint-level valid capabilities.
