# sources/cloud-native/nydus-snapshotter/pkg/remote/remotes/docker/handler.go

## Purpose
Adds Docker distribution source-label support so pulled blobs/configs remember source repositories and future pushes can attempt cross-repository blob mounts.

## Important APIs, Types, And Functions
`AppendDistributionSourceLabel`, `appendDistributionSourceLabel`, `distributionSourceLabelKey`, `selectRepositoryMountCandidate`, and `commonPrefixComponents`.

## Control Flow
`AppendDistributionSourceLabel` parses the image reference into source host and repository, then returns an image handler. For each descriptor, it reads current content info, appends the repo into the source label, validates label size/format, and updates that label. Push code later reads descriptor annotations derived from these labels and `selectRepositoryMountCandidate` picks a different source repo with the longest common path-prefix match.

## State And Persistence
Persists labels in the content manager under `containerd.io/distribution.source.<host>`. The label value is a sorted, deduplicated comma-separated repo list.

## Dependencies And Integration Points
Uses containerd content manager, image handlers, label validation, and reference parsing. It integrates with `remotes.annotateDistributionSourceHandler` and `dockerPusher` mount-from flow.

## Risks And Edge Cases
Long labels may exceed containerd label validation and are skipped with a warning. The insertion-sort dedupe treats empty repos specially. Mount candidate selection excludes the target repo but otherwise trusts label content.

## Test Signals
`handler_test.go` validates label append/dedupe/sort behavior, label key construction, common-prefix counting, and mount candidate selection.
