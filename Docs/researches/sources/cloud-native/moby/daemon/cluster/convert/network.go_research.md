# sources/cloud-native/moby/daemon/cluster/convert/network.go

## Purpose
Converts swarmkit network, endpoint, IPAM, port, and filter representations to Docker API/network types and back for swarm-scoped networks.

## Important APIs, Types, And Functions
Key functions include `networkAttachmentFromGRPC`, `networkFromGRPC`, `ipamFromGRPC`, `endpointSpecFromGRPC`, `endpointFromGRPC`, `swarmPortConfigToAPIPortConfig`, `BasicNetworkFromGRPC`, `NetworkInspectFromGRPC`, `BasicNetworkCreateToGRPC`, `IsIngressNetwork`, and `FilterNetwork` methods.

## Control Flow
Inbound conversion copies metadata, annotations, drivers, endpoint ports/VIPs, IPAM configs, config-from references, and status extras. IP/CIDR parsing is best-effort for values already stored in swarmkit. Outbound network create conversion defaults IPAM driver to `default`, unmapped/masks prefixes, and includes config-from and IPv6 only when provided.

## State And Persistence
No local state. It translates swarmkit raft objects into API responses and create requests into raft specs.

## Dependencies And Integration Points
Used by cluster network APIs, filters, and task/service conversion. Integrates `netextra.StatusFrom`, libnetwork swarm scope, netip utility wrappers, and Docker network filters.

## Risks And Test Signals
Legacy ingress detection accepts label `com.docker.swarm.internal` plus name `ingress`. Invalid stored IPs become zero values. Test coverage here only checks `CreatedAt`; broader network API tests should cover IPAM/status/ingress/filter behavior.
