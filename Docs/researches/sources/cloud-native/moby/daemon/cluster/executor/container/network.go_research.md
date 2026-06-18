# Research: sources/cloud-native/moby/daemon/cluster/executor/container/network.go

## sources/cloud-native/moby/daemon/cluster/executor/container/network.go

Purpose: converts SwarmKit `api.IPAMConfig` into Engine `network.IPAMConfig` while collecting parse errors. The single API is `ipamConfig`.

Control flow parses subnet and range with `netiputil.MaybeParseCIDR`, parses gateway with `MaybeParseAddr`, unmaps the gateway address, and returns `errors.Join` of all parse failures so callers can log a complete validation result. `container.go` uses this when building swarm network creation requests and `executor.go` uses it for ingress setup.

There is no persistent state. Dependencies are Engine network API types, SwarmKit IPAM structs, and daemon netip utilities. Risk is that callers often append the returned config even when errors are logged, so malformed fields may produce partially populated network create requests. Test coverage for this helper is indirect through network creation paths; no direct tests are in this subset.
