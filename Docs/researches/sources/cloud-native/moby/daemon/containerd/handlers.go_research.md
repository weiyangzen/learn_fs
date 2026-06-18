# sources/cloud-native/moby/daemon/containerd/handlers.go

## Purpose
Defines descriptor-walk helpers that traverse only content present in the local content store. This is used when operations need to inspect or delete reachable descriptors without failing on missing children.

## Important APIs, Types, And Functions
- `ImageService.walkPresentChildren` wraps containerd `images.Walk`.
- `presentChildrenHandler` checks descriptor presence with `content.Store.Info`, invokes a caller handler, and appends containerd-discovered child descriptors.

## Control Flow
For each descriptor, the wrapper first verifies the digest exists. Missing descriptors return `images.ErrSkipDesc`, which prunes that branch. Present descriptors are passed to the caller handler, then `images.Children` is called to discover and append children, again skipping missing child metadata.

## State And Persistence
Read-only. It observes the content store but does not mutate descriptors or labels.

## Dependencies And Integration Points
Depends on containerd content and image traversal APIs. It is used by platform-specific image deletion to gather content descendants that are actually present before deletion.

## Risks And Edge Cases
The helper deliberately tolerates missing content, which is correct for partial image stores but can hide integrity issues if used where complete content is required. Non-not-found errors still abort traversal.

## Test Signals
Indirectly covered by image deletion and platform-specific content tests. Expected signals are skipped missing descriptors and correct traversal of present manifests/config/layers.
