# subset-b-000059 Research

Grouped research for containerd mount manager, mount platform helpers, mount proxy, Docker auth/config/conversion/error handling. Each section preserves the source path for reconciliation into per-file research reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/format.go -->
# sources/cloud-native/containerd/core/mount/manager/format.go

Purpose: implements the `format` mount transformer used by the mount manager to rewrite mount source, target, and option strings from templates that refer to previously activated mounts.

Important APIs/types/functions: `mountFormatter.Transform` implements `mount.Transformer`; `formatString` returns a closure only when the string contains `{{`; template funcs are `source`, `target`, `mount`, and `overlay`. `overlay(start,end)` expands active mount points in forward or reverse order joined by `:`, matching overlayfs lowerdir syntax.

Control flow: `Transform` checks `Source`, `Target`, and each option independently. It avoids allocating a replacement options slice until the first option actually changes, then copies and patches by index. `formatString` parses a Go `text/template` at execution time and bounds-checks indexes/ranges against the active mount slice.

State and persistence: no persistent state. The transform returns a modified copy of the input `mount.Mount`; only the options slice may be copied when needed.

Dependencies and integration points: used by `manager.go` in the built-in transform chain for mount types like `format/overlay`; consumes `mount.ActiveMount` values produced by earlier manager-mounted entries.

Risks: template parsing on each transform is heavier than a purpose-built formatter; error messages expose index/range details and stop activation; all template functions trust active mount order. Unescaped template syntax in otherwise literal options will be interpreted.

Test signals: `format_test.go` covers no-op formatting, source/target substitution, overlay expansion, reverse ranges, single-range expansion, and options-copy behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/format.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/format_test.go -->
# sources/cloud-native/containerd/core/mount/manager/format_test.go

Purpose: unit-tests the `mountFormatter` transformer against synthetic active mounts.

Important APIs/types/functions: `TestFormatMount` constructs five `mount.ActiveMount` entries with predictable `Source`, `Target`, and `MountPoint` values, then table-tests `mountFormatter{}.Transform`.

Control flow: each case runs the transformer and compares the whole returned `mount.Mount` with the expected struct using `assert.Equal`.

State and persistence: no external state; all test data is in-memory.

Dependencies and integration points: validates the transformer contract expected by `manager.go`, especially that later overlay mounts can reference earlier manager-activated mount points.

Risks covered: verifies no formatting leaves mounts unchanged, overlay ranges preserve intended ordering, reverse overlay ranges work, and source/target references use the correct active mount fields.

Test signals: positive-only coverage. It does not cover malformed templates, out-of-range indexes, or invalid overlay ranges, so error-path confidence comes from implementation inspection rather than tests here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/format_test.go -->

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

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/manager_linux_test.go -->
# sources/cloud-native/containerd/core/mount/manager/manager_linux_test.go

Purpose: Linux root integration tests for mount manager activation paths that perform real loopback, ext4, overlay, and temporary mounts.

Important APIs/types/functions: `TestLoopbackMount`, `TestLoopbackOverlay`, `TestTemporaryMountActivation`, `TestTemporaryOverlayMountActivation`, and helper `initalizeBlockDevice`.

Control flow: tests create temporary ext4 images with `mkfs.ext4`, mount and populate them via `fstest`, activate manager mount arrays, mount returned `ActivationInfo.System` mounts into a target, and compare resulting filesystem contents. Temporary activation tests assert the returned system mount is a bind mount sourcing the manager-created mounted tree.

State and persistence: uses temporary bbolt DBs, temporary target directories, real loop devices or loop mount options, and real mount namespaces; cleanup uses `Deactivate` and test unmount helpers.

Dependencies and integration points: requires root and Linux mount support; depends on external `mkfs.ext4`; exercises `LoopbackHandler`, `format` transformer, ordinary `mount.All`, and `WithTemporary`.

Risks covered: verifies transformed overlay lowerdir expressions point to mounted backing layers, separate loop handler and direct loop option flows both work, and temporary activations return a usable bind mount for `ctr images mount` style consumers.

Test signals: high-value integration coverage but environment-sensitive. It skips only by requiring root; failures can reflect kernel/filesystem/tooling availability rather than pure code regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/manager_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/manager_test.go -->
# sources/cloud-native/containerd/core/mount/manager/manager_test.go

Purpose: unit and local integration tests for the Bolt-backed mount manager using fake handlers and temporary Bolt databases.

Important APIs/types/functions: `TestManager`, `noopHandler`, `errOnceHandler`, `TestGC`, `checkGCActive`, `TestActivateAlreadyExists`, `TestActivateStaleIncomplete`, `TestInfo`, `TestInfoSystemMounts`, `TestActivateConcurrentSameName`, and `TestClose`.

Control flow: tests activate mounts with no handlers, fake handlers, labels, and mixed handled/system types; inspect returned and persisted activation info; drive metadata collection manually; and assert deactivation/cleanup behavior. The stale test writes a partial Bolt bucket directly and ensures a later activation replaces it and removes its target directory.

State and persistence: validates bbolt bucket lifecycle, lease/backref effects, target directory cleanup, active/system mount serialization, and manager close closing root handles plus the Bolt DB.

Dependencies and integration points: uses `metadata.CollectionContext`, `gc.Node`, `namespaces`, `errdefs`, and bbolt. Fake handlers emulate plugin-managed mounts without performing real kernel mounts except in the root-required base `TestManager`.

Risks covered: duplicate activation returns `ErrAlreadyExists`; same-name concurrent activations are serialized; GC tolerates an unmount error then succeeds later; stale incomplete records are not mistaken for valid activations.

Test signals: broad behavioral coverage for manager state transitions. Open TODOs note missing direct tests for `Deactivate`, `Sync`, and some collection methods; `Sync`/`Update` are currently not implemented.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/mkdir.go -->
# sources/cloud-native/containerd/core/mount/manager/mkdir.go

Purpose: built-in mount transformer that consumes `X-containerd.mkdir.path=...` options and creates directories under configured allowed roots before a mount is performed.

Important APIs/types/functions: `mkdir` holds `rootMap map[string]*os.Root`; `(*mkdir).Transform` implements `mount.Transformer`. Options follow `X-containerd.mkdir.path=value[:mode[:uid:gid]]`; default mode is `0700`, default ownership is the current process uid/gid.

Control flow: transform scans options, parses mkdir-specific options, selects an `os.Root` whose path prefixes the requested directory, converts to a root-relative subpath, stats the path, creates it when absent, and strips consumed mkdir options from the mount. Non-mkdir options are preserved.

State and persistence: persists only the created directory in the filesystem. The returned mount has internal options removed so kernel mount parsing will not see them.

Dependencies and integration points: used by `manager.go` for `mkdir/<type>` transform prefixes. It relies on `os.Root` path-scoped filesystem operations and `errdefs` for invalid argument/not implemented classification.

Risks: only one directory level is created because `os.Root.MkdirAll` is not yet used; chmod/chown are explicitly not implemented; root selection uses map iteration and simple prefix matching, which can be ambiguous for overlapping roots and string-prefix false positives. Mode parsing rejects non-permission bits.

Test signals: `mkdir_linux_test.go` verifies successful creation with explicit mode and current uid/gid, option stripping indirectly, and likely error classification for unsupported ownership/mode cases on Linux.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/mkdir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/mkdir_linux_test.go -->
# sources/cloud-native/containerd/core/mount/manager/mkdir_linux_test.go

Purpose: Linux test coverage for the mkdir transformer.

Important APIs/types/functions: `TestMkdirHandler` creates a temp allowed root, opens it with `os.OpenRoot`, constructs a `mkdir` transformer, and passes a mount carrying `X-containerd.mkdir.path=<dir>:<mode>:<uid>:<gid>`.

Control flow: the test invokes `Transform`, then stats the requested directory and checks that it exists with the requested permissions. It uses current uid/gid so the unimplemented chown path is not triggered.

State and persistence: writes a real directory under a temporary root and verifies filesystem mode.

Dependencies and integration points: validates `os.Root`-relative creation expected when `manager.go` runs `mkdir/...` transforms before the actual mount.

Risks covered: confirms the happy path for explicit mode parsing and allowed-root lookup. It does not cover nested paths, overlapping roots, unsupported chown/chmod, invalid option syntax, or path traversal attempts.

Test signals: local filesystem test, not a real mount test. It gives confidence that internal options can prepare overlay directories without passing through to `mount_linux.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/mkdir_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/mkfs.go -->
# sources/cloud-native/containerd/core/mount/manager/mkfs.go

Purpose: built-in mount transformer that creates and formats a writable filesystem image file before subsequent mounts use it.

Important APIs/types/functions: `mkfs` holds allowed `os.Root` instances; `(*mkfs).Transform` consumes `X-containerd.mkfs.size`, `.fs`, and `.uuid` options; `createWritableImage` runs the selected mkfs binary. Supported filesystems are `ext2`, `ext3`, `ext4`, and `xfs`; default is `ext4`.

Control flow: transform chooses an allowed root by source prefix, strips mkfs options, parses size with `go-units.RAMInBytes`, validates filesystem type, creates/truncates the image file when absent, appends uuid-specific arguments, and runs `mkfs.<fs>`. If the file already exists it currently only leaves a TODO for magic checking and returns the mount unchanged except for consumed options.

State and persistence: creates a file under an allowed root, truncates it to the requested size, and formats it using external system tools. The returned mount no longer contains internal mkfs options.

Dependencies and integration points: called from `manager.go` for `mkfs/<type>` transform prefixes; used before loopback or other mounts that need an initialized image. Depends on `os.Root`, external `mkfs.ext*`/`mkfs.xfs`, `errdefs`, and logging.

Risks: external binaries are resolved from PATH at transform time; existing files are not validated for filesystem type/uuid/size; prefix root matching can be ambiguous; xfs/ext format behavior depends on installed tools and permissions. A missing `mkfs.size` fails activation.

Test signals: root integration tests indirectly exercise formatted ext4 image flows through loopback setup, but this file lacks direct unit tests for option parsing, unsupported fs, existing file handling, and external command failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/mkfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/transformer.go -->
# sources/cloud-native/containerd/core/mount/manager/transformer.go

Purpose: defines shared transformer type-prefix handling for mount manager internal transforms.

Important APIs/types/functions: constants `prefixMkdir = "X-containerd.mkdir."` and `prefixMkfs = "X-containerd.mkfs."`; `typeTransformer` embeds `mount.Transformer` and stores the final `mountType`.

Control flow: `typeTransformer.Transform` delegates to the embedded transformer and then overwrites the returned mount's `Type` with the stripped type selected by `manager.go` while parsing chains such as `format/mkdir/overlay`.

State and persistence: no state beyond wrapper fields; only mutates the returned mount value.

Dependencies and integration points: used by `manager.go` to compose built-in transforms while preserving the eventual concrete mount type for handler lookup or system mounting.

Risks: transform ordering is determined by slash-prefix order in the mount type; an unknown transform breaks the chain and logs a warning in the manager. The wrapper assumes the embedded transformer should not control final type.

Test signals: covered indirectly by manager and format/mkdir tests that use transformed mount types and expect final system mounts to be concrete types.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/manager/transformer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount.go -->
# sources/cloud-native/containerd/core/mount/mount.go

Purpose: defines the core `Mount` data structure and platform-neutral helpers for mounting arrays, unmounting arrays, canonical paths, read-only conversion, and protobuf conversion.

Important APIs/types/functions: `Mount`, `HasBindMounts`, `All`, `UnmountMounts`, `CanonicalizePath`, `(*Mount).ReadOnly`, `(*Mount).Mount`, `readonlyMounts`, `readonlyOverlay`, `isSkippedReadonlyOption`, `ToProto`, and `FromProto`.

Control flow: `All` mounts entries in order. `UnmountMounts` unmounts in reverse order using `fs.RootPath` for subtargets and returns the last mount error only when the top-level unmount fails. `Mount` resolves target under a root with `fs.RootPath` and delegates to platform-specific `m.mount`. Read-only conversion strips `rw`/duplicate `ro` for normal mounts and rewrites overlay mounts by removing `workdir`, `upperdir`, uid/gid idmap options, and prepending the old upperdir to lowerdir.

State and persistence: no persistent state. Helpers modify slices in place for read-only conversion, while proto conversion allocates new slices.

Dependencies and integration points: `Mount` is the common mount descriptor across snapshots, runtimes, mount manager, RPC proxy, and API protobufs. Uses continuity `fs.RootPath` to avoid unsafe target joins.

Risks: `readonlyMounts` mutates the input slice and nested options slices, so callers must copy if they need originals. `readonlyOverlay` only updates an existing `lowerdir=` option if one exists. `FromProto` assumes non-nil protobuf mount entries.

Test signals: `mount_test.go` validates overlay read-only rewriting, normal mount `ro` normalization, and volatile option copy behavior in adjacent temp helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_darwin.go -->
# sources/cloud-native/containerd/core/mount/mount_darwin.go

Purpose: Darwin-specific stub for mounting.

Important APIs/types/functions: platform `(*Mount).mount` returns `errdefs.ErrNotImplemented`.

Control flow: every call to `Mount.Mount` eventually fails with not implemented on Darwin.

State and persistence: no state and no filesystem changes.

Dependencies and integration points: selected by build constraints for Darwin. `HasBindMounts` in `mount.go` is also false for Darwin, allowing higher layers to skip bind-dependent paths.

Risks: callers must branch or tolerate `ErrNotImplemented`. Any code path assuming Unix-like `mount(2)` support will fail at runtime on Darwin.

Test signals: no direct Darwin test in this subset; behavior is simple stub logic.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_freebsd.go -->
# sources/cloud-native/containerd/core/mount/mount_freebsd.go

Purpose: FreeBSD platform mount implementation using the system `mount(8)` command because Go syscall packages do not expose a FreeBSD `Mount` wrapper.

Important APIs/types/functions: platform `(*Mount).mount` builds `mount -o <opt> -t <type> <source> <target>` arguments; it uses `Lookup` and `unmount` for ECHILD retry cleanup.

Control flow: captures mount info before invoking `mount`; retries up to ten times on `unix.ECHILD`; when mount ID changes after an ECHILD, unmounts the new mount before retrying. Non-ECHILD failures include command output in the returned error.

State and persistence: creates a real FreeBSD mount at the target when successful; may perform cleanup unmounts during uncertain helper failures.

Dependencies and integration points: selected on FreeBSD; integrates with the same public `Mount.Mount` API as Linux. Depends on external `/sbin/mount` resolution through PATH and mountinfo lookup.

Risks: command-line escaping depends on `exec.Command` argument boundaries but option semantics are delegated to FreeBSD `mount(8)`. ECHILD retry logic may still leave ambiguous partial state if lookup/unmount fails.

Test signals: no FreeBSD-specific tests in this subset; Linux tests exercise analogous helper retry ideas for FUSE.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_idmapped_linux.go -->
# sources/cloud-native/containerd/core/mount/mount_idmapped_linux.go

Purpose: Linux idmapped mount primitives and id mapping parsers.

Important APIs/types/functions: `parseIDMapping`, `parseIDMappingList`, `IDMapMount`, `IDMapMountWithAttrs`, and `GetUsernsFD`.

Control flow: mapping strings must be `container-id:host-id:size`, optionally comma-separated. `IDMapMountWithAttrs` clones a mount tree with `open_tree`, applies `MOUNT_ATTR_IDMAP` plus requested set/clear attributes via `mount_setattr`, and attaches it to the target with `move_mount`. `GetUsernsFD` parses uid/gid maps and delegates to the utility helper.

State and persistence: produces a mounted tree at the target and returns an open user namespace FD from helper code. No repository-level persistence.

Dependencies and integration points: used by `mount_linux.go` for `uidmap=`/`gidmap=` mount options and overlay lowerdir remapping. Requires Linux kernel idmapped mount support and valid user namespace mappings.

Risks: accepts zero size because it only rejects negative values; mapping semantics are kernel-enforced later. Syscalls require kernel and filesystem support; partial failures close tree fds but may still depend on callers for target cleanup.

Test signals: `mount_idmapped_linux_test.go` covers valid/invalid mapping strings, writable/read-only idmapped mounts, and uid/gid remapping effects under root and kernel >= 5.12.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_idmapped_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_idmapped_linux_test.go -->
# sources/cloud-native/containerd/core/mount/mount_idmapped_linux_test.go

Purpose: root/kernel-gated tests and benchmarks for Linux idmapped mount support.

Important APIs/types/functions: benchmarks for concurrent `getUsernsFD`; `TestIdmappedMount` with subtests `GetUsernsFD`, `IDMapMount`, and `IDMapMountWithAttrs`; helper `initIDMappedChecker`.

Control flow: tests skip unless root and kernel >= 5.12. They create files owned by container IDs, mount through an idmapped user namespace, then verify host-side uid/gid values at the destination. Read-only attribute tests assert writes fail with `EROFS`.

State and persistence: creates real user namespaces, idmapped mount trees, temp files, and mount targets; cleanup unmounts with `UnmountAll`.

Dependencies and integration points: validates the lower-level functions used by `mount_linux.go` when `uidmap`/`gidmap` options are present.

Risks covered: invalid negative mapping components fail; concurrent namespace FD creation is benchmarked; read-only mount attributes are enforced. Tests are environment-sensitive and skip on unsupported kernels/filesystems.

Test signals: strong integration coverage for kernel idmap behavior; does not explicitly test zero-size mapping or partial syscall failure cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_idmapped_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_idmapped_utils_linux.go -->
# sources/cloud-native/containerd/core/mount/mount_idmapped_utils_linux.go

Purpose: creates a pinnable user namespace file descriptor for idmapped mounts.

Important APIs/types/functions: `getUsernsFD` starts `/proc/self/exe` in a new user namespace with provided uid/gid maps and pidfd support; `pidfdWaitid` waits on a pidfd while ignoring EINTR.

Control flow: checks pidfd support, starts a traced reexec-like child with `CLONE_NEWUSER`, `Pdeathsig`, and `PidFD`; opens `/proc/<pid>/ns/user`; verifies the child is still alive with `PidfdSendSignal(0)`; returns the user namespace file while deferring child kill/wait and pidfd close.

State and persistence: returns an `*os.File` holding a kernel reference to the user namespace after the helper process has been killed and reaped.

Dependencies and integration points: used by `GetUsernsFD` in `mount_idmapped_linux.go`; depends on `pkg/sys.SupportsPidFD`, Linux pidfd syscalls, and user namespace clone privileges.

Risks: environment and security policy can block user namespace creation; if the child dies before namespace FD open/validation, the function fails. The helper path uses `/proc/self/exe`, so runtime execution context matters.

Test signals: idmapped tests and benchmarks exercise this helper under concurrent use and real kernel behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_idmapped_utils_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_linux.go -->
# sources/cloud-native/containerd/core/mount/mount_linux.go

Purpose: Linux `Mount` implementation, including option parsing, loop setup, overlay lowerdir compaction, FUSE helpers, bind remount handling, and idmapped mount support.

Important APIs/types/functions: `mountOpt`, `prepareIDMappedOverlay`, `(*Mount).mount`, `getUnprivilegedMountFlags`, `doPrepareIDMappedOverlay`, `getCommonDirectory`, `buildIDMappedPaths`, `parseMountOptions`, `hasDirectIO`, `compactLowerdirOption`, `findOverlayLowerdirs`, `longestCommonPrefix`, `copyOptions`, `optionsSize`, `mountAt`, and `mountWithHelper`.

Control flow: `mount` dispatches `fuse.`/`fuse3.` types to helper binaries; parses fstab-style options into flags/data/loop/idmap; obtains a user namespace fd when both uidmap and gidmap are present; remaps overlay lowerdirs through temporary read-only idmapped mounts; compacts large overlay lowerdir options by chdiring into the common directory; sets up loop devices when `loop` is present; invokes `unix.Mount`; applies propagation flags separately; remounts read-only bind mounts while preserving locked unprivileged flags; and idmaps non-overlay targets after mount.

State and persistence: creates real mounts, temporary idmapped lowerdir mounts under `tempMountLocation`, loop devices with autoclear, and possible helper-managed FUSE mounts. Cleanup functions are deferred in the mount path for temporary idmapped overlay mounts.

Dependencies and integration points: central implementation used by `Mount.Mount`, manager system mounts, temp mounts, snapshotters, and runtime handoff. Depends on `unix`, `userns`, loop setup helpers, mountinfo lookup, and optional helper binaries `mount.fuse`/`mount.fuse3`.

Risks: Linux mount option strings are page-size limited; compaction assumes overlay snapshot path shape; only both uidmap and gidmap together trigger idmapping; `X-containerd.*` options intentionally error if manager transforms did not consume them. Helper ECHILD retry can unmount uncertain partial mounts but still depends on mountinfo accuracy.

Test signals: `mount_linux_test.go` covers lowerdir compaction, FUSE helper mounting, `mountAt` chdir isolation, recursive/unordered unmounts, idmapped overlay preparation and cleanup, unprivileged flag preservation, path rewriting, common-directory edge cases, and internal-option rejection.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_linux_test.go -->
# sources/cloud-native/containerd/core/mount/mount_linux_test.go

Purpose: Linux tests for mount option helpers, real mount behavior, recursive cleanup, FUSE helper integration, and idmapped overlay lowerdir preparation.

Important APIs/types/functions: `TestLongestCommonPrefix`, `TestCompactLowerdirOption`, `TestFUSEHelper`, `TestMountAt`, `TestUnmountMounts`, `TestUnmountRecursive`, `TestDoPrepareIDMappedOverlayCleanups`, `TestDoPrepareIDMappedOverlay`, `TestGetUnprivilegedMountFlags`, `setupMounts`, `supportsIDMap`, `TestBuildIDMappedPaths`, `TestGetCommonDirectory`, and `TestXContainerdOptionsFiltered`.

Control flow: non-root-safe helpers test string/path logic directly; root tests mount bind/tmpfs/FUSE/idmapped trees, read files through mount points, and verify cleanup. IDMapped overlay tests create lowerdirs, remap a common parent, assert content appears through rewritten paths, and simulate busy cleanup failures.

State and persistence: creates temporary directories and real kernel mounts; tests clean up with `Unmount`, `UnmountAll`, or cleanup callbacks.

Dependencies and integration points: requires root for most mount syscalls, optional `fuse-overlayfs`, and idmap-capable kernel/filesystem for idmapped tests. Exercises functions used by `mount_linux.go` during normal `Mount.Mount`.

Risks covered: page-size compaction path correctness, working-directory isolation in `mountAt`, preservation of original lowerdirs during idmapped overlay cleanup, and rejection of unconsumed `X-containerd.*` options.

Test signals: high coverage but many environment skips/requirements. It complements pure parser checks with actual kernel behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_test.go -->
# sources/cloud-native/containerd/core/mount/mount_test.go

Purpose: platform-neutral tests for read-only mount rewriting and temporary overlay option filtering.

Important APIs/types/functions: `TestReadonlyMounts` and `TestRemoveVolatileTempMount`.

Control flow: tests table-driven input mount slices and expected output slices using `reflect.DeepEqual`; the volatile tests also verify original input slices are not modified when `RemoveVolatileOption` copies.

State and persistence: no external state.

Dependencies and integration points: validates helpers used by `WithReadonlyTempMount` and `WithTempMount` before real mounting occurs.

Risks covered: overlay read-only conversion removes `upperdir`/`workdir` and prepends upperdir to lowerdir; normal mounts normalize `ro`; overlay-only volatile stripping leaves non-overlay options intact.

Test signals: does not cover `RemoveIDMapOption` directly and does not exercise `Mount.Mount`; those are covered elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_unix.go -->
# sources/cloud-native/containerd/core/mount/mount_unix.go

Purpose: Unix unmount helpers for non-Windows, non-OpenBSD platforms.

Important APIs/types/functions: `UnmountRecursive(target, flags)` canonicalizes a target, finds all mountinfo entries under it, sorts deepest paths first, and calls `UnmountAll`.

Control flow: empty target returns nil. Nonexistent canonical target is treated as no-op. Mountpoints are deduplicated through a map, sorted by descending path length, and unmounted; errors from children are tolerated unless the final/top-level target fails.

State and persistence: removes kernel mount state below a path; no metadata persistence.

Dependencies and integration points: used by temp mount cleanup, idmapped overlay cleanup, and mount manager cleanup paths. Depends on `moby/sys/mountinfo`, `CanonicalizePath`, and platform `UnmountAll`.

Risks: prefix filtering depends on canonical paths; non-final child unmount failures can be ignored, potentially leaving busy nested mounts. Sorting by string length is a practical deepest-first heuristic.

Test signals: `mount_linux_test.go` exercises recursive unmounts with nested bind mounts.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_unsupported.go -->
# sources/cloud-native/containerd/core/mount/mount_unsupported.go

Purpose: OpenBSD unsupported mount implementation.

Important APIs/types/functions: platform stubs for `(*Mount).mount`, `Unmount`, `UnmountAll`, and `UnmountRecursive`, all returning `errdefs.ErrNotImplemented`.

Control flow: every mount/unmount entry point fails immediately.

State and persistence: no state and no filesystem changes.

Dependencies and integration points: selected by `openbsd` build tag so shared code compiles while callers can detect unsupported behavior.

Risks: any path that does not check `ErrNotImplemented` will fail on OpenBSD. `HasBindMounts` is false for OpenBSD in `mount.go`.

Test signals: no direct tests in this subset; behavior is trivial stubbing.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_windows.go -->
# sources/cloud-native/containerd/core/mount/mount_windows.go

Purpose: Windows layer mount implementation using HCSShim layer activation/preparation and bind filter links.

Important APIs/types/functions: `(*Mount).mount` handles `windows-layer`; helper methods parse parent paths from options and manage bindfilter links; constants include an alternate data stream name for recording source paths.

Control flow: validates mount type, splits source into home/layer ID, computes parent layer paths, activates and prepares the layer with cleanup defers, obtains the layer mount path, and either links base layer `Files` or uses bindfilter for mounted layers. Cleanup deactivates/unprepares on failure.

State and persistence: modifies Windows container layer state through hcsshim and creates filesystem links/bindfilter state at target. It may write/read source metadata through alternate streams for cleanup support.

Dependencies and integration points: selected on Windows; integrates `hcsshim`, `go-winio` bindfilter, Windows syscall package, and containerd logging. It is the platform implementation behind `Mount.Mount` for Windows snapshot/layer mounts.

Risks: highly dependent on Windows container layer invariants and hcsshim behavior. Failure cleanup must unwind activation/preparation in the correct order; base-layer handling differs from child-layer handling.

Test signals: no Windows tests in this subset; coverage is platform-specific elsewhere or by integration.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mount_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mountinfo.go -->
# sources/cloud-native/containerd/core/mount/mountinfo.go

Purpose: exposes mountinfo lookup through the mount package.

Important APIs/types/functions: this file aliases or wraps `moby/sys/mountinfo` types/functions so callers can query mount table entries without importing the lower-level package directly.

Control flow: lookup functions read current mountinfo and filter by target/path according to the underlying mountinfo implementation.

State and persistence: read-only view of kernel mount table state.

Dependencies and integration points: used by platform mount implementations and tests to compare mount IDs before/after helper invocations and to detect successful mounts.

Risks: behavior depends on `/proc/self/mountinfo` availability and namespace context on Unix-like systems. Stale or namespace-mismatched lookup results can affect ECHILD cleanup decisions.

Test signals: indirectly exercised by FUSE/FreeBSD-style helper retry logic and Linux tests using `Lookup`/unmount flows.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/mountinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/proxy/convert.go -->
# sources/cloud-native/containerd/core/mount/proxy/convert.go

Purpose: converts between core mount activation structs and protobuf API structs for the mounts service.

Important APIs/types/functions: `ActivationInfoToProto`, `ActivationInfoFromProto`, `ActiveMountToProto`, `ActiveMountFromProto`, `toTimestamp`, and `fromTimestamp`.

Control flow: conversions allocate same-length slices, copy mount fields, mount points, mount data, labels, and timestamps. Nil `ActivationInfo` proto input returns a zero-value core struct; nil time/timestamp pointers stay nil.

State and persistence: no persistence; pure data translation.

Dependencies and integration points: used by `proxy.go` and server/client code for gRPC/ttrpc mount manager RPCs. Relies on `mount.ToProto`/`FromProto` for system mounts and protobuf timestamp helpers.

Risks: `ActiveMountFromProto` assumes each proto active mount and nested `Mount` are non-nil. Timestamp conversion uses `AsTime` without validation checks.

Test signals: no direct tests in this subset; exercised indirectly by proxy clients when RPC tests exist.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/proxy/convert.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/proxy/proxy.go -->
# sources/cloud-native/containerd/core/mount/proxy/proxy.go

Purpose: client-side `mount.Manager` implementation backed by the containerd mounts gRPC/ttrpc service.

Important APIs/types/functions: `proxyMounts`, `NewMountManager`, and methods `Activate`, `Deactivate`, `Info`, `Update`, and `List`.

Control flow: `NewMountManager` accepts a gRPC mounts client, generic gRPC connection, ttrpc mounts client, or ttrpc client, wrapping gRPC as a ttrpc-compatible interface where needed. Each method converts core structs/options into API requests, calls the remote client, converts responses back, and maps gRPC errors to native errors with `errgrpc.ToNative`. `List` consumes a streaming response until `io.EOF`.

State and persistence: stores only the RPC client. Persistent activation state lives in the remote manager service.

Dependencies and integration points: bridges `core/mount.Manager` callers to API service `api/services/mounts/v1`. Update masks use containerd protobuf field mask type.

Risks: `NewMountManager` panics on unsupported client types. `Activate` forwards labels and `Temporary` but not `AllowMountTypes`, so remote behavior cannot honor that option through this proxy as written. Streaming errors abort list.

Test signals: no direct proxy tests in this subset; conversion/proxy correctness is inferred from API use.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/proxy/proxy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/temp.go -->
# sources/cloud-native/containerd/core/mount/temp.go

Purpose: temporary mount lifecycle helpers and option filtering for temporary/read-only access to mount arrays.

Important APIs/types/functions: package variable `tempMountLocation`; `WithTempMount`, `RemoveVolatileOption`, `RemoveIDMapOption`, `copyMounts`, `WithReadonlyTempMount`, and `getTempDir`.

Control flow: `WithTempMount` creates a temp directory under `tempMountLocation`, defers `os.Remove` and reverse unmount, mounts all input mounts after removing overlay volatile options, runs the callback, and combines callback/unmount errors carefully. `RemoveVolatileOption` and `RemoveIDMapOption` lazily copy mounts only when a matching option is removed. `WithReadonlyTempMount` first converts mounts to read-only.

State and persistence: creates and removes a temporary directory; performs real mounts through `All` and unmounts through `UnmountMounts`. It deliberately uses `os.Remove` instead of `RemoveAll` to avoid deleting mounted data if unmount fails.

Dependencies and integration points: used by image unpack/inspection and temporary access flows. `SetTempMountLocation` in platform files changes the base location; Linux idmapped overlay helpers also use `tempMountLocation`.

Risks: temp dirs can leak when unmount fails, by design. `RemoveIDMapOption` removes while ranging and may skip adjacent idmap options after slice mutation. `RemoveVolatileOption` removes only the first volatile-like option per overlay mount.

Test signals: `mount_test.go` covers volatile removal and input preservation; read-only conversion tests cover `WithReadonlyTempMount` preprocessing. Runtime mount/unmount behavior is exercised through Linux tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/temp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/temp_unix.go -->
# sources/cloud-native/containerd/core/mount/temp_unix.go

Purpose: Unix implementation for configuring and cleaning temporary mount directories.

Important APIs/types/functions: `SetTempMountLocation(root string)` and `CleanupTempMounts(flags int)`.

Control flow: `SetTempMountLocation` creates the directory, canonicalizes it, and assigns `tempMountLocation` so later prefix filtering works. `CleanupTempMounts` lists mountinfo entries under the temp location, sorts deepest first, unmounts each with `UnmountAll`, removes each mountpoint directory, and accumulates warnings while returning a fatal error only for mountinfo lookup failure.

State and persistence: updates package-global temp mount base and removes real temporary mounts/directories.

Dependencies and integration points: used by daemon startup/cleanup flows and idmapped overlay temporary remounts. Depends on `moby/sys/mountinfo`, `CanonicalizePath`, and platform unmount helpers.

Risks: warnings are non-fatal, so callers must inspect them to notice leaked mounts or directories. Prefix filtering depends on canonical temp path.

Test signals: no direct test in this subset, but recursive unmount behavior is covered in Linux mount tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/temp_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/temp_unsupported.go -->
# sources/cloud-native/containerd/core/mount/temp_unsupported.go

Purpose: Windows stub implementation for temporary mount location configuration and cleanup.

Important APIs/types/functions: `SetTempMountLocation` returns nil and `CleanupTempMounts` returns nil warnings/error.

Control flow: both functions are no-ops.

State and persistence: no state changes and no cleanup.

Dependencies and integration points: selected by Windows build tag. Windows mount lifecycle is handled through Windows layer primitives rather than Unix temp mount cleanup.

Risks: callers expecting cleanup warnings will see success even though no scanning occurs. This is intentional platform behavior.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/temp_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/auth/fetch.go -->
# sources/cloud-native/containerd/core/remotes/docker/auth/fetch.go

Purpose: builds token request options from registry auth challenges and fetches bearer/OAuth tokens from Docker distribution-compatible authorization servers.

Important APIs/types/functions: `ErrNoToken`, `GenerateTokenOptions`, `TokenOptions`, `OAuthTokenResponse`, `FetchTokenWithOAuth`, `FetchTokenResponse`, and `FetchToken`.

Control flow: `GenerateTokenOptions` requires and parses `realm`, copies `service`, username/secret, and splits challenge `scope` on spaces. OAuth POST builds form data for password or refresh-token grant, optional `access_type=offline`, default User-Agent, request headers, and decodes `access_token`. GET token fetch adds service/scope query params, optional Basic auth, optional `offline_token=true`, decodes `token`/`access_token`, and canonicalizes `access_token` into `Token`.

State and persistence: no persistent state. HTTP clients are shallow-copied before tracing instrumentation so caller clients are not mutated.

Dependencies and integration points: used by `docker/authorizer.go` to fetch scoped bearer tokens after parsing `WWW-Authenticate`. Uses containerd tracing, versioned User-Agent, log, and remotes unexpected-status errors.

Risks: only HTTP status 200-399 is accepted; response body size is not explicitly capped here; `strings.Split(scope, " ")` can produce empty scope elements when scope is absent but present as an empty parameter. OAuth POST fallback behavior is implemented in the authorizer, not here.

Test signals: `fetch_test.go` covers token option generation, multiple/single/no scopes, missing realm, and invalid realm. Token HTTP fetch functions are not directly tested in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/auth/fetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/auth/fetch_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/auth/fetch_test.go

Purpose: tests challenge-to-token-option generation.

Important APIs/types/functions: `TestGenerateTokenOptions` builds `Challenge` values and asserts `GenerateTokenOptions` output.

Control flow: table cases cover multiple scopes, one scope, and no scope; subtests verify missing `realm` and unparsable `realm` return errors.

State and persistence: in-memory only.

Dependencies and integration points: validates inputs used by `dockerAuthorizer.AddResponses` before token fetching.

Risks covered: required realm validation and scope splitting. The no-scope expected value uses `strings.Split("", " ")`, which yields one empty string when the map includes an empty `scope` value; this documents current behavior.

Test signals: does not exercise HTTP token endpoints, offline token flags, headers, User-Agent, or error status handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/auth/fetch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/auth/parse.go -->
# sources/cloud-native/containerd/core/remotes/docker/auth/parse.go

Purpose: parses `WWW-Authenticate` headers into typed Docker registry authentication challenges.

Important APIs/types/functions: `AuthenticationScheme` bit constants `BasicAuth`, `DigestAuth`, `BearerAuth`; `Challenge`; `ParseAuthHeader`; parsing helpers `parseValueAndParams`, `skipSpace`, `expectToken`, and `expectTokenOrQuoted`; `byScheme` prioritizes bearer over digest over basic.

Control flow: initialization classifies ASCII bytes as token or space according to RFC token/separator rules. `ParseAuthHeader` iterates all canonical `WWW-Authenticate` headers, parses scheme/params, ignores unknown schemes, and stable-sorts by scheme priority. Parameter keys are lowercased; quoted strings support backslash escapes.

State and persistence: package-level octet classification table only; parsing itself is stateless.

Dependencies and integration points: consumed by `dockerAuthorizer.AddResponses` to decide whether to configure bearer or basic auth handlers.

Risks: parser is intentionally permissive and returns partial/empty results on malformed input instead of detailed errors. It parses one challenge per header string and does not fully model comma-separated multiple challenges with independent schemes.

Test signals: `parse_test.go` covers bearer challenge parsing, empty quoted parameter values, service extraction, and fuzzes arbitrary header strings for panics.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/auth/parse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/auth/parse_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/auth/parse_test.go

Purpose: tests and fuzzes Docker auth challenge parsing.

Important APIs/types/functions: `TestParseAuthHeaderBearer`, `TestParseAuthHeader`, and `FuzzParseAuthHeader`.

Control flow: bearer tests format header strings with realm/service/scope and compare exact `Challenge` slices. Empty parameter test ensures an empty quoted value is preserved. Fuzzing feeds arbitrary strings through `ParseAuthHeader`.

State and persistence: no external state.

Dependencies and integration points: protects `authorizer.go` from malformed registry `WWW-Authenticate` headers causing panics or lost important parameters.

Risks covered: multiple-space-separated scopes as one parameter value, empty quoted values, and parser robustness. It does not cover basic/digest sorting or escaped quotes explicitly.

Test signals: useful parser regression coverage plus fuzz panic resistance.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/auth/parse_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/authorizer.go -->
# sources/cloud-native/containerd/core/remotes/docker/authorizer.go

Purpose: Docker registry `Authorizer` implementation that reacts to 401 challenges, caches per-host auth handlers, injects Basic or Bearer authorization headers, and optionally returns refresh tokens.

Important APIs/types/functions: `dockerAuthorizer`, `authorizerConfig`, option functions `WithAuthClient`, `WithAuthCreds`, `WithAuthHeader`, `WithFetchRefreshToken`, `NewDockerAuthorizer`, `Authorize`, `AddResponses`, `authHandler`, `authResult`, `doBasicAuth`, `doBearerAuth`, `getExpirationTime`, `invalidAuthorization`, and `sameRequest`.

Control flow: `AddResponses` parses the last response challenge. Bearer challenges may clear cached handlers on invalid-token retry, fetch credentials, generate common token options, and install a per-host auth handler. Basic challenges require non-empty credentials. `Authorize` looks up the host handler, gets an auth value, sets `Authorization`, and calls the refresh-token callback when present. Bearer auth merges request scopes from context, caches token fetches by scope string, uses a `WaitGroup` result so concurrent requests share one fetch, prefers OAuth POST when credentials exist, and falls back to GET on known incompatible statuses.

State and persistence: in-memory host handler map guarded by `mu`; each handler has a mutex-protected scoped token cache with optional expiration time. No disk persistence; refresh token persistence is delegated to the callback.

Dependencies and integration points: used by Docker resolver/pusher request retry loops; depends on `auth.ParseAuthHeader`, `auth.FetchToken*`, remotes unexpected-status errors, `ErrInvalidAuthorization`, and request scope context helpers.

Risks: token cache key is a joined scope string and order-sensitive. Expired token replacement overwrites the cache entry but waiters on the old result still receive old state. Basic credentials are not cached separately from handler setup. `getAuthHandler` takes a write lock even for reads. Invalid authorization retry logic allows one retry per distinct request before returning `ErrInvalidAuthorization`.

Test signals: integration coverage appears in resolver tests outside this subset; `hosts_resolver_test.go` indirectly exercises bearer token fetching with per-host headers. Auth fetch/parse tests cover lower-level pieces.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/authorizer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/config_unix.go -->
# sources/cloud-native/containerd/core/remotes/docker/config/config_unix.go

Purpose: Unix host directory search layout for Docker registry `certs.d`/`hosts.toml` configuration.

Important APIs/types/functions: `hostPaths(root, host)` returns candidate directories.

Control flow: converts a host with port through `hostDirectory` (`host:5000` to `host_5000_`) and, when that differs, checks it first. Then checks the literal host directory and `_default`.

State and persistence: read-only path construction; actual filesystem probing is in `HostDirFromRoot`.

Dependencies and integration points: used by `hosts.go` to locate host-specific registry config on non-Windows platforms.

Risks: both sanitized and literal forms may exist; first match wins. IPv6/colon behavior relies on `hostDirectory`.

Test signals: `hosts_test.go` and resolver tests exercise host directory lookup through `HostDirFromRoot`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/config_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/config_windows.go -->
# sources/cloud-native/containerd/core/remotes/docker/config/config_windows.go

Purpose: Windows host directory search layout for Docker registry config.

Important APIs/types/functions: `hostPaths(root, host)` mirrors Unix but strips `:` characters because Windows paths cannot contain colons.

Control flow: if `hostDirectory` changed the host, it checks the colon-stripped sanitized name; then checks the colon-stripped literal host and `_default`.

State and persistence: path construction only.

Dependencies and integration points: used by `HostDirFromRoot` on Windows for `hosts.toml` and certificate discovery.

Risks: stripping colons can cause name collisions that are impossible on Unix. IPv6 address directory names may be less readable and potentially ambiguous.

Test signals: resolver test has a Windows-specific branch when constructing expected host config directories.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/config_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/docker_fuzzer_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/config/docker_fuzzer_test.go

Purpose: fuzz target for `parseHostsFile`.

Important APIs/types/functions: `FuzzParseHostsFile` uses `go-fuzz-headers` to create arbitrary files and TOML bytes under a temp dir, then calls `parseHostsFile`.

Control flow: fuzz input is split between generated filesystem fixtures and bytes passed as the hosts file. Errors are intentionally ignored because the objective is crash/panic resistance.

State and persistence: temporary directories and generated files only.

Dependencies and integration points: protects Docker registry configuration parsing from malformed TOML and file path combinations.

Risks covered: parser robustness, relative path handling, and type assertion paths. It does not assert semantic correctness for accepted configs.

Test signals: fuzz-only coverage complements deterministic `hosts_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/docker_fuzzer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/hosts.go -->
# sources/cloud-native/containerd/core/remotes/docker/config/hosts.go

Purpose: builds Docker registry host configuration from defaults, `hosts.toml`, Docker-style certificate directories, TLS settings, headers, credentials, and per-host client customization.

Important APIs/types/functions: `UpdateClientFunc`, `hostConfig`, `HostOptions`, `ConfigureHosts`, `updateTLSConfigFromHost`, `HostDirFromRoot`, `hostDirectory`, `loadHostDir`, `hostFileConfig`, `parseHostsFile`, `parseHostConfig`, `getSortedHosts`, `makeStringSlice`, `makeAbsPath`, and `loadCertFiles`.

Control flow: `ConfigureHosts` returns a `docker.RegistryHosts` closure. For a requested host it loads host configs from `HostDir`, defaults to Docker Hub or the requested host when no config exists, builds a default transport/client/authorizer, then creates `docker.RegistryHost` entries. Per-host TLS, dial timeout, or headers cause a cloned client/transport and a separate authorizer with merged auth headers. HTTP endpoints with TLS configuration and non-80 ports are upgraded to HTTPS plus `docker.NewHTTPFallback`.

State and persistence: reads `hosts.toml`, CA certs, client cert/key files, and directory listings. It does not persist config; returned registry hosts carry clients, TLS roots/certs, headers, and authorizers in memory.

Dependencies and integration points: used by Docker resolver configuration. Integrates `docker.RegistryHost` capabilities, `docker.NewDockerAuthorizer`, `docker.DefaultHTTPTransport`, `docker.NewHTTPFallback`, pelletier TOML parser, x509/tls, and Docker cert directory conventions.

Config semantics: `parseHostsFile` preserves host table order using the TOML unstable parser, parses mirror hosts first, and appends root `server` config last. `parseHostConfig` normalizes server URLs, appends `/v2` unless `override_path` is true, maps capabilities (`pull`, `resolve`, `push`, `referrers`), resolves relative cert paths, supports multiple CA/client forms, headers as string or string list, and `dial_timeout`.

Risks: TLS configs are mutated on cloned transports; bad cert files fail host resolution. `getSortedHosts` depends on unstable TOML APIs. `HostDirFromRoot` first existing path wins. Header types and cert/client TOML shapes are strict. Localhost default skip-verify/fallback logic is nuanced and easy to regress.

Test signals: `hosts_test.go` covers Docker Hub defaults, detailed TOML parsing, cert file discovery, and HTTP fallback matrix. `hosts_resolver_test.go` covers real resolver behavior with server/mirror/token headers. `docker_fuzzer_test.go` fuzzes parser robustness.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/hosts.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/hosts_resolver_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/config/hosts_resolver_test.go

Purpose: integration-style resolver tests for `hosts.toml` server/mirror config, TLS roots, bearer token flow, and per-host headers.

Important APIs/types/functions: `TestResolverWithHostsDir`, `testResolverWithHostsDir`, `runBasicTest`, `newTLSServer`, `testContent`, `testManifest`, and related helpers.

Control flow: each scenario creates upstream, mirror, server, and token TLS test servers. A generated `hosts.toml` defines a server and mirror with distinct headers. The resolver resolves an image and assertions verify which endpoint handled requests and which headers were sent to registry and token endpoints.

State and persistence: writes a temporary host directory and `hosts.toml`; creates in-memory TLS servers and content descriptors/manifests.

Dependencies and integration points: exercises `ConfigureHosts`, `HostDirFromRoot`, Docker resolver, `NewDockerAuthorizer`, token fetching, TLS root pools, and `RegistryHost` capability ordering.

Risks covered: server entry prevents upstream calls, mirror priority over server, server fallback when mirror disabled, per-host headers do not bleed across endpoints, and token requests inherit the selected host headers.

Test signals: high-value behavioral signal for config/auth integration. It relies on local test servers and copied resolver test helpers.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/hosts_resolver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/hosts_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/config/hosts_test.go

Purpose: deterministic unit tests for default registry host config, hosts.toml parsing, Docker cert directory fallback, and HTTP fallback selection.

Important APIs/types/functions: `TestDefaultHosts`, `TestParseHostFile`, `TestLoadCertFiles`, `TestHTTPFallback`, comparison/printing helpers, and `testKey`.

Control flow: tests compare returned host configs field-by-field, including scheme/host/path/capabilities/CA/client pairs/skipVerify/headers/dial timeout. Cert tests create `.crt`, `.cert`, and `.key` files and load them through `loadHostDir`. Fallback tests generate many host/default scheme/TLS cases and inspect returned scheme plus transport type.

State and persistence: uses temp directories and test certificate/key files. No network requests.

Dependencies and integration points: validates `hosts.go`, `config_unix.go`/`config_windows.go` path behavior, and `docker.NewHTTPFallback` selection assumptions.

Risks covered: host table ordering, `override_path`, no-referrers capability omission, header list parsing, client cert shape variants, localhost/port HTTP-vs-HTTPS defaults, and default Docker Hub mapping.

Test signals: broad unit coverage for config parsing and defaulting; semantic network behavior is covered by `hosts_resolver_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/config/hosts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/converter.go -->
# sources/cloud-native/containerd/core/remotes/docker/converter.go

Purpose: converts legacy Docker schema2 manifests whose config media type is `application/octet-stream` into manifests using the Docker schema2 config media type.

Important APIs/types/functions: `LegacyConfigMediaType` and `ConvertManifest`.

Control flow: exits unchanged for non-manifest descriptors. Reads the manifest blob from a content store, unmarshals OCI manifest JSON, returns unchanged when config media type is not legacy, rewrites the config media type, marshals indented JSON, recomputes descriptor digest/size, builds GC reference labels for config and layers, and writes the new blob under a remote ref key.

State and persistence: writes a new content blob to `content.Store`; the old manifest is left for future GC. Descriptor digest/size are returned for the new content.

Dependencies and integration points: used in Docker remote conversion paths to normalize old registry content. Integrates `content.ReadBlob`, `content.WriteBlob`, `images` media type helpers, OCI descriptors, digest calculation, and remotes ref keys.

Risks: only manifest media types are converted, not manifest lists; malformed or missing blobs return errors. JSON indentation changes the digest by design. Existing labels are replaced with generated GC refs.

Test signals: `converter_fuzz_test.go` fuzzes descriptor/content-store inputs for panic resistance; deterministic conversion assertions are outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/converter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/converter_fuzz_test.go -->
# sources/cloud-native/containerd/core/remotes/docker/converter_fuzz_test.go

Purpose: fuzz target for `ConvertManifest`.

Important APIs/types/functions: `FuzzConvertManifest` generates arbitrary OCI descriptors and invokes `ConvertManifest` against a temp local content store.

Control flow: fuzz input populates an `ocispec.Descriptor`; a local content store is created; conversion is called and errors are ignored. Logging is set to panic level to suppress expected warnings for non-manifest media types.

State and persistence: uses a temporary local content store.

Dependencies and integration points: protects manifest conversion against malformed descriptor inputs and content-store edge cases.

Risks covered: panic resistance only; most fuzz descriptors will not reference valid content, so semantic conversion success is sparse.

Test signals: complements any deterministic converter tests elsewhere by widening malformed-input coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/converter_fuzz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/errcode.go -->
# sources/cloud-native/containerd/core/remotes/docker/errcode.go

Purpose: Docker registry error-code model and JSON error envelope handling.

Important APIs/types/functions: `ErrorCoder`, `ErrorCode`, `Error`, `ErrorDescriptor`, `ParseErrorCode`, `Errors`, `unexpectedResponseErr`, plus methods for text marshal/unmarshal, message/detail/args construction, JSON marshal/unmarshal, and error formatting.

Control flow: `ErrorCode` resolves descriptors through generated maps and falls back to `ErrorCodeUnknown`. `Errors.MarshalJSON` normalizes `ErrorCode`, `Error`, and arbitrary errors into an `{"errors":[...]}` envelope. `Errors.UnmarshalJSON` collapses detail-less/default-message entries back to bare `ErrorCode`. `unexpectedResponseErr` wraps remotes unexpected status and, when the response body contains registry errors, joins the status error with typed registry errors.

State and persistence: no persistent state; serialization/deserialization of registry error payloads.

Dependencies and integration points: used by Docker resolver/pusher error paths to expose typed registry errors while retaining HTTP status context. Depends on generated descriptor maps in companion files and `core/remotes/errors`.

Risks: unknown error details may be marshaled as `ErrorCodeUnknown` with arbitrary detail values. `unexpectedResponseErr` type-asserts the unexpected status shape and ignores malformed registry error bodies. Joined errors require callers to use `errors.As/Is` correctly.

Test signals: no direct tests in this subset. Behavior is likely covered by resolver/pusher tests outside this work item.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/remotes/docker/errcode.go -->
