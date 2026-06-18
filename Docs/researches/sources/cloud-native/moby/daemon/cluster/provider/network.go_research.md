# Research: sources/cloud-native/moby/daemon/cluster/provider/network.go

## sources/cloud-native/moby/daemon/cluster/provider/network.go

Purpose: defines lightweight provider data structures used by the container executor and daemon cluster backend for swarm-managed network creation and service binding.

Types: `NetworkCreateRequest` embeds Engine `network.CreateRequest` with a swarm network ID; `NetworkCreateResponse` returns an ID; `VirtualAddress` stores IPv4/IPv6 service VIPs; `PortConfig` stores service port metadata; `ServiceConfig` stores service ID/name, aliases, virtual addresses, and exposed ingress ports.

There is no control flow or persistence. Integration points include `container.go` network/service config generation and backend methods that create managed networks or activate service bindings. Risks are schema drift with libnetwork/backend expectations and sparse IPv6 use because current service config generation only fills IPv4 VIPs. Tests are indirect.
