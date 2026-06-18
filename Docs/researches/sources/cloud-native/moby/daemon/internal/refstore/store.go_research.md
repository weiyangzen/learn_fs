<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/refstore/store.go -->
# sources/cloud-native/moby/daemon/internal/refstore/store.go

Purpose: implements Docker's JSON-backed image reference store, mapping repository references to image digests and supporting reverse lookup by digest.

Important APIs and types: `Association`, `Store`, `refStore`, `repository`, sorting types, `NewReferenceStore`, `AddTag`, `AddDigest`, `favorDigest`, `addReference`, `Delete`, `Get`, `References`, `ReferencesByName`, `save`, and `reload`.

Control flow: `NewReferenceStore` resolves the JSON path, initializes maps, reloads existing JSON or creates a new file. Adds normalize tag-only refs, favor digest over tag+digest refs, reject ambiguous `sha256` repo tags, enforce digest immutability, optionally force tag overwrites, update reverse cache, and save atomically. Delete normalizes the ref, removes it from repository and reverse cache, prunes empty maps, and saves. Get gives digest precedence for tag+digest references. Reload decodes JSON and rebuilds reverse cache.

State and persistence: repositories persist as JSON at `jsonPath`, written by `atomicwriter.WriteFile` with mode 0600. In-memory state is guarded by RW mutex and includes `referencesByIDCache`.

Dependencies and integration: used by image management code to track tags/digests independent of containerd metadata. Depends on distribution/reference, OCI digest, and atomicwriter.

Risks: JSON corruption prevents store creation. Cache rebuild skips unparsable refs silently even though that should not happen. Save marshals the store struct, relying on exported `Repositories` and unexported fields being ignored. Force applies only to tags, never digests.

Test signals: `store_test.go` covers load/save exact JSON, add/delete/get, lexical sorting, force rules, digest immutability, not-found, invalid tags, and errdefs classification.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/refstore/store.go -->
