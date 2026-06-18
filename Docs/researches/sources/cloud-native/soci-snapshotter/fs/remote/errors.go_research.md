# sources/cloud-native/soci-snapshotter/fs/remote/errors.go

Purpose: centralizes sentinel errors for remote blob resolution, HTTP status/header parsing, redirect, fetcher creation, and registry request failures.

Important APIs and flow: exported errors include unexpected status, failed layer-size retrieval, invalid host, failed redirect, unable to create fetcher, no regions, parse failures for content length/range/type, failed URL refresh, and request failure. Callers wrap these with `%w` so higher layers can classify failures with `errors.Is`.

State and persistence: no state or side effects.

Dependencies and integration: used by `remote/resolver.go` and exposed through `Blob.Check`, `Resolver.Resolve`, and filesystem check/mount paths.

Risks and test signals: useful for error classification, but the file itself has no tests. Consistency depends on all call sites wrapping rather than formatting without `%w`.
