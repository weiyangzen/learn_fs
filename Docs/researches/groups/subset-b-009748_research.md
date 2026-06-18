# Research: subset-b-009748

Grouped research for rclone Jottacloud, Koofr, Linkbox, local backend, and Mail.ru API files. Each section is source-tree aligned and bounded by reconciliation markers for per-file extraction.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/jottacloud/jottacloud.go -->
# sources/user-network-fs/rclone/backend/jottacloud/jottacloud.go

## Purpose
Implements the rclone Jottacloud backend, including backend registration, interactive configuration, OAuth/token migration, JFS/XML and JSON API clients, object metadata, listing, uploads, server-side copy/move, trash cleanup, quota, public links, and shutdown of token renewal.

## Important APIs, Types, And Control Flow
Key types are `Options`, `Fs`, `Object`, and the internal `service` descriptor for white-label OAuth providers. `Config` is a state machine covering standard personal login tokens, traditional OAuth, legacy password/OTP auth, and optional device/mountpoint selection/creation. `NewFs` builds OAuth clients, REST clients, pacer, features, user endpoints, and root-file detection. Filesystem methods include `List`, `ListR`, `Put`, `Mkdir`, `Rmdir`, `Purge`, `Copy`, `Move`, `DirMove`, `PublicLink`, `About`, `UserInfo`, and `CleanUp`. Object methods manage MD5, times, metadata, range reads, allocation/resumable upload, and soft/hard delete.

## State And Persistence
Persistent state lives in rclone config keys such as token URL, client ID/secret, OAuth token, config version, device, and mountpoint. Runtime state includes REST clients, pacer backoff, cached object metadata, upload temp files from `readMD5`, and a background token renewer. Remote persistence is through Jottacloud file, trash, share, metadata timestamp, and deduplicated upload allocation APIs.

## Dependencies And Integration Points
Depends on rclone `fs`, `oauthutil`, `rest`, `pacer`, `encoder`, `accounting`, hashes, and Jottacloud API structs. It integrates with rclone optional interfaces including `Purger`, `Copier`, `Mover`, `DirMover`, `ListRer`, `PublicLinker`, `Abouter`, `UserInfoer`, `CleanUpper`, `Shutdowner`, `MimeTyper`, and `Metadataer`.

## Risks And Test Signals
High-risk paths include legacy token refresh body rewriting, config-version compatibility, white-label provider endpoint drift, XML liststream count validation, trash-only filtering, hard delete semantics, MD5 buffering to disk for large files, upload resume offsets, no-versions delete-before-upload, and metadata timestamp parsing. Tests should cover config branches with mocked REST, liststream parsing, `readMD5`, allocation/dedupe/resume upload, metadata copy/move, trash-only behavior, root-as-file, and token renewer shutdown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/jottacloud/jottacloud.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/jottacloud/jottacloud_internal_test.go -->
# sources/user-network-fs/rclone/backend/jottacloud/jottacloud_internal_test.go

## Purpose
Provides package-internal tests for Jottacloud helper behavior and backend-specific fstests extension hooks.

## Important APIs, Types, And Control Flow
`TestReadMD5` iterates sizes and memory thresholds, computes the expected MD5 from `readers.NewPatternReader`, calls `readMD5`, and verifies both returned checksum and replay reader contents. `InternalTestMetadata` uploads an object with `btime` and `mtime` metadata through `fstests.PutTestContentsMetadata`, reads back `Object.Metadata`, and checks timestamp precision, upload time, and content type where relevant. `InternalTest` exposes this as `fstests.InternalTester`.

## State And Persistence
The test creates temporary remote objects under the configured Jottacloud test remote and removes them afterward. `TestReadMD5` exercises both in-memory and temporary-file buffering without permanent repository state.

## Dependencies And Integration Points
Uses rclone `fstest`, `fstests`, `fs.Metadata`, random test contents, pattern readers, and testify assertions. It integrates with the generic backend integration suite through the `InternalTester` interface.

## Risks And Test Signals
Signals checksum correctness across threshold branches and verifies metadata round-trip behavior. Remaining risk is that remote metadata tests require a live account and can be sensitive to server timestamp precision or upload-time delays.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/jottacloud/jottacloud_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/jottacloud/jottacloud_test.go -->
# sources/user-network-fs/rclone/backend/jottacloud/jottacloud_test.go

## Purpose
Registers the Jottacloud backend with rclone's standard integration test harness.

## Important APIs, Types, And Control Flow
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestJottacloud:"` and a nil object sentinel of type `*jottacloud.Object`. The generic suite exercises object creation, listing, updates, removals, directory operations, feature declarations, hashes, and optional backend hooks.

## State And Persistence
State is entirely test-remote data created and cleaned up by `fstests.Run`; no local persistent files are produced beyond normal test artifacts.

## Dependencies And Integration Points
Depends on the external Jottacloud test remote being configured in rclone's test environment. Imports the backend package to expose the concrete object type to the generic suite.

## Risks And Test Signals
The test is a broad integration signal but not hermetic. Failures can reflect account quota, network/API changes, config drift, or backend regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/jottacloud/jottacloud_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/koofr/koofr.go -->
# sources/user-network-fs/rclone/backend/koofr/koofr.go

## Purpose
Implements the rclone backend for Koofr-compatible storage providers, including Koofr, Digi Storage, and custom endpoints.

## Important APIs, Types, And Control Flow
Key types are `Options`, `Fs`, and `Object`. Registration declares provider-specific config options, encoding, credentials, mount selection, and mtime capability. `NewFs` parses config, applies provider defaults, reveals the password, creates a Koofr client with basic auth, selects the configured or primary mount, and detects file roots. Object methods expose remote name, size, MD5, millisecond mtime, range reads, overwriting uploads, and delete. Fs methods cover listing, object lookup, upload/stream upload, recursive mkdir, rmdir-empty check, server-side copy/move/dirmove, quota, purge, and public links.

## State And Persistence
Persistent state is backend config: provider, endpoint, mount ID, user, obscured password, `setmtime`, and encoding. Runtime state is small: client, selected mount ID, root, feature table, and object `FileInfo`. Remote persistence is delegated to Koofr file, folder, mount, and link APIs.

## Dependencies And Integration Points
Uses rclone `fs`, config, encoder, fshttp, hash APIs, plus `github.com/koofr/go-koofrclient` and `go-httpclient`. Implements rclone optional interfaces such as put streaming, copy, move, dir move, purge, about, and public link.

## Risks And Test Signals
Important risks are unchecked type assertions in copy/move/dirmove, provider endpoint inference for legacy configs, mount selection errors, translating Koofr 400/404 into rclone errors, duplicate mkdir races, and public-link URL rewriting assumptions. Test signals should include provider defaulting, root-file detection, mkdir idempotency, error translation, range reads, copy/move across mounts, quota unit conversion, and link URL generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/koofr/koofr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/koofr/koofr_test.go -->
# sources/user-network-fs/rclone/backend/koofr/koofr_test.go

## Purpose
Connects the Koofr backend to rclone's standard integration tests.

## Important APIs, Types, And Control Flow
`TestIntegration` invokes `fstests.Run` with `RemoteName: "TestKoofr:"`. The generic suite exercises the backend through rclone interfaces rather than direct helper calls.

## State And Persistence
Creates temporary remote test data in the configured Koofr account/mount and relies on the generic test harness for cleanup.

## Dependencies And Integration Points
Requires a configured `TestKoofr:` remote. This file intentionally imports only `fstests`, so concrete backend behavior is reached through backend registration elsewhere.

## Risks And Test Signals
Provides live end-to-end coverage but no unit-level isolation for provider defaults or error translation. Failures may come from network, credentials, account state, or backend regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/koofr/koofr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/linkbox/linkbox.go -->
# sources/user-network-fs/rclone/backend/linkbox/linkbox.go

## Purpose
Implements rclone support for Linkbox cloud storage using both Linkbox's open API and web API.

## Important APIs, Types, And Control Flow
Core types are `Options`, `Fs`, `Object`, `entity`, response wrappers, and upload response structs. `NewFs` parses token/email/password, builds normal and CDN REST clients, disables HTTP/2 and sets a browser-like user agent for CDN downloads, restores or obtains a web token, and initializes `dircache`. `login` obtains and stores the web token. `listAll`, `FindLeaf`, `CreateDir`, `List`, `NewObject`, `Mkdir`, `Rmdir`, and `Purge` are directory-cache driven. `Open` downloads via stored or refreshed CDN URL. `Update` rejects empty/unknown size, deletes existing files, hashes the first 10 MiB, requests an upload URL or dedupe status, uploads via PUT if needed, finalizes with `folder_upload_file`, and polls for eventual consistency.

## State And Persistence
Persistent config includes open API token, email, obscured password, and cached `web_token`. Runtime state includes pacer, REST clients, directory cache, web token protected by mutex, and object entity data. Remote state is Linkbox folders/files and object deletion/recreation during update.

## Dependencies And Integration Points
Uses rclone `fs`, `rest`, `fshttp`, `pacer`, `fserrors`, `hash`, `obscure`, and `dircache`. Implements `Fs`, `Purger`, `DirCacheFlusher`, and `Object`; public sharing is intentionally omitted because Linkbox links are page links rather than direct file links.

## Risks And Test Signals
Risks include two-token authentication drift, web-token refresh retry semantics, Linkbox status-code quirks, case-insensitive matching, pagination limit, delete-before-upload data loss on later failures, inability to upload empty or unknown-sized files, first-10-MiB hash protocol assumptions, CDN fingerprint workarounds, and eventual consistency polling. Tests should cover token refresh, list pagination, dircache create/find/flush, upload status 1 and 600 paths, empty/unknown upload rejection, remove/rmdir error mapping, and download URL refresh.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/linkbox/linkbox.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/linkbox/linkbox_test.go -->
# sources/user-network-fs/rclone/backend/linkbox/linkbox_test.go

## Purpose
Runs the generic rclone integration suite for Linkbox.

## Important APIs, Types, And Control Flow
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestLinkbox:"`, `NilObject: (*linkbox.Object)(nil)`, and `SkipLeadingDot: true` because Linkbox does not support leading-dot filenames.

## State And Persistence
The test creates remote objects and directories in the configured Linkbox test account and delegates cleanup to `fstests`.

## Dependencies And Integration Points
Depends on a live `TestLinkbox:` remote and generic rclone test behavior. It validates the backend through public `fs.Fs` and `fs.Object` interfaces.

## Risks And Test Signals
Broadly detects API or implementation regressions but is affected by live service behavior. It does not directly isolate the web-token refresh, upload-url, or CDN-download special cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/linkbox/linkbox_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/about_unix.go -->
# sources/user-network-fs/rclone/backend/local/about_unix.go

## Purpose
Adds quota/usage reporting for local filesystems on Darwin, DragonFly, FreeBSD, and Linux.

## Important APIs, Types, And Control Flow
`About` calls `syscall.Statfs` on `f.root`, translates missing root into `fs.ErrorDirNotFound`, and returns `fs.Usage` using block size times total blocks, used blocks, and available blocks.

## State And Persistence
No persistent state is changed. It reads filesystem statistics from the kernel.

## Dependencies And Integration Points
Depends on `syscall.Statfs` and rclone `fs.Usage`. The compile-time interface assertion makes local `Fs` an `fs.Abouter` on supported Unix platforms.

## Risks And Test Signals
Risk is platform-specific interpretation of `Bfree` versus `Bavail`; available space is user-visible upload capacity. Tests should verify missing-root mapping and sane totals on temporary filesystems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/about_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/about_windows.go -->
# sources/user-network-fs/rclone/backend/local/about_windows.go

## Purpose
Provides Windows local filesystem quota reporting.

## Important APIs, Types, And Control Flow
`About` converts `f.root` to UTF-16 and invokes `GetDiskFreeSpaceExW`, returning total bytes, total-free-derived used bytes, and user-available bytes as `fs.Usage`.

## State And Persistence
No filesystem state is modified; it only queries Kernel32.

## Dependencies And Integration Points
Uses `golang.org/x/sys/windows`, `unsafe`, and rclone `fs.Usage`. The backend implements `fs.Abouter` under the Windows build tag.

## Risks And Test Signals
Risks include path conversion failures and Windows API errno handling. Tests should check UNC/long-path roots and that available free space honors user quotas rather than raw volume free bytes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/about_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/clone_darwin.go -->
# sources/user-network-fs/rclone/backend/local/clone_darwin.go

## Purpose
Enables local server-side copy on macOS with cgo by using APFS clonefile-style copying.

## Important APIs, Types, And Control Flow
`Fs.Copy` validates Darwin and `--local-no-clone`, requires a local `*Object`, excludes translated symlink clones, fetches metadata if enabled, creates destination parents, optionally resolves symlink targets under `--copy-links`, calls `Clone`, writes metadata, and returns the new object. `Clone` wraps `go-darwin/apfs.CopyFile` with `COPYFILE_CLONE`.

## State And Persistence
Creates a destination file that may share blocks with the source. Metadata is also persisted if requested.

## Dependencies And Integration Points
Integrates with rclone `fs.Copier`, local `Object` metadata, and APFS copyfile APIs. Disabled by build tags except `darwin && cgo`.

## Risks And Test Signals
Risks include APFS-only semantics, cgo availability, symlink mode differences, and metadata application after clone success. Tests should cover regular-file clone, fallback error behavior, `NoClone`, `--links`, `--copy-links`, and metadata preservation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/clone_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/lchmod.go -->
# sources/user-network-fs/rclone/backend/local/lchmod.go

## Purpose
Defines a safe no-op `lChmod` implementation for platforms where changing symlink permissions without following the link is unavailable or unsafe.

## Important APIs, Types, And Control Flow
Sets `haveLChmod = false` and implements `lChmod(name, mode)` to return nil without modifying anything.

## State And Persistence
No filesystem state changes occur.

## Dependencies And Integration Points
Used by metadata writing when `--links` targets translated symlinks. Build tags cover Windows, Plan 9, JS, and Linux.

## Risks And Test Signals
The silent no-op avoids unsafe target chmod but means requested symlink mode metadata is not persisted. Tests should assert metadata writes do not alter symlink targets on these platforms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/lchmod.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/lchmod_unix.go -->
# sources/user-network-fs/rclone/backend/local/lchmod_unix.go

## Purpose
Provides symlink chmod support on Unix platforms where `fchmodat` with `AT_SYMLINK_NOFOLLOW` works.

## Important APIs, Types, And Control Flow
`syscallMode` maps Go mode bits to syscall permission, setuid, setgid, and sticky bits. `lChmod` calls `unix.Fchmodat` with `AT_SYMLINK_NOFOLLOW` and wraps failures in `os.PathError`.

## State And Persistence
Persists mode changes on the link itself, not the target, on supported platforms.

## Dependencies And Integration Points
Used by `writeMetadataToFile` for translated symlink `mode` metadata. Linux is excluded because its `fchmodat` behavior does not support this flag safely.

## Risks And Test Signals
Risks include platform kernel differences and incorrect mode bit mapping. Tests should verify target permissions remain unchanged and link mode errors are surfaced.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/lchmod_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/lchtimes.go -->
# sources/user-network-fs/rclone/backend/local/lchtimes.go

## Purpose
Provides a no-op link timestamp setter on Plan 9 and JS.

## Important APIs, Types, And Control Flow
Sets `haveLChtimes = false` and implements `lChtimes` to return nil without changing atime or mtime.

## State And Persistence
No metadata is persisted for symlink times.

## Dependencies And Integration Points
Called by `Object.setTimes` when an object is a translated symlink.

## Risks And Test Signals
The no-op prevents unsupported platform failures but hides inability to set link times. Tests should account for `haveLChtimes` before expecting symlink time round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/lchtimes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/lchtimes_unix.go -->
# sources/user-network-fs/rclone/backend/local/lchtimes_unix.go

## Purpose
Implements no-follow symlink timestamp updates on Unix-like platforms except Windows, Plan 9, and JS.

## Important APIs, Types, And Control Flow
`lChtimes` converts access and modification times to `unix.Timespec` values and calls `unix.UtimesNanoAt` with `AT_SYMLINK_NOFOLLOW`.

## State And Persistence
Persists link atime and mtime without touching the target where the OS supports it.

## Dependencies And Integration Points
Supports local backend `--links` mode, metadata writes, and symlink tests that check `haveLChtimes`.

## Risks And Test Signals
Risks are filesystem support differences and precision rounding. Tests should compare times within filesystem precision and verify target metadata is not modified.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/lchtimes_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/lchtimes_windows.go -->
# sources/user-network-fs/rclone/backend/local/lchtimes_windows.go

## Purpose
Implements symlink timestamp updates on Windows.

## Important APIs, Types, And Control Flow
Sets `haveLChtimes = true` and delegates `lChtimes` to `setTimes` with the `link` flag enabled and no birth-time change.

## State And Persistence
Persists atime and mtime on the reparse point rather than the target.

## Dependencies And Integration Points
Uses the Windows `setbtime_windows.go` helper and is called from translated symlink metadata paths.

## Risks And Test Signals
Risks include Windows handle flags and privilege/attribute behavior. Tests should verify link-target isolation and timestamp round trips on Windows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/lchtimes_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/local.go -->
# sources/user-network-fs/rclone/backend/local/local.go

## Purpose
Implements rclone's local disk backend, mapping local files, directories, symlinks, metadata, hashes, streaming, and moves into rclone filesystem interfaces.

## Important APIs, Types, And Control Flow
Key types are `Options`, `Fs`, `Object`, `Directory`, `localOpenFile`, and the `timeType` enum. Registration exposes many backend flags: symlink handling, Unicode normalization, update checking, one-file-system, case sensitivity, cloning, preallocation, sparse writes, modtime disabling, fatal ENOSPC, time type, hashes, and encoding. `NewFs` parses options, rejects conflicting symlink modes, cleans roots, sets features, chooses `os.Stat` vs `os.Lstat`, detects root files and translated links, and stores root device for one-filesystem filtering. `List` handles platform directory reads, filtering, symlink following/translation, device boundary checks, special-file skips, and invalid UTF-8 warnings. Object methods handle hash caching, update-change detection, range reads, symlink-as-file translation, writes with preallocation/hash options, metadata writes, random-access writers, removal, and root path cleaning.

## State And Persistence
Persistent state is the local filesystem itself: files, directories, symlinks, times, modes, ownership, xattrs, and optional sparse/preallocated extents. Runtime state includes cached metadata/hashes guarded by `objectMetaMu`, warning deduplication, detected precision, root device, and xattr support flag.

## Dependencies And Integration Points
Uses rclone `fs`, accounting, filter, fserrors, hash, operations expectations, encoder, file helpers, and readers. OS-specific helpers provide `About`, copy clone, device IDs, metadata, xattrs, symlink errors, removal, and time setters. Implements many optional interfaces including put streaming, mover, dir mover, commander, writer-at, dir modtime, mkdir metadata, metadata, and set metadata.

## Risks And Test Signals
Risks include races with changing files, stale hash cache, partial-write cleanup, ENOSPC fatal wrapping, Windows hidden-file handling, symlink security isolation, filter-aware error suppression, one-filesystem device filtering, path encoding/UNC normalization, preallocation side effects, sparse warnings, and platform metadata disparities. Tests cover update detection, symlink modes, metadata/xattrs, filtering, copy links, hash cache invalidation, disk-full fatal behavior, remove retry, Windows cleanup, and generic local integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/local.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/local_internal_diskfull_test.go -->
# sources/user-network-fs/rclone/backend/local/local_internal_diskfull_test.go

## Purpose
Tests local backend ENOSPC detection and optional fatal wrapping.

## Important APIs, Types, And Control Flow
`TestIsDiskFullError` checks direct and wrapped `syscall.ENOSPC`, `file.ErrDiskFull`, `os.PathError`, and `os.SyscallError` cases. `updateWithReader` injects a reader that always returns a configured error into `Object.Update`. The remaining tests assert ENOSPC is non-fatal by default, fatal when `FatalIfNoSpace` is true, and unrelated errors are not made fatal.

## State And Persistence
Uses temporary fstest local directories and synthetic readers; no durable state.

## Dependencies And Integration Points
Depends on `fserrors`, `file.ErrDiskFull`, `object.NewStaticObjectInfo`, and local `Object.Update` defer logic.

## Risks And Test Signals
Strongly validates the backup-script safety feature. Remaining risk is platform-specific ENOSPC wrapping not represented by the cases; Plan 9 is excluded by build tag.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/local_internal_diskfull_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/local_internal_test.go -->
# sources/user-network-fs/rclone/backend/local/local_internal_test.go

## Purpose
Provides local backend unit and integration-style tests for update detection, symlinks, hashing, metadata, filters, and copy behavior.

## Important APIs, Types, And Control Flow
`TestMain` initializes fstest. `TestUpdatingCheck` verifies `localOpenFile.Read` fails when source size/mtime changes unless `NoCheckUpdated` is set. Symlink tests switch between no flags, `--copy-links`, and `--links`, check `.rclonelink` translation, NewFs root-file rules, range reads, and conflict errors. Hash tests validate `hash.None`, hash recomputation after update, and cache clearing after remove. Metadata tests exercise file and symlink metadata/xattrs and confirm symlink metadata does not alter the target. Filter tests validate filter-aware listing and symlink filtering. Copy tests ensure translated symlinks recreate links and copy-links produces regular files.

## State And Persistence
Creates temporary local trees with files, directories, symlinks, xattrs, modes, and timestamps. Cleanup is handled by fstest runs and defers.

## Dependencies And Integration Points
Uses rclone `filter`, `accounting`, `operations`, `object`, `hash`, `readers`, `file`, and testify. It tests both direct local helpers and rclone operation-level copy behavior.

## Risks And Test Signals
This is the primary local backend regression suite. It explicitly covers security-sensitive symlink metadata isolation and behavior that differs by OS capability flags such as xattrs, link time setting, and birth time setting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/local_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/local_internal_windows_test.go -->
# sources/user-network-fs/rclone/backend/local/local_internal_windows_test.go

## Purpose
Tests Windows-specific directory removal behavior for read-only directories.

## Important APIs, Types, And Control Flow
`TestRmdirWindows` creates a local directory through rclone operations, marks it with `FILE_ATTRIBUTE_DIRECTORY | FILE_ATTRIBUTE_READONLY`, then calls `operations.Rmdir` and expects success.

## State And Persistence
Uses a temporary local test root and modifies Windows file attributes on a test directory.

## Dependencies And Integration Points
Depends on `syscall.SetFileAttributes`, rclone `operations`, and local `Rmdir` fallback that chmods before remove when Windows returns permission errors.

## Risks And Test Signals
Validates a Windows-specific workaround for Go issue 26295. It is skipped outside Windows and does not cover other attributes such as hidden/system.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/local_internal_windows_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/local_test.go -->
# sources/user-network-fs/rclone/backend/local/local_test.go

## Purpose
Runs rclone's generic integration test suite against the local backend.

## Important APIs, Types, And Control Flow
`TestIntegration` calls `fstests.Run` with the empty local remote name, nil object sentinel `*local.Object`, and `QuickTestOK: true`.

## State And Persistence
Creates temporary local files and directories under the fstest root and cleans them up through the test harness.

## Dependencies And Integration Points
Uses the standard `fstests` suite to exercise local backend interface behavior across many common operations.

## Risks And Test Signals
Provides broad interface regression coverage. Platform-specific behavior is partly covered here and partly in internal tests and build-tagged helper tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/local_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/metadata.go -->
# sources/user-network-fs/rclone/backend/local/metadata.go

## Purpose
Defines local backend metadata keys and shared metadata parsing/writing behavior.

## Important APIs, Types, And Control Flow
`systemMetadataInfo` documents owned keys: mode, uid, gid, rdev, atime, mtime, and btime. `parseMetadataTime` and `parseMetadataInt` parse RFC3339Nano and integer values with debug logging on invalid input. `writeMetadataToFile` applies atime/mtime, optional btime, ownership, and mode. It uses no-follow helpers for translated symlinks and regular OS calls for normal files.

## State And Persistence
Persists filesystem timestamps, ownership, and permissions. Does not currently write `rdev`.

## Dependencies And Integration Points
Relies on OS-specific `readMetadataFromFile`, `readTime`, `lChtimes`, `lChmod`, and btime helpers. Called by object and directory metadata setters.

## Risks And Test Signals
Risks include partial metadata application, privilege failures on ownership, symlink-target safety, Windows/Plan9 ownership no-op, mode parsing limits, and unsupported birth time. Tests should verify invalid metadata is ignored/logged and that symlink writes do not alter targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/metadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/metadata_bsd.go -->
# sources/user-network-fs/rclone/backend/local/metadata_bsd.go

## Purpose
Implements metadata reads and selectable times for Darwin, FreeBSD, and NetBSD.

## Important APIs, Types, And Control Flow
`readTime` extracts atime, birth time, or ctime from `syscall.Stat_t`, falling back to mtime. `readMetadataFromFile` lstat/stat reads mode, uid, gid, rdev, atime, mtime, and btime into `fs.Metadata`.

## State And Persistence
Only reads filesystem metadata; writes are handled by shared metadata code.

## Dependencies And Integration Points
Uses BSD `Stat_t` `Timespec` fields and feeds local `Object.Metadata` and configured `time_type`.

## Risks And Test Signals
Risks include failed `Sys` type assertions and platform-specific nanosecond precision. Tests should verify btime/ctime/atime exposure on supported BSD systems and symlink behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/metadata_bsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/metadata_linux.go -->
# sources/user-network-fs/rclone/backend/local/metadata_linux.go

## Purpose
Implements Linux metadata reads, preferring `statx` when available and falling back to `fstatat`.

## Important APIs, Types, And Control Flow
`readTime` supports atime and ctime from `syscall.Stat_t`. `readMetadataFromFile` initializes a once-selected reader: `readMetadataFromFileStatx` if `statx` is available and not Android, otherwise `readMetadataFromFileFstatat`. The statx path reads type, mode, uid, gid, atime, mtime, ctime, and btime; the fallback reads mode, uid, gid, rdev, atime, and mtime.

## State And Persistence
No writes; caches the chosen metadata read function in package globals.

## Dependencies And Integration Points
Uses `golang.org/x/sys/unix`, local `FollowSymlinks` to choose no-follow flags, and supplies local metadata/time-type behavior.

## Risks And Test Signals
Risks include kernel `statx` availability detection, Android exclusion, architecture-dependent timespec casts, symlink no-follow correctness, and btime absence in fallback. Tests should exercise both statx and fallback where possible.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/metadata_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/metadata_other.go -->
# sources/user-network-fs/rclone/backend/local/metadata_other.go

## Purpose
Provides minimal metadata support for DragonFly, Plan 9, JS, and AIX.

## Important APIs, Types, And Control Flow
`readTime` always returns `fi.ModTime`. `readMetadataFromFile` reads local info and sets only `mode` and `mtime`.

## State And Persistence
Reads metadata only; no persistent changes.

## Dependencies And Integration Points
Acts as the build-tag fallback for platforms without richer stat support.

## Risks And Test Signals
Capabilities are intentionally limited. Tests should expect absent uid/gid/atime/btime/ctime and confirm no crashes on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/metadata_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/metadata_unix.go -->
# sources/user-network-fs/rclone/backend/local/metadata_unix.go

## Purpose
Implements metadata reads for OpenBSD and Solaris.

## Important APIs, Types, And Control Flow
`readTime` extracts atime or ctime from `syscall.Stat_t`, otherwise mtime. `readMetadataFromFile` sets mode, uid, gid, optional rdev, atime, and mtime.

## State And Persistence
Only reads filesystem metadata.

## Dependencies And Integration Points
Feeds local metadata and `time_type` support for OpenBSD/Solaris builds.

## Risks And Test Signals
Risks include missing btime support and `Stat_t` layout differences. Tests should validate supported keys and graceful fallback on unexpected `Sys` values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/metadata_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/metadata_windows.go -->
# sources/user-network-fs/rclone/backend/local/metadata_windows.go

## Purpose
Provides Windows metadata reads and time selection.

## Important APIs, Types, And Control Flow
`readTime` reads access time or creation time from `syscall.Win32FileAttributeData`, otherwise mtime. `readMetadataFromFile` sets portable mode plus atime, mtime, and btime from Windows filetime values.

## State And Persistence
Reads metadata only; write support for timestamps is in `setbtime_windows.go`.

## Dependencies And Integration Points
Supports local backend metadata reads and `time_type` on Windows.

## Risks And Test Signals
Risks include missing Windows attribute metadata and filetime conversion precision. Tests should validate creation-time round trips and behavior for reparse points.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/metadata_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/read_device_other.go -->
# sources/user-network-fs/rclone/backend/local/read_device_other.go

## Purpose
Provides a device-ID fallback for platforms without supported stat device fields.

## Important APIs, Types, And Control Flow
`readDevice` ignores its inputs and returns `devUnset`.

## State And Persistence
No state is read or modified beyond receiving an `os.FileInfo`.

## Dependencies And Integration Points
Used by local `NewFs` and `List` for `--one-file-system`; on these platforms that feature cannot enforce boundaries.

## Risks And Test Signals
Risk is user expectation mismatch for `--one-file-system`. Tests should confirm device filtering is effectively disabled on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/read_device_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/read_device_unix.go -->
# sources/user-network-fs/rclone/backend/local/read_device_unix.go

## Purpose
Reads filesystem device IDs for Unix-like platforms that support `syscall.Stat_t.Dev`.

## Important APIs, Types, And Control Flow
`readDevice` returns `devUnset` unless `oneFileSystem` is true. When enabled, it asserts `fi.Sys().(*syscall.Stat_t)` and returns `Dev`; assertion failures are logged and treated as unset.

## State And Persistence
Reads file metadata only. The returned value is stored in `Fs.dev` and compared during listing.

## Dependencies And Integration Points
Supports local backend `--one-file-system` by preventing directory traversal across device boundaries.

## Risks And Test Signals
Risks include type assertion failures on unusual filesystems and platform-specific device IDs. Tests should create or mock different devices if possible and verify boundary filtering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/read_device_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/remove_other.go -->
# sources/user-network-fs/rclone/backend/local/remove_other.go

## Purpose
Defines normal local object removal on non-Windows platforms.

## Important APIs, Types, And Control Flow
`remove` simply calls `os.Remove(name)`.

## State And Persistence
Deletes the named filesystem entry if allowed by the OS.

## Dependencies And Integration Points
Called by `Object.Remove` and partial-write cleanup paths.

## Risks And Test Signals
Behavior is OS-native. Tests should verify error propagation and successful deletion of normal files; open-file deletion behavior differs from Windows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/remove_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/remove_test.go -->
# sources/user-network-fs/rclone/backend/local/remove_test.go

## Purpose
Tests local `remove` behavior when the file is still open.

## Important APIs, Types, And Control Flow
`TestRemove` creates a temp file, checks it exists, schedules background close after 250 ms using a wait group, calls `remove`, asserts no error and non-existence, then waits for close completion.

## State And Persistence
Creates and deletes one temporary file outside the repository.

## Dependencies And Integration Points
Exercised against platform-specific `remove` implementations. On Windows it validates sharing-violation retry; on Unix it validates ordinary unlink semantics.

## Risks And Test Signals
Timing-dependent on Windows retry behavior but bounded. It catches regressions in deletion retry and temp-file cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/remove_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/remove_windows.go -->
# sources/user-network-fs/rclone/backend/local/remove_windows.go

## Purpose
Implements Windows removal with retry for sharing violations.

## Important APIs, Types, And Control Flow
`remove` tries `os.Remove` up to ten times. If the error is an `os.PathError` wrapping `windows.ERROR_SHARING_VIOLATION`, it logs, sleeps with exponential backoff starting at 1 ms, and retries.

## State And Persistence
Deletes a filesystem entry after temporary sharing conflicts clear.

## Dependencies And Integration Points
Used by local `Object.Remove` and cleanup paths on Windows. Integrates with fs logging and `x/sys/windows` errno constants.

## Risks And Test Signals
Risks include insufficient retry budget or masking non-sharing errors. `remove_test.go` is the direct signal for open-file deletion behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/remove_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/setbtime.go -->
# sources/user-network-fs/rclone/backend/local/setbtime.go

## Purpose
Provides non-Windows stubs for setting birth/creation time.

## Important APIs, Types, And Control Flow
Sets `haveSetBTime = false`; `setBTime` and `lsetBTime` return nil without changes.

## State And Persistence
No birth time metadata is written.

## Dependencies And Integration Points
Used by shared metadata write code, which checks `haveSetBTime` before attempting btime writes.

## Risks And Test Signals
Silent no-op is guarded by capability flag. Tests should skip btime write expectations when `haveSetBTime` is false.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/setbtime.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/setbtime_windows.go -->
# sources/user-network-fs/rclone/backend/local/setbtime_windows.go

## Purpose
Implements Windows atime, mtime, and birth-time updates for files and links.

## Important APIs, Types, And Control Flow
`setTimes` opens the path with `FILE_WRITE_ATTRIBUTES`, `FILE_FLAG_BACKUP_SEMANTICS`, and optionally `FILE_FLAG_OPEN_REPARSE_POINT`, converts non-zero Go times to Windows filetimes, calls `SetFileTime`, and closes the handle. `setBTime` and `lsetBTime` specialize birth-time writes.

## State And Persistence
Persists Windows file timestamps, including creation time and link reparse-point timestamps.

## Dependencies And Integration Points
Shared by `lchtimes_windows.go` and metadata writing. `haveSetBTime = true` enables btime write tests.

## Risks And Test Signals
Risks include handle sharing/permissions, close-error propagation, and link-target confusion. Tests should verify file and symlink timestamp writes on Windows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/setbtime_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/symlink.go -->
# sources/user-network-fs/rclone/backend/local/symlink.go

## Purpose
Detects circular symlink errors on Unix-like platforms.

## Important APIs, Types, And Control Flow
`isCircularSymlinkError` unwraps `*os.PathError`, checks for a `syscall.Errno`, and returns true when the errno is `ELOOP`.

## State And Persistence
No state is modified.

## Dependencies And Integration Points
Used in local `List` when following symlinks to convert circular symlinks into non-retry listing errors instead of aborting traversal.

## Risks And Test Signals
Risks are error wrapping shapes that hide `ELOOP`. Tests should include circular symlink listing in `--copy-links` mode.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/symlink.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/symlink_other.go -->
# sources/user-network-fs/rclone/backend/local/symlink_other.go

## Purpose
Provides circular symlink detection for Windows, Plan 9, and JS where Unix `ELOOP` is not used.

## Important APIs, Types, And Control Flow
`isCircularSymlinkError` checks whether the error string contains "The name of the file cannot be resolved by the system".

## State And Persistence
No state is modified.

## Dependencies And Integration Points
Supports local listing behavior when following links on non-Unix platforms.

## Risks And Test Signals
String matching is brittle and locale-sensitive. Windows tests should cover circular/junction resolution errors if feasible.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/symlink_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/tests_test.go -->
# sources/user-network-fs/rclone/backend/local/tests_test.go

## Purpose
Tests Windows path cleaning and encoding behavior.

## Important APIs, Types, And Control Flow
`testsWindows` contains raw input/output path pairs covering drive paths, long UNC paths, slash normalization, and replacement of Windows-reserved characters. `TestCleanWindows` skips non-Windows platforms and asserts `cleanRootPath(..., true, encoder.OS)` matches each expected path.

## State And Persistence
No filesystem changes are made; the test checks string transformation only.

## Dependencies And Integration Points
Directly validates local `cleanRootPath`, Windows path normalization, and `encoder.OS`.

## Risks And Test Signals
Signals regressions in root path encoding before filesystem operations. It does not test `noUNC=false` conversion or actual filesystem access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/tests_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/xattr.go -->
# sources/user-network-fs/rclone/backend/local/xattr.go

## Purpose
Implements user metadata storage through extended attributes on platforms supported by `pkg/xattr`.

## Important APIs, Types, And Control Flow
Defines `xattrPrefix = "user."` and `xattrSupported = xattr.XATTR_SUPPORTED`. `xattrIsNotSupported` detects ENOTSUP, ENOATTR, and EINVAL, disables future xattr operations atomically, and logs once. `getXattr` lists and reads attributes with follow/no-follow variants, lowercases names, filters non-`user.` and backend-owned system metadata keys, and returns user metadata. `setXattr` writes non-system metadata as `user.<key>`.

## State And Persistence
Persists user metadata as filesystem xattrs. Runtime state includes the `Fs.xattrSupported` atomic flag that can disable xattr use after unsupported errors.

## Dependencies And Integration Points
Used by local object and directory metadata read/write paths. Integrates with `github.com/pkg/xattr`, local symlink-following options, and `systemMetadataInfo`.

## Risks And Test Signals
Risks include namespace portability, lowercasing key names, symlink xattr support differences, partial writes, and dynamic disabling after one unsupported error. Metadata tests cover read/write and symlink limitations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/xattr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/xattr_unsupported.go -->
# sources/user-network-fs/rclone/backend/local/xattr_unsupported.go

## Purpose
Provides no-op xattr support for OpenBSD and Plan 9 where `pkg/xattr` is unavailable.

## Important APIs, Types, And Control Flow
Sets `xattrSupported = false`; `getXattr` and `setXattr` return nil without reading or writing metadata.

## State And Persistence
No xattr metadata is persisted.

## Dependencies And Integration Points
Keeps local metadata APIs compilable while feature flags report user metadata support as unavailable.

## Risks And Test Signals
The expected behavior is graceful absence of user metadata. Tests should assert feature flags and skip xattr round trips on these platforms.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/local/xattr_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mailru/api/bin.go -->
# sources/user-network-fs/rclone/backend/mailru/api/bin.go

## Purpose
Defines constants for Mail.ru Cloud's binary protocol.

## Important APIs, Types, And Control Flow
Exports content type and fixed ID lengths, operation codes for add file, rename, create folder, folder list, shared folder list, and partially understood operations, plus result codes for mkdir, move, add-file, list options, list parse flags, list results, and directory item types.

## State And Persistence
No runtime state or persistence; all values are compile-time protocol constants.

## Dependencies And Integration Points
Consumed by Mail.ru backend request builders and binary response parsers alongside `helpers.go`.

## Risks And Test Signals
Risks are protocol drift and ambiguous TODO opcodes/result names. Tests should validate binary requests/responses against known captures and live API behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mailru/api/bin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mailru/api/helpers.go -->
# sources/user-network-fs/rclone/backend/mailru/api/helpers.go

## Purpose
Provides binary protocol reader/writer helpers for the Mail.ru Cloud backend.

## Important APIs, Types, And Control Flow
`BinWriter` wraps a byte buffer and writes unsigned varints, signed-as-uvarint values, zero-terminated strings, raw buffers, and length-prefixed buffers. `BinReader` wraps a counting buffered reader, stores the first parse error, and exposes reads for bytes, shorts, little-endian uint16, uvarints, fixed byte counts, length-prefixed bytes, zero-terminated strings, and Unix dates. Parse errors set `err`; non-EOF parse errors also panic through `check`.

## State And Persistence
Reader state is current byte position and first error; writer state is accumulated request bytes. No external persistence.

## Dependencies And Integration Points
Uses `encoding/binary`, `bufio`, rclone `readers.CountingReader`, and Mail.ru binary constants. Higher-level API code uses these helpers to serialize operations and parse opaque binary responses.

## Risks And Test Signals
Risks include panic-on-malformed-response behavior, partial `Read` handling with `bufio.Reader.Read`, unchecked large lengths causing allocations, uvarint treatment of signed values, and zero-termination validation. Tests should cover malformed EOF, invalid length, nonzero terminator, count tracking, and round-trip writer/reader sequences.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mailru/api/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mailru/api/m1.go -->
# sources/user-network-fs/rclone/backend/mailru/api/m1.go

## Purpose
Defines Mail.ru Cloud M1 JSON API endpoints, error types, and response structures.

## Important APIs, Types, And Control Flow
Exports server URLs for API, public links, dispatch, and OAuth plus OAuth client ID. `ServerErrorResponse` and `FileErrorResponse` implement `error`. Response structs model user info, list items, item info, folder info, cleanup responses, and generic status/body responses with nested JSON fields for quota, billing, UI settings, file metadata, folder counts, and account identity.

## State And Persistence
No runtime state; structs are JSON marshal/unmarshal contracts.

## Dependencies And Integration Points
Consumed by the Mail.ru backend's REST calls for auth, listing, quota/user info, cleanup, file/folder metadata, and error handling. Complements the binary protocol definitions in `bin.go`.

## Risks And Test Signals
Risks include API schema drift, incomplete error message normalization, optional fields represented with concrete zero values, and mixed string/int status forms across endpoints. Tests should unmarshal recorded API responses for success and error cases and assert error strings are useful.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/mailru/api/m1.go -->
