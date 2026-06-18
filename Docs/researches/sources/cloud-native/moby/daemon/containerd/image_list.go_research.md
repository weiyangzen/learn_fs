<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_list.go -->
# sources/cloud-native/moby/daemon/containerd/image_list.go

Purpose: implements Docker image listing on top of containerd images, content, snapshots, and daemon container metadata, including multi-platform aggregation, manifest metadata, labels, filters, shared size, and optional identity fields.

Important APIs and flow: `Images` validates filters, builds an `imageFilterFunc`, lists image records, collapses multiple names by target digest, hides intermediate dangling builder images unless `All` is set, gathers tags by digest, and computes summaries in parallel. `multiPlatformSummary` walks reachable manifests, classifies image vs attestation vs pseudo image, records availability, content size, unpacked snapshot size, chain IDs, containers using each manifest, and best platform. `imageSummary` emits either a combined multi-platform summary or a selected `singlePlatformImage`. `setupFilters` implements `before`, `since`, `until`, `label`, `label!`, `dangling`, and `reference`. `setupLabelFilter` walks present config blobs and deliberately skips BuildKit attestation subtrees. `computeSharedSize` counts shared snapshot chain IDs and shared content blobs without double-counting duplicates within one image.

State and persistence: read-only over image metadata, content metadata/blobs, snapshot usage, container store state, and identity cache. It treats descriptor availability as a first-class output so partially present indexes can be listed.

Dependencies and integration: tightly integrated with `ImageManifest`, `presentChildrenHandler` and `walkReachableImageManifests`, containerd `images.Dispatch`, Docker reference parsing, Moby filters/timestamp parsing, daemon container store, snapshotter usage APIs, and image identity cache helpers.

Risks: concurrent summary calculation requires careful locking around result slices and shared-size maps. The selected best platform uses host preference when no platform was requested, but total size/container counts still represent all manifests. Label filters can be expensive because they dispatch through content for each candidate. Shared size currently assumes one configured snapshotter. Some paths log and continue on corrupt/missing content, so list output may be partial rather than failing.

Test signals: `image_list_test.go` covers total content size, missing layers, multi-platform grouping, odd targets, identity-cache-only behavior, and shared-size content counting. `image_provenance_test.go` covers attestation manifest classification in list output.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/containerd/image_list.go -->
