# sources/cloud-native/moby/daemon/libnetwork/network_windows.go

## Purpose
Windows platform implementation for network compartment execution, internal DNS resolver lifecycle, HNS endpoint resolver configuration, Windows IPAM defaulting, and prune eligibility for HNS-owned networks.

## Important APIs, Types, And Functions
`platformNetwork` stores `resolverOnce` and `dnsCompartment`. `executeInCompartment` locks the OS thread and switches HNS compartment. `ExecFunc` runs a callback inside the DNS compartment. `startResolver` creates resolvers on HNS subnet gateways. `IsPruneable` protects predefined and externally owned HNS networks. `addEpToResolverImpl` and `deleteEpFromResolverImpl` configure per-source external DNS forwarding. `findHNSEp`, `findResolver`, and `defaultIpamForNetworkType` support those flows.

## Control Flow
Resolver startup ignores ICS networks, loads the HNS network by ID from driver options, iterates subnets with gateways, creates resolvers, sets the DNS compartment, retries resolver start up to three times, and stores successful resolvers. Endpoint resolver configuration finds the matching HNS endpoint by IPv4/IPv6 address, ensures internal DNS is enabled, finds the resolver by gateway, removes the resolver itself from the DNS server list, and sets external servers for endpoint source addresses. Deletion clears those per-source mappings.

## State And Persistence
State is process-local in `Network.resolver`, `resolverOnce`, and `dnsCompartment`. HNS network/endpoint state is read through `hcsshim`. Generic driver labels persist ownership and HNS IDs.

## Dependencies And Integration Points
Integrates with Microsoft HNS/hcsshim, Windows libnetwork drivers, Windows IPAM, resolver internals, netlabel generic options, and Windows daemon predefined network names.

## Risks
Compartment switching must stay on a locked OS thread and reset to compartment 0. Resolver setup depends on HNS data shape and gateway/DNS server strings. `addEpToResolver`/`deleteEpFromResolver` ignore HNS list errors, which avoids hard failures but can hide cleanup/configuration gaps. Prune logic is compatibility-sensitive for adopted HNS networks.

## Test Signals
`network_windows_test.go` validates resolver selection, external DNS extraction, IPv4/IPv6 source mappings, disabled internal DNS handling, and cleanup.
