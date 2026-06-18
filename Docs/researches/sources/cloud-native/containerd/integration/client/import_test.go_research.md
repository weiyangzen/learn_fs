<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/import_test.go -->
# sources/cloud-native/containerd/integration/client/import_test.go

## Purpose
Exercises archive import/export and transfer-based image import for Docker v2 archives, OCI layouts, sparse indexes, labels, ref prefix/filter behavior, digest references, and garbage-collection safety after import.

## APIs, Types, And Functions
Tests are `TestExportAndImport`, `TestExportAndImportMultiLayer`, `TestImport`, and `TestTransferImport`. Helpers include `testExportImport`, `checkImages`, `createContent`, `createConfig`, `createManifest`, `createManifestList`, `createIndex`, `imagesProgress`, `createImages`, and `hash64`. The file uses `client.Export`, `client.Import`, `client.Transfer`, archive import/export options, transfer `image.Store`, `tartest`, content APIs, leases, compression, OCI specs, and platform matching.

## Control Flow And State
`testExportImport` fetches an image, exports it, deletes it, imports with an image ref translator, unpacks imported records, creates/deletes a lease to force GC, and verifies a container can still be created from the image. `TestImport` builds synthetic tar archives for valid and invalid Docker/OCI cases, imports them into unique namespaces, and checks resulting image names, target digests, manifests, labels, or expected errors. `TestTransferImport` builds OCI layouts with named, tag-only, manifest digest, and index digest references, transfers an import stream into an image store, tracks progress events, and verifies saved image descriptors.

## Persistence And Integration Points
The tests write temporary tar files/streams, daemon content, image records, leases, and snapshots. They integrate with OCI image layout grammar, Docker legacy archive layouts, archive ref translators, transfer progress, named/digest image storage options, and GC retention through leases/snapshots.

## Risks And Test Signals
Failures identify import regressions around sparse indexes, missing descendants, bad OS/arch configs, annotation-derived names, label propagation, digest ref overwrites, media type preservation, and GC deleting needed content. The multi-layer test skips unavailable architecture combinations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/integration/client/import_test.go -->
