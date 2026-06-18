## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/NoopBlockWorker.java

**Purpose:** Test double implementing `BlockWorker` with no operational behavior. It is useful where a component needs a worker interface but the test does not care about block storage side effects.

**Important APIs:** Implements worker methods for block lifecycle, cache/load, metadata/reporting, metrics/configuration, service registration, worker identity/address, dependencies, start/stop/close, and session cleanup.

**Control flow:** Most mutating methods are no-ops. Many accessors return `null`, empty collections, or completed futures, so callers must only use methods relevant to their test path.

**State and persistence:** It stores no state and performs no persistence. It does not track blocks, sessions, metrics, or worker identity.

**Dependencies and integration:** Depends on the full `BlockWorker` interface and gRPC/wire types, but intentionally avoids `TieredBlockStore`, UFS, and master clients.

**Risks:** Because many accessors return `null`, this double can hide missing setup until a code path dereferences a value. It is safest for tests that only need an object identity or no-op side-effect sink.

**Test signals:** Not a test itself; its value is enabling isolated tests of collaborators without spinning a real block worker.
