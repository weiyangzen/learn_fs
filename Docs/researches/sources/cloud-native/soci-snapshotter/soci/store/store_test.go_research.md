# sources/cloud-native/soci-snapshotter/soci/store/store_test.go

Purpose: this file tests content-store configuration helpers and GC label helper functions.

Important tests and helpers: `TestStoreCanonicalizeContentStoreType` checks empty/default, `soci`, `containerd`, and invalid types. `TestStoreGetContentStorePath` verifies default paths, custom SOCI root path, containerd ignoring custom root, and invalid type errors. `fakeStore` embeds ORAS memory store and records labels/deletes while satisfying the `Store` interface. `TestStoreLabelGCRoot` and `TestStoreLabelGCRefContent` assert label names, target digest, and referenced digest.

Control flow and state: tests are in-memory except for `filepath.Join` path expectations. Label helper tests record calls in slices on `fakeStore`.

Dependencies and integration points: validates behavior consumed by `soci_index.go` and `soci_convert.go` when keeping content reachable under containerd GC.

Risks and gaps: no tests instantiate `NewContentStore`, `NewSociStore`, or `ContainerdStore`; no tests cover `Push`, `Fetch`, `Exists`, `Delete`, batch leases, containerd client lazy initialization, address trimming, or already-exists normalization. The fake store does not emulate label update errors.

Test signal quality: solid for pure configuration and label formatting; absent for real storage behavior.
