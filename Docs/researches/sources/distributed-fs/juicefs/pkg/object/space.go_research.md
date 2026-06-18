# sources/distributed-fs/juicefs/pkg/object/space.go

Purpose: implements DigitalOcean Spaces-style S3-compatible storage as a wrapper registered as `space`.

Important APIs and types: `space` embeds `s3client`, overrides `String`, delegates `Limits`, and overrides `InitTiers` to set empty tiers and return `notSupported` to avoid storage-class panics.

Control flow and state: `newSpace` defaults to HTTPS, parses bucket and region from host segments, removes the bucket from the base endpoint, builds AWS config with static credentials, unsigned payload middleware, path-style disabled, shared HTTP client, and one retry.

Persistence and integration: all storage operations come from embedded `s3client`; persisted data lives in the configured Space. Registration occurs in `init`.

Risks and test signals: endpoint parsing ignores parse errors (`uri, _`) and assumes host has expected segments, so malformed endpoints can panic or misconfigure. Tier support is deliberately disabled. No Spaces-specific tests are present.
