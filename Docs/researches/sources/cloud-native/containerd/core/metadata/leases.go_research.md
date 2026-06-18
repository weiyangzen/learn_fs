# sources/cloud-native/containerd/core/metadata/leases.go

Purpose: implements a metadata-backed `leases.Manager` and the internal helpers used by content, ingest, image, and snapshot code to attach or remove resources from the current lease in context.

Important APIs and types: `leaseManager`, `NewLeaseManager`, `Create`, `Delete`, `List`, `AddResource`, `DeleteResource`, and `ListResources` implement the public lease contract. Internal helpers include `addSnapshotLease`, `removeSnapshotLease`, `addContentLease`, `removeContentLease`, `addIngestLease`, `removeIngestLease`, `addImageLease`, `removeImageLease`, and `parseLeaseResource`.

Control flow: public methods require a namespace. `Create` applies lease options, requires an ID, creates the namespace lease bucket, writes `createdat`, optional labels, and returns the created lease. `Delete` removes the lease bucket and increments DB dirty state. `List` parses filters, iterates lease subbuckets, reads timestamps and labels, and matches `adaptLease`. Resource add/delete methods validate the lease exists, parse resource type into nested bucket keys, and write or delete a nil value at the resource ID. `ListResources` walks content, images, ingests, and nested snapshotter buckets to rebuild `leases.Resource` values.

State and persistence: leases live under `v1/<namespace>/leases/<lease-id>`. Resource references are nested by type, with snapshots stored as `snapshots/<snapshotter>/<snapshot-key>`. Content resource IDs are normalized through digest parsing. Image lease helpers only attach images with `containerd.io/gc.expire` labels, matching expiring image GC semantics.

Dependencies and integration: depends on `leases`, `boltutil`, `filters`, `namespaces`, `errdefs`, bbolt, and `go-digest`. It is called by image, content, ingest, and snapshot metadata paths when `leases.WithLease` has been placed in context.

Risks: invalid or unsupported resource types produce `ErrInvalidArgument` or `ErrNotImplemented`; callers must preserve these distinctions. Helper functions panic if the namespace has not already been required in code paths where that invariant is assumed. Delete helpers silently succeed when the resource-type bucket does not exist, making cleanup idempotent but possibly masking missing lease references.

Test signals: `leases_test.go` covers create/delete/list filtering, duplicate IDs, supported and unsupported resource types, digest validation, snapshot type encoding, resource listing, and deletion.
