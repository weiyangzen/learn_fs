# Research: subset-b-009603

Grouped source-tree-aligned research for selected `go-fuse` files. Each file section preserves the source path in its title and is wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/mem_test.go -->
## sources/user-network-fs/go-fuse/fs/mem_test.go

Purpose: exercises the modern `fs` in-memory node helpers and shared test mount helper. It verifies ownership defaults, explicit root inode numbers, `MemRegularFile` read/write/stat behavior, large reads, symlink construction, readdirplus consistency, and a POSIX subset over an in-memory writable directory.

Important APIs/types/functions: `testMount` wraps `Mount`, configures debug logging, waits for mount, and registers cleanup. `SymlinkerRoot.Symlink` creates `MemSymlink` persistent inodes. `readDirStream` drains `DirStream`. `memDir.Create` creates handleless `MemRegularFile` children. Tests call `NewPersistentInode`, `AddChild`, `NewLoopbackDirStream`, `posixtest`, and `fuse.Attr`.

Control flow: each test builds a root `Inode`, often populates children via `Options.OnAdd`, mounts into `t.TempDir`, performs kernel-facing syscalls through the mount, then unmounts through cleanup. Readdir tests compare parsed kernel directory streams across many concurrent readers. `TestMemPosix` iterates selected POSIX scenarios and remounts per subtest.

State and persistence: data is process-memory state stored in `MemRegularFile.Data` and inode child maps; no durable persistence is expected. Timeouts influence kernel entry/attribute caching. `FirstAutomaticIno`, `RootStableAttr`, UID/GID options, and stable attrs determine visible inode metadata.

Dependencies and integration: integrates `fs.Mount`, `fuse.Server`, `fuse.Attr`, `internal/testutil`, and `posixtest`. It is a regression suite for the high-level inode API and for compatibility with kernel syscall behavior.

Risks and test signals: concurrency-sensitive readdirplus and POSIX tests catch races in directory stream conversion, inode lookup, and file handle paths. The tests require a working FUSE environment; failures may reflect mount permissions or kernel behavior rather than pure Go logic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/mem_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/mem_unix.go -->
## sources/user-network-fs/go-fuse/fs/mem_unix.go

Purpose: non-Linux implementation of `keepSizeMode`, a platform hook used by in-memory file allocation/truncation behavior.

Important APIs/types/functions: `keepSizeMode(mode uint32) bool` always returns false under `!linux`.

Control flow: callers branch on the boolean to decide whether an allocation mode preserves file size. On non-Linux platforms, the path never treats the mode as keep-size.

State and persistence: stateless helper; no persistence or external state.

Dependencies and integration: selected by Go build tags for non-Linux `fs` builds, complementing the Linux-specific in-memory file implementation.

Risks and test signals: platform divergence is intentional. Any feature relying on Linux fallocate keep-size semantics must handle false here or remain Linux-only.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/mem_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/mount.go -->
## sources/user-network-fs/go-fuse/fs/mount.go

Purpose: convenience entry point that mounts a high-level `fs` inode tree and starts serving it.

Important APIs/types/functions: `Mount(dir string, root InodeEmbedder, options *Options) (*fuse.Server, error)` calls `NewNodeFS`, passes `options.MountOptions` into `fuse.NewServer`, launches `server.Serve()` in a goroutine, waits with `WaitMount`, and returns the server.

Control flow: construct raw bridge, create server, start serving, wait for mount completion. If mount creation or waiting fails, the error is returned; the failed serve loop is expected to exit naturally.

State and persistence: it owns no filesystem state directly, but wires `Options` into both high-level FS behavior and kernel mount options. The returned server controls lifecycle and unmount.

Dependencies and integration: integrates the `fs` package with the raw `fuse.Server`. This wrapper is used by examples and most `fs` tests.

Risks and test signals: callers must call `Unmount`/`Wait` to clean up. Errors after `Serve` starts rely on the server loop exiting; tests around parallel mount and basic mount lifecycle exercise this path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/panic_test.go -->
## sources/user-network-fs/go-fuse/fs/panic_test.go

Purpose: verifies that panics inside high-level FS handlers are caught, logged, and translated to a kernel-visible error.

Important APIs/types/functions: `panicNode` embeds `Inode` and implements `NodeSymlinker`. Its `Symlink` method panics. `TestPanic` mounts a raw `NewNodeFS` with a logger buffer, performs `syscall.Symlink`, and checks for `EIO` plus a panic log line.

Control flow: the test bypasses `fs.Mount` to inject `MountOptions.Logger`, starts `fuse.Server`, triggers the symlink path, unmounts, and inspects the captured log.

State and persistence: transient mount and log buffer only. No durable inode changes should survive because the operation panics before returning a child.

Dependencies and integration: covers panic recovery in the `fs` bridge and `fuse.MountOptions.PanicHandler` default behavior.

Risks and test signals: prevents panics from killing the server goroutine silently or hanging kernel callers. It also verifies the log text stays useful for diagnosis.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/panic_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/passthrough_test.go -->
## sources/user-network-fs/go-fuse/fs/passthrough_test.go

Purpose: tests Linux kernel passthrough behavior where read/write operations bypass the Go FUSE handler after a backing file is registered.

Important APIs/types/functions: `rwRegisteringNode` embeds `LoopbackNode` and wraps `Read`/`Write` to increment counters before delegating to `FileReader`/`FileWriter`. `TestPassthrough` constructs a custom `LoopbackRoot` and verifies counters remain zero after file I/O.

Control flow: the test requires effective root/CAP_SYS_ADMIN, mounts a loopback tree, checks `server.KernelSettings().Flags64()&fuse.CAP_PASSTHROUGH`, writes and reads a file, unmounts, and asserts no Go-level read/write callbacks occurred.

State and persistence: backing data lives in a temporary loopback directory. The node records read/write counts protected by a mutex.

Dependencies and integration: integrates `fs.LoopbackNode`, `fuse.CAP_PASSTHROUGH`, and kernel passthrough registration support.

Risks and test signals: skipped when permissions or kernel capability are missing. Failing counters indicate passthrough was not used or file handle registration changed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/passthrough_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/piperead_test.go -->
## sources/user-network-fs/go-fuse/fs/piperead_test.go

Purpose: Linux regression test for short or failing pipe-backed read results. It ensures a `ReadResultPipe` that promises more data than was written does not corrupt the returned content.

Important APIs/types/functions: `pipefailNode` implements `Open`, `Getattr`, and `Read`. `Read` obtains a splice pipe, grows it, writes only `actual` bytes, and returns `fuse.ReadResultPipe(pair, total)` where `total` may exceed available data.

Control flow: test mounts a file whose stat size is `promise` but whose pipe contains fewer bytes, then `os.ReadFile` checks the read result equals `actual`.

State and persistence: node stores `promise` size and `actual` bytes in memory. Kernel caching is enabled through one-second entry and attr timeouts.

Dependencies and integration: depends on Linux build tag, `splice.Get`, `fuse.ReadResultPipe`, and high-level mount plumbing.

Risks and test signals: catches edge cases in pipe/splice result cleanup and EOF handling. Failures may manifest as hangs, `EIO`, or extra bytes if pipe accounting is wrong.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/piperead_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/randomtype_test.go -->
## sources/user-network-fs/go-fuse/fs/randomtype_test.go

Purpose: tests that READDIRPLUS fixes directory entry type bits using lookup attributes when `Readdir` returns stale or generic types.

Important APIs/types/functions: `randomTypeTest` implements `NodeLookuper` and `NodeReaddirer`. `Lookup` returns pseudo-random file or directory stable attrs based on CRC32 of the name. `Readdir` returns all entries as directories. `TestReaddirTypeFixup` reads kernel dirents and validates final type bits.

Control flow: mount root, open the directory, use `NewLoopbackDirStream` to parse `getdents`, then compare each entry mode with the deterministic CRC rule.

State and persistence: children are dynamically created by lookup; no durable backing store.

Dependencies and integration: exercises `DirEntryList.FixMode`, `ReadDirPlus`, lookup integration, and loopback directory parsing.

Risks and test signals: catches mismatches between `Readdir` hints and lookup-derived `EntryOut.Attr.Mode`, important for clients relying on `d_type`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/randomtype_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/readonly_test.go -->
## sources/user-network-fs/go-fuse/fs/readonly_test.go

Purpose: verifies default read-only behavior for an empty inode tree and default permission modes for bare directory/file inodes.

Important APIs/types/functions: `TestReadonlyCreate` opens a non-existing file with `O_CREAT` and expects `EROFS`. `TestDefaultPermissions` creates child inodes with only file type bits and checks visible modes are directory `0755` and file `0644`.

Control flow: tests mount a root `Inode`, optionally populate children through `Options.OnAdd`, then use `unix.Open` or `syscall.Lstat` against the mount.

State and persistence: all state is in-memory inode metadata. No file data is written.

Dependencies and integration: validates default operation implementations and `StableAttr.Mode` normalization in the high-level `fs` package.

Risks and test signals: protects public API expectations for default nodes. Incorrect defaults can break simple read-only filesystems or permission-sensitive clients.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/readonly_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/readwrite_handleless_example_test.go -->
## sources/user-network-fs/go-fuse/fs/readwrite_handleless_example_test.go

Purpose: runnable example of a writable file implemented directly on a node without a separate file handle.

Important APIs/types/functions: `bytesNode` stores bytes and a mutex. It implements `NodeGetattrer`, `NodeSetattrer`, `NodeReader`, `NodeWriter`, and `NodeOpener`. Helpers `getattr` and `resize` maintain `fuse.Attr` fields. `Example_handleLess` mounts the node using `fs.Mount`.

Control flow: `Open` returns nil handle with cache flags. `Read` copies from the node byte slice by offset. `Write` resizes and copies into the slice. `Setattr` handles truncation through `GetSize`. `Getattr` reports size/mode under lock.

State and persistence: file content exists only in `bytesNode.data`; mutex protects concurrent kernel calls. No durable storage.

Dependencies and integration: demonstrates handleless high-level file APIs, `fuse.ReadResultData`, `FOPEN_KEEP_CACHE`, and set-attribute resize semantics.

Risks and test signals: example code is compiled and can be run as documentation. The main risk is concurrent access; the mutex is the intended pattern for node-backed mutable state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/readwrite_handleless_example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/rmchild_test.go -->
## sources/user-network-fs/go-fuse/fs/rmchild_test.go

Purpose: concurrency stress test for `Inode.RmChild` and child-map mutation.

Important APIs/types/functions: `TestRmChildParallel` creates many named persistent child inodes, starts goroutines that remove children concurrently, and validates operations complete without races or panics.

Control flow: per iteration, root is populated, goroutines call `RmChild` over different names, and a wait group joins. The test repeats to increase exposure to scheduling variance.

State and persistence: only the in-memory inode child map is mutated. Removed child references are transient.

Dependencies and integration: targets `fs.Inode` locking and tree bookkeeping used by lookup, unlink, rename, and notification paths.

Risks and test signals: catches missing locks, map concurrent writes, and stale parent/child relationships. It is most valuable under `go test -race`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/rmchild_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/simple_test.go -->
## sources/user-network-fs/go-fuse/fs/simple_test.go

Purpose: broad integration suite for the modern `fs` loopback implementation and mount lifecycle.

Important APIs/types/functions: `testCase`, `testOptions`, and `newTestCase` set up backing and mount directories, `NewLoopbackRoot`, `NewNodeFS`, and `fuse.NewServer`. Tests cover basic stat/remove, executable files, fd leaks, notify entry/prune, readdir stress, statfs, getattr/close races, unsupported mknod, POSIX matrix, disabled splice, direct I/O, fsstress, stale hardlinks, parallel mounts, handleless create, and lchown on dangling symlinks.

Control flow: most tests mount a loopback FS, mutate either the backing directory or mount path, then assert kernel-visible behavior. Stress tests fan out goroutines and external `ls` loops. POSIX tests delegate to `posixtest.All`.

State and persistence: durable test state lives in temp backing directories; `rawBridge` tracks open files and inode state. Caches are explicitly toggled through attr and entry timeouts.

Dependencies and integration: integrates high-level `fs`, raw `fuse.Server`, `LoopbackNode`, `posixtest`, `unix` syscalls, and kernel mount options such as direct mount, splice, locks, and idmapped mount.

Risks and test signals: this is a primary regression file for deadlocks, descriptor leaks, stale inode reuse, cache invalidation, and mount concurrency. Some tests are environment-sensitive and may skip or fail depending on filesystem type, privileges, or FUSE support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/simple_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/statx_linux_test.go -->
## sources/user-network-fs/go-fuse/fs/statx_linux_test.go

Purpose: Linux test for `statx` forwarding and timestamp/attribute fidelity through loopback mounts.

Important APIs/types/functions: `lstatxPath` calls `unix.Statx` with `AT_SYMLINK_NOFOLLOW`. `clearStatx` masks volatile fields before comparison. `TestStatx` compares statx results from the original path and mounted path.

Control flow: the test creates loopback-backed filesystem state, gathers `Statx_t` from both sides, normalizes fields that are known to differ, and checks equality.

State and persistence: backing files live in temp directories. The mount should not synthesize persistent statx values beyond what loopback returns.

Dependencies and integration: targets Linux `NodeStatxer`/raw `STATX` plumbing and `fuse.Statx.FromStatx` conversion.

Risks and test signals: catches field loss in statx conversion, masking, or raw opcode dispatch. It is Linux-only and depends on kernel statx support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/statx_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/windows_example_test.go -->
## sources/user-network-fs/go-fuse/fs/windows_example_test.go

Purpose: example showing Windows-like delete semantics on a loopback filesystem by preventing unlink of open files.

Important APIs/types/functions: `WindowsNode` wraps children with `WrapChild`, intercepts `Open`, `Create`, `Release`, and `Unlink`, and tracks an `openCount`. `isBusy` checks a child node's open count before unlink. `Example_loopbackReuse` mounts a loopback root using the wrapper.

Control flow: new children are wrapped into `WindowsNode`. Open/create increments count; release decrements. `Unlink` checks for active opens and returns a busy error rather than unlinking.

State and persistence: backing data lives in the loopback directory. Open counts are in-memory per wrapper node and protected by a mutex/atomic style in the example.

Dependencies and integration: demonstrates `NodeWrapChilder`, high-level node wrappers, loopback reuse, and Windows compatibility policy atop POSIX kernel calls.

Risks and test signals: as an example, it documents a policy pattern rather than a full test. Correctness depends on balanced Release calls and wrapping every child.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/windows_example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/windows_test.go -->
## sources/user-network-fs/go-fuse/fs/windows_test.go

Purpose: tests Windows-emulation behavior implemented by the loopback layer.

Important APIs/types/functions: `TestWindowsEmulations` mounts the `WindowsNode` example wrapper, opens a file through the mount, and validates unlink behavior around an open handle.

Control flow: creates a loopback-backed mount, writes and reads a file, opens it, checks that `syscall.Unlink` fails while the file is open, closes the handle, waits briefly for FUSE `RELEASE`, and verifies unlink then succeeds.

State and persistence: temp backing directory persists file contents during the test. Runtime state includes open file handles and loopback node bookkeeping.

Dependencies and integration: connects `fs` loopback behavior with Windows compatibility options and kernel open/release sequencing.

Risks and test signals: protects cross-platform busy-delete semantics. Regressions usually indicate open-count tracking, node wrapping, release ordering, or unlink policy drift.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/zip_test.go -->
## sources/user-network-fs/go-fuse/fs/zip_test.go

Purpose: tests ZIP-backed read-only filesystem construction and on-add tree population.

Important APIs/types/functions: `testData` defines archive contents. `createZip` writes deterministic zip entries. `byteReaderAt` adapts a byte slice for `zip.NewReader`. `TestZipFS` and `TestZipFSOnAdd` mount zip contents and verify file reads and directory layout.

Control flow: create in-memory zip data, build a zip reader, construct the zip FS, mount it, and read paths through the kernel. The on-add variant verifies child population at mount time.

State and persistence: archive bytes are in memory; mounted files are read-only views over zip entry data. No writes persist back into the archive.

Dependencies and integration: uses Go `archive/zip`, the `fs` zip example implementation, and normal FUSE read/stat paths.

Risks and test signals: catches tree-building mistakes, path normalization issues, and reader-at offset bugs in compressed file serving.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/zip_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/zipfs_example_test.go -->
## sources/user-network-fs/go-fuse/fs/zipfs_example_test.go

Purpose: example implementation of a read-only filesystem backed by a zip archive.

Important APIs/types/functions: `zipFile` stores a `zip.File`, implements `NodeGetattrer`, `NodeOpener`, and `NodeReader`; it reports mode/size, opens zip entry readers, and reads by offset. `zipRoot.OnAdd` walks archive entries and creates persistent child inodes. `Example_zipFS` demonstrates mount setup.

Control flow: on mount, the root iterates zip entries, creates directories/files as inodes, and links them into the tree. File reads open an archive entry reader, seek/copy as needed, and return `ReadResultData`.

State and persistence: archive metadata and bytes are immutable backing state. Inode tree is materialized in memory at mount time.

Dependencies and integration: integrates Go `archive/zip` with `fs.Inode`, `StableAttr`, and FUSE stat/open/read callbacks.

Risks and test signals: example must handle nested directories, file modes, and repeated reads without leaking readers. It is covered by example compilation and related zip tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fs/zipfs_example_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/api.go -->
## sources/user-network-fs/go-fuse/fuse/api.go

Purpose: public raw FUSE API documentation and core interfaces for implementing a filesystem at protocol level.

Important APIs/types/functions: `ReadResult` abstracts read data as bytes, fd-backed ranges, or pipe-backed data. `MountOptions` controls kernel mount negotiation, caching, capabilities, logging, direct mount, idmapped mount, passthrough, xattrs, locks, splice, panic handling, and request limits. `RawFileSystem` declares callbacks for lookup, attrs, namespace mutation, xattrs, file I/O, locks, directory I/O, statfs, statx, init, and unmount.

Control flow: `fuse.NewServer` mounts and dispatches kernel requests to `RawFileSystem` methods, typically concurrently. `Serve` may run in foreground or goroutine; callers wait with `WaitMount`.

State and persistence: the file defines contracts only. Implementations must own thread-safe inode/file state and must not retain reused request buffers without copying.

Dependencies and integration: foundation for the higher-level `fs`, deprecated `nodefs`, and `pathfs` packages.

Risks and test signals: incorrect implementations can deadlock, race on request memory, or mishandle interrupts. Many tests in this subset validate options and raw dispatch behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/attr.go -->
## sources/user-network-fs/go-fuse/fuse/attr.go

Purpose: utility methods for converting and inspecting FUSE attribute structs.

Important APIs/types/functions: `Attr.IsFifo`, `IsChar`, `IsDir`, `IsBlock`, `IsRegular`, `IsSymlink`, and `IsSocket` inspect mode type bits. `SetTimes`, `ChangeTime`, `AccessTime`, and `ModTime` convert between Go `time.Time` and FUSE timestamp fields. `ToStatT` and `ToAttr` adapt `os.FileInfo` to syscall and FUSE attrs.

Control flow: conversions are direct field mapping helpers used by loopback and tests.

State and persistence: stateless helpers mutating only the provided `Attr`.

Dependencies and integration: used by loopback filesystems, node adapters, and stat tests for consistent kernel metadata.

Risks and test signals: mode bit or time conversion mistakes propagate into cache validation, permissions, and stat comparisons.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/attr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/attr_linux.go -->
## sources/user-network-fs/go-fuse/fuse/attr_linux.go

Purpose: Linux-specific conversion from syscall `Stat_t` and `unix.Statx_t` to FUSE protocol structs.

Important APIs/types/functions: `Attr.FromStat` maps inode, size, blocks, timestamps, mode, link count, owner, device, and block size. `Statx.FromStatx` maps statx timestamps, mask, attributes, device numbers, and ownership.

Control flow: direct field assignment from kernel syscall structs into FUSE structs.

State and persistence: stateless conversion; no storage.

Dependencies and integration: used by Linux loopback, statx dispatch, and tests that compare mounted and backing metadata.

Risks and test signals: Linux struct layout and field semantics are platform-specific. `statx_linux_test.go` is the direct signal for statx conversion fidelity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/attr_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/attr_unix.go -->
## sources/user-network-fs/go-fuse/fuse/attr_unix.go

Purpose: non-Linux Unix conversion from `syscall.Stat_t` to FUSE `Attr`.

Important APIs/types/functions: `Attr.FromStat` maps inode, size, blocks, `Atimespec`/`Mtimespec`/`Ctimespec`, mode, nlink, uid, gid, rdev, and block size.

Control flow: build-tag-selected direct conversion for Darwin/FreeBSD-style stat fields.

State and persistence: no state; mutates the destination attribute object.

Dependencies and integration: supports loopback and nodefs/pathfs metadata on non-Linux platforms.

Risks and test signals: platform field names differ from Linux. Errors appear as wrong stat output, permissions, or cache behavior on non-Linux CI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/attr_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/bufferpool.go -->
## sources/user-network-fs/go-fuse/fuse/bufferpool.go

Purpose: explicit page-aligned buffer reuse to reduce GC overhead while communicating with the FUSE device.

Important APIs/types/functions: `bufferPool` stores `sync.Pool`s indexed by page count and testing counters. `AllocBuffer(size)` rounds up to at least one page and returns a slice with requested length backed by a pooled page-multiple capacity. `FreeBuffer(slice)` returns page-aligned buffers to the corresponding pool. `counters` exposes outstanding allocation counts.

Control flow: allocation computes page count, obtains or creates a pool under lock, gets a backing slice, and slices it to requested size. Free validates capacity/page count and returns the full slice.

State and persistence: in-memory pool state and counters persist for the process.

Dependencies and integration: used by server request handling to bound allocation churn and interacts with `MaxInflightRequestBytes`.

Risks and test signals: wrong rounding or free accounting can cause memory bloat or buffer reuse races. `bufferpool_test.go` covers counters and request handler reuse.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/bufferpool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/bufferpool_test.go -->
## sources/user-network-fs/go-fuse/fuse/bufferpool_test.go

Purpose: verifies buffer pool allocation/free accounting and integration with server request processing.

Important APIs/types/functions: `TestBufferPool` exercises `AllocBuffer`, `FreeBuffer`, and `counters`. `readFS` implements a tiny raw FS with `Open`, `Read`, and `Lookup`. `TestBufferPoolRequestHandler` mounts it and performs reads.

Control flow: direct unit test checks page rounding and counter balance. Integration test routes kernel reads through raw callbacks and expects buffers to be returned after request completion.

State and persistence: temporary mount plus buffer pool counters. `readFS` serves static data.

Dependencies and integration: targets `fuse.Server`, `RawFileSystem`, request allocation, and read result lifecycle.

Risks and test signals: catches leaks where buffers remain checked out after requests, and regressions where read result `Done`/response paths skip frees.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/bufferpool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/constants.go -->
## sources/user-network-fs/go-fuse/fuse/constants.go

Purpose: defines portable FUSE and syscall-adjacent constants used across the package.

Important APIs/types/functions: constants include open flags, file mode bits, status-related values, FUSE IDs, and defaults shared by mount and protocol code.

Control flow: no executable flow; compile-time values are imported by request handlers, mount code, and adapters.

State and persistence: none.

Dependencies and integration: platform-specific constants files fill in values that differ across Linux and FreeBSD.

Risks and test signals: incorrect constants break wire protocol interpretation or option negotiation. Failures surface broadly in mount, open, mode, and xattr tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/constants.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/constants_freebsd.go -->
## sources/user-network-fs/go-fuse/fuse/constants_freebsd.go

Purpose: FreeBSD-specific definitions for syscall open flag constants that are not directly shared with Linux.

Important APIs/types/functions: defines `syscall_O_LARGEFILE` and `syscall_O_NOATIME` as FreeBSD-compatible bit values.

Control flow: compile-time constant selection through build constraints.

State and persistence: none.

Dependencies and integration: used by flag formatting and open request handling code that wants consistent symbolic support across OSes.

Risks and test signals: wrong values can misreport or mishandle open flags on FreeBSD. Coverage depends on FreeBSD builds/tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/constants_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/constants_linux.go -->
## sources/user-network-fs/go-fuse/fuse/constants_linux.go

Purpose: Linux-specific syscall open flag aliases.

Important APIs/types/functions: assigns `syscall_O_LARGEFILE` and `syscall_O_NOATIME` from `syscall`.

Control flow: compile-time build selection.

State and persistence: none.

Dependencies and integration: used by debug printing and protocol flag handling.

Risks and test signals: low-risk wrapper; regressions show up as incorrect flag formatting or behavior in Linux open-path tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/constants_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/context.go -->
## sources/user-network-fs/go-fuse/fuse/context.go

Purpose: bridges FUSE caller metadata into Go `context.Context`.

Important APIs/types/functions: `Context` stores `*Caller` and implements `Deadline`, `Done`, `Err`, and `Value`. `FromContext` extracts caller data from a generic context. `NewContext` attaches caller metadata using a private key.

Control flow: raw request handling can wrap contexts with caller metadata; high-level code retrieves it without depending on concrete context type.

State and persistence: context values are per-request transient state.

Dependencies and integration: used by high-level fs/nodefs/pathfs callbacks to access UID/GID/PID or request ownership.

Risks and test signals: incorrect context propagation breaks permission-sensitive filesystems and idmapped/default-permission behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/defaultraw.go -->
## sources/user-network-fs/go-fuse/fuse/defaultraw.go

Purpose: null implementation of `RawFileSystem` for embedding by custom filesystems.

Important APIs/types/functions: `NewDefaultRawFileSystem` returns `defaultRawFileSystem`. Methods implement all `RawFileSystem` callbacks, generally returning `ENOSYS`, `EIO`, or no-op success where appropriate, with `String`, `Init`, `OnUnmount`, and `SetDebug`.

Control flow: embedded implementations override selected methods; unimplemented operations receive consistent kernel errors.

State and persistence: stateless singleton-style implementation.

Dependencies and integration: used by tests and user filesystems that want to implement only a subset of raw operations.

Risks and test signals: default status choices influence kernel behavior. For example, `ENOSYS` may disable future kernel calls for some operations, so changes are compatibility-sensitive.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/defaultraw.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/direntry.go -->
## sources/user-network-fs/go-fuse/fuse/direntry.go

Purpose: encodes and decodes FUSE directory entry records for READDIR and READDIRPLUS responses.

Important APIs/types/functions: `DirEntry` holds name, inode, mode, and offset. `Parse` reads a kernel dirent buffer. `DirEntryList` owns output buffer state. `AddDirEntry`, `Add`, `AddDirLookupEntry`, `FixMode`, and `bytes` serialize entries and optional `EntryOut` prefixes. `modeToType` converts mode bits to dirent type.

Control flow: request handlers create a list with `NewDirEntryList`, append entries until the buffer is full, and then set `req.outPayload` to serialized bytes.

State and persistence: list state is per-request buffer plus current offset; no durable state.

Dependencies and integration: core to directory serving in raw `fuse`, `fs`, and `nodefs`.

Risks and test signals: alignment, offset, and type mistakes break `readdir`, `ls`, and READDIRPLUS. `randomtype_test.go`, `mem_test.go`, and directory stress tests exercise this code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/direntry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/direntry_darwin.go -->
## sources/user-network-fs/go-fuse/fuse/direntry_darwin.go

Purpose: Darwin-specific layout adapter for parsing raw directory entries.

Important APIs/types/functions: defines platform `dirent` struct and `nameLength` helper for Darwin getdirentries layout.

Control flow: `DirEntry.Parse` uses this platform type to interpret names and record sizes.

State and persistence: stateless struct mapping.

Dependencies and integration: build-tag companion to generic direntry parsing.

Risks and test signals: layout drift causes directory parsing errors on macOS. Directory consistency tests are the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/direntry_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/direntry_freebsd.go -->
## sources/user-network-fs/go-fuse/fuse/direntry_freebsd.go

Purpose: FreeBSD-specific raw directory entry layout support.

Important APIs/types/functions: defines platform `dirent` fields and `nameLength`.

Control flow: selected at build time for FreeBSD and used by `DirEntry.Parse`.

State and persistence: none.

Dependencies and integration: supports directory parsing in tests and loopback directory streams on FreeBSD.

Risks and test signals: incorrect struct layout affects every parsed directory entry on FreeBSD.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/direntry_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/direntry_linux.go -->
## sources/user-network-fs/go-fuse/fuse/direntry_linux.go

Purpose: Linux-specific raw `getdents` entry layout support.

Important APIs/types/functions: `dirent` mirrors Linux dirent fields and `nameLength` computes name bytes from record length.

Control flow: generic directory parsing reads this structure from byte buffers.

State and persistence: stateless.

Dependencies and integration: used by `NewLoopbackDirStream` and directory tests on Linux.

Risks and test signals: bad name length or alignment produces corrupted directory names or skipped entries; readdir stress tests expose this quickly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/direntry_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/misc.go -->
## sources/user-network-fs/go-fuse/fuse/misc.go

Purpose: miscellaneous helpers for status conversion, owner discovery, and timestamp conversion.

Important APIs/types/functions: `Status.String`, `Status.Ok`, `ToStatus(error)`, `CurrentOwner`, and `UtimeToTimespec`. `ToStatus` maps nil to `OK`, syscall errors to negative statuses, and unknown errors to `EIO`.

Control flow: adapters call `ToStatus` around syscalls and Go file operations. `UtimeToTimespec` translates nil to platform `UTIME_OMIT`.

State and persistence: `CurrentOwner` reads process uid/gid; otherwise stateless.

Dependencies and integration: widely used by loopback, nodefs, pathfs, and raw server replies.

Risks and test signals: wrong error mapping changes kernel-visible errno. `misc_test.go` covers representative conversions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/misc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/misc_darwin.go -->
## sources/user-network-fs/go-fuse/fuse/misc_darwin.go

Purpose: Darwin-specific fallback constant for omitting utimens fields.

Important APIs/types/functions: defines `_UTIME_OMIT = -2`.

Control flow: used by timestamp conversion helpers when a time pointer is nil.

State and persistence: none.

Dependencies and integration: supports `UtimeToTimespec` and Darwin file timestamp updates.

Risks and test signals: wrong omit value can accidentally set timestamps instead of preserving them on macOS.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/misc_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/misc_test.go -->
## sources/user-network-fs/go-fuse/fuse/misc_test.go

Purpose: unit tests for error-to-FUSE-status conversion.

Important APIs/types/functions: `TestToStatus` passes nil, `syscall.Errno`, and wrapped/ordinary errors into `ToStatus`.

Control flow: table-style assertions check that known syscall errors map to matching status codes and unknown errors map to `EIO`.

State and persistence: no state.

Dependencies and integration: validates `misc.go`, which is used by all syscall-backed adapters.

Risks and test signals: protects errno compatibility; broad filesystem behavior depends on this conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/misc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/misc_unix.go -->
## sources/user-network-fs/go-fuse/fuse/misc_unix.go

Purpose: Unix-specific `_UTIME_OMIT` value for timestamp syscalls.

Important APIs/types/functions: defines `_UTIME_OMIT = unix.UTIME_OMIT`.

Control flow: selected on platforms with `golang.org/x/sys/unix` support.

State and persistence: none.

Dependencies and integration: used by `UtimeToTimespec` and file timestamp update paths.

Risks and test signals: timestamp preservation during `utimens` and setattr depends on correct value.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/misc_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/mount.go -->
## sources/user-network-fs/go-fuse/fuse/mount.go

Purpose: shared mount plumbing for inherited FUSE file descriptors and fd reservation.

Important APIs/types/functions: package-level `reservedFDs` holds pipes to keep fd 3 from accidentally becoming a FUSE fd. `init` reserves low fds. `getConnection(local *os.File)` reads an fd sent over a Unix socket using `ReadMsgUnix` and `SCM_RIGHTS`.

Control flow: OS-specific mount helpers create socket pairs and privileged helper processes; `getConnection` receives the opened `/dev/fuse` fd from the helper.

State and persistence: `reservedFDs` intentionally leaks low-numbered descriptors for process lifetime to avoid helper deadlocks.

Dependencies and integration: used by Darwin/Linux mount helpers and mount tests.

Risks and test signals: fd handling is delicate. Incorrect reservation or control-message parsing can deadlock mounting or receive the wrong fd.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/mount_darwin.go -->
## sources/user-network-fs/go-fuse/fuse/mount_darwin.go

Purpose: macOS mount and unmount implementation using macFUSE/osxfuse helper binaries.

Important APIs/types/functions: `getMaxWrite` returns 1 MiB. `unixgramSocketpair` creates a socketpair. `mount` invokes `mount_macfuse`/`mount_osxfuse` with environment variables and fd 3 communication, receives the FUSE fd, and reports helper completion on `ready`. `unmount` calls `syscall.Unmount`. `fusermountBinary` locates helper paths.

Control flow: create socketpair, start helper with remote socket as extra file, receive fd with `getConnection`, set close-on-exec, and asynchronously wait for helper after server startup.

State and persistence: mount state is kernel state plus helper process lifecycle; no Go persistent data beyond fd ownership.

Dependencies and integration: plugs into `fuse.NewServer` on Darwin.

Risks and test signals: helper path, fd inheritance, and delayed helper wait are fragile. Failures appear as mount timeouts or missing FUSE fd on macOS.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/mount_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/mount_freebsd.go -->
## sources/user-network-fs/go-fuse/fuse/mount_freebsd.go

Purpose: FreeBSD mount and unmount implementation using `mount_fusefs`.

Important APIs/types/functions: `getMaxWrite`, `callMountFuseFs`, `mount`, `unmount`, and `fusermountBinary`. The code opens `/dev/fuse`, forks `mount_fusefs --safe`, passes fd 3, waits for helper status, and returns the device fd.

Control flow: direct raw fd management avoids Go GC closing descriptors. Errors close fds through deferred cleanup. `mount` coordinates helper completion with server readiness.

State and persistence: kernel mount and `/dev/fuse` fd are the primary state; file descriptors must remain open for mount lifetime.

Dependencies and integration: FreeBSD-specific backend for `fuse.NewServer`.

Risks and test signals: fd lifetime and helper exit interpretation are key risks. FreeBSD CI/mount tests are needed for coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/mount_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/mount_linux.go -->
## sources/user-network-fs/go-fuse/fuse/mount_linux.go

Purpose: Linux mount/unmount implementation supporting direct `mount(2)`, fusermount helper, `/dev/fd/N` inherited mounts, option assembly, and max-write limits.

Important APIs/types/functions: `unixgramSocketpair`, `mountDirect`, `callFusermount`, `mount`, `unmount`, `lookPathFallback`, `fusermountBinary`, `umountBinary`, `getMaxWrite`, and `maxPageLimit`.

Control flow: `mount` handles `/dev/fd/N`, strict/direct mount, or fusermount fallback. Direct mount opens `/dev/fuse`, builds `fd=`, rootmode, user/group, max_read, and option strings, then calls `syscall.Mount`. Fusermount starts helper, receives fd over socket, and waits asynchronously. `unmount` tries direct unmount or helper fallback.

State and persistence: mount state is kernel-managed; Go owns the `/dev/fuse` fd and helper process state. Mount options encode persistent kernel behavior for the mount lifetime.

Dependencies and integration: central Linux backend for all FUSE server tests, including direct mount, idmapped mount, and max write negotiation.

Risks and test signals: option escaping, fd passing, privilege fallback, and max page detection are high-risk. `mount_linux_test.go` covers major branches.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/mount_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/mount_linux_test.go -->
## sources/user-network-fs/go-fuse/fuse/mount_linux_test.go

Purpose: Linux integration tests for mount option handling, direct mount behavior, inherited `/dev/fd/N`, suid/dev flags, and max-write negotiation.

Important APIs/types/functions: `TestMountDevFd`, `TestMountMaxWrite`, `mountCheckOptions`, `TestDirectMount`, `TestDirectMountDevSuid`, and `TestEscapedMountOption`.

Control flow: tests mount small raw filesystems under different `MountOptions`, inspect mountinfo and syscall stat results, verify helper/direct flags, and unmount cleanly.

State and persistence: temporary mountpoints and kernel mount table entries are created for each test.

Dependencies and integration: uses Linux mountinfo parsing, raw FUSE mount code, and environment privileges.

Risks and test signals: tests are environment-sensitive but critical for preventing regressions in option escaping, mount security flags, and max request sizes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/mount_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/api.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/api.go

Purpose: deprecated inode-oriented high-level API predating `fs`.

Important APIs/types/functions: `Node` interface defines inode tree, namespace, attributes, xattrs, file I/O, locks, and statfs callbacks. `File` interface defines open-file operations and lifecycle. `WithFlags` carries open file plus FUSE/open flags. `Options` configures timeouts, owner rewriting, debug, and lookup behavior.

Control flow: `FileSystemConnector` translates raw FUSE requests to `Node` and `File` methods; users embed default implementations and override methods.

State and persistence: implementations own their node and file state; connector manages inode/file handles and lookup counts.

Dependencies and integration: bridges to `fuse.RawFileSystem` and underlies deprecated `pathfs`.

Risks and test signals: API is broad and concurrency-sensitive. Incorrect Node/File implementations can leak handles or mis-handle kernel forgets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/defaultfile.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/defaultfile.go

Purpose: null `File` implementation for embedding in nodefs file objects.

Important APIs/types/functions: `NewDefaultFile` returns a `File` whose operations return `ENOSYS` or no-op values. Methods include read/write, locks, flush, release, getattr, fsync, utimens, truncate, ownership, mode, and allocation.

Control flow: user file types embed/compose this and override supported operations.

State and persistence: stateless and nil-receiver friendly.

Dependencies and integration: used by `dataFile`, `devNullFile`, custom tests, and user code.

Risks and test signals: default return codes influence kernel fallback behavior. It must continue satisfying the full `File` interface as APIs evolve.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/defaultfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/defaultnode.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/defaultnode.go

Purpose: null `Node` implementation for embedding in nodefs nodes.

Important APIs/types/functions: `NewDefaultNode` returns a node that stores its inode pointer and implements mount hooks, lookup, namespace operations, xattrs, attrs, locks, read/write, and metadata operations with default errors or no-ops.

Control flow: callbacks return `ENOSYS`, `ENOENT`, or reasonable defaults. `OpenDir` can synthesize entries from known children when no custom directory reader exists.

State and persistence: stores only the associated `*Inode`; user embedding types provide actual state.

Dependencies and integration: baseline for `memNode`, tests, and user nodefs implementations.

Risks and test signals: defaults must be compatible with kernel expectations; wrong default errors can change user-visible read-only behavior or directory listing semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/defaultnode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/dir.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/dir.go

Purpose: directory response adapter for nodefs connector.

Important APIs/types/functions: `connectorDir` implements raw directory reads. `ReadDir` and `ReadDirPlus` pull directory entries from a node, add entries to `fuse.DirEntryList`, and include lookup entries for READDIRPLUS. `rawDir` captures directory-reading behavior.

Control flow: for each kernel directory read, the connector resolves the inode, obtains children or calls node `OpenDir`, serializes entries, and updates lookup counts for plus entries.

State and persistence: per-request state is the dir entry list; persistent state is inode children and lookup counts managed elsewhere.

Dependencies and integration: connects `nodefs.Inode` children with raw `fuse.DirEntryList`.

Risks and test signals: READDIRPLUS lookup accounting and directory offsets are tricky. Directory tests and handle count tests expose issues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/dir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/fileless_test.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/fileless_test.go

Purpose: tests nodefs support for files that return no file handle and serve reads directly from the node.

Important APIs/types/functions: `nodeReadNode` implements `Open`, `Read`, `GetAttr`, and `Lookup`. `newNodeReadNode` configures no-open and directory modes. `TestNoOpen` and `TestNodeRead` mount variants and read through the kernel.

Control flow: lookup creates child nodes, open may return nil, and read is dispatched to node-level `Read` when no `File` handle exists.

State and persistence: data is held in `nodeReadNode` byte slices. No durable backing store.

Dependencies and integration: targets rawBridge dispatch in `nodefs/fsops.go` for nil file handle paths.

Risks and test signals: protects no-open support and direct node read fallback. Regressions can cause `EBADF`, `ENOSYS`, or nil dereference.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/fileless_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/files.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/files.go

Purpose: built-in nodefs `File` implementations for memory data, `/dev/null`, loopback files, locks, and read-only wrappers.

Important APIs/types/functions: `NewDataFile`, `dataFile.Read/GetAttr`; `NewDevNullFile`; `NewLoopbackFile`, `loopbackFile` read/write/release/flush/fsync/locks/truncate/chmod/chown/getattr; `NewReadOnlyFile` and `readOnlyFile` deny mutating operations.

Control flow: loopback reads return `fuse.ReadResultFd` for zero-copy reads, writes use `WriteAt`, flush closes a dup fd, release closes the real file, and lock operations map FUSE locks to `flock` or OFD `fcntl` locks.

State and persistence: loopback file state is an `*os.File` protected by a mutex. DataFile stores immutable bytes in memory. ReadOnlyFile wraps inner state.

Dependencies and integration: used by nodefs loopback/pathfs and tests. Platform-specific files add allocation and utimens.

Risks and test signals: fd reuse races and close/read concurrency are core risks; mutexes and tests around fd leaks and locks protect this behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/files.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/files_darwin.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/files_darwin.go

Purpose: Darwin-specific loopback file allocation and timestamp update support.

Important APIs/types/functions: `loopbackFile.Allocate` uses `F_PREALLOCATE` via `fcntl`. `timeToTimeval` converts Go time to timeval. `loopbackFile.Utimens` emulates utimens behavior using `Futimes` and helper filling for omitted times.

Control flow: lock file, invoke platform syscall, map errno/status. For nil atime/mtime, read current attrs before building timeval array.

State and persistence: mutates underlying file allocation/timestamps on disk.

Dependencies and integration: complements generic `loopbackFile` on macOS and uses `internal/utimens`.

Risks and test signals: pre-High-Sierra timestamp emulation can race with concurrent updates. Platform tests are needed for coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/files_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/files_linux.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/files_linux.go

Purpose: Linux-specific loopback file allocation and timestamp updates.

Important APIs/types/functions: `loopbackFile.Allocate` wraps `syscall.Fallocate`. `loopbackFile.Utimens` builds two `Timespec`s using `fuse.UtimeToTimespec` and calls `futimens`.

Control flow: lock file fd, call syscall, convert errors to `fuse.Status`.

State and persistence: mutates underlying file allocation and timestamps on disk.

Dependencies and integration: used by nodefs loopback files and POSIX truncate/fallocate/timestamp tests.

Risks and test signals: keep-size/allocation mode support depends on kernel and filesystem. Errors propagate to FUSE callers through `ToStatus`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/files_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/files_test.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/files_test.go

Purpose: placeholder/minimal test file for nodefs file implementations.

Important APIs/types/functions: contains package/test scaffolding only, ensuring the test package compiles with file implementation code.

Control flow: no substantive runtime flow in the file itself.

State and persistence: none.

Dependencies and integration: participates in `go test` package compilation.

Risks and test signals: value is mostly compile coverage; behavioral coverage lives in other nodefs tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/files_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/fsconnector.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/fsconnector.go

Purpose: core nodefs connector state machine translating kernel inode handles to Go `Inode` objects.

Important APIs/types/functions: `FileSystemConnector`, `NewOptions`, `NewFileSystemConnector`, `Server`, `SetDebug`, `verify`, `childLookup`, `toInode`, `lookupUpdate`, `forgetUpdate`, `InodeHandleCount`, `Node`, `LookupNode`, `mountRoot`, `Mount`, and `Unmount`.

Control flow: constructor creates root inode, mounts it, registers root lookup count, and later raw operations use `toInode`/lookup/forget paths. Lookup increments handle counts; forget decrements, potentially deleting nodes when deletable. Submount helpers attach additional roots.

State and persistence: maintains `inodeMap`, root node, server pointer, debug flag, and `lookupLock`. This is long-lived mount state, not durable beyond process.

Dependencies and integration: backs `nodefs.RawFS`, mount helpers, notification support, and pathfs.

Risks and test signals: lookup/forget races, stale handles, and submount lifecycle are high risk. Handle tests and fileless tests cover parts of this logic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/fsconnector.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/fsmount.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/fsmount.go

Purpose: nodefs mount metadata and open-file handle support for mounted inode subtrees.

Important APIs/types/functions: `openedFile` stores a registered regular file or open directory plus `WithFlags`. `fileSystemMount` stores mount/root/parent inodes, `Options`, `treeLock`, `openFiles`, debug flag, and connector. Methods include `mountName`, `setOwner`, `fillEntry`, `fillAttr`, `getOpenedFile`, `unregisterFileHandle`, `registerFileHandle`, and `negativeEntry`.

Control flow: raw open/create/opendir paths register `File` or `connectorDir` objects into the mount's handle map, flatten nested `WithFlags`, attach the file to the inode, and return handle 0 for handleless opens. Release paths unregister the handle and remove it from the inode's open-file slice. Entry/attr helpers apply timeout and owner options before returning protocol structs.

State and persistence: mount records, open file handles, tree locks, and timeout/owner options are in-memory mount-lifetime state. Backing persistence belongs to the node/file implementation.

Dependencies and integration: used by `FileSystemConnector.Mount`, `Unmount`, and `fsops` lookup redirection.

Risks and test signals: handleless-open handling, open-file slice removal, nested `WithFlags`, and negative entry timeouts are sensitive. Handle and fileless tests provide direct signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/fsmount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/fsops.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/fsops.go

Purpose: raw FUSE operation implementation for nodefs by adapting protocol structs to `Node` and `File` callbacks.

Important APIs/types/functions: `FileSystemConnector.RawFS`, `rawBridge`, and methods for `Lookup`, `Forget`, `GetAttr`, `OpenDir`, `ReadDir`, `ReadDirPlus`, `Open`, `SetAttr`, namespace ops, xattrs, `Create`, `Release`, `Read`, `Write`, locks, `StatFs`, `Flush`, `CopyFileRange`, `Lseek`, `Statx`, `OnUnmount`, and `Ioctl`.

Control flow: each raw request resolves an inode/file handle, builds a `fuse.Context`, invokes node or file methods, fills protocol outputs, and updates handle/lookup tables. Create/open register files; release/forget unregister.

State and persistence: mutates connector inode map, inode file lists, lookup counts, and file handle maps. Backing persistence is delegated to nodes/files.

Dependencies and integration: core bridge between `fuse.Server` and deprecated nodefs API.

Risks and test signals: nil file handles, concurrent close/stat, lookup/forget ordering, and xattr sizing are high risk. `fileless_test.go`, `handle_test.go`, and broader FUSE tests cover these paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/fsops.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/fuse.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/fuse.go

Purpose: convenience mounting functions for deprecated nodefs filesystems.

Important APIs/types/functions: `Mount` creates a `FileSystemConnector`, creates a `fuse.Server` from its raw FS, starts serving, waits for mount, and returns server/connector. `MountRoot` mounts with default raw mount options.

Control flow: build connector, mount server, launch serve goroutine, wait for mount readiness, then expose lifecycle objects to caller.

State and persistence: connector owns inode/file state; server owns kernel fd and mount lifecycle.

Dependencies and integration: nodefs equivalent of modern `fs.Mount`.

Risks and test signals: failure handling mirrors raw server mount behavior. Users must unmount to release kernel and connector state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/fuse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/handle.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/handle.go

Purpose: portable handle map for converting Go objects to stable uint64 FUSE handles with lookup counts and generations.

Important APIs/types/functions: `handleMap` interface, `handled` embedded metadata, `_ALREADY_MSG`, `portableHandleMap`, `newPortableHandleMap`, `Register`, `Handle`, `Count`, `Decode`, `Forget`, and `Has`.

Control flow: registering assigns a new handle/generation, stores object, and initializes lookup count. Additional lookups increment counts. `Forget` decrements and removes the object when count reaches zero, clearing object handle metadata.

State and persistence: process-local maps from handles to objects and object metadata. No durable state.

Dependencies and integration: used for inode and file handle maps in nodefs connector.

Risks and test signals: generation reuse, double registration, and lookup count underflow are critical. `handle_test.go` directly covers these cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/handle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/handle_test.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/handle_test.go

Purpose: unit tests for portable handle map behavior.

Important APIs/types/functions: `markSeen` checks panic messages. Tests cover lookup counts, basic register/decode/forget, multiple objects, generation changes after reuse, and known generation behavior.

Control flow: tests register `handled` objects, call map operations, assert counts and decoded pointers, and verify panics for invalid double registration.

State and persistence: in-memory handle maps only.

Dependencies and integration: validates `handle.go`, which protects nodefs inode/file lifetime semantics.

Risks and test signals: failures here indicate potential stale inode/file handle reuse visible to the kernel.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/handle_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/inode.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/inode.go

Purpose: nodefs in-memory inode tree representation and child/file bookkeeping.

Important APIs/types/functions: `parentData`, `Inode`, `newInode`, `String`, `AnyFile`, `Children`, `Parent`, `FsChildren`, `Node`, `Files`, `IsDir`, `NewChild`, `GetChild`, `AddChild`, `TreeWatcher`, `RmChild`, `addChild`, `rmChild`, `mountFs`, `canUnmount`, `getMountDirEntries`, and `verify`.

Control flow: nodes add/remove children under tree locks, maintain parent references, track open files, and expose snapshots to readers. Mount helpers annotate inodes with mount metadata and verify invariants when paranoia is enabled.

State and persistence: all inode tree, child maps, parent links, and open file slices are in memory.

Dependencies and integration: used throughout nodefs connector and pathfs translation.

Risks and test signals: concurrent mutation, stale parent data, and unmount with active files are primary risks. Memnode and connector tests exercise these structures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/inode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/lockingfile.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/lockingfile.go

Purpose: thread-safe wrapper for nodefs `File` implementations.

Important APIs/types/functions: `lockingFile` wraps a `File` with a mutex and delegates all operations while serializing access. Constructor helpers create the wrapper.

Control flow: each file method locks, calls the inner file, and unlocks. `InnerFile` exposes the wrapped file for unwrapping chains.

State and persistence: wrapper holds mutex and inner file reference; underlying file owns durable or in-memory data.

Dependencies and integration: useful for non-thread-safe file implementations returned to nodefs.

Risks and test signals: serialization avoids races but can deadlock if inner file calls back into code expecting the same lock. Behavioral coverage is indirect through concurrent file tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/lockingfile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/memnode.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/memnode.go

Purpose: simple deprecated nodefs in-memory filesystem backed by temporary on-disk files for file content.

Important APIs/types/functions: `NewMemNodeFSRoot`, `memNodeFs`, `memNode`, `memNodeFile`, and methods for tree creation, filename mapping, mkdir/unlink/rmdir/symlink/rename/link/create/open/getattr/truncate/utimens/chmod/chown.

Control flow: filesystem allocates temp files under a prefix, creates nodes for directories/files/symlinks, and maps inode operations to temp file operations. `memNodeFile.Flush` syncs data back to node metadata as needed.

State and persistence: tree metadata is in memory; file contents are stored in temp files under the prefix and removed with lifecycle cleanup.

Dependencies and integration: used by nodefs examples/tests and POSIX-style validation of nodefs.

Risks and test signals: temp-file cleanup, rename/link bookkeeping, and metadata consistency are risk areas. `memnode_test.go` exercises core operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/memnode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/memnode_test.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/memnode_test.go

Purpose: tests for deprecated nodefs memory filesystem behavior.

Important APIs/types/functions: tests construct `NewMemNodeFSRoot`, mount it through nodefs, create/read/write/rename/remove files and directories, and verify visible results.

Control flow: each test mounts the memnode root into a temp mountpoint, performs filesystem operations through the kernel, and unmounts.

State and persistence: in-memory tree plus temporary backing files created by `memnode.go`.

Dependencies and integration: validates `memNode`, `FileSystemConnector`, and raw FUSE dispatch working together.

Risks and test signals: detects regressions in basic namespace mutation, file content persistence during mount lifetime, and cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/memnode_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/syscall_linux.go -->
## sources/user-network-fs/go-fuse/fuse/nodefs/syscall_linux.go

Purpose: Linux syscall wrapper used by nodefs file timestamp updates.

Important APIs/types/functions: `futimens` wraps the appropriate Linux syscall for setting file descriptor timestamps from `Timespec` values.

Control flow: called by `loopbackFile.Utimens` after building atime/mtime timespecs.

State and persistence: mutates timestamps of the file referenced by fd.

Dependencies and integration: Linux companion to `files_linux.go`.

Risks and test signals: syscall number/signature mistakes break `utimens` through nodefs loopback files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/nodefs/syscall_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/opcode.go -->
## sources/user-network-fs/go-fuse/fuse/opcode.go

Purpose: raw FUSE opcode registry and dispatch functions for protocol requests.

Important APIs/types/functions: opcode constants, `doInit`, operation-specific `do*` handlers, `operationHandler`, `operationHandlers`, `operationName`, `getHandler`, and `checkFixedBufferSize`. Handlers parse request input, call `RawFileSystem`, fill output structs, and set status.

Control flow: package init builds handler table names, functions, input/output sizes, filename counts, and suppress-reply flags. Runtime request processing finds handlers by opcode and invokes the appropriate `do*` function.

State and persistence: global handler table and `maxInputSize`; server-specific state includes kernel settings, options, and notify retrieve tables.

Dependencies and integration: core dispatch layer used by `protocolServer` and every raw/high-level FS.

Risks and test signals: protocol layout, capability negotiation, xattr sizing, forget handling, and fixed buffer sizes are high risk. Many tests indirectly cover this; platform opcode tests cover extensions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/opcode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/opcode_darwin.go -->
## sources/user-network-fs/go-fuse/fuse/opcode_darwin.go

Purpose: Darwin-specific registration for macFUSE monitor opcode.

Important APIs/types/functions: `_OP_MONITOR`, `doMonitor`, and init-time `operationHandlers[_OP_MONITOR]` entry with `MonitorIn` input.

Control flow: monitor notifications suppress replies and do not call filesystem handlers.

State and persistence: mutates global opcode handler table at init.

Dependencies and integration: extends `opcode.go` for macFUSE-specific advisory events.

Risks and test signals: missing registration can break macFUSE notifications. `opcode_darwin_test.go` verifies the handler exists.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/opcode_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/opcode_darwin_test.go -->
## sources/user-network-fs/go-fuse/fuse/opcode_darwin_test.go

Purpose: unit test for Darwin monitor opcode registration.

Important APIs/types/functions: `TestMonitorOpcodeRegistered` calls `getHandler(_OP_MONITOR)` and checks name and function.

Control flow: simple registration assertion during Darwin test builds.

State and persistence: reads global handler table.

Dependencies and integration: validates `opcode_darwin.go` init side effect.

Risks and test signals: catches accidental removal or overwrite of the macFUSE monitor handler.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/opcode_darwin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/opcode_linux.go -->
## sources/user-network-fs/go-fuse/fuse/opcode_linux.go

Purpose: Linux-specific registration and dispatch for FUSE `STATX`.

Important APIs/types/functions: `doStatx` parses `StatxIn`, fills `StatxOut`, and calls `RawFileSystem.Statx`. init registers `_OP_STATX` handler with sizes and types.

Control flow: global handler table is extended after generic opcode init and fixed buffer size is rechecked.

State and persistence: global opcode table mutation; no per-request persistent state beyond output filling.

Dependencies and integration: supports Linux statx syscalls through `fuse.Server`, high-level `fs`, and loopback tests.

Risks and test signals: handler size mismatches can corrupt request parsing. `fs/statx_linux_test.go` is the main behavioral signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/opcode_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/passthrough_linux.go -->
## sources/user-network-fs/go-fuse/fuse/passthrough_linux.go

Purpose: Linux support for registering kernel passthrough backing file descriptors.

Important APIs/types/functions: ioctl constants `_DEV_IOC_BACKING_OPEN` and `_DEV_IOC_BACKING_CLOSE`; `Server.RegisterBackingFd(*BackingMap)` and `Server.UnregisterBackingFd(id int32)`.

Control flow: methods serialize ioctl calls with `writeMu`, call `SYS_IOCTL` on the mount fd, log when debug is enabled, and return kernel id/errno.

State and persistence: kernel stores backing fd registrations until unregistered or mount teardown. Server mutex protects mount fd writes.

Dependencies and integration: used by high-level loopback passthrough support and tested by `fs/passthrough_test.go`.

Risks and test signals: registration lifecycle leaks or inconsistent ids can bypass wrong files. Requires kernel capability and elevated privileges in tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/passthrough_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/api.go -->
## sources/user-network-fs/go-fuse/fuse/pathfs/api.go

Purpose: deprecated path-based filesystem API layered on nodefs.

Important APIs/types/functions: `FileSystem` interface defines path-string callbacks for attrs, namespace mutation, xattrs, mount hooks, open/create, directory reads, symlinks, and statfs. `PathNodeFsOptions` configures client inode usage and debug.

Control flow: `PathNodeFs` translates inode requests into path strings and calls this interface; implementations usually embed `NewDefaultFileSystem`.

State and persistence: API itself owns no state; implementers store backing path or virtual tree state.

Dependencies and integration: depends on `fuse.Context` and `nodefs.File`, and is marked deprecated in favor of `fs`.

Risks and test signals: path-based APIs are simpler but can struggle with hardlinks, renames, and concurrent mutation. Loopback/pathfs tests cover common behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/copy.go -->
## sources/user-network-fs/go-fuse/fuse/pathfs/copy.go

Purpose: helper to copy a file between two pathfs filesystems through their public interfaces.

Important APIs/types/functions: `CopyFile(srcFs, destFs FileSystem, srcFile, destFile string, context *fuse.Context) fuse.Status`.

Control flow: open source read-only, get source attrs, create/truncate destination with source mode, then loop reading 128 KiB chunks and writing them at increasing offsets. Releases and flushes both files with defers. Short writes return `EIO`.

State and persistence: persists data into the destination filesystem; source is read only.

Dependencies and integration: uses `FileSystem.Open`, `GetAttr`, `Create`, and nodefs `File` read/write/flush/release APIs.

Risks and test signals: lacks sparse-file/xattr preservation and assumes offset writes succeed fully. `copy_test.go` covers basic overwrite behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/copy_test.go -->
## sources/user-network-fs/go-fuse/fuse/pathfs/copy_test.go

Purpose: tests basic `CopyFile` behavior between loopback pathfs instances.

Important APIs/types/functions: `TestCopyFile` creates two temp dirs, wraps them with `NewLoopbackFileSystem`, writes source content, calls `CopyFile`, then verifies destination content. It repeats in reverse to confirm overwrite.

Control flow: file data is written to one backing dir, copied through pathfs APIs, read from the other backing dir, then copied back.

State and persistence: uses real temp-directory files as durable test data.

Dependencies and integration: validates pathfs loopback plus nodefs file read/write behavior indirectly.

Risks and test signals: covers normal copy and overwrite only; not permissions, partial writes, large files, or error cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/copy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/default.go -->
## sources/user-network-fs/go-fuse/fuse/pathfs/default.go

Purpose: null implementation of deprecated pathfs `FileSystem`.

Important APIs/types/functions: `NewDefaultFileSystem` returns `defaultFileSystem`; methods return `ENOSYS`, `ENOENT`, empty xattr values, no-op mount hooks, and nil statfs as appropriate.

Control flow: user path filesystems embed it and override only supported path operations.

State and persistence: stateless.

Dependencies and integration: baseline for pathfs examples and wrappers.

Risks and test signals: default errno choices affect kernel feature probing and read-only behavior. Compile coverage ensures it satisfies the full interface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/default.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/locking.go -->
## sources/user-network-fs/go-fuse/fuse/pathfs/locking.go

Purpose: serializing wrapper for pathfs `FileSystem` implementations that are not internally thread-safe.

Important APIs/types/functions: `lockingFileSystem`, `NewLockingFileSystem`, `locked`, and delegated methods for attrs, namespace operations, xattrs, mount hooks, open/create, directory reads, symlink/readlink, and statfs.

Control flow: most methods acquire a mutex via `locked()` defer-unlock pattern, call the wrapped filesystem, and return its result. `Create` locks while creating and wraps the returned file with `nodefs.NewLockingFile`; `Open` wraps the returned file with the same mutex without taking the filesystem lock around the open call in this file.

State and persistence: wrapper stores a mutex and inner filesystem; persistent data belongs to the inner filesystem.

Dependencies and integration: useful because FUSE dispatches operations concurrently.

Risks and test signals: coarse locking can reduce concurrency and deadlock if inner callbacks call back into the wrapper. The unlocked `Open` path is a notable behavior to preserve or review carefully if tightening synchronization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/locking.go -->
