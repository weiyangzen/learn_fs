<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmappers/nat/mapper_linux.go -->
## sources/cloud-native/moby/daemon/libnetwork/portmappers/nat/mapper_linux.go

Purpose: Linux NAT port mapper that allocates host ports, binds sockets, prepares NAT metadata, and integrates with RootlessKit port drivers.

Important APIs/types/functions: `PortDriverClient` abstracts RootlessKit child IP and port-add calls. `Register` registers mapper name `nat`. `Config` passes `RlkClient`. `PortMapper.MapPorts` and `UnmapPorts` implement the mapper. Helpers `setChildHostIP` and `configPortDriver` handle rootless child namespace translation and cleanup callbacks.

Control flow: `MapPorts` verifies all grouped requests share protocol, container port, and host range. Unsupported rootless requests are dropped. It requests one common port for all child host IPs from `portallocator.NewOSAllocator`, constructs `PortBinding` entries with `BoundSocket` and `NAT`, then configures the port driver. On any error, a defer unmaps partial bindings. `UnmapPorts` closes sockets, invokes RootlessKit removal callbacks, then releases logical ports.

State and persistence: state is returned to callers as bindings; no mapper-owned persistent map. Socket ownership transfers through `BoundSocket`.

Dependencies and integration points: depends on `portallocator`, `portmapperapi`, RootlessKit client errors, and firewall/proxy consumers.

Risks and test signals: grouped request mismatch is guarded. Dropping unsupported rootless requests can produce fewer bindings. Cleanup must close sockets and release allocations. Test covers mismatch error.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/portmappers/nat/mapper_linux.go -->
