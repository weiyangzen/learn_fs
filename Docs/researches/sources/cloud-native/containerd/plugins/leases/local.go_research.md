# sources/cloud-native/containerd/plugins/leases/local.go

## Purpose
Registers the local lease manager plugin and adds synchronous-delete GC behavior.

## Important APIs, Types, And Functions
`gcScheduler` abstracts `ScheduleAndWait`. `local` embeds `leases.Manager` and overrides `Delete`. `init` constructs a metadata lease manager and stores the GC scheduler dependency.

## Control Flow
Startup gets metadata DB and GC scheduler, returns a `local` manager. Delete applies delete options, deletes the lease through the embedded manager, then triggers and waits for GC when `leases.SynchronousDelete` is requested.

## State And Persistence
Lease data is persisted in metadata DB. GC may remove unreferenced content/snapshots after lease deletion.

## Dependencies And Integration Points
Requires metadata and GC plugins. The gRPC leases service depends on this plugin and exposes synchronous delete through request flags.

## Risks
If GC fails after lease deletion, the delete call returns an error even though the lease is already removed. Synchronous delete latency depends on full metadata GC duration.

## Test Signals
No direct tests here; lease service and GC scheduler tests cover adjacent behavior.
