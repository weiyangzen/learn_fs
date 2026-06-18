<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/handler.go -->
# sources/cloud-native/containerd/core/remotes/docker/handler.go

## Purpose
Manages distribution source labels and cross-repository mount candidate selection. These labels record where content came from so pushes can try efficient registry-side blob mounts instead of reuploading common layers.

## Important APIs, Types, And Functions
- `AppendDistributionSourceLabel(manager, ref)` returns an image handler that appends a repository to the content label `containerd.io/distribution.source.<host>`.
- `appendDistributionSourceLabel(originLabel, repo)` sorts and deduplicates comma-separated repository values.
- `distributionSourceLabelKey(source)` builds the label key.
- `selectRepositoryMountCandidate(refspec, sources)` selects the best source repository for a cross-repo mount by longest common path-prefix components.
- `commonPrefixComponents(components, target)` scores path similarity.

## Control Flow
`AppendDistributionSourceLabel` parses the reference, extracts registry host and repository, and returns a descriptor handler. The handler reads content info, builds the source-label value, validates label size/key rules, and updates only the target label field. Pusher code later examines descriptor annotations to choose a mount source.

## State And Persistence
State is persisted as content-store labels through `content.Manager.Update`. The append helper uses sorted strings to keep deterministic label values and collapse duplicates.

## Dependencies And Integration Points
Depends on `content.Manager`, `images.HandlerFunc`, `labels.Validate`, `reference.Parse`, and OCI descriptors. Integrates with generic remotes handler annotation propagation and `pusher.go` cross-repo mount logic.

## Risks And Edge Cases
Content labels have size limits, and widely shared layers can accumulate many source repositories; the handler logs and skips label updates when validation fails. Candidate selection intentionally skips the target repo and may choose a later equal-score repo because it uses `>=`.

## Test Signals
`handler_test.go` covers label append sorting/deduplication, label key construction, prefix scoring, and mount candidate selection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/handler.go -->
