# sources/cloud-native/moby/daemon/containerd/image_delete.go

## Purpose
Implements image deletion, untagging, platform-specific content removal, conflict detection, and optional dangling-parent pruning for the containerd-backed image service.

## Important APIs, Types, And Functions
- `ImageDelete` is the public delete API.
- `deleteImagePlatforms` and `deleteImagePlatformByImageID` remove selected platform descriptor content.
- `deleteAll`, `imageDeleteHelper`, `untagReferences`, and `getSameReferences` manage image reference deletion.
- `checkImageDeleteConflict` classifies running-container, stopped-container, and active-reference conflicts.
- `imageDeleteConflict`, `conflictType`, and `isImageIDPrefix` support delete semantics and errors.

## Control Flow
Deletion resolves the requested ref/ID to a matching image and all references sharing the target. Named references may only untag matching references, while explicit image IDs or dangling refs can delete all references. Conflicts are hard for running containers and soft for stopped containers or multiple active refs unless force is used. Platform-specific deletion walks present descendants of the selected manifest and deletes content digests directly. Full deletion removes image records, logs untag/delete events, records API delete responses, and optionally prunes dangling parents quietly.

## State And Persistence
Mutates the containerd image store by deleting image names and can mutate the content store for platform-specific deletion. It may create a dangling image name to preserve parent/child relationships before deleting an active tag. It logs daemon image events and updates metrics on successful full API calls.

## Dependencies And Integration Points
Depends on image resolution helpers, container store usage checks, containerd image/content APIs, events, metrics, platform matchers, daemon image errors, and parent/child label helpers. It backs `docker image rm` and platform variant removal.

## Risks And Edge Cases
Reference grouping is subtle: tags, digest refs, dangling refs, and other repositories sharing the same target are treated differently. Platform deletion warns that shared manifests across indexes are not fully protected. Mounted image volumes are checked by source digest, but parentage conflicts are still a TODO. Force can untag images used by containers but must not remove running-container images through hard conflicts.

## Test Signals
`image_delete_test.go` covers many reference-resolution and untag/delete combinations. Additional integration coverage is needed for containers, forced deletes, platform deletion, events, and parent pruning.
