# sources/cloud-native/buildkit/cache/remotecache/gha/ghatypes/config.go

## Purpose

This file defines the daemon-side configuration structure for signed and verified GitHub Actions cache indexes.

## Important APIs, Types, and Functions

- `CacheConfig` groups optional signing and verification settings.
- `SignConfig` carries the external signing command argv.
- `VerifyConfig` carries a `Required` flag and `VerifyPolicy`.
- `VerifyPolicy` defines timestamp and transparency-log thresholds and embeds Sigstore Fulcio `certificate.Summary` fields for signer certificate matching.

## Control Flow and State

There is no executable control flow. The structures are populated from TOML configuration and consumed by `gha.go`. When `Sign` is non-nil and has a command, the exporter signs serialized cache index bytes. When `Verify.Required` is true, the importer requires a matching signature bundle before accepting the index. Policy fields are compared by converting certificate summaries to a string map and applying simple wildcard matching in the GHA backend.

## Dependencies and Integration Points

The sole dependency is Sigstore's `certificate.Summary`, which provides normalized signer identity fields. The type is imported by `cache/remotecache/gha` through `*ghatypes.CacheConfig`.

## Risks and Edge Cases

Policy behavior depends on JSON field names emitted for `certificate.Summary`; adding or renaming fields upstream can affect matching. Empty certificate policy values are ignored, so partially specified policy is permissive for unspecified fields. An empty signing command with non-nil `Sign` results in no signing work.

## Test Signals

No tests in this subset instantiate these structs directly. Their behavior is indirectly constrained by the signature verification path in `gha.go`, but signed cache integration tests are not present here.
