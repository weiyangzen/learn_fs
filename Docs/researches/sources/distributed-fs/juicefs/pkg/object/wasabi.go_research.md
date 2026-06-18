# sources/distributed-fs/juicefs/pkg/object/wasabi.go

Purpose: implements Wasabi object storage as an S3-compatible wrapper registered as `wasabi`.

Important APIs and types: `wasabi` embeds `s3client`, overrides `String`, and disables tier storage by setting empty tiers in `InitTiers` and returning `notSupported`.

Control flow and state: `newWasabi` defaults to HTTPS, parses bucket and region from host segments, strips the bucket from the base endpoint, builds a static-credential AWS S3 client with unsigned payload middleware, virtual-host addressing, shared HTTP client, and one retry attempt.

Persistence and integration: object behavior is inherited from `s3client`; persistent data lives in a Wasabi bucket.

Risks and test signals: endpoint parsing assumes Wasabi host layout and can misparse nonstandard endpoints. Tier support is deliberately disabled to avoid unsupported storage-class behavior. No Wasabi-specific tests are present.
