<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/transport/pool_test.go -->
## sources/cloud-native/nydus-snapshotter/pkg/utils/transport/pool_test.go

Purpose: tests transport pool resolution, cache hit behavior, and cache invalidation after a redirect failure.

Important components: `FakeReference` implements `name.Reference` for a local httptest repository. `TestResolve` starts a local HTTP server, creates a pool, resolves a fake digest three times, and asserts call counts and transport/url reuse.

Control flow and state: first resolve performs auth setup plus redirect. Second resolve uses cached transport and only redirects. Third resolve forces the server to fail once; the pool removes the cached entry, re-authenticates/retries, and returns the same effective transport/url.

Dependencies/integration: uses httptest, go-containerregistry `name`, and testify require. It exercises real HTTP behavior without an external registry.

Risks and test signals: digest is an arbitrary string and the server does not verify path/method/range headers, so URL construction is only partially covered. Concurrency and timeout behavior are untested.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus-snapshotter/pkg/utils/transport/pool_test.go -->
