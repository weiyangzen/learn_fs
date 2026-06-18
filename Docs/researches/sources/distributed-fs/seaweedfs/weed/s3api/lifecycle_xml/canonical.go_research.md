# Research: sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/canonical.go

## sources/distributed-fs/seaweedfs/weed/s3api/lifecycle_xml/canonical.go

Purpose: converts S3 bucket lifecycle XML wire structs into the lifecycle engine’s canonical `s3lifecycle.Rule` representation.

Important APIs: `Parse` decodes XML bytes into `Lifecycle`. `ParseCanonical` combines parsing and conversion. `LifecycleToCanonical` handles nil safely and converts each `Rule`. `ruleToCanonical` maps ID/status, flattened filters, expiration days/date/delete-marker, noncurrent version expiration, newer noncurrent versions, and abort-incomplete-MPU days. `flattenFilter` supports absent filters, `<Prefix>`, single `<Tag>`, `<And>` with prefix/multiple tags/object-size bounds, and filter-level size bounds.

State and dependencies: pure conversion; no persistence. Dependencies are `encoding/xml`, `bytes`, and `weed/s3api/s3lifecycle`. Integration points are bucket lifecycle configuration handlers and lifecycle worker/shell callers that need canonical rule execution without importing the full S3 API package. Risks: transition and noncurrent transition fields are parsed by types but not currently mapped into canonical output here; prefix fallback from legacy top-level `<Prefix>` occurs only when filter prefix is empty. Tests cover filter forms, multiple actions, dates, delete markers, disabled status, nil, and empty rules.
