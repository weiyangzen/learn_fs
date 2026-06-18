# sources/cloud-native/soci-snapshotter/soci/store/store.go

Purpose: this file abstracts SOCI artifact blob storage over either an ORAS OCI layout store under the SOCI root or containerd's content store.

Important APIs and types: `BasicStore` defines `Exists`, `Fetch`, and `Push`. `Store` adds `Label`, `Delete`, and `BatchOpen`. `ContentStoreType` aliases config types. `ContainerdClient` lazily creates a containerd client under a mutex. `ContentStoreConfig` and `Option` configure store type, containerd address, snapshotter root, and client. `NewContentStore` selects `SociStore` or `ContainerdStore`. Helper functions include `CanonicalizeContentStoreType`, `GetContentStorePath`, `IsErrAlreadyExists`, `LabelGCRoot`, and `LabelGCRefContent`.

Control flow: ORAS-backed `SociStore` wraps `oci.Store` and stubs labels, delete, and batching. Containerd-backed `ContainerdStore` creates a client on demand, checks existence with content info, fetches through `ReaderAt` plus `io.SectionReader`, pushes with `content.OpenWriter`, copies in chunks below gRPC receive limit, validates size, commits by digest, labels content by updating label fields, deletes content, and opens leases for batch protection.

State and persistence: ORAS store persists blobs under the selected OCI layout path. Containerd store persists through containerd's content service and labels. `ContainerdClient` caches the client pointer for process lifetime.

Dependencies and integration points: integrates repo config defaults, containerd client/content/defaults, OCI descriptors, ORAS OCI store, ORAS/containerd already-exists errors, and SOCI index/artifact builders.

Risks: `DefaultSociContentStorePath` concatenates `config.DefaultSociSnapshotterRootPath + "content"` without `filepath.Join`; correctness depends on the default ending with a slash or intentionally forming that path. ORAS `Delete` is a no-op, so cleanup semantics differ by store type. Containerd `Push` uses the digest string as writer ref, which can conflict with stale incomplete writers. Size validation only triggers when expected size is positive. Lazy client creation hides containerd availability until first operation.

Test signals: `store_test.go` covers store-type canonicalization, path derivation, and GC label helper naming/value behavior through a fake memory store.
