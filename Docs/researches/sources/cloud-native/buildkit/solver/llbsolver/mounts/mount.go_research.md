# sources/cloud-native/buildkit/solver/llbsolver/mounts/mount.go

Purpose: implements `MountManager`, the llbsolver bridge from protobuf mount declarations to BuildKit cache, tmpfs, SSH, and secret mountables. It is central to `ExecOp` mount preparation and to `RUN --mount=type=cache|secret|ssh|tmpfs` behavior.

Important APIs/types/functions: `NewMountManager`, `MountableCache`, `MountableTmpFS`, `MountableSecret`, `MountableSSH`, `SearchCacheDir`, `CacheRefMetadata`, `cacheRefGetter`, `cacheRefs`, and `cacheRefShare`. `getRefCacheDir` decides cache sharing semantics. `secretMountInstance.Mount` materializes secret bytes into a temporary tmpfs-backed file with requested uid/gid/mode. `sshMountInstance.Mount` forwards a session SSH socket. `tmpfsMount.Mount` emits a tmpfs mount with readonly and size options.

Control flow: cache mounts build a key from cache ID plus optional parent ref ID, check per-manager active shares, then branch on `SHARED`, `PRIVATE`, or `LOCKED`. Shared mounts coordinate through global `sharedCacheRefs`; locked mounts poll while reusable refs are locked. New refs are created through `cache.Manager.New` and tagged with the `cache-dir` metadata index. Release of cloned cache refs decrements share membership and releases the underlying mutable ref only when the last clone is released.

State/persistence: cache mount state is both in-memory (`MountManager.cacheMounts`, global `sharedCacheRefs`) and persistent metadata (`cache-dir:<id>` index). Secret and SSH mount state is transient and cleaned by release callbacks. Global hijack vars are test hooks and are concurrency-sensitive.

Dependencies/integration: depends on cache manager identity mapping, session manager, secrets and sshforward session services, containerd mount primitives, metadata search, `locker`, and user namespace detection. `ExecOp` reaches this through `container.PrepareMounts`.

Risks: release ordering and lock hierarchy are high risk for deadlocks or leaked mutable refs. Secret mounts must preserve noexec/nodev/nosuid behavior and userns fallback. `SearchCacheDir` prefix matching must avoid partial-id false positives. Global shared cache refs make tests and long-lived workers sensitive to stale state.

Test signals: `mount_test.go` covers private/shared/locked cache ref reuse, blocking behavior, release reuse, and a historical shared-ref deadlock.
