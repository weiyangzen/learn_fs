## sources/cloud-native/buildkit/util/estargz/labels.go

Purpose: generates snapshot labels needed by stargz snapshotter remote/lazy-pull integration for eStargz layers.

Important API: `SnapshotLabels(ref string, descs []ocispecs.Descriptor, targetIndex int) map[string]string` extracts TOC digest and uncompressed size annotations from the target descriptor, records remote reference and target digest, and builds a comma-separated layer digest list.

Control flow: if the descriptor slice is too short for the target index it returns nil; otherwise it iterates from `targetIndex` forward and appends layer digests until `containerd/pkg/labels.Validate` reports the label would exceed constraints. It trims the final comma before returning.

State/persistence: stateless label map creation. Dependencies: containerd labels validation, stargz snapshotter annotation keys, OCI descriptors.

Integration points: output labels are consumed by containerd snapshotters under `containerd.io/snapshot/remote/stargz.*`. Risks: the bounds check uses `len(descs) < targetIndex`, so `targetIndex == len(descs)` would panic; expected callers likely provide valid indices. Skipping layer digests is accepted but can reduce remote snapshotter performance. Test signals: no direct test in this subset.
