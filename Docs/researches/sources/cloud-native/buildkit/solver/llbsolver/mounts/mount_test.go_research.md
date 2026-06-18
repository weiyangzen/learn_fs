# sources/cloud-native/buildkit/solver/llbsolver/mounts/mount_test.go

Purpose: validates cache mount reference lifecycle and concurrency behavior for `mount.go`. It builds a real containerd-backed `cache.Manager` with native snapshots, metadata DB, content store, leases, differ, applier, and mount pool.

Important APIs/types/functions: `cmOpt`, `cmOut`, `newCacheManager`, `newRefGetter`, `TestCacheMountPrivateRefs`, `TestCacheMountSharedRefs`, `TestCacheMountLockedRefs`, and `TestCacheMountSharedRefsDeadlock`. The helper constructs a full cache stack under `t.TempDir`, closes BoltDB/metadata/cache manager via cleanup, and returns a manager suitable for `cacheRefGetter`.

Control flow: tests create multiple independent `cacheRefGetter` instances and compare mutable ref IDs across cache sharing modes. Private mode shares only within one getter, shared mode shares across getters via `sharedCacheRefs`, and locked mode blocks a second getter until the first refs release. The deadlock test injects sleeps into clone/release hooks while concurrently releasing one ref and acquiring another.

State/persistence: temporary snapshot/content/metadata stores are persistent only for the test duration. Test references are real cache refs whose ID reuse after release verifies metadata index behavior and mutable ref unlock behavior.

Dependencies/integration: exercises native containerd snapshotter, BuildKit cache manager, metadata store, leases, Windows-aware differ/applier wrappers, and the package-global shared cache ref table.

Risks: tests mutate global hook vars and `sharedCacheRefs`; they use `defer` to restore hooks but parallel tests still rely on no overlapping hook mutation except the non-parallel deadlock test. Timing assertions use 500 ms and 2 s windows, so heavily loaded CI can affect lock tests.

Test signals: strong regression coverage for moby/buildkit#1322 deadlock, cache sharing contracts, locked cache blocking, and release-driven reuse. It does not cover secret/SSH/tmpfs mount materialization.
