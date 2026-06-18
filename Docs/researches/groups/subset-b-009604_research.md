# Research Group subset-b-009604

Grouped research for go-fuse pathfs, fuse server/protocol, tests, and internal syscall helper files. Each section preserves the source path for deterministic reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/loopback.go -->
# `sources/user-network-fs/go-fuse/fuse/pathfs/loopback.go`

## Purpose
Implements `NewLoopbackFileSystem`, a pathfs `FileSystem` backed by a real directory. It translates virtual paths with `GetPath` and delegates stat, open, directory listing, metadata mutation, links, and create/delete operations to the host OS.

## Important APIs, Types, And Functions
`loopbackFileSystem`, `NewLoopbackFileSystem`, `StatFs`, `GetAttr`, `OpenDir`, `Open`, `Create`, `Access`, and path-based chmod/chown/truncate/link/rename methods. `Open` and `Create` return `nodefs.NewLoopbackFile` handles.

## Control Flow
Construction canonicalizes the root to an absolute path. Reads and metadata requests join the FUSE-relative name to `Root`; root getattr follows symlinks with `Stat`, while non-root entries use `Lstat`. Directory reads batch `Readdir(500)` into `fuse.DirEntry` values.

## State And Persistence
Persistent state is only the absolute backing `Root`; all file data and metadata persist in the underlying filesystem. `Access` computes permissions from fetched attributes and caller credentials rather than relying on kernel `access`.

## Dependencies And Integration Points
Depends on `os`, `syscall`, `filepath`, `nodefs`, `fuse`, and `internal.HasAccess`. It is commonly wrapped by `PathNodeFs` and `NewLockingFileSystem` in tests.

## Risks And Edge Cases
Path joining intentionally exposes the backing tree semantics; symlink behavior is host-filesystem behavior. `Open` strips `O_APPEND` because kernel offsets are expected to handle append, and `Create` returns a loopback file even when `os.OpenFile` returns an error, so callers must trust the status.

## Test Signals
Exercised by loopback integration tests covering read/write-through, hard links, POSIX operations, statfs parity, symlink roots, access checks, large IO, and utimens behavior.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/loopback.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/loopback_darwin.go -->
# `sources/user-network-fs/go-fuse/fuse/pathfs/loopback_darwin.go`

## Purpose
Implements Darwin-specific path-based `loopbackFileSystem.Utimens` using `syscall.Utimes` because older macOS lacks `utimensat`/`UTIME_OMIT`.

## Important APIs, Types, And Functions
`Utimens` and `utimens.Fill` are the key APIs; it fetches attrs when either timestamp is nil, preserving the missing timestamp before calling host `Utimes`.

## Control Flow
`Utimens` and `utimens.Fill` are the key APIs; it fetches attrs when either timestamp is nil, preserving the missing timestamp before calling host `Utimes`.

## State And Persistence
The file persists only host filesystem timestamps and depends on `fuse.Attr`, `syscall`, and internal `utimens`. Risk is symlink behavior: `Utimes` follows paths, unlike Linux no-follow `utimensat`. The shared loopback utimens tests cover nil-atime/nil-mtime preservation.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
The file persists only host filesystem timestamps and depends on `fuse.Attr`, `syscall`, and internal `utimens`. Risk is symlink behavior: `Utimes` follows paths, unlike Linux no-follow `utimensat`. The shared loopback utimens tests cover nil-atime/nil-mtime preservation.

## Test Signals
The file persists only host filesystem timestamps and depends on `fuse.Attr`, `syscall`, and internal `utimens`. Risk is symlink behavior: `Utimes` follows paths, unlike Linux no-follow `utimensat`. The shared loopback utimens tests cover nil-atime/nil-mtime preservation.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/loopback_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/loopback_linux.go -->
# `sources/user-network-fs/go-fuse/fuse/pathfs/loopback_linux.go`

## Purpose
Adds Linux xattr and timestamp support for the loopback pathfs implementation.

## Important APIs, Types, And Functions
Exports loopback methods `ListXAttr`, `GetXAttr`, `SetXAttr`, `RemoveXAttr`, `String`, and `Utimens`; `Utimens` builds two `Timespec` values and calls `sysUtimensat` with `_AT_SYMLINK_NOFOLLOW`.

## Control Flow
Exports loopback methods `ListXAttr`, `GetXAttr`, `SetXAttr`, `RemoveXAttr`, `String`, and `Utimens`; `Utimens` builds two `Timespec` values and calls `sysUtimensat` with `_AT_SYMLINK_NOFOLLOW`.

## State And Persistence
State lives in the backing filesystem xattr/timestamp metadata. Dependencies are Linux `syscall` xattr calls and the local xattr/list helpers. Risks include ERANGE retry sizing and Linux-only no-follow timestamp semantics. Covered by pathfs xattr and utimens tests.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State lives in the backing filesystem xattr/timestamp metadata. Dependencies are Linux `syscall` xattr calls and the local xattr/list helpers. Risks include ERANGE retry sizing and Linux-only no-follow timestamp semantics. Covered by pathfs xattr and utimens tests.

## Test Signals
State lives in the backing filesystem xattr/timestamp metadata. Dependencies are Linux `syscall` xattr calls and the local xattr/list helpers. Risks include ERANGE retry sizing and Linux-only no-follow timestamp semantics. Covered by pathfs xattr and utimens tests.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/loopback_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/loopback_test.go -->
# `sources/user-network-fs/go-fuse/fuse/pathfs/loopback_test.go`

## Purpose
Contains only package-level scaffolding for pathfs loopback tests.

## Important APIs, Types, And Functions
There are no active test functions or exported APIs in this file; it exists to keep package/test organization stable.

## Control Flow
There are no active test functions or exported APIs in this file; it exists to keep package/test organization stable.

## State And Persistence
No runtime state, dependencies, or persistence behavior. Risk is negligible except that future tests added here should coordinate with existing loopback integration coverage in `fuse/test/loopback_test.go`.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No runtime state, dependencies, or persistence behavior. Risk is negligible except that future tests added here should coordinate with existing loopback integration coverage in `fuse/test/loopback_test.go`.

## Test Signals
No runtime state, dependencies, or persistence behavior. Risk is negligible except that future tests added here should coordinate with existing loopback integration coverage in `fuse/test/loopback_test.go`.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/loopback_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/owner_test.go -->
# `sources/user-network-fs/go-fuse/fuse/pathfs/owner_test.go`

## Purpose
Tests owner override behavior when pathfs attributes flow through nodefs mount options.

## Important APIs, Types, And Functions
Defines `ownerFs`, `_RANDOM_OWNER`, `setupOwnerTest`, and tests `TestOwnerDefault`, `TestOwnerRoot`, `TestOwnerOverride`.

## Control Flow
Defines `ownerFs`, `_RANDOM_OWNER`, `setupOwnerTest`, and tests `TestOwnerDefault`, `TestOwnerRoot`, `TestOwnerOverride`.

## State And Persistence
The fake fs returns random uid/gid for file attrs; nodefs options either replace ownership with current user, preserve fs owner, or force explicit owner. Risks are platform uid/gid stat differences and root/current-user behavior. Signals validate owner mapping policy.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
The fake fs returns random uid/gid for file attrs; nodefs options either replace ownership with current user, preserve fs owner, or force explicit owner. Risks are platform uid/gid stat differences and root/current-user behavior. Signals validate owner mapping policy.

## Test Signals
The fake fs returns random uid/gid for file attrs; nodefs options either replace ownership with current user, preserve fs owner, or force explicit owner. Risks are platform uid/gid stat differences and root/current-user behavior. Signals validate owner mapping policy.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/owner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/pathfs.go -->
# `sources/user-network-fs/go-fuse/fuse/pathfs/pathfs.go`

## Purpose
Bridges the path-oriented `pathfs.FileSystem` API to `nodefs.Node`/inode operations. It keeps enough inode tree state to translate kernel inode callbacks back into paths and to optionally coalesce hard links by client inode number.

## Important APIs, Types, And Functions
Defines `PathNodeFs`, `pathInode`, `refCountedInode`, `NewPathNodeFs`, `Mount`, `Unmount`, `Node`, `LookupNode`, `Path`, `Notify`, `FileNotify`, `EntryNotify`, `AllFiles`, and the full node operation surface (`Lookup`, `Open`, `Create`, `GetAttr`, `Chmod`, `Utimens`, locking, xattrs).

## Control Flow
Mounting stores the connector and invokes the wrapped filesystem. Most operations call `GetPath()` then delegate to the wrapped `FileSystem`; successful create/mkdir/symlink/link/lookup operations add child inodes. `Lookup` removes stale known children when type or existence changed, then either finds an existing client inode or creates a new child.

## State And Persistence
State is in the node tree plus `clientInodeMap`, guarded by `pathLock`. `clientInode` reference counts model hard-link aliases and are cleared by forget/removal paths. Deleted open files get synthetic `.deleted.<inode>` paths so file-handle fallbacks can still work where possible.

## Dependencies And Integration Points
Integrates tightly with `fuse/nodefs`, `fuse` request types, and the wrapped `pathfs.FileSystem`. It is the adapter used by loopback, prefix, readonly, locking, and many tests.

## Risks And Edge Cases
Correctness depends on lock discipline around client inode references and on fallback ordering from file-handle methods to path methods. Rename/remove races can leave temporary stale children, and hard-link support is disabled unless `ClientInodes` is set.

## Test Signals
Covered by loopback hard-link tests, lookup-known-children cache tests, mount/unmount tests, fsetattr tests, cache invalidation tests, and race-oriented getattr tests.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/pathfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/prefixfs.go -->
# `sources/user-network-fs/go-fuse/fuse/pathfs/prefixfs.go`

## Purpose
Implements `NewPrefixFileSystem`, a decorator that prepends a fixed path prefix to all pathfs operations.

## Important APIs, Types, And Functions
`prefixFileSystem` forwards every `FileSystem` method after `filepath.Join(Prefix, name)`, including xattrs, create/open, metadata, links, statfs, mount hooks, and debug toggling.

## Control Flow
`prefixFileSystem` forwards every `FileSystem` method after `filepath.Join(Prefix, name)`, including xattrs, create/open, metadata, links, statfs, mount hooks, and debug toggling.

## State And Persistence
It stores only the wrapped filesystem and prefix. Integration point is composition: it can expose a subtree without changing the underlying fs. Risks are filepath clean/join semantics and ensuring every method is forwarded consistently; no direct tests in this subset.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
It stores only the wrapped filesystem and prefix. Integration point is composition: it can expose a subtree without changing the underlying fs. Risks are filepath clean/join semantics and ensuring every method is forwarded consistently; no direct tests in this subset.

## Test Signals
It stores only the wrapped filesystem and prefix. Integration point is composition: it can expose a subtree without changing the underlying fs. Risks are filepath clean/join semantics and ensuring every method is forwarded consistently; no direct tests in this subset.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/prefixfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/readonlyfs.go -->
# `sources/user-network-fs/go-fuse/fuse/pathfs/readonlyfs.go`

## Purpose
Implements `NewReadonlyFileSystem`, a decorator that blocks mutating pathfs operations while allowing reads and metadata lookup.

## Important APIs, Types, And Functions
`readonlyFileSystem` forwards read-only methods (`GetAttr`, `Readlink`, `OpenDir`, read-only `Open`, xattr get/list, statfs) and returns `EROFS` for mutation paths.

## Control Flow
`readonlyFileSystem` forwards read-only methods (`GetAttr`, `Readlink`, `OpenDir`, read-only `Open`, xattr get/list, statfs) and returns `EROFS` for mutation paths.

## State And Persistence
State is just the wrapped filesystem. `Open` checks write flags and rejects writes before delegating. Risks include missing a mutating method or misclassifying flags. It integrates as a simple safety wrapper above any pathfs implementation.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is just the wrapped filesystem. `Open` checks write flags and rejects writes before delegating. Risks include missing a mutating method or misclassifying flags. It integrates as a simple safety wrapper above any pathfs implementation.

## Test Signals
State is just the wrapped filesystem. `Open` checks write flags and rejects writes before delegating. Risks include missing a mutating method or misclassifying flags. It integrates as a simple safety wrapper above any pathfs implementation.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/readonlyfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/syscall_linux.go -->
# `sources/user-network-fs/go-fuse/fuse/pathfs/syscall_linux.go`

## Purpose
Provides Linux syscall helpers for pathfs xattr listing/getting and `utimensat` with no-follow semantics.

## Important APIs, Types, And Functions
Key helpers are `getXAttr`, `listXAttr`, `_AT_SYMLINK_NOFOLLOW`, and `sysUtimensat`.

## Control Flow
Key helpers are `getXAttr`, `listXAttr`, `_AT_SYMLINK_NOFOLLOW`, and `sysUtimensat`.

## State And Persistence
The helpers allocate buffers after probing sizes and parse NUL-separated xattr names. Risks include empty xattr list handling, direct syscall ABI drift, and `dest[0]` assumptions for non-empty buffers. `syscall_test.go` validates `sysUtimensat`.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
The helpers allocate buffers after probing sizes and parse NUL-separated xattr names. Risks include empty xattr list handling, direct syscall ABI drift, and `dest[0]` assumptions for non-empty buffers. `syscall_test.go` validates `sysUtimensat`.

## Test Signals
The helpers allocate buffers after probing sizes and parse NUL-separated xattr names. Risks include empty xattr list handling, direct syscall ABI drift, and `dest[0]` assumptions for non-empty buffers. `syscall_test.go` validates `sysUtimensat`.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/syscall_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/syscall_test.go -->
# `sources/user-network-fs/go-fuse/fuse/pathfs/syscall_test.go`

## Purpose
Tests Linux `sysUtimensat` behavior through an actual temporary file.

## Important APIs, Types, And Functions
`TestSysUtimensat` creates a file, calls `sysUtimensat`, stats it, and compares timestamp seconds.

## Control Flow
`TestSysUtimensat` creates a file, calls `sysUtimensat`, stats it, and compares timestamp seconds.

## State And Persistence
Persistent state is temporary filesystem metadata only. The test signal confirms pathfs can update times without requiring file handles and is sensitive to filesystem timestamp precision/permissions.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Persistent state is temporary filesystem metadata only. The test signal confirms pathfs can update times without requiring file handles and is sensitive to filesystem timestamp precision/permissions.

## Test Signals
Persistent state is temporary filesystem metadata only. The test signal confirms pathfs can update times without requiring file handles and is sensitive to filesystem timestamp precision/permissions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/syscall_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/verbose_test.go -->
# `sources/user-network-fs/go-fuse/fuse/pathfs/verbose_test.go`

## Purpose
Provides a package-local `VerboseTest` helper for pathfs tests.

## Important APIs, Types, And Functions
`VerboseTest` reads the `test.v` flag and returns true when tests run verbose.

## Control Flow
`VerboseTest` reads the `test.v` flag and returns true when tests run verbose.

## State And Persistence
No persistent state; it depends on `flag`. It gates debug mount logging in pathfs xattr tests. Risk is flag availability outside `go test`, where it returns false.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistent state; it depends on `flag`. It gates debug mount logging in pathfs xattr tests. Risk is flag availability outside `go test`, where it returns false.

## Test Signals
No persistent state; it depends on `flag`. It gates debug mount logging in pathfs xattr tests. Risk is flag availability outside `go test`, where it returns false.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/verbose_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/xattr_test.go -->
# `sources/user-network-fs/go-fuse/fuse/pathfs/xattr_test.go`

## Purpose
Linux pathfs xattr integration tests using a synthetic filesystem with in-memory xattr maps.

## Important APIs, Types, And Functions
Defines `XAttrTestFs`, `NewXAttrFs`, xattr method overrides, `xattrTestCase`, and tests for empty attrs, missing attrs, reading, writing, listing, and removing xattrs.

## Control Flow
Defines `XAttrTestFs`, `NewXAttrFs`, xattr method overrides, `xattrTestCase`, and tests for empty attrs, missing attrs, reading, writing, listing, and removing xattrs.

## State And Persistence
State is an in-memory `map[string][]byte`, copied on set to avoid aliasing. It integrates through pathfs/nodefs mount and Linux helper calls. Risks include unordered list results and Linux-only xattr namespace behavior.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is an in-memory `map[string][]byte`, copied on set to avoid aliasing. It integrates through pathfs/nodefs mount and Linux helper calls. Risks include unordered list results and Linux-only xattr namespace behavior.

## Test Signals
State is an in-memory `map[string][]byte`, copied on set to avoid aliasing. It integrates through pathfs/nodefs mount and Linux helper calls. Risks include unordered list results and Linux-only xattr namespace behavior.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/pathfs/xattr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/poll.go -->
# `sources/user-network-fs/go-fuse/fuse/poll.go`

## Purpose
Implements the Go runtime epoll avoidance hack for FUSE `_OP_POLL`.

## Important APIs, Types, And Functions
Defines `pollHackName`, `pollHackInode`, and `doPollHackLookup` handling LOOKUP/OPEN/GETATTR/SETATTR/GETXATTR/POLL/ACCESS/FLUSH/RELEASE for the synthetic file.

## Control Flow
Defines `pollHackName`, `pollHackInode`, and `doPollHackLookup` handling LOOKUP/OPEN/GETATTR/SETATTR/GETXATTR/POLL/ACCESS/FLUSH/RELEASE for the synthetic file.

## State And Persistence
No persisted state; it synthesizes a fake inode and returns ENOSYS for POLL so the kernel stops polling. Integrated from `protocolServer.handleRequest` and `Server.WaitMount`. Risk is accidentally disabling unrelated kernel features with ENOSYS, so unsupported opcodes return ERANGE.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persisted state; it synthesizes a fake inode and returns ENOSYS for POLL so the kernel stops polling. Integrated from `protocolServer.handleRequest` and `Server.WaitMount`. Risk is accidentally disabling unrelated kernel features with ENOSYS, so unsupported opcodes return ERANGE.

## Test Signals
No persisted state; it synthesizes a fake inode and returns ENOSYS for POLL so the kernel stops polling. Integrated from `protocolServer.handleRequest` and `Server.WaitMount`. Risk is accidentally disabling unrelated kernel features with ENOSYS, so unsupported opcodes return ERANGE.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/poll.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/poll_darwin.go -->
# `sources/user-network-fs/go-fuse/fuse/poll_darwin.go`

## Purpose
Darwin implementation of `pollHack` using a direct `SYS_POLL` wrapper.

## Important APIs, Types, And Functions
Defines `pollFd`, `sysPoll`, and `pollHack`; it opens the synthetic poll file, tolerates sandbox EPERM, and performs zero-timeout poll.

## Control Flow
Defines `pollFd`, `sysPoll`, and `pollHack`; it opens the synthetic poll file, tolerates sandbox EPERM, and performs zero-timeout poll.

## State And Persistence
State is just a temporary fd. Dependencies are `syscall`, `unsafe`, and path joining. Risk is Darwin syscall ABI/sandbox behavior; integration is via `WaitMount`.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is just a temporary fd. Dependencies are `syscall`, `unsafe`, and path joining. Risk is Darwin syscall ABI/sandbox behavior; integration is via `WaitMount`.

## Test Signals
State is just a temporary fd. Dependencies are `syscall`, `unsafe`, and path joining. Risk is Darwin syscall ABI/sandbox behavior; integration is via `WaitMount`.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/poll_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/poll_unix.go -->
# `sources/user-network-fs/go-fuse/fuse/poll_unix.go`

## Purpose
Non-Darwin poll-hack implementation using `golang.org/x/sys/unix.Poll`.

## Important APIs, Types, And Functions
`pollHack` opens `.go-fuse-epoll-hack`, polls for read/priority/write events with timeout 0, and closes the fd.

## Control Flow
`pollHack` opens `.go-fuse-epoll-hack`, polls for read/priority/write events with timeout 0, and closes the fd.

## State And Persistence
No persistent state. Dependencies are `syscall` and `unix`. Risk is failure to open the mountpoint during startup; `WaitMount` propagates errors.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistent state. Dependencies are `syscall` and `unix`. Risk is failure to open the mountpoint during startup; `WaitMount` propagates errors.

## Test Signals
No persistent state. Dependencies are `syscall` and `unix`. Risk is failure to open the mountpoint during startup; `WaitMount` propagates errors.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/poll_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/print.go -->
# `sources/user-network-fs/go-fuse/fuse/print.go`

## Purpose
Pretty-printer for FUSE protocol structs and flags used by debug logging.

## Important APIs, Types, And Functions
Defines flag-name maps, `flagNames`, `flagString`, `Print`, and many `string()` methods for request/response structs, attrs, locks, xattrs, ioctl, notify, and init messages.

## Control Flow
Defines flag-name maps, `flagNames`, `flagString`, `Print`, and many `string()` methods for request/response structs, attrs, locks, xattrs, ioctl, notify, and init messages.

## State And Persistence
State is global flag-name tables extended by platform init files. It integrates with `request.InputDebug`/`OutputDebug` and mount debug logs. Risks are overlapping flags, nondeterministic output, and missing platform flag names; tests assert stable ordering/defaults.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is global flag-name tables extended by platform init files. It integrates with `request.InputDebug`/`OutputDebug` and mount debug logs. Risks are overlapping flags, nondeterministic output, and missing platform flag names; tests assert stable ordering/defaults.

## Test Signals
State is global flag-name tables extended by platform init files. It integrates with `request.InputDebug`/`OutputDebug` and mount debug logs. Risks are overlapping flags, nondeterministic output, and missing platform flag names; tests assert stable ordering/defaults.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/print.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/print_darwin.go -->
# `sources/user-network-fs/go-fuse/fuse/print_darwin.go`

## Purpose
Darwin-specific debug string formatting and capability names.

## Important APIs, Types, And Functions
`init` registers macFUSE capability bits; `CreateIn`, `GetAttrIn`, `MknodIn`, `ReadIn`, and `WriteIn` string methods match Darwin request layouts.

## Control Flow
`init` registers macFUSE capability bits; `CreateIn`, `GetAttrIn`, `MknodIn`, `ReadIn`, and `WriteIn` string methods match Darwin request layouts.

## State And Persistence
No persistence; modifies global printer tables at init. Risk is conflict with Linux bit meanings and Darwin-specific struct fields. Covered indirectly by print tests and debug logs on Darwin.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistence; modifies global printer tables at init. Risk is conflict with Linux bit meanings and Darwin-specific struct fields. Covered indirectly by print tests and debug logs on Darwin.

## Test Signals
No persistence; modifies global printer tables at init. Risk is conflict with Linux bit meanings and Darwin-specific struct fields. Covered indirectly by print tests and debug logs on Darwin.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/print_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/print_freebsd.go -->
# `sources/user-network-fs/go-fuse/fuse/print_freebsd.go`

## Purpose
FreeBSD-specific printer initialization.

## Important APIs, Types, And Functions
`init` registers `CAP_NO_OPENDIR_SUPPORT` so init capability debug output can name it.

## Control Flow
`init` registers `CAP_NO_OPENDIR_SUPPORT` so init capability debug output can name it.

## State And Persistence
No state beyond global flag table mutation. Risk is limited to debug readability; functional protocol behavior is elsewhere.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No state beyond global flag table mutation. Risk is limited to debug readability; functional protocol behavior is elsewhere.

## Test Signals
No state beyond global flag table mutation. Risk is limited to debug readability; functional protocol behavior is elsewhere.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/print_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/print_linux.go -->
# `sources/user-network-fs/go-fuse/fuse/print_linux.go`

## Purpose
Linux-specific debug string formatting for open/statx/capability flags.

## Important APIs, Types, And Functions
Registers Linux-only open and init flags, defines `Statx.string`, and `StatxIn.string`.

## Control Flow
Registers Linux-only open and init flags, defines `Statx.string`, and `StatxIn.string`.

## State And Persistence
Global printer tables are mutated at init. Dependencies include `runtime`, `syscall`, and `x/sys/unix`. Risks include architecture-specific flag aliases like `O_LARGEFILE`/`O_DIRECT` and keeping statx field names current.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Global printer tables are mutated at init. Dependencies include `runtime`, `syscall`, and `x/sys/unix`. Risks include architecture-specific flag aliases like `O_LARGEFILE`/`O_DIRECT` and keeping statx field names current.

## Test Signals
Global printer tables are mutated at init. Dependencies include `runtime`, `syscall`, and `x/sys/unix`. Risks include architecture-specific flag aliases like `O_LARGEFILE`/`O_DIRECT` and keeping statx field names current.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/print_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/print_test.go -->
# `sources/user-network-fs/go-fuse/fuse/print_test.go`

## Purpose
Unit tests for flag formatting determinism and overlap detection.

## Important APIs, Types, And Functions
Sets `isTest`, then tests ordering, default rendering, unknown bits, and multi-bit flag behavior in `flagString`.

## Control Flow
Sets `isTest`, then tests ordering, default rendering, unknown bits, and multi-bit flag behavior in `flagString`.

## State And Persistence
No filesystem state. Test signal protects debug output stability and catches flag table overlaps during init.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No filesystem state. Test signal protects debug output stability and catches flag table overlaps during init.

## Test Signals
No filesystem state. Test signal protects debug output stability and catches flag table overlaps during init.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/print_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/print_unix.go -->
# `sources/user-network-fs/go-fuse/fuse/print_unix.go`

## Purpose
Non-Darwin printer methods for common Unix request layouts.

## Important APIs, Types, And Functions
Defines string methods for `CreateIn`, `GetAttrIn`, `MknodIn`, `ReadIn`, and `WriteIn`, including umask, lock owner, and open flags.

## Control Flow
Defines string methods for `CreateIn`, `GetAttrIn`, `MknodIn`, `ReadIn`, and `WriteIn`, including umask, lock owner, and open flags.

## State And Persistence
No persistence; integrates with debug logging. Risk is stale formatting if Linux/FreeBSD request structs diverge.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistence; integrates with debug logging. Risk is stale formatting if Linux/FreeBSD request structs diverge.

## Test Signals
No persistence; integrates with debug logging. Risk is stale formatting if Linux/FreeBSD request structs diverge.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/print_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/protocol-server.go -->
# `sources/user-network-fs/go-fuse/fuse/protocol-server.go`

## Purpose
Provides an in-process protocol dispatcher from raw FUSE request buffers to a `RawFileSystem`, plus an experimental `ProtocolServer` for virtiofs-style IOV request handling without a mounted `/dev/fuse` fd.

## Important APIs, Types, And Functions
Defines `protocolServer`, `ProtocolServer`, `NewProtocolServer`, `HandleRequest`, interrupt tracking methods, `iovLen`, and `iovLens`.

## Control Flow
`handleRequest` marks requests inflight, logs input, handles the poll hack, rejects missing handlers, runs the opcode handler under panic recovery, suppresses eligible replies, and serializes output. `HandleRequest` flattens header/control IOVs, validates output IOV shape, dispatches, and returns the exact written descriptor length.

## State And Persistence
Tracks inflight requests under `interruptMu`, a connection-dead flag for cancellation, latency recorder, kernel settings, mount options, and notify-retrieve wait table.

## Dependencies And Integration Points
Uses operation handlers from the raw protocol layer, `request` parsing/serialization, and `MountOptions` panic/debug behavior. The public wrapper forces `DisableSplice` because in-process dispatch cannot splice to a kernel fd.

## Risks And Edge Cases
IOV shape validation must be strict to avoid corrupting guest/device buffers. Interrupt cancellation is linear over inflight requests and rare by design. Panic handling relies on user-supplied handler returning a nonzero status.

## Test Signals
`protocol-server_test.go` feeds a GETXATTR-like IOV request and verifies header length/status serialization against the default raw filesystem.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/protocol-server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/protocol-server_test.go -->
# `sources/user-network-fs/go-fuse/fuse/protocol-server_test.go`

## Purpose
Tests the experimental `ProtocolServer.HandleRequest` IOV path.

## Important APIs, Types, And Functions
`TestProtocolServerParse` sends a split GETXATTR request, captures debug logs, and checks output header length and ENOSYS status.

## Control Flow
`TestProtocolServerParse` sends a split GETXATTR request, captures debug logs, and checks output header length and ENOSYS status.

## State And Persistence
State is local byte buffers. The signal protects IOV flattening, output descriptor length calculation, and negative status encoding.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is local byte buffers. The signal protects IOV flattening, output descriptor length calculation, and negative status encoding.

## Test Signals
State is local byte buffers. The signal protects IOV flattening, output descriptor length calculation, and negative status encoding.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/protocol-server_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/read.go -->
# `sources/user-network-fs/go-fuse/fuse/read.go`

## Purpose
Defines `ReadResult` implementations for direct byte data and fd-backed zero-copy reads.

## Important APIs, Types, And Functions
`ReadResultData`, `ReadResultFd`, `readResultData`, `readResultFd`, `seekableResult`, and `statefulResult` are the important APIs.

## Control Flow
`ReadResultData`, `ReadResultFd`, `readResultData`, `readResultFd`, `seekableResult`, and `statefulResult` are the important APIs.

## State And Persistence
Data may be returned as in-memory bytes or lazily via `syscall.Pread`. Integration point is server response writing/splice fallback. Risks include fd lifetime, short reads at EOF, and buffer sizing.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Data may be returned as in-memory bytes or lazily via `syscall.Pread`. Integration point is server response writing/splice fallback. Risks include fd lifetime, short reads at EOF, and buffer sizing.

## Test Signals
Data may be returned as in-memory bytes or lazily via `syscall.Pread`. Integration point is server response writing/splice fallback. Risks include fd lifetime, short reads at EOF, and buffer sizing.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/read.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/request.go -->
# `sources/user-network-fs/go-fuse/fuse/request.go`

## Purpose
Defines reusable request storage and low-level parsing/serialization helpers for raw FUSE messages.

## Important APIs, Types, And Functions
`request`, `requestAlloc`, `parseRequest`, `InputDebug`, `OutputDebug`, `setInput`, `filename`, `filenames`, `serializeHeader`, `outPayloadSize`, plus unsafe typed accessors.

## Control Flow
Reads start as byte slices, `parseRequest` chooses input/control sizes from opcode handlers and kernel settings, and output sizes are determined from handler metadata plus dynamic READ/READDIR/XATTR/IOCTL payload lengths. Serialization writes `OutHeader` with negative errno for normal replies.

## State And Persistence
`requestAlloc` carries pooled request state plus inline buffers for small input/output. `clear` resets per-request fields before reuse; read results may be direct payloads or deferred `ReadResult` objects.

## Dependencies And Integration Points
Depends on operation handler tables, protocol structs, debug printing, and unsafe layout equivalence between byte buffers and FUSE structs.

## Risks And Edge Cases
Unsafe parsing makes struct layout and short-read checks critical. INIT has version-dependent size trimming; GETXATTR/LISTXATTR switch between size query and data reply; response status sign handling must remain exact.

## Test Signals
Covered indirectly by protocol-server parsing tests, print/debug tests, and all server integration tests that exercise request lifecycles.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/request.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/request_darwin.go -->
# `sources/user-network-fs/go-fuse/fuse/request_darwin.go`

## Purpose
Darwin request layout specialization.

## Important APIs, Types, And Functions
Defines Darwin-specific request struct aliases/fields where macFUSE differs from generic Unix layouts.

## Control Flow
Defines Darwin-specific request struct aliases/fields where macFUSE differs from generic Unix layouts.

## State And Persistence
State is protocol layout only; risk is wire ABI mismatch with macFUSE. Integrated through shared `parseRequest` and platform build tags.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is protocol layout only; risk is wire ABI mismatch with macFUSE. Integrated through shared `parseRequest` and platform build tags.

## Test Signals
State is protocol layout only; risk is wire ABI mismatch with macFUSE. Integrated through shared `parseRequest` and platform build tags.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/request_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/request_freebsd.go -->
# `sources/user-network-fs/go-fuse/fuse/request_freebsd.go`

## Purpose
FreeBSD request layout specialization.

## Important APIs, Types, And Functions
Provides FreeBSD-specific request type definitions/aliases for the shared parser.

## Control Flow
Provides FreeBSD-specific request type definitions/aliases for the shared parser.

## State And Persistence
No runtime state. Risk is FreeBSD FUSE kernel header drift; integration is compile-time via build tags.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No runtime state. Risk is FreeBSD FUSE kernel header drift; integration is compile-time via build tags.

## Test Signals
No runtime state. Risk is FreeBSD FUSE kernel header drift; integration is compile-time via build tags.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/request_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/request_linux.go -->
# `sources/user-network-fs/go-fuse/fuse/request_linux.go`

## Purpose
Linux request layout specialization.

## Important APIs, Types, And Functions
Provides Linux-specific request type definitions/aliases consumed by `parseRequest` and operation handlers.

## Control Flow
Provides Linux-specific request type definitions/aliases consumed by `parseRequest` and operation handlers.

## State And Persistence
No persistence. Risk is kernel protocol additions changing struct sizes; tests exercise Linux parsing through mounted integration and protocol server tests.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistence. Risk is kernel protocol additions changing struct sizes; tests exercise Linux parsing through mounted integration and protocol server tests.

## Test Signals
No persistence. Risk is kernel protocol additions changing struct sizes; tests exercise Linux parsing through mounted integration and protocol server tests.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/request_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/server.go -->
# `sources/user-network-fs/go-fuse/fuse/server.go`

## Purpose
Implements the main FUSE device server: mount setup, INIT negotiation, request reader concurrency, request memory accounting, dispatch into `protocolServer`, response writes, notifications, cache retrieval, unmount, and wait semantics.

## Important APIs, Types, And Functions
Exports `Server`, `NewServer`, `Serve`, `Wait`, `Unmount`, `WaitMount`, `KernelSettings`, `RecordLatencies`, notification methods, `requestAccountingSizes`, and capability helpers on `InitIn`.

## Control Flow
`NewServer` normalizes options, mounts, reads and handles INIT synchronously, initializes the filesystem, then arms the serve loop. `readRequest` reserves request bytes, reads from `/dev/fuse`, parses headers, and may spawn more readers. `handleRequest` parses typed buffers, dispatches, serializes, and writes unless reply is suppressed.

## State And Persistence
Holds mount fd/path, reader counts, inflight byte accounting, buffer/request pools, kernel settings, notification retrieve table, and wait groups. Unmount closes the device after loops exit and wakes pending cache-retrieve waiters with `ENODEV`.

## Dependencies And Integration Points
Depends on OS mount/unmount helpers, `writev`, `pollHack`, splice support, raw FUSE protocol structs, and `RawFileSystem` handlers.

## Risks And Edge Cases
Concurrency and resource accounting are central risks: readers must be refilled without exceeding `MaxInflightRequestBytes`; writes must not race close; notification retrieval must not leak waiters. INIT/version sizing and errno polarity are protocol-sensitive.

## Test Signals
`server_linux_test.go`, cache-control tests, notify tests, mount tests, and broad loopback integration exercise reader liveness, request limits, notification paths, and unmount behavior.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/server_linux.go -->
# `sources/user-network-fs/go-fuse/fuse/server_linux.go`

## Purpose
Linux server response writer and splice policy.

## Important APIs, Types, And Functions
Defines `useSingleReader=false` and `Server.write`; writes header-only replies with writev, optionally splices fd-backed reads, otherwise materializes bytes and reserializes lengths.

## Control Flow
Defines `useSingleReader=false` and `Server.write`; writes header-only replies with writev, optionally splices fd-backed reads, otherwise materializes bytes and reserializes lengths.

## State And Persistence
State touched is request read-result ownership and mount fd writes. Dependencies include `writev`, splice helpers, and `ReadResult`. Risks are splice short-read handling and ensuring `Done` is called.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State touched is request read-result ownership and mount fd writes. Dependencies include `writev`, splice helpers, and `ReadResult`. Risks are splice short-read handling and ensuring `Done` is called.

## Test Signals
State touched is request read-result ownership and mount fd writes. Dependencies include `writev`, splice helpers, and `ReadResult`. Risks are splice short-read handling and ensuring `Done` is called.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/server_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/server_linux_test.go -->
# `sources/user-network-fs/go-fuse/fuse/server_linux_test.go`

## Purpose
Tests `MaxInflightRequestBytes` on Linux with blocked direct writes.

## Important APIs, Types, And Functions
Defines `blockingWriteFS` and `TestMaxInflightRequestBytesLimitsLargeWritesAndKeepsReader` with helpers for writer entry/results and reader liveness.

## Control Flow
Defines `blockingWriteFS` and `TestMaxInflightRequestBytesLimitsLargeWritesAndKeepsReader` with helpers for writer entry/results and reader liveness.

## State And Persistence
State includes blocked write channels and server reader counters. The signal ensures large writes are throttled by request bytes without starving the request reader.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State includes blocked write channels and server reader counters. The signal ensures large writes are throttled by request bytes without starving the request reader.

## Test Signals
State includes blocked write channels and server reader counters. The signal ensures large writes are throttled by request bytes without starving the request reader.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/server_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/server_unix.go -->
# `sources/user-network-fs/go-fuse/fuse/server_unix.go`

## Purpose
Non-Linux server response writer.

## Important APIs, Types, And Functions
Defines `useSingleReader=true` and simple `Server.write` that materializes any `ReadResult` then writes header/data/payload with `writev`.

## Control Flow
Defines `useSingleReader=true` and simple `Server.write` that materializes any `ReadResult` then writes header/data/payload with `writev`.

## State And Persistence
No additional persistent state beyond request buffers. Risk is higher copy cost and correct `ReadResult.Done`/serialization on platforms without splice.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No additional persistent state beyond request buffers. Risk is higher copy cost and correct `ReadResult.Done`/serialization on platforms without splice.

## Test Signals
No additional persistent state beyond request buffers. Risk is higher copy cost and correct `ReadResult.Done`/serialization on platforms without splice.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/server_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/splice_darwin.go -->
# `sources/user-network-fs/go-fuse/fuse/splice_darwin.go`

## Purpose
Darwin splice stub.

## Important APIs, Types, And Functions
`setSplice` disables splice and `trySplice` returns fallback/unavailable behavior.

## Control Flow
`setSplice` disables splice and `trySplice` returns fallback/unavailable behavior.

## State And Persistence
No state. Integration keeps common server code compiling while forcing byte-copy reads on Darwin; risk is performance only.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No state. Integration keeps common server code compiling while forcing byte-copy reads on Darwin; risk is performance only.

## Test Signals
No state. Integration keeps common server code compiling while forcing byte-copy reads on Darwin; risk is performance only.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/splice_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/splice_freebsd.go -->
# `sources/user-network-fs/go-fuse/fuse/splice_freebsd.go`

## Purpose
FreeBSD splice stub.

## Important APIs, Types, And Functions
Provides no-op splice support matching unsupported platform behavior.

## Control Flow
Provides no-op splice support matching unsupported platform behavior.

## State And Persistence
No persistent state. It prevents Linux-only zero-copy assumptions from leaking to FreeBSD.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistent state. It prevents Linux-only zero-copy assumptions from leaking to FreeBSD.

## Test Signals
No persistent state. It prevents Linux-only zero-copy assumptions from leaking to FreeBSD.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/splice_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/splice_linux.go -->
# `sources/user-network-fs/go-fuse/fuse/splice_linux.go`

## Purpose
Linux zero-copy read path using pipe splice pairs.

## Important APIs, Types, And Functions
Defines `setSplice`, `trySplice`, `pipeReadResult`, and `ReadResultPipe`.

## Control Flow
Defines `setSplice`, `trySplice`, `pipeReadResult`, and `ReadResultPipe`.

## State And Persistence
Uses splice pipe pairs as transient state; short fd reads drain/rewrite headers and recurse through a pipe-backed result. Integrated by `server_linux.go`. Risks include pipe growth, fd lifetime, EOF short read length correction, and cleanup via `Done`.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Uses splice pipe pairs as transient state; short fd reads drain/rewrite headers and recurse through a pipe-backed result. Integrated by `server_linux.go`. Risks include pipe growth, fd lifetime, EOF short read length correction, and cleanup via `Done`.

## Test Signals
Uses splice pipe pairs as transient state; short fd reads drain/rewrite headers and recurse through a pipe-backed result. Integrated by `server_linux.go`. Risks include pipe growth, fd lifetime, EOF short read length correction, and cleanup via `Done`.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/splice_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/syscall_darwin.go -->
# `sources/user-network-fs/go-fuse/fuse/syscall_darwin.go`

## Purpose
Darwin xattr syscall wrappers for the fuse package.

## Important APIs, Types, And Functions
Implements `getxattr`, `GetXAttr`, `listxattr`, `ListXAttr`, `Setxattr`, and `Removexattr` via direct syscalls and C strings.

## Control Flow
Implements `getxattr`, `GetXAttr`, `listxattr`, `ListXAttr`, `Setxattr`, and `Removexattr` via direct syscalls and C strings.

## State And Persistence
State is host xattr metadata. Risks include zero-length buffers/data, Darwin syscall argument order, and parsing NUL-separated names. Integrated by raw/path xattr operations.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is host xattr metadata. Risks include zero-length buffers/data, Darwin syscall argument order, and parsing NUL-separated names. Integrated by raw/path xattr operations.

## Test Signals
State is host xattr metadata. Risks include zero-length buffers/data, Darwin syscall argument order, and parsing NUL-separated names. Integrated by raw/path xattr operations.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/syscall_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/syscall_linux.go -->
# `sources/user-network-fs/go-fuse/fuse/syscall_linux.go`

## Purpose
Linux `writev` wrapper.

## Important APIs, Types, And Functions
`writev` delegates to `unix.Writev` and returns byte count/error.

## Control Flow
`writev` delegates to `unix.Writev` and returns byte count/error.

## State And Persistence
No persistent state; it is the core response/notify write primitive on Linux. Risk is partial writes and errno propagation.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistent state; it is the core response/notify write primitive on Linux. Risk is partial writes and errno propagation.

## Test Signals
No persistent state; it is the core response/notify write primitive on Linux. Risk is partial writes and errno propagation.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/syscall_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/syscall_unix.go -->
# `sources/user-network-fs/go-fuse/fuse/syscall_unix.go`

## Purpose
Non-Linux `writev` wrapper using raw `SYS_WRITEV`.

## Important APIs, Types, And Functions
Defines `sys_writev` and `writev`; builds syscall iovecs from non-empty packet slices and retries EINTR.

## Control Flow
Defines `sys_writev` and `writev`; builds syscall iovecs from non-empty packet slices and retries EINTR.

## State And Persistence
No persistence. Risks include empty packet slice handling, iovec lifetime, and platform syscall differences.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistence. Risks include empty packet slice handling, iovec lifetime, and platform syscall differences.

## Test Signals
No persistence. Risks include empty packet slice handling, iovec lifetime, and platform syscall differences.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/syscall_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/cache_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/cache_test.go`

## Purpose
Integration tests for kernel data-cache control and nonseekable/read race behavior.

## Important APIs, Types, And Functions
Defines `cacheFs`, `setupCacheTest`, `TestFopenKeepCache`, `nonseekFs`, `TestNonseekable`, and `TestGetAttrRace`.

## Control Flow
Defines `cacheFs`, `setupCacheTest`, `TestFopenKeepCache`, `nonseekFs`, `TestNonseekable`, and `TestGetAttrRace`.

## State And Persistence
State uses temp backing/mount dirs and kernel cache TTLs. It validates `FOPEN_KEEP_CACHE`, explicit invalidation with `FileNotify`, nonseekable open flags, and concurrent create/stat behavior. Risks are kernel/version-dependent cache semantics and Darwin skip.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State uses temp backing/mount dirs and kernel cache TTLs. It validates `FOPEN_KEEP_CACHE`, explicit invalidation with `FileNotify`, nonseekable open flags, and concurrent create/stat behavior. Risks are kernel/version-dependent cache semantics and Darwin skip.

## Test Signals
State uses temp backing/mount dirs and kernel cache TTLs. It validates `FOPEN_KEEP_CACHE`, explicit invalidation with `FileNotify`, nonseekable open flags, and concurrent create/stat behavior. Risks are kernel/version-dependent cache semantics and Darwin skip.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/cachecontrol_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/cachecontrol_test.go`

## Purpose
Tests storing and retrieving kernel page cache through notify operations.

## Important APIs, Types, And Functions
Defines `DataNode` and `TestCacheControl`, then reads cached content, uses `InodeNotifyStoreCache`/`InodeRetrieveCache`, and validates byte results/status.

## Control Flow
Defines `DataNode` and `TestCacheControl`, then reads cached content, uses `InodeNotifyStoreCache`/`InodeRetrieveCache`, and validates byte results/status.

## State And Persistence
State is a mounted nodefs tree and kernel page cache. Integration covers notify-retrieve table and server notification writes. Risks are protocol-version support and kernel cache eviction behavior.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is a mounted nodefs tree and kernel page cache. Integration covers notify-retrieve table and server notification writes. Risks are protocol-version support and kernel cache eviction behavior.

## Test Signals
State is a mounted nodefs tree and kernel page cache. Integration covers notify-retrieve table and server notification writes. Risks are protocol-version support and kernel cache eviction behavior.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/cachecontrol_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/defaultnode_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/defaultnode_test.go`

## Purpose
Tests default node getattr behavior.

## Important APIs, Types, And Functions
`TestDefaultNodeGetAttr` mounts a default node and confirms stat behavior on the root/default implementation.

## Control Flow
`TestDefaultNodeGetAttr` mounts a default node and confirms stat behavior on the root/default implementation.

## State And Persistence
No persistent state beyond temp mount. Signal protects sane default node attributes and mount wiring.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistent state beyond temp mount. Signal protects sane default node attributes and mount wiring.

## Test Signals
No persistent state beyond temp mount. Signal protects sane default node attributes and mount wiring.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/defaultnode_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/defaultread_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/defaultread_test.go`

## Purpose
Tests default read behavior for nodes/files that do not implement custom read paths.

## Important APIs, Types, And Functions
`defaultReadTest` mounts a test filesystem; `TestDefaultRead` verifies expected read/status behavior.

## Control Flow
`defaultReadTest` mounts a test filesystem; `TestDefaultRead` verifies expected read/status behavior.

## State And Persistence
State is temp files/mounts only. It guards fallback read semantics and default ENOSYS-like behavior without crashes.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is temp files/mounts only. It guards fallback read semantics and default ENOSYS-like behavior without crashes.

## Test Signals
State is temp files/mounts only. It guards fallback read semantics and default ENOSYS-like behavior without crashes.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/defaultread_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/delete_linux_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/delete_linux_test.go`

## Purpose
Linux test for delete notifications.

## Important APIs, Types, And Functions
`TestDeleteNotify` mounts a filesystem, removes/renames entries, and checks kernel-visible delete notification behavior.

## Control Flow
`TestDeleteNotify` mounts a filesystem, removes/renames entries, and checks kernel-visible delete notification behavior.

## State And Persistence
State lives in temp mount and kernel dentry cache. Risk is Linux-only notification support and timing around cached directory entries.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State lives in temp mount and kernel dentry cache. Risk is Linux-only notification support and timing around cached directory entries.

## Test Signals
State lives in temp mount and kernel dentry cache. Risk is Linux-only notification support and timing around cached directory entries.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/delete_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/file_lock_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/file_lock_test.go`

## Purpose
Linux integration tests for flock/lock dispatch.

## Important APIs, Types, And Functions
Defines `TestFlockExclusive`, `lockingNode`, `TestFlockInvoked`, and `TestNoLockSupport`.

## Control Flow
Defines `TestFlockExclusive`, `lockingNode`, `TestFlockInvoked`, and `TestNoLockSupport`.

## State And Persistence
State includes OS advisory locks and invocation booleans guarded by mutex. It validates `EnableLocks`, file lock handlers, and VFS fallback when fs returns ENOSYS. Risks include external `flock` availability and platform lock semantics.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State includes OS advisory locks and invocation booleans guarded by mutex. It validates `EnableLocks`, file lock handlers, and VFS fallback when fs returns ENOSYS. Risks include external `flock` availability and platform lock semantics.

## Test Signals
State includes OS advisory locks and invocation booleans guarded by mutex. It validates `EnableLocks`, file lock handlers, and VFS fallback when fs returns ENOSYS. Risks include external `flock` availability and platform lock semantics.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/file_lock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/fsetattr_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/fsetattr_test.go`

## Purpose
Tests setattr operations that should prefer file-handle methods before path fallback.

## Important APIs, Types, And Functions
Defines `MutableDataFile`, `FSetAttrFs`, setup helpers, and `TestFSetAttr`.

## Control Flow
Defines `MutableDataFile`, `FSetAttrFs`, setup helpers, and `TestFSetAttr`.

## State And Persistence
State is mutable in-memory file data and attrs. It validates ftruncate, chmod, chown, utimens, fsync, and getattr paths through open files. Risks include nil file handles and kernel differences in passing fh for setattr.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is mutable in-memory file data and attrs. It validates ftruncate, chmod, chown, utimens, fsync, and getattr paths through open files. Risks include nil file handles and kernel differences in passing fh for setattr.

## Test Signals
State is mutable in-memory file data and attrs. It validates ftruncate, chmod, chown, utimens, fsync, and getattr paths through open files. Risks include nil file handles and kernel differences in passing fh for setattr.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/fsetattr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/loopback_darwin_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/loopback_darwin_test.go`

## Purpose
Darwin-specific loopback integration tests.

## Important APIs, Types, And Functions
Covers macOS-only loopback expectations such as timestamp or filesystem semantics that differ from Linux.

## Control Flow
Covers macOS-only loopback expectations such as timestamp or filesystem semantics that differ from Linux.

## State And Persistence
State is temp backing/mount dirs. Risks are macFUSE version behavior and Darwin timestamp/xattr differences.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is temp backing/mount dirs. Risks are macFUSE version behavior and Darwin timestamp/xattr differences.

## Test Signals
State is temp backing/mount dirs. Risks are macFUSE version behavior and Darwin timestamp/xattr differences.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/loopback_darwin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/loopback_linux_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/loopback_linux_test.go`

## Purpose
Linux-specific loopback tests for time, overlayfs, fallocate, and readdir inode details.

## Important APIs, Types, And Functions
Defines overlayfs flag setup plus tests `TestTouch`, `TestNegativeTime`, `TestUtimesNano`, `TestOverlayfs`, `TestFallocate`, `TestSpecialEntries`, and `TestReaddirInodes`.

## Control Flow
Defines overlayfs flag setup plus tests `TestTouch`, `TestNegativeTime`, `TestUtimesNano`, `TestOverlayfs`, `TestFallocate`, `TestSpecialEntries`, and `TestReaddirInodes`.

## State And Persistence
State uses temp loopback mounts and sometimes overlayfs. Signals validate nanosecond/negative timestamps, allocation, special directory entries, and inode reporting. Risks include kernel version and optional overlayfs flag.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State uses temp loopback mounts and sometimes overlayfs. Signals validate nanosecond/negative timestamps, allocation, special directory entries, and inode reporting. Risks include kernel version and optional overlayfs flag.

## Test Signals
State uses temp loopback mounts and sometimes overlayfs. Signals validate nanosecond/negative timestamps, allocation, special directory entries, and inode reporting. Risks include kernel version and optional overlayfs flag.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/loopback_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/loopback_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/loopback_test.go`

## Purpose
Primary loopback integration suite and shared `testCase` harness.

## Important APIs, Types, And Functions
Defines mounting helpers plus tests for open/read/write/remove/link/forget/POSIX operations/access/mknod/readdir rename/fsync/large IO/statfs/symlink root/double open/chgrp/known-child attrs/utimens.

## Control Flow
Defines mounting helpers plus tests for open/read/write/remove/link/forget/POSIX operations/access/mknod/readdir rename/fsync/large IO/statfs/symlink root/double open/chgrp/known-child attrs/utimens.

## State And Persistence
State is temp backing directory, mountpoint, pathfs connector, kernel cache TTLs, and client inode mappings. It is the strongest signal for pathfs-loopback behavior. Risks are kernel timing, root permissions, and FUSE mount availability.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is temp backing directory, mountpoint, pathfs connector, kernel cache TTLs, and client inode mappings. It is the strongest signal for pathfs-loopback behavior. Risks are kernel timing, root permissions, and FUSE mount availability.

## Test Signals
State is temp backing directory, mountpoint, pathfs connector, kernel cache TTLs, and client inode mappings. It is the strongest signal for pathfs-loopback behavior. Risks are kernel timing, root permissions, and FUSE mount availability.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/loopback_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/mount_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/mount_test.go`

## Purpose
Tests nested nodefs mounts under an existing FUSE mount.

## Important APIs, Types, And Functions
Covers mount-on-existing EBUSY, rename protection, readdir visibility, recursive mount access, unmount EBUSY with open files, default-node mounting, and fd liveness after GC.

## Control Flow
Covers mount-on-existing EBUSY, rename protection, readdir visibility, recursive mount access, unmount EBUSY with open files, default-node mounting, and fd liveness after GC.

## State And Persistence
State includes mounted child nodes and open file handles. Signals protect mount lifecycle, busy detection, tree integration, and finalizer-related fd stability.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State includes mounted child nodes and open file handles. Signals protect mount lifecycle, busy detection, tree integration, and finalizer-related fd stability.

## Test Signals
State includes mounted child nodes and open file handles. Signals protect mount lifecycle, busy detection, tree integration, and finalizer-related fd stability.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/nil_file_truncation_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/nil_file_truncation_test.go`

## Purpose
Regression test for truncate with nil file handles.

## Important APIs, Types, And Functions
Defines `truncatableFile` returning nil file from `Open`; `TestNilFileTruncation` mounts it and truncates without crashing.

## Control Flow
Defines `truncatableFile` returning nil file from `Open`; `TestNilFileTruncation` mounts it and truncates without crashing.

## State And Persistence
State is temp mount only. The risk addressed is server/pathnode code assuming non-nil file handles for setattr/truncate.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is temp mount only. The risk addressed is server/pathnode code assuming non-nil file handles for setattr/truncate.

## Test Signals
State is temp mount only. The risk addressed is server/pathnode code assuming non-nil file handles for setattr/truncate.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/nil_file_truncation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/node_parallel_lookup_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/node_parallel_lookup_test.go`

## Purpose
Tests parallel lookup behavior and request concurrency around node creation.

## Important APIs, Types, And Functions
Defines a lookup-counting/synchronizing node and `TestNodeParallelLookup`.

## Control Flow
Defines a lookup-counting/synchronizing node and `TestNodeParallelLookup`.

## State And Persistence
State includes goroutine synchronization and node child state. It validates that concurrent lookups do not duplicate or corrupt nodes. Risks are timing sensitivity under race detector/load.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State includes goroutine synchronization and node child state. It validates that concurrent lookups do not duplicate or corrupt nodes. Risks are timing sensitivity under race detector/load.

## Test Signals
State includes goroutine synchronization and node child state. It validates that concurrent lookups do not duplicate or corrupt nodes. Risks are timing sensitivity under race detector/load.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/node_parallel_lookup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/node_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/node_test.go`

## Purpose
Tests direct node update behavior.

## Important APIs, Types, And Functions
Includes `TestUpdateNode`, exercising node attribute/content update notifications or connector state refresh.

## Control Flow
Includes `TestUpdateNode`, exercising node attribute/content update notifications or connector state refresh.

## State And Persistence
State is a mounted node tree. Signal protects nodefs update propagation through the connector.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is a mounted node tree. Signal protects nodefs update propagation through the connector.

## Test Signals
State is a mounted node tree. Signal protects nodefs update propagation through the connector.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/node_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/nofile_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/nofile_test.go`

## Purpose
Tests filesystems/nodes with entries that do not maintain normal file handles.

## Important APIs, Types, And Functions
`TestNoFile` sets up a small fs and verifies open/read behavior when file implementations are absent or minimal.

## Control Flow
`TestNoFile` sets up a small fs and verifies open/read behavior when file implementations are absent or minimal.

## State And Persistence
State is temp mount and synthetic nodes. It guards default file fallback behavior and error handling for missing file handles.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is temp mount and synthetic nodes. It guards default file fallback behavior and error handling for missing file handles.

## Test Signals
State is temp mount and synthetic nodes. It guards default file fallback behavior and error handling for missing file handles.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/nofile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/notify_linux_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/notify_linux_test.go`

## Purpose
Linux tests for inode notification invalidation.

## Important APIs, Types, And Functions
Defines `NotifyTest` harness and `TestInodeNotify`.

## Control Flow
Defines `NotifyTest` harness and `TestInodeNotify`.

## State And Persistence
State is backing content plus kernel cache/attrs. It validates that `InodeNotify` invalidates cached data/metadata. Risks are protocol-version and cache timing.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is backing content plus kernel cache/attrs. It validates that `InodeNotify` invalidates cached data/metadata. Risks are protocol-version and cache timing.

## Test Signals
State is backing content plus kernel cache/attrs. It validates that `InodeNotify` invalidates cached data/metadata. Risks are protocol-version and cache timing.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/notify_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/test.go`

## Purpose
Package marker for the integration test package.

## Important APIs, Types, And Functions
No functions or runtime APIs are defined; it anchors package-level test organization.

## Control Flow
No functions or runtime APIs are defined; it anchors package-level test organization.

## State And Persistence
No state or dependencies beyond package declaration. Risk is none.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No state or dependencies beyond package declaration. Risk is none.

## Test Signals
No state or dependencies beyond package declaration. Risk is none.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/umask_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/umask_test.go`

## Purpose
Tests create/mkdir umask propagation through pathfs/nodefs.

## Important APIs, Types, And Functions
`TestUmask` mounts loopback variants and creates files/directories under known umask expectations.

## Control Flow
`TestUmask` mounts loopback variants and creates files/directories under known umask expectations.

## State And Persistence
State is temp backing/mount dirs and process umask. Signal protects mode calculation from kernel to filesystem. Risk is process-global umask interference.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is temp backing/mount dirs and process umask. Signal protects mode calculation from kernel to filesystem. Risk is process-global umask interference.

## Test Signals
State is temp backing/mount dirs and process umask. Signal protects mode calculation from kernel to filesystem. Risk is process-global umask interference.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/umask_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/xattr_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/xattr_test.go`

## Purpose
Tests default xattr behavior at nodefs/fuse level.

## Important APIs, Types, And Functions
`TestDefaultXAttr` and `TestEmptyXAttr` mount default or empty xattr nodes and assert expected errors/empty responses.

## Control Flow
`TestDefaultXAttr` and `TestEmptyXAttr` mount default or empty xattr nodes and assert expected errors/empty responses.

## State And Persistence
State is temp mount only. Signals protect xattr defaults, ENOATTR/ENODATA mapping, and empty-list handling.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is temp mount only. Signals protect xattr defaults, ENOATTR/ENODATA mapping, and empty-list handling.

## Test Signals
State is temp mount only. Signals protect xattr defaults, ENOATTR/ENODATA mapping, and empty-list handling.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/xattr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/xfs_test.go -->
# `sources/user-network-fs/go-fuse/fuse/test/xfs_test.go`

## Purpose
Linux/XFS-oriented readdir-plus seek test.

## Important APIs, Types, And Functions
`TestReaddirPlusSeek` reuses loopback harness to validate directory seek offsets under READDIRPLUS-like behavior.

## Control Flow
`TestReaddirPlusSeek` reuses loopback harness to validate directory seek offsets under READDIRPLUS-like behavior.

## State And Persistence
State is temp directory entries and kernel directory offsets. Risk is filesystem-specific offset semantics; signal protects xfs-style cookies.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is temp directory entries and kernel directory offsets. Risk is filesystem-specific offset semantics; signal protects xfs-style cookies.

## Test Signals
State is temp directory entries and kernel directory offsets. Risk is filesystem-specific offset semantics; signal protects xfs-style cookies.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/test/xfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/typeprint.go -->
# `sources/user-network-fs/go-fuse/fuse/typeprint.go`

## Purpose
Small helper file for type-print/debug support.

## Important APIs, Types, And Functions
Provides package-level functionality used by debug formatting or generated type string behavior.

## Control Flow
Provides package-level functionality used by debug formatting or generated type string behavior.

## State And Persistence
No runtime state beyond debug support. Risk is limited to diagnostics.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No runtime state beyond debug support. Risk is limited to diagnostics.

## Test Signals
No runtime state beyond debug support. Risk is limited to diagnostics.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/typeprint.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/types.go -->
# `sources/user-network-fs/go-fuse/fuse/types.go`

## Purpose
Declares the cross-platform FUSE wire structs, status constants, capability bits, request/response payload types, TTL helpers, caller identity, lock conversion helpers, and newer statx/copy-file-range structures.

## Important APIs, Types, And Functions
Important APIs include `Status`, errno constants, `SetAttrInCommon` getters, `InitIn/InitOut.Flags64`, `EntryOut`/`AttrOut` timeout helpers, `FileLock` conversion methods, `InHeader`, `OutHeader`, `ReadIn`, `WriteIn`, xattr, ioctl, notify, and statx structs.

## Control Flow
Handlers parse these structs from request buffers, fill output structs, then `request.serializeHeader` packages them for the kernel. Helper getters decode optional setattr fields based on `Valid` bits and produce Go `time.Time` values.

## State And Persistence
No active state is stored here; structs model kernel protocol state, TTLs, capabilities, inode ids, file handles, owners, and offsets.

## Dependencies And Integration Points
Depends on `syscall`, `time`, and `io`; platform files add OS-specific `Attr`, errno, and capability variants.

## Risks And Edge Cases
Wire compatibility is the main risk: field order, sizes, version-dependent flags, and errno aliases must match kernel/macFUSE/FreeBSD expectations. `SetAttrInCommon` uses current time for NOW flags, making tests time-sensitive.

## Test Signals
Type behavior is exercised by protocol parsing, print formatting tests, lock tests, setattr/fsetattr tests, and broad integration suites.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/types_darwin.go -->
# `sources/user-network-fs/go-fuse/fuse/types_darwin.go`

## Purpose
Darwin protocol type and capability definitions.

## Important APIs, Types, And Functions
Defines Darwin `Attr`, Darwin `SetAttrIn`, xattr request shapes, macFUSE capabilities, `GetxtimesOut`, `ExchangeIn`, `MonitorIn`, errno aliases, and Darwin `StatfsOut.FromStatfsT`/`InitOut.setFlags`.

## Control Flow
Defines Darwin `Attr`, Darwin `SetAttrIn`, xattr request shapes, macFUSE capabilities, `GetxtimesOut`, `ExchangeIn`, `MonitorIn`, errno aliases, and Darwin `StatfsOut.FromStatfsT`/`InitOut.setFlags`.

## State And Persistence
State is wire layout only. Risks are macFUSE ABI/capability bit differences and block-size adjustment in statfs conversion. Integrated by all Darwin builds.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is wire layout only. Risks are macFUSE ABI/capability bit differences and block-size adjustment in statfs conversion. Integrated by all Darwin builds.

## Test Signals
State is wire layout only. Risks are macFUSE ABI/capability bit differences and block-size adjustment in statfs conversion. Integrated by all Darwin builds.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/types_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/types_freebsd.go -->
# `sources/user-network-fs/go-fuse/fuse/types_freebsd.go`

## Purpose
FreeBSD errno, capability, statfs, and init flag definitions.

## Important APIs, Types, And Functions
Defines ENOATTR/ENODATA aliases, `CAP_NO_OPENDIR_SUPPORT`, unsupported capability zeros, `FromStatfsT`, and `setFlags`.

## Control Flow
Defines ENOATTR/ENODATA aliases, `CAP_NO_OPENDIR_SUPPORT`, unsupported capability zeros, `FromStatfsT`, and `setFlags`.

## State And Persistence
No active state. Risk is FreeBSD kernel header drift and correct signed/unsigned statfs field conversion.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No active state. Risk is FreeBSD kernel header drift and correct signed/unsigned statfs field conversion.

## Test Signals
No active state. Risk is FreeBSD kernel header drift and correct signed/unsigned statfs field conversion.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/types_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/types_linux.go -->
# `sources/user-network-fs/go-fuse/fuse/types_linux.go`

## Purpose
Linux errno, capability, statfs, and statx helpers.

## Important APIs, Types, And Functions
Defines ENODATA/ENOATTR/EREMOTEIO, Linux-only capability bits, `FromStatfsT`, `InitOut.setFlags`, and `SxTime.FromStatxTimestamp`.

## Control Flow
Defines ENODATA/ENOATTR/EREMOTEIO, Linux-only capability bits, `FromStatfsT`, `InitOut.setFlags`, and `SxTime.FromStatxTimestamp`.

## State And Persistence
No active state. Integrated by INIT negotiation, statfs replies, xattr errors, and statx output. Risk is keeping Linux capability bits in sync with kernel headers.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No active state. Integrated by INIT negotiation, statfs replies, xattr errors, and statx output. Risk is keeping Linux capability bits in sync with kernel headers.

## Test Signals
No active state. Integrated by INIT negotiation, statfs replies, xattr errors, and statx output. Risk is keeping Linux capability bits in sync with kernel headers.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/types_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/types_unix.go -->
# `sources/user-network-fs/go-fuse/fuse/types_unix.go`

## Purpose
Shared non-Darwin wire layout definitions for `Attr` and `SetAttrIn`.

## Important APIs, Types, And Functions
Defines Unix `Attr` fields and embeds `SetAttrInCommon` in `SetAttrIn`.

## Control Flow
Defines Unix `Attr` fields and embeds `SetAttrInCommon` in `SetAttrIn`.

## State And Persistence
State is protocol struct layout only. Risk is platform-specific padding/field mismatch; Linux/FreeBSD build tags combine this with per-OS constants.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is protocol struct layout only. Risk is platform-specific padding/field mismatch; Linux/FreeBSD build tags combine this with per-OS constants.

## Test Signals
State is protocol struct layout only. Risk is platform-specific padding/field mismatch; Linux/FreeBSD build tags combine this with per-OS constants.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/fuse/types_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/access.go -->
# `sources/user-network-fs/go-fuse/internal/access.go`

## Purpose
Implements permission checking used by loopback `Access`.

## Important APIs, Types, And Functions
`HasAccess` checks root, zero mask, owner bits, primary group bits, other bits, and supplementary groups via `os/user`.

## Control Flow
`HasAccess` checks root, zero mask, owner bits, primary group bits, other bits, and supplementary groups via `os/user`.

## State And Persistence
No persistent state; it queries OS user/group database on demand. Risks include expensive/fragile supplementary group lookup and simplified root semantics. Tests cover owner/group/other/root cases.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistent state; it queries OS user/group database on demand. Risks include expensive/fragile supplementary group lookup and simplified root semantics. Tests cover owner/group/other/root cases.

## Test Signals
No persistent state; it queries OS user/group database on demand. Risks include expensive/fragile supplementary group lookup and simplified root semantics. Tests cover owner/group/other/root cases.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/access.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/access_test.go -->
# `sources/user-network-fs/go-fuse/internal/access_test.go`

## Purpose
Unit tests for `internal.HasAccess`.

## Important APIs, Types, And Functions
`TestHasAccess` builds table cases using current uid/gid and another group id when available.

## Control Flow
`TestHasAccess` builds table cases using current uid/gid and another group id when available.

## State And Persistence
State is local user/group identity. Signal validates root, owner, group, other, and supplementary group permission decisions; risk is host account configuration variance.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is local user/group identity. Signal validates root, owner, group, other, and supplementary group permission decisions; risk is host account configuration variance.

## Test Signals
State is local user/group identity. Signal validates root, owner, group, other, and supplementary group permission decisions; risk is host account configuration variance.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/access_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/barrier/barrier.go -->
# `sources/user-network-fs/go-fuse/internal/barrier/barrier.go`

## Purpose
Declares architecture-specific memory barrier functions.

## Important APIs, Types, And Functions
Exports assembly-backed `Write`, `Read`, `Full`, and `LoadUint16`.

## Control Flow
Exports assembly-backed `Write`, `Read`, `Full`, and `LoadUint16`.

## State And Persistence
No Go state; these functions enforce ordering where lower-level shared memory/virtqueue code needs it. Risk is architecture-specific assembly correctness.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No Go state; these functions enforce ordering where lower-level shared memory/virtqueue code needs it. Risk is architecture-specific assembly correctness.

## Test Signals
No Go state; these functions enforce ordering where lower-level shared memory/virtqueue code needs it. Risk is architecture-specific assembly correctness.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/barrier/barrier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/barrier/barrier_amd64.s -->
# `sources/user-network-fs/go-fuse/internal/barrier/barrier_amd64.s`

## Purpose
amd64 implementations of memory barriers and 16-bit load.

## Important APIs, Types, And Functions
`Write`/`Read` are no-ops under x86 TSO, `Full` emits `MFENCE`, and `LoadUint16` loads with zero extension.

## Control Flow
`Write`/`Read` are no-ops under x86 TSO, `Full` emits `MFENCE`, and `LoadUint16` loads with zero extension.

## State And Persistence
No persistence. Risk is relying on TSO assumptions and correct Go ABI frame offsets.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistence. Risk is relying on TSO assumptions and correct Go ABI frame offsets.

## Test Signals
No persistence. Risk is relying on TSO assumptions and correct Go ABI frame offsets.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/barrier/barrier_amd64.s -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/barrier/barrier_arm64.s -->
# `sources/user-network-fs/go-fuse/internal/barrier/barrier_arm64.s`

## Purpose
arm64 implementations of memory barriers and 16-bit load.

## Important APIs, Types, And Functions
Uses `DMB` variants for store/load/full barriers and `MOVHU` for `LoadUint16`.

## Control Flow
Uses `DMB` variants for store/load/full barriers and `MOVHU` for `LoadUint16`.

## State And Persistence
No persistence. Risk is choosing the correct DMB domain/order; important for shared-memory integrations.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistence. Risk is choosing the correct DMB domain/order; important for shared-memory integrations.

## Test Signals
No persistence. Risk is choosing the correct DMB domain/order; important for shared-memory integrations.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/barrier/barrier_arm64.s -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/fallocate/fallocate.go -->
# `sources/user-network-fs/go-fuse/internal/fallocate/fallocate.go`

## Purpose
Cross-platform wrapper package for preallocating file space.

## Important APIs, Types, And Functions
Exports `Fallocate(fd, mode, off, len)` and delegates to platform `fallocate` implementation.

## Control Flow
Exports `Fallocate(fd, mode, off, len)` and delegates to platform `fallocate` implementation.

## State And Persistence
No state; host filesystem allocation persists. Integrated by loopback/nodefs allocation paths. Risk is mode support differing by OS.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No state; host filesystem allocation persists. Integrated by loopback/nodefs allocation paths. Risk is mode support differing by OS.

## Test Signals
No state; host filesystem allocation persists. Integrated by loopback/nodefs allocation paths. Risk is mode support differing by OS.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/fallocate/fallocate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/fallocate/fallocate_darwin.go -->
# `sources/user-network-fs/go-fuse/internal/fallocate/fallocate_darwin.go`

## Purpose
Darwin fallocate implementation via `fcntl(F_PREALLOCATE)`.

## Important APIs, Types, And Functions
Builds an `fstore_t`-like struct and calls `SYS_FCNTL`; currently ignores `mode`.

## Control Flow
Builds an `fstore_t`-like struct and calls `SYS_FCNTL`; currently ignores `mode`.

## State And Persistence
Persistent effect is disk preallocation. Risks are incomplete mode semantics and struct layout correctness.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Persistent effect is disk preallocation. Risks are incomplete mode semantics and struct layout correctness.

## Test Signals
Persistent effect is disk preallocation. Risks are incomplete mode semantics and struct layout correctness.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/fallocate/fallocate_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/fallocate/fallocate_freebsd.go -->
# `sources/user-network-fs/go-fuse/internal/fallocate/fallocate_freebsd.go`

## Purpose
FreeBSD fallocate implementation using `posix_fallocate` syscall.

## Important APIs, Types, And Functions
Calls `SYS_POSIX_FALLOCATE`, ignores mode, and converts nonzero return to `unix.Errno`.

## Control Flow
Calls `SYS_POSIX_FALLOCATE`, ignores mode, and converts nonzero return to `unix.Errno`.

## State And Persistence
State is allocated file blocks. Risk is lack of mode support and syscall return convention.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is allocated file blocks. Risk is lack of mode support and syscall return convention.

## Test Signals
State is allocated file blocks. Risk is lack of mode support and syscall return convention.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/fallocate/fallocate_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/fallocate/fallocate_linux.go -->
# `sources/user-network-fs/go-fuse/internal/fallocate/fallocate_linux.go`

## Purpose
Linux fallocate implementation.

## Important APIs, Types, And Functions
Delegates directly to `unix.Fallocate(fd, mode, off, len)`.

## Control Flow
Delegates directly to `unix.Fallocate(fd, mode, off, len)`.

## State And Persistence
State is host file allocation. Risk is kernel/filesystem support for mode flags; loopback Linux tests cover fallocate.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is host file allocation. Risk is kernel/filesystem support for mode flags; loopback Linux tests cover fallocate.

## Test Signals
State is host file allocation. Risk is kernel/filesystem support for mode flags; loopback Linux tests cover fallocate.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/fallocate/fallocate_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/ioctl/ioctl.go -->
# `sources/user-network-fs/go-fuse/internal/ioctl/ioctl.go`

## Purpose
Utility package for constructing and inspecting Linux ioctl command numbers.

## Important APIs, Types, And Functions
Defines direction constants, `Command`, `New`, and accessors such as read/write/type/number/size decoding.

## Control Flow
Defines direction constants, `Command`, `New`, and accessors such as read/write/type/number/size decoding.

## State And Persistence
No persistence. Integrated by ioctl tests and FUSE IOCTL handlers. Risk is command bitfield layout and panic on sizes >=16 KiB.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistence. Integrated by ioctl tests and FUSE IOCTL handlers. Risk is command bitfield layout and panic on sizes >=16 KiB.

## Test Signals
No persistence. Integrated by ioctl tests and FUSE IOCTL handlers. Risk is command bitfield layout and panic on sizes >=16 KiB.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/ioctl/ioctl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/openat/openat.go -->
# `sources/user-network-fs/go-fuse/internal/openat/openat.go`

## Purpose
Symlink-aware open helper rooted at a base directory.

## Important APIs, Types, And Functions
`OpenSymlinkAware` opens `baseDir` as a directory fd, rejects absolute relative paths, and calls platform `openatNoSymlinks`.

## Control Flow
`OpenSymlinkAware` opens `baseDir` as a directory fd, rejects absolute relative paths, and calls platform `openatNoSymlinks`.

## State And Persistence
State is only transient fds. Integration protects passthrough/loopback-style opens from symlink traversal. Risk is non-Linux fallback only blocks final component symlinks.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is only transient fds. Integration protects passthrough/loopback-style opens from symlink traversal. Risk is non-Linux fallback only blocks final component symlinks.

## Test Signals
State is only transient fds. Integration protects passthrough/loopback-style opens from symlink traversal. Risk is non-Linux fallback only blocks final component symlinks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/openat/openat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/openat/openat_linux.go -->
# `sources/user-network-fs/go-fuse/internal/openat/openat_linux.go`

## Purpose
Linux no-symlink open implementation.

## Important APIs, Types, And Functions
Uses `openat2` with `RESOLVE_NO_SYMLINKS`, `O_CLOEXEC`, and falls back to `openat` with `O_NOFOLLOW` on ENOSYS.

## Control Flow
Uses `openat2` with `RESOLVE_NO_SYMLINKS`, `O_CLOEXEC`, and falls back to `openat` with `O_NOFOLLOW` on ENOSYS.

## State And Persistence
Transient fd state only. Risk is weaker fallback on old kernels and correct mode/flags propagation.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Transient fd state only. Risk is weaker fallback on old kernels and correct mode/flags propagation.

## Test Signals
Transient fd state only. Risk is weaker fallback on old kernels and correct mode/flags propagation.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/openat/openat_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/openat/openat_unix.go -->
# `sources/user-network-fs/go-fuse/internal/openat/openat_unix.go`

## Purpose
Non-Linux no-symlink open fallback.

## Important APIs, Types, And Functions
Uses `unix.Openat` with `O_NOFOLLOW|O_CLOEXEC`.

## Control Flow
Uses `unix.Openat` with `O_NOFOLLOW|O_CLOEXEC`.

## State And Persistence
No persistence. Risk is explicitly documented: `O_NOFOLLOW` protects only the final component, not intermediate symlinks.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistence. Risk is explicitly documented: `O_NOFOLLOW` protects only the final component, not intermediate symlinks.

## Test Signals
No persistence. Risk is explicitly documented: `O_NOFOLLOW` protects only the final component, not intermediate symlinks.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/openat/openat_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/renameat/renameat.go -->
# `sources/user-network-fs/go-fuse/internal/renameat/renameat.go`

## Purpose
Cross-platform renameat wrapper.

## Important APIs, Types, And Functions
Exports `Renameat(olddirfd, oldpath, newdirfd, newpath, flags)` and delegates to platform implementation.

## Control Flow
Exports `Renameat(olddirfd, oldpath, newdirfd, newpath, flags)` and delegates to platform implementation.

## State And Persistence
Persistent effect is filesystem rename/exchange. Integrated by FUSE rename handling needing flags. Risk is platform flag support mismatch.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Persistent effect is filesystem rename/exchange. Integrated by FUSE rename handling needing flags. Risk is platform flag support mismatch.

## Test Signals
Persistent effect is filesystem rename/exchange. Integrated by FUSE rename handling needing flags. Risk is platform flag support mismatch.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/renameat/renameat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/renameat/renameat_darwin.go -->
# `sources/user-network-fs/go-fuse/internal/renameat/renameat_darwin.go`

## Purpose
Darwin renameat implementation using `renameatx_np`.

## Important APIs, Types, And Functions
Defines `SYS_RENAMEATX_NP`, `RENAME_SWAP`, `RENAME_EXCHANGE`, converts paths to C strings, and performs `Syscall6`.

## Control Flow
Defines `SYS_RENAMEATX_NP`, `RENAME_SWAP`, `RENAME_EXCHANGE`, converts paths to C strings, and performs `Syscall6`.

## State And Persistence
State is host filesystem namespace changes. Risk is syscall number/API compatibility across Darwin versions.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is host filesystem namespace changes. Risk is syscall number/API compatibility across Darwin versions.

## Test Signals
State is host filesystem namespace changes. Risk is syscall number/API compatibility across Darwin versions.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/renameat/renameat_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/renameat/renameat_freebsd.go -->
# `sources/user-network-fs/go-fuse/internal/renameat/renameat_freebsd.go`

## Purpose
FreeBSD renameat implementation.

## Important APIs, Types, And Functions
Defines Linux-compatible `RENAME_EXCHANGE` constant but returns ENOSYS for nonzero flags; plain rename delegates to `unix.Renameat`.

## Control Flow
Defines Linux-compatible `RENAME_EXCHANGE` constant but returns ENOSYS for nonzero flags; plain rename delegates to `unix.Renameat`.

## State And Persistence
Persistent namespace change only. Risk is callers expecting exchange/no-replace semantics on FreeBSD.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Persistent namespace change only. Risk is callers expecting exchange/no-replace semantics on FreeBSD.

## Test Signals
Persistent namespace change only. Risk is callers expecting exchange/no-replace semantics on FreeBSD.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/renameat/renameat_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/renameat/renameat_linux.go -->
# `sources/user-network-fs/go-fuse/internal/renameat/renameat_linux.go`

## Purpose
Linux renameat implementation.

## Important APIs, Types, And Functions
Defines `RENAME_EXCHANGE` from `unix` and delegates to `unix.Renameat2`.

## Control Flow
Defines `RENAME_EXCHANGE` from `unix` and delegates to `unix.Renameat2`.

## State And Persistence
Persistent namespace change only. Risk is kernel/filesystem support for flags and errno propagation.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Persistent namespace change only. Risk is kernel/filesystem support for flags and errno propagation.

## Test Signals
Persistent namespace change only. Risk is kernel/filesystem support for flags and errno propagation.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/renameat/renameat_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/testutil/helpers.go -->
# `sources/user-network-fs/go-fuse/internal/testutil/helpers.go`

## Purpose
Placeholder/helper package file for shared test utilities.

## Important APIs, Types, And Functions
Contains package declaration and licensing; no functions in this file.

## Control Flow
Contains package declaration and licensing; no functions in this file.

## State And Persistence
No state. It keeps `internal/testutil` package shape stable.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No state. It keeps `internal/testutil` package shape stable.

## Test Signals
No state. It keeps `internal/testutil` package shape stable.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/testutil/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/testutil/log.go -->
# `sources/user-network-fs/go-fuse/internal/testutil/log.go`

## Purpose
Test logging initialization.

## Important APIs, Types, And Functions
`init` sets standard log flags to microseconds for tests.

## Control Flow
`init` sets standard log flags to microseconds for tests.

## State And Persistence
Global process log state is modified. Risk is test-global side effect, but it improves timing diagnostics.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
Global process log state is modified. Risk is test-global side effect, but it improves timing diagnostics.

## Test Signals
Global process log state is modified. Risk is test-global side effect, but it improves timing diagnostics.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/testutil/log.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/testutil/verbose.go -->
# `sources/user-network-fs/go-fuse/internal/testutil/verbose.go`

## Purpose
Shared verbose-test detection helper.

## Important APIs, Types, And Functions
`VerboseTest` checks the runtime stack for `TestNonVerbose` and reads `test.v`.

## Control Flow
`VerboseTest` checks the runtime stack for `TestNonVerbose` and reads `test.v`.

## State And Persistence
No persistence. Integrated into many mount options to enable debug logs under `go test -v`. Risk is stack-name heuristic and unavailable flag outside tests.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No persistence. Integrated into many mount options to enable debug logs under `go test -v`. Risk is stack-name heuristic and unavailable flag outside tests.

## Test Signals
No persistence. Integrated into many mount options to enable debug logs under `go test -v`. Risk is stack-name heuristic and unavailable flag outside tests.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/testutil/verbose.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/utimens/utimens_darwin.go -->
# `sources/user-network-fs/go-fuse/internal/utimens/utimens_darwin.go`

## Purpose
Darwin timestamp helper for preserving omitted atime/mtime.

## Important APIs, Types, And Functions
Defines `timeToTimeval` and `Fill`; nil timestamps are filled from `fuse.Attr`, then converted to `syscall.Timeval`.

## Control Flow
Defines `timeToTimeval` and `Fill`; nil timestamps are filled from `fuse.Attr`, then converted to `syscall.Timeval`.

## State And Persistence
State is returned timeval slice only. Risk is pre-1970 conversion and attr requirement when either timestamp is nil. Used by pathfs loopback Darwin.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
State is returned timeval slice only. Risk is pre-1970 conversion and attr requirement when either timestamp is nil. Used by pathfs loopback Darwin.

## Test Signals
State is returned timeval slice only. Risk is pre-1970 conversion and attr requirement when either timestamp is nil. Used by pathfs loopback Darwin.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/utimens/utimens_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/utimens/utimens_linux.go -->
# `sources/user-network-fs/go-fuse/internal/utimens/utimens_linux.go`

## Purpose
Placeholder file so the `utimens` package exists on Linux.

## Important APIs, Types, And Functions
No runtime API in this file; Linux uses `utimensat` in pathfs instead of Darwin timeval emulation.

## Control Flow
No runtime API in this file; Linux uses `utimensat` in pathfs instead of Darwin timeval emulation.

## State And Persistence
No state or risks beyond package consistency.

## Dependencies And Integration Points
Dependencies and integration are captured by the package imports and neighboring files in this subset.

## Risks And Edge Cases
No state or risks beyond package consistency.

## Test Signals
No state or risks beyond package consistency.

<!-- END_FILE_RESEARCH: sources/user-network-fs/go-fuse/internal/utimens/utimens_linux.go -->
