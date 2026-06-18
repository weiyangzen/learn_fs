# sources/cloud-native/containerd/core/metadata/images.go

Purpose: implements the namespace-scoped `images.Store` on top of the metadata bbolt database, including image CRUD, filtering, validation, persistence encoding, lease linkage for expiring images, and create/update/delete event publication.

Important APIs and types: `imageStore`, `NewImageStore`, `Get`, `List`, `Create`, `Update`, and `Delete` implement the public image store contract. Internal helpers `validateImage`, `validateTarget`, `readImage`, `writeImage`, and `encodeInt` enforce image target requirements and serialize descriptor fields.

Control flow: every public method first requires a namespace from context. Reads use `view`; mutations use `update`. `Create` validates the image, creates the namespace images bucket, optionally records an image lease through `addImageLease`, creates an image bucket, stamps `CreatedAt` and `UpdatedAt`, writes labels/annotations/target, then publishes `/images/create`. `Update` reads the existing record, applies either full replacement or selected field paths (`labels`, `labels.KEY`, `annotations`, `annotations.KEY`, `target`), validates, preserves `CreatedAt`, refreshes `UpdatedAt`, writes the bucket, and publishes `/images/update`. `Delete` can check an expected target digest before bucket deletion and publishes `/images/delete`.

State and persistence: images live under the versioned namespace images bucket, one subbucket per image name. Timestamps, labels, and annotations are stored via `boltutil`; target descriptor fields are stored in a nested `target` bucket as digest, media type, and varint size. The store increments the DB dirty counter on delete so GC can be triggered.

Dependencies and integration: depends on `images.Store`, OCI descriptors, `filters`, `labels`, namespace context, bbolt errors, `epoch.FromContext` for deterministic timestamps, and metadata lease helpers. It integrates with the DB publisher for image lifecycle events and with GC through labels and lease references.

Risks: `Update` only supports full target replacement, not partial target fields. `addImageLease` only adds expiring images to an active lease; an update removing expiration does not explicitly remove old lease entries. `readImage` ignores varint decoding errors for size, so corrupt size bytes can silently decode to zero and be caught only if later validation occurs.

Test signals: covered by `images_test.go` for create/list/filter/update/delete, timestamp behavior, target validation, fieldpath behavior, and digest-guarded delete failures.
