<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/api/types/system/info.go -->
# sources/cloud-native/moby/api/types/system/info.go

## Purpose
Info contains response of Engine API: GET "/info"

## Important APIs, Types, And Functions
- Exported types: Info, ContainerdInfo, ContainerdNamespaces, PluginsInfo, Commit, NetworkAddressPool, FirewallInfo, DeviceInfo, NRIInfo.
- `Info` fields include ID, Containers, ContainersRunning, ContainersPaused, ContainersStopped, Images, Driver, DriverStatus, SystemStatus, Plugins, MemoryLimit, SwapLimit, CPUCfsPeriod, CPUCfsQuota, and others.
- `ContainerdInfo` fields include Address, Namespaces.
- `ContainerdNamespaces` fields include Containers, Plugins.
- `PluginsInfo` fields include Volume, Network, Authorization, Log.
- `Commit` fields include ID.
- Wire JSON fields include CpuCfsPeriod, CpuCfsQuota, Driver, FirewallBackend, HttpProxy, HttpsProxy, ID, Info, Source.
- Source comments highlight: Info contains response of Engine API: GET "/info" ContainerdInfo holds information about the containerd instance used by the daemon. ContainerdNamespaces reflects the containerd namespaces used by the daemon.

## Control Flow
- There is no active control flow; the file defines data contracts serialized by higher-level daemon/client code.

## State And Persistence
- The file stores no process-local mutable state; structs represent serialized daemon state, request options, or response bodies.
- Several fields use `omitempty`, so absent, zero, and explicitly empty values can carry different compatibility implications.
- Persistence is external: Docker daemon stores the actual objects, while these types preserve the wire representation exposed to clients.

## Dependencies And Integration Points
- Imports: `net/netip`, `github.com/moby/moby/api/types/container`, `github.com/moby/moby/api/types/registry`, `github.com/moby/moby/api/types/swarm`.
- Integrates as a public `api/types` wire contract used by daemon handlers, client decoding, CLI output, and downstream Go consumers.
- Uses `net/netip` typed IP/prefix values, preserving validated address semantics instead of raw strings.

## Risks And Edge Cases
- Public API compatibility risk: field names, JSON tags, enum strings, and zero-value behavior are consumed by external clients.
- Address parsing and JSON behavior depend on `netip` semantics; invalid or legacy textual addresses need explicit handling upstream.

## Test Signals
- No direct test file is paired with this source; coverage is mostly integration-level through daemon/client API tests and compile-time use by downstream packages.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/api/types/system/info.go -->
