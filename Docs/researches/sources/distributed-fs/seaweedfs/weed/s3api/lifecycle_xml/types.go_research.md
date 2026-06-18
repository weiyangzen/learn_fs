# Research: sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/types.go

## sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/types.go

Purpose: defines the XML wire model for S3 `BucketLifecycleConfiguration` without importing the full `weed/s3api` package graph.

Important types/APIs: `Lifecycle`, `Rule`, `Filter`, `Prefix`, `And`, `Expiration`, `ExpireDeleteMarker`, `ExpirationDate`, `Transition`, `NoncurrentVersionExpiration`, `NoncurrentVersionTransition`, and `AbortIncompleteMultipartUpload`. Custom marshal/unmarshal methods track presence via private `set`, `andSet`, and `tagSet` flags, so absent elements differ from present-empty elements. Constructors/accessors include `NewPrefix`, `NewExpirationDays`, `Prefix.Set/Val`, `Filter.Set/AndSet/TagSet`, and `Set` methods for optional actions.

State and persistence: structs represent XML request/response state, not durable storage by themselves. Dependencies are `encoding/xml` and `time`. Integration points are lifecycle config handlers, canonical conversion, and external callers such as shell/lifecycle worker. Risks: private set flags are crucial; constructing structs manually without constructors may omit XML on marshal. `Filter.MarshalXML` chooses And, Tag, or Prefix branch and then writes size bounds; unsupported/unknown XML children are skipped on unmarshal. Tests cover round-trip and canonical behavior for major forms.
