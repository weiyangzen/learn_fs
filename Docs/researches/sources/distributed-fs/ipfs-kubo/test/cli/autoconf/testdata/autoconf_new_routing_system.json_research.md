# sources/distributed-fs/ipfs-kubo/test/cli/autoconf/testdata/autoconf_new_routing_system.json

Purpose: compact AutoConf fixture for a non-native `NewRoutingSystem`, used to prove new delegated systems can populate routing and IPNS publisher fields under auto routing.

Important fields: `SystemRegistry.NewRoutingSystem` has `URL`, description, `DelegatedConfig.Read` for providers, peers, and IPNS, and `DelegatedConfig.Write` for IPNS. `DNSResolvers.eth.` points at `dns.eth.limo`. `DelegatedEndpoints` maps `https://new-routing.example.com` to `Systems: ["NewRoutingSystem"]`, read providers/peers, and write IPNS.

Control flow is data-only. `expand_test.go` serves this fixture, starts a daemon to cache it, and expects `config Routing.DelegatedRouters --expand-auto` to include provider and peer URLs under `new-routing.example.com`, while `Ipns.DelegatedPublishers` includes `/routing/v1/ipns`. State is the declared service registry and endpoint capability matrix. Dependencies are path-joining/filtering logic in AutoConf expansion. Risks include unsupported endpoint schemes or path policy changes invalidating expected URLs. Test signal demonstrates extensibility for unknown delegated systems.
