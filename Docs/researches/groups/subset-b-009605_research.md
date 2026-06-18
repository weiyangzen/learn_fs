# Research Group subset-b-009605

This grouped report covers the requested go-fuse virtiofs/vhost-user support files, POSIX and splice/archive test helpers, and the go-nfs server/helper/example files. Each source file has a delimited section for reconciliation into a source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/device.go -->
# sources/user-network-fs/go-fuse/internal/vhostuser/device.go

## Purpose
Owns the vhost-user device state used by the virtiofs backend: request fd, virtqueues, memory regions, dirty-log table, feature negotiation, and the FUSE request callback.

## Important APIs, Types, and Functions
`Device`, `NewDevice`, `Close`, vring setters, `SetLogBase`, feature/protocol feature getters, and `VirtqElem` are the main API surface.

## Control Flow
Control-plane requests from `server.go` call setter methods under `dispatchMu`; enabling a vring starts queue processing through `Virtq.SetEnable`. The request callback returns the number of response bytes written to guest buffers.

## State and Persistence Behavior
The device owns open eventfds through its queues, mmaped memory regions, and an optional mmaped log table. `Close` tears down queues, regions, and log memory, but feature setters currently persist no negotiated mask.

## Dependencies and Integration Points
Integrates with `Server` dispatch, `Virtq` data-plane processing, `deviceRegions` address translation, Linux `mmap`/eventfd semantics, and `fuse.ProtocolServer` via `virtiofs.go`.

## Risks and Edge Cases
Queue count is hardcoded to two, feature setters ignore client masks, log-table support is partly implemented but not advertised consistently, and index bounds depend on well-formed driver messages.

## Test Signals
End-to-end coverage comes from `virtiofs` QEMU tests; focused tests should reject late `SET_VRING_KICK`, invalid queue indexes, repeated log-base setup, and close behavior with partially initialized queues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/device.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/deviceregion.go -->
# sources/user-network-fs/go-fuse/internal/vhostuser/deviceregion.go

## Purpose
Represents one shared-memory region supplied by QEMU for vhost-user guest memory.

## Important APIs, Types, and Functions
`deviceRegion`, `configure`, `Close`, `containsGuestAddr`, `FromDriverAddr`, and `String` wrap a `VhostUserMemoryRegion` plus the mmaped byte slice.

## Control Flow
`configure` validates driver-address overflow, maps the fd at `MmapOffset` for `MemorySize`, marks it `MADV_DONTDUMP`, and records the region. Translation methods later return byte-backed pointers or containment checks.

## State and Persistence Behavior
State is the mmaped `Data` slice and copied wire region metadata. `Close` unmaps the slice; the fd is owned by the caller and is closed in higher-level setup paths.

## Dependencies and Integration Points
Used by `deviceRegions.AddMemReg`, `Virtq.SetVringAddr`, and descriptor translation; depends on `syscall.Mmap`, `syscall.Munmap`, and `golang.org/x/sys/unix`.

## Risks and Edge Cases
Unsafe pointer conversion assumes the mmap remains live while vring and request buffers use it. Huge-page fds are rejected elsewhere; partial mappings or offset mistakes would corrupt guest address translation.

## Test Signals
QEMU virtiofs tests exercise normal mmap translation. Unit tests should cover overflow, offset mapping, out-of-range driver addresses, and unmap failure propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/deviceregion.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/regions.go -->
# sources/user-network-fs/go-fuse/internal/vhostuser/regions.go

## Purpose
Maintains the collection of vhost-user memory regions and supplies lock-free address translation for queue readers.

## Important APIs, Types, and Functions
`deviceRegions`, `load`, `AddMemReg`, `FromDriverAddr`, `FromGuestAddr`, `findRegionByGuestAddr`, `Close`, and `GetMaxMemslots` are central.

## Control Flow
Writers add regions under `mu`, keep the slice sorted by guest address, and publish a new immutable slice with `atomic.Pointer`. Readers search the current slice without taking a lock.

## State and Persistence Behavior
Region slices are append-only after publication; old mapped regions remain alive. `Close` unmaps the currently loaded regions. There is no remove-region path despite protocol constants existing.

## Dependencies and Integration Points
Used by vhost-user control handling and virtqueue descriptor mapping. It depends on `deviceRegion.configure`, `getFDHugepagesize`, sorting, atomics, and unsafe byte slice exposure.

## Risks and Edge Cases
Overlap detection is absent, partial guest-range lookup only returns the first segment, and old slices could keep regions mapped after future remove support. Huge-page rejection may limit deployments.

## Test Signals
Tests should add multiple out-of-order regions, translate across boundaries, verify max-slot enforcement, reject huge pages, and run queue reads concurrently with `AddMemReg` under race detection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/regions.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/server.go -->
# sources/user-network-fs/go-fuse/internal/vhostuser/server.go

## Purpose
Implements the vhost-user control socket protocol for configuring the backend device over a Unix domain socket.

## Important APIs, Types, and Functions
`Server`, `NewServer`, `Serve`, `Close`, `oneRequest`, feature request helpers, and the request switch over `REQ_*` define the API.

## Control Flow
`oneRequest` reads a fixed header, parses ancillary fds, optionally reads payload bytes, logs decoded messages, validates expected fd counts, dispatches to `Device` methods under `dispatchMu`, and writes replies when required.

## State and Persistence Behavior
The server owns the Unix connection and delegates persistent state to `Device`. It serializes each control request and closes no inbound fd on failed dispatch except where the device method consumes it.

## Dependencies and Integration Points
Integrates with `types.go` wire structs, `Device` setters, Unix rights parsing, and QEMU vhost-user message ordering. It is the only path from QEMU control-plane messages into queues and memory maps.

## Risks and Edge Cases
Only a subset of protocol requests is implemented; payload size uses a fixed 4 KiB buffer; all fds are made nonblocking before device code sometimes changes them; unknown operations become device errors.

## Test Signals
Virtiofs QEMU tests cover the happy path. Protocol tests should inject wrong fd counts, oversized payloads, truncated second reads, unknown requests, and `_NEED_REPLY` error responses.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/types.go -->
# sources/user-network-fs/go-fuse/internal/vhostuser/types.go

## Purpose
Defines vhost-user and virtio split-ring constants, request IDs, wire payload structs, feature-name decoding, and debug stringers.

## Important APIs, Types, and Functions
Important items include protocol feature constants, virtio feature constants, `Header`, `VhostVringAddr`, `VhostVringState`, `VhostUserMemoryRegion`, descriptor/ring structs, and `inFDCount`.

## Control Flow
There is no runtime protocol logic beyond formatting and mask composition support; `Server` casts payload bytes to these structs with `unsafe.Pointer` and uses decode maps for debug logging.

## State and Persistence Behavior
Struct values mirror wire messages and shared-memory ring layouts. They are transient except when copied into `Device`, `Ring`, or `Virtq` state.

## Dependencies and Integration Points
All vhost-user control handling depends on this file. It must stay ABI-compatible with QEMU/Linux headers and with the little-endian shared-memory expectations documented in `server.go`.

## Risks and Edge Cases
Unsafe struct casting is sensitive to padding, host endianness, and field width. Some constants are present without implementation, which can mislead future feature negotiation changes.

## Test Signals
Builds and QEMU negotiation provide coverage. ABI tests should check `unsafe.Sizeof` values, stringer output for masks, fd-count expectations, and request IDs against upstream vhost-user headers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/util.go -->
# sources/user-network-fs/go-fuse/internal/vhostuser/util.go

## Purpose
Provides small utility functions for vhost-user setup: hugepage detection, feature mask composition, and the virtqueue eventfd read loop.

## Important APIs, Types, and Functions
`getFDHugepagesize`, `composeMask`, and `Virtq.readLoop` are the relevant functions.

## Control Flow
`readLoop` blocks on the kick fd, drains a batch from the virtqueue, clears writable buffers, logs optional debug data, calls the device handler in a goroutine per element, pushes completion, and notifies the guest.

## State and Persistence Behavior
The loop persists until its `readerControl.cancel` is closed or the kick fd read fails. It mutates request buffers and queue state but does not own durable storage.

## Dependencies and Integration Points
Depends on Linux fd/statfs behavior, `Virtq.popBatch`, `pushQueue`, `queueNotify`, and the FUSE protocol server callback used by virtiofs.

## Risks and Edge Cases
Spawning one goroutine per element can amplify load; handler panics can bypass completion; kick fd read errors terminate processing; `getFDHugepagesize` is Linux-specific behavior in a generic internal package.

## Test Signals
End-to-end virtiofs tests cover loop liveness. Race tests should toggle control-plane setup while kicks arrive and assert no goroutine or fd leak after disable/close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/virtq.go -->
# sources/user-network-fs/go-fuse/internal/vhostuser/virtq.go

## Purpose
Implements virtio split-ring data-plane operations for descriptor mapping, queue popping, used-ring publishing, notification, and queue lifecycle.

## Important APIs, Types, and Functions
Core APIs are `Virtq`, `Ring`, `MapRing`, `SetEnable`, `popBatch`, `popQueue`, `queueMapDesc`, `readVringEntry`, `pushQueue`, `queueNotify`, `SetVringAddr`, `Close`, and `VringNeedEvent`.

## Control Flow
On enable, `readLoop` consumes kicks. `popQueue` checks ring initialization, reads avail entries with barriers, maps descriptor chains including indirect descriptors, and increments in-use count. Completion writes used-ring entries, advances indexes, and signals the call fd when event-index logic requires it.

## State and Persistence Behavior
Queue state includes ring pointers into guest memory, eventfds, used/avail indexes, inflight placeholders, debug pointer, and goroutine control channels. It uses `mu` for vring state and device `dispatchMu` for control/data coordination.

## Dependencies and Integration Points
Depends on `deviceRegions` for guest address resolution, `barrier` memory fences for virtio ordering, Linux eventfd writes, and `types.go` ring structs.

## Risks and Edge Cases
Descriptor chains are guest-controlled and pointer-heavy; loops, mixed indirect chains, partial region reads, nil event pointers, or notification arithmetic mistakes can hang or corrupt queues. Packed rings and inflight recovery are not implemented.

## Test Signals
QEMU virtiofs traffic is the main signal. Unit tests should cover indirect descriptor bounds, multi-region buffers, event-index notification thresholds, queue disable while active, and malformed avail heads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/vhostuser/virtq.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/constants_linux.go -->
# sources/user-network-fs/go-fuse/internal/xattr/constants_linux.go

## Purpose
Provides the Linux spelling of the missing-xattr error for go-fuse's internal xattr helpers.

## Important APIs, Types, and Functions
Exports `ENOATTR` as `unix.ENODATA`, matching Linux's `getxattr` missing-attribute errno.

## Control Flow
No control flow beyond build-tag selection. Linux builds compile this file instead of the non-Linux constant file.

## State and Persistence Behavior
Stateless constant only; no persistence.

## Dependencies and Integration Points
Used by `posixtest.XAttr` and any FUSE code comparing missing extended attributes portably; depends on `golang.org/x/sys/unix`.

## Risks and Edge Cases
Incorrect errno mapping would make xattr tests fail or hide missing attributes as generic errors.

## Test Signals
Linux xattr tests should call `Getxattr` before and after `Setxattr`/`Removexattr` and compare against `xattr.ENOATTR`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/constants_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/constants_unix.go -->
# sources/user-network-fs/go-fuse/internal/xattr/constants_unix.go

## Purpose
Provides the non-Linux spelling of the missing-xattr error for portable xattr handling.

## Important APIs, Types, and Functions
Exports `ENOATTR` as `unix.ENOATTR` on non-Linux builds.

## Control Flow
Build tags choose this file outside Linux; there is no runtime branch.

## State and Persistence Behavior
Stateless constant only.

## Dependencies and Integration Points
Used by the common xattr tests and any platform-specific FUSE code needing a portable not-found comparison.

## Risks and Edge Cases
Platform headers vary; unsupported platforms could fail to define `ENOATTR` or map it differently.

## Test Signals
FreeBSD/Darwin xattr tests should verify missing attributes compare equal to this constant.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/constants_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/xattr.go -->
# sources/user-network-fs/go-fuse/internal/xattr/xattr.go

## Purpose
Exports the package-level xattr list-name parser behind a stable public internal function.

## Important APIs, Types, and Functions
`ParseAttrNames` delegates to the platform-selected `parseAttrNames` implementation.

## Control Flow
Runtime flow is a single call through to either BSD length-prefixed parsing or Unix NUL-separated parsing.

## State and Persistence Behavior
Stateless; returns slices referencing the caller-provided buffer.

## Dependencies and Integration Points
Used by `posixtest.XAttr` after `unix.Listxattr`; integrates with platform files selected by build tags.

## Risks and Edge Cases
Callers must not mutate or discard the buffer before consuming returned names. Empty trailing names may appear on NUL-separated platforms.

## Test Signals
Xattr list tests should set an attribute, list names, parse the result, and find the expected name on Linux and BSD conventions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/xattr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/xattr_freebsd.go -->
# sources/user-network-fs/go-fuse/internal/xattr/xattr_freebsd.go

## Purpose
Implements FreeBSD/BSD extended-attribute name parsing, where each name is prefixed by a one-byte length.

## Important APIs, Types, and Functions
`parseAttrNames` walks the byte buffer and appends `buf[p:p+len]` entries.

## Control Flow
The loop reads a length byte, slices the following name bytes, appends the name, and advances until the buffer is exhausted.

## State and Persistence Behavior
Stateless; output names alias the input buffer.

## Dependencies and Integration Points
Selected on FreeBSD and used through `ParseAttrNames` by xattr tests and FUSE compatibility code.

## Risks and Edge Cases
Malformed buffers with a length exceeding remaining bytes will panic. The parser trusts kernel output, so it is unsuitable for untrusted arbitrary input without validation.

## Test Signals
FreeBSD tests should list multiple xattrs, including short and long names, and verify no Linux-style NUL splitting is assumed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/xattr_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/xattr_unix.go -->
# sources/user-network-fs/go-fuse/internal/xattr/xattr_unix.go

## Purpose
Implements non-FreeBSD extended-attribute list parsing, where names are NUL-separated.

## Important APIs, Types, and Functions
`parseAttrNames` uses `bytes.Split(buf, []byte{0})`.

## Control Flow
There is no filtering; the split result is returned directly.

## State and Persistence Behavior
Stateless; returned slices alias the input buffer and may include a final empty name when the kernel buffer ends with NUL.

## Dependencies and Integration Points
Used by Linux, Darwin, and other Unix builds through `ParseAttrNames`.

## Risks and Edge Cases
A trailing empty attribute name can appear; callers must tolerate it. Embedded NULs are impossible in real xattr names but would be split if given synthetic data.

## Test Signals
Tests should include kernel `Listxattr` output and synthetic buffers with trailing NULs to document the empty-tail behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/xattr/xattr_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/newunionfs/unionfs.go -->
# sources/user-network-fs/go-fuse/newunionfs/unionfs.go

## Purpose
Implements a writable-over-readonly union filesystem using go-fuse's inode API and deletion marker files in the writable branch.

## Important APIs, Types, and Functions
Important pieces are `unionFSRoot`, `unionFSNode`, marker helpers, `Lookup`, `Readdir`, `Create`, `Open`, `Setattr`, deletion operations, `promote`, and `promoteRegularFile`.

## Control Flow
Reads search branches unless a deletion marker hides the path. Writes and metadata changes promote lower-branch files/directories into the writable branch, then operate there. Deletes unlink writable files or create marker files for lower entries.

## State and Persistence Behavior
Persistent state lives in the writable root: promoted copies and `DELETIONS/<hash>-<base>` marker files. Inode state is go-fuse runtime state derived from branch lookups.

## Dependencies and Integration Points
Depends on `github.com/hanwen/go-fuse/v2/fs`, `fuse`, loopback files, raw syscalls, path hashing, and POSIX metadata operations.

## Risks and Edge Cases
Promotion handles regular files and directories but panics on other modes; marker hashes can collide in theory; path/time handling has rough edges; setattr has a dead `fh` type assertion branch after a nil check.

## Test Signals
`unionfs_test.go` covers create, delete, marker removal, readdir merging, promotion, and selected `posixtest` cases. More tests should cover symlink promotion, xattrs, hard links, and marker collisions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/newunionfs/unionfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/newunionfs/unionfs_test.go -->
# sources/user-network-fs/go-fuse/newunionfs/unionfs_test.go

## Purpose
Tests the new union filesystem's branch lookup, deletion markers, promotion, readdir behavior, and selected POSIX compatibility cases.

## Important APIs, Types, and Functions
`newTestCase`, `testCase.Clean`, `TestBasic`, `TestDelete`, `TestDeleteMarker`, `TestCreate`, `TestPromote`, `TestReaddir*`, and `TestPosix` are the main test APIs.

## Control Flow
Each test creates temp `ro`, `rw`, and mount directories, mounts `unionFSRoot`, mutates the mounted view, and verifies effects in the backing trees or mounted paths.

## State and Persistence Behavior
Test state is isolated in temp dirs and a mounted FUSE server; `Clean` unmounts. `init` sets umask to zero for predictable modes.

## Dependencies and Integration Points
Depends on go-fuse mount support, `internal/testutil`, and the shared `posixtest` suite.

## Risks and Edge Cases
Tests require FUSE availability and can be flaky if unmount fails. Only a subset of POSIX tests is enabled, leaving rename, hard link, and directory mutation gaps.

## Test Signals
The file itself is the primary signal for unionfs regressions and should be run with verbose FUSE logging when debugging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/newunionfs/unionfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/listfds.go -->
# sources/user-network-fs/go-fuse/posixtest/listfds.go

## Purpose
Lists open file descriptors for POSIX fd-leak tests, filtering known uninteresting descriptors.

## Important APIs, Types, and Functions
`listFds(pid, prefix)` returns strings of `fd[mode]=target` plus a filtered summary.

## Control Flow
It opens `/dev/fd` for the current process or `/proc/<pid>/fd` for another Linux process, reads entries, lstat/readlinks each fd, filters pipes, epoll, and non-prefix targets, and returns the rest.

## State and Persistence Behavior
No persistent state; it observes live process fd state and handles races where descriptors close mid-scan.

## Dependencies and Integration Points
Used by `posixtest.FdLeak`; depends on `/dev/fd`, Linux `/proc`, and Go runtime fd behavior.

## Risks and Edge Cases
Mode bits from fd symlinks are approximate, `/proc` is Linux-only for other pids, and filtering could hide relevant pipe leaks from splice-heavy code.

## Test Signals
`FdLeak` reads a file repeatedly and asserts the descriptor count remains low; race runs can catch descriptors closed during enumeration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/listfds.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/platform_freebsd.go -->
# sources/user-network-fs/go-fuse/posixtest/platform_freebsd.go

## Purpose
Normalizes FreeBSD stat structures for cross-platform POSIX tests by clearing revision-specific spare fields.

## Important APIs, Types, and Functions
`clearStatRevision` copies an empty `syscall.Stat_t.Spare` over `unix.Stat_t.Spare`.

## Control Flow
Called before comparing `Stat_t` values in tests that otherwise expect stable metadata.

## State and Persistence Behavior
Stateless test helper.

## Dependencies and Integration Points
Used by `FstatDeleted` on FreeBSD; depends on `golang.org/x/sys/unix` and `syscall.Stat_t` layout.

## Risks and Edge Cases
If FreeBSD stat layout changes, the field adjustment could fail to compile or miss noisy fields.

## Test Signals
FreeBSD CI or `test-freebsd.bash` validates that deleted-file stat comparisons are not revision-noisy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/platform_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/platform_unix.go -->
# sources/user-network-fs/go-fuse/posixtest/platform_unix.go

## Purpose
Provides the no-op implementation of stat normalization for non-FreeBSD POSIX tests.

## Important APIs, Types, and Functions
`clearStatRevision` accepts `*unix.Stat_t` and does nothing.

## Control Flow
Build tags select this file outside FreeBSD.

## State and Persistence Behavior
Stateless helper.

## Dependencies and Integration Points
Used by shared tests to compile uniformly across Unix-like systems.

## Risks and Edge Cases
If another platform gains volatile stat fields, comparisons may become flaky until this helper is specialized.

## Test Signals
Linux and Darwin POSIX runs indirectly exercise this no-op path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/platform_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/posixtest_test.go -->
# sources/user-network-fs/go-fuse/posixtest/posixtest_test.go

## Purpose
Runs all registered POSIX conformance tests against either a temp directory or a user-supplied `-posixdir`.

## Important APIs, Types, and Functions
Defines `probeDir` and `TestAll`.

## Control Flow
`TestAll` iterates `All`, skips two known-problem tests, creates a subdirectory per case, and invokes the registered test function.

## State and Persistence Behavior
Test state is per-subtest directory under a temp or supplied root; no persistent repo state is changed.

## Dependencies and Integration Points
Depends on the shared `All` registry in `test.go` and Go's testing flags.

## Risks and Edge Cases
Map iteration order is random, so failures are not ordered. A shared `-posixdir` can retain data between runs if subdirectories are not cleaned externally.

## Test Signals
Running `go test ./posixtest` or embedding the binary in virtiofs QEMU tests exercises the registry.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/posixtest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/test.go -->
# sources/user-network-fs/go-fuse/posixtest/test.go

## Purpose
Defines the reusable POSIX filesystem conformance suite used by go-fuse filesystems and virtiofs tests.

## Important APIs, Types, and Functions
`All` maps names to tests covering symlinks, basic files, truncation, fd leaks, mkdir/rmdir, link/rename, deleted fstat, directory reads, append, openat, fallocate, locks, lseek holes, xattrs, and symlink races.

## Control Flow
Each test mutates a supplied mount/path with standard library and syscall operations, then checks observed POSIX semantics through stat, readback, errno, directory entries, locks, or xattr state.

## State and Persistence Behavior
State is limited to files under the supplied test root plus transient open fds and goroutines in race/parallel tests.

## Dependencies and Integration Points
Integrates with go-fuse filesystem tests, unionfs tests, virtiofs guest tests, `internal/xattr`, `internal/fallocate`, and platform flock helpers.

## Risks and Edge Cases
Several tests depend on kernel/filesystem support and may skip or fail on unsupported O_DIRECT, xattr, SEEK_HOLE, or lock behavior. `OpenSymlinkRace` is intentionally stressy.

## Test Signals
This file is the main behavior signal for filesystem correctness; running with `-race` and under real FUSE/virtiofs backends catches fd, locking, and path-resolution regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/test_darwin.go -->
# sources/user-network-fs/go-fuse/posixtest/test_darwin.go

## Purpose
Provides Darwin's `F_OFD_GETLK` command number for the POSIX flock test helper.

## Important APIs, Types, and Functions
`sysFcntlFlockGetOFDLock` calls `syscall.FcntlFlock` with constant `92`.

## Control Flow
The shared lock test passes an fd and lock struct; this wrapper performs the platform-specific query.

## State and Persistence Behavior
Stateless helper.

## Dependencies and Integration Points
Used by `FcntlFlockSetLk` on macOS builds.

## Risks and Edge Cases
The hardcoded command value assumes macOS Sierra-or-newer behavior and may not apply to all Darwin-like environments.

## Test Signals
Darwin POSIX test runs validate OFD lock reporting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/test_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/test_freebsd.go -->
# sources/user-network-fs/go-fuse/posixtest/test_freebsd.go

## Purpose
Provides FreeBSD lock-query behavior for POSIX flock tests despite missing `F_OFD_GETLK`.

## Important APIs, Types, and Functions
`sysFcntlFlockGetOFDLock` creates a pipe, forks, queries `F_GETLK` in the child, writes the lock struct to the parent, and exits.

## Control Flow
The child uses a read-lock request to discover the write lock held by the parent process, approximating Linux OFD lock visibility.

## State and Persistence Behavior
Transient state includes forked child and pipe fds; the helper does not wait for the child explicitly.

## Dependencies and Integration Points
Used by `FcntlFlockSetLk` on FreeBSD; depends on raw `fork`, pipes, unsafe struct transfer, and `syscall.FcntlFlock`.

## Risks and Edge Cases
Missing wait can leave short-lived zombies; partial pipe reads are not checked; errors in the child are ignored.

## Test Signals
FreeBSD POSIX testing should run locking cases and watch for process leaks or hangs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/test_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/test_linux.go -->
# sources/user-network-fs/go-fuse/posixtest/test_linux.go

## Purpose
Provides Linux-specific POSIX helpers and registers a Linux-only fallocate keep-size test.

## Important APIs, Types, and Functions
`sysFcntlFlockGetOFDLock` uses `unix.F_OFD_GETLK`; `FallocateKeepSize` validates `FALLOC_FL_KEEP_SIZE`; `init` adds it to `All`.

## Control Flow
The fallocate test writes data, allocates a range past the middle with keep-size, seeks back, reads all data, and verifies content is unchanged.

## State and Persistence Behavior
State is a single file under the supplied test root.

## Dependencies and Integration Points
Depends on Linux `unix` constants and `syscall.Fallocate`.

## Risks and Edge Cases
Filesystems without keep-size support may fail rather than skip; OFD lock behavior is Linux-specific.

## Test Signals
Linux `go test ./posixtest` exercises this through the `All` registry.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/test_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/xfstests.go -->
# sources/user-network-fs/go-fuse/posixtest/xfstests.go

## Purpose
Ports an xfstests directory offset seek case into the POSIX suite.

## Important APIs, Types, and Functions
`DirSeek` creates many entries, captures raw dirents, seeks to each previous offset, and verifies the next dirent matches.

## Control Flow
It uses `readAllDirEntries`, `unix.Seek`, and `unix.ReadDirent` to validate stable `d_off` handling in directory streams.

## State and Persistence Behavior
State is the `ttt` directory and 168 files under the supplied root.

## Dependencies and Integration Points
Depends on raw getdents parsing through go-fuse `fuse.DirEntry`.

## Risks and Edge Cases
Directory offset behavior is subtle across kernels and FUSE implementations; incorrect offsets can cause repeated, skipped, or zero entries after seek.

## Test Signals
Included in the `All` registry and particularly useful for regressions around readdir cookies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/posixtest/xfstests.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/copy.go -->
# sources/user-network-fs/go-fuse/splice/copy.go

## Purpose
Provides Linux zero-copy file copying helpers built on splice pipe pairs with an `io.Copy` fallback.

## Important APIs, Types, and Functions
`SpliceCopy`, `CopyFile`, and `CopyFds` are the public functions.

## Control Flow
`SpliceCopy` repeatedly splices from source fd into a pipe, then from pipe to destination fd, stopping on EOF or short final chunk. `CopyFds` borrows a pooled pair, grows it, and falls back to `io.Copy` if unavailable.

## State and Persistence Behavior
State is borrowed from the global splice pair pool and returned after use; destination files are created/truncated by `CopyFile`.

## Dependencies and Integration Points
Depends on `Pair.LoadFrom`, `Pair.WriteTo`, `splicePool`, Linux `splice(2)`, and standard file APIs.

## Risks and Edge Cases
A short write path returns `err` even when nil, so partial splice without an error may look successful. Linux-only build tag excludes other platforms.

## Test Signals
`copy_test.go` verifies small file copy and large splice copy with max pipe growth.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/copy_test.go -->
# sources/user-network-fs/go-fuse/splice/copy_test.go

## Purpose
Tests Linux splice copy helpers.

## Important APIs, Types, and Functions
`TestCopyFile` and `TestSpliceCopy` cover file-level and pair-level copying.

## Control Flow
Tests create temp files, write known data, call the copy helpers, and inspect destination contents or pipe sizing.

## State and Persistence Behavior
State is temp files and a temporary splice pair that is closed manually in the large-copy test.

## Dependencies and Integration Points
Depends on the Linux splice package and `/proc/sys/fs/pipe-max-size` indirectly.

## Risks and Edge Cases
The large-copy test does not validate destination bytes after `SpliceCopy`, so it mainly catches setup and syscall failures.

## Test Signals
Run with `go test ./splice` on Linux; additional assertions should compare the 2 MiB destination content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/copy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/pair.go -->
# sources/user-network-fs/go-fuse/splice/pair.go

## Purpose
Defines the Linux splice pipe-pair abstraction used as an in-memory kernel pipe buffer.

## Important APIs, Types, and Functions
`Pair`, `Grow`, `MaxGrow`, `Cap`, `Close`, `Read`, `Write`, `ReadFd`, and `WriteFd` are the API.

## Control Flow
`Grow` uses `F_SETPIPE_SZ` when supported and within `maxPipeSize`; other methods wrap raw fd reads/writes and closing.

## State and Persistence Behavior
A pair owns read and write pipe fds plus its current capacity. Pool code controls reuse and final close.

## Dependencies and Integration Points
Used by copy and low-level splice functions; depends on `fcntl` constants initialized in `splice.go`.

## Risks and Edge Cases
Capacity growth can fail due to kernel limits; callers must return or close pairs exactly once to avoid leaks/double close.

## Test Signals
`TestPairSize` and `TestDiscard` exercise capacity and pipe draining; copy tests exercise read/write fd use.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/pair.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/pair_linux.go -->
# sources/user-network-fs/go-fuse/splice/pair_linux.go

## Purpose
Implements Linux-specific splice syscalls and pipe draining for `Pair`.

## Important APIs, Types, and Functions
`LoadFromAt`, `LoadFrom`, `WriteTo`, and `discard` are the important methods.

## Control Flow
Load methods splice from a file fd to the pair's write end; `WriteTo` splices from the read end to a destination fd; `discard` nonblocking-splices remaining bytes to `/dev/null` until `FIONREAD` reports empty.

## State and Persistence Behavior
No durable state beyond pipe contents; `discard` is called before returning a pair to the pool.

## Dependencies and Integration Points
Depends on Linux `syscall.Splice`, `/dev/null`, `unix.IoctlGetInt`, and pair capacity.

## Risks and Edge Cases
If an fd was accidentally closed, `discard` panics after trying to close both ends. `LoadFromAt` uses a local offset and does not advance the source fd.

## Test Signals
Splice tests cover over-capacity load and discard emptiness. Fault tests should simulate closed fds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/pair_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/pool.go -->
# sources/user-network-fs/go-fuse/splice/pool.go

## Purpose
Provides the global pool for reusable Linux splice pipe pairs.

## Important APIs, Types, and Functions
Public helpers are `ClearSplicePool`, `Get`, `Done`, `Drop`, `Total`, and `Used`; internal methods manage `unused` and `usedCount`.

## Control Flow
`get` increments used count and returns an unused pair or creates a new one. `done` drains the pipe and stores it for reuse. `drop` closes it and decrements usage.

## State and Persistence Behavior
Pool state is process-global and protected by a mutex; unused pairs retain open fds until cleared or process exit.

## Dependencies and Integration Points
Used by `CopyFds` and other go-fuse splice users.

## Risks and Edge Cases
Misbalanced `Get`/`Done`/`Drop` calls leak counts or fds. `done` drains before locking, so callers must not use the pair concurrently.

## Test Signals
Pool tests and fd-leak tests are useful signals; race tests should stress concurrent get/done/drop.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/splice.go -->
# sources/user-network-fs/go-fuse/splice/splice.go

## Purpose
Initializes Linux splice support, discovers pipe capacity behavior, opens `/dev/null` lazily, and wraps fcntl/pipe creation.

## Important APIs, Types, and Functions
`Resizable`, `MaxPipeSize`, `DefaultPipeSize`, `devNullFD`, `fcntl`, `osPipe`, and `newSplicePair` are the key APIs.

## Control Flow
Package init reads `/proc/sys/fs/pipe-max-size`, creates a probe pipe, checks get/set pipe size support, and records whether resizing works.

## State and Persistence Behavior
Global state includes `maxPipeSize`, `resizable`, and a lazily opened `/dev/null` fd that stays open for the process lifetime.

## Dependencies and Integration Points
Used by `Pair.Grow`, `Pair.discard`, and the pair pool. It depends on Linux `/proc`, `pipe2`, and fcntl constants.

## Risks and Edge Cases
The error check in `newSplicePair` compares `err` instead of `errNo` for `EINVAL`, so fallback may not trigger as intended. `/dev/null` fd is intentionally never closed.

## Test Signals
`TestSpliceCopy` checks pipe size sanity; unit tests should mock or assert fallback paths on kernels without resize support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/splice.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/splice_test.go -->
# sources/user-network-fs/go-fuse/splice/splice_test.go

## Purpose
Tests Linux splice pair capacity validation and discard behavior.

## Important APIs, Types, and Functions
`TestPairSize` and `TestDiscard` are the test cases.

## Control Flow
The first grows a pair to max, writes a file bigger than capacity, and expects `LoadFrom` to reject it. The second writes data into the pipe, discards it, and expects a nonblocking read to return `EAGAIN`.

## State and Persistence Behavior
Uses global pool state and temp files; returns pairs with `Done`.

## Dependencies and Integration Points
Depends on Linux nonblocking pipe semantics and splice discard implementation.

## Risks and Edge Cases
Expected read result checks `n == -1`, which follows raw syscall conventions but may be surprising. Tests can be sensitive to pool contamination from other tests.

## Test Signals
Run with `go test ./splice`; race/fd-leak tests should include repeated pool usage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/splice/splice_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/test-freebsd.bash -->
# sources/user-network-fs/go-fuse/test-freebsd.bash

## Purpose
Automates FreeBSD test execution for go-fuse inside a QEMU VM backed by a downloaded FreeBSD raw image.

## Important APIs, Types, and Functions
The bash script downloads/caches an image, copies it, attaches it via loop, mounts UFS with `fuse-ufs-bin`, cross-compiles Go test binaries, injects boot scripts, runs QEMU, and extracts logs.

## Control Flow
Control flow is linear: prepare cache/temp image, mount partition, copy tests and `rc.local`, unmount, boot QEMU, then remount and copy logs out.

## State and Persistence Behavior
Persistent state is cached under `$HOME/.cache/go-fuse-freebsd`; temp state is created under that cache and loop devices must be cleaned by the operator if interrupted.

## Dependencies and Integration Points
Integrates with `posixtest`, `fs` tests, QEMU, KVM, UFS FUSE tooling, Go cross-compilation, and FreeBSD boot scripts.

## Risks and Edge Cases
Requires sudo, KVM, loop devices, a local UFS FUSE binary, network download, and careful cleanup. It appends loader config to the copied image only.

## Test Signals
Success signals are extracted `posixtest.log` and `fs.log`; failures often require inspecting QEMU serial output and mounted image contents.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/test-freebsd.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/fs_test.go -->
# sources/user-network-fs/go-fuse/virtiofs/fs_test.go

## Purpose
Runs a basic end-to-end virtiofs QEMU test against a host loopback filesystem served by go-fuse.

## Important APIs, Types, and Functions
`killNotifyRoot`, its `Lookup`, and `TestBasic` are the main pieces.

## Control Flow
The test creates host files, starts `ServeFS` on a vhost-user socket, builds an initrd with a script, boots QEMU with `vhost-user-fs-pci`, mounts virtiofs in the guest, copies and lists files, then signals completion by looking up `killme.txt`.

## State and Persistence Behavior
State includes temp host directory, socket, initrd, QEMU process, and condition-variable flags for guest progress.

## Dependencies and Integration Points
Depends on `fs.LoopbackNode`, `mkinitRam`, prepared kernel/busybox/modules, QEMU/KVM, and the internal vhost-user backend.

## Risks and Edge Cases
Environment requirements are heavy; QEMU is killed externally because guest poweroff was unreliable. Test can hang if sentinel lookup never happens.

## Test Signals
The test verifies copied file contents and directory listing written back through virtiofs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/fs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/posixtest_test.go -->
# sources/user-network-fs/go-fuse/virtiofs/posixtest_test.go

## Purpose
Builds and runs the shared `posixtest` suite inside a QEMU guest mounted over virtiofs.

## Important APIs, Types, and Functions
`buildStaticPosixtest` and `TestPosixtest` are central.

## Control Flow
It compiles a static test binary, embeds it in the initrd, starts `ServeFS`, boots QEMU, mounts virtiofs, runs `posixtest.test` with DirectIO skipped, writes output and exit code into the host-backed mount, and parses failures.

## State and Persistence Behavior
State is temp initrd/socket, host loopback directory, QEMU process, and guest-generated output files.

## Dependencies and Integration Points
Integrates the POSIX suite with the full virtiofs/vhost-user/FUSE stack.

## Risks and Edge Cases
Same heavy environment risks as `fs_test.go`; parsing test output by regex may miss unusual failure formats; DirectIO is skipped.

## Test Signals
Signals include nonzero guest exit code, per-subtest failure lines, presence of `test_exit.txt`, and the `killme.txt` completion lookup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/posixtest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/ramdisk_test.go -->
# sources/user-network-fs/go-fuse/virtiofs/ramdisk_test.go

## Purpose
Builds gzipped cpio initrds for virtiofs QEMU tests, including busybox links, decompressed kernel modules, init scripts, and extra files.

## Important APIs, Types, and Functions
Key helpers are `decompressModule`, `stripCompression`, and `mkinitRam`.

## Control Flow
`mkinitRam` creates a temp root, copies busybox, creates standard directories, embeds modules and extra files, creates many busybox symlinks, writes or links init, then runs `cpio --null -ov --format=newc` through gzip to the output path.

## State and Persistence Behavior
State is temporary filesystem content and the final initrd file; it does not remove the temp build dir explicitly.

## Dependencies and Integration Points
Depends on external `xz`, `zstd`, `cpio`, gzip, busybox, and module paths discovered by setup code.

## Risks and Edge Cases
Missing tools or compressed modules fail at runtime. Not cleaning the temp directory can leave artifacts. The hardcoded busybox command list may include commands not supported by the chosen binary.

## Test Signals
Virtiofs tests validate initrd bootability; focused tests could inspect cpio contents and module decompression paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/ramdisk_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/setup_test.go -->
# sources/user-network-fs/go-fuse/virtiofs/setup_test.go

## Purpose
Prepares host assets required by virtiofs QEMU tests and skips the package cleanly when unavailable.

## Important APIs, Types, and Functions
`TestMain`, `prepareAssets`, `ensureBusybox`, `findHostKernel`, `findVirtioFSModules`, and `moduleInsmodLines` are central.

## Control Flow
Setup finds the architecture-specific QEMU binary, creates a cache dir, downloads a static busybox if missing, locates the running kernel image, and asks `modprobe --show-depends virtiofs` for modules or builtin status.

## State and Persistence Behavior
Persistent cache lives in `$HOME/.cache/go-fuse-virtiofs`; discovered paths are stored in package-level `testAssets`.

## Dependencies and Integration Points
Depends on host QEMU, network access for busybox, `/boot` kernel naming, `modprobe`, and module compression handling in `ramdisk_test.go`.

## Risks and Edge Cases
It exits 0 to skip all tests on setup failure, which can hide missing coverage in CI. The busybox URL is x86-64-specific despite partial arm64 QEMU mapping.

## Test Signals
Test package startup is the signal; CI should log skip reasons and provide cached assets where deterministic coverage is required.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/virtiofs.go -->
# sources/user-network-fs/go-fuse/virtiofs/virtiofs.go

## Purpose
Connects a go-fuse raw filesystem to a vhost-user virtio-fs socket.

## Important APIs, Types, and Functions
`ServeFS(sockpath, rawFS, opts)` is the exported entry point.

## Control Flow
It listens on a Unix socket, disables splice in mount options, creates a `fuse.ProtocolServer`, accepts connections, constructs a `vhostuser.Device` whose handler calls `HandleRequest`, then serves vhost-user control messages until disconnect.

## State and Persistence Behavior
State is per-accepted connection device/server state plus the shared protocol server. The listener remains active until accept fails.

## Dependencies and Integration Points
Depends on `net.UnixConn`, `fuse.ProtocolServer`, and `internal/vhostuser`. Used by QEMU tests.

## Risks and Edge Cases
The function logs fatally on listen errors and has no shutdown context. It serially handles accepted connections and enables verbose vhost-user debug logging.

## Test Signals
End-to-end QEMU tests are the main validation; tests should also cover socket bind failure and reconnect behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/virtiofs/virtiofs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/multizip.go -->
# sources/user-network-fs/go-fuse/zipfs/multizip.go

## Purpose
Implements a dynamic archive-mounting filesystem where symlinks under `/config` mount archive trees at root-level names.

## Important APIs, Types, and Functions
`MultiZipFs.OnAdd`, `configRoot.Unlink`, and `configRoot.Symlink` define behavior.

## Control Flow
On add, the root creates `/config`. Creating a symlink in `/config/<name>` opens the target archive with `NewArchiveFileSystem`, adds it as `/<name>`, and stores a memory symlink under config. Unlink removes both views.

## State and Persistence Behavior
Persistent state is in the in-memory inode tree, not on disk. Mounted archive contents are immutable child inode trees.

## Dependencies and Integration Points
Depends on go-fuse persistent inodes, `NewArchiveFileSystem`, and `fs.MemSymlink`.

## Risks and Edge Cases
`Unlink` calls `RmChild` twice and may race with cache invalidation. Archive paths are trusted and opened from the host. Root remains read-only except dynamic mounts.

## Test Signals
`multizip_test.go` covers readonly behavior, dynamic mount, readlink, archive access, and removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/multizip.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/multizip_test.go -->
# sources/user-network-fs/go-fuse/zipfs/multizip_test.go

## Purpose
Tests dynamic multi-archive mounting through the `MultiZipFs` config symlink interface.

## Important APIs, Types, and Functions
`setupMzfs`, `TestMultiZipReadonly`, and `TestMultiZipFs` are the main tests.

## Control Flow
Tests mount `MultiZipFs`, verify root/config write restrictions, symlink a test zip into `/config/zipmount`, inspect `/zipmount`, read the config symlink target, and unlink it to ensure the mounted tree disappears or is unreachable.

## State and Persistence Behavior
State is a temp FUSE mount and the test zip file; cleanup unmounts the server.

## Dependencies and Integration Points
Depends on FUSE support, `testZipFile`, and kernel notify support for strict invalidation checks.

## Risks and Edge Cases
If invalid inode notifications are unsupported, the removal assertion falls back to directory listing, so stale path behavior is less strictly tested.

## Test Signals
Running `go test ./zipfs` covers these flows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/multizip_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/tarfs.go -->
# sources/user-network-fs/go-fuse/zipfs/tarfs.go

## Purpose
Builds a read-only go-fuse inode tree from tar, tar.gz, or tar.bz2 archives.

## Important APIs, Types, and Functions
`HeaderToFileInfo`, `tarRoot.OnAdd`, `readCloser`, and `NewTarCompressedTree` are key APIs.

## Control Flow
On add, it streams tar entries, handles GNU long-name records, reads each file body, creates missing directory inodes, maps tar metadata into `fuse.Attr`, and installs memory files, symlinks, directories, device-like nodes, or FIFOs.

## State and Persistence Behavior
All archive content is loaded into memory inode/file objects during `OnAdd`; compressed input file handles are closed after reading.

## Dependencies and Integration Points
Depends on `archive/tar`, gzip, bzip2, go-fuse memory inode types, and archive dispatch in `zipfs.go`.

## Risks and Edge Cases
Large archives can consume large memory; hard links are logged but unsupported; directory entries are represented with `MemRegularFile` plus directory mode, which is unusual but works for attrs.

## Test Signals
`tarfs_test.go` covers directories, regular files, attributes, and readback; symlink test data is present conditionally.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/tarfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/tarfs_test.go -->
# sources/user-network-fs/go-fuse/zipfs/tarfs_test.go

## Purpose
Tests tar archive filesystem construction and mounted attribute/read behavior.

## Important APIs, Types, and Functions
`TestTar` builds an in-memory tar and mounts `tarRoot`.

## Control Flow
The test writes headers for directory and regular file entries, mounts the resulting tree, lstat checks file types/modes, and reads file contents.

## State and Persistence Behavior
State is an in-memory tar buffer and temp FUSE mount.

## Dependencies and Integration Points
Depends on `archive/tar`, `fs.Mount`, and `HeaderToFileInfo` behavior.

## Risks and Edge Cases
The current fixture map does not include a symlink entry despite code paths checking for one, leaving symlink handling less covered.

## Test Signals
`go test ./zipfs -run TestTar` validates tar tree construction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/tarfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/zipfs.go -->
# sources/user-network-fs/go-fuse/zipfs/zipfs.go

## Purpose
Implements read-only archive filesystem dispatch and zip archive inode/file support.

## Important APIs, Types, and Functions
`zipRoot`, `NewZipTree`, `zipFile.Getattr`, `zipFile.Open`, `zipFile.Read`, and `NewArchiveFileSystem` are central.

## Control Flow
`zipRoot.OnAdd` walks zip entries, creates directory inodes, and attaches `zipFile` leaves. A `zipFile` lazily decompresses content on first open and serves reads from cached memory. Dispatch chooses zip, tar, tar.gz, or tar.bz2 by suffix.

## State and Persistence Behavior
Zip file content is cached per `zipFile` in memory after first open; the zip reader remains open for the tree lifetime.

## Dependencies and Integration Points
Depends on `archive/zip`, go-fuse node APIs, tar support in `tarfs.go`, and standard path handling.

## Risks and Edge Cases
`Read` indexes `zf.data[off:end]` with `off` as int64, so very large offsets can panic or fail to compile depending on conversion rules; negative offsets are not guarded. Zip reader close is not exposed.

## Test Signals
`zipfs_test.go` checks directory listing, file attrs, mtime, blocks, readback, and link count.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/zipfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/zipfs_test.go -->
# sources/user-network-fs/go-fuse/zipfs/zipfs_test.go

## Purpose
Tests zip archive filesystem mounting, attributes, content reads, and link count reporting.

## Important APIs, Types, and Functions
`testZipFile`, `setupZipfs`, `TestZipFs`, and `TestLinkCount` are the test helpers/cases.

## Control Flow
The setup locates `test.zip`, builds an archive filesystem, mounts it, and tests root entries, directory type, file mode, block count, mtime, content, and Nlink.

## State and Persistence Behavior
State is a temp FUSE mount over a static test archive.

## Dependencies and Integration Points
Depends on runtime caller path discovery, FUSE support, and `zipfs.go`.

## Risks and Edge Cases
The setup ignores mount errors before returning cleanup, which could panic if mount failed. Tests assume exact metadata in the fixture archive.

## Test Signals
`go test ./zipfs` is the main signal for zipfs behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/zipfs/zipfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/.github/dependabot.yml -->
# sources/user-network-fs/go-nfs/.github/dependabot.yml

## Purpose
Configures Dependabot for the go-nfs repository.

## Important APIs, Types, and Functions
The YAML declares version 2 updates for the `gomod` ecosystem at `/` on a daily schedule.

## Control Flow
GitHub Dependabot reads this file and opens dependency update PRs for Go module manifests.

## State and Persistence Behavior
State is GitHub-side scheduling and generated PRs; no runtime project state.

## Dependencies and Integration Points
Integrates with GitHub dependency management and the root `go.mod`.

## Risks and Edge Cases
Daily cadence can create noisy PRs; only Go modules are covered, not GitHub Actions versions.

## Test Signals
Signals are Dependabot PRs and GitHub dependency graph alerts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/.github/workflows/codeql-analysis.yml -->
# sources/user-network-fs/go-nfs/.github/workflows/codeql-analysis.yml

## Purpose
Defines the go-nfs CodeQL code-scanning workflow.

## Important APIs, Types, and Functions
The workflow triggers on push, pull request, and a weekly Wednesday schedule; job checks out code, initializes CodeQL, autobuilds, and analyzes.

## Control Flow
For PRs it fetches depth 2 and checks out `HEAD^2` before CodeQL setup. CodeQL action v1 performs initialization and analysis.

## State and Persistence Behavior
State lives in GitHub Actions runs and uploaded code-scanning results.

## Dependencies and Integration Points
Integrates with GitHub CodeQL actions and repository build tooling.

## Risks and Edge Cases
Uses old action versions (`checkout@v2`, CodeQL v1) and a brittle PR checkout command. Autobuild may not fully represent Go module tests.

## Test Signals
Signals are CodeQL alerts and workflow pass/fail status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/.github/workflows/codeql-analysis.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/.github/workflows/go.yml -->
# sources/user-network-fs/go-nfs/.github/workflows/go.yml

## Purpose
Defines the go-nfs Go CI workflow.

## Important APIs, Types, and Functions
The workflow triggers on pushes and PRs to `master`, sets read-only contents permission, installs Go 1.x, checks out, gets deps, builds, runs golangci-lint, and tests the root package.

## Control Flow
Control flow is linear GitHub Actions steps in one Ubuntu job.

## State and Persistence Behavior
State is ephemeral CI workspace and module cache.

## Dependencies and Integration Points
Integrates with `actions/setup-go`, `actions/checkout`, `golangci-lint-action`, and `go test -v .`.

## Risks and Edge Cases
`go get -t -d` is dated, action versions are old, and only `go test .` runs rather than `./...`, so helpers/examples may not be covered.

## Test Signals
Signals are CI build/lint/test results on PRs and master pushes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/.github/workflows/go.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/conn.go -->
# sources/user-network-fs/go-nfs/conn.go

## Purpose
Implements ONC RPC-over-TCP request parsing, response framing, handler dispatch, serialized writes, and generic RPC/NFS error handling.

## Important APIs, Types, and Functions
Important types are `conn`, `request`, `response`, `ResponseCode`, `readRequestHeader`, `handle`, `err`, `Write`, `writeHeader`, `drain`, and `finish`.

## Control Flow
A connection reads record-marked RPC frames, decodes the XID/type/header into a limited body reader, dispatches by program/procedure, drains unread request bytes, formats application errors if needed, and enqueues the response buffer to a writer goroutine that prepends the last-fragment marker.

## State and Persistence Behavior
State includes the network connection, per-request response buffer/responded flag/error formatter, and write serializer channel. It does not reconstruct multi-fragment records.

## Dependencies and Integration Points
Depends on go-nfs `Server.handlerFor`, go-nfs-client RPC/XDR packages, TCP record marking, and procedure handlers registered from `nfs.go`/`mount.go`.

## Risks and Edge Cases
Fragment reconstruction is unimplemented; malformed auth/version handling is minimal; error marshalling uses mixed endian in some RPC errors; writer goroutine failure silently returns.

## Test Signals
Protocol tests should cover short records, unsupported procedures, unread body drain, duplicate header writes, multi-request serialization, and client disconnects.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/conn.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/errors.go -->
# sources/user-network-fs/go-nfs/errors.go

## Purpose
Defines RPC-level and NFS-level error types plus helpers for status bodies and write-error mapping.

## Important APIs, Types, and Functions
`RPCError`, `AuthError`, `RPCMismatchError`, `ResponseCodeProcUnavailableError`, `ResponseCodeSystemError`, `NFSStatusError`, `StatusErrorWithBody`, `errFormatterWithBody`, and `statusFromWriteError` are central.

## Control Flow
Handlers return ordinary errors or these typed errors. `conn.err` uses the active formatter to write RPC accept/deny status and optional NFS status body.

## State and Persistence Behavior
Errors are transient response state; formatter functions with prebuilt zero bodies are package-level constants.

## Dependencies and Integration Points
Integrated by every NFS handler via `w.errorFmt`, especially weak-cache-consistency and post-op-attr error replies.

## Risks and Edge Cases
`AuthError` and `RPCMismatchError` marshal little-endian while XDR is big-endian, likely wrong. Unknown errors collapse to system error, losing detail.

## Test Signals
Tests should assert wire bytes for each error class and procedure-specific error body length.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/helloworld/main.go -->
# sources/user-network-fs/go-nfs/example/helloworld/main.go

## Purpose
Shows a minimal read-only NFS server backed by an in-memory billy filesystem.

## Important APIs, Types, and Functions
Defines `ROFS` capability wrapper and `main`.

## Control Flow
The program listens on an ephemeral TCP port, creates a memfs file `hello.txt`, wraps memfs as read-only, layers null auth and caching handlers, and calls `nfs.Serve`.

## State and Persistence Behavior
State is in-memory only and lasts for the process.

## Dependencies and Integration Points
Depends on billy memfs, go-nfs helpers, and TCP listener setup.

## Risks and Edge Cases
No authentication or export selection; ephemeral port is printed for manual use. It is an example, not hardened server code.

## Test Signals
Manual signal is mounting the printed address and reading `hello.txt`; build tests catch API drift.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/helloworld/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/osnfs/changeos.go -->
# sources/user-network-fs/go-nfs/example/osnfs/changeos.go

## Purpose
Adds metadata mutation support to a billy OS filesystem wrapper for the writable NFS example.

## Important APIs, Types, and Functions
`NewChangeOSFS`, `COS`, `Chmod`, `Lchown`, `Chown`, and `Chtimes` are the main APIs.

## Control Flow
Each method joins the billy root with the requested path and delegates to the corresponding `os` package function.

## State and Persistence Behavior
No extra state beyond the embedded billy filesystem.

## Dependencies and Integration Points
Used by `example/osnfs/main.go` through `NullAuthHandler.Change`; integrates with NFS setattr/create/mkdir flows.

## Risks and Edge Cases
Path joining relies on the billy filesystem's root and join behavior; no extra path traversal hardening beyond osfs/chroot semantics.

## Test Signals
Manual NFS setattr/chmod/chown tests against `osnfs` validate these methods.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/osnfs/changeos.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/osnfs/changeos_unix.go -->
# sources/user-network-fs/go-nfs/example/osnfs/changeos_unix.go

## Purpose
Adds Unix special-file and hard-link operations to the writable OS-backed NFS example.

## Important APIs, Types, and Functions
`COS.Mknod`, `Mkfifo`, `Link`, and `Socket` implement the `nfs.UnixChange` interface on Unix builds.

## Control Flow
Methods map NFS major/minor into a device number, call Unix mknod/mkfifo/link, or create and bind a Unix socket.

## State and Persistence Behavior
State is the special filesystem object created in the exported OS tree; socket fd is not explicitly closed after bind.

## Dependencies and Integration Points
Used by `nfs_onmknod.go` and `nfs_onlink.go` when the example handler is mounted.

## Risks and Edge Cases
Requires privileges for device nodes, does not close socket fd, and `Link` expects its source path interpretation to match handler call sites.

## Test Signals
Manual client tests for `mknod`, FIFO creation, socket creation, and hard links exercise this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/osnfs/changeos_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/osnfs/main.go -->
# sources/user-network-fs/go-nfs/example/osnfs/main.go

## Purpose
Runs an NFS server exporting a real OS directory with writable metadata and Unix special-file support.

## Important APIs, Types, and Functions
`main` parses `<path> [port]`, listens, wraps `osfs.New` with `NewChangeOSFS`, layers null auth and caching handlers, and serves.

## Control Flow
The server binds to the requested or ephemeral TCP port and serves until `nfs.Serve` returns.

## State and Persistence Behavior
State is the exported OS directory and in-memory handle cache.

## Dependencies and Integration Points
Depends on billy osfs, helper handlers, and the `COS` change wrapper files.

## Risks and Edge Cases
No authentication, no export restrictions beyond the chosen path, and no graceful shutdown. Running as privileged user exposes powerful filesystem mutation operations.

## Test Signals
Manual mount/read/write/setattr tests and `go build ./example/osnfs` are the key signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/osnfs/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/osview/main.go -->
# sources/user-network-fs/go-nfs/example/osview/main.go

## Purpose
Runs a read-only view-style NFS server using `memphis` to expose an OS tree through a billy filesystem.

## Important APIs, Types, and Functions
`main` parses args, listens, builds `memphis.FromOS(...).AsBillyFS(0,0)`, wraps null auth/caching, and serves.

## Control Flow
Control flow is the same example server pattern as `osnfs`, but without writable change support.

## State and Persistence Behavior
State is the external OS tree as represented by memphis plus the in-memory handle cache.

## Dependencies and Integration Points
Depends on the external `github.com/willscott/memphis` package and go-nfs helpers.

## Risks and Edge Cases
No auth or write support; behavior depends on memphis snapshot/live-view semantics.

## Test Signals
Build and manual NFS mount tests validate the example.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/osview/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/file.go -->
# sources/user-network-fs/go-nfs/file.go

## Purpose
Defines NFS file metadata conversion, weak-cache-consistency helpers, and parsing/applying NFS setattr requests.

## Important APIs, Types, and Functions
Key types/functions are `FileAttribute`, `FileType`, `FileCacheAttribute`, `ToFileAttribute`, `tryStat`, `WriteWcc`, `WritePostOpAttrs`, `SetFileAttributes`, `Apply`, `Mode`, and `ReadSetFileAttributes`.

## Control Flow
Handlers convert billy `os.FileInfo` into NFS attributes, parse optional sattr fields from XDR, apply requested changes through `billy.Change`, and encode pre/post attribute presence wrappers.

## State and Persistence Behavior
No global state; operations mutate backing files through `Chmod`, `Lchown`, `Chtimes`, opening/truncating files, and derive attributes from current stat calls.

## Dependencies and Integration Points
Used by nearly all NFS procedures; depends on billy, the internal `file` metadata package, XDR, and OS error mapping.

## Risks and Edge Cases
`Apply` returns nil for some unknown `Lstat` errors, time pointer comparison is by pointer not value in one check, and truncation opens with `O_EXCL` in a questionable way.

## Test Signals
Procedure tests for setattr, create, mkdir, write, wcc bodies, symlinks, and platform stat metadata cover this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file.go -->
# sources/user-network-fs/go-nfs/file/file.go

## Purpose
Defines portable extraction of non-standard stat metadata from `os.FileInfo`.

## Important APIs, Types, and Functions
`FileInfo` carries nlink, uid, gid, device major/minor, and fileid; `GetInfo` checks custom `Sys()` payloads then delegates to platform code.

## Control Flow
Callers pass `os.FileInfo`; the function returns platform metadata when available or nil when unsupported.

## State and Persistence Behavior
Stateless conversion helper.

## Dependencies and Integration Points
Used by `nfs.ToFileAttribute` to populate NFS nlink, owner, specdata, and fileid.

## Risks and Edge Cases
Fallback hashing in callers is less stable than real inode data; custom `Sys()` values must match this package's type.

## Test Signals
Metadata tests should feed both real OS stats and synthetic `file.FileInfo` payloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file_other.go -->
# sources/user-network-fs/go-nfs/file/file_other.go

## Purpose
Provides the fallback metadata extractor for unsupported platforms.

## Important APIs, Types, and Functions
`getOSFileInfo` always returns nil.

## Control Flow
Build tags select this file for platforms not otherwise handled.

## State and Persistence Behavior
Stateless.

## Dependencies and Integration Points
Used indirectly by `file.GetInfo`.

## Risks and Edge Cases
NFS fileids fall back to path hashes and ownership/specdata are unavailable on these platforms.

## Test Signals
Cross-compilation builds validate this fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file_unix.go -->
# sources/user-network-fs/go-nfs/file/file_unix.go

## Purpose
Extracts Unix stat metadata for common Unix-like platforms.

## Important APIs, Types, and Functions
`getOSFileInfo` reads `*syscall.Stat_t` and returns nlink, uid, gid, `unix.Major/Minor(Rdev)`, and inode fileid.

## Control Flow
Called by `GetInfo` after a filesystem stat.

## State and Persistence Behavior
Stateless conversion.

## Dependencies and Integration Points
Feeds NFS attributes for Unix exports and special devices.

## Risks and Edge Cases
Assumes `FileInfo.Sys()` is `*syscall.Stat_t`; virtual filesystems returning other payloads fall back to path hashes.

## Test Signals
Unix tests should verify inode/fileid stability and device major/minor on special nodes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file_wasm.go -->
# sources/user-network-fs/go-nfs/file/file_wasm.go

## Purpose
Extracts wasm-compatible stat metadata where major/minor device numbers are unavailable.

## Important APIs, Types, and Functions
`getOSFileInfo` maps nlink, uid, gid, and inode into `FileInfo`.

## Control Flow
Same flow as the Unix extractor but omits specdata.

## State and Persistence Behavior
Stateless.

## Dependencies and Integration Points
Used by wasm builds of go-nfs metadata conversion.

## Risks and Edge Cases
Wasm filesystem semantics may not provide meaningful inode or ownership values.

## Test Signals
Wasm compilation and simple stat conversion tests validate it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file_wasm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file_windows.go -->
# sources/user-network-fs/go-nfs/file/file_windows.go

## Purpose
Provides the Windows metadata extractor fallback.

## Important APIs, Types, and Functions
`getOSFileInfo` currently returns nil, with a comment noting possible future Windows API support.

## Control Flow
No runtime control flow beyond returning nil.

## State and Persistence Behavior
Stateless.

## Dependencies and Integration Points
Used by `file.GetInfo` on Windows.

## Risks and Edge Cases
NFS attributes lack nlink/uid/gid/inode and fall back to path-derived fileids in callers.

## Test Signals
Windows build tests validate compilation; behavior tests would need custom metadata support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/filesystem.go -->
# sources/user-network-fs/go-nfs/filesystem.go

## Purpose
Defines the filesystem-level statistics structure used by the NFS FSSTAT procedure.

## Important APIs, Types, and Functions
`FSStat` contains total/free/available sizes and files plus `CacheHint`.

## Control Flow
`onFSStat` fills defaults and lets the user handler override the struct.

## State and Persistence Behavior
No behavior or persistence in this file.

## Dependencies and Integration Points
Part of the `Handler.FSStat` integration point.

## Risks and Edge Cases
Fields must match XDR ordering expected by NFSv3 clients.

## Test Signals
FSSTAT procedure tests should assert encoded values after handler customization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/filesystem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/handler.go -->
# sources/user-network-fs/go-nfs/handler.go

## Purpose
Defines the user-supplied filesystem handler interfaces for go-nfs.

## Important APIs, Types, and Functions
`Handler`, `UnixChange`, and `CachingHandler` specify mount authorization, mutation support, handle mapping, FS stats, special-file operations, and directory verifier cache hooks.

## Control Flow
Connection/procedure code calls these interfaces for every request rather than owning a filesystem directly.

## State and Persistence Behavior
Implementations may hold persistent handle caches, mounted filesystems, and authorization state; this file only defines contracts.

## Dependencies and Integration Points
Used by helper handlers, examples, and all NFS procedures.

## Risks and Edge Cases
Incorrect handler implementations can break stateless NFS semantics, leak stale handles, or expose writes without authorization. `HandleLimit` influences readdir chunking.

## Test Signals
Interface conformance is tested indirectly by helpers, examples, and procedure tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/cachinghandler.go -->
# sources/user-network-fs/go-nfs/helpers/cachinghandler.go

## Purpose
Provides an LRU-backed implementation of opaque NFS file handles and directory verifier caching around another handler.

## Important APIs, Types, and Functions
`NewCachingHandler`, `CachingHandler.ToHandle`, `FromHandle`, `InvalidateHandle`, `HandleLimit`, `VerifierFor`, `DataForVerifier`, and reverse-cache helpers are central.

## Control Flow
`ToHandle` reuses an existing UUID for the same filesystem/path or allocates one, evicting the oldest cache entry. `FromHandle` resolves UUIDs and refreshes related entries. Directory verifiers hash path and sorted contents and cache listings.

## State and Persistence Behavior
Persistent process state includes active handle LRU, reverse path-to-UUID map protected by a mutex, verifier LRU, and cache size.

## Dependencies and Integration Points
Used by examples and recommended for handlers that do not provide stable handles themselves.

## Risks and Edge Cases
`activeHandles` LRU is used concurrently without an outer mutex; reverse handle slices are returned without copying; filesystem comparison uses `reflect.DeepEqual`. Race tests target this area.

## Test Signals
`cachinghandler_test.go` stresses concurrent ToHandle/FromHandle/Invalidate; running with `-race` is important.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/cachinghandler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/cachinghandler_test.go -->
# sources/user-network-fs/go-nfs/helpers/cachinghandler_test.go

## Purpose
Concurrency tests for the caching handler's handle and reverse-cache paths.

## Important APIs, Types, and Functions
Tests are `TestCachingHandlerConcurrentToHandle`, `TestCachingHandlerConcurrentToHandleAndFromHandle`, and `TestCachingHandlerConcurrentInvalidateHandle`.

## Control Flow
They create a memfs-backed null-auth handler, wrap it in `CachingHandler`, then run goroutines creating, resolving, and invalidating handles across unique and shared paths.

## State and Persistence Behavior
State is in-memory cache structures and a memfs filesystem.

## Dependencies and Integration Points
Depends on `helpers/memfs` and helper handler construction.

## Risks and Edge Cases
The tests do not assert returned values; they are intended primarily for race detector coverage.

## Test Signals
Run with `go test -race -run TestCachingHandlerConcurrent ./helpers` to catch synchronization bugs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/cachinghandler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/memfs/memfs.go -->
# sources/user-network-fs/go-nfs/helpers/memfs/memfs.go

## Purpose
Implements an in-memory billy filesystem variant with stable enough file behavior for go-nfs tests.

## Important APIs, Types, and Functions
`Memory`, `New`, filesystem methods, symlink resolution, `file` methods, `fileInfo`, and flag helpers are central.

## Control Flow
Filesystem operations delegate to `storage`; opened files duplicate shared content with independent cursor/flags. Reads/writes/truncates operate on shared `content`; symlinks resolve relative targets for `Stat`, `OpenFile`, and `ReadDir`.

## State and Persistence Behavior
Persistent state is in `storage` maps and shared `content` byte slices. File handles track cursor, flags, mode, mtime, and closed state.

## Dependencies and Integration Points
Used by helper tests and examples needing a billy filesystem without OS dependencies.

## Risks and Edge Cases
Storage maps are not mutex-protected, so concurrent filesystem mutations can race. `WriteAt` semantics in storage overwrite by append/slice and may not preserve tail in all cases.

## Test Signals
Caching handler tests use this filesystem; direct tests should cover symlinks, append, truncate, rename, and concurrent access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/memfs/memfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/memfs/storage.go -->
# sources/user-network-fs/go-nfs/helpers/memfs/storage.go

## Purpose
Stores the backing tree for the helper memfs implementation.

## Important APIs, Types, and Functions
`storage`, `newStorage`, `New`, `Get`, `Children`, `Rename`, `move`, `Remove`, `clean`, and `content.ReadAt/WriteAt` are important.

## Control Flow
`New` creates files and recursively ensures parents. `Rename` builds a list of paths to move and updates file/children maps. `content` protects byte access with an RW mutex.

## State and Persistence Behavior
Persistent state is `files` and `children` maps plus each file's shared content buffer.

## Dependencies and Integration Points
Used exclusively by `memfs.go` behind billy filesystem methods.

## Risks and Edge Cases
Map operations are unsynchronized; directory rename prefix matching can catch paths with similar prefixes; `WriteAt` casts offsets into slice bounds and needs careful large-offset handling.

## Test Signals
Memfs-focused tests should exercise nested rename/remove, directory children consistency, sparse writes, negative offsets, and race detection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/memfs/storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/nullauthhandler.go -->
# sources/user-network-fs/go-nfs/helpers/nullauthhandler.go

## Purpose
Provides a trivial no-auth handler exposing one billy filesystem for all mount requests.

## Important APIs, Types, and Functions
`NewNullAuthHandler`, `NullAuthHandler.Mount`, `Change`, `FSStat`, handle stubs, and `HandleLimit` are central.

## Control Flow
Mount always succeeds with `AUTH_NULL`; `Change` returns the filesystem if it implements `billy.Change`; handle methods are placeholders intended to be wrapped by `CachingHandler`.

## State and Persistence Behavior
State is only the embedded billy filesystem.

## Dependencies and Integration Points
Used by examples and tests as the simplest `nfs.Handler` implementation.

## Risks and Edge Cases
Using it without `CachingHandler` returns empty handles and cannot resolve them. It performs no authorization or export path checks.

## Test Signals
Examples and helper tests validate it in combination with `CachingHandler`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/helpers/nullauthhandler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/log.go -->
# sources/user-network-fs/go-nfs/log.go

## Purpose
Implements the package-level logging abstraction and default logger for go-nfs.

## Important APIs, Types, and Functions
`Logger`, `DefaultLogger`, log levels, `SetLogger`, `ParseLevel`, level getters/setters, and per-level print/printf methods are central.

## Control Flow
Package init reads `LOG_LEVEL`; methods compare configured level against message severity and delegate to the standard `log` package with prefixes.

## State and Persistence Behavior
Global mutable state is `nfs.Log`; default logger stores a level. There is no synchronization around logger replacement or level mutation.

## Dependencies and Integration Points
Used throughout connection and handler code for diagnostics.

## Risks and Edge Cases
`Panic`/`Fatal` methods only log, they do not call `panic` or `os.Exit`, which may surprise callers. Level comparison allows messages at or below the configured threshold per enum ordering.

## Test Signals
Tests should parse all levels, verify filtering, and document non-exiting fatal/panic behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/mount.go -->
# sources/user-network-fs/go-nfs/mount.go

## Purpose
Registers and implements the ONC mount protocol procedures needed by NFS clients.

## Important APIs, Types, and Functions
`onMountNull`, `onMount`, and `onUMount` are registered for mount service procedures.

## Control Flow
`onMount` reads the requested dirpath, calls `Handler.Mount`, writes RPC success, encodes mount status, and when OK writes the root file handle and auth flavors. `onUMount` consumes the opaque path and acknowledges.

## State and Persistence Behavior
No server-side mount table is maintained; state is delegated to the handler and handle cache.

## Dependencies and Integration Points
Depends on `RegisterMessageHandler`, `MountRequest`, XDR, and `Handler.ToHandle`.

## Risks and Edge Cases
Auth is TODO; unmount does not invalidate handles or track clients; status OK with an empty handle is possible if handler/cache is misconfigured.

## Test Signals
Mount client integration tests should verify handle/auth flavor encoding and non-OK status behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/mountinterface.go -->
# sources/user-network-fs/go-nfs/mountinterface.go

## Purpose
Defines mount protocol constants, enum stringers, auth flavor constants, and mount request/response shapes.

## Important APIs, Types, and Functions
Important declarations are service ID companion values, `FHSize`, `MNTNameLen`, `MountStatus`, `MountProcedure.String`, `AuthFlavor`, `MountRequest`, and `MountResponse`.

## Control Flow
No runtime control flow except enum string conversion.

## State and Persistence Behavior
Stateless protocol definitions.

## Dependencies and Integration Points
Used by `mount.go`, handler implementations, and request logging.

## Risks and Edge Cases
Constants must match RFC/NFS mount protocol expectations. `MountResponse.AuthFlavors` uses `[]int` while auth flavor constants are typed, so encoding assumptions matter.

## Test Signals
Mount procedure tests and client mount attempts validate the wire shape.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/mountinterface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs.go -->
# sources/user-network-fs/go-nfs/nfs.go

## Purpose
Registers all NFSv3 procedure handlers and implements the null procedure.

## Important APIs, Types, and Functions
`init` calls `RegisterMessageHandler` for NFS procedures 0 through 21; `onNull` writes an empty successful response.

## Control Flow
At package initialization, handlers become available to the server dispatch table; null requests return no body.

## State and Persistence Behavior
State is global registration in the server handler registry defined elsewhere in the package.

## Dependencies and Integration Points
Integrates every `nfs_on*.go` handler with `conn.handle`.

## Risks and Edge Cases
Missing or duplicate registration would make procedures unavailable. Registration errors are intentionally ignored with `_ =`.

## Test Signals
Protocol tests should assert all expected NFS procedures are registered and null returns success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onaccess.go -->
# sources/user-network-fs/go-nfs/nfs_onaccess.go

## Purpose
Implements NFS ACCESS, returning allowed access bits and post-op attributes.

## Important APIs, Types, and Functions
`onAccess` is the handler.

## Control Flow
It reads a file handle and requested mask, resolves the handle, reads the mask, writes OK status and post-op attrs, and strips write-related bits when the filesystem lacks write capability.

## State and Persistence Behavior
No persistent state; observes filesystem capabilities and attributes.

## Dependencies and Integration Points
Depends on `Handler.FromHandle`, billy capability checks, `tryStat`, and XDR.

## Risks and Edge Cases
Permission checks are coarse and do not inspect actual mode bits, uid/gid, or path-specific ACLs.

## Test Signals
ACCESS tests should compare masks on read-only and writable handlers and validate stale/invalid handle errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onaccess.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_oncommit.go -->
# sources/user-network-fs/go-nfs/nfs_oncommit.go

## Purpose
Implements NFS COMMIT as a no-op because writes are immediately pushed to the backing store.

## Important APIs, Types, and Functions
`onCommit` handles the procedure.

## Control Flow
It reads the file handle, lets the connection drain offset/count, resolves the handle, checks write capability, writes OK, post-op attrs, and the server write verifier ID.

## State and Persistence Behavior
No data is flushed here beyond whatever backing filesystem already did; response includes `Server.ID`.

## Dependencies and Integration Points
Depends on `Handler.FromHandle`, billy write capability, `tryStat`, and connection body draining.

## Risks and Edge Cases
Returning server fault on read-only commit may not match all client expectations. It ignores offset/count entirely.

## Test Signals
Write/commit client tests should assert verifier stability and response WCC body.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_oncommit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_oncreate.go -->
# sources/user-network-fs/go-nfs/nfs_oncreate.go

## Purpose
Implements NFS CREATE for regular files with unchecked and guarded modes.

## Important APIs, Types, and Functions
`onCreate` and create mode constants are central.

## Control Flow
The handler decodes directory/name and create mode, parses attributes or rejects exclusive mode, resolves the parent, checks write capability and name length, creates/closes the file, applies attributes, returns optional handle, post-op attrs, and directory WCC.

## State and Persistence Behavior
Persistent changes are file creation and metadata mutations in the backing billy filesystem plus a new cached handle.

## Dependencies and Integration Points
Depends on `SetFileAttributes`, `Handler.Change`, billy create/stat, and XDR.

## Risks and Edge Cases
Exclusive create is unsupported; post-op attrs call `tryStat(fs, []string{file.Name()})`, which may lose parent path; guarded semantics are minimal.

## Test Signals
CREATE tests should cover existing file guarded/unchecked behavior, exclusive rejection, attributes, and directory WCC.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_oncreate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onfsinfo.go -->
# sources/user-network-fs/go-nfs/nfs_onfsinfo.go

## Purpose
Implements NFS FSINFO with advertised transfer sizes and capability flags.

## Important APIs, Types, and Functions
`onFSInfo` and `FSInfoProperty*` constants are central.

## Control Flow
It reads a handle, resolves it, writes post-op attrs, fills an inline `fsinfores` with large read/write limits, dtpref, max filesize, nanosecond delta, and properties inferred from filesystem interfaces/capabilities.

## State and Persistence Behavior
No persistent state.

## Dependencies and Integration Points
Depends on billy symlink/write capability, `tryStat`, and XDR encoding.

## Risks and Edge Cases
Advertised limits are guesses and not user-configurable; hard-link support is inferred from symlink support, which is imprecise.

## Test Signals
FSINFO tests should assert property bits for read-only, writable, and symlink-capable filesystems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onfsinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onfsstat.go -->
# sources/user-network-fs/go-nfs/nfs_onfsstat.go

## Purpose
Implements NFS FSSTAT with defaults that handlers can override.

## Important APIs, Types, and Functions
`onFSStat` is the handler.

## Control Flow
It reads a handle, resolves it, initializes huge default capacity values, zeros available space for read-only filesystems, calls `Handler.FSStat`, and writes post-op attrs plus the final stats.

## State and Persistence Behavior
No persistent state; handler may compute live filesystem statistics.

## Dependencies and Integration Points
Depends on `FSStat`, billy capabilities, handler override, and XDR.

## Risks and Edge Cases
Defaults are unrealistic and may mislead clients if handlers do not override. Handler errors are mapped coarsely unless already `NFSStatusError`.

## Test Signals
FSSTAT tests should verify defaults, read-only adjustment, and custom handler overrides.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onfsstat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_ongetattr.go -->
# sources/user-network-fs/go-nfs/nfs_ongetattr.go

## Purpose
Implements NFS GETATTR by resolving a file handle and encoding current file attributes.

## Important APIs, Types, and Functions
`onGetAttr` is the handler.

## Control Flow
It reads an opaque handle, resolves it to filesystem/path, lstat's the path, maps not-exist and I/O errors, converts stat info with `ToFileAttribute`, and writes OK plus attrs.

## State and Persistence Behavior
No mutation; observes backing filesystem metadata.

## Dependencies and Integration Points
Depends on `Handler.FromHandle`, billy `Lstat`, `ToFileAttribute`, and XDR.

## Risks and Edge Cases
Symlink handling depends on `Lstat`; missing or stale handles are distinguishable only through handler errors.

## Test Signals
GETATTR tests should cover files, dirs, symlinks, stale handles, and platform metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_ongetattr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onlink.go -->
# sources/user-network-fs/go-nfs/nfs_onlink.go

## Purpose
Implements NFS LINK for filesystems whose `Change` object supports `UnixChange`.

## Important APIs, Types, and Functions
`onLink` is the handler.

## Control Flow
It decodes a target directory/name, attributes, and source opaque data, resolves parent, validates write capability/name/nonexistence/parent directory, obtains `UnixChange`, calls `Link`, applies attrs, and returns handle, attrs, and WCC.

## State and Persistence Behavior
Persistent state is a new hard link and possible metadata changes.

## Dependencies and Integration Points
Depends on `UnixChange.Link`, `SetFileAttributes`, and handle caching.

## Risks and Edge Cases
The source is decoded as opaque bytes and cast to string path; this may not match NFS LINK argument semantics, where source is usually a file handle. Error mappings are broad.

## Test Signals
Hard-link integration tests against `example/osnfs` should validate source semantics and link counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onlink.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onlookup.go -->
# sources/user-network-fs/go-nfs/nfs_onlookup.go

## Purpose
Implements NFS LOOKUP including special handling for `.` and `..`.

## Important APIs, Types, and Functions
`lookupSuccessResponse` and `onLookup` are central.

## Control Flow
The handler decodes directory handle/name, verifies parent is a directory, returns the same handle for `.`, parent handle for `..`, or lstat's a child and returns a new handle plus object and directory attrs.

## State and Persistence Behavior
No mutation; may create/reuse cached handles.

## Dependencies and Integration Points
Depends on `Handler.FromHandle`, `Handler.ToHandle`, billy `Lstat`, `tryStat`, and XDR.

## Risks and Edge Cases
Root `..` returns access error rather than root; appending to path slices can alias underlying arrays if handlers reuse slices carelessly.

## Test Signals
LOOKUP tests should cover dot, dotdot, root dotdot, missing entries, and symlink lstat behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onlookup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onmkdir.go -->
# sources/user-network-fs/go-nfs/nfs_onmkdir.go

## Purpose
Implements NFS MKDIR.

## Important APIs, Types, and Functions
`onMkdir` and `mkdirDefaultMode` are central.

## Control Flow
It decodes parent/name and attributes, resolves parent, checks write capability/name/special dot names/existing path, creates the directory with requested or default mode, applies attributes when possible, and returns handle, attrs, and parent WCC.

## State and Persistence Behavior
Persistent state is a new directory and metadata changes.

## Dependencies and Integration Points
Depends on billy `MkdirAll`, handler change support, and XDR.

## Risks and Edge Cases
Default mode is `755` decimal, not octal `0755`, which likely creates wrong permissions. `MkdirAll` may create missing parents instead of strict single-level mkdir.

## Test Signals
MKDIR tests should assert mode bits, existing-file/dir errors, dot-name rejection, and parent WCC.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onmkdir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onmknod.go -->
# sources/user-network-fs/go-nfs/nfs_onmknod.go

## Purpose
Implements NFS MKNOD for character devices, block devices, sockets, and FIFOs through `UnixChange`.

## Important APIs, Types, and Functions
`nfs_ftype` constants and `onMknod` are central.

## Control Flow
The handler decodes parent/name/type, resolves and validates parent/write support, obtains `UnixChange`, parses type-specific attrs/specdata, creates the special node, applies attrs, and writes handle, attrs, and WCC.

## State and Persistence Behavior
Persistent state is a special filesystem object in the backing store.

## Dependencies and Integration Points
Depends on `UnixChange.Mknod`, `Mkfifo`, `Socket`, `SetFileAttributes`, and XDR.

## Risks and Edge Cases
The switch groups char and block cases together via empty `case FTYPE_NF3CHR:` fallthrough-like behavior is not automatic in Go, so char devices currently do nothing before success body. Permissions require OS privileges.

## Test Signals
Tests should cover each supported ftype, char-device behavior, bad type, no UnixChange, and unprivileged error mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onmknod.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onpathconf.go -->
# sources/user-network-fs/go-nfs/nfs_onpathconf.go

## Purpose
Implements NFS PATHCONF with static path configuration limits.

## Important APIs, Types, and Functions
`PathNameMax` and `onPathConf` are central.

## Control Flow
It reads a handle, resolves it, writes post-op attrs, and encodes static link/name/truncation/chown/case flags.

## State and Persistence Behavior
No persistent state.

## Dependencies and Integration Points
Used by clients after FSINFO; depends on `tryStat` and XDR.

## Risks and Edge Cases
Static `LinkMax=1` conflicts with hard-link support in some handlers; case sensitivity and chown restriction are not derived from the backing filesystem.

## Test Signals
PATHCONF tests should assert constants and stale handle behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onpathconf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onread.go -->
# sources/user-network-fs/go-nfs/nfs_onread.go

## Purpose
Implements NFS READ.

## Important APIs, Types, and Functions
`nfsReadArgs`, `nfsReadResponse`, `MaxRead`, and `onRead` are central.

## Control Flow
It reads handle/offset/count, opens the file, stats it, clamps count at EOF and `MaxRead`, reads with `ReadAt`, sets EOF when appropriate, and writes post-op attrs plus data.

## State and Persistence Behavior
No persistent mutation; opens and closes a backing file per request.

## Dependencies and Integration Points
Depends on billy file `ReadAt`, `Stat`, `ToFileAttribute`, and XDR.

## Risks and Edge Cases
Large offsets cast to int64 after uint64 may overflow; opening directories or special files maps to access/IO depending on billy behavior.

## Test Signals
READ tests should cover EOF, partial reads, MaxRead clamp, missing files, and large offset validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onread.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onreaddir.go -->
# sources/user-network-fs/go-nfs/nfs_onreaddir.go

## Purpose
Implements NFS READDIR with cookie verifier support.

## Important APIs, Types, and Functions
`readDirArgs`, `readDirEntity`, `onReadDir`, `getDirListingWithVerifier`, and local `hashPathAndContents` are central.

## Control Flow
It resolves a directory handle, obtains sorted listing from cache or filesystem, validates cookie verifier, emits `.`/`..` and entries starting after the requested cookie until estimated count or handle-limit thresholds, then writes eof.

## State and Persistence Behavior
No filesystem mutation; verifier/listing caches may be updated through `CachingHandler`.

## Dependencies and Integration Points
Depends on handler handle/verifier interfaces, billy `ReadDir`, sorting, and XDR.

## Risks and Edge Cases
Response sizing uses rough estimates, cookies are index-based and unstable if directory changes, and there is a duplicate hash helper also present in helpers with slightly different input format.

## Test Signals
READDIR tests should cover small count, bad verifier, continuation cookies, changed directories, and handle-limit truncation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onreaddir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onreaddirplus.go -->
# sources/user-network-fs/go-nfs/nfs_onreaddirplus.go

## Purpose
Implements NFS READDIRPLUS with attrs and handles for each directory entry.

## Important APIs, Types, and Functions
`readDirPlusArgs`, `readDirPlusEntity`, `joinPath`, and `onReadDirPlus` are central.

## Control Flow
It mirrors READDIR but also generates attributes and file handles for entries, tracks both `DirCount` and `MaxCount`, and includes post-op attrs and verifier in the response.

## State and Persistence Behavior
May allocate/reuse many cached handles for returned entries; no backing filesystem mutation.

## Dependencies and Integration Points
Depends on `getDirListingWithVerifier`, `Handler.ToHandle`, `ToFileAttribute`, and XDR optional fields.

## Risks and Edge Cases
Sizing is approximate; handle cache limits influence pagination; `.` and `..` do not both include handles/attrs consistently.

## Test Signals
READDIRPLUS tests should cover pagination, verifier reuse, attrs/handles presence, and too-small arguments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onreaddirplus.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onreadlink.go -->
# sources/user-network-fs/go-nfs/nfs_onreadlink.go

## Purpose
Implements NFS READLINK.

## Important APIs, Types, and Functions
`onReadLink` is the handler.

## Control Flow
It reads a handle, resolves it, calls `fs.Readlink`, maps missing/non-symlink/access errors, writes post-op attrs and the link target string.

## State and Persistence Behavior
No mutation.

## Dependencies and Integration Points
Depends on billy symlink support, `tryStat`, and XDR.

## Risks and Edge Cases
The non-symlink check calls `fs.Stat`, which follows symlinks, so error classification can be imperfect.

## Test Signals
READLINK tests should cover valid symlink, regular file, missing file, and stale handle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onreadlink.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onremove.go -->
# sources/user-network-fs/go-nfs/nfs_onremove.go

## Purpose
Implements NFS REMOVE and is reused for RMDIR.

## Important APIs, Types, and Functions
`onRemove` is the handler.

## Control Flow
It decodes parent/name, resolves parent, checks write capability/name length/parent directory, captures pre-op dir attrs, removes the child, invalidates the child's cached handle, and writes directory WCC.

## State and Persistence Behavior
Persistent state is deletion from the backing filesystem and handle invalidation.

## Dependencies and Integration Points
Depends on billy `Remove`, handler cache invalidation, WCC helpers, and XDR.

## Risks and Edge Cases
Same implementation for files and directories may not distinguish non-empty directory or wrong procedure status precisely; it creates a handle for deletion solely to invalidate it.

## Test Signals
REMOVE/RMDIR tests should cover file removal, empty/non-empty directories, read-only FS, stale handles, and cache invalidation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onremove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onrename.go -->
# sources/user-network-fs/go-nfs/nfs_onrename.go

## Purpose
Implements NFS RENAME across paths within the same billy filesystem.

## Important APIs, Types, and Functions
`doubleWccErrorBody` and `onRename` are central.

## Control Flow
It decodes source and destination directory/name pairs, resolves both handles, rejects cross-filesystem renames, checks write capability/name lengths/parent dirs, captures pre-op WCC for both dirs, renames, invalidates the old handle, and writes both WCC blocks.

## State and Persistence Behavior
Persistent state is the backing filesystem rename and handle invalidation.

## Dependencies and Integration Points
Depends on billy `Rename`, `reflect.DeepEqual` for filesystem identity, and XDR.

## Risks and Edge Cases
Filesystem identity via `DeepEqual` can be fragile; destination handle invalidation is not explicit; overwrite semantics are delegated to billy implementation.

## Test Signals
RENAME tests should cover same dir, cross dir, overwrite, cross filesystem rejection, stale source handle, and WCC bodies.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onrename.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onrmdir.go -->
# sources/user-network-fs/go-nfs/nfs_onrmdir.go

## Purpose
Implements NFS RMDIR by delegating to REMOVE.

## Important APIs, Types, and Functions
`onRmDir` simply calls `onRemove`.

## Control Flow
All parsing, validation, deletion, and response behavior are inherited from `onRemove`.

## State and Persistence Behavior
Persistent state is directory deletion through the backing filesystem.

## Dependencies and Integration Points
Depends entirely on `nfs_onremove.go`.

## Risks and Edge Cases
RMDIR-specific status distinctions are not represented here; non-directory removal through RMDIR may map according to billy `Remove` rather than NFS expectations.

## Test Signals
RMDIR tests should include non-directory target, non-empty directory, and successful empty directory removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onrmdir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onsetattr.go -->
# sources/user-network-fs/go-nfs/nfs_onsetattr.go

## Purpose
Implements NFS SETATTR, including optional ctime guard support and weak-cache-consistency response.

## Important APIs, Types, and Functions
`onSetAttr` is the handler.

## Control Flow
It reads a handle, resolves it, parses `SetFileAttributes`, lstat's the object, optionally reads and checks a guard ctime, validates write capability, applies changes through `Handler.Change`, then writes OK and WCC data.

## State and Persistence Behavior
Persistent state is metadata or size mutation of the backing object.

## Dependencies and Integration Points
Depends on `ReadSetFileAttributes`, `SetFileAttributes.Apply`, billy write capability, XDR, and WCC helpers.

## Risks and Edge Cases
Guard comparison depends on `FileTime` equality from current stat; `Apply` may return non-NFS errors for some paths; read-only filesystems reject after parsing guard.

## Test Signals
SETATTR tests should cover mode, uid/gid, size, atime/mtime, guard success/failure, symlink truncation rejection, and read-only behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onsetattr.go -->
