# sources/cloud-native/moby/daemon/libnetwork/ipams/remote/remote.go

## Purpose
Implements the IPAM driver adapter for remote Docker plugins. It translates `ipamapi.Ipam` calls into plugin RPC calls and registers active/activated plugins.

## Important APIs, Types, And Functions
- `allocator` holds plugin client and name.
- `PluginResponse` abstracts responses with `IsSuccess` and `GetError`.
- `newAllocator` constructs an `ipamapi.Ipam`.
- `Register` registers existing managed plugins and installs a handler for future plugin activation.
- `getPluginClient` adapts v1 plugin clients or managed plugin addresses into `plugins.Client`.
- `call` invokes `IpamDriver.<method>` and converts plugin error fields into Go errors.
- `getCapabilities`, `GetDefaultAddressSpaces`, `RequestPool`, `requestPool`, `checkOverlaps`, `ReleasePool`, `RequestAddress`, `ReleaseAddress`, and `IsBuiltIn` implement the driver behavior.

## Control Flow
Registration probes plugin capabilities when possible; legacy plugins without capabilities are still registered. `RequestPool` first gets the global default address space, calls the plugin, and for local dynamic requests loops while returned pools overlap the request's excluded prefixes. Overlapping temporary leases are held to prevent the plugin from returning the same pool again, then released in a deferred cleanup.

## State And Persistence
The adapter itself stores only plugin endpoint/name. Actual allocation state is owned by the remote plugin. Temporary overlapping leases are released before returning from `RequestPool`.

## Dependencies And Integration Points
Uses Moby plugin APIs, `plugingetter`, `ipamapi`, remote API structs, libnetwork `types`, and containerd logging. It integrates plugin lifecycle with libnetwork's IPAM registry.

## Risks
Remote correctness depends on plugin behavior and protocol compatibility. The overlap loop can spin until plugin exhaustion/error if the plugin keeps handing excluded ranges. The code preserves old request-pool behavior including skipping overlap checks for explicit pools, global address space, and `0.0.0.0/0`. Missing or invalid address strings produce `ErrNoIPReturned` or parse errors.

## Test Signals
`remote_test.go` validates capability probing, legacy capability failure, default address space retrieval, pool/subpool request payload handling, metadata propagation, address request/release, and plugin spec HTTP setup.
