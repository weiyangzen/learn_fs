<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/store_test.go -->
# sources/cloud-native/moby/daemon/images/store_test.go

Purpose: unit tests for legacy image-store lease wrappers and pull content-store digest tracking.

Important APIs and control flow: `setupTestStores` creates temporary image, content, metadata, and lease stores under a namespace. `TestImageDelete` verifies image delete succeeds without a lease and removes an existing image lease. `TestContentStoreForPull` verifies a committed content writer records its digest and that attempting to write already-existing content also records the digest.

State and persistence: creates temporary filesystem stores and a Bolt metadata DB, then removes them in cleanup. It mutates real local content and lease metadata.

Dependencies and integration: uses containerd local content, metadata DB/lease manager, Moby image FS store, namespaces, bbolt, and `gotest.tools`.

Risks: the temporary directory is created with `os.MkdirTemp("", t.Name())`, so failures before cleanup can leave OS temp state. Tests check core lease behavior but not `imageStoreForPull.updateLease` resource addition end to end.

Test signals: direct coverage for the lease deletion contract and pull digest accounting.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/store_test.go -->
