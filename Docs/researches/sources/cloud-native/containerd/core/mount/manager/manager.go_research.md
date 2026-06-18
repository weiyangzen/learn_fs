<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/manager.go -->
# sources/cloud-native/containerd/core/mount/manager/manager.go

Purpose: provides a BoltDB-backed implementation of `mount.Manager` plus `metadata.Collector`, coordinating custom mount handlers, built-in transformers, activation persistence, deactivation, and garbage collection cleanup.

Important APIs/types/functions: `BoltManager` combines `mount.Manager`, `metadata.Collector`, and `Sync`; `WithMountHandler` registers custom handlers by mount type; `WithAllowedRoot` opens additional `os.Root` instances for secure path-scoped transforms; `NewManager` creates target roots and `mountManager`. Key methods are `Activate`, `Deactivate`, `Info`, `List`, `StartCollection`, `ReferenceLabel`, collection context methods, `cleanupAll`, and `unmountAll`.

Control flow: `Activate` requires a namespace, serializes same-name activations with a keyed mutex, inspects mount types for chained transformers (`format/`, `mkfs/`, `mkdir/`), decides how many leading mounts must be handled by the manager, and returns `ErrNotImplemented` if nothing needs manager handling. It creates a Bolt bucket in `v1/<namespace>/mounts/<name>`, stores id/labels/timestamps/lease reference, cleans stale incomplete buckets, creates a numeric target directory, applies transforms and handlers/system mounts in order, and finally writes active/system activation state in a second transaction. On error it rolls back Bolt metadata and unmounts already mounted entries.

State and persistence: persists activation metadata in bbolt buckets keyed by namespace and activation name. Active mounts store type, mount point, and mount time; system mounts store type/source/target/options. Lease mappings under `leases/<lease>/<name>` protect activations from GC. Target directories are numeric mount IDs under the manager target root, with paired `<n>` and `<n>-type` files for cleanup ordering and handler lookup.

Dependencies and integration points: depends on `mount.Manager` interfaces from `core/mount/manager.go`, `mount.Mount` platform mounting, `errdefs`, `leases`, `namespaces`, `boltutil`, `kmutex`, and `metadata.CollectionContext`. Handlers can mount plugin-specific types outside the container namespace; returned `ActivationInfo.System` is later mounted by runtimes or tools.

Garbage collection behavior: `StartCollection` takes the manager write lock and opens a writable Bolt transaction. `All`, `ActiveWithBackRefs`, `Leased`, and `Remove` expose mount nodes and backrefs to metadata GC. `Finish` deletes removed buckets and lease refs, commits, computes target directories not referenced by remaining mount IDs, unlocks, and unmounts/removes those directories. `Cancel` rolls back and unlocks.

Risks: cleanup order relies on directory/type-file naming and `Readdirnames` order; `unmountAll` may join multiple errors and leave directories for a later GC run. `putActiveMount` does not persist active source/target/options. `Update` and `Sync` are not implemented. `WithAllowedRoot` and prefix matching in transforms rely on absolute root names and longest-prefix ambiguity is not explicitly resolved. Same-name locking prevents a stale-incomplete race, but only within the process.

Test signals: `manager_test.go` covers no-op/system-only `ErrNotImplemented`, custom handler activation, GC removal/backrefs/error retry, duplicate activate, stale incomplete cleanup, info/list-like persistence, system mount persistence, same-name concurrency, and close behavior. `manager_linux_test.go` root-tests loopback, overlay formatting, and temporary bind-return flows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/manager.go -->
