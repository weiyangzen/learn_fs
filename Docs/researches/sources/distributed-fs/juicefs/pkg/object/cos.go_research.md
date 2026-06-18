# sources/distributed-fs/juicefs/pkg/object/cos.go


Purpose: implements Tencent Cloud COS storage behind `!nocos`, registering `cos`.

Important APIs and flow: `COS` wraps `cos.Client` plus tier configuration. It implements bucket creation, head/get/put/copy/delete/list, restore, and multipart operations. `Get` uses HTTP Range headers and verifies stored CRC32C metadata on full-object reads. `Put` stores CRC metadata for `io.ReadSeeker` inputs, applies storage class and encoded object tag from the active tier, and returns request/storage-class attrs. `List` decodes URL-encoded keys and merges common prefixes for delimiter listing.

State and persistence: objects, metadata, tags, restore state, and multipart uploads live in COS. Local persistent state is limited to the endpoint host and tier map.

Dependencies and integration: depends on Tencent COS SDK, shared checksum helpers, `ResponseAttrs`, `TierKey`, and `DefaultStorageClass`. `newCOS` can discover bucket endpoint from service listing, falls back to `COS_SECRETID` and `COS_SECRETKEY`, and supports disabling SDK CRC with `disable-checksum=true`.

Risks: automatic endpoint discovery needs list-bucket permissions. Some request IDs and storage classes are header-dependent. Checksum verification only applies to full reads with metadata. Copy source formatting depends on endpoint host. `ListAll` is not implemented.

Test signals: environment-gated `TestCOS` in `object_storage_test.go` runs the broad storage contract when COS credentials are available.
