<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmappers/routed/mapper_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/portmappers/routed/mapper_linux.go

Purpose: Linux routed-mode port mapper for networks where NAT is disabled and host port numbers should not be allocated.

Important APIs/types/functions: registers mapper name `routed`; `PortMapper` implements `MapPorts` and `UnmapPorts`.

Control flow: `MapPorts` returns one `PortBinding` for each request with `Forwarding=true`. If a host port or host range is specified, it logs that the host port is ignored because NAT is disabled and clears `HostPort`/`HostPortEnd`. `UnmapPorts` is a no-op.

State and persistence: no internal state, no sockets, no logical port allocations.

Dependencies and integration points: used by libnetwork port-mapper registry. The returned `Forwarding` flag tells higher layers to allow forwarding to the container address without DNAT.

Risks and test signals: users may be surprised that requested host ports are ignored in routed mode, but the log makes the behavior explicit. No direct test is in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmappers/routed/mapper_linux.go -->
