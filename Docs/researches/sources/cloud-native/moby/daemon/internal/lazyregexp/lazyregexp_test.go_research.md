## sources/cloud-native/moby/daemon/internal/lazyregexp/lazyregexp_test.go

Purpose: Tests lazy regexp construction in test mode.

Important test: `TestCompileOnce` has an invalid regexp subtest expecting `New("[")` to panic, and a valid regexp subtest expecting `[a-z]` to match `"hello"`.

Control flow and state: Panic recovery validates eager compilation under test binary detection.

Dependencies and integration: Uses the package's `New` and `MatchString`.

Risks covered: Invalid patterns are caught during tests and valid patterns work after construction. It does not assert `sync.Once` directly or every wrapper method.

Persistence: None.
