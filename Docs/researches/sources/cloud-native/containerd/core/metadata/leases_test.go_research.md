# sources/cloud-native/containerd/core/metadata/leases_test.go

Purpose: verifies metadata lease lifecycle, filter behavior, and resource reference validation/listing/deletion.

Important APIs and helpers: `TestLeases`, `TestLeasesList`, and `TestLeaseResource` exercise `NewLeaseManager`, `Create`, `Delete`, `List`, `AddResource`, `DeleteResource`, and `ListResources`.

Control flow: `TestLeases` creates leases inside bbolt transactions, expects duplicate create to map to `ErrAlreadyExists`, lists created leases and timestamps, then deletes them and checks not-found behavior. `TestLeasesList` creates labeled leases and table-drives ID and label filters. `TestLeaseResource` creates one lease, attempts to add content, ingest, image, and snapshot resources plus invalid lease/container/snapshot type cases, then validates `ListResources` uniqueness and snapshot deletion.

State and persistence: tests use the real bbolt-backed lease manager, including transactional context via `boltutil.WithTransaction`. Resource expected values reflect normalized content digest IDs and nested snapshot type strings such as `snapshots/overlayfs`.

Dependencies and integration: uses `leases`, bbolt, `errdefs`, and metadata test environment helpers. It is a direct behavioral check for `leases.go`.

Risks: the create/delete test has lenient error handling around expected delete errors, so not all delete-error paths are equally strong. Resource list ordering is not assumed; the test uses a map.

Test signals: good coverage for lease CRUD, filters, supported resource encodings, duplicate add idempotency, and explicit rejection of unsupported resource families.
