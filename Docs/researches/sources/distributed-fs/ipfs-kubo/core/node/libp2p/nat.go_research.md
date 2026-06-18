# sources/distributed-fs/ipfs-kubo/core/node/libp2p/nat.go

Purpose: provides NAT port mapping and AutoNAT service options. Important APIs are `NatPortMap` and `AutoNATService`.

Control flow: `NatPortMap` is a simple option wrapping `libp2p.NATPortMap`. `AutoNATService` enables the AutoNAT service, applies optional throttle limits, and enables AutoNAT v2 unless `v1only` is true.

State and persistence: no persistence; options affect runtime host services.

Dependencies/integration: Kubo AutoNAT throttle config and libp2p options. Wired by `groups.go` based on `Swarm.DisableNatPortMap` and `AutoNAT.ServiceMode`.

Risks: enabling NAT services broadly affects resource use and network behavior; throttle config must be sane. No direct tests.
