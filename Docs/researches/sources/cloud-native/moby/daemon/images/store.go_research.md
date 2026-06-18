<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/store.go -->
# sources/cloud-native/moby/daemon/images/store.go

Purpose: adds content lease management around legacy image and content stores used during pulls and deletes.

Important APIs and control flow: `imageKey` names per-image leases. `imageStoreWithLease.Delete` deletes the matching lease before deleting the image. `imageStoreForPull.Put/Get` delegates image config storage and then calls `updateLease`. `updateLease` creates or reuses a lease named for the image config digest and adds every ingested content digest as a content resource. `contentStoreForPull` tracks committed digests from content writers, including already-existing content. `contentWriter.Commit` records digests on successful or already-existing commits.

State and persistence: mutates containerd leases and content store data, and delegates image config store mutations. It keeps an in-memory per-pull digest list protected by a mutex.

Dependencies and integration: used by `image_pull.go` and `NewImageService`. It integrates containerd leases/content, namespaces, distribution image config stores, and legacy image deletion.

Risks: lease naming is tied to image config digest, so config-digest identity must remain stable. `imageStoreWithLease.Delete` uses `context.TODO` with a stored namespace because the image store interface lacks context. Content writer `AlreadyExists` handling depends on descriptor options being present.

Test signals: `store_test.go` covers lease deletion and digest tracking for successful and already-existing content writes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/images/store.go -->
