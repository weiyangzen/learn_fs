# sources/cloud-native/moby/daemon/internal/distribution/pull_v2.go

## Purpose
Implements Docker Registry v2 image pull: manifest resolution, platform selection, config/layer download, verification, metadata recording, image-store insertion, and refstore updates.

## APIs, Control Flow, and Integration
`newPuller` wires endpoint, repo name, config, metadata service, and manifest store. `pull` creates an authenticated repository and manifest service. `pullRepository` pulls a specific ref or all tags. `pullTag` resolves tag/digest to manifest, validates config media type, dispatches schema2/OCI/manifest-list handling, writes digest status, and updates tag/digest references. `pullSchema2Layers` skips existing images, validates media types, builds `layerDescriptor`s, concurrently pulls image config and layers, checks Windows compatibility early, verifies downloaded DiffIDs match config rootfs, and stores image config. `layerDescriptor.Download` supports temp-file resume, byte-range retry, digest verification, and metadata registration.

## State, Dependencies, and Risks
State spans temp files, layer store via download manager, image store configs, refstore tags/digests, content-store manifest cache, and v2 metadata. Risks include concurrent config/layer race handling, rootfs mismatch security, AI/unsupported media type blocking, digest verification, temp-file cleanup, and manifest-list recursion/no-match handling. Tests cover no-match messages and config retry/auth behavior.
