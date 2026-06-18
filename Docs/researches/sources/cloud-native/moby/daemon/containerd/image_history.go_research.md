# sources/cloud-native/moby/daemon/containerd/image_history.go

## Purpose
Builds Docker image history output for a selected platform by reading OCI config history, computing layer sizes from snapshots, and assigning tags/IDs through legacy builder parent labels.

## Important APIs, Types, And Functions
- `ImageHistory(ctx, name, platform)` returns `[]*image.HistoryResponseItem`.
- `getImageTags` converts non-dangling image names into familiar references.
- `getParentsByBuilderLabel` locates parent image records through `org.mobyproject.image.parent`.

## Control Flow
The method resolves the image, selects the best present manifest for requested/default platform, reads config rootfs/history, computes cumulative chain snapshot usage for each diff ID, walks history entries in reverse Docker order, assigns size only to non-empty layers, then walks parent images to fill IDs and tags for each history item.

## State And Persistence
Read-only against image store, content store, and snapshotter usage data. It updates image-action metrics for successful history requests.

## Dependencies And Integration Points
Depends on platform matching, OCI identity chain IDs, containerd snapshot usage, distribution reference parsing, image labels, metrics, and image resolution. It backs `docker image history`.

## Risks And Edge Cases
Missing snapshots are logged and reported as zero-size rather than fatal. History entries with more non-empty layers than sizes cause an error. Parent lookup only works for legacy builder labels, so BuildKit lineage may show less ancestry. Invalid image names are skipped for tags.

## Test Signals
No direct tests in this subset. Expected coverage should include platform-specific history, missing snapshots, empty layers, tag assignment, and parent-label traversal.
