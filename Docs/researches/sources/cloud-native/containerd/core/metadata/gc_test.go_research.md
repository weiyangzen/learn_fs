# sources/cloud-native/containerd/core/metadata/gc_test.go

Purpose: validates the metadata garbage-collection graph by constructing synthetic bbolt layouts for content, images, containers, snapshots, ingests, leases, and sandboxes. It is a white-box test of root discovery, reference discovery, removal behavior, and custom collector integration.

Important APIs and helpers: `TestResourceMax`, `TestGCRoots`, `TestGCRemove`, `TestGCRefs`, and `TestCollectibleResources` call internal GC context methods such as `scanRoots`, `scanAll`, `references`, and `remove`. The `testCollector` implements the package collector interfaces with `All`, `Active`, `ActiveWithBackRefs`, `Leased`, and `Remove`. Helper `alterFunc` builders (`addImage`, `addSnapshot`, `addContent`, `addIngest`, `addLease*`, `addContainer`, `addSandbox`) create exact bucket structures under `bucketKeyVersion`.

Control flow: each test opens a temporary bbolt database, applies a list of bucket mutations in one update transaction, then scans through the metadata GC implementation and compares sorted `gc.Node` lists. `TestGCRefs` first primes roots and then checks the reference set for many node types, including label references, back references, flat references, conditional snapshot references, and expired/non-expired resources.

State and persistence: the tests intentionally bypass public stores and write bbolt buckets directly, making them sensitive to schema names and label contracts. They cover namespace separation and resource key encoding such as `snapshotter/name` for snapshots and digest strings for content.

Dependencies and integration: depends on `github.com/containerd/containerd/v2/pkg/gc`, `boltutil`, `go-digest`, and `logtest`. It integrates with the metadata package's internal bucket helpers and GC label constants, so failures often indicate schema or label-semantic regressions.

Risks: because the tests mirror internal bbolt layout, any schema migration must update these helpers. Time-sensitive expiration checks use `time.Now()` and can be fragile if expiration boundary handling changes. The comparison helper sorts nodes but preserves duplicate references, so duplicate reference behavior is explicitly part of the signal.

Test signals: strong coverage for GC graph correctness, resource deletion, root expiration, custom resource collectors, back-reference hooks, and malformed reference labels. It does not exercise live DB compaction or concurrent GC execution.
