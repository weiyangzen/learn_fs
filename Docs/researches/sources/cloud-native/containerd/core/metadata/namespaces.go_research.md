# sources/cloud-native/containerd/core/metadata/namespaces.go

Purpose: implements a transaction-scoped `namespaces.Store` backed by metadata bbolt buckets, including namespace creation, label management, listing, and guarded deletion.

Important APIs and types: `namespaceStore`, `NewNamespaceStore`, `Create`, `Labels`, `SetLabel`, `List`, `Delete`, `listNs`, and `isBucketEmpty`.

Control flow: `Create` ensures the version bucket, validates namespace identifier and labels, creates the namespace bucket, then writes labels under the labels bucket. `Labels` returns an empty map when no label bucket exists. `SetLabel` validates the key/value and deletes the label when value is empty. `List` returns all subbuckets under the version bucket. `Delete` applies delete options, calls `listNs`, refuses non-empty namespaces with a failed-precondition error, and deletes the namespace bucket otherwise.

State and persistence: namespaces are top-level subbuckets under `bucketKeyVersion`. Labels are stored in a dedicated labels bucket. Deletion checks only major object families for emptiness: images, blobs, containers, and per-snapshotter snapshot buckets.

Dependencies and integration: depends on identifier and label validation packages, namespace API types, bbolt, and metadata bucket helpers. It is used within DB transaction paths that expose namespace management.

Risks: `Delete` assumes the version bucket exists before deleting; callers should only delete known namespaces. `listNs` intentionally returns object type summaries rather than exact objects, so error messages are diagnostic but not exhaustive. The delete emptiness check must be kept in sync with persisted object families that should block namespace deletion.

Test signals: `namespaces_test.go` covers empty deletion and deletion refusal when containers and snapshotter data exist.
