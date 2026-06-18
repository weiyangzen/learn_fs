<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/contrib/diffservice/service.go -->
# sources/cloud-native/containerd/contrib/diffservice/service.go

## Purpose
Adapter that exposes containerd diff Applier/Comparer implementations as a gRPC Diff service.

## Important APIs, Types, And Functions
Defines `service`, `FromApplierAndComparer`, `Apply`, and `Diff`.

## Control Flow
Apply forwards request descriptors/mounts/options to the applier and returns applied digest. Diff forwards mount sets and media/ref/label options to comparer and returns descriptor.

## State And Persistence
May mutate content store/snapshots through underlying applier/comparer; service itself stores only interfaces.

## Dependencies And Integration Points
containerd diff interfaces, diff service protobuf API, OCI descriptors, mount types.

## Risks And Test Signals
Trusts underlying implementations for validation and persistence; thin adapter has little direct test coverage. Source size reviewed: 111 lines in the current workspace.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/contrib/diffservice/service.go -->
