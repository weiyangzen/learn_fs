<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/main_test.go -->
# sources/security-integrity/gocryptfs/tests/matrix/main_test.go

## Purpose
Defines the matrix test harness for gocryptfs forward-mode integration tests. It reruns the same package tests across combinations of filename encryption, OpenSSL acceleration, AES-SIV, raw64, XChaCha, serialized reads, shared storage, and deterministic names.

## Important APIs, Types, And Functions
- `testcaseMatrix` records the active mode: `plaintextnames`, `openssl`, `aessiv`, `raw64`, and `extraArgs`.
- `testcase` and `ctlsockPath` are package globals consumed by other matrix tests.
- `(*testcaseMatrix).isSet` checks whether a mount option is active.
- `TestMain` is the package entry point and loops over every configured matrix row.

## Control Flow
`TestMain` parses flags, skips OpenSSL-only rows when built without OpenSSL, resets the shared temp directories, builds mount arguments, mounts gocryptfs with `-zerokey` and a control socket, runs `m.Run`, checks the test process for file descriptor leaks, unmounts, and exits on the first failing matrix row.

## State And Persistence
The harness recreates `test_helpers.DefaultPlainDir` and `DefaultCipherDir` for every row, optionally writes `gocryptfs.diriv`, creates a per-row control socket, and removes it after unmount to avoid asynchronous socket cleanup races.

## Dependencies And Integration Points
Depends on `internal/stupidgcm` for OpenSSL build detection and on `tests/test_helpers` for reset, mount, fd listing, and unmount behavior. All package tests implicitly depend on the global `testcase` and default directories initialized here.

## Risks And Edge Cases
Because the same tests run many times, leaked file descriptors or stale mount state can cascade. Mode flags alter expected behavior, especially reserved names, diriv files, and deterministic name handling.

## Test Signals
Signals success by completing every matrix row with `m.Run()==0`, stable fd counts, and clean unmounts. Failures identify the exact matrix row printed by `TestMain`.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/matrix_test.go -->
# sources/security-integrity/gocryptfs/tests/matrix/matrix_test.go

## Purpose
Contains the bulk of forward-mode filesystem behavior tests for gocryptfs. It verifies data integrity, truncation, sparse files, name encryption, long names, metadata operations, timestamps, special files, permissions, sizing, and rename exchange.

## Important APIs, Types, And Functions
- `testWriteN` writes deterministic random-sized payloads and verifies size plus MD5.
- `TestWrite10`, `TestWrite100`, `TestWrite1M`, `TestWrite100x100`, and `TestWrite10Tight` cover repeated file I/O.
- `TestTruncate`, `TestAppend`, `TestFileHoles`, and `TestRmwRace` stress content size, sparse, append, and concurrent read-modify-write paths.
- `TestFiltered`, `TestFilenameEncryption`, `TestNameLengths`, `TestLongNames`, `TestLongLink`, and `TestMagicNames` cover name translation edge cases.
- `doTestUtimesNano`, `TestUtimesNano`, `TestUtimesNanoFd`, `TestUtimesNanoSymlink`, `TestChmod`, `TestAccess`, `TestStatfs`, `TestSymlinkSize`, `TestLinkSize`, `TestDirSize`, and `TestRenameExchangeOnGocryptfs` cover metadata and syscall behavior.

## Control Flow
Each test operates under the active mount created by `matrix/main_test.go`. Data-path tests create files under `DefaultPlainDir`, verify plaintext results, and sometimes inspect `DefaultCipherDir` or the control socket to reason about encrypted names. Metadata tests call low-level syscalls directly to catch FUSE/kernel contract regressions.

## State And Persistence
State is mostly temporary filesystem state in the mounted gocryptfs tree. Some tests intentionally create long-name helper files, special names, FIFOs, symlinks, hard links, and nested directories, then remove them or compare final cipherdir entry counts.

## Dependencies And Integration Points
Depends on Go `os`, `syscall`, `golang.org/x/sys/unix`, `internal/syscallcompat`, `ctlsock`, and shared helpers for MD5, size checks, rename checks, and control-socket queries.

## Risks And Edge Cases
The file contains mode-sensitive expectations for `-plaintextnames`, long-name virtual files, raw64, deterministic names, and Darwin timestamp limitations. `TestRmwRace` records acceptable hashes but does not assert the map contents, so it is mainly a race reproducer scaffold.

## Test Signals
Strong signals include fixed MD5s after truncation, size agreement between read/stat/fstat, successful long-name create/rename/unlink cycles without cipherdir leaks, correct symlink and hardlink sizes, and successful `RENAME_EXCHANGE` content swap.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/matrix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/symlink_darwin_test.go -->
# sources/security-integrity/gocryptfs/tests/matrix/symlink_darwin_test.go

## Purpose
Provides the Darwin-specific symlink-open test for matrix mounts, using macOS `O_SYMLINK` semantics instead of Linux `O_PATH`.

## Important APIs, Types, And Functions
- `TestOpenSymlinkDarwin` creates a dangling symlink, opens it with `unix.O_SYMLINK`, checks `Fstat` size, unlinks the path, and confirms the open fd remains stat-able.

## Control Flow
The test creates a symlink in the mounted plaintext directory, opens the symlink object itself, validates reported size equals target length, unlinks it, and repeats `Fstat` on the still-open descriptor.

## State And Persistence
Only a single temporary symlink and fd are created. The fd is closed with `defer`; the path is removed during the test.

## Dependencies And Integration Points
Depends on `golang.org/x/sys/unix`, `os`, and the matrix default mount provided by `test_helpers.DefaultPlainDir`.

## Risks And Edge Cases
This is platform-specific; it would not compile or behave correctly on Linux because the open flag differs. It also checks a subtle post-unlink descriptor lifetime contract.

## Test Signals
Success means Darwin can open and stat symlink dentries through gocryptfs and preserve fd validity after unlink.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/symlink_darwin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/symlink_linux_test.go -->
# sources/security-integrity/gocryptfs/tests/matrix/symlink_linux_test.go

## Purpose
Provides the Linux-specific symlink-open test for matrix mounts, using `openat2` with `O_PATH|O_NOFOLLOW` and `Fstatat(AT_EMPTY_PATH)`.

## Important APIs, Types, And Functions
- `TestOpenSymlinkLinux` creates a dangling symlink, opens the symlink object using `unix.Openat2`, checks target-length size, unlinks it, and attempts a post-unlink empty-path stat.

## Control Flow
The test exercises Linux kernel APIs directly against the FUSE mount to validate symlink dentry metadata and document a known post-unlink compliance limitation.

## State And Persistence
State is a single symlink and an open `O_PATH` fd. The symlink is unlinked before the final stat check.

## Dependencies And Integration Points
Depends on Linux `openat2`, `AT_EMPTY_PATH`, `golang.org/x/sys/unix`, and the shared matrix mount.

## Risks And Edge Cases
The final `Fstatat` failure is logged rather than fatal because gocryptfs is not notified about the earlier `O_PATH` open; treating it as fatal would encode a currently unresolved compliance issue.

## Test Signals
Success is a valid pre-unlink fd stat with correct symlink size and no fatal errors during creation/open/unlink.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/matrix/symlink_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/plaintextnames/file_holes_test.go -->
# sources/security-integrity/gocryptfs/tests/plaintextnames/file_holes_test.go

## Purpose
Targets sparse-file preservation in `-plaintextnames` mode, where plaintext and ciphertext paths map directly enough to compare hole layouts on both sides.

## Important APIs, Types, And Functions
- `findHolesPretty` wraps `contrib/findholes/holes.Find` and pretty-prints sparse extents.
- `doTestFileHoleCopy` creates a sparse file, copies it repeatedly with `cp --sparse=auto`, verifies MD5s, block usage, and hole/data segment stability.
- `TestFileHoleCopy` defines deterministic and randomized sparse layouts but is currently skipped.

## Control Flow
The helper creates a sparse source, records plaintext and cipherdir hole segments, copies through the mount several times, then compares MD5, disk blocks, and hole maps across copies. Randomized subtests would broaden sparse extent coverage if the skip were removed.

## State And Persistence
It creates multiple plaintext and ciphertext files named from `TestFileHoleCopy.*`. State is local to the plaintextnames test mount and is not cleaned inside the helper beyond initial removal of the base path.

## Dependencies And Integration Points
Depends on GNU `cp --sparse=auto`, `contrib/findholes/holes`, `syscall.Stat`, MD5 helpers, and the plaintextnames package globals `pDir` and `cDir`.

## Risks And Edge Cases
The entire test is skipped with a TODO for recent-kernel failures, so it documents desired behavior more than it protects CI. Sparse detection depends on filesystem allocation heuristics and ext4 extent behavior.

## Test Signals
Current test signal is `SKIP`. If enabled, pass conditions include stable MD5, bounded block-count drift, and identical pretty-printed hole maps across copies.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/plaintextnames/file_holes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/plaintextnames/plaintextnames_test.go -->
# sources/security-integrity/gocryptfs/tests/plaintextnames/plaintextnames_test.go

## Purpose
Defines integration tests specific to gocryptfs `-plaintextnames` mode, where filenames are not encrypted and several normal encrypted-name invariants change.

## Important APIs, Types, And Functions
- `TestMain` initializes and mounts a plaintextnames filesystem.
- `TestFlags` decrypts `gocryptfs.conf` and checks feature flags.
- `TestDirIV` asserts diriv files are not created in root or subdirectories.
- `TestFiltered` checks reserved root `gocryptfs.conf` filtering while allowing other magic names.
- `TestInoReuseEvil` manipulates cipherdir entries behind the mount to stress inode reuse.
- `TestRootIno` checks the root inode number is nonzero.

## Control Flow
The package-level mount is created once. Tests inspect config flags, create directories and files through the mount, and in `TestInoReuseEvil` deliberately remove and recreate backing objects to mimic inode reuse collisions.

## State And Persistence
`cDir`, `pDir`, and `testPw` are package state. The mounted filesystem persists for all package tests and is unmounted in `TestMain` after `m.Run`.

## Dependencies And Integration Points
Depends on `internal/configfile` for config verification and `test_helpers` for initialization and mounting. Uses direct `syscall` calls to test low-level behavior.

## Risks And Edge Cases
The inode reuse test relies on filesystems such as ext4 that recycle inode numbers; on others it may not reproduce the intended edge. Reserved-name behavior differs between root and subdirectories.

## Test Signals
Signals include exact feature flag set, absent diriv files, expected failures for root `gocryptfs.conf`, allowed non-root magic names, and nonzero root inode.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/plaintextnames/plaintextnames_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/correctness_test.go -->
# sources/security-integrity/gocryptfs/tests/reverse/correctness_test.go

## Purpose
Exercises reverse-mode correctness through a normal directory, a reverse encrypted view, and a forward mount of that encrypted view. It focuses on virtual files, symlinks, long names, access checks, sparse seeking, inode reuse, and timestamp nudging.

## Important APIs, Types, And Functions
- `TestLongnameStat`, `TestSymlinks`, `TestSymlinkDentrySize`, and `TestConfigMapping` verify reverse presentation of names, symlinks, and config mapping.
- `TestAccessVirtualDirIV`, `TestAccess`, `TestEnoent`, `TestTooLongSymlink`, `Test0100Dir`, `TestStatfs`, and `TestSeekData` cover syscall semantics.
- `newWorkdir` maps plaintext workdirs to encrypted paths by inode.
- `TestHardlinkedLongname` and `TestMtimePlus10` protect virtual longname and diriv inode/cache behavior.

## Control Flow
Tests create source files in `dirA`, observe encrypted names in `dirB`, and often verify decrypted content through `dirC`. Control socket queries and inode matching bridge plaintext and encrypted views for long-name and virtual-file assertions.

## State And Persistence
State spans all three package global dirs initialized by reverse `TestMain`. Some tests move or rename files instead of unlinking to avoid immediate ext4 inode reuse side effects.

## Dependencies And Integration Points
Depends on `ctlsock`, `internal/syscallcompat`, `golang.org/x/sys/unix`, shared helper functions, and the reverse package globals `plaintextnames`, `deterministic_names`, `dirA`, `dirB`, and `dirC`.

## Risks And Edge Cases
Many expectations are mode-sensitive: plaintextnames and deterministic names skip virtual diriv or longname assertions. Long symlink limits vary by backing filesystem.

## Test Signals
Signals include readable forward-remounted content, correct virtual config and diriv behavior, expected `ENOENT`/`ENAMETOOLONG`, successful traversal of execute-only dirs, preserved SEEK_DATA behavior in plaintextnames mode, distinct `.name` inodes, and mtime+10 for virtual files.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/correctness_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/ctlsock_reverse_test_fs/.gocryptfs.reverse.conf -->
# sources/security-integrity/gocryptfs/tests/reverse/ctlsock_reverse_test_fs/.gocryptfs.reverse.conf

## Purpose
Fixture configuration for reverse-mode control-socket path mapping tests. It supplies deterministic keys, scrypt parameters, version, and feature flags for the `ctlsock_reverse_test_fs` tree.

## Important APIs, Types, And Functions
- `Creator` records the originating gocryptfs version string.
- `EncryptedKey` and `ScryptObject` define the encrypted master key and KDF parameters.
- `FeatureFlags` includes `GCMIV128`, `DirIV`, `EMENames`, `LongNames`, and `AESSIV`.

## Control Flow
The file is consumed by gocryptfs when the fixture directory is mounted with `-reverse -extpass 'echo test'`. The tests then query deterministic encrypted and plaintext path mappings through the control socket.

## State And Persistence
Persistent fixture state is the JSON configuration itself. The low scrypt `N=1024` keeps tests fast while preserving the config shape.

## Dependencies And Integration Points
Integrated by reverse tests, especially `ctlsock_test.go` and `correctness_test.go`, via `test_helpers.MountOrFatal` against `ctlsock_reverse_test_fs`.

## Risks And Edge Cases
Changing this file invalidates hard-coded encrypted path fixtures. The key material is test-only but still grants access to fixture expectations.

## Test Signals
A valid signal is successful mount and exact control-socket mapping for every hard-coded fixture path.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/ctlsock_reverse_test_fs/.gocryptfs.reverse.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/ctlsock_test.go -->
# sources/security-integrity/gocryptfs/tests/reverse/ctlsock_test.go

## Purpose
Verifies reverse-mode control socket `EncryptPath` and `DecryptPath` operations against a deterministic fixture tree with short and long names.

## Important APIs, Types, And Functions
- `ctlSockTestCases` maps encrypted fixture paths to plaintext paths.
- `TestCtlSockPathOps` round-trips every case through `ctlsock.RequestStruct`.
- `TestCtlSockCrash` sends a malformed longname request under relaxed panic/syslog settings.

## Control Flow
The tests mount `ctlsock_reverse_test_fs` in reverse mode with a per-test socket, then issue decrypt and encrypt requests. After populating longname parent caches, they query deliberately wrong parent/name combinations and expect `ENOENT`.

## State And Persistence
State is the mounted fixture tree and its control socket. The fixture config and files provide deterministic encrypted names.

## Dependencies And Integration Points
Depends on `ctlsock`, `test_helpers.QueryCtlSock`, `test_helpers.MountOrFatal`, and reverse package `plaintextnames` to skip non-encrypted-name modes.

## Risks And Edge Cases
Hard-coded names are brittle by design; any encryption, longname, or fixture config change requires updating the table. Crash coverage intentionally does not assert much beyond not terminating the mount.

## Test Signals
Pass signals are exact path round trips, expected `ENOENT` for cache mixups, and no panic/crash on nonsensical longname input.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/ctlsock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/exclude_test.go -->
# sources/security-integrity/gocryptfs/tests/reverse/exclude_test.go

## Purpose
Tests reverse-mode exclude and exclude-wildcard handling, including gitignore-style patterns, long names, negation, directory-only matches, anchors, and recursive globs.

## Important APIs, Types, And Functions
- `ctlsockEncryptPath` encrypts plaintext relative paths through the reverse control socket.
- `doTestExcludeTestFs` mounts with exclude flags, creates a synthetic tree, encrypts expected paths, and checks visibility.
- `directoryTree` models visible and hidden files and directories.
- `TestExcludeTestFs` and `TestExcludeAllOnlyDir1` define pattern sets and expected trees.

## Control Flow
For each pattern set, the test creates the backing tree after mounting, converts expected plaintext paths to encrypted names, adds `.name` companions for long encrypted names, and verifies hidden paths are absent while visible paths exist.

## State And Persistence
State is a temporary reverse filesystem and generated backing directory tree. The test relies on control-socket encryption to avoid embedding mode-specific encrypted names.

## Dependencies And Integration Points
Depends on `ctlsock`, `internal/nametransform`, reverse `newReverseFS`, and `test_helpers.VerifyExistence`.

## Risks And Edge Cases
Long-name exclusion has two artifacts: content and `.name`. Negation and anchored patterns can be easy to regress because visibility is checked in encrypted view rather than plaintext tree.

## Test Signals
Signals include absence of every hidden encrypted path, presence of every visible encrypted path, and coverage of both `-exclude-wildcard` and `-ew` aliases.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/exclude_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/force_owner_test.go -->
# sources/security-integrity/gocryptfs/tests/reverse/force_owner_test.go

## Purpose
Checks reverse-mode `-force_owner` ownership rewriting when mounting a real filesystem root through gocryptfs.

## Important APIs, Types, And Functions
- `TestForceOwner` mounts `/` with `-reverse -zerokey -force_owner=1234:1234` and mode-specific name flags.

## Control Flow
The test creates a temporary mountpoint, mounts the system root in reverse mode, lists root entries, then `Lstat`s the mountpoint and each top-level entry to verify uid/gid rewriting.

## State And Persistence
State is a temporary reverse mount. It does not mutate `/`; it only reads metadata through the mount.

## Dependencies And Integration Points
Depends on `test_helpers.MountOrFatal`, `syscall.Lstat`, and reverse globals for plaintext/deterministic name mode.

## Risks And Edge Cases
Running against `/` means host permissions and mount contents affect coverage. The deferred unmount uses `UnmountErr`, so failures are reported but not panic-cleaned.

## Test Signals
Pass signal is every checked path reporting uid and gid 1234.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/force_owner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/inomap_test.go -->
# sources/security-integrity/gocryptfs/tests/reverse/inomap_test.go

## Purpose
Validates inode mapping for reverse-mode passthrough files and virtual files such as `gocryptfs.diriv` and longname `.name` helpers.

## Important APIs, Types, And Functions
- `findIno` scans a directory for an entry with a requested inode.
- `TestVirtualFileIno` compares original parent/child inodes with encrypted parent, diriv, child, and `.name` inodes.

## Control Flow
The test creates a parent directory and a long-name child, records source inodes, locates the encrypted parent by inode in `dirB`, enumerates its entries, classifies virtual and real entries, and applies collision and high-bit spill-space checks.

## State And Persistence
State is a generated directory tree under `dirA` and corresponding virtual entries under `dirB`. No durable state escapes the reverse test temp dirs.

## Dependencies And Integration Points
Depends on reverse globals, direct `syscall.Lstat`, and directory enumeration. It shares `findIno` with `correctness_test.go` through package scope.

## Risks And Edge Cases
Plaintextnames mode has no virtual files and is skipped. Deterministic names suppress diriv checks. The test encodes assumptions about lower 48-bit passthrough inode space and high spill-space allocation.

## Test Signals
Signals include matching parent and child passthrough inodes, no collisions with diriv or `.name`, lower-bit diriv derivation when applicable, and `.name` inode above `1<<63`.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/inomap_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/linux-tarball-test.bash -->
# sources/security-integrity/gocryptfs/tests/reverse/linux-tarball-test.bash

## Purpose
End-to-end reverse-mode smoke test that extracts the Linux 3.0 tarball, mounts it reverse, remounts the encrypted view forward, and verifies the original tree through MD5 checks.

## Important APIs, Types, And Functions
- `../dl-linux-tarball.bash` ensures `/tmp/linux-3.0.tar.gz` exists.
- `gocryptfs -reverse -init`, reverse mount, and forward mount build an `a -> b -> c` chain.
- `md5sum -c` compares against `tests/stress_tests/linux-3.0.md5sums`.

## Control Flow
The script creates a temp workdir under `/tmp`, extracts the kernel tree to `a`, initializes reverse config, mounts `a` on `b`, mounts `b` on `c`, then runs MD5 verification from `c` with `pv` progress and filters OK lines.

## State And Persistence
It creates temp directories and FUSE mounts, cleaned by an EXIT trap using `fuse-unmount -z` and `rm -rf`.

## Dependencies And Integration Points
Depends on shell utilities, tar, md5sum, pv, gocryptfs in PATH, the shared unmount helper, and the Linux tarball checksum fixture.

## Risks And Edge Cases
The test is heavyweight and assumes `/tmp` space plus Linux checksum fixture stability. It does not use the just-built `../../gocryptfs` path explicitly.

## Test Signals
A clean pass means every file in the forward-remounted reverse view matches the known Linux 3.0 MD5 sums.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/linux-tarball-test.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/longname_perf_test.go -->
# sources/security-integrity/gocryptfs/tests/reverse/longname_perf_test.go

## Purpose
Benchmark for reverse-mode stat performance over very large numbers of long-name files.

## Important APIs, Types, And Functions
- `genName` formats numbered long filenames using the shared `x240` suffix.
- `generateLongnameFiles` creates 100000 long-name files.
- `BenchmarkLongnameStat` enumerates encrypted names in `dirB` and repeatedly stats them.

## Control Flow
The benchmark seeds `dirA` with long files, reads the encrypted directory listing once, resets the timer, and stats encrypted names round-robin for `b.N` iterations.

## State And Persistence
It creates a large persistent set of files during benchmark setup and removes/recreates `dirA` after timing stops.

## Dependencies And Integration Points
Depends on the reverse `TestMain` mount, `x240`, and filesystem ability to handle 100000 entries.

## Risks And Edge Cases
The comment says 10000 files but the loop creates 100000. It is expensive and can dominate benchmark setup time or temp storage.

## Test Signals
Signal is benchmark latency for stat calls in the encrypted reverse view without stat failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/longname_perf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/main_test.go -->
# sources/security-integrity/gocryptfs/tests/reverse/main_test.go

## Purpose
Defines the reverse-mode package test harness. It runs the reverse tests across encrypted names, plaintextnames, and deterministic-names modes using a reverse mount plus a forward mount.

## Important APIs, Types, And Functions
- `x240` is a long-name suffix shared by reverse tests.
- `plaintextnames`, `deterministic_names`, `dirA`, `dirB`, and `dirC` are package globals.
- `TestMain` loops over mode combinations and controls mount lifecycle.
- `newReverseFS` initializes and mounts a reverse filesystem, returning backing, mount, and control-socket paths.

## Control Flow
`TestMain` creates `dirA` backing via `newReverseFS`, mounts the encrypted reverse view `dirB` forward at `dirC`, runs all tests, unmounts both layers, cleans temp dirs, and exits on the first failing mode.

## State And Persistence
The harness persists mode globals for each `m.Run` and removes all dirs after each mode. `newReverseFS` creates a config using `InitFS` with reverse-related flags.

## Dependencies And Integration Points
Depends on `test_helpers.InitFS`, `MountOrExit`, `UnmountPanic`, Go test flag parsing, and the gocryptfs binary.

## Risks And Edge Cases
Global state means tests must not assume a single mode. Cleanup depends on successful unmount of both reverse and forward layers.

## Test Signals
Signals are complete success across all three mode rows with clean mount setup and teardown.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/one_file_system_test.go -->
# sources/security-integrity/gocryptfs/tests/reverse/one_file_system_test.go

## Purpose
Tests reverse-mode `-one-file-system` behavior on Linux by mounting `/` and ensuring cross-device mountpoints are hidden except for expected virtual entries.

## Important APIs, Types, And Functions
- `TestOneFileSystem` identifies top-level directories whose inode numbers were remapped above the passthrough range, then attempts to read them.

## Control Flow
The test mounts `/` with `-reverse -zerokey -one-file-system`, scans top-level entries, treats high inode numbers as mountpoints from other devices, and verifies their directory listings are empty or contain only `gocryptfs.diriv` depending on mode.

## State And Persistence
State is a temporary reverse mount of `/`; it reads host root metadata but does not modify it.

## Dependencies And Integration Points
Depends on Linux, reverse mode flags, `test_helpers`, and inode range assumptions copied from inomap.

## Risks And Edge Cases
It skips on non-Linux and when no mountpoints are found. Host root layout affects how much coverage is achieved.

## Test Signals
Pass signal is every detected cross-device mountpoint exposing only the expected number of entries.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/one_file_system_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/xattr_test.go -->
# sources/security-integrity/gocryptfs/tests/reverse/xattr_test.go

## Purpose
Checks xattr pass-through behavior in reverse mode, including list/get on source-created attributes and mountpoint error handling.

## Important APIs, Types, And Functions
- `xattrSupported` probes whether a path supports user xattrs.
- `TestXattrList` creates many `user.*` attrs on a source file and compares the reverse-forward view.
- `TestXattrGetMountpoint` ensures querying the reverse mountpoint does not return `EINVAL`.

## Control Flow
The list test writes xattrs on `dirA`, lists and reads them through `dirC`, filters unrelated `security.*` attributes, and compares names and values. The mountpoint test probes `dirB` directly.

## State And Persistence
State consists of a temporary file and its xattrs in the reverse test backing dir.

## Dependencies And Integration Points
Depends on `github.com/pkg/xattr`, reverse package dirs, and Linux-like xattr semantics.

## Risks And Edge Cases
Xattr support is filesystem-dependent and may skip. Security attributes can appear externally and are ignored to avoid false failures.

## Test Signals
Signals include equal user xattr counts and values through reverse/forward layers, and no `EINVAL` on mountpoint xattr get.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/reverse/xattr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/root_test/btrfs_test.go -->
# sources/security-integrity/gocryptfs/tests/root_test/btrfs_test.go

## Purpose
Root-only tests for detecting btrfs fallocate quirks and ensuring the NOCOW attribute suppresses the broken-fallocate quirk.

## Important APIs, Types, And Functions
- `createBtrfsImage` creates, formats, mounts, and returns cleanup for a loop-backed btrfs image.
- `TestBtrfsQuirks` expects `DetectQuirks` to report `QuirkBtrfsBrokenFalloc` on normal btrfs.
- `TestBtrfsQuirksNoCow` applies `chattr +C` and expects that quirk to be absent.

## Control Flow
The helper skips unless root and `mkfs.btrfs` are available, then uses an image file as a mounted btrfs filesystem. Tests run quirk detection on the mount root and on a NOCOW subdirectory.

## State And Persistence
Creates a 200 MiB image and a mounted loop filesystem under `test_helpers.TmpDir`, cleaned by unmount and unlink.

## Dependencies And Integration Points
Depends on root, `mkfs.btrfs`, `mount`, optional `chattr`, and `internal/syscallcompat.DetectQuirks`.

## Risks And Edge Cases
Cleanup does not remove the mount directory and uses plain `syscall.Unmount`; abrupt failures can leave loop mounts. The test is sensitive to kernel btrfs behavior.

## Test Signals
Pass signals are exact quirk detection for normal btrfs and absence of `QuirkBtrfsBrokenFalloc` on NOCOW directories.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/root_test/btrfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/root_test/issue893_test.go -->
# sources/security-integrity/gocryptfs/tests/root_test/issue893_test.go

## Purpose
Regression tests for issue 893, where credential-changing syscalls began affecting the whole Go process and broke concurrent `allow_other` operations.

## Important APIs, Types, And Functions
- `TestConcurrentUserOps` runs multiple goroutines that switch credentials with `asUser` and perform mkdir/write/unlink cycles.
- `TestAsUserSleep` verifies `asUser` keeps the expected euid stable during concurrent sleeps.

## Control Flow
Both tests skip unless running as root. They spawn goroutines that call the shared thread-locked credential helper and perform either filesystem mutations through the root test mount or direct euid checks.

## State And Persistence
State is temporary directory/file content under `DefaultPlainDir` plus process credential changes confined by `runtime.LockOSThread` in `asUser`.

## Dependencies And Integration Points
Depends on root, the root test package mount, `asUser` from `root_test.go`, and Linux credential behavior.

## Risks And Edge Cases
These tests are concurrency-sensitive and can expose process-wide credential leakage. Failures may leave created directories but the root harness resets temp state between package runs.

## Test Signals
Signals are no credential mismatch and no filesystem operation errors across all concurrent user contexts.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/root_test/issue893_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/root_test/main_test.go -->
# sources/security-integrity/gocryptfs/tests/root_test/main_test.go

## Purpose
Linux-only root test harness that mounts a default gocryptfs filesystem with `-allow_other` for tests that need uid/gid switching, ACLs, overlay, disk-full, and root-specific behavior.

## Important APIs, Types, And Functions
- `TestMain` resets temp dirs, opens cipherdir permissions, mounts with `-zerokey -allow_other`, runs package tests, unmounts, and removes the temp tree.

## Control Flow
The harness creates a diriv-enabled cipherdir, chmods it to 0777 so switched users can access it, mounts gocryptfs, delegates to `m.Run`, and tears everything down.

## State And Persistence
It owns package-wide temp state in `test_helpers.DefaultCipherDir`, `DefaultPlainDir`, and `TmpDir`.

## Dependencies And Integration Points
Depends on Linux build tag, `test_helpers.ResetTmpDir`, `MountOrExit`, and `UnmountPanic`.

## Risks And Edge Cases
If mount setup fails the whole root package exits. Root and FUSE `allow_other` configuration are prerequisites for useful coverage.

## Test Signals
Success means all root package tests can share one mounted filesystem and cleanup removes the temp tree.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/root_test/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/root_test/root_test.go -->
# sources/security-integrity/gocryptfs/tests/root_test/root_test.go

## Purpose
Contains root-only integration tests for credential switching, supplementary groups, ENOSPC handling, ACL enforcement, overlayfs compatibility, and `-force_owner` operations.

## Important APIs, Types, And Functions
- `asUser` locks the current OS thread, sets groups/gid/uid, runs a callback, and resets real/effective/saved ids and gids.
- `TestSupplementaryGroups` checks group-based access under `allow_other`.
- `writeTillFull` and `TestDiskFull` fill a tiny ext4-backed gocryptfs mount and verify both writers get `ENOSPC` without truncating readable data.
- `TestAcl` uses `setfacl`/`getfacl` to verify read/write permission changes for another uid.
- `TestOverlay` mounts overlayfs on directories inside gocryptfs.
- `TestRootForceOwner` checks mkdir, create, and socket mknod as a forced owner.

## Control Flow
Tests skip unless root, then either use the package mount or create nested initialized filesystems. Credential tests run callbacks as synthetic users. Disk-full tests create a loop ext4 image, mount gocryptfs inside it, and concurrently write until no space remains.

## State And Persistence
State includes process credentials, supplementary groups, temp ext4 images, nested FUSE mounts, ACL xattrs, overlay mounts, and test files. Cleanup uses defers for unmounts and image removal.

## Dependencies And Integration Points
Depends on Linux syscalls, `internal/syscallcompat`, `mkfs.ext4`, `mount`, `setfacl`, `getfacl`, overlayfs support, and the shared root harness.

## Risks And Edge Cases
`asUser` must reset saved ids as well as effective ids to avoid later FUSE permission failures. Disk-full and overlay tests are host-kernel and privilege sensitive.

## Test Signals
Signals include successful group-authorized operations, both concurrent writers receiving `ENOSPC` with readable full contents, ACL read/write transitions matching expectations, successful overlay mount, and force-owner operations succeeding as uid/gid 1234.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/root_test/root_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/sharedstorage/sharedstorage_test.go -->
# sources/security-integrity/gocryptfs/tests/sharedstorage/sharedstorage_test.go

## Purpose
Tests behavior when the same gocryptfs cipherdir is mounted twice, with and without the `-sharedstorage` cache-coherency option.

## Important APIs, Types, And Functions
- `TestMain` runs the whole package once without and once with `-sharedstorage`.
- `testCase` stores cipherdir and two mountpoints.
- `newTestCase`, `cleanup`, and `mountSharedstorage` manage paired mounts.
- `TestDirUnlink` replaces a directory with a file through one mount and unlinks through the other.
- `TestStaleHardlinks` creates and deletes hardlinks across mounts, then opens the surviving link.

## Control Flow
Each test creates a fresh initialized cipherdir and mounts it twice. Mutations through one mount intentionally stale the other mount's cache; the test either expects immediate success under `-sharedstorage` or success after the entry timeout expires.

## State And Persistence
State is a temporary cipherdir with two live FUSE mounts. `waitForExpire` reflects the one-second kernel entry timeout plus margin.

## Dependencies And Integration Points
Depends on `golang.org/x/sys/unix` and `test_helpers` mount lifecycle helpers.

## Risks And Edge Cases
Without `-sharedstorage`, the tests encode timeout-based eventual correctness, which can be timing-sensitive. With `-sharedstorage`, stale-cache failures are fatal immediately.

## Test Signals
Signals are successful cross-mount unlink/open behavior in sharedstorage mode and after cache expiration in normal mode.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/sharedstorage/sharedstorage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/sshfs-benchmark.bash -->
# sources/security-integrity/gocryptfs/tests/sshfs-benchmark.bash

## Purpose
Ad hoc benchmark comparing basic operations on raw sshfs versus gocryptfs layered on sshfs.

## Important APIs, Types, And Functions
- `prepare_mounts` mounts `$HOST:/tmp` via sshfs, creates a remote-backed cipherdir, initializes gocryptfs, and mounts it locally.
- `etime` wraps `/usr/bin/time -f %e` and prints aligned elapsed seconds.
- `cleanup` unmounts both FUSE layers and removes temp dirs.

## Control Flow
The script takes a host argument, prepares sshfs and gocryptfs-on-sshfs mounts, then times `git init`, `rsync`, recursive remove, mkdir/rmdir, touch, and rm on both paths.

## State And Persistence
Creates local temp dirs, a remote temp dir under sshfs, and two FUSE mounts. Cleanup is registered after sshfs mount setup.

## Dependencies And Integration Points
Depends on sshfs, gocryptfs, git, rsync, `/usr/bin/time`, fusermount, and passwordless or interactive SSH access to the host.

## Risks And Edge Cases
The script assumes `$1` is present and uses unquoted generated `seq` arguments intentionally. Network latency and remote `/tmp` filesystem dominate results.

## Test Signals
Output table of elapsed seconds is the benchmark signal; any command failure exits due to `set -eu`.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/sshfs-benchmark.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/extractloop.bash -->
# sources/security-integrity/gocryptfs/tests/stress_tests/extractloop.bash

## Purpose
Long-running stress loop that repeatedly extracts and deletes the Linux 3.0 tree through gocryptfs, EncFS, or go-fuse loopback while optionally recording memory and iteration time.

## Important APIs, Types, And Functions
- `check_md5sums` verifies extracted contents when `md5sum` is available.
- `cleanup_exit` tears down mounts and, for loopback, triggers memory profile output.
- `loop` performs extract, checksum, delete, and CSV metric append for one worker.
- `memprof` periodically signals loopback for memory profiles.

## Control Flow
The script prepares a temp cipherdir and mountpoint, selects filesystem mode from arguments, mounts it, symlinks the CSV to `/tmp/extractloop.csv`, then launches two infinite loop workers. Each worker extracts the tarball, verifies checksums, removes the tree, records RSS and duration if possible, and repeats.

## State And Persistence
Persistent runtime artifacts include temp backing and mount dirs, CSV metrics, and optional `/tmp/loopback*.memprof` files. Cleanup removes the backing tree and mountpoint.

## Dependencies And Integration Points
Depends on Linux tarball download helper, tar, md5sum or macOS fallback, gocryptfs/encfs/loopback binaries, `/proc` for RSS, and `fuse-unmount.bash`.

## Risks And Edge Cases
It is intentionally unbounded and creates huge file churn. Running on non-Linux skips checksum if `md5sum` is absent, reducing integrity signal.

## Test Signals
Continued iterations with stable checksum validation and bounded RSS in the CSV are the main signals.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/extractloop.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/extractloop_plot_csv.m -->
# sources/security-integrity/gocryptfs/tests/stress_tests/extractloop_plot_csv.m

## Purpose
Octave plotting helper for visualizing `extractloop.bash` CSV output.

## Important APIs, Types, And Functions
- `csvread('/tmp/extractloop.csv')` loads runtime, RSS, and iteration duration rows.
- `plotyy` renders RSS in MiB and iteration time in seconds against runtime.
- Axes labels, line styles, grid, and a blocking `input` keep the figure visible.

## Control Flow
The script reads the CSV, opens a large figure, plots memory and duration on separate y axes, formats markers, draws immediately, and waits for Enter before exit.

## State And Persistence
Reads only `/tmp/extractloop.csv`; it writes no files.

## Dependencies And Integration Points
Depends on GNU Octave and the CSV shape produced by `extractloop.bash` as `N,SECONDS,RSS,delta`.

## Risks And Edge Cases
No validation is performed for missing, empty, or malformed CSV data. `plotyy` behavior can differ across Octave versions.

## Test Signals
A visible plot with RSS and iteration-time trends is the intended signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/extractloop_plot_csv.m -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/fsstress-encfs.bash -->
# sources/security-integrity/gocryptfs/tests/stress_tests/fsstress-encfs.bash

## Purpose
Runs the shared fsstress loop in `EncFS` mode to repeatedly exercise high-concurrency filesystem mutations against a mounted filesystem until an error occurs.

## Important APIs, Types, And Functions
- `TMPDIR` defaults to `/var/tmp`; `DEBUG` toggles FUSE or loopback debug mode.
- `FSSTRESS=/var/lib/xfstests/ltp/fsstress` is required.
- Mode selection is inferred from the script basename and chooses gocryptfs, EncFS, or go-fuse loopback mounting.

## Control Flow
The script creates a backing directory and mountpoint, cleans stale mounts matching its temp prefix, mounts the selected filesystem, waits for a FUSE mount entry, and loops through three fsstress profiles followed by recursive cleanup of the mount contents.

## State And Persistence
It creates and removes temporary backing and mount directories, keeps the selected filesystem mounted for the process lifetime, and may leave artifacts if the trap is bypassed by abrupt termination.

## Dependencies And Integration Points
Depends on xfstests `fsstress`, Go/GOPATH for gocryptfs or loopback modes, EncFS for EncFS mode, `/proc/self/mounts`, and the shared `fuse-unmount.bash` helper.

## Risks And Edge Cases
The loop is intentionally unbounded and destructive inside its temp tree. The cleanup trap uses `kill %1`, so job-control assumptions matter. Running with `DEBUG=1` can generate large logs.

## Test Signals
The only pass signal is continued iteration. Any fsstress, rm, mount, or unmount failure exits because `set -eu` is active.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/fsstress-encfs.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/fsstress-gocryptfs.bash -->
# sources/security-integrity/gocryptfs/tests/stress_tests/fsstress-gocryptfs.bash

## Purpose
Runs the shared fsstress loop in `gocryptfs` mode to repeatedly exercise high-concurrency filesystem mutations against a mounted filesystem until an error occurs.

## Important APIs, Types, And Functions
- `TMPDIR` defaults to `/var/tmp`; `DEBUG` toggles FUSE or loopback debug mode.
- `FSSTRESS=/var/lib/xfstests/ltp/fsstress` is required.
- Mode selection is inferred from the script basename and chooses gocryptfs, EncFS, or go-fuse loopback mounting.

## Control Flow
The script creates a backing directory and mountpoint, cleans stale mounts matching its temp prefix, mounts the selected filesystem, waits for a FUSE mount entry, and loops through three fsstress profiles followed by recursive cleanup of the mount contents.

## State And Persistence
It creates and removes temporary backing and mount directories, keeps the selected filesystem mounted for the process lifetime, and may leave artifacts if the trap is bypassed by abrupt termination.

## Dependencies And Integration Points
Depends on xfstests `fsstress`, Go/GOPATH for gocryptfs or loopback modes, EncFS for EncFS mode, `/proc/self/mounts`, and the shared `fuse-unmount.bash` helper.

## Risks And Edge Cases
The loop is intentionally unbounded and destructive inside its temp tree. The cleanup trap uses `kill %1`, so job-control assumptions matter. Running with `DEBUG=1` can generate large logs.

## Test Signals
The only pass signal is continued iteration. Any fsstress, rm, mount, or unmount failure exits because `set -eu` is active.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/fsstress-gocryptfs.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/fsstress-loopback.bash -->
# sources/security-integrity/gocryptfs/tests/stress_tests/fsstress-loopback.bash

## Purpose
Runs the shared fsstress loop in `go-fuse loopback` mode to repeatedly exercise high-concurrency filesystem mutations against a mounted filesystem until an error occurs.

## Important APIs, Types, And Functions
- `TMPDIR` defaults to `/var/tmp`; `DEBUG` toggles FUSE or loopback debug mode.
- `FSSTRESS=/var/lib/xfstests/ltp/fsstress` is required.
- Mode selection is inferred from the script basename and chooses gocryptfs, EncFS, or go-fuse loopback mounting.

## Control Flow
The script creates a backing directory and mountpoint, cleans stale mounts matching its temp prefix, mounts the selected filesystem, waits for a FUSE mount entry, and loops through three fsstress profiles followed by recursive cleanup of the mount contents.

## State And Persistence
It creates and removes temporary backing and mount directories, keeps the selected filesystem mounted for the process lifetime, and may leave artifacts if the trap is bypassed by abrupt termination.

## Dependencies And Integration Points
Depends on xfstests `fsstress`, Go/GOPATH for gocryptfs or loopback modes, EncFS for EncFS mode, `/proc/self/mounts`, and the shared `fuse-unmount.bash` helper.

## Risks And Edge Cases
The loop is intentionally unbounded and destructive inside its temp tree. The cleanup trap uses `kill %1`, so job-control assumptions matter. Running with `DEBUG=1` can generate large logs.

## Test Signals
The only pass signal is continued iteration. Any fsstress, rm, mount, or unmount failure exits because `set -eu` is active.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/fsstress-loopback.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/fsstress.collect-crashes.sh -->
# sources/security-integrity/gocryptfs/tests/stress_tests/fsstress.collect-crashes.sh

## Purpose
Operator helper for repeatedly running `fsstress-loopback.bash` on an ext4 ramdisk and collecting bounded crash/debug logs.

## Important APIs, Types, And Functions
- Sets working directory to a developer GOPATH checkout path.
- `TMPDIR=/mnt/ext4-ramdisk` is required and write-tested.
- Loops up to 1000 times, capturing the last 1,000,000 lines of DEBUG fsstress output into timestamped logs.

## Control Flow
The script creates a log directory under `/tmp/$$`, removes old fsstress temp dirs, runs the loopback stress script with `DEBUG=1`, and pipes output through `tail` to cap each log file.

## State And Persistence
Writes logs under `/tmp/<pid>` and deletes fsstress temp dirs under the ramdisk before each run.

## Dependencies And Integration Points
Depends on a specific checkout location, writable ext4 ramdisk, and the fsstress loopback script.

## Risks And Edge Cases
The hard-coded path makes it non-portable. Each log can still be large, and the script does not stop after a successful no-crash run unless the child exits.

## Test Signals
Signals are collected logs for postmortem analysis; skipped existing log names avoid overwriting prior captures.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/fsstress.collect-crashes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/parallel_cp.sh -->
# sources/security-integrity/gocryptfs/tests/stress_tests/parallel_cp.sh

## Purpose
Reproducer for a historical parallel copy race where concurrent `cp` operations could fail with missing destination directories under gocryptfs.

## Important APIs, Types, And Functions
- Initializes a gocryptfs filesystem under `$TMPDIR` using `$GOPATH/bin/gocryptfs`.
- Creates 778 origin files with `dd`.
- Launches 100 background subshells that create subdirectories and copy the same origin file list.

## Control Flow
After mounting, the script precomputes `ORIGIN_FILES=origin/*`, then starts many concurrent mkdir/cp jobs. A final `wait` collects all background failures before cleanup.

## State And Persistence
Creates a temporary cipherdir and mountpoint, many files under the mount, and removes both on EXIT.

## Dependencies And Integration Points
Depends on Go GOPATH install of gocryptfs, dd, cp, seq, and the shared unmount helper.

## Risks And Edge Cases
It uses unquoted `$ORIGIN_FILES` intentionally for shell expansion captured once. The test is load-sensitive and may need cache-dropping pressure to reproduce old failures.

## Test Signals
A pass is all background copies completing and the script printing runtime without any `cp` or mkdir failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/parallel_cp.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/pingpong-rsync.bash -->
# sources/security-integrity/gocryptfs/tests/stress_tests/pingpong-rsync.bash

## Purpose
Runs the shared ping-pong stress script in rsync mode, moving the Linux 3.0 tree between two gocryptfs mounts with `rsync --remove-source-files` and verifying MD5s each hop.

## Important APIs, Types, And Functions
- `MYNAME` basename selects rsync behavior inside `move_and_md5`.
- `move_and_md5` uses `rsync -a --remove-source-files`, deletes empty source dirs, and runs `md5sum --status -c`.

## Control Flow
The script initializes two independent gocryptfs cipherdirs, mounts them, extracts the tarball into the ping mount, then loops moving the tree ping-to-pong and pong-to-ping with checksum verification.

## State And Persistence
Creates two temp cipherdirs and mountpoints in `/tmp`, cleaned by an EXIT trap that tolerates already-unmounted FUSE mounts.

## Dependencies And Integration Points
Depends on rsync, gocryptfs, md5sum, tarball fixture, and `fuse-unmount.bash`.

## Risks And Edge Cases
Infinite loop by design; rsync semantics differ from `mv` and exercise remove-source and directory cleanup paths. Any leftover source directory is fatal.

## Test Signals
Continued numbered iterations with successful MD5 checks are the signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/pingpong-rsync.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/pingpong.bash -->
# sources/security-integrity/gocryptfs/tests/stress_tests/pingpong.bash

## Purpose
Runs an infinite move-and-verify stress test that shuttles the Linux 3.0 tree between two gocryptfs mounts using plain `mv`.

## Important APIs, Types, And Functions
- `move_and_md5` chooses plain `mv` when the basename is not `pingpong-rsync.bash`.
- The loop verifies the moved tree against `linux-3.0.md5sums` after each hop.

## Control Flow
The script prepares two independent gocryptfs mounts, extracts the source tree once, then alternates moving it between mounts and validating checksums.

## State And Persistence
State is two temp cipherdirs and mountpoints under `/tmp`, removed by the EXIT trap.

## Dependencies And Integration Points
Depends on gocryptfs, tar, md5sum, renice, and the shared unmount helper.

## Risks And Edge Cases
It is unbounded and intentionally churns large directory trees. Plain `mv` exercises rename-heavy behavior rather than rsync copy/unlink behavior.

## Test Signals
A pass is continued iteration with no checksum mismatch and no remaining source tree after each move.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/stress_tests/pingpong.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/symlink_race/main.go -->
# sources/security-integrity/gocryptfs/tests/symlink_race/main.go

## Purpose
Standalone race reproducer that alternates a path between symlink and regular file while another goroutine opens and writes it, looking for unsafe symlink-following behavior.

## Important APIs, Types, And Functions
- `renameLoop` repeatedly creates a symlink to `/root/chmod_me`, renames it into place, creates a regular temp file, and renames that into place.
- `openLoop` repeatedly opens `symlink_race.test_file` with `O_RDWR`, writes `owned`, reads back, and exits nonzero if content appears.
- `main` starts `openLoop` and runs `renameLoop` forever.

## Control Flow
Two loops race on the same filename. One loop swaps file type through atomic renames; the other tries to open and modify the path, which can reveal time-of-check/time-of-use issues.

## State And Persistence
Creates and mutates `symlink_race.test_file` and `.tmp` in the current working directory indefinitely.

## Dependencies And Integration Points
Depends only on Go `os`, `syscall`, and filesystem rename/open semantics. It is intended to run inside a target mount.

## Risks And Edge Cases
It is destructive in the current directory and infinite. The target `/root/chmod_me` is hard-coded to expose privilege-sensitive symlink following if run with elevated access.

## Test Signals
The failure signal is printing unexpected content and exiting with status 1; otherwise it prints progress dots and transient errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/symlink_race/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/test_helpers/helpers.go -->
# sources/security-integrity/gocryptfs/tests/test_helpers/helpers.go

## Purpose
Shared Go test utility package for gocryptfs integration tests. It owns temp directory setup, filesystem initialization, hashing, size checks, common operation tests, control-socket queries, disk-usage helpers, and command exit-code decoding.

## Important APIs, Types, And Functions
- `doInit` initializes `TmpDir`, `DefaultPlainDir`, `DefaultCipherDir`, `MountInfo`, and `X255`.
- `ResetTmpDir` removes prior mounts/content and recreates default dirs, optionally writing `gocryptfs.diriv`.
- `InitFS` runs `../../gocryptfs -init` with fast scrypt settings.
- `Md5fn`, `Md5hex`, `VerifySize`, `VerifyExistence`, and `Du` provide assertions.
- `TestMkdirRmdir` and `TestRename` are reusable behavior checks.
- `QueryCtlSock` wraps `ctlsock.New` and query error handling.
- `ExtractCmdExitCode` normalizes exec and path errors to integer codes.

## Control Flow
Package init creates a user-specific parent temp dir and unique test temp dir. Tests call reset/init helpers, then mount helpers from the companion file. Assertion helpers combine high-level reads with low-level stat/fstat or directory enumeration to catch FUSE inconsistencies.

## State And Persistence
Global state includes temp paths and `MountInfo`. `ResetTmpDir` can unmount busy child dirs before deleting them, making it both setup and cleanup.

## Dependencies And Integration Points
Depends on gocryptfs internal packages `nametransform` and `syscallcompat`, the `ctlsock` package, external gocryptfs binary, and OS temp/filesystem behavior.

## Risks And Edge Cases
Because helpers panic on unexpected cleanup errors, stale mounts can fail unrelated tests. MD5 helpers read whole files into memory and are unsuitable for very large data.

## Test Signals
Signals are consumed by callers: consistent size/read/stat/fstat, consistent existence across stat/open/readdir, successful control socket responses, and reusable operation assertions.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/test_helpers/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/test_helpers/mount_unmount.go -->
# sources/security-integrity/gocryptfs/tests/test_helpers/mount_unmount.go

## Purpose
Shared mount lifecycle utilities for gocryptfs tests. It starts the gocryptfs process, waits for readiness, records process file descriptors, unmounts with retries, and detects fd leaks.

## Important APIs, Types, And Functions
- `Mount` builds gocryptfs arguments, creates the mountpoint, starts `../../gocryptfs`, waits for SIGUSR1 readiness or process exit, and records mount info.
- `MountOrExit` and `MountOrFatal` adapt mount errors to process exit or test failure.
- `UnmountPanic` and `UnmountErr` run the FUSE unmount wrapper with retries and fd-leak checks.
- `ListFds` enumerates `/proc/<pid>/fd` or `/dev/fd`, filtering runtime pipes and eventpoll fds.

## Control Flow
Mounting starts gocryptfs foreground with quiet/no-syslog flags, Linux `-wpanic`, optional FUSE debug, and caller args. Unmounting waits for asynchronous close operations, compares fd counts allowing the frontend dir cache, then retries unmount up to ten times.

## State And Persistence
State is stored in global `MountInfo` keyed by mountpoint, containing the gocryptfs pid and baseline fd list.

## Dependencies And Integration Points
Depends on the gocryptfs binary, signal delivery, the `fuse-unmount.bash` wrapper, `/proc` for child fd inspection on Linux, and lsof for panic diagnostics.

## Risks And Edge Cases
Readiness relies on `-notifypid` SIGUSR1 within two seconds. FD leak checks allow `maxCacheFds` and filter runtime-created descriptors, so some leaks can be masked and some platform differences skipped.

## Test Signals
Signals are successful mount readiness, clean unmount, stable fd counts within cache allowance, and useful diagnostics on busy mounts.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/test_helpers/mount_unmount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/xattr/xattr_fd_test.go -->
# sources/security-integrity/gocryptfs/tests/xattr/xattr_fd_test.go

## Purpose
Linux-only tests for file-descriptor xattr syscalls through a gocryptfs mount.

## Important APIs, Types, And Functions
- `TestFdXattr` opens a file, uses `Flistxattr`, `Fsetxattr`, `Fgetxattr`, and `Fremovexattr`, and verifies list sizes and values.

## Control Flow
The test creates a file in the mounted plaintext dir, opens it once, performs fd-based xattr operations, and checks the xattr list before set, after set, and after removal.

## State And Persistence
State is one temporary file and one `user.foo` xattr, removed by test cleanup through temp-dir teardown.

## Dependencies And Integration Points
Depends on Linux fd xattr APIs from `golang.org/x/sys/unix` and the xattr integration package `TestMain` mount.

## Risks And Edge Cases
Darwin is excluded because it lacks these fd APIs. The expected list size includes the NUL terminator from Linux `flistxattr`.

## Test Signals
Pass signals are empty initial/final lists, exact listed name, and exact readback value.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/xattr/xattr_fd_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/xattr/xattr_integration_test.go -->
# sources/security-integrity/gocryptfs/tests/xattr/xattr_integration_test.go

## Purpose
Integration tests for encrypted extended attributes in gocryptfs, covering regular files, FIFOs, directories, empty values, large lists, base64 compatibility, permissions, ACL blobs, and names containing slashes.

## Important APIs, Types, And Functions
- `TestMain` checks xattr support, writes deterministic diriv, mounts with `-zerokey`, and tears down.
- `setGetRmList` and `setGetRmList3` implement list/set/get/remove/list assertions.
- `TestSetGetRmRegularFile`, `TestSetGetRmFifo`, `TestSetGetRmDir`, `TestXattrSetEmpty`, and `TestXattrList` cover basic operations.
- `TestBase64XattrRead` inspects encrypted backing attrs and verifies raw/base64 encrypted value decoding plus broken-data `EIO`.
- `TestList0000File`, `TestSet0200File`, `TestList0000Dir`, `TestSet0200Dir`, `TestAcl`, and `TestSlashInName` cover permissions and special names.

## Control Flow
The package mounts a deterministic encrypted-name filesystem. Tests usually operate through the plaintext mount, while `TestBase64XattrRead` also accesses the cipherdir directly using known encrypted names and attr names.

## State And Persistence
State includes xattrs on test files and directories plus a remount inside `TestBase64XattrRead` with `-wpanic=false` to tolerate intentionally malformed backing values.

## Dependencies And Integration Points
Depends on `github.com/pkg/xattr`, `internal/cryptocore`, deterministic diriv contents, and filesystem xattr/ACL support.

## Risks And Edge Cases
The deterministic encrypted names are tightly coupled to diriv and `-zerokey`. Broken backing xattrs intentionally trigger `EIO`, and ACL behavior depends on system xattr namespace support.

## Test Signals
Signals include exact value round trips, empty-list checks after removal, correct handling of nil values, expected `EIO` on malformed encrypted attr values, and permission-independent list/set behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/tests/xattr/xattr_integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/gocryptfs/version.go -->
# sources/security-integrity/gocryptfs/version.go

## Purpose
Implements gocryptfs version reporting, combining build-time linker variables, Go build-info fallback, feature tags, go-fuse dependency version, build date, race detector status, and target platform.

## Important APIs, Types, And Functions
- `GitVersion`, `GitVersionFuse`, and `BuildDate` are build-time variables with sentinel defaults.
- `init` calls `versionFromBuildInfo` before main code uses version fields.
- `printVersion` formats and prints the user-facing version line.
- `versionFromBuildInfo` reads module build metadata and fills unset version fields.
- `raceDetector` is set by a separate race-build file when compiled with `-race`.

## Control Flow
At startup, build-info fallback runs only for unset linker fields. `printVersion` then derives optional tags such as `without_openssl`, appends `-race` when relevant, and prints program name, gocryptfs version, go-fuse version, build date, Go runtime version, OS, and architecture.

## State And Persistence
State is process-global version variables set either by build scripts or Go module metadata. No persistent files are touched.

## Dependencies And Integration Points
Depends on `runtime/debug.ReadBuildInfo`, `internal/stupidgcm` for OpenSSL tag reporting, and `internal/tlog.ProgramName`.

## Risks And Edge Cases
Fallback build info may be unavailable or `(devel)`, leaving sentinel strings if build scripts did not inject values. Replacement modules with empty replacement versions can affect go-fuse version output.

## Test Signals
Test signals are indirect: CLI `--version` output should include expected build/version metadata and tags for the binary build mode.
<!-- END_FILE_RESEARCH: sources/security-integrity/gocryptfs/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/.github/workflows/ci.yml -->
# sources/security-integrity/ima-evm-utils/.github/workflows/ci.yml

## Purpose
GitHub Actions workflow for ima-evm-utils distro CI. It runs checkpatch review, builds/caches a UML integrity kernel, and tests a large distro/compiler/TSS matrix in privileged containers.

## Important APIs, Types, And Functions
- `review` job checks generated patch files with `scripts/checkpatch.pl`.
- `build` job finds the latest linux-integrity commit, caches a UML kernel and signing key, and compiles with merged kernel configs.
- `job` matrix covers Debian i386/cross, Alpine, openSUSE, Ubuntu, Fedora, CentOS Stream, Debian testing/stable, and ALT.
- Install steps dispatch to `ci/$INSTALL[.$VARIANT].sh`; compile step calls `./build.sh` with matrix environment.

## Control Flow
Push or pull request events first run patch review. The build job prepares kernel artifacts keyed by Linux SHA and kernel config hashes. The main matrix runs in privileged containers, installs distro deps, optionally builds OpenSSL/TSS/swtpm, retrieves UML artifacts for kernel tests, prints compiler version, and builds/tests the project.

## State And Persistence
Persistent CI state is through Actions caches for `linux` and `signing_key.pem`. The workflow also mutates privileged containers with package installs and mounts.

## Dependencies And Integration Points
Depends on GitHub Actions, container images, Linux integrity git remote variables, kernel config files, package-manager scripts, tests helper installers, and `build.sh`.

## Risks And Edge Cases
Privileged containers and kernel caches are broad blast-radius CI choices. Empty optional env vars are tested with shell `[ "$VARIANT" ]` style, so shell compatibility and unset variables matter.

## Test Signals
Signals are checkpatch success, cache/build success for UML kernel, and green matrix rows through `make check` or accepted skip code handling in `build.sh`.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/.github/workflows/ci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/.travis.yml -->
# sources/security-integrity/ima-evm-utils/.travis.yml

## Purpose
Legacy Travis CI configuration that runs ima-evm-utils across distro/compiler/TSS combinations inside Docker or Podman containers.

## Important APIs, Types, And Functions
- `matrix.include` mirrors native, i386, cross-compile, musl, glibc, and ALT/Fedora/CentOS/OpenSUSE/Ubuntu/Debian rows.
- `before_install` optionally installs Podman support, creates a Dockerfile, and builds an image from the repository.
- `script` derives the distro install script, runs variant and distro CI scripts, optional OpenSSL/TSS/swtpm setup, and `build.sh`.

## Control Flow
Travis builds a throwaway container image containing the repository, then runs all dependency installation and build/test commands inside that image with environment-driven script selection.

## State And Persistence
State exists in Travis service containers/images. The generated Dockerfile in the worktree is transient during CI.

## Dependencies And Integration Points
Depends on Travis focal, docker or podman, distro images, the same `ci/*.sh` scripts and `build.sh` used by GitHub Actions.

## Risks And Edge Cases
This is legacy and can drift from GitHub Actions. Some distro tags differ, such as older Ubuntu xenial/resolute style rows.

## Test Signals
Pass signal is each configured container completing dependency install, optional helper builds, and `./build.sh`.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/.travis.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/Makefile.am -->
# sources/security-integrity/ima-evm-utils/Makefile.am

## Purpose
Top-level Automake file for ima-evm-utils. It coordinates subdirectories, documentation distribution, tarball/RPM targets, manpage generation, and shellcheck delegation.

## Important APIs, Types, And Functions
- `SUBDIRS = src tests` plus optional `doc` when `HAVE_PANDOC` is true.
- `doc_DATA` distributes key-generation example scripts.
- `$(tarname)`, `tar`, and `rpm` package release artifacts.
- `evmctl.1.html`, `evmctl.1`, `rmman`, and `doc` build documentation when docbook XSL is available.
- `shellcheck` delegates to `tests`.

## Control Flow
Automake expands conditionals from `configure.ac`, then recursive make builds source, tests, and optional docs. Release targets use `git archive` tagged by package version and rpmbuild.

## State And Persistence
Generated artifacts include tarballs, manpages, HTML, temporary XSL, RPM build outputs, and cleaned `CLEANFILES`.

## Dependencies And Integration Points
Depends on Autotools variables, pandoc/asciidoc/xsltproc/docbook availability, Git tags, and RPM build tree layout.

## Risks And Edge Cases
Release packaging assumes tag `v$(PACKAGE_VERSION)` and `$HOME/rpmbuild/SOURCES`. Missing docbook XSL disables manpage distribution.

## Test Signals
Signals are successful recursive make, generated docs when enabled, and functioning `make shellcheck`, `make tar`, or `make rpm` targets.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/autogen.sh -->
# sources/security-integrity/ima-evm-utils/autogen.sh

## Purpose
Minimal bootstrap script for generating Autotools build files.

## Important APIs, Types, And Functions
- `set -e` exits on bootstrap failure.
- `autoreconf -i` installs missing helper files and regenerates configure machinery.

## Control Flow
The script simply invokes `autoreconf -i` from the caller's current checkout context.

## State And Persistence
Writes generated Autoconf/Automake/Libtool files such as `configure`, `Makefile.in`, `aclocal.m4`, and helper scripts.

## Dependencies And Integration Points
Depends on autoconf, automake, libtool, and m4 macro availability.

## Risks And Edge Cases
It does not enforce running from the repository root; callers normally invoke it from `build.sh` after `cd dirname $0`.

## Test Signals
Success is a generated `configure` script usable by the subsequent build.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/autogen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/build-static.sh -->
# sources/security-integrity/ima-evm-utils/build-static.sh

## Purpose
One-command static build helper for the `evmctl` binary.

## Important APIs, Types, And Functions
- Runs `gcc -static` over `src/evmctl.c` and `src/libimaevm.c`.
- Forces inclusion of `config.h`.
- Links against `crypto`, `keyutils`, and `dl`.

## Control Flow
The script directly invokes gcc without running configure or make, assuming generated config and dependencies are already present.

## State And Persistence
Writes `evmctl.static` in the current directory.

## Dependencies And Integration Points
Depends on static libc and static/linkable OpenSSL and keyutils libraries.

## Risks And Edge Cases
By bypassing Automake, it can miss conditional source selection or compiler flags from the normal build. Static linking availability varies by distro.

## Test Signals
The signal is a successfully linked `evmctl.static` executable.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/build-static.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/build.sh -->
# sources/security-integrity/ima-evm-utils/build.sh

## Purpose
Shared CI build-and-test driver for ima-evm-utils. It configures compiler flags, optional OpenSSL 3 build paths, native/i386/cross variants, kernel-test enablement, install prefix, and test log handling.

## Important APIs, Types, And Functions
- `title` prints section headers.
- `log_exit` dumps logs and exits with normalized status.
- `CC`, `CFLAGS`, `PREFIX`, `COMPILE_SSL`, `VARIANT`, `TESTGROUP`, and `TST_*` environment variables control behavior.
- Runs `./autogen.sh`, `./configure`, `make -j$(nproc)`, `make install`, `openssl list -providers`, and `make check`.

## Control Flow
Under CI it enables shell tracing, redirects stderr to stdout, and mounts securityfs. It sets paths, handles OpenSSL override, chooses variant flags, disables kernel tests unless requested, builds, installs, skips checks for cross-compile, and interprets test exit 77 as warning/skip.

## State And Persistence
Mutates the source tree with generated Autotools files and build outputs, installs into `$PREFIX`, and may mount `/sys/kernel/security` in CI.

## Dependencies And Integration Points
Depends on package scripts having installed build dependencies, optional OpenSSL under `/opt/openssl3`, and tests producing standard Automake logs.

## Risks And Edge Cases
Unset variables are used under `/bin/sh`; CI usually supplies them, but local runs may need explicit defaults. Mounting securityfs requires privileges.

## Test Signals
Signals are successful configure/build/install, provider listing, green `make check`, accepted skip handling, and `tests/make check_logs` on success.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/alpine.sh -->
# sources/security-integrity/ima-evm-utils/ci/alpine.sh

## Purpose
Installs the ima-evm-utils build and test dependencies inside a Alpine/musl CI container. It normalizes CI-provided compiler and TPM/TSS selections into distro package names before the shared `build.sh` runs.

## Important APIs, Types, And Functions
- `CC` is mandatory and is expanded to include `gcc` when helper tools require it.
- `TSS` is translated to distro-specific IBM TSS or tpm2-tss development packages.
- `apk` installs compiler, autotools, OpenSSL, keyutils, xattr/attr, docbook/asciidoc, TPM simulator, pkcs11, and filesystem utility packages.

## Control Flow
The script validates required environment, rewrites `TSS`, refreshes package metadata when needed, installs a broad dependency set, and optionally runs helper installers for components that are missing or not packaged.

## State And Persistence
It mutates the container package database and may install files under `/usr`, `/usr/local`, or helper-script defaults. No repository source files are modified.

## Dependencies And Integration Points
Integrated by GitHub Actions and legacy Travis through the derived `ci/alpine.sh` launcher. It feeds the later autoconf, make, and test phases in `build.sh`.

## Risks And Edge Cases
Package names are distro-sensitive; stale package names, missing optional repos, or unavailable `tpm2-tss-dev or source-built IBM TSS` packages can fail CI before source compilation. Several optional installs are deliberately best-effort, so coverage can vary by image.

## Test Signals
A successful run is signaled indirectly by the next CI stage reaching `./configure`, `make`, and `make check` on Alpine/musl.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/alpine.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/alt.sh -->
# sources/security-integrity/ima-evm-utils/ci/alt.sh

## Purpose
Installs the ima-evm-utils build and test dependencies inside a ALT Linux CI container. It normalizes CI-provided compiler and TPM/TSS selections into distro package names before the shared `build.sh` runs.

## Important APIs, Types, And Functions
- `CC` is mandatory and is expanded to include `gcc` when helper tools require it.
- `TSS` is translated to distro-specific IBM TSS or tpm2-tss development packages.
- `apt-get` installs compiler, autotools, OpenSSL, keyutils, xattr/attr, docbook/asciidoc, TPM simulator, pkcs11, and filesystem utility packages.

## Control Flow
The script validates required environment, rewrites `TSS`, refreshes package metadata when needed, installs a broad dependency set, and optionally runs helper installers for components that are missing or not packaged.

## State And Persistence
It mutates the container package database and may install files under `/usr`, `/usr/local`, or helper-script defaults. No repository source files are modified.

## Dependencies And Integration Points
Integrated by GitHub Actions and legacy Travis through the derived `ci/alt.sh` launcher. It feeds the later autoconf, make, and test phases in `build.sh`.

## Risks And Edge Cases
Package names are distro-sensitive; stale package names, missing optional repos, or unavailable `ALT-provided TSS package` packages can fail CI before source compilation. Several optional installs are deliberately best-effort, so coverage can vary by image.

## Test Signals
A successful run is signaled indirectly by the next CI stage reaching `./configure`, `make`, and `make check` on ALT Linux.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/alt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/centos.sh -->
# sources/security-integrity/ima-evm-utils/ci/centos.sh

## Purpose
Installs the ima-evm-utils build and test dependencies inside a CentOS/Fedora-family CI container. It normalizes CI-provided compiler and TPM/TSS selections into distro package names before the shared `build.sh` runs.

## Important APIs, Types, And Functions
- `CC` is mandatory and is expanded to include `gcc` when helper tools require it.
- `TSS` is translated to distro-specific IBM TSS or tpm2-tss development packages.
- `yum` installs compiler, autotools, OpenSSL, keyutils, xattr/attr, docbook/asciidoc, TPM simulator, pkcs11, and filesystem utility packages.

## Control Flow
The script validates required environment, rewrites `TSS`, refreshes package metadata when needed, installs a broad dependency set, and optionally runs helper installers for components that are missing or not packaged.

## State And Persistence
It mutates the container package database and may install files under `/usr`, `/usr/local`, or helper-script defaults. No repository source files are modified.

## Dependencies And Integration Points
Integrated by GitHub Actions and legacy Travis through the derived `ci/centos.sh` launcher. It feeds the later autoconf, make, and test phases in `build.sh`.

## Risks And Edge Cases
Package names are distro-sensitive; stale package names, missing optional repos, or unavailable `tss2-devel or tpm2-tss-devel` packages can fail CI before source compilation. Several optional installs are deliberately best-effort, so coverage can vary by image.

## Test Signals
A successful run is signaled indirectly by the next CI stage reaching `./configure`, `make`, and `make check` on CentOS/Fedora-family.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/centos.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/debian.cross-compile.sh -->
# sources/security-integrity/ima-evm-utils/ci/debian.cross-compile.sh

## Purpose
Variant setup script for Debian cross-compilation CI rows.

## Important APIs, Types, And Functions
- `ARCH` is mandatory and mapped to `aarch64`, `powerpc64le`, or `s390x` gcc triplets.
- `dpkg --add-architecture $ARCH` enables target packages.
- Installs target gcc, target libc headers, `dpkg-dev`, and `libssl-dev`.

## Control Flow
The script validates the requested architecture, adds it as a Debian foreign architecture, updates apt metadata, and installs cross toolchain pieces needed before the generic Debian dependency script and `build.sh` run.

## State And Persistence
Mutates dpkg architecture state and apt package database in the CI container.

## Dependencies And Integration Points
Integrated by CI when `VARIANT=cross-compile`; `build.sh` later derives `--host` from `CC`.

## Risks And Edge Cases
Only arm64, ppc64el, and s390x are supported. Other ARCH values fail immediately.

## Test Signals
Pass signal is availability of the cross compiler and target headers for configure.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/debian.cross-compile.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/debian.i386.sh -->
# sources/security-integrity/ima-evm-utils/ci/debian.i386.sh

## Purpose
Variant setup script for Debian i386 CI builds.

## Important APIs, Types, And Functions
- Adds the `i386` architecture.
- Installs `linux-libc-dev:i386`, `gcc-multilib`, and `pkg-config:i386`.

## Control Flow
The script enables i386 package resolution and installs the minimal multilib support needed before the generic Debian script installs architecture-qualified libraries.

## State And Persistence
Mutates dpkg architecture state and apt package database.

## Dependencies And Integration Points
Integrated by CI when `VARIANT=i386`; `build.sh` later adds `-m32` flags and i386 pkg-config path.

## Risks And Edge Cases
Assumes Debian repositories provide i386 packages for the selected image.

## Test Signals
Pass signal is successful installation of multilib compiler/pkg-config support.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/debian.i386.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/debian.sh -->
# sources/security-integrity/ima-evm-utils/ci/debian.sh

## Purpose
Installs the ima-evm-utils build and test dependencies inside a Debian CI container. It normalizes CI-provided compiler and TPM/TSS selections into distro package names before the shared `build.sh` runs.

## Important APIs, Types, And Functions
- `CC` is mandatory and is expanded to include `gcc` when helper tools require it.
- `TSS` is translated to distro-specific IBM TSS or tpm2-tss development packages.
- `apt` installs compiler, autotools, OpenSSL, keyutils, xattr/attr, docbook/asciidoc, TPM simulator, pkcs11, and filesystem utility packages.

## Control Flow
The script validates required environment, rewrites `TSS`, refreshes package metadata when needed, installs a broad dependency set, and optionally runs helper installers for components that are missing or not packaged.

## State And Persistence
It mutates the container package database and may install files under `/usr`, `/usr/local`, or helper-script defaults. No repository source files are modified.

## Dependencies And Integration Points
Integrated by GitHub Actions and legacy Travis through the derived `ci/debian.sh` launcher. It feeds the later autoconf, make, and test phases in `build.sh`.

## Risks And Edge Cases
Package names are distro-sensitive; stale package names, missing optional repos, or unavailable `libtss-dev or libtss2-dev` packages can fail CI before source compilation. Several optional installs are deliberately best-effort, so coverage can vary by image.

## Test Signals
A successful run is signaled indirectly by the next CI stage reaching `./configure`, `make`, and `make check` on Debian.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/debian.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/fedora.sh -->
# sources/security-integrity/ima-evm-utils/ci/fedora.sh

## Purpose
Installs the ima-evm-utils build and test dependencies inside a Fedora/CentOS-family CI container. It normalizes CI-provided compiler and TPM/TSS selections into distro package names before the shared `build.sh` runs.

## Important APIs, Types, And Functions
- `CC` is mandatory and is expanded to include `gcc` when helper tools require it.
- `TSS` is translated to distro-specific IBM TSS or tpm2-tss development packages.
- `yum` installs compiler, autotools, OpenSSL, keyutils, xattr/attr, docbook/asciidoc, TPM simulator, pkcs11, and filesystem utility packages.

## Control Flow
The script validates required environment, rewrites `TSS`, refreshes package metadata when needed, installs a broad dependency set, and optionally runs helper installers for components that are missing or not packaged.

## State And Persistence
It mutates the container package database and may install files under `/usr`, `/usr/local`, or helper-script defaults. No repository source files are modified.

## Dependencies And Integration Points
Integrated by GitHub Actions and legacy Travis through the derived `ci/fedora.sh` launcher. It feeds the later autoconf, make, and test phases in `build.sh`.

## Risks And Edge Cases
Package names are distro-sensitive; stale package names, missing optional repos, or unavailable `tss2-devel or tpm2-tss-devel` packages can fail CI before source compilation. Several optional installs are deliberately best-effort, so coverage can vary by image.

## Test Signals
A successful run is signaled indirectly by the next CI stage reaching `./configure`, `make`, and `make check` on Fedora/CentOS-family.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/fedora.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/opensuse.sh -->
# sources/security-integrity/ima-evm-utils/ci/opensuse.sh

## Purpose
Installs the ima-evm-utils build and test dependencies inside a openSUSE Leap CI container. It normalizes CI-provided compiler and TPM/TSS selections into distro package names before the shared `build.sh` runs.

## Important APIs, Types, And Functions
- `CC` is mandatory and is expanded to include `gcc` when helper tools require it.
- `TSS` is translated to distro-specific IBM TSS or tpm2-tss development packages.
- `zypper` installs compiler, autotools, OpenSSL, keyutils, xattr/attr, docbook/asciidoc, TPM simulator, pkcs11, and filesystem utility packages.

## Control Flow
The script validates required environment, rewrites `TSS`, refreshes package metadata when needed, installs a broad dependency set, and optionally runs helper installers for components that are missing or not packaged.

## State And Persistence
It mutates the container package database and may install files under `/usr`, `/usr/local`, or helper-script defaults. No repository source files are modified.

## Dependencies And Integration Points
Integrated by GitHub Actions and legacy Travis through the derived `ci/opensuse.sh` launcher. It feeds the later autoconf, make, and test phases in `build.sh`.

## Risks And Edge Cases
Package names are distro-sensitive; stale package names, missing optional repos, or unavailable `ibmtss-devel or tpm2-0-tss-devel` packages can fail CI before source compilation. Several optional installs are deliberately best-effort, so coverage can vary by image.

## Test Signals
A successful run is signaled indirectly by the next CI stage reaching `./configure`, `make`, and `make check` on openSUSE Leap.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/opensuse.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/quay.io.sh -->
# sources/security-integrity/ima-evm-utils/ci/quay.io.sh

## Purpose
Installs the ima-evm-utils build and test dependencies inside a quay.io CentOS-family CI container. It normalizes CI-provided compiler and TPM/TSS selections into distro package names before the shared `build.sh` runs.

## Important APIs, Types, And Functions
- `CC` is mandatory and is expanded to include `gcc` when helper tools require it.
- `TSS` is translated to distro-specific IBM TSS or tpm2-tss development packages.
- `yum` installs compiler, autotools, OpenSSL, keyutils, xattr/attr, docbook/asciidoc, TPM simulator, pkcs11, and filesystem utility packages.

## Control Flow
The script validates required environment, rewrites `TSS`, refreshes package metadata when needed, installs a broad dependency set, and optionally runs helper installers for components that are missing or not packaged.

## State And Persistence
It mutates the container package database and may install files under `/usr`, `/usr/local`, or helper-script defaults. No repository source files are modified.

## Dependencies And Integration Points
Integrated by GitHub Actions and legacy Travis through the derived `ci/quay.io.sh` launcher. It feeds the later autoconf, make, and test phases in `build.sh`.

## Risks And Edge Cases
Package names are distro-sensitive; stale package names, missing optional repos, or unavailable `tss2-devel or tpm2-tss-devel` packages can fail CI before source compilation. Several optional installs are deliberately best-effort, so coverage can vary by image.

## Test Signals
A successful run is signaled indirectly by the next CI stage reaching `./configure`, `make`, and `make check` on quay.io CentOS-family.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/quay.io.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/tumbleweed.sh -->
# sources/security-integrity/ima-evm-utils/ci/tumbleweed.sh

## Purpose
Installs the ima-evm-utils build and test dependencies inside a openSUSE Tumbleweed CI container. It normalizes CI-provided compiler and TPM/TSS selections into distro package names before the shared `build.sh` runs.

## Important APIs, Types, And Functions
- `CC` is mandatory and is expanded to include `gcc` when helper tools require it.
- `TSS` is translated to distro-specific IBM TSS or tpm2-tss development packages.
- `zypper` installs compiler, autotools, OpenSSL, keyutils, xattr/attr, docbook/asciidoc, TPM simulator, pkcs11, and filesystem utility packages.

## Control Flow
The script validates required environment, rewrites `TSS`, refreshes package metadata when needed, installs a broad dependency set, and optionally runs helper installers for components that are missing or not packaged.

## State And Persistence
It mutates the container package database and may install files under `/usr`, `/usr/local`, or helper-script defaults. No repository source files are modified.

## Dependencies And Integration Points
Integrated by GitHub Actions and legacy Travis through the derived `ci/tumbleweed.sh` launcher. It feeds the later autoconf, make, and test phases in `build.sh`.

## Risks And Edge Cases
Package names are distro-sensitive; stale package names, missing optional repos, or unavailable `ibmtss-devel or tpm2-0-tss-devel` packages can fail CI before source compilation. Several optional installs are deliberately best-effort, so coverage can vary by image.

## Test Signals
A successful run is signaled indirectly by the next CI stage reaching `./configure`, `make`, and `make check` on openSUSE Tumbleweed.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/tumbleweed.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/ubuntu.sh -->
# sources/security-integrity/ima-evm-utils/ci/ubuntu.sh

## Purpose
Installs the ima-evm-utils build and test dependencies inside a Ubuntu CI container. It normalizes CI-provided compiler and TPM/TSS selections into distro package names before the shared `build.sh` runs.

## Important APIs, Types, And Functions
- `CC` is mandatory and is expanded to include `gcc` when helper tools require it.
- `TSS` is translated to distro-specific IBM TSS or tpm2-tss development packages.
- `apt` installs compiler, autotools, OpenSSL, keyutils, xattr/attr, docbook/asciidoc, TPM simulator, pkcs11, and filesystem utility packages.

## Control Flow
The script validates required environment, rewrites `TSS`, refreshes package metadata when needed, installs a broad dependency set, and optionally runs helper installers for components that are missing or not packaged.

## State And Persistence
It mutates the container package database and may install files under `/usr`, `/usr/local`, or helper-script defaults. No repository source files are modified.

## Dependencies And Integration Points
Integrated by GitHub Actions and legacy Travis through the derived `ci/ubuntu.sh` launcher. It feeds the later autoconf, make, and test phases in `build.sh`.

## Risks And Edge Cases
Package names are distro-sensitive; stale package names, missing optional repos, or unavailable `libtss-dev or libtss2-dev` packages can fail CI before source compilation. Several optional installs are deliberately best-effort, so coverage can vary by image.

## Test Signals
A successful run is signaled indirectly by the next CI stage reaching `./configure`, `make`, and `make check` on Ubuntu.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/ci/ubuntu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/configure.ac -->
# sources/security-integrity/ima-evm-utils/configure.ac

## Purpose
Autoconf configuration for ima-evm-utils. It defines package metadata, compiler checks, library/header probes, feature toggles, generated files, and a configuration summary.

## Important APIs, Types, And Functions
- `AC_INIT`, `AM_INIT_AUTOMAKE`, `AC_CONFIG_HEADERS`, `AC_CONFIG_MACRO_DIR`, and `LT_INIT` bootstrap the build.
- `PKG_CHECK_MODULES(LIBCRYPTO)` requires libcrypto >= 0.9.8.
- `AC_CHECK_LIB` and `AC_CHECK_HEADER` probe tpm2-tss, IBM TSS, OpenSSL engine/provider, xattr, and keyutils support.
- `AC_ARG_WITH(kernel_headers)` and `AC_ARG_ENABLE` define kernel headers, openssl config, sigv1, engine, provider, and kerneltests options.
- `AC_CONFIG_FILES` emits Makefiles and RPM spec.

## Control Flow
Configure checks programs and dependencies, sets Automake conditionals for optional components, applies debug or optimized CFLAGS, expands project-specific macros for docbook XSL and default hash algorithm, writes configured files, then prints a human-readable feature summary.

## State And Persistence
Persistent generated state includes `config.h`, Makefiles, configured spec file, and substituted variables such as `KERNEL_HEADERS` and `HASH_ALGO`.

## Dependencies And Integration Points
Depends on local m4 macros (`PKG_ARG_ENABLE`, `EVMCTL_MANPAGE_DOCBOOK_XSL`, `AX_DEFAULT_HASH_ALGO`), pkg-config, OpenSSL, keyutils, xattr headers, and optional TSS libraries.

## Risks And Edge Cases
A typo in the provider help text says `providre`. Optional engine/provider support depends on both symbols and headers, so OpenSSL version differences change build shape.

## Test Signals
Signals are configure success, correct conditional Makefile generation, and an accurate final summary of detected features.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/configure.ac -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/doc/Makefile.am -->
# sources/security-integrity/ima-evm-utils/doc/Makefile.am

## Purpose
Doc subdirectory Automake entry point.

## Important APIs, Types, And Functions
- `SUBDIRS = sf` delegates all doc build work to the `sf` folder.

## Control Flow
When top-level Automake includes `doc`, recursive make descends into `doc/sf`.

## State And Persistence
No direct generated state is defined in this file.

## Dependencies And Integration Points
Depends on top-level `HAVE_PANDOC` conditional and the child `doc/sf/Makefile.am`.

## Risks And Edge Cases
The file is intentionally minimal; missing child Makefile generation would make doc builds fail.

## Test Signals
Signal is recursive make entering and completing `doc/sf`.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/doc/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/doc/sf/Makefile.am -->
# sources/security-integrity/ima-evm-utils/doc/sf/Makefile.am

## Purpose
Automake rules for generating the SourceForge wiki HTML document.

## Important APIs, Types, And Functions
- `noinst_DATA = sf-wiki.html` builds the HTML without installing it.
- `sf-wiki.html: sf-wiki.md` runs pandoc from markdown to HTML.
- `CLEANFILES` removes generated HTML.

## Control Flow
Recursive make invokes pandoc when `sf-wiki.md` is newer than the generated HTML.

## State And Persistence
Writes `sf-wiki.html` in the doc/sf build directory.

## Dependencies And Integration Points
Depends on pandoc and the source markdown file.

## Risks And Edge Cases
No install target means generated HTML is build artifact only. Pandoc output can vary by version.

## Test Signals
Signal is successful generation and cleanup of `sf-wiki.html`.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/doc/sf/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/examples/functions -->
# sources/security-integrity/ima-evm-utils/examples/functions

## Purpose
Shared shell library for generating IMA/EVM signing keys and local CA material with OpenSSL.

## Important APIs, Types, And Functions
- `SUPPORTED_ALGORITHMS` lists RSA, EC, and ML-DSA options.
- `get_ossl_keyalgo` maps user algorithms to OpenSSL `-newkey` parameters and enforces OpenSSL >= 3.5 for ML-DSA.
- `get_ossl_keyalgo_detail` returns EC curve pkey options.
- `ima_gen_signing_key` creates a CSR/key and signs it with a local CA.
- `ima_gen_localca` creates a local CA key/cert pair.
- `ima_gen_signing_key_selfsigned` creates a self-signed EVM/IMA key and public key.

## Control Flow
Wrapper scripts source this file, choose a default or user-provided key algorithm, then call one generator. The functions write temporary OpenSSL config files via heredocs and invoke `openssl req`, `openssl x509`, and public-key extraction commands.

## State And Persistence
Creates key, CSR, DER certificate, PEM certificate, serial, and generated config files in the examples directory because wrappers `cd` there before sourcing.

## Dependencies And Integration Points
Depends on OpenSSL CLI behavior, hostname/whoami for certificate subject fields, and local CA files for non-self-signed signing keys.

## Risks And Edge Cases
There is a likely typo in the self-signed public-key case pattern `primve256v1`, so `prime256v1` may miss the EC-specific extraction path. Generated private keys are unencrypted (`-nodes`) and should be handled as sensitive material.

## Test Signals
Signals are generated key/cert files and nonzero OpenSSL failures propagated to wrappers.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/examples/functions -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/examples/ima-gen-local-ca.sh -->
# sources/security-integrity/ima-evm-utils/examples/ima-gen-local-ca.sh

## Purpose
User-facing wrapper that creates a local IMA/EVM CA using the shared examples function library.

## Important APIs, Types, And Functions
- Changes to its own directory and sources `./functions`.
- Defaults `keyalgo` to `rsa:2048`.
- Prints help for `-?` or `--help` and otherwise calls `ima_gen_localca`.

## Control Flow
The script normalizes execution directory, parses an optional positional key algorithm, and delegates all OpenSSL work to the shared function.

## State And Persistence
Writes local CA artifacts such as `ima-local-ca.genkey`, `.x509`, `.priv`, and `.pem` in the examples directory.

## Dependencies And Integration Points
Depends on OpenSSL and supported algorithms from `functions`.

## Risks And Edge Cases
Private CA key output is unencrypted. Positional parsing is intentionally simple and ignores extra arguments.

## Test Signals
Exit status is the generator's OpenSSL-derived status.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/examples/ima-gen-local-ca.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/examples/ima-genkey-self.sh -->
# sources/security-integrity/ima-evm-utils/examples/ima-genkey-self.sh

## Purpose
User-facing wrapper that creates a self-signed EVM/IMA signing key.

## Important APIs, Types, And Functions
- Sources `./functions` from the examples directory.
- Defaults to `rsa:2048` unless a key algorithm argument is supplied.
- Displays help and calls `ima_gen_signing_key_selfsigned`.

## Control Flow
The wrapper performs minimal argument handling and delegates certificate/key generation to the shared shell library.

## State And Persistence
Writes `x509_evm.genkey`, `x509_evm.der`, `privkey_evm.pem`, and `pubkey_evm.pem` style artifacts.

## Dependencies And Integration Points
Depends on OpenSSL and the algorithm mapping in `functions`.

## Risks And Edge Cases
The EC public-key extraction typo in `functions` can affect this wrapper for `prime256v1`. Private key output is unencrypted.

## Test Signals
Exit status is the self-signed generator result.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/examples/ima-genkey-self.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/examples/ima-genkey.sh -->
# sources/security-integrity/ima-evm-utils/examples/ima-genkey.sh

## Purpose
User-facing wrapper that creates an IMA file signing key signed by the local CA generated by `ima-gen-local-ca.sh`.

## Important APIs, Types, And Functions
- Sources `./functions` from its own directory.
- Defaults to `rsa:2048`.
- Displays help and calls `ima_gen_signing_key`.

## Control Flow
The wrapper chooses the algorithm from the first positional argument and delegates CSR/private-key generation and CA signing to the shared function.

## State And Persistence
Writes `ima.genkey`, `csr_ima.pem`, `privkey_ima.pem`, and `x509_ima.der`; also uses local CA files and serial state.

## Dependencies And Integration Points
Depends on OpenSSL and existing `ima-local-ca.pem` plus `ima-local-ca.priv`.

## Risks And Edge Cases
Fails if local CA material has not been generated. Private key output is unencrypted.

## Test Signals
Exit status is the signing-key generator result.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/examples/ima-genkey.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/packaging/ima-evm-utils.spec.in -->
# sources/security-integrity/ima-evm-utils/packaging/ima-evm-utils.spec.in

## Purpose
RPM spec template generated by configure for packaging ima-evm-utils.

## Important APIs, Types, And Functions
- Autoconf substitutes `@PACKAGE_NAME@` and `@PACKAGE_VERSION@`.
- `BuildRequires` lists autoconf, automake, OpenSSL development headers, and keyutils development headers.
- `%build` runs `./autogen.sh`, `%configure --prefix=/usr`, and `make`.
- `%install` runs `make DESTDIR=%{buildroot} install`.
- `%files` includes binaries, libimaevm libraries, and headers.

## Control Flow
RPM prep unpacks the release tarball, build regenerates/configures/compiles, install populates the buildroot, and scriptlets call `ldconfig` for shared library cache updates.

## State And Persistence
Package state includes installed binaries under `%{_bindir}`, libraries under `%{_libdir}`, and headers under `%{_includedir}`.

## Dependencies And Integration Points
Depends on RPM macros, Autotools, OpenSSL/keyutils development packages, and the configured source tarball.

## Risks And Edge Cases
The spec is minimal and old-style, with `BuildRoot` and broad `%{_bindir}/*` file globs. Runtime dependencies are mostly inferred by RPM.

## Test Signals
Signal is successful `rpmbuild -ba` from the top-level `make rpm` target and correct installed file ownership/default attributes.
<!-- END_FILE_RESEARCH: sources/security-integrity/ima-evm-utils/packaging/ima-evm-utils.spec.in -->
