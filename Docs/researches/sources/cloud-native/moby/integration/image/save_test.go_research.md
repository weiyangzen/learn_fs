# sources/cloud-native/moby/integration/image/save_test.go

Purpose: integration tests for image save archive contents, OCI layout export, platform-filtered save/load, multi-image repository export, and layer directory permissions.

Important APIs and helpers: `imageSaveManifestEntry`, `tarIndexFS`, `TestSaveCheckTimes`, `TestSaveOCI`, `TestSaveAndLoadPlatform`, `TestSaveRepoWithMultipleImages`, `TestSaveDirectoryPermissions`, and `listTar`.

Control flow: `tarIndexFS` copies an archive to a temp file and uses `tar2go` for indexed reads. Time test ensures tar member modtimes are not newer than image creation or are zero for containerd export. OCI test saves images, reads `index.json`, manifests, configs, and blobs, and compares layer diff IDs and annotations. Platform round-trip pulls selected platforms, saves selected subsets, removes and reloads images, then inspects expected platforms. Multi-image test commits two tags under one repo plus busybox and validates `manifest.json`/blob coverage. Directory permission test builds a layer with owned directories, saves it, decompresses layers, and checks expected tar entries.

State and persistence: exercises image archive serialization, blob/config/manifest relationships, platform-specific content selection, repository tag grouping, and filesystem metadata in layers.

Dependencies and integration: depends on tar handling, `tar2go`, compression detection, OCI specs, digest calculations, BuildKit/build helpers, fake contexts, special images, API version gates, and image save/load APIs.

Risks: platform round-trip pulls multiple architectures from a registry and is snapshotter-sensitive. Archive details differ between graphdriver and snapshotter modes, so assertions branch. Tar content expectations may vary by storage backend whiteout/dev entries.

Test signals: broad and deep coverage of archive correctness, OCI metadata, platform filtering, multi-image save, and preserved filesystem structure.
