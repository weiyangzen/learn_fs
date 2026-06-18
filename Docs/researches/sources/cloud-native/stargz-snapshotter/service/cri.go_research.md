<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/cri.go -->
# sources/cloud-native/stargz-snapshotter/service/cri.go

## Purpose
Builds a `source.GetSources` provider from CRI snapshot labels. It lets the filesystem resolve a specific target layer and optionally pre-resolve neighboring image layers for parallel lazy pulling.

## Important APIs, Types, And Functions
- Label constants cover image ref, target layer digest, full image layer list, descriptor URL maps, and target URLs.
- `sourceFromCRILabels(hosts)` returns a closure that parses labels into one `source.Source`.
- Uses `reference.Parse`, `digest.Parse`, and OCI descriptors/manifests.

## Control Flow
The closure requires `containerd.io/snapshot/cri.image-ref` and `containerd.io/snapshot/cri.layer-digest`. It parses optional comma-separated image layer labels, skips the target digest when building neighbors, attaches URLs from indexed labels, adds target URLs, and returns a manifest whose first layer is the target followed by neighbors.

## State And Persistence
No persistent state is written. State is derived from snapshot labels supplied during `Prepare`.

## Dependencies And Integration Points
Integrated by `service.NewFileSystem` ahead of default label parsing. It depends on containerd CRI label conventions and stargz filesystem `source.Source` semantics.

## Risks And Edge Cases
Missing or malformed labels fail source resolution. Neighbor layer metadata affects performance rather than correctness. URL labels are comma-split without escaping, so unusual URL values can misparse.

## Test Signals
Expected signals are successful source construction from CRI labels, digest parse failures for invalid labels, descriptor URL propagation, and fallback to other source providers when CRI labels are absent.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/service/cri.go -->
