# subset-b-009558 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/serve_test.go -->
# sources/user-network-fs/bazil-fuse/fs/serve_test.go

Purpose: This is a broad integration test suite for the high-level `bazil.org/fuse/fs` server adapter. It validates that `fs.Serve` turns real kernel FUSE operations into the expected `fs.FS`, `fs.Node*`, and `fs.Handle*` method calls, and that responses, errno translation, cache behavior, notifications, polling, locking, xattrs, mmap, direct I/O, and platform differences behave as intended.

Important APIs, types, and functions: The file defines many small test-only nodes and helpers: `testPanic`, `testStatFS`, `root`, `readAll`, `write`, `mkdir1`, `create1`, `symlink1`, `link1`, `rename1`, `mknod1`, `interrupt`, `deadline`, `readDirAll*`, `chmod`, `openNonSeekable`, xattr nodes, `inMemoryFile`, invalidation nodes, poll nodes, lock nodes, `generateInodeFS`, and `fAllocateFile`. The tests exercise public interfaces such as `fs.Node`, `fs.NodeOpener`, `fs.HandleReader`, `fs.HandleWriter`, `fs.NodeCreater`, `fs.NodeMkdirer`, `fs.NodeStringLookuper`, `fs.NodePoller`, `fs.HandlePoller`, `fs.HandleLocker`, `fs.FSInodeGenerator`, and server helpers such as `InvalidateNodeAttr`, `InvalidateNodeData`, `InvalidateNodeDataRange`, `InvalidateEntry`, `NotifyDelete`, `NotifyStore`, `NotifyRetrieve`, and `NotifyPollWakeup`.

Control flow: Each test mounts a temporary FUSE filesystem with `fstestutil.MountedT` or `MountedFuncT`, spawns an HTTP/JSON helper subprocess through `spawntest`, performs a normal OS syscall or library operation against the mountpoint, and then checks the request captured by test recorders or the observable syscall result. Subprocesses are used for operations that can block, signal, mmap, poll, or hold open file descriptors without deadlocking the in-process FUSE server. Several tests normalize Linux/FreeBSD differences before comparison.

State and persistence behavior: State is intentionally in-memory and test-scoped: recorders store last requests, counters count cache hits, `atomic.Value` carries dynamic file contents, mutexes protect helper-held file descriptors, and `ReleaseWaiter` synchronizes close/release observations. Persistent effects are limited to temporary mountpoints and kernel page/dentry caches, which tests explicitly probe and invalidate. No durable repository data is written by the source under test.

Dependencies and integration points: The tests depend on `bazil.org/fuse`, `bazil.org/fuse/fs`, `fstestutil`, `record`, `spawntest`, `httpjson`, `fuseutil.HandleRead`, `golang.org/x/sys/unix`, real FUSE mount helpers, OS syscalls, and platform kernel behavior. They are an integration boundary between Go service interfaces and actual kernel FUSE clients.

Risks: These tests are environment-sensitive: they need FUSE support, mount permissions, helper binaries, `/etc/fuse.conf` for `AllowOther`, root for some mknod/sticky tests, and stable kernel cache behavior. Several assertions deliberately account for FreeBSD behavior or older Linux quirks. Cache invalidation tests can report false positives under extreme memory pressure. Locking and poll behavior are especially kernel/version-dependent.

Test signals: The file itself is the main behavioral signal for the `fs` server layer. It covers successful and failing paths, syscall errno mapping, panics, deadlines, interrupt cancellation, xattr sizing and ERANGE, direct I/O, mmap writeback, directory cache behavior, notification APIs, context injection, `runtime.Goexit`, flock/POSIX/OFD locks, generated inode values, and fallocate requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/serve_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/tree.go -->
# sources/user-network-fs/bazil-fuse/fs/tree.go

Purpose: `tree.go` provides a small read-only directory tree implementation for users who want to expose a static path hierarchy through `fs.Serve`. The tree directories are read-only, but the leaf `Node` values inserted into the tree may implement writable behavior themselves.

Important APIs, types, and functions: `Tree` embeds the internal `tree` and implements `Root() (Node, error)`. `(*Tree).Add(path string, node Node)` installs nodes by slash-separated path. Internal `treeDir` stores a basename and child node, while `tree` stores an ordered slice of entries and implements `Attr`, `Lookup`, and `ReadDirAll`.

Control flow: `Add` cleans the path by prefixing `/`, using `path.Clean`, stripping the leading slash, and splitting on `/`. It walks existing `tree` nodes, creating intermediate `tree` directories as needed. If an existing path conflicts with the new path, or a prefix is already a non-tree node, it panics. Lookup performs a linear scan. `ReadDirAll` emits `fuse.Dirent` values in insertion order.

State and persistence behavior: All state is in memory in `tree.dir`. There is no synchronization; the comment explicitly says `Add` is only safe before serving requests. Runtime request handling is read-only with no persistence beyond process memory.

Dependencies and integration points: The file integrates with the `fs` package's `Node` interfaces and the low-level `fuse.Attr` and `fuse.Dirent` types. It uses `context`, `os.FileMode`, `path`, `strings`, and `syscall.ENOENT`.

Risks: Panics are part of the configuration-time contract, so callers must avoid duplicate or overlapping paths. Directory lookup is O(n) per directory. No directory entry type or inode is set in `ReadDirAll`, so clients may need follow-up getattr calls. Concurrent mutation after serving begins is unsafe.

Test signals: This file has no direct tests in this subset, but `serve_test.go` exercises directory lookup and `ReadDirAll` behavior through similar test nodes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/tree.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuse.go -->
# sources/user-network-fs/bazil-fuse/fuse.go

Purpose: `fuse.go` is the main low-level FUSE protocol implementation. It exposes `Mount`, `Conn`, request/response types, errno conversion, kernel message parsing, response serialization, cache invalidation, notification APIs, and typed request structures used by both low-level users and the higher-level `fs` package.

Important APIs, types, and functions: Key exported types include `Conn`, `Request`, `Header`, `RequestID`, `NodeID`, `HandleID`, `Errno`, `ErrorNumber`, `Attr`, request/response pairs for lookup, getattr, xattr, open, create, mkdir, read, write, setattr, release, forget, directory entries, symlink/link/rename/mknod/fsync/interrupt/poll/lock/fallocate, and notification helpers. `Mount` applies `MountOption`s, calls the platform `mount`, then negotiates protocol features through `initMount`. `ReadRequest` decodes raw kernel messages into concrete request structs. `Respond` methods encode replies into FUSE wire structs and write them back to the kernel.

Control flow: Mounting builds a `mountConfig`, opens a kernel communication file through the OS-specific `mount`, reads the initial `initRequest`, rejects too-old protocol versions, intersects kernel flags with supported/configured flags, and sends `initResponse`. Normal serving loops call `Conn.ReadRequest`; it reads from `/dev/fuse`, validates header length, handles a FreeBSD init length quirk, then switches on opcode. Each opcode parser validates structure length and string terminators before constructing a typed request. Unknown opcodes become `UnrecognizedRequest`; malformed messages return errors. Responses flow through `Header.respond`, which fills the response unique ID, writes via `Conn.writeToKernel`, and returns the message buffer to `reqPool`.

State and persistence behavior: `Conn` owns the kernel file descriptor, negotiated protocol, feature flags, and read/write locks. Request buffers are reused through `sync.Pool`; request lifetime ends at `Respond`, `RespondError`, or no-response handling. The code does not persist filesystem data; it transports requests and replies. Notifications manipulate kernel caches but do not store durable state.

Dependencies and integration points: It depends on OS syscalls, unsafe wire-struct layout from `fuse_kernel.go`, platform `mount` and `unmount`, option configuration, and the higher-level `fs` server. Notification APIs integrate with kernel cache and poll mechanisms. Error mapping integrates Go errors, `syscall.Errno`, and custom `ErrorNumber`.

Risks: This file is protocol-critical and uses `unsafe`; struct layout and version gates must match kernel ABI. Buffer lifetime rules are strict: handlers must not retain request/response byte slices after responding. `ToErrno` intentionally does not unwrap `syscall.Errno` from wrapper errors, which avoids accidental leakage but can surprise callers. Kernel behavior differs by platform and version. Notification length checks guard name truncation but cache operations still depend on kernel support and can return `ErrNotCached`.

Test signals: `fuse_test.go` checks feature negotiation from mount options. `fuse_kernel_test.go` checks open flag masking/stringing. `serve_test.go` exercises most request/response types indirectly through real syscalls, including notifications, xattrs, locks, polling, and fallocate.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuse_freebsd.go -->
# sources/user-network-fs/bazil-fuse/fuse_freebsd.go

Purpose: This FreeBSD-specific file defines the maximum write payload size the library is prepared to receive from the kernel.

Important APIs, types, and functions: It declares `const maxWrite = 128 * 1024`, used by `fuse.go` to size request buffers and advertise `MaxWrite` during init negotiation.

Control flow: There is no runtime control flow in this file. The build tag is implicit by filename suffix; Go includes it for FreeBSD builds.

State and persistence behavior: No state or persistence.

Dependencies and integration points: `maxWrite` feeds `bufSize` and `initResponse.MaxWrite` in `fuse.go`.

Risks: The comment says the value is a guess on FreeBSD. If the kernel sends larger writes than this buffer supports, the library can reject or fail large write handling.

Test signals: Large write behavior is exercised by `serve_test.go` through `TestWriteLarge`, but no FreeBSD-only unit directly validates this constant.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuse_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuse_kernel.go -->
# sources/user-network-fs/bazil-fuse/fuse_kernel.go

Purpose: `fuse_kernel.go` is the Go representation of the FUSE kernel wire protocol. It defines protocol version limits, opcode constants, bit flags, kernel input/output structs, and formatting helpers used by `fuse.go` to parse requests and serialize replies.

Important APIs, types, and functions: It exports flag types and constants such as `AttrFlags`, `GetattrFlags`, `SetattrValid`, `OpenFlags`, `OpenRequestFlags`, `OpenResponseFlags`, `InitFlags`, `ReleaseFlags`, `ReadFlags`, `WriteFlags`, `SetxattrFlags`, `LockFlags`, `LockType`, `PollFlags`, `PollEvents`, and `FAllocateFlags`. Helpers such as `entryOutSize`, `attrOutSize`, `mknodInSize`, `mkdirInSize`, `createInSize`, `readInSize`, `writeInSize`, and `setxattrInSize` encode protocol-version-specific struct sizing. Internal structs mirror kernel ABI messages.

Control flow: The file mostly contains declarations. The key dynamic behavior is flag formatting through `flagString` and version-gated size helpers. `OpenFlags` access-mode helpers mask with `OpenAccessModeMask` because read-only/write-only/read-write are alternatives rather than independent bits.

State and persistence behavior: There is no runtime state. The declarations define how transient kernel messages are interpreted by other files.

Dependencies and integration points: It uses `syscall`, `unsafe`, and `golang.org/x/sys/unix`. `fuse.go` relies on these definitions for every message parse and response. Platform-specific `openFlags` helpers in `fuse_kernel_linux.go` and `fuse_kernel_freebsd.go` adapt OS flag quirks before values become exported `OpenFlags`.

Risks: ABI drift is the main risk. Incorrect field order, padding, version-gated sizes, opcode values, or flag constants would corrupt protocol parsing. `unsafe.Sizeof` and `unsafe.Offsetof` require the Go structs to match C kernel layout. Comments note incomplete or platform-odd behavior around FreeBSD locks, FUSE submounts, setxattr extensions, and fallocate mode support.

Test signals: `fuse_kernel_test.go` validates open access mode masking and string formatting. `serve_test.go` indirectly exercises many struct definitions by driving real kernel operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuse_kernel.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuse_kernel_freebsd.go -->
# sources/user-network-fs/bazil-fuse/fuse_kernel_freebsd.go

Purpose: This FreeBSD-specific adapter converts raw open flags from kernel messages into `OpenFlags`.

Important APIs, types, and functions: It defines `openFlags(flags uint32) OpenFlags`, returning `OpenFlags(flags)` unchanged.

Control flow: No branching; all flag bits are passed through.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Called by `fuse.go` while decoding open, read, write, create, and release requests. It pairs with `fuse_kernel_linux.go`, which masks Linux-specific ABI noise.

Risks: Passing all bits through is correct only if FreeBSD FUSE uses the same meaningful flag surface expected by the package. Other tests note FreeBSD does not always pass append/truncate/lock fields the same way Linux does.

Test signals: `serve_test.go` contains FreeBSD-specific expectations for file flags, create flags, lock behavior, and open non-seekable behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuse_kernel_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuse_kernel_linux.go -->
# sources/user-network-fs/bazil-fuse/fuse_kernel_linux.go

Purpose: This Linux-specific adapter normalizes raw open flags from FUSE kernel messages before exposing them as `OpenFlags`.

Important APIs, types, and functions: `openFlags(flags uint32) OpenFlags` clears bit `0x8000`, the 32-bit `O_LARGEFILE` bit, then converts the result to `OpenFlags`.

Control flow: The function always masks out `0x8000` and returns the remaining bits. The comments explain that this ABI bit is uninteresting for FUSE protocol consumers.

State and persistence behavior: No state or persistence.

Dependencies and integration points: Used by `fuse.go` when decoding request file flags. It makes exported open flags stable across Linux architectures and client ABI details.

Risks: If a future Linux flag meaningfully reuses this bit in FUSE context, it would be hidden. The current risk is low because the comment ties it to `O_LARGEFILE` noise.

Test signals: `serve_test.go` normalizes other Linux open flag quirks such as historical `O_CLOEXEC` leakage in some tests. `fuse_kernel_test.go` covers access mode masking after flags are converted.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuse_kernel_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuse_kernel_test.go -->
# sources/user-network-fs/bazil-fuse/fuse_kernel_test.go

Purpose: This unit test file validates `OpenFlags` access-mode helpers and string formatting.

Important APIs, types, and functions: Tests cover `OpenAccessModeMask`, `OpenReadOnly`, `OpenWriteOnly`, `OpenReadWrite`, `IsReadOnly`, `IsWriteOnly`, `IsReadWrite`, and `OpenFlags.String`.

Control flow: Each test builds an `OpenFlags` value from `os.O_*` flags, checks the masked access mode, then verifies the boolean helpers. `TestOpenFlagsString` expects combined access and modifier flags to format as `OpenReadWrite+OpenAppend+OpenSync`.

State and persistence behavior: No persistent state. Tests are deterministic and in-process.

Dependencies and integration points: Uses Go `os` constants and the public `bazil.org/fuse` API from an external test package, which helps verify exported behavior.

Risks: Coverage is intentionally narrow. It does not test all open flags, unknown flags, platform-specific `openFlags`, or kernel message decoding.

Test signals: Provides a focused regression guard for access-mode masking, which is easy to get wrong because access modes are not independent one-bit flags.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuse_kernel_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuse_linux.go -->
# sources/user-network-fs/bazil-fuse/fuse_linux.go

Purpose: This Linux-specific file defines the maximum kernel write request size supported by the library.

Important APIs, types, and functions: It declares `const maxWrite = 128 * 1024`.

Control flow: No runtime control flow.

State and persistence behavior: No state or persistence.

Dependencies and integration points: `fuse.go` uses `maxWrite` to size the request buffer and cap `initResponse.MaxWrite`. The comment ties the value to observed Linux 4.2 behavior with 32 FUSE pages of 4 KiB each.

Risks: Kernels with larger maximum page/request configurations could support larger writes than this library advertises. Because the library advertises this cap, the kernel should not send larger writes after negotiation.

Test signals: `serve_test.go` has `TestWriteLarge`, which exercises multi-request or large-buffer write behavior through the negotiated limit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuse_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuse_test.go -->
# sources/user-network-fs/bazil-fuse/fuse_test.go

Purpose: This integration test validates feature flag negotiation between mount options and the FUSE kernel during `Mount`.

Important APIs, types, and functions: `getFeatures` mounts a temporary filesystem and returns `Conn.Features()`. `TestFeatures` checks `LockingFlock`, `LockingPOSIX`, `AsyncRead`, `WritebackCache`, `CacheSymlinks`, and `ExplicitInvalidateData` mount options against negotiated `InitFlags`.

Control flow: For each subtest, the test mounts an empty temporary FUSE filesystem with selected options, reads negotiated flags, computes missing wanted bits and disallowed extra bits, and unmounts/cleans up. FreeBSD skips `InitFlockLocks` expectations because FreeBSD FUSE does not implement flock locks.

State and persistence behavior: Uses a temporary directory and a live kernel mount; all state is cleaned up through `conn.Close`, `fuse.Unmount`, and `os.RemoveAll`.

Dependencies and integration points: Depends on working FUSE mount support, platform mount helpers, and the public `fuse` API. It directly validates the `Mount` -> `initMount` -> `Conn.Features` path.

Risks: Environment-sensitive and may fail without FUSE privileges or helper binaries. It does not validate max background/congestion values or every feature bit.

Test signals: Strong signal that option-selected `InitFlags` survive negotiation and that default bare mounts do not unexpectedly enable POSIX/flock locking.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuse_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuseutil/fuseutil.go -->
# sources/user-network-fs/bazil-fuse/fuseutil/fuseutil.go

Purpose: `fuseutil.go` provides a small helper for serving read requests from an in-memory byte slice representing the entire file content.

Important APIs, types, and functions: `HandleRead(req *fuse.ReadRequest, resp *fuse.ReadResponse, data []byte)` adjusts `data` by `req.Offset` and `req.Size`, copies the selected range into `resp.Data`, and shrinks `resp.Data` to the number of copied bytes.

Control flow: If the read offset is at or beyond EOF, the helper returns an empty response. Otherwise it slices from the offset, truncates to the requested size, copies into `resp.Data[:req.Size]`, and sets `resp.Data = resp.Data[:n]`.

State and persistence behavior: Stateless. It mutates only the supplied response buffer.

Dependencies and integration points: Used by test and example handles that implement `Read`. It depends on `bazil.org/fuse` request/response types.

Risks: The caller must ensure `resp.Data` has length at least `req.Size`; otherwise `resp.Data[:req.Size]` will panic. The helper assumes `req.Offset` is non-negative as provided by kernel/FUSE semantics.

Test signals: Many `serve_test.go` read-related tests rely on this helper, including `Read`, direct read, invalidation, poll, and mmap-backed read paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fuseutil/fuseutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/mount.go -->
# sources/user-network-fs/bazil-fuse/mount.go

Purpose: `mount.go` contains shared helper logic for platform mount implementations, specifically line-based logging for mount helper stdout/stderr.

Important APIs, types, and functions: `neverIgnoreLine` always returns false. `lineLogger(wg, prefix, ignore, r)` scans an `io.ReadCloser`, logs non-ignored lines with a prefix, logs scanner errors, and calls `wg.Done` when finished.

Control flow: Platform mount functions start helper commands, obtain stdout/stderr pipes, and launch `lineLogger` goroutines. Ignore callbacks can suppress known noisy lines or capture structured errors while allowing other helper output through logging.

State and persistence behavior: No durable state. It coordinates goroutine completion through a `sync.WaitGroup` and writes to the process logger.

Dependencies and integration points: Used by `mount_linux.go` and `mount_freebsd.go`. Depends on `bufio.Scanner`, `io`, `log`, and `sync`.

Risks: `bufio.Scanner` has a default token size limit; extremely long helper lines could produce scanner errors. Logging helper output can expose environment-specific details but is valuable for mount diagnostics.

Test signals: Mount error path tests in `serve_test.go` and mount option tests indirectly exercise this logging path when helpers fail.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/mount_freebsd.go -->
# sources/user-network-fs/bazil-fuse/mount_freebsd.go

Purpose: This file implements the FreeBSD FUSE mount operation using `/dev/fuse` and `/sbin/mount_fusefs`.

Important APIs, types, and functions: `handleMountFusefsStderr` parses mount helper stderr and turns missing mountpoint messages into `MountpointDoesNotExistError`. `isBoringMountFusefsError` suppresses uninteresting exit status 1 when a better parsed error exists. `mount(dir, conf)` validates options, opens `/dev/fuse`, and runs `mount_fusefs --safe -o <opts> 3 <dir>` with the FUSE fd passed as an extra file.

Control flow: Before mounting, it rejects option keys or values containing commas because FreeBSD's helper does not support escaping. It opens `/dev/fuse`, configures command pipes and `ExtraFiles`, starts stdout/stderr loggers, waits for helper output to drain, then waits for process exit. If stderr produced a structured missing-mountpoint error, that error is returned in preference to the generic exit error.

State and persistence behavior: The live mount and `/dev/fuse` file descriptor are the only state. No repository state is written.

Dependencies and integration points: Depends on `os`, `os/exec`, `syscall`, `strings`, `sync`, logging helpers from `mount.go`, and `mountConfig.getOptions`. It is called by `Mount` in `fuse.go` on FreeBSD.

Risks: Option comma rejection is platform-specific and can surprise callers. The code assumes `/dev/fuse` and `/sbin/mount_fusefs` are available and that fd `3` is accepted by the helper. Helper output parsing is string-fragile.

Test signals: `serve_test.go` validates missing mountpoint error typing. `options_test.go` skips unsupported FSName/subtype/default permission behavior on FreeBSD and notes several FreeBSD kernel/helper differences.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/mount_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/mount_linux.go -->
# sources/user-network-fs/bazil-fuse/mount_linux.go

Purpose: This file implements Linux mounting through the `fusermount3` helper and receives the opened `/dev/fuse` fd over a Unix socket.

Important APIs, types, and functions: `handleFusermountStderr` ignores a common `/etc/fuse.conf` permission warning and parses missing mountpoint errors into `MountpointDoesNotExistError`. `isBoringFusermountError` recognizes helper exit status 1. `mount(dir, conf)` creates a socketpair, starts `fusermount3 -o <opts> -- <dir>` with `_FUSE_COMMFD=3`, and extracts the passed fd with `ParseSocketControlMessage` and `ParseUnixRights`.

Control flow: The function creates a parent/child socketpair, passes one end to `fusermount3`, logs helper stdout/stderr, waits for the helper, then converts the parent socket into `*net.UnixConn`. It reads out-of-band SCM_RIGHTS data, validates that exactly one control message and one fd were received, wraps that fd as `/dev/fuse`, and returns it to `Mount`.

State and persistence behavior: Temporary socket files/fds are closed with defers. The resulting `*os.File` represents the live kernel FUSE connection. No durable filesystem data is managed here beyond the mount itself.

Dependencies and integration points: Depends on `net`, `os`, `os/exec`, `syscall`, `sync`, `mountConfig`, and shared logging helpers. It is the Linux platform implementation behind `fuse.Mount`.

Risks: Requires `fusermount3` in PATH and user permission to mount FUSE. SCM_RIGHTS parsing assumes exactly one fd. String parsing of helper errors is brittle across helper versions/locales. If `ReadMsgUnix` returns an error, the current code proceeds to parse `oob[:oobn]` without an explicit immediate error check after the read.

Test signals: `serve_test.go` covers missing mountpoint behavior. `options_test.go` validates Linux-visible FSName/subtype/default permission/read-only option behavior. `fuse_test.go` validates negotiated flags on live mounts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/mount_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/options.go -->
# sources/user-network-fs/bazil-fuse/options.go

Purpose: `options.go` defines the public `MountOption` API and the internal `mountConfig` used to configure mount helper options and FUSE init feature flags.

Important APIs, types, and functions: `mountConfig` stores string mount options, `maxReadahead`, `initFlags`, `maxBackground`, and `congestionThreshold`. `escapeComma` escapes backslashes and commas for option strings. `getOptions` serializes the option map. Public options include `FSName`, `Subtype`, `DaemonTimeout`, `AllowOther`, `AllowDev`, `AllowSUID`, `DefaultPermissions`, `ReadOnly`, `MaxReadahead`, `AsyncRead`, `WritebackCache`, `CacheSymlinks`, `ExplicitInvalidateData`, `AllowNonEmptyMount`, `MaxBackground`, `CongestionThreshold`, `LockingFlock`, `LockingPOSIX`, and `HandleKillPriv`.

Control flow: `Mount` creates a config, then invokes each `MountOption` function. Options either add key/value strings for the platform mount helper or OR feature bits into `initFlags` for the FUSE init negotiation. `getOptions` escapes each key/value and joins with commas.

State and persistence behavior: Configuration is transient per mount. The map iteration order is not stable, but mount helpers treat options as a set.

Dependencies and integration points: Integrates with `fuse.Mount`, platform `mount` functions, and `initMount`. Feature flags are defined in `fuse_kernel.go`; platform-specific `DaemonTimeout` behavior lives in `options_freebsd.go` and `options_linux.go`.

Risks: Because options are stored in a map, duplicate keys overwrite previous values and serialized order is nondeterministic. Escaping is Linux-oriented; FreeBSD rejects commas before serialization. Some options are platform ignored or require system configuration, for example `AllowOther` needs `/etc/fuse.conf` on Linux.

Test signals: `options_test.go` validates FSName escaping for comma, whitespace, newline, and backslash; subtype; allow_other preconditions; default permissions; read-only; and mount acceptance for max background/congestion threshold.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/options_freebsd.go -->
# sources/user-network-fs/bazil-fuse/options_freebsd.go

Purpose: This FreeBSD-specific file implements `DaemonTimeout` support.

Important APIs, types, and functions: `daemonTimeout(name string) MountOption` returns an option that sets `conf.options["timeout"] = name`.

Control flow: The returned closure mutates the mount config when `Mount` applies options.

State and persistence behavior: Transient mount configuration only.

Dependencies and integration points: Used by the public `DaemonTimeout` function in `options.go`; consumed by `mount_freebsd.go` through `conf.getOptions`.

Risks: The value is a raw string, so validation is delegated to the FreeBSD mount helper. FreeBSD option serialization cannot tolerate commas.

Test signals: No direct test in this subset validates `DaemonTimeout`; FreeBSD option behavior is otherwise covered indirectly by mount option tests with platform skips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/options_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/options_helper_test.go -->
# sources/user-network-fs/bazil-fuse/options_helper_test.go

Purpose: This test-only helper exposes a way for tests to inject arbitrary mount option key/value pairs that the public safe API would normally prevent.

Important APIs, types, and functions: `ForTestSetMountOption(k, v string) MountOption` returns a mount option closure that writes `conf.options[k] = v`.

Control flow: Tests can pass this option to `Mount`; when options are applied, the raw key/value is inserted into the mount config.

State and persistence behavior: Transient test mount configuration only.

Dependencies and integration points: It is in package `fuse`, not `fuse_test`, so it can access private `mountConfig`. The lint ignore documents that the helper is used by tests such as a comma-error test outside this file's visible subset.

Risks: This bypasses validation and can produce mount helper errors. It is correctly scoped to `_test.go`.

Test signals: Its presence indicates option serialization has edge cases that require deliberate unsafe injection for coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/options_helper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/options_linux.go -->
# sources/user-network-fs/bazil-fuse/options_linux.go

Purpose: This Linux-specific file defines `DaemonTimeout` as a no-op because the option is FreeBSD-only.

Important APIs, types, and functions: `daemonTimeout(name string) MountOption` returns `dummyOption`.

Control flow: Applying this option on Linux does nothing and returns nil.

State and persistence behavior: No state changes.

Dependencies and integration points: Used by public `DaemonTimeout` in `options.go` to keep the API portable.

Risks: Callers may assume the timeout is enforced on Linux, but the `options.go` comment says non-FreeBSD platforms ignore it.

Test signals: No direct test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/options_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/options_test.go -->
# sources/user-network-fs/bazil-fuse/options_test.go

Purpose: This integration test file validates public mount options against real kernel-visible behavior.

Important APIs, types, and functions: Tests cover `FSName`, escaping of unusual FS names, `Subtype`, `AllowOther`, `DefaultPermissions`, `ReadOnly`, `MaxBackground`, and `CongestionThreshold`. Helpers include `etcFuseHasAllowOther`, `openErrHelper`, `unwritableFile`, and `createrDir`.

Control flow: Tests mount temporary FUSE filesystems with selected options, then inspect mount metadata or drive syscalls through helper subprocesses. FSName/subtype tests inspect mount info. Permission tests attempt opens/creates and check kernel-returned errnos. Max background and congestion threshold tests currently only verify mount success and contain TODOs to inspect `/sys/fs/fuse/connections`.

State and persistence behavior: Test state is temporary mountpoints and helper processes. No durable repository state is changed.

Dependencies and integration points: Depends on FUSE mounts, `/etc/fuse.conf` for `AllowOther`, `fstestutil`, `spawntest`, `httpjson`, and the `fuse/fs` server layer. FreeBSD skips unsupported options.

Risks: Environment-sensitive; tests skip or fail depending on system FUSE configuration and privileges. FSName option order is not tested because option serialization uses a map. MaxBackground/CongestionThreshold lack assertions beyond successful mount.

Test signals: Strong coverage for option escaping and security-sensitive behavior: `DefaultPermissions` should make the kernel enforce file modes, and `ReadOnly` should block creation before the filesystem's `Create` method returns its distinct error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/options_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/protocol.go -->
# sources/user-network-fs/bazil-fuse/protocol.go

Purpose: `protocol.go` defines a simple FUSE protocol version type and feature predicate helpers.

Important APIs, types, and functions: `Protocol{Major, Minor}` implements `String`, `LT`, and `GE`. Deprecated feature predicates `HasAttrBlockSize`, `HasReadWriteFlags`, `HasGetattrFlags`, `HasOpenNonSeekable`, `HasUmask`, and `HasInvalidate` now always return true because the package minimum protocol supports them. `HasNotifyDelete` returns true for protocol >= 7.18.

Control flow: Version comparison is lexicographic by major then minor. Feature helpers are direct boolean returns.

State and persistence behavior: Stateless value type.

Dependencies and integration points: Used in `fuse.go` init negotiation and in kernel struct size/version gating from `fuse_kernel.go`.

Risks: Deprecated helpers may give callers a false sense that runtime negotiation still varies for those features. `HasNotifyDelete` remains version-sensitive and should be checked by code using delete notifications.

Test signals: No direct test in this subset, but `fuse.go` and integration tests exercise negotiated protocol behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/protocol.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/syscallx/syscallx.go -->
# sources/user-network-fs/bazil-fuse/syscallx/syscallx.go

Purpose: `syscallx.go` preserves a deprecated compatibility package that forwards extended attribute and msync helpers to `golang.org/x/sys/unix`.

Important APIs, types, and functions: Exported wrappers are `Getxattr`, `Listxattr`, `Setxattr`, `Removexattr`, and `Msync`.

Control flow: Each function directly calls the matching `unix` function and returns its result.

State and persistence behavior: The package itself is stateless. The wrapped syscalls can read or mutate filesystem extended attributes or flush memory-mapped data depending on caller inputs.

Dependencies and integration points: Depends only on `golang.org/x/sys/unix`. Comments mark the package and each function deprecated in favor of direct `unix` usage.

Risks: Deprecation comments contain typos saying `unic` in several places. Keeping wrappers may encourage new code to use obsolete APIs, but it preserves compatibility for existing imports.

Test signals: `serve_test.go` uses `unix` directly for xattrs and `Msync`, demonstrating the preferred replacement path rather than this wrapper package.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/syscallx/syscallx.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/unmount.go -->
# sources/user-network-fs/bazil-fuse/unmount.go

Purpose: `unmount.go` exposes the public unmount API.

Important APIs, types, and functions: `Unmount(dir string) error` delegates to the platform-specific private `unmount` implementation.

Control flow: Single direct call.

State and persistence behavior: No internal state. It affects the OS mount table by unmounting a FUSE mount.

Dependencies and integration points: Called by users and by `Mount` cleanup after failed init. The implementation is selected from `unmount_linux.go` or `unmount_std.go`.

Risks: Behavior and error messages are platform-specific. Callers must close active connections or files as needed to avoid busy mounts.

Test signals: Many integration tests defer mount cleanup through `fstestutil`, which ultimately relies on this API.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/unmount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/unmount_linux.go -->
# sources/user-network-fs/bazil-fuse/unmount_linux.go

Purpose: This file implements Linux unmounting through the `fusermount3 -u` helper.

Important APIs, types, and functions: `unmount(dir string) error` runs `exec.Command("fusermount3", "-u", dir).CombinedOutput()`.

Control flow: If the helper exits with an error and produced output, the function trims trailing newlines and appends the helper output to the error string before returning it. Successful helper exit returns nil.

State and persistence behavior: No internal state. It requests removal of a live FUSE mount from the OS mount table.

Dependencies and integration points: Depends on `os/exec`, `bytes`, and `errors`. Used by public `Unmount`.

Risks: Requires `fusermount3` in PATH. The returned error is a newly formatted `errors.New`, so callers cannot inspect the original `exec.ExitError` except by parsing text. Busy mounts or permission issues are helper-dependent.

Test signals: Integration tests repeatedly exercise unmount during cleanup but do not directly assert Linux unmount error formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/unmount_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/unmount_std.go -->
# sources/user-network-fs/bazil-fuse/unmount_std.go

Purpose: This non-Linux implementation unmounts using the Go `syscall.Unmount` API.

Important APIs, types, and functions: `unmount(dir string) error` calls `syscall.Unmount(dir, 0)` and wraps failures in `*os.PathError{Op: "unmount", Path: dir, Err: err}`.

Control flow: Single syscall with error wrapping on failure.

State and persistence behavior: No internal state. It changes the OS mount table.

Dependencies and integration points: Built when `!linux`; used by public `Unmount`, including FreeBSD builds.

Risks: Does not use a platform helper, so behavior depends directly on syscall permissions and platform semantics. No forced/lazy unmount flags are used.

Test signals: FreeBSD integration cleanup paths indirectly exercise it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/unmount_std.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/actions/disk-benchmark/action.yml -->
# sources/user-network-fs/blobfuse2/.github/actions/disk-benchmark/action.yml

Purpose: This composite GitHub Action benchmarks local disk read and write throughput with FIO and publishes results to GitHub Pages through `benchmark-action/github-action-benchmark`.

Important APIs, types, and functions: Inputs are required `GITHUB_TOKEN` and `ARCH`. The first step runs shell commands to create `/mnt/localssd` and `disk`, run sequential write and read FIO jobs, transform JSON output with `jq` into benchmark JSON files, remove the temporary FIO file, and print results. The next two steps publish write and read results separately with `tool: customBiggerIsBetter`, `auto-push: true`, branch `benchmarks`, and paths under `${{ inputs.ARCH }}/disk/write` and `${{ inputs.ARCH }}/disk/read`.

Control flow: The shell step uses `set -euo pipefail`, so FIO/JQ failures stop the action. Write benchmark creates `/mnt/localssd/fiotest.tmp`; read benchmark reads the same file; cleanup removes it. Publishing steps consume `disk/write.json` and `disk/read.json`.

State and persistence behavior: Runner-local state includes `/mnt/localssd/fiotest.tmp` and `./disk/*.json`. Persistent remote state is benchmark data pushed to the `benchmarks` branch by the benchmark action.

Dependencies and integration points: Requires `sudo`, `fio`, `jq`, writable `/mnt/localssd`, GitHub token permissions, and `benchmark-action/github-action-benchmark@v1`. It is intended for BlobFuse2 CI benchmark workflows and groups results by architecture.

Risks: The action assumes `/mnt/localssd` exists or can be used after `mkdir`, but it does not mount a disk there. `sudo chmod 777` is broad. `sudo mkdir disk` creates a workspace directory as root and then chmods it, which can be surprising. The read job depends on the write job leaving a valid 4 GiB file. `auto-push: true` mutates the `benchmarks` branch from CI and can fail on token/branch protection issues.

Test signals: There is no test file here; validation is by successful CI execution and generated benchmark history. The JSON conversion reports MiB/s by dividing FIO KiB/s by 1024.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/.github/actions/disk-benchmark/action.yml -->
