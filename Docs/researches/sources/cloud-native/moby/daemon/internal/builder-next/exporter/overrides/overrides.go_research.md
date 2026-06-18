# sources/cloud-native/moby/daemon/internal/builder-next/exporter/overrides/overrides.go

## Purpose
Sanitizes BuildKit exporter image names before passing them into Moby/containerd image export.

## APIs, Control Flow, and Integration
`SanitizeRepoAndTags` skips empty names, parses normalized references, rejects references containing a digest, applies `reference.TagNameOnly`, and deduplicates while preserving first occurrence order. It returns normalized repo:tag strings for `exporter/wrapper.go`.

## State, Dependencies, and Risks
No persistence. Dependency is `distribution/reference`. The primary risk is user-visible normalization: untagged names become `:latest`, duplicate aliases are removed, and digest-tag combinations are forbidden with a generic error. Test coverage is indirect; wrapper behavior depends on this function to prevent BuildKit from naming immutable digest refs.
