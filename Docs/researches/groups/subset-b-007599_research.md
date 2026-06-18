# subset-b-007599 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/docs/examples/kubo-as-a-library/main.go -->
# sources/distributed-fs/ipfs-kubo/docs/examples/kubo-as-a-library/main.go

## Purpose

This example is an executable tutorial for embedding Kubo as a Go library. It creates temporary repos, starts two in-process online IPFS nodes, connects them directly, adds local files and directories, reads them back through the CoreAPI, and demonstrates Bitswap retrieval from a peer without DHT or bootstrap discovery.

## Important APIs, Types, and Functions

`setupPlugins` initializes the plugin loader, including built-in plugins. `createTempRepo` creates an Ed25519 identity, configures a minimal loopback-only repo, disables QUIC/relay/web transports/autoconf/bootstrap/DHT, optionally toggles experimental features, and calls `fsrepo.Init`. `createNode` opens the repo and builds a `core.IpfsNode` with `libp2p.NilRouterOption`. `spawnEphemeral` uses `sync.Once` to load plugins only once, then returns `coreapi.NewCoreAPI`. `connectToPeers` parses `/p2p/` multiaddrs into grouped `peer.AddrInfo` entries and connects concurrently. `getUnixfsNode` adapts filesystem paths into `boxo/files.Node`.

## Control Flow, State, and Integration

`main` uses a two-minute context, starts node A and B, connects B to A via A's first local swarm address, adds content to node A, imports example file/directory content into node B, writes retrieved UnixFS nodes to a temporary output directory, then fetches node A's CID through node B. Persistent state is intentionally temporary: repos are created under the system temp directory, no bootstrap list is saved, and only the per-repo datastore retains added blocks during the process lifetime.

## Dependencies, Risks, and Test Signals

The example depends on Kubo core, CoreAPI, fsrepo, config, libp2p, multiformats multiaddrs, and boxo UnixFS files. Risks include relying on local example fixtures, assuming `peerAddrs[0]` exists, using temp repos without cleanup, and using `panic` instead of library-style error handling because this is tutorial code. The companion test runs `go run main.go` with reduced logging and checks for the final success banner; the Makefile also runs the example against published and local Kubo module replacements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/docs/examples/kubo-as-a-library/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/docs/examples/kubo-as-a-library/main_test.go -->
# sources/distributed-fs/ipfs-kubo/docs/examples/kubo-as-a-library/main_test.go

## Purpose

This test smoke-tests the library example as a real program rather than unit-testing individual helpers. It verifies that `go run main.go` can start temporary Kubo nodes, add and retrieve content, and reach the tutorial's completion path.

## Important APIs, Types, and Functions

`TestExample` uses `exec.Command("go", "run", "main.go")`, streams stdout and stderr through `io.MultiWriter` to both the test process and an in-memory buffer, and sets `GOLOG_LOG_LEVEL=error` to reduce libp2p noise.

## Control Flow, State, and Integration

The test records elapsed runtime, runs the example in the package directory, fails with captured output on command error, and asserts that output contains `All done!`. It exercises the full example's temporary repo creation, plugin setup, node startup, peer connection, UnixFS add/get, and Bitswap fetch paths.

## Dependencies, Risks, and Test Signals

The test depends on the Go toolchain, network loopback, the example fixture directory, and enough time for libp2p setup. It is intentionally broad and can fail from environment issues that unit tests would isolate. The key test signal is the final output string, plus command exit status and elapsed time logs for diagnosing CI hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/docs/examples/kubo-as-a-library/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/fusetest/detect.go -->
# sources/distributed-fs/ipfs-kubo/fuse/fusetest/detect.go

## Purpose

This file centralizes platform and environment detection for FUSE tests on supported go-fuse platforms. It lets tests skip cleanly when FUSE is unavailable while still allowing CI to force failures when FUSE is expected.

## Important APIs, Types, and Functions

`fuseFlagFromEnv` reads `TEST_FUSE`, with legacy `TEST_NO_FUSE=1` treated as `TEST_FUSE=0`. `fuseAvailable` verifies `runtime.GOOS`, then checks `fusermount` or `fusermount3` on Linux and `umount` on Darwin/FreeBSD.

## Control Flow, State, and Integration

There is no persisted state. The helper calls `t.Skip` with targeted messages for unsupported OSes and missing mount helpers. It is consumed by `SkipUnlessFUSE` in `fusetest.go` and therefore gates all shared FUSE integration tests.

## Dependencies, Risks, and Test Signals

Dependencies are `os/exec`, `runtime`, and Go's testing package. The main risk is false positives: helper binaries may exist while kernel permissions, `/dev/fuse`, or macFUSE setup still prevent mounting. That risk is handled later by `MountError`, which skips or fails based on `TEST_FUSE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/fusetest/detect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/fusetest/fusetest.go -->
# sources/distributed-fs/ipfs-kubo/fuse/fusetest/fusetest.go

## Purpose

`fusetest.go` provides shared test utilities for mounting go-fuse filesystems and asserting POSIX stat behavior. It prevents each FUSE package from duplicating environment detection, mount cleanup, and stat assertions.

## Important APIs, Types, and Functions

`SkipUnlessFUSE` implements the `TEST_FUSE` decision order. `TestMount` creates a temp mountpoint, fills default `fs.Options` with null permissions and current UID/GID, calls `fs.Mount`, and registers unmount cleanup. `AssertStatfsNonZero` verifies real filesystem space data. `AssertStatBlocks` validates `st_blocks` and `st_blksize`. `MountError` fails when `TEST_FUSE=1` and otherwise skips on mount errors.

## Control Flow, State, and Integration

The file controls test-time lifecycle only: temp dirs are owned by `testing.T`, and mounted servers are unmounted in cleanup. It integrates with `/ipfs`, `/ipns`, `/mfs`, and writable suite tests.

## Dependencies, Risks, and Test Signals

Dependencies are `hanwen/go-fuse/v2/fs`, `syscall`, `os`, and `testify/require`. Risks include platform-specific `syscall.Stat_t` assumptions and cleanup relying on `server.Unmount`. Test signals are non-zero statfs values, correctly rounded 512-byte block counts, and fatal behavior when CI declares FUSE mandatory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/fusetest/fusetest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/fusetest/writablesuite.go -->
# sources/distributed-fs/ipfs-kubo/fuse/fusetest/writablesuite.go

## Purpose

This file defines the shared behavioral conformance suite for writable Kubo FUSE mounts. It is used by both `/mfs` and writable `/ipns/local` to ensure the shared `fuse/writable` adapter behaves like a practical POSIX filesystem.

## Important APIs, Types, and Functions

`MountFunc` abstracts mount creation from a `writable.Config`. `RunWritableSuite` registers subtests for reads, writes, append, multiwrite, directory creation, immediate create/mkdir attrs, renames, removals, fsync, truncate, large files, temporary-file replacement patterns, sparse writes, `O_EXCL`, symlinks, metadata persistence, xattrs, concurrent writes/reads, read/write snapshots, and filesystem thrash. Helpers include `RandBytes`, `WriteFile`, `WriteFileOrFail`, `VerifyFile`, `CheckExists`, and `Lchtimes`.

## Control Flow, State, and Integration

Each subtest calls the supplied mount function to create a fresh filesystem. Data is persisted through the mount's backing MFS/IPNS state, then checked through normal `os`, `syscall`, and `unix` calls. Some tests enable `StoreMtime` or `StoreMode` to exercise UnixFS optional metadata. Concurrent tests use goroutines and `sync.WaitGroup`; race builds reduce workload size.

## Dependencies, Risks, and Test Signals

The suite depends on standard filesystem syscalls, `golang.org/x/sys/unix`, `testify/require`, and `fuse/writable`. It guards high-risk areas: MFS descriptor locks, kernel attr caching after create, non-atomic rename behavior, sparse write visibility, symlink metadata, xattr error mapping, fsync cache invalidation, and large-file readahead concurrency. Failures usually point to regressions in `writable.go`, mount capabilities, or mutable cache handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/fusetest/writablesuite.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/common.go -->
# sources/distributed-fs/ipfs-kubo/fuse/ipns/common.go

## Purpose

This file contains the shared IPNS initialization helper used by tests and mount orchestration. It initializes a key's IPNS record to an empty directory so writable IPNS mounts have a valid MFS root.

## Important APIs, Types, and Functions

`InitializeKeyspace` creates a cancellable context from the node context, constructs `unixfs.EmptyDirNode`, pins and flushes it through `n.Pinning`, creates a `namesys.NewIPNSPublisher`, and publishes the empty directory CID with the supplied private key.

## Control Flow, State, and Integration

The function mutates node state by adding a pinned empty directory and writing an IPNS record into the repo datastore/routing backend. It is used by IPNS FUSE tests and node-level mount tests before mounting `/ipns`.

## Dependencies, Risks, and Test Signals

Dependencies are boxo UnixFS, namesys, Kubo core, libp2p crypto, and datastore-backed IPNS publishing. Risks include pin/flush failures leaving partial state and publication failures in offline or misconfigured routing contexts. Tests verify persistence by mounting, writing, unmounting, and remounting the same node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/common.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/ipns_test.go -->
# sources/distributed-fs/ipfs-kubo/fuse/ipns/ipns_test.go

## Purpose

This file tests the `/ipns` FUSE mount and adapts the shared writable suite to the writable `/ipns/local` directory. It also covers IPNS-specific symlink, namespace mode, persistence, and statfs behavior.

## Important APIs, Types, and Functions

`mountWrap` tracks the mounted directory, `Root`, and go-fuse server. `fakeMount` simulates an active daemon IPNS mount so publish guards are exercised. `setupIpnsTest` creates or reuses a node, initializes keyspace, builds CoreAPI, creates a root with alias `local`, mounts it with writable capabilities, and sets `nd.Mounts.Ipns`. `newIpnsMount` translates `writable.Config` to `config.Mounts` and returns `/local`.

## Control Flow, State, and Integration

The tests create real FUSE mounts, write through MFS-backed IPNS directories, close roots to flush/publish, and remount against the same node to check persistence. `TestIpnsLocalLink` verifies the alias symlink points to the peer ID directory. `TestNamespaceRootMode` checks execute-only root permissions. `TestStatfs` points the root at a real repo directory and verifies non-zero filesystem stats.

## Dependencies, Risks, and Test Signals

Dependencies include Kubo core, CoreAPI, config, go-fuse, `fusetest`, and `fuse/writable`. Risks covered include issue #2168's publish guard bypass, missing root close on unmount, stale IPNS state after remount, incorrect namespace permissions, and Finder-visible zero statfs values. The broad writable suite provides regression coverage for POSIX operations on `/ipns/local`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/ipns_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/ipns_unix.go -->
# sources/distributed-fs/ipfs-kubo/fuse/ipns/ipns_unix.go

## Purpose

`ipns_unix.go` implements the FUSE tree for `/ipns` on supported platforms. Local keys are writable directories backed by MFS roots, aliases are symlinks to key IDs, and non-local IPNS names resolve to read-only symlinks into the `/ipfs` mount.

## Important APIs, Types, and Functions

`Root` stores CoreAPI, key aliases, local writable directories, MFS roots, symlinks, mount roots, and repo path. `ipnsPubFunc` publishes updated MFS root CIDs with `Name().Publish`, marking the context via `fusemount.ContextWithPublish`. `loadRoot` resolves the key path or falls back to an empty directory, builds an `mfs.Root`, and wraps it in `writable.NewDir`. `CreateRoot` builds writable config from mount/import settings and creates all local key directories and alias links. `Root` implements `Getattr`, `Statfs`, `Lookup`, `Readdir`, and `Close`.

## Control Flow, State, and Integration

Lookup first hides macOS probe names, then returns local alias symlinks, local writable directories, or resolves arbitrary `/ipns/<name>` and maps IPFS results to `/ipfs/<cid>` symlinks. `Close` closes all MFS roots, which flushes and publishes local key state. State persists through the MFS root DAG, pinning/datastore, and IPNS records.

## Dependencies, Risks, and Test Signals

Dependencies include CoreAPI, namesys, mfs, UnixFS DAG services, config, `fuse/writable`, and `internal/fusemount`. High-risk behavior includes local publishes being blocked without the context bypass, non-protobuf IPNS roots, stale kernel cache for mutable entries, and external publishes overwriting local mount state. Tests check local alias links, persistence across unmount/remount, statfs, and the shared writable suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/ipns_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/link_unix.go -->
# sources/distributed-fs/ipfs-kubo/fuse/ipns/link_unix.go

## Purpose

This file implements symlink nodes used by the `/ipns` FUSE root. They represent aliases such as `/ipns/local` and resolved remote IPNS names that point into `/ipfs`.

## Important APIs, Types, and Functions

`Link` embeds `fs.Inode` and stores a `Target`. `Getattr` sets symlink permissions, and `Readlink` returns the target bytes.

## Control Flow, State, and Integration

The object is immutable after construction by `Root.Lookup` or `CreateRoot`. It has no persistence of its own; it reflects root-level alias maps or resolved names. It integrates with go-fuse `NodeGetattrer` and `NodeReadlinker` behavior through method names.

## Dependencies, Risks, and Test Signals

Dependencies are go-fuse and syscall mode constants. The main risk is incomplete symlink attributes; mode here is permission bits, while stable inode type is supplied by the parent lookup. IPNS tests verify `/ipns/local` readlink behavior and readdir mode reporting through root entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/link_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/mount_unix.go -->
# sources/distributed-fs/ipfs-kubo/fuse/ipns/mount_unix.go

## Purpose

This file mounts the `/ipns` FUSE filesystem and wraps unmount so local MFS roots are closed and published. It is the daemon-facing entry point for the IPNS mount.

## Important APIs, Types, and Functions

`mutableCacheTime` is one second for entry and attr caching. `Mount` builds CoreAPI, reads repo config, derives MFS root options from import config, gets the self key, calls `CreateRoot`, fills `fs.Options`, and calls `fusemnt.NewMount`. `ipnsMount` embeds `mount.Mount` and overrides `Unmount` to close the `Root`.

## Control Flow, State, and Integration

Mount creation configures current UID/GID, optional `AllowOther`, `FsName=ipns`, `MaxReadAhead`, `IPFS_FUSE_DEBUG`, and `WritableMountCapabilities`. On mount failure after root creation, it closes the root to avoid losing in-memory state. On unmount, root close is attempted even if the low-level unmount returns an error.

## Dependencies, Risks, and Test Signals

Dependencies include coreapi, config, go-fuse, `fuse/mount`, and the IPNS root implementation. Risks include failing to close roots, incorrect cache duration for mutable names, and misconfigured `AllowOther`. Tests mount with the same options, verify persistence, and exercise external unmount via node-level tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/ipns/mount_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mfs/mfs_test.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mfs/mfs_test.go

## Purpose

This file tests the `/mfs` FUSE mount by running the shared writable suite and MFS-specific persistence/stat assertions. It ensures the local mutable file store behaves correctly through FUSE.

## Important APIs, Types, and Functions

`testMount` mounts a root with mutable cache time, max readahead, and writable capabilities. `mfsMount` creates a node, maps `writable.Config` into `config.Mounts`, and returns a mounted `NewFileSystem`. `TestWritableSuite` runs the shared conformance tests. Other tests verify data persistence across remounts, stat block accounting with a configured chunker, symlink stat fields, and statfs reporting.

## Control Flow, State, and Integration

The tests write through FUSE into `ipfs.FilesRoot`, remount against the same node, and read state back. `TestStatBlocks` configures `Import.UnixFSChunker` to `size-65536`, writes multi-block and small files, and asserts POSIX stat fields.

## Dependencies, Risks, and Test Signals

Dependencies include Kubo core/node config, go-fuse, `fusetest`, `fuse/mount`, and `fuse/writable`. Risks covered include attr cache zeros after create, wrong block accounting, missing statfs on macOS, lost MFS state after unmount/remount, and symlink metadata errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mfs/mfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mfs/mfs_unix.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mfs/mfs_unix.go

## Purpose

`mfs_unix.go` constructs the FUSE root for Kubo's mutable file system. It adapts `ipfs.FilesRoot.GetDirectory()` into the shared writable FUSE directory implementation.

## Important APIs, Types, and Functions

`NewFileSystem` returns `writable.NewDir` with `StoreMtime`, `StoreMode`, DAG service, repo path, and preferred block size derived from `Import.UnixFSChunker`.

## Control Flow, State, and Integration

There is no mount lifecycle here; it only builds the root object. Persistent state is Kubo's MFS DAG and repo datastore. The `RepoPath` flows into statfs, and `Blksize` flows into stat fields for tools such as `cp`, `du`, and `rsync`.

## Dependencies, Risks, and Test Signals

Dependencies are config, core, `fuse/mount`, and `fuse/writable`. The major risk is constructing writable roots without a DAG or with stale chunker-derived block size; `writable.NewDir` panics on missing DAG and tests cover block size normalization/stat behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mfs/mfs_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mfs/mount_unix.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mfs/mount_unix.go

## Purpose

This file provides the daemon-facing mount entry point for `/mfs`. It reads repo configuration, creates the MFS FUSE root, and mounts it with writable options.

## Important APIs, Types, and Functions

`mutableCacheTime` is one second. `Mount` reads `ipfs.Repo.Config`, calls `NewFileSystem`, prepares `fs.Options`, and delegates to `fusemnt.NewMount`.

## Control Flow, State, and Integration

The mount uses null permissions, current UID/GID, mutable entry/attr cache, optional `AllowOther`, `FsName=mfs`, `MaxReadAhead`, `IPFS_FUSE_DEBUG`, and `WritableMountCapabilities`. State persists through `ipfs.FilesRoot` and the repo.

## Dependencies, Risks, and Test Signals

Dependencies include go-fuse, config, Kubo core, and `fuse/mount`. Risks are incorrect mount options, missing atomic truncate capability, stale mutable cache behavior, and repo config read failures. MFS tests and node mount tests exercise this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mfs/mount_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/caps.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/caps.go

## Purpose

This file defines FUSE capabilities required by writable mounts. It isolates a kernel-level behavior dependency from MFS/IPNS mount setup.

## Important APIs, Types, and Functions

`WritableMountCapabilities` is `fuse.CAP_ATOMIC_O_TRUNC`. It asks the kernel to deliver `O_TRUNC` as part of `Open` rather than issuing a separate `SETATTR(size=0)` before `Open`.

## Control Flow, State, and Integration

The constant is consumed by `/mfs` and `/ipns` mount options. It has no runtime state but changes kernel-to-userspace request ordering for truncate-open operations.

## Dependencies, Risks, and Test Signals

Dependency is go-fuse's capability constants. Without this capability, MFS can deadlock because `SETATTR` needs a temporary write descriptor before `Open` obtains the intended descriptor. Writable suite tests such as `OpenTrunc`, `VimSavePattern`, and overwrite cases are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/caps.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/errno.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/errno.go

## Purpose

This file normalizes read/write errors into FUSE errno values, with special treatment for cancelled contexts.

## Important APIs, Types, and Functions

`ReadErrno` maps `context.Canceled` and `context.DeadlineExceeded` to `syscall.EINTR`; all other errors go through `fs.ToErrno`.

## Control Flow, State, and Integration

Read handlers in readonly and writable file handles call this after DAG reader operations. It is specifically tied to kernel `FUSE_INTERRUPT` behavior when a userspace process is killed during a blocking syscall.

## Dependencies, Risks, and Test Signals

Dependencies are `context`, `syscall`, and go-fuse. The risk is returning opaque errno values on cancellation, making killed reads appear as unrelated I/O errors or hang symptoms. `TestReadCancellationUnblocks` in readonly tests verifies the EINTR path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/errno.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/fuse.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/fuse.go

## Purpose

`fuse.go` implements the generic `Mount` wrapper around go-fuse server lifecycle. It tracks active state, detects external unmounts, and provides robust unmount fallback.

## Important APIs, Types, and Functions

`ErrNotMounted` signals inactive mounts. The private `mount` type stores mountpoint, `fuse.Server`, active flag, lock, and `sync.Once`. `NewMount` applies platform options, calls `fs.Mount`, starts a goroutine watching `server.Wait`, and returns a `Mount`. `Unmount`, `IsActive`, and `setActive` manage lifecycle state.

## Control Flow, State, and Integration

On normal unmount, `server.Unmount` clears active state. If unmount fails, it calls `ForceUnmountManyTimes`. If the mount is externally unmounted, the `server.Wait` goroutine marks it inactive so later `Unmount` returns `ErrNotMounted`. This wrapper is used by `/ipfs`, `/ipns`, and `/mfs`.

## Dependencies, Risks, and Test Signals

Dependencies are go-fuse, locks, and `fuse/mount` force-unmount helpers. Risks include double unmount races, external unmount state not propagating, and force unmount failures. `fuse/node/mount_test.go` validates external unmount detection for all three mounts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/fuse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/mode.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/mode.go

## Purpose

This file defines shared POSIX modes, FUSE read-ahead size, and CID xattr names used across readonly and writable FUSE filesystems.

## Important APIs, Types, and Functions

Constants include writable defaults `DefaultFileModeRW=0644`, `DefaultDirModeRW=0755`, readonly defaults `DefaultFileModeRO=0444`, `DefaultDirModeRO=0555`, execute-only `NamespaceRootMode=0111`, `SymlinkMode=0777`, `MaxReadAhead=64 MiB`, `XattrCID="ipfs.cid"`, and deprecated `XattrCIDDeprecated="ipfs_cid"`.

## Control Flow, State, and Integration

There is no control flow. The constants are used in attr filling, mount options, xattr handlers, and tests. They form a user-visible filesystem contract.

## Dependencies, Risks, and Test Signals

Dependency is `os.FileMode`. Risks include silently changing permissions, causing `ls`, `find`, or traversal behavior regressions, or breaking tools using old xattr names. FUSE tests check namespace mode, default file/dir modes, symlink mode, and xattr behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/mode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/mount.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/mount.go

## Purpose

This file defines the generic mount abstraction and platform-specific force-unmount command selection used by FUSE lifecycle code.

## Important APIs, Types, and Functions

`Mount` exposes `MountPoint`, `Unmount`, and `IsActive`. `ForceUnmount` tries `umount` first, then a GOOS-specific fallback from `UnmountCmd`. `UnmountCmd` selects `diskutil umount force` on Darwin, `fusermount3 -u` or `fusermount -u` on Linux, and errors elsewhere. `ForceUnmountManyTimes` retries with delay. `Closer` wraps a mount as `io.Closer`.

## Control Flow, State, and Integration

Force unmount runs the command in a goroutine and times out after seven seconds. Multi-retry unmount is used by `fuse.go` after `server.Unmount` fails. The code does not persist state; it invokes host tools.

## Dependencies, Risks, and Test Signals

Dependencies are `os/exec`, `runtime`, and system unmount helpers. Risks include missing helper binaries, unsupported FreeBSD fallback despite build support elsewhere, command hangs, and error string differences. Node external-unmount tests call `UnmountCmd` directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/opts_darwin.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/opts_darwin.go

## Purpose

This Darwin-specific file adjusts macFUSE mount options to improve Finder presentation and avoid Apple metadata side effects.

## Important APIs, Types, and Functions

`PlatformMountOpts` appends `volname=<FsName>` when available, plus `noapplexattr` and `noappledouble`.

## Control Flow, State, and Integration

The function mutates `fuse.MountOptions` before `fs.Mount`. It is called by `NewMount` for every Kubo FUSE mount on macOS.

## Dependencies, Risks, and Test Signals

Dependency is go-fuse mount options. The risk is macFUSE option drift or disabling useful Finder metadata unexpectedly. The intended signal is reduced ENOATTR chatter and avoidance of `._` sidecar files; platform-specific manual and integration testing are most relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/opts_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/opts_other.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/opts_other.go

## Purpose

This file provides the Linux/FreeBSD implementation of platform mount option adjustment.

## Important APIs, Types, and Functions

`PlatformMountOpts` is a no-op for `fuse.MountOptions`.

## Control Flow, State, and Integration

It is called by `NewMount`, preserving a common call site while avoiding Darwin-only options on other platforms.

## Dependencies, Risks, and Test Signals

Dependency is go-fuse types only. The main risk is missing future platform-specific options for Linux/FreeBSD. Existing FUSE tests implicitly confirm the no-op does not break mount setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/opts_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/stat.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/stat.go

## Purpose

This file provides stat-related constants and helpers shared by FUSE filesystems. It anchors Kubo's visible `st_blocks` and `st_blksize` behavior.

## Important APIs, Types, and Functions

`StatBlockSize` is 512 bytes, matching POSIX `st_blocks`. `DefaultBlksize` is 1 MiB. `SizeToStatBlocks` rounds byte sizes up to 512-byte units. `BlksizeFromChunker` extracts sizes from `size-<bytes>` chunker strings, falls back for variable/malformed chunkers, and clamps values to `fuse.MAX_KERNEL_WRITE`.

## Control Flow, State, and Integration

Readonly and writable attr fillers use these helpers for files, directories, and symlinks. MFS/IPNS mount setup derives writable block size from import config.

## Dependencies, Risks, and Test Signals

Dependencies are string parsing and go-fuse's kernel write limit. Risks include breaking `du`/`ls -s` semantics, advertising oversized buffers, or drifting from CID-deterministic defaults. `stat_test.go`, readonly tests, and MFS tests cover rounding, fallback, clamping, and per-entry stat fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/stat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/stat_test.go -->
# sources/distributed-fs/ipfs-kubo/fuse/mount/stat_test.go

## Purpose

This test file pins the stat helper behavior used by all FUSE mounts.

## Important APIs, Types, and Functions

`TestDefaultBlksizeAnchor` asserts `DefaultBlksize` remains 1 MiB. `TestBlksizeFromChunker` covers default and custom size chunkers, variable chunkers, malformed inputs, zero sizes, and values above `fuse.MAX_KERNEL_WRITE`.

## Control Flow, State, and Integration

The tests are table-driven and have no persistent state. They protect values that affect FUSE-visible stat output and IO buffer sizing.

## Dependencies, Risks, and Test Signals

Dependency is go-fuse's max kernel write constant. Failures indicate a user-visible stat contract change or parser regression that would ripple into `/ipfs`, `/mfs`, and `/ipns`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/mount/stat_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_darwin.go -->
# sources/distributed-fs/ipfs-kubo/fuse/node/mount_darwin.go

## Purpose

This Darwin-specific file installs a pre-mount check for macFUSE/OSXFUSE helper binaries.

## Important APIs, Types, and Functions

`init` assigns `platformFuseChecks = darwinFuseCheck`. `macFUSEPaths` lists known mount helper locations. `darwinFuseCheck` returns nil if any helper exists and otherwise returns a multi-line installation error.

## Control Flow, State, and Integration

The check runs before node-level mount orchestration. It does not mount or persist anything; it fails early with actionable guidance.

## Dependencies, Risks, and Test Signals

Dependencies are `os.Stat`, Kubo core types, and current macFUSE installation paths. Risks include path changes or installed but unusable macFUSE. macOS FUSE integration tests and user mount attempts are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_nofuse.go -->
# sources/distributed-fs/ipfs-kubo/fuse/node/mount_nofuse.go

## Purpose

This build-tagged stub makes Kubo compile with `nofuse` on non-Windows platforms while returning a clear runtime error for mount requests.

## Important APIs, Types, and Functions

`Mount` returns `errors.New("not compiled in")`; `Unmount` is a no-op.

## Control Flow, State, and Integration

No state is created. This file replaces the real FUSE implementation under `!windows && nofuse`.

## Dependencies, Risks, and Test Signals

Dependencies are minimal. The risk is callers not surfacing the error clearly. Build-tag CI or manual `go build -tags nofuse` verifies this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_nofuse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_notsupp.go -->
# sources/distributed-fs/ipfs-kubo/fuse/node/mount_notsupp.go

## Purpose

This stub provides a runtime error for platforms where go-fuse does not compile but the build did not explicitly disable FUSE.

## Important APIs, Types, and Functions

`Mount` returns an error explaining FUSE is unsupported on OpenBSD or NetBSD and references issue #5334. `Unmount` is a no-op.

## Control Flow, State, and Integration

It applies to OpenBSD, NetBSD, and Plan 9 without `nofuse`, preventing build failures and giving users an explanatory error.

## Dependencies, Risks, and Test Signals

Dependencies are only `errors` and Kubo core type signatures. The wording is slightly narrower than the build tag because it mentions OpenBSD/NetBSD but not Plan 9. Cross-platform builds are the main validation signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_notsupp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_test.go -->
# sources/distributed-fs/ipfs-kubo/fuse/node/mount_test.go

## Purpose

This file tests node-level mount orchestration, especially detection of external unmounts for `/ipfs`, `/ipns`, and `/mfs`.

## Important APIs, Types, and Functions

`mkdir` creates mount directories. `TestExternalUnmount` mounts all three filesystems, invokes the platform unmount command externally, waits briefly, then asserts `IsActive` is false and `Unmount` returns `mount.ErrNotMounted`. `setupAllMounts` creates an online mock node, initializes IPNS keyspace, creates temp mountpoints, mounts all filesystems, and registers cleanup.

## Control Flow, State, and Integration

The test exercises `node.Mount`, individual mount implementations, and the `fuse/mount` goroutine that watches `fuse.Server.Wait`. State is real FUSE kernel mount state plus node `Mounts` fields.

## Dependencies, Risks, and Test Signals

Dependencies include FUSE availability, mock core nodes, IPNS initialization, and system unmount commands. Risks are timing sensitivity after external unmount and environment-specific helper behavior. Passing tests confirm active-state reconciliation and idempotent cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_unix.go -->
# sources/distributed-fs/ipfs-kubo/fuse/node/mount_unix.go

## Purpose

`mount_unix.go` orchestrates mounting and unmounting all supported Kubo FUSE filesystems: read-only `/ipfs`, writable `/ipns`, and writable `/mfs`.

## Important APIs, Types, and Functions

`platformFuseChecks` is overridable by OS-specific files. `Mount` first unmounts live mounts, runs platform checks, then calls `doMount`. `Unmount` best-effort unmounts active entries in `node.Mounts`. `doMount` mounts `/ipfs`, `/ipns` when the node is online, and `/mfs` concurrently, normalizes common fusermount errors, rolls back partial success, and stores mount handles on the node.

## Control Flow, State, and Integration

Mounts are attempted in parallel using `sync.WaitGroup`. If any mount fails, successful mounts are immediately unmounted and the first relevant error is returned. Node state is updated only after all required mounts succeed. Offline nodes skip `/ipns`.

## Dependencies, Risks, and Test Signals

Dependencies are Kubo core, `fuse/readonly`, `fuse/ipns`, `fuse/mfs`, and `fuse/mount`. Risks include partial mount cleanup failures, concurrent mount ordering, brittle fusermount error strings, and nil `Ipns` mount for offline nodes. Node tests verify external unmount state, and CLI FUSE tests exercise daemon integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_windows.go -->
# sources/distributed-fs/ipfs-kubo/fuse/node/mount_windows.go

## Purpose

This Windows stub makes the node mount API compile while reporting that FUSE-style mounting is unsupported.

## Important APIs, Types, and Functions

`Mount` returns `errors.New("not implemented")`; `Unmount` is a no-op.

## Control Flow, State, and Integration

No state is mutated. It preserves API shape across platforms.

## Dependencies, Risks, and Test Signals

Dependency is just Kubo core type signatures. The risk is user-facing command paths needing clearer Windows guidance. Windows builds validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/node/mount_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/readonly/doc.go -->
# sources/distributed-fs/ipfs-kubo/fuse/readonly/doc.go

## Purpose

This package doc identifies `fuse/readonly` as the FUSE filesystem for accessing files stored in IPFS.

## Important APIs, Types, and Functions

The file contains only the package declaration and doc comment. The implementation lives in `readonly_unix.go` and mount setup in `mount_unix.go`.

## Control Flow, State, and Integration

There is no executable flow or state.

## Dependencies, Risks, and Test Signals

The risk is documentation drift if the package grows beyond read-only `/ipfs`. Package-level docs are indirectly checked by Go doc generation and normal package builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/readonly/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/readonly/ipfs_test.go -->
# sources/distributed-fs/ipfs-kubo/fuse/readonly/ipfs_test.go

## Purpose

This file tests the read-only `/ipfs` FUSE implementation directly, covering CID lookup, UnixFS directory traversal, raw leaves, metadata, symlinks, xattrs, stat fields, read cancellation, and concurrency.

## Important APIs, Types, and Functions

`testMount` mounts readonly roots with immutable cache settings. `randObj` builds random trickle DAGs. `setupIpfsTest` creates a mock node and mounts `NewRoot`. Tests cover empty directories, bare CIDv0/CIDv1 reads, mixed dag-pb/raw directories, basic file and directory reads, stress reads, file size reporting, UnixFS metadata, default modes, CID xattrs, symlink readlink/readdir, seek reads, concurrent large-file reads, cancellation through `blockingDagReader`, stat blocks, statfs, and unknown xattrs.

## Control Flow, State, and Integration

Tests construct DAG nodes in a mock node's blockstore, then access them through normal filesystem operations under the FUSE mount. The cancellation test bypasses mounting and directly invokes `roFileHandle.Read` with a fake blocking reader.

## Dependencies, Risks, and Test Signals

Dependencies include coremock, CoreAPI, boxo UnixFS importer/io, go-fuse, and fusetest. The tests guard high-risk areas: raw leaf decoding, stable inode types, kernel attr caching, concurrent readahead against non-thread-safe DagReaders, cancellation-to-EINTR mapping, and POSIX stat/xattr behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/readonly/ipfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/readonly/mount_unix.go -->
# sources/distributed-fs/ipfs-kubo/fuse/readonly/mount_unix.go

## Purpose

This file is the daemon-facing mount entry point for read-only `/ipfs`.

## Important APIs, Types, and Functions

`Mount` reads repo config, constructs `NewRoot`, fills `fs.Options` with current UID/GID, immutable attr/entry timeout, `AllowOther`, `FsName=ipfs`, `MaxReadAhead`, and `IPFS_FUSE_DEBUG`, then calls `fusemnt.NewMount`.

## Control Flow, State, and Integration

The function creates no content state; it exposes existing blockstore/DAG content through a FUSE root. Mount state is managed by the returned `fuse/mount.Mount`.

## Dependencies, Risks, and Test Signals

Dependencies are go-fuse, config, Kubo core, and `fuse/mount`. Risks include bad `AllowOther`, excessive immutable cache if mutable paths slip into `/ipfs`, and missing repo config. Readonly and node mount tests exercise the path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/readonly/mount_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/readonly/readonly_unix.go -->
# sources/distributed-fs/ipfs-kubo/fuse/readonly/readonly_unix.go

## Purpose

`readonly_unix.go` implements the read-only `/ipfs` FUSE filesystem. It maps immutable `/ipfs/<cid>/<path>` names to UnixFS DAG nodes and exposes files, directories, symlinks, stat fields, and CID xattrs.

## Important APIs, Types, and Functions

`Root` stores the node and repo path. `Root.Lookup` parses immutable paths, resolves with `UnixFSPathResolver`, decodes raw or dag-pb blocks, fills entry attrs, and returns `Node`. `Root.Statfs`, `Getattr`, and `Readdir` handle namespace behavior. `Node` wraps an IPLD node and lazily caches `unixfs.FSNode`. `Node.Open` returns a serialized `roFileHandle` with a DagReader. `fillAttr`, `Lookup`, `Readdir`, `Listxattr`, `Getxattr`, `Readlink`, `roFileHandle.Read`, `Release`, and `stableAttrFor` implement the FUSE contracts.

## Control Flow, State, and Integration

Lookups traverse immutable CIDs and child links, readdir fetches child nodes to infer file types, opens create per-handle DagReaders, and reads seek to the requested offset before context-aware reads. Kernel cache time is set to one year because `/ipfs` paths are content-addressed. Persistent state is only the underlying blockstore/DAG; this filesystem does not mutate it.

## Dependencies, Risks, and Test Signals

Dependencies include go-fuse, boxo UnixFS, merkledag, DAG reader, Kubo core resolvers/blockstore, CID links, and shared mount helpers. Risks include unsupported codecs, not-found handling, non-thread-safe DagReader access, stale attr fill causing zero-mode cache, expensive readdir child fetches, and large immutable cache for malformed names. The readonly test file covers raw leaves, symlinks, xattrs, stat fields, concurrent reads, and cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/readonly/readonly_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/writable/writable.go -->
# sources/distributed-fs/ipfs-kubo/fuse/writable/writable.go

## Purpose

This file implements the shared writable FUSE adapter for MFS-backed mounts. `/mfs` and local `/ipns` directories use it to expose MFS directories, files, and UnixFS symlinks as POSIX-like writable filesystems.

## Important APIs, Types, and Functions

`Config` controls metadata persistence, DAG access, repo statfs path, and block-size hints. `NewDir` validates the DAG and normalizes block size. `Dir` implements getattr/statfs/setattr/lookup/readdir/mkdir/unlink/rmdir/rename/create/xattr/symlink. `FileInode` implements getattr/open/setattr/xattr. `FileHandle` serializes read/write/flush/release/fsync around an MFS descriptor. `Symlink` implements readlink/getattr/setattr. `roFileHandle` provides snapshot reads via DagReader. `SymlinkTarget` detects UnixFS symlink nodes represented as MFS files.

## Control Flow, State, and Integration

Directory operations delegate to boxo MFS, then flush where needed. `Rename` unlinks before add and is explicitly non-atomic. `Create` adds an empty UnixFS file, opens an MFS descriptor, and fills attrs to avoid kernel zero caching. Read-only opens bypass MFS's descriptor lock by creating a DagReader from the current DAG node; write opens use MFS descriptors and handle `O_TRUNC` and `O_APPEND`. Flush, release, and fsync invalidate go-fuse kernel caches. Metadata writes persist UnixFS optional mode/mtime when configured.

## Dependencies, Risks, and Test Signals

Dependencies include go-fuse, boxo MFS, UnixFS DAG helpers, Kubo mount constants, and IPLD DAG services. Risks include non-atomic rename data loss on mid-operation failure, deadlocks if read-only opens use MFS locks, stale kernel caches after writes, sparse write semantics, symlink metadata limitations, StoreMode dropping high permission bits, and statfs path errors. The shared writable suite plus writable unit tests cover these risks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/writable/writable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/writable/writable_test.go -->
# sources/distributed-fs/ipfs-kubo/fuse/writable/writable_test.go

## Purpose

This file contains focused unit tests for writable FUSE helpers that do not require full kernel-level flows.

## Important APIs, Types, and Functions

`TestNewDirNormalizesBlksize` verifies zero block size falls back to `DefaultBlksize` and explicit values pass through. `TestSymlinkSetattrChmodNoError` verifies symlink chmod-like setattr requests succeed without storing permissions. `TestStatfsReportsSpace` verifies statfs proxies repo filesystem data and handles empty repo paths.

## Control Flow, State, and Integration

The tests instantiate `Config`, `Dir`, and `Symlink` directly, avoiding FUSE mounts except for go-fuse structs. They validate behavior that may not be forwarded by Linux VFS in normal integration tests.

## Dependencies, Risks, and Test Signals

Dependencies include go-fuse structs, merkledag DAG service stubs, and shared mount constants. Failures signal regressions in block-size defaults, symlink POSIX compatibility, or Finder-facing statfs behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/fuse/writable/writable_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/gc/gc.go -->
# sources/distributed-fs/ipfs-kubo/gc/gc.go

## Purpose

`gc.go` implements Kubo block garbage collection. It computes a colored set of blocks reachable from pins and best-effort roots, then sweeps unmarked blocks from the GC blockstore and optionally asks the datastore to collect its own garbage.

## Important APIs, Types, and Functions

`Result` carries either a removed CID or an error. `toRawCids` normalizes marked CIDs to raw CIDv1 by multihash. `GC` locks the blockstore, builds a DAG service, calls `ColoredSet`, iterates `AllKeysChan`, deletes unmarked blocks, emits incremental results, and invokes `dstore.GCDatastore.CollectGarbage` when available. `Descendants` validates CIDs and walks DAGs from streamed pins. `ColoredSet` marks recursive pins, best-effort roots, direct pins, and internal pins. Error types include `CannotFetchLinksError` and `CannotDeleteBlockError`.

## Control Flow, State, and Integration

GC runs asynchronously and returns a channel. It uses context cancellation to stop work and unlocks the blockstore in a deferred cleanup. Missing best-effort root links are tolerated only when they are not found; other traversal errors abort marking. Delete errors are non-fatal per block but cause a final `ErrCannotDeleteSomeBlocks`. Persistent state changes are block deletions and optional datastore compaction.

## Dependencies, Risks, and Test Signals

Dependencies are boxo blockstore/blockservice/offline exchange/merkledag/pinner, datastore GC, cid sets, verifcid, and IPLD traversal. Risks include high memory use for the colored set, CID codec normalization assumptions, aborting on insecure hash validation, partial delete failures, and best-effort root semantics. `gc_test.go` verifies pinned and best-effort DAGs are kept while unpinned DAGs are removed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/gc/gc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/gc/gc_test.go -->
# sources/distributed-fs/ipfs-kubo/gc/gc_test.go

## Purpose

This test validates the mark-and-sweep behavior of `GC` against direct pins, recursive pins, best-effort roots, and unpinned DAGs.

## Important APIs, Types, and Functions

`TestGC` constructs an in-memory datastore, GC blockstore, DAG service, datastore-backed pinner, and DAG generator. It pins direct and recursive DAGs, adds unpinned DAGs, adds best-effort root DAGs, runs `GC`, and compares removed/kept multihashes. `toMHs` maps CIDs to multihashes for codec-insensitive comparison.

## Control Flow, State, and Integration

The test creates known DAG sets, tracks expected kept and discarded hashes, drains the GC result channel while requiring no errors, then enumerates remaining blockstore keys.

## Dependencies, Risks, and Test Signals

Dependencies include boxo blockstore, merkledag test utilities, dspinner pinner, and testify. The test does not cover delete failure, traversal failure, context cancellation, or datastore compaction errors, but it strongly signals the main mark/sweep contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/gc/gc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/internal/fusemount/context.go -->
# sources/distributed-fs/ipfs-kubo/internal/fusemount/context.go

## Purpose

This internal package provides a context marker that allows the IPNS FUSE mount's own republishing path to bypass manual-publish guards in the Name API.

## Important APIs, Types, and Functions

`publishKey` is an unexported context key. `ContextWithPublish` returns a context carrying the marker. `IsPublish` checks whether the marker is present.

## Control Flow, State, and Integration

The marker is process-local context state only; it is not persisted. `fuse/ipns` uses it inside the MFS publish function before calling `Name().Publish`, while core API guard code can distinguish mount-internal publishes from user-initiated publishes.

## Dependencies, Risks, and Test Signals

Dependency is the standard `context` package. Risks include over-broad bypass if misused and a documented unresolved conflict: external `ipfs name publish` for a mounted local key can be overwritten on next mount flush. IPNS persistence tests exercise the intended bypass path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/internal/fusemount/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/fsutil/fsutil.go -->
# sources/distributed-fs/ipfs-kubo/misc/fsutil/fsutil.go

## Purpose

This utility package provides small filesystem helpers for repo/plugin code, especially writable-directory validation and home-directory expansion.

## Important APIs, Types, and Functions

`DirWritable` expands `~`, creates a missing directory with `0775`, rejects non-directories, and verifies writability by creating/removing a temp file. `ExpandHome` expands `~` or `~/...`/`~\...` using `os.UserHomeDir` and rejects `~user` syntax. `FileExists` uses `os.Lstat` and returns false only for not-exist errors.

## Control Flow, State, and Integration

`DirWritable` may persist state by creating the target directory and a temporary probe file. It is used by the Pebble datastore plugin before opening the datastore path.

## Dependencies, Risks, and Test Signals

Dependencies are standard `os`, `io/fs`, and `filepath`. Risks include non-atomic writability probes, permission differences across platforms, and `FileExists` treating non-permission errors as existence. Tests cover empty paths, bad home expansion, directory creation, read-only directories on non-Windows, file existence, and home env behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/fsutil/fsutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/fsutil/fsutil_test.go -->
# sources/distributed-fs/ipfs-kubo/misc/fsutil/fsutil_test.go

## Purpose

This file tests the filesystem utility helpers used by datastore and repo-adjacent code.

## Important APIs, Types, and Functions

`TestDirWritable` covers empty input, unsupported `~user`, creation of missing directories, repeated success, and read-only directory failures outside Windows. `TestFileExists` checks nonexistent and created files. `TestExpandHome` covers empty paths, non-home paths, `~user` rejection, home env expansion, and missing home env errors.

## Control Flow, State, and Integration

Tests use temporary directories and manipulate `HOME` or `USERPROFILE` with restoration. They skip read-only permission checks on Windows.

## Dependencies, Risks, and Test Signals

Dependencies are `runtime`, `os`, `filepath`, and testify. The tests signal regressions in path expansion and permission error normalization that could break datastore setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/fsutil/fsutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/launchd/install.sh -->
# sources/distributed-fs/ipfs-kubo/misc/launchd/install.sh

## Purpose

This shell script installs and loads a macOS launchd plist for running the IPFS daemon.

## Important APIs, Types, and Functions

The script derives its source directory, sets `plist=io.ipfs.ipfs-daemon.plist`, chooses `$HOME/Library/LaunchAgents`, defaults `IPFS_PATH` to `$HOME/.ipfs`, resolves `ipfs` binary path with `which`, substitutes `{{IPFS_PATH}}` and `{{IPFS_BIN}}` into the plist via `sed`, unloads an existing job, and loads or bootstraps based on macOS version.

## Control Flow, State, and Integration

It writes the generated plist into the user's LaunchAgents directory and invokes `launchctl`. For newer macOS versions it changes ownership to root and bootstraps into the system domain.

## Dependencies, Risks, and Test Signals

Dependencies are bash, sed, `which`, `launchctl`, `sw_vers`, and sudo for newer systems. Risks include weak quoting around paths, questionable `if [ $? ]` logic that is always true for non-empty status strings, version parsing assumptions, and root ownership of a user LaunchAgents path. Manual macOS install testing is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/launchd/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-api.socket -->
# sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-api.socket

## Purpose

This systemd socket unit provides socket activation for the Kubo API listener.

## Important APIs, Types, and Functions

The unit sets `Service=ipfs.service`, `FileDescriptorName=io.ipfs.api`, `BindIPv6Only=true`, and listens on `127.0.0.1:5001` and `[::1]:5001`.

## Control Flow, State, and Integration

When enabled, systemd owns the API socket and passes it to `ipfs.service`, overriding API listeners configured in Kubo config. It installs under `sockets.target`.

## Dependencies, Risks, and Test Signals

Dependencies are systemd socket activation support and Kubo service code recognizing `io.ipfs.api`. Risks include surprising config override and port conflicts. Validation is `systemctl enable --now ipfs-api.socket` plus checking daemon API fd adoption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-api.socket -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-gateway.socket -->
# sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-gateway.socket

## Purpose

This systemd socket unit provides socket activation for the Kubo gateway listener.

## Important APIs, Types, and Functions

The unit sets `Service=ipfs.service`, `FileDescriptorName=io.ipfs.gateway`, `BindIPv6Only=true`, and listens on `127.0.0.1:8080` and `[::1]:8080`.

## Control Flow, State, and Integration

Enabling it lets systemd bind gateway sockets and pass descriptors to `ipfs.service`, completely overriding configured gateway listeners. It is wanted by `sockets.target`.

## Dependencies, Risks, and Test Signals

Dependencies are systemd and daemon socket activation support. Risks are hidden listener override, local port conflicts, and IPv4/IPv6 binding nuances. Runtime validation should check gateway availability and descriptor name handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-gateway.socket -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-hardened.service -->
# sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-hardened.service

## Purpose

This systemd service unit runs Kubo with a broad set of hardening directives for installations that do not need FUSE mounting.

## Important APIs, Types, and Functions

The unit configures `ReadWritePaths=/var/lib/ipfs/`, `ProtectSystem=strict`, private devices/tmp, restricted namespaces/realtime/SUID, syscall filters, address family limits, `CapabilityBoundingSet=CAP_NET_BIND_SERVICE`, `MemorySwapMax=0`, infinite startup timeout, `Type=notify`, `User/Group=ipfs`, `StateDirectory=ipfs`, `IPFS_PATH="${HOME}"`, `ExecStart=/usr/local/bin/ipfs daemon --init --migrate`, restart on failure, and SIGINT shutdown.

## Control Flow, State, and Integration

systemd creates/manages state under `/var/lib/ipfs`, starts the daemon with init/migration, and expects sd-notify readiness. Hardening blocks device access and FUSE-related functionality by design.

## Dependencies, Risks, and Test Signals

Dependencies are systemd features, an `ipfs` system user/group, and Kubo notify support. Risks include hardening directives unsupported by older systemd, FUSE breakage, `HOME` semantics under `StateDirectory`, and too-restrictive paths for custom repos. Validation is daemon startup, migration, restart behavior, and confirming forbidden FUSE paths are acceptable for this unit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-hardened.service -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-sysusers.conf -->
# sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-sysusers.conf

## Purpose

This sysusers configuration declares the system user and group used by the systemd Kubo service units.

## Important APIs, Types, and Functions

It creates user `ipfs` with description `IPFS daemon` and home `/var/lib/ipfs`, creates group `ipfs`, and adds user `ipfs` to group `ipfs`.

## Control Flow, State, and Integration

systemd-sysusers consumes this file during package install or boot, persisting `/etc/passwd`/group database entries through the platform's sysusers mechanism.

## Dependencies, Risks, and Test Signals

Dependencies are systemd-sysusers. Risks include conflicts with pre-existing users/groups or packaging systems that manage users differently. Validation is `systemd-sysusers --dry-run` and service startup under the created account.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs-sysusers.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs.service -->
# sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs.service

## Purpose

This is the standard systemd service unit for running the Kubo daemon with fewer hardening restrictions than the hardened variant.

## Important APIs, Types, and Functions

It declares `After=network.target`, optional commented capability/env/NOFILE settings, `MemorySwapMax=0`, infinite startup timeout, `Type=notify`, `User=ipfs`, `Group=ipfs`, `StateDirectory=ipfs`, `Environment=IPFS_PATH="${HOME}"`, `ExecStart=/usr/local/bin/ipfs daemon --init --migrate`, restart on failure, and SIGINT shutdown.

## Control Flow, State, and Integration

systemd creates/manages the state directory, launches the daemon, waits for notify readiness, and restarts on failure. Comments document drop-in override mechanics.

## Dependencies, Risks, and Test Signals

Dependencies are systemd notify support, the `ipfs` user/group, and binary path `/usr/local/bin/ipfs`. Risks include custom repo paths requiring drop-ins, low file descriptor defaults, and infinite startup masking hangs. Validation checks daemon startup, readiness notification, migrations, restart, and compatibility with optional socket units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/misc/systemd/ipfs.service -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/footer.mk -->
# sources/distributed-fs/ipfs-kubo/mk/footer.mk

## Purpose

This makefile fragment restores directory-tracking variables for Kubo's recursive make include pattern.

## Important APIs, Types, and Functions

It sets `d := $(dirstack_$(sp))` and `sp := $(basename $(sp))`.

## Control Flow, State, and Integration

Included at the end of nested make fragments, it unwinds the `d` and `sp` state established by `header.mk`.

## Dependencies, Risks, and Test Signals

Dependency is GNU Make variable expansion. Risks are include-order errors and corrupted directory context for subsequent fragments. Build targets depending on nested `Rules.mk` files validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/footer.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/git.mk -->
# sources/distributed-fs/ipfs-kubo/mk/git.mk

## Purpose

This makefile fragment derives Git metadata for builds, including commit description, release tag, and normalized origin.

## Important APIs, Types, and Functions

`git-hash` uses `git describe --always --match=NeVeRmAtCh --dirty` with fallback to `git rev-parse --short HEAD`. `git-tag` is set only for clean HEADs with a `v*` tag. `git-origin` normalizes ssh/https origin URLs into `host/org/repo` and strips `.git` and userinfo.

## Control Flow, State, and Integration

The variables are evaluated by Make shell calls and feed version/user-agent/fork detection logic elsewhere in the build.

## Dependencies, Risks, and Test Signals

Dependencies are Git, sed, grep, and shell behavior. Risks include missing Git metadata in tarballs or containers, dirty tree detection differences, and URL normalization edge cases. Build/version tests and release builds are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/git.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/golang.mk -->
# sources/distributed-fs/ipfs-kubo/mk/golang.mk

## Purpose

This fragment defines Go build/test helpers and major Kubo test targets.

## Important APIs, Types, and Functions

It enables modules, defines `GOCC`, `GOTAGS`, `GOTFLAGS`, `GOFLAGS=-trimpath`, `GOPATH`, package-name helpers, build macros, coverage exclusions, `test_unit`, `test_cli`, FUSE test targets, `test_examples`, platform build check, formatting, and lint targets. It also aggregates `TEST_GO`, `TEST`, and `TEST_SHORT`.

## Control Flow, State, and Integration

Targets call `go list`, `go build`, `gotestsum`, Kubo CLI integration tests, FUSE tests with `TEST_FUSE=1`, and example module replacement tests. In tarball mode it adds `-mod=vendor`.

## Dependencies, Risks, and Test Signals

Dependencies are GNU Make, Go toolchain, gotestsum, golangci-lint, Kubo test binaries, FUSE environment, and shell utilities. Risks include regex exclusions hiding packages, test timeouts too short or long, local `GOFLAGS` pollution, and module replacement cleanup in `test_examples`. CI test targets are the primary validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/golang.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/header.mk -->
# sources/distributed-fs/ipfs-kubo/mk/header.mk

## Purpose

This makefile fragment saves recursive make directory context before entering an included subdirectory rules file.

## Important APIs, Types, and Functions

It computes `p := $(sp).x`, stores `dirstack_$(sp) := $(d)`, and sets `d := $(dir)`.

## Control Flow, State, and Integration

Included at the beginning of make fragments, it pushes directory state that `footer.mk` later restores.

## Dependencies, Risks, and Test Signals

Dependency is GNU Make. Risks include incorrect `sp` or `dir` values causing targets to be generated under the wrong path. Any recursive build using `Rules.mk` validates this convention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/header.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/tarball.mk -->
# sources/distributed-fs/ipfs-kubo/mk/tarball.mk

## Purpose

This fragment configures behavior for source tarball builds and exposes tarball creation targets.

## Important APIs, Types, and Functions

It sets `tarball-is` based on `.tarball`, overrides `git-hash` from that file in tarball mode, defines `GOCC`, and provides `go-ipfs-source.tar.gz` and `kubo-source.tar.gz` targets that depend on `distclean` and run `bin/maketarball.sh`.

## Control Flow, State, and Integration

When `.tarball` exists, other Go build settings use vendor mode and fixed version metadata. Tarball targets produce release archives after cleaning.

## Dependencies, Risks, and Test Signals

Dependencies are GNU Make, Go, and `bin/maketarball.sh`. Risks include stale `.tarball` metadata and destructive expectations from `distclean`. Release packaging jobs validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/tarball.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/util.mk -->
# sources/distributed-fs/ipfs-kubo/mk/util.mk

## Purpose

This fragment defines cross-platform Make utility variables.

## Important APIs, Types, and Functions

It detects `OS`, sets `WINDOWS`, executable suffix `?exe`, and `PATH_SEP`. It also notes that build platforms now live in `.github/build-platforms.yml`.

## Control Flow, State, and Integration

The variables are consumed by other Make fragments to build executable names and PATH values portably.

## Dependencies, Risks, and Test Signals

Dependencies are shell `uname` and GNU Make conditionals. Risks include ambiguous `?exe` variable naming and incorrect Windows detection outside native Windows Make. Cross-platform build checks validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/mk/util.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/listener.go -->
# sources/distributed-fs/ipfs-kubo/p2p/listener.go

## Purpose

This file defines listener abstractions and registries for Kubo's libp2p stream forwarding feature.

## Important APIs, Types, and Functions

`Listener` exposes protocol, listen/target addresses, close, done channel, and an internal key. `Listeners` stores protocol-keyed listeners under an RWMutex. `newListenersLocal` creates a local registry. `newListenersP2P` registers a libp2p stream handler match for protocols present in the registry and dispatches incoming streams to `remoteListener.handleStream`. `Register` rejects duplicate keys. `Close` removes matching listeners and closes them outside the lock.

## Control Flow, State, and Integration

The registry is mutable in memory only. Local listeners key by local bind address string; remote listeners key by protocol. The P2P registry integrates with `host.SetStreamHandlerMatch` so active registrations dynamically control accepted libp2p protocols.

## Dependencies, Risks, and Test Signals

Dependencies are libp2p host/network/protocol and multiaddr. Risks include type assertion to `*remoteListener`, protocol key collisions, and handlers observing registry changes concurrently. P2P command/integration tests should validate duplicate listener errors and stream dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/listener.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/local.go -->
# sources/distributed-fs/ipfs-kubo/p2p/local.go

## Purpose

`local.go` implements local forwarding: a local manet listener accepts local connections and opens libp2p streams to a remote peer/protocol.

## Important APIs, Types, and Functions

`localListener` stores context, parent `P2P`, protocol, listen address, remote peer, manet listener, and done channel. `ForwardLocal` listens on a multiaddr, registers the listener, and starts accept loop. `dial` opens a libp2p stream with a 30-second timeout. `acceptConns` handles temporary accept errors. `setupStream` creates a `Stream` binding local connection to remote stream and registers it.

## Control Flow, State, and Integration

Each accepted local connection spawns a goroutine that dials the remote peer and then starts bidirectional copying through `StreamRegistry`. `close` closes the local listener and done channel. Listener state is in-memory and removed through registry close operations.

## Dependencies, Risks, and Test Signals

Dependencies are libp2p network/peer/protocol, multiaddr net, and temp error catcher. Risks include accept loop not closing `done` on natural errors, hard-coded dial timeout, and local sockets closed on dial failure. Integration tests should confirm local TCP/Unix forwarding and cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/p2p.go -->
# sources/distributed-fs/ipfs-kubo/p2p/p2p.go

## Purpose

This file defines the top-level P2P forwarding manager that owns listener registries and active stream tracking.

## Important APIs, Types, and Functions

`P2P` contains local listener registry, remote/libp2p listener registry, stream registry, identity, peer host, and peerstore. `New` initializes these and wires the stream registry to the host connection manager. `CheckProtoExists` checks whether a protocol is registered in the host muxer.

## Control Flow, State, and Integration

The manager is in-memory runtime state owned by a Kubo node. It coordinates CLI/API P2P listener creation with libp2p host stream handlers and active stream connection-manager tags.

## Dependencies, Risks, and Test Signals

Dependencies are go-log, libp2p host/peerstore/protocol. Risks include stale registries if callers do not close listeners and mux protocol checks racing with handler changes. P2P API integration tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/p2p.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/remote.go -->
# sources/distributed-fs/ipfs-kubo/p2p/remote.go

## Purpose

`remote.go` implements remote forwarding: incoming libp2p streams for a protocol are proxied to a local multiaddr service.

## Important APIs, Types, and Functions

`remoteListener` stores parent `P2P`, protocol, target address, `reportRemote`, and done channel. `ForwardRemote` registers it. `handleStream` dials the local target, optionally writes the remote peer ID line first, creates origin `/ipfs/<peer>` multiaddr, and registers a bidirectional `Stream`. Address methods expose listen and target addresses, and `key` returns the protocol.

## Control Flow, State, and Integration

The libp2p stream handler from `listener.go` invokes `handleStream`. Dial failures or peer multiaddr construction failures reset the remote stream. Successful streams are tracked by `StreamRegistry`.

## Dependencies, Risks, and Test Signals

Dependencies are libp2p network/protocol, multiaddr, and manet. Risks include local target dial failures, `reportRemote` protocol compatibility, and remote listener `close` not unregistering host handlers directly but relying on registry removal. Integration tests should verify service exposure and remote peer reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/remote.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/stream.go -->
# sources/distributed-fs/ipfs-kubo/p2p/stream.go

## Purpose

This file tracks active P2P forwarding streams and copies bytes bidirectionally between local manet connections and libp2p streams.

## Important APIs, Types, and Functions

`Stream` records ID, protocol, origin/target addresses, peer, local connection, remote stream, and registry. `startStreaming` launches two `io.Copy` goroutines. `StreamRegistry` stores streams, per-peer connection counts, next ID, and libp2p connection manager. `Register`, `Deregister`, `Close`, and `Reset` manage lifecycle and connection-manager tags.

## Control Flow, State, and Integration

Register tags the peer with `stream-fwd`, increments counts, assigns an ID, stores the stream, and starts copying. Either copy direction closes or resets both endpoints and deregisters. Untagging occurs when the last stream for a peer is removed.

## Dependencies, Risks, and Test Signals

Dependencies are `io`, mutexes, libp2p connmgr/network/peer/protocol, and manet. Risks include both copy goroutines racing to close/reset/deregister the same stream, ID growth, and connection-manager tag leaks if deregistration is missed. Stress/integration tests should watch for leaks and correct half-close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/p2p/stream.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/Rules.mk -->
# sources/distributed-fs/ipfs-kubo/plugin/Rules.mk

## Purpose

This Make fragment wires plugin subdirectories into the Kubo build.

## Important APIs, Types, and Functions

It includes `mk/header.mk`, sets `dir` to `$(d)/loader` and `$(d)/plugins`, includes each subdirectory `Rules.mk`, then includes `mk/footer.mk`.

## Control Flow, State, and Integration

The fragment participates in recursive Make directory tracking and delegates all concrete plugin build logic to loader and plugins rules.

## Dependencies, Risks, and Test Signals

Dependencies are the make header/footer convention and both child rules files. Build target discovery validates it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/Rules.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/daemon.go -->
# sources/distributed-fs/ipfs-kubo/plugin/daemon.go

## Purpose

This file defines the public daemon plugin interface for plugins that run after the Kubo daemon starts.

## Important APIs, Types, and Functions

`PluginDaemon` embeds `Plugin` and adds `Start(coreiface.CoreAPI) error`.

## Control Flow, State, and Integration

The loader calls `Start` after injection during `PluginLoader.Start`, passing a CoreAPI wrapper around the node.

## Dependencies, Risks, and Test Signals

Dependency is `coreiface`. Risks are plugin startup failures causing loader close and daemon startup errors. Loader integration tests or daemon plugin tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/daemon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/daemoninternal.go -->
# sources/distributed-fs/ipfs-kubo/plugin/daemoninternal.go

## Purpose

This file defines an internal daemon plugin interface that receives direct `*core.IpfsNode` access.

## Important APIs, Types, and Functions

`PluginDaemonInternal` embeds `Plugin` and adds `Start(*core.IpfsNode) error`.

## Control Flow, State, and Integration

The loader starts these plugins after injection. Built-in peerlog and telemetry use this interface because they need node internals.

## Dependencies, Risks, and Test Signals

Dependency is Kubo core. The interface is explicitly unstable; plugins can break across internal graph changes. Built-in plugin tests and daemon startup validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/daemoninternal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/datastore.go -->
# sources/distributed-fs/ipfs-kubo/plugin/datastore.go

## Purpose

This file defines the interface for datastore plugins that add repo datastore backends.

## Important APIs, Types, and Functions

`PluginDatastore` embeds `Plugin` and requires `DatastoreTypeName` and `DatastoreConfigParser`.

## Control Flow, State, and Integration

During plugin injection, the loader registers each parser with `fsrepo.AddDatastoreConfigHandler`, allowing repo configs to instantiate backend-specific datastores.

## Dependencies, Risks, and Test Signals

Dependency is `repo/fsrepo`. Risks include type-name collisions and parser errors making repos unloadable. Datastore plugin tests and repo open/init paths validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/datastore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/fx.go -->
# sources/distributed-fs/ipfs-kubo/plugin/fx.go

## Purpose

This file defines the interface for plugins that modify Kubo's Fx dependency graph.

## Important APIs, Types, and Functions

`PluginFx` embeds `Plugin` and adds `Options(core.FXNodeInfo) ([]fx.Option, error)`.

## Control Flow, State, and Integration

The loader registers each option function through `core.RegisterFXOptionFunc`. Implementations receive existing node info and usually append or decorate options.

## Dependencies, Risks, and Test Signals

Dependencies are Kubo core and Uber Fx. The interface is invasive and can destabilize node construction if plugins replace the wrong dependencies. Built-in `fxtest` and `nopfs` exercise the pattern.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/fx.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/ipld.go -->
# sources/distributed-fs/ipfs-kubo/plugin/ipld.go

## Purpose

This file defines the interface for plugins that register IPLD codecs.

## Important APIs, Types, and Functions

`PluginIPLD` embeds `Plugin` and requires `Register(multicodec.Registry) error`.

## Control Flow, State, and Integration

The loader calls `Register` against `multicodec.DefaultRegistry` during injection. Built-in git and dag-jose plugins use it.

## Dependencies, Risks, and Test Signals

Dependency is go-ipld-prime multicodec. Risks include codec ID collisions, decode/encode registration errors, and process-global registry mutation. IPLD import/export paths validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/ipld.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/Rules.mk -->
# sources/distributed-fs/ipfs-kubo/plugin/loader/Rules.mk

## Purpose

This Make fragment declares how generated plugin loader preload code participates in builds.

## Important APIs, Types, and Functions

It includes `mk/header.mk`, adds `$(d)/preload.go` to `DEPS_GO`, and includes `mk/footer.mk`.

## Control Flow, State, and Integration

Any target depending on `DEPS_GO` will include the generated preload file in dependency tracking.

## Dependencies, Risks, and Test Signals

Dependencies are make header/footer and preload generation. Risks include stale `preload.go` not causing rebuilds. Plugin build tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/Rules.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/load_nocgo.go -->
# sources/distributed-fs/ipfs-kubo/plugin/loader/load_nocgo.go

## Purpose

This file disables dynamic plugin loading when building on supported Unix-like platforms without cgo.

## Important APIs, Types, and Functions

`init` assigns `loadPluginFunc = nocgoLoadPlugin`. `nocgoLoadPlugin` returns `not built with cgo support`.

## Control Flow, State, and Integration

Preloaded compiled-in plugins still work; only runtime `.so` loading fails. The loader will surface the error if executable files are found in the plugins directory.

## Dependencies, Risks, and Test Signals

Dependencies are build tags and plugin interface types. Risks include confusing users who expect dynamic plugins in cgo-disabled builds. Build matrix tests with `CGO_ENABLED=0` validate this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/load_nocgo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/load_noplugin.go -->
# sources/distributed-fs/ipfs-kubo/plugin/loader/load_noplugin.go

## Purpose

This file disables dynamic plugin loading when Kubo is built with the `noplugin` tag.

## Important APIs, Types, and Functions

`init` assigns `loadPluginFunc = nopluginLoadPlugin`. `nopluginLoadPlugin` returns `not built with plugin support`.

## Control Flow, State, and Integration

The loader can still manage preloaded plugins compiled into the binary, but dynamic plugin files cannot be loaded.

## Dependencies, Risks, and Test Signals

Dependencies are build tags and plugin interface types. Risks are user confusion and startup errors if plugin files are present. Build-tag tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/load_noplugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/load_unix.go -->
# sources/distributed-fs/ipfs-kubo/plugin/loader/load_unix.go

## Purpose

This file enables dynamic Go plugin loading on supported Unix-like platforms when cgo is available and `noplugin` is not set.

## Important APIs, Types, and Functions

`init` assigns `loadPluginFunc = unixLoadPlugin`. `unixLoadPlugin` calls `plugin.Open`, looks up the exported `Plugins` symbol, asserts it is `*[]plugin.Plugin`, and returns the slice.

## Control Flow, State, and Integration

`loadDynamicPlugins` in `loader.go` invokes this for executable files in the repo plugins directory. Loaded plugins then enter the normal loader state machine.

## Dependencies, Risks, and Test Signals

Dependencies are Go's `plugin` package, cgo, and compatible buildmode/plugin artifacts. Risks include ABI/version mismatch, symbol type mismatch, platform support gaps, and the typo in the error message. Dynamic plugin build/load smoke tests validate this path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/load_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/loader.go -->
# sources/distributed-fs/ipfs-kubo/plugin/loader/loader.go

## Purpose

`loader.go` implements Kubo's plugin lifecycle manager: load preloaded and dynamic plugins, initialize them with repo/config context, inject extension points, start daemon plugins, and close started plugins.

## Important APIs, Types, and Functions

`Preload` appends compiled-in plugins during init. `loaderState` and `PluginLoader` enforce lifecycle phases. `NewPluginLoader` reads plugin config, loads preloaded plugins, and scans the repo plugins directory. `readPluginsConfig` reads only the config `Plugins` section. `Load`, `LoadDirectory`, and `loadDynamicPlugins` handle duplicate/disabled/executable checks. `Initialize`, `Inject`, `Start`, and `Close` transition states. Injection helpers register datastore parsers, IPLD codecs, tracers, and Fx option functions.

## Control Flow, State, and Integration

The loader is a strict state machine: loading -> initializing -> initialized -> injecting -> injected -> starting -> started -> closing/closed, with `loaderFailed` on errors. Dynamic plugin scan ignores directories, rejects non-executable files, and uses the platform `loadPluginFunc`. Started plugins that implement `io.Closer` are closed in startup order. State is in memory, while config is read from the repo.

## Dependencies, Risks, and Test Signals

Dependencies include config parsing, fsrepo datastore registry, core/CoreAPI, multicodec default registry, OpenTracing global tracer, and platform dynamic loading. Risks include process-global registry mutations, duplicate plugin names, disabled config semantics, dynamic plugin ABI failures, partial startup cleanup, and error aggregation on close. Built-in plugin initialization, example setup, and daemon startup are major signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/loader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/preload.go -->
# sources/distributed-fs/ipfs-kubo/plugin/loader/preload.go

## Purpose

This generated file preloads Kubo's built-in plugins into the plugin loader.

## Important APIs, Types, and Functions

The `init` function calls `Preload` for git, dag-jose, badgerds, flatfs, levelds, pebbleds, peerlog, fxtest, nopfs, and telemetry plugin slices.

## Control Flow, State, and Integration

At package initialization time, each plugin slice is appended to the global preload list. `NewPluginLoader` later loads that list before scanning external plugins.

## Dependencies, Risks, and Test Signals

Dependencies are all built-in plugin packages. Risks include generated order changes, stale generated file after plugin list edits, and unavoidable side effects from importing plugin packages. `preload.sh` and plugin startup tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/preload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/preload.sh -->
# sources/distributed-fs/ipfs-kubo/plugin/loader/preload.sh

## Purpose

This shell script regenerates `plugin/loader/preload.go` from a fixed list of built-in plugin import paths.

## Important APIs, Types, and Functions

It defines a `plugins` list, writes package/import boilerplate to `preload.go`, emits one `Preload(alias.Plugins...)` line per plugin, then runs `go fmt`.

## Control Flow, State, and Integration

The script overwrites `preload.go` in the current directory. It is a build-maintenance tool, not runtime code.

## Dependencies, Risks, and Test Signals

Dependencies are bash, redirection, and `go fmt`. Risks include alias generation mistakes, running from the wrong directory, and plugin list drift relative to `plugin/plugins/Rules.mk`. A clean generated diff and successful build validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/loader/preload.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugin.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugin.go

## Purpose

This file defines the base plugin contract and initialization environment shared by all Kubo plugin types.

## Important APIs, Types, and Functions

`Environment` carries repo path and arbitrary plugin config from `Plugins.Plugins["plugin-name"].Config`. `Plugin` requires `Name`, `Version`, and `Init`, and may optionally also implement `io.Closer`.

## Control Flow, State, and Integration

The loader constructs an `Environment` for each loaded plugin during initialization. Implementations use it to persist repo paths or parse config.

## Dependencies, Risks, and Test Signals

There are no external dependencies. Risks include untyped config causing runtime assertions in plugins and plugin name/version collisions. Loader duplicate checks and built-in plugin tests validate the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/Rules.mk -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/Rules.mk

## Purpose

This Make fragment defines dynamic plugin build scaffolding for plugin packages.

## Important APIs, Types, and Functions

It tracks plugin package lists, generated `main/main.go` files, `.so` outputs, invokes `gen_main.sh`, runs `go fmt`, builds with `-buildmode=plugin` and a dynamic-link pkgdir, marks outputs executable, and wires cleanup/build targets.

## Control Flow, State, and Integration

When plugin packages are listed in `$($(d)_plugins)`, Make generates wrapper mains and builds `.so` artifacts. Current list is empty, so the rules are infrastructure.

## Dependencies, Risks, and Test Signals

Dependencies are GNU Make, Go plugin buildmode, GOPATH pkgdir, and `gen_main.sh`. Risks include Linux amd64-specific pkgdir, dynamic plugin ABI fragility, and generated wrapper cleanup. Dynamic plugin build jobs validate it when plugins are listed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/Rules.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/badgerds/badgerds.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/badgerds/badgerds.go

## Purpose

This built-in datastore plugin registers the deprecated Badger v1 datastore backend.

## Important APIs, Types, and Functions

`badgerdsPlugin` implements `PluginDatastore` with type name `badgerds`. Its parser requires `path`, optionally accepts `syncWrites`, `truncate`, and string `vlogFileSize` parsed by `humanize.ParseBytes`. `datastoreConfig.DiskSpec` returns datastore metadata. `Create` prints/logs a deprecation warning, resolves relative paths against repo path, creates the directory, configures Badger options, and calls `badgerds.NewDatastore`.

## Control Flow, State, and Integration

After loader injection, fsrepo can instantiate badgerds repos. The plugin persists data in the configured directory and writes a prominent warning to stderr every creation.

## Dependencies, Risks, and Test Signals

Dependencies are go-ds-badger, humanize, fsrepo, repo datastore interface, and filesystem directory creation. Risks include deprecated upstream bugs, future removal, path/config type errors, and noisy stderr. Repo open tests for badger configs and migration guidance are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/badgerds/badgerds.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/dagjose/dagjose.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/dagjose/dagjose.go

## Purpose

This IPLD plugin registers the dag-jose codec for Kubo.

## Important APIs, Types, and Functions

`dagjosePlugin` implements `PluginIPLD`, returns name `ipld-codec-dagjose`, version `0.0.1`, no-op init, and registers dag-jose encoder/decoder under multicodec `DagJose`.

## Control Flow, State, and Integration

Loader injection mutates the global multicodec registry. Once registered, IPLD operations can encode/decode dag-jose blocks.

## Dependencies, Risks, and Test Signals

Dependencies are Ceramic's dag-jose library and go-ipld-prime multicodec. Risks include codec registration conflicts and decoder behavior changes. IPLD codec round-trip tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/dagjose/dagjose.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/flatfs/flatfs.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/flatfs/flatfs.go

## Purpose

This datastore plugin registers the FlatFS datastore backend.

## Important APIs, Types, and Functions

`flatfsPlugin` implements `PluginDatastore` with type name `flatfs`. The parser requires string `path`, string `shardFunc`, and bool `sync`; it parses the shard function with `flatfs.ParseShardFunc`. `DiskSpec` records type/path/shardFunc. `Create` resolves relative path and calls `flatfs.CreateOrOpen`.

## Control Flow, State, and Integration

The plugin registers a config handler with fsrepo during loader injection. Persistent state lives in the configured FlatFS directory.

## Dependencies, Risks, and Test Signals

Dependencies are go-ds-flatfs and fsrepo. Risks include strict config type requirements, malformed shard functions, and a misleading error message for missing path. Repo init/open tests with flatfs specs validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/flatfs/flatfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/fxtest/fxtest.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/fxtest/fxtest.go

## Purpose

This built-in test plugin validates the `PluginFx` extension mechanism without affecting production unless explicitly enabled by environment.

## Important APIs, Types, and Functions

`fxtestPlugin` implements `PluginFx`. `Options` returns existing FX options and, when `TEST_FX_PLUGIN` is set, appends an `fx.Invoke` that logs a debug statement.

## Control Flow, State, and Integration

The plugin is preloaded and initialized like other plugins. Its runtime effect is gated by an environment variable.

## Dependencies, Risks, and Test Signals

Dependencies are Uber Fx, Kubo core FX info, and go-log. Risks are minimal, but accidental env setting could add an invocation. FX plugin tests should assert the invocation path works.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/fxtest/fxtest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/gen_main.sh -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/gen_main.sh

## Purpose

This helper generates a wrapper `main.go` for building a plugin package as a Go `.so` plugin.

## Important APIs, Types, and Functions

It requires output dir and package import path parameters, creates `<dir>/main`, writes a `package main` that imports the target package as `uniquepkgname`, exports `var Plugins = uniquepkgname.Plugins`, and defines a panic-only `main`.

## Control Flow, State, and Integration

The script writes generated source under the plugin package's `main` subdirectory. `plugin/plugins/Rules.mk` then formats and builds it with `-buildmode=plugin`.

## Dependencies, Risks, and Test Signals

Dependencies are bash and shell redirection. Risks include unescaped package paths, fixed alias collisions, and generated files left behind. Dynamic plugin build tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/gen_main.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/git/git.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/git/git.go

## Purpose

This IPLD plugin registers Git object codecs, including a compatibility decoder for zlib-compressed raw Git objects.

## Important APIs, Types, and Functions

`gitPlugin` implements `PluginIPLD`. `Register` registers a reserved-range decoder for zlib-encoded Git raw objects, plus standard GitRaw encoder and decoder. `decodeZlibGit` wraps the input with `zlib.NewReader` and delegates to `go-ipld-git.Decode`.

## Control Flow, State, and Integration

Loader injection mutates the global multicodec registry. Importing the go-ipld-git package also has codec registration side effects noted in the comment.

## Dependencies, Risks, and Test Signals

Dependencies are `compress/zlib`, go-ipld-git, go-ipld-prime, and multicodec IDs. Risks include registry conflicts, zlib reader errors, and reserved-range compatibility assumptions. Git DAG import/export tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/git/git.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/levelds/levelds.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/levelds/levelds.go

## Purpose

This datastore plugin registers LevelDB-backed repo datastore support.

## Important APIs, Types, and Functions

`leveldsPlugin` implements `PluginDatastore` with type name `levelds`. The parser requires `path` and optionally accepts `compression` values `none`, `snappy`, empty, or nil. `DiskSpec` records type/path. `Create` resolves relative paths and calls `levelds.NewDatastore` with the selected compression.

## Control Flow, State, and Integration

Once injected into fsrepo, configs using `levelds` instantiate persistent LevelDB directories under the repo or absolute path.

## Dependencies, Risks, and Test Signals

Dependencies are go-ds-leveldb and goleveldb options. Risks include unrecognized compression values, filesystem corruption risks if used concurrently, and path resolution mistakes. Repo datastore config tests validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/levelds/levelds.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/nopfs/nopfs.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/nopfs/nopfs.go

## Purpose

This Fx plugin integrates `nopfs` content blocking into Kubo's block service, name system, and path resolvers.

## Important APIs, Types, and Functions

`nopfsPlugin` stores the repo path during `Init` and implements `PluginFx`. `MakeBlocker` loads default denylist files and repo-local `denylists` files, then creates a `nopfs.Blocker`. `PathResolvers` wraps online and offline IPLD/UnixFS path resolvers. `Options` returns original FX options when `IPFS_CONTENT_BLOCKING_DISABLE` is set, otherwise provides the blocker and decorates block service, name system, and resolvers.

## Control Flow, State, and Integration

At node construction time, Fx creates the blocker from filesystem denylist files and decorates core dependencies. The plugin reads repo-local state under `<repo>/denylists` but does not itself persist data.

## Dependencies, Risks, and Test Signals

Dependencies are ipfs-shipyard/nopfs, Kubo core/node fetchers, and Fx. Risks include denylist read failures breaking node construction, broad resolver wrapping, environment-disable bypass, and stale denylists needing restart. Integration tests should verify blocked CIDs/paths and disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/nopfs/nopfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/pebbleds/pebbleds.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/pebbleds/pebbleds.go

## Purpose

This datastore plugin registers experimental Pebble-backed repo datastore support with tunable Pebble options.

## Important APIs, Types, and Functions

`pebbledsPlugin` implements `PluginDatastore` with type name `pebbleds`. The parser requires `path`, reads numeric/bool options via `getConfigInt` and `getConfigBool`, handles cache size, sync/WAL/format/compaction/memtable options, warns about older format major versions, and builds optional `pebble.Options`. `Create` resolves the path, checks it with `fsutil.DirWritable`, and calls `pebbleds.NewDatastore` with cache and Pebble options.

## Control Flow, State, and Integration

After loader injection, fsrepo can create Pebble datastores. The datastore persists data in the configured directory and may ratchet DB format to the newest format when not configured, affecting downgrade compatibility.

## Dependencies, Risks, and Test Signals

Dependencies are CockroachDB Pebble v2, go-ds-pebble, fsutil, fsrepo, and repo interfaces. Risks include int/float64 config coercion truncation, downgrade prevention from format ratcheting, unsafe WAL disabling, and write-throttle misconfiguration. Telemetry tests use pebbleds to create a repo, giving a basic integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/pebbleds/pebbleds.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/peerlog/peerlog.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/peerlog/peerlog.go

## Purpose

This internal daemon plugin logs peer connection and identify events when explicitly enabled in plugin config.

## Important APIs, Types, and Functions

`eventType`, `plEvent`, and `peerLogPlugin` model queued events. `extractEnabled` reads boolean `Enabled` from untyped config. `Init` allocates a large buffered event channel and stores enabled state. `Start` sets plugin log level, subscribes to identify events, registers a network connected notifee, and starts event collection. `emit` drops events under backpressure. `collectEvents` logs connected/identified events and reports dropped counts with backoff and queue draining.

## Control Flow, State, and Integration

When disabled, `Start` returns without side effects. When enabled, it creates goroutines tied to node context. State is in memory: event queue, dropped counter, and event subscriptions. It reads agent versions from the peerstore.

## Dependencies, Risks, and Test Signals

Dependencies are libp2p event bus/network/peerstore, Kubo core, zap logging, and atomics. Risks include high memory buffer size, dropped event accounting, event goroutines not being stopped except by node context, and unsupported config shape. `peerlog_test.go` covers config extraction; integration tests should cover event emission under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/peerlog/peerlog.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/peerlog/peerlog_test.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/peerlog/peerlog_test.go

## Purpose

This file tests peerlog's config parser for the `Enabled` flag.

## Important APIs, Types, and Functions

`TestExtractEnabled` table-tests nil config, wrong config type, missing field, nil field, non-boolean field, and true boolean field.

## Control Flow, State, and Integration

The tests call `extractEnabled` directly and do not start a node or plugin.

## Dependencies, Risks, and Test Signals

Dependency is the testing package only. The test covers opt-in safety but not runtime event logging, queue overflow, or close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/peerlog/peerlog_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/telemetry/telemetry.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/telemetry/telemetry.go

## Purpose

This daemon-internal plugin collects anonymized Kubo usage/configuration telemetry and periodically sends it to a configured HTTP endpoint, with opt-out and delayed first send semantics.

## Important APIs, Types, and Functions

`LogEvent` defines the JSON payload: UUID, agent version, private network, bootstrap customization, repo size and uptime buckets, routing/provide/autonat/autoconf/swarm/autotls/discovery/platform fields. `telemetryPlugin` stores mode, endpoint, UUID filename, send delay, node/config/event, and start time. `Init` reads mode/delay/endpoint from env/config, handles opt-out UUID removal, and defaults to on/auto. `loadUUID` reads or creates repo-local `telemetry_uuid`. `Start` validates daemon/online mode, loads UUID, shows opt-in info in auto mode, and schedules sends. `prepareEvent` calls collectors, platform detection is cached, and `sendTelemetry` posts JSON with a 30-second HTTP timeout.

## Control Flow, State, and Integration

The plugin is initialized before node start, then started with direct `IpfsNode`. In production it waits `sendDelay` before first send, then repeats every 24 hours. In tests `runOnce` sends immediately. Persistent state is the UUID file in the repo, removed on opt-out. Collection reads repo config, repo size, swarm addresses, private network key, peer host reachability, runtime OS/arch, and host/container/VM indicators.

## Dependencies, Risks, and Test Signals

Dependencies include HTTP, JSON, uuid, Kubo config/core/corerepo, libp2p network/pnet/multiaddr, runtime OS files under `/proc` and `/sys`, and environment variables. Risks include privacy-sensitive field creep, endpoint failures, UUID persistence after config changes, goroutine timer leaks only ending with process, false container/VM detection, repo-size cost, and Unicode console output. `telemetry_test.go` verifies immediate send to a mock server and UUID round-trip; more tests would be useful for opt-out, delay parsing, bucketing, and platform detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/telemetry/telemetry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/telemetry/telemetry_test.go -->
# sources/distributed-fs/ipfs-kubo/plugin/plugins/telemetry/telemetry_test.go

## Purpose

This file integration-tests telemetry send behavior against a local HTTP server and a real temporary Kubo repo.

## Important APIs, Types, and Functions

`mockServer` returns an `httptest.Server` that requires POST `/`, JSON content type, non-empty body, unmarshals `LogEvent`, and exposes the received event. `makeNode` creates a temp fsrepo using pebbleds, registers the pebbleds datastore parser, initializes config, opens the repo, builds an online node with nil routing, and marks it daemon. `TestSendTelemetry` initializes a `telemetryPlugin` with `runOnce`, overrides endpoint to the test server, starts it, and checks UUID equality.

## Control Flow, State, and Integration

The test writes a real repo and datastore under temp paths, starts a real core node, and performs an actual HTTP POST to the test server. It does not wait for timers because `runOnce` bypasses delay.

## Dependencies, Risks, and Test Signals

Dependencies include httptest, pebbleds, fsrepo, config, core node construction, and nil libp2p routing. It signals that telemetry can collect and send without crashing, but does not cover opt-out removal, failed HTTP status, delay scheduling, or platform detection branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/plugins/telemetry/telemetry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/tracer.go -->
# sources/distributed-fs/ipfs-kubo/plugin/tracer.go

## Purpose

This file defines the plugin interface for providing an OpenTracing tracer.

## Important APIs, Types, and Functions

`PluginTracer` embeds `Plugin` and adds `InitTracer() (opentracing.Tracer, error)`.

## Control Flow, State, and Integration

The loader calls `InitTracer` during injection and sets the returned tracer as the global OpenTracing tracer. The loader logs that tracer plugins are deprecated in favor of OpenTelemetry collector configuration.

## Dependencies, Risks, and Test Signals

Dependency is OpenTracing. Risks include process-global tracer mutation, deprecated API usage, and plugin initialization failure preventing injection. Loader tests or a sample tracer plugin would validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/plugin/tracer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/profile/goroutines.go -->
# sources/distributed-fs/ipfs-kubo/profile/goroutines.go

## Purpose

This helper writes all goroutine stacks without the 64 MiB truncation behavior of Go's standard pprof stack writer.

## Important APIs, Types, and Functions

`WriteAllGoroutineStacks` repeatedly calls `runtime.Stack(buf, true)`, doubling the buffer from 1 MiB until it fits, then writes the captured stack dump to an `io.Writer`.

## Control Flow, State, and Integration

The function allocates progressively larger buffers and returns the writer error. It does not persist data itself; callers decide where profile output goes.

## Dependencies, Risks, and Test Signals

Dependencies are `runtime` and `io`. Risks include large memory allocation in processes with enormous goroutine dumps and racing stack changes while sizing. Profile tests and operational profile collection validate that dumps are complete enough for debugging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/profile/goroutines.go -->
