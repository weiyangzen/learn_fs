# sources/cloud-native/containerd/core/metadata/images_test.go

Purpose: tests the bbolt-backed image store behavior for listing, filters, validation, fieldpath updates, timestamp semantics, and target-checked deletion.

Important APIs and helpers: `TestImagesList`, `TestImagesCreateUpdateDelete`, `imageBase`, `checkImageTimestamps`, and `checkImagesEqual`. The test operates through `NewImageStore(NewDB(...))`, not raw buckets.

Control flow: `TestImagesList` creates four images with labels and target annotations, then runs filter cases for full set, label disjunction, specific labels, name, combined filters, and target media type pattern. It deletes every image and expects a second delete to return not found. `TestImagesCreateUpdateDelete` table-drives create and update cases, including label replacement, single-label mutation, annotation mutation, full target replacement, invalid targets, update of a non-existent name, and digest-checked delete.

State and persistence: verifies timestamps are set on create, equal on create, and `UpdatedAt` advances on update while `CreatedAt` is preserved. Tests compare complete `images.Image` structs after get/list/update, so persisted labels, annotations, target size/media type/digest, and timestamps all matter.

Dependencies and integration: uses containerd `images` package, filter parser, `errdefs`, OCI descriptors, `go-digest`, and the local test DB environment. It validates behavior exposed by `images.go`.

Risks: tests rely on wall-clock timestamp ordering and assume update time is after create time. Table names become image names, so duplicate test names could collide if subtests were run in the same store with reused names.

Test signals: strong signal for store-level behavior and fieldpath semantics. It does not inspect event publication or lease side effects for expiring images.
