<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/extra_status.go -->
# sources/cloud-native/moby/daemon/libnetwork/cnmallocator/extra_status.go

## Purpose
Adds optional IPAM operational status to Swarm network objects when callers request it through network extra options.

## Important APIs, Types, And Functions
`OnGetNetwork(ctx, swarmnet, typeurl, appdata)` implements `networkallocator.OnGetNetworker`. It parses `netextra.OptionsFrom`, resolves the local allocator network and IPAM driver, optionally uses `ipamapi.PoolStatuser`, constructs `networktypes.Status`, and marshals it back into `swarmnet.Extra`.

## Control Flow
If `WithIPAMStatus` is not set, it returns without mutation. Otherwise it loads local network pool IDs, calls `PoolStatus` for each pool, builds subnet status with `IPsInUse` and `DynamicIPsAvailable`, and writes marshaled status into the Swarm API object.

## State And Persistence
Reads allocator in-memory pool state and IPAM driver status. Mutates only the provided `api.Network` response object.

## Dependencies And Integration Points
Integrates SwarmKit network get hooks, Moby network API status types, `netextra` appdata encoding, and optional IPAM driver status support.

## Risks And Edge Cases
Status is unavailable if allocator state is missing or the IPAM driver does not implement `PoolStatuser`. Errors while reading one pool abort the entire status response.

## Test Signals
Useful tests would mock `PoolStatuser` and assert `swarmnet.Extra` contains per-subnet status only when requested.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/libnetwork/cnmallocator/extra_status.go -->
