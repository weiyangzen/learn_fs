# sources/cloud-native/containerd/plugins/services/leases/service.go

## Purpose
Registers the gRPC leases service over the local lease manager.

## Important APIs, Types, And Functions
`service` wraps `leases.Manager` and implements `Register`, `Create`, `Delete`, `List`, `AddResource`, `DeleteResource`, `ListResources`, and `leaseToGRPC`.

## Control Flow
Startup loads the lease manager plugin. Create applies labels and either random or requested ID. Delete maps sync flag to `leases.SynchronousDelete`. Resource methods convert proto resource IDs/types and delegate. List converts all leases to proto.

## State And Persistence
Lease records and resources persist in metadata DB through the lease manager. Synchronous delete can trigger GC through the local manager wrapper.

## Dependencies And Integration Points
Requires lease plugin ID `manager`, gRPC server registration, errgrpc, protobuf timestamp conversion, and core leases APIs.

## Risks
Delete with sync can return GC errors after lease deletion. Resource requests assume non-nil resource fields.

## Test Signals
No direct tests in this subset.
