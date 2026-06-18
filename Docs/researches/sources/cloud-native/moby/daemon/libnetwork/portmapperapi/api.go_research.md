<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmapperapi/api.go -->
## sources/cloud-native/moby/daemon/libnetwork/portmapperapi/api.go

Purpose: shared API contract between libnetwork and pluggable port mappers.

Important APIs/types/functions: `Registerer` registers mappers by name. `PortMapper` defines `MapPorts` and `UnmapPorts`. `PortBindingReq` extends `types.PortBinding` with `Mapper` and transient `ChildHostIP`. `PortBinding` extends `types.PortBinding` with mapper name, NAT target, forwarding flag, bound socket, rootless child IP, port-driver cleanup callback, proxy stop callback, and rootless unsupported marker. `ChildPortBinding` returns the daemon-visible host IP binding.

Control flow: `PortBindingReq.Compare` orders requests by mapper, exact-before-range, container port, protocol, host range, host IP, and container IP so equivalent multi-IP bindings are adjacent and can share a host port.

State and persistence: API structs carry runtime-only fields excluded from JSON. NAT/forwarding fields tell callers how to program firewall and proxy state.

Dependencies and integration points: used by NAT and routed mappers and higher libnetwork port-binding reconciliation.

Risks and test signals: incorrect compare ordering can prevent grouped multi-address allocations from sharing the same port. Test file covers the ordering dimensions.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmapperapi/api.go -->
