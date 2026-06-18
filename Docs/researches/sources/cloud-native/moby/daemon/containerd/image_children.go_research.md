# sources/cloud-native/moby/daemon/containerd/image_children.go

## Purpose
Finds image child and parent relationships encoded by classic builder labels in the containerd image store.

## Important APIs, Types, And Functions
- `getImagesWithLabel` lists image IDs with a matching label key/value.
- `Children(ctx, id)` returns images whose parent label equals `id`.
- `parents(ctx, id)` follows parent labels upward from a child image and returns parent image records.

## Control Flow
Children lookup is a direct image-store label filter. Parent traversal resolves the starting image by digest string, repeatedly reads the parent label, parses it as a digest, resolves that digest to an image, appends it, and continues until no parent label is present.

## State And Persistence
Read-only against containerd image labels. Parent relationships are only as accurate as labels written by builder/commit paths.

## Dependencies And Integration Points
Depends on containerd image store filters, Moby image IDs, and digest parsing. `parents` is used by image deletion to prune dangling parent images.

## Risks And Edge Cases
Malformed parent labels abort parent traversal. Multiple image references for the same digest are collapsed by `resolveImage` behavior, which may pick one reference. BuildKit images generally do not carry these legacy labels, so lineage is limited to classic builder images.

## Test Signals
No direct tests in this subset. Image deletion prune tests and builder cache tests should verify child/parent label behavior.
