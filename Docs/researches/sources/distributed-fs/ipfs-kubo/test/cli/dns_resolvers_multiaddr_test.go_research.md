# sources/distributed-fs/ipfs-kubo/test/cli/dns_resolvers_multiaddr_test.go

Purpose: regression coverage that `DNS.Resolvers` applies to multiaddr DNS resolution while `libp2p.direct` peer-address hostnames still resolve locally.

Important APIs/constants/functions: `testDomainSuffix`, `TestDNSResolversApplyToMultiaddr`, config `DNS.Resolvers`, bootstrap clearing, `swarm connect`, `id --peerid-base base36`, and `SwarmAddrs`.

Control flow: one subtest configures a broken DoH resolver and expects `/dnsaddr/bootstrap.libp2p.io` connection to fail with DNS/dial-related text. The second creates two local nodes, breaks node0’s resolver, constructs a `libp2p.direct` DNS4 multiaddr from node1’s base36 peer ID and TCP port, and asserts swarm connection succeeds.

State/persistence: daemon config, bootstrap lists, local peer connections, and DNS resolver settings.

Dependencies/integration: DNS resolver wiring, multiaddr resolver stack, p2p-forge/libp2p.direct local resolution, peer ID base conversion, and swarm dialer.

Risks/test signals: includes sleeps and error-message alternatives for asynchronous startup and DNS implementation variation.
