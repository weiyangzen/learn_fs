# subset-b-009767 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cachestats/cachestats.go -->
# sources/user-network-fs/rclone/cmd/cachestats/cachestats.go

## Purpose

This build-tagged command keeps the deprecated `rclone cachestats` entry point available on supported platforms. It prints JSON cache backend statistics for a `backend/cache` remote and directs users toward the newer `rclone backend stats` path.

## Important APIs, Types, and Functions

`init` registers `commandDefinition` on `cmd.Root`. The Cobra command validates one `source:` argument, builds an Fs with `cmd.NewFsSrc`, unwraps through `Features().UnWrap` when needed, requires a `*cache.Fs`, calls `Stats`, and formats the resulting map with `json.MarshalIndent`.

## Control Flow

The command emits a deprecation log, enters `cmd.Run` without retries or stats, resolves the source, rejects non-cache remotes, marshals stats, and writes to stdout.

## State and Persistence Behavior

It does not mutate the remote. It reads in-memory or backend-owned cache state and produces transient stdout output.

## Dependencies and Integration Points

It integrates with Cobra command registration, the rclone root command helpers, `backend/cache`, Fs feature unwrapping, and JSON output.

## Risks and Test Signals

Risks are stale compatibility with a deprecated backend, type assertion failures through wrappers, and unsupported-platform build behavior. Tests should cover direct cache Fs, wrapped cache Fs, non-cache errors, JSON marshal shape, and deprecation visibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cachestats/cachestats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cachestats/cachestats_unsupported.go -->
# sources/user-network-fs/rclone/cmd/cachestats/cachestats_unsupported.go

## Purpose

This Plan 9 and JS build-tag placeholder keeps the `cachestats` package buildable where the cache backend command is not compiled.

## Important APIs, Types, and Functions

The file declares only `package cachestats`; it exports no command, functions, state, or types.

## Control Flow

There is no runtime control flow. Package import succeeds without registering a command.

## State and Persistence Behavior

No state is read or persisted.

## Dependencies and Integration Points

The only integration point is Go build selection via `//go:build plan9 || js`, preventing "no buildable Go source files" errors for the package.

## Risks and Test Signals

Risk is accidental command availability assumptions on unsupported targets. Build-matrix tests for Plan 9/JS should confirm the package compiles and no cachestats command registration is required.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cachestats/cachestats_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cat/cat.go -->
# sources/user-network-fs/rclone/cmd/cat/cat.go

## Purpose

`cat.go` implements `rclone cat`, streaming one file or a filtered tree of files to stdout, discard, or another writer, with optional byte-range selection and separators between objects.

## Important APIs, Types, and Functions

Package globals hold flag state: `head`, `tail`, `offset`, `count`, `discard`, and `separator`. `init` registers the command and flags. The Cobra `Run` validates mutually exclusive range modes, normalizes `--head` and `--tail` into `offset`/`count`, builds the source Fs with `cmd.NewFsSrc`, chooses `os.Stdout` or `io.Discard`, and calls `operations.Cat`.

## Control Flow

Argument validation happens before Fs construction. Transfer execution is delegated to `cmd.Run(false, false, ...)`, so no retry loop or stats display is requested by this command.

## State and Persistence Behavior

Remote state is read-only. Local output is stdout unless `--discard` is set; no persistent files are created by this wrapper.

## Dependencies and Integration Points

It depends on Cobra, rclone flag helpers, `cmd` Fs helpers, filtering inherited from the root command, and `fs/operations.Cat`.

## Risks and Test Signals

Risks include conflicting range flags, negative offsets on unknown-size objects, separator escaping expectations, and stdout binary output. Tests should cover range normalization, conflict rejection, discard behavior, multi-file separators, single-file filters, and operation errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cat/cat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/check/check.go -->
# sources/user-network-fs/rclone/cmd/check/check.go

## Purpose

`check.go` implements `rclone check`, comparing source and destination trees or a checksum file against a destination without mutating either remote.

## Important APIs, Types, and Functions

Global flags drive download mode, one-way comparison, report files, and `--checkfile` hash type. `AddFlags` exposes shared report flags for other commands. `FlagsHelp` provides reusable documentation. `GetCheckOpt` builds `operations.CheckOpt`, opens report writers including stdout for `-`, and returns a close function. `commandDefinition.RunE` selects normal two-Fs checking or checksum-file mode, validates hash names, and dispatches to `operations.Check`, `CheckDownload`, or `CheckSum`.

## Control Flow

The command validates arguments, creates Fs objects, then runs under `cmd.Run(false, true, ...)`. Report writers are opened inside the run function and closed with deferred cleanup.

## State and Persistence Behavior

Remote state is read-only. Optional local report files are created/truncated. Global flag variables affect one invocation.

## Dependencies and Integration Points

It integrates with `cmd.NewFsSrcDst`, `cmd.NewFsSrcFileDst`, `fs/hash`, `fs/operations`, and shared report flags used by `checksum` and `cryptcheck`.

## Risks and Test Signals

Risks include report file leaks, nil Fs use in checksum mode, hash overlap fallback to size-only behavior, stdout report interleaving, and download-mode cost. Tests should cover report open/close failures, `--checkfile` parsing, no-common-hash logging, one-way reports, and operation error propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/check/check.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/checksum/checksum.go -->
# sources/user-network-fs/rclone/cmd/checksum/checksum.go

## Purpose

`checksum.go` implements `rclone checksum`, validating a destination against a SUM-format hash file.

## Important APIs, Types, and Functions

The package has a `download` flag and imports `cmd/check` for shared report flags and help. The Cobra command requires `<hash> sumfile dst:path`, parses the hash with `hash.Type.Set`, resolves the SUM file and destination with `cmd.NewFsSrcFileDst`, builds `CheckOpt` through `check.GetCheckOpt(nil, fsrc)`, and calls `operations.CheckSum`.

## Control Flow

Argument and hash validation happen before `cmd.Run(false, true, ...)`. The report writers are opened during run execution and closed after `CheckSum`.

## State and Persistence Behavior

Remote state is read-only. It may create local report files via inherited check flags. SUM file contents are read and destination object hashes or downloaded content are compared.

## Dependencies and Integration Points

It relies on `fs/hash`, `operations.CheckSum`, and shared `check` report option plumbing.

## Risks and Test Signals

Risks include unsupported hash names, malformed SUM files, nil source Fs confusion in report options, expensive `--download`, and report path truncation. Tests should cover hash validation, SUM file-as-source argument splitting, all report outputs, download mode, and error propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/checksum/checksum.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cleanup/cleanup.go -->
# sources/user-network-fs/rclone/cmd/cleanup/cleanup.go

## Purpose

`cleanup.go` implements `rclone cleanup`, invoking a backend-specific cleanup operation such as emptying trash or deleting old versions.

## Important APIs, Types, and Functions

The command is registered in `init`. Its Cobra `Run` validates one remote argument, resolves it with `cmd.NewFsSrc`, and calls `operations.CleanUp` inside `cmd.Run(true, false, ...)`.

## Control Flow

The command uses the standard retry loop because cleanup can fail transiently. The actual behavior is entirely backend feature dependent.

## State and Persistence Behavior

This command can mutate remote-side storage, trash, or version history. It creates no local persistent state.

## Dependencies and Integration Points

It integrates with rclone's operation layer and any backend implementing cleanup semantics.

## Risks and Test Signals

Risks are backend-specific data loss, unsupported backend errors, dry-run expectations not being obvious, and retrying non-idempotent cleanup. Tests should cover unsupported remotes, a mock cleanup feature, retry classification, and preservation of normal command exit behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cleanup/cleanup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmd.go -->
# sources/user-network-fs/rclone/cmd/cmd.go

## Purpose

`cmd.go` is the central command runtime for rclone. It provides version printing, filesystem argument resolution, root command execution, retries, stats/progress lifecycle, global config initialization, backend flag registration, and exit-code mapping.

## Important APIs, Types, and Functions

Key helpers are `ShowVersion`, `NewFsFile`, `NewFsSrc`, `NewFsDir`, `NewFsSrcDst`, `NewFsSrcFileDst`, `NewFsSrcDstFiles`, and `NewFsDstFile`. `Run` wraps command work with retry accounting, stats/progress, signal handling, cache shutdown, dumps, and final exit resolution. `CheckArgs` performs fatal usage validation. `StartStats` owns a periodic stats goroutine. `initConfig` initializes global options, logging, config file loading, accounting, console behavior, rc/metrics servers, and CPU/memory profiling. `resolveExitCode`, `AddBackendFlags`, and `Main` finish process behavior.

## Control Flow

`Main` configures the root command, adds backend flags, and executes Cobra. Each command typically validates args, constructs Fs values through these helpers, and calls `Run`. `Run` invokes the command function repeatedly until success, fatal/no-retry status, retry exhaustion, or disabled retries, then exits the process.

## State and Persistence Behavior

The file pins CLI Fs cache entries, clears cache on completion, mutates global config/accounting/logging state, starts rc/metrics servers, can create profile files, and always exits via `os.Exit`.

## Dependencies and Integration Points

It ties together `fs`, `cache`, `filter`, `accounting`, `configfile`, `configflags`, `rcserver`, `sync` errors, terminal handling, atexit callbacks, build info, Cobra, and pflag.

## Risks and Test Signals

Risks include process-exit behavior in tests, global state leakage, retrying side-effecting operations, filter conflicts with single-file sources, incorrect destination file/dir inference, goroutine leaks in stats/progress, and exit-code regressions. Tests should isolate exit behavior, cover Fs helper edge cases, retry classification, profile setup errors, `--error-on-no-transfer`, backend flag generation, and cache cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/arch.go -->
# sources/user-network-fs/rclone/cmd/cmount/arch.go

## Purpose

`arch.go` reports whether cgo-FUSE support is provided for a target OS.

## Important APIs, Types, and Functions

`ProvidedBy(osName string) bool` returns true for `windows` and `darwin`, false otherwise.

## Control Flow

There is no complex flow; callers pass an OS name and receive a capability answer.

## State and Persistence Behavior

The function is stateless and has no persistence behavior.

## Dependencies and Integration Points

It integrates with build/support reporting that needs to distinguish cmount-capable platform binaries.

## Risks and Test Signals

Risk is divergence from actual build tags and platform support. Tests should compare `ProvidedBy` with the maintained cmount support matrix for linux, darwin, windows, BSDs, and unsupported OS names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/arch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/fs.go -->
# sources/user-network-fs/rclone/cmd/cmount/fs.go

## Purpose

`fs.go` adapts rclone's VFS layer to the cgofuse `FileSystemInterface`, implementing file, directory, stat, read/write, metadata, symlink, and error translation callbacks for `cmount`.

## Important APIs, Types, and Functions

`FS` stores the VFS, backing Fs, mount options, readiness channel, handle table, mutex, and destroyed flag. `NewFS` constructs it. Handle helpers `openHandle`, `getHandle`, and `closeHandle` map FUSE file handles to `vfs.Handle` objects. Callback methods include `Init`, `Destroy`, `Getattr`, `Opendir`, `Readdir`, `Statfs`, `OpenEx`, `CreateEx`, `Truncate`, `Read`, `Write`, `Flush`, `Release`, `Unlink`, `Mkdir`, `Rmdir`, `Rename`, `Utimens`, `Symlink`, `Readlink`, `Getpath`, and no-op or ENOSYS methods for unsupported operations. `translateError`, `translateOpenFlags`, and `getMode` bridge error codes, flags, and file modes.

## Control Flow

FUSE invokes callbacks concurrently. Most paths resolve a VFS node or parent directory, perform the VFS operation, translate errors to negative FUSE errno values, and log through `log.Trace`.

## State and Persistence Behavior

In-process state is the handle table and destroyed flag. Persistent effects are remote/VFS mutations for create, write, truncate, delete, rename, mkdir, rmdir, symlink, and modtime changes. Unsupported chmod/chown/access/fsync paths are no-ops.

## Dependencies and Integration Points

It depends on `mountlib`, `fs`, `fserrors`, VFS nodes/handles, cgofuse, and OS file modes. It is instantiated by `mount.go` and must satisfy cgofuse interfaces.

## Risks and Test Signals

Risks include handle-table races or leaks, off-by-one bad handle checks, direct-IO behavior for unknown sizes, Readdir offset incompatibility, errno mismatches, Windows timestamp filtering, unsupported xattrs/hardlinks, and no-op permission semantics. Tests should run VFS mount suites, concurrent open/read/write/release cases, error translation tables, directory listing with long names, modtime boundaries, and symlink support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mount.go -->
# sources/user-network-fs/rclone/cmd/cmount/mount.go

## Purpose

`mount.go` registers and runs the cgo/cgofuse-based rclone mount implementation for supported cmount builds.

## Important APIs, Types, and Functions

`init` selects command naming (`cmount` on linux, `mount` plus `cmount` alias elsewhere), registers the mount command and rc mount handler, and appends a build tag. `mountOptions` translates `mountlib.Options` and VFS settings into cgofuse/WinFsp options. `waitFor` polls for readiness. `mount` resolves the mountpoint, creates `FS` and `fuse.FileSystemHost`, sets capabilities, starts `host.Mount` in a goroutine, builds an unmount closure, waits for `FS.Init`, and returns the error channel, unmount function, and mountpoint.

## Control Flow

Startup is asynchronous but the function waits until FUSE calls `Init` or mount exits early. Unmount shuts down VFS, avoids redundant host unmount after signals or destroy, and waits for Windows mountpoint disappearance.

## State and Persistence Behavior

It creates a live kernel/user-space mount and runtime VFS state. It may expose remote mutations through mounted filesystem operations but does not write config.

## Dependencies and Integration Points

It integrates `mountlib`, `vfs`, `atexit`, build info, cgofuse, OS runtime checks, and platform mountpoint helpers.

## Risks and Test Signals

Risks include platform option drift, early mount failure races, panic handling around missing WinFsp, unmount hangs, capability mismatch, and read-only option propagation. Tests should cover mount option construction per OS, early error paths, unmount closure behavior, Windows wait loops, signal handling, and VFS integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mount_brew.go -->
# sources/user-network-fs/rclone/cmd/cmount/mount_brew.go

## Purpose

This macOS Homebrew build-tag variant registers `rclone mount` but returns a clear unsupported error because Homebrew builds lack the required FUSE support.

## Important APIs, Types, and Functions

`init` registers a mount command and `cmount` alias through `mountlib`, plus the rc mount hook. The local `mount` function matches the mountlib signature and always returns an explanatory error.

## Control Flow

Any attempt to mount reaches the stub and fails before creating VFS or cgofuse state.

## State and Persistence Behavior

No mount, remote mutation, or local persistent state is created.

## Dependencies and Integration Points

It integrates with macOS `brew` build tags, `mountlib`, and VFS only for type compatibility.

## Risks and Test Signals

Risks are misleading command availability or stale installation guidance. Build-tag tests should verify this variant compiles, registers expected aliases, and returns the exact unsupported path instead of attempting a mount.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mount_brew.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mount_test.go -->
# sources/user-network-fs/rclone/cmd/cmount/mount_test.go

## Purpose

`mount_test.go` runs the standard VFS mount test suite against the cmount implementation.

## Important APIs, Types, and Functions

`TestMount` skips unreliable macOS runs, then calls `vfstest.RunTests(t, false, vfscommon.CacheModeOff, true, mount)`. The build tags exclude unsupported cmount targets and Windows race-detector builds.

## Control Flow

The test delegates all behavioral scenarios to `vfstest`, using the package `mount` function as the mount backend under test.

## State and Persistence Behavior

Tests create temporary remotes and live mounts, then rely on the VFS test harness for cleanup.

## Dependencies and Integration Points

It integrates with `fstest/testy`, `vfstest`, `vfscommon`, and build-tag platform selection.

## Risks and Test Signals

Risk is weak local coverage when platform tests are skipped or flaky. Signals include successful VFS read/write/list/delete flows, cache-mode-off behavior, mount/unmount cleanup, and race-detector exclusions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mount_unsupported.go -->
# sources/user-network-fs/rclone/cmd/cmount/mount_unsupported.go

## Purpose

This fallback file keeps the `cmount` package buildable when cmount support is not selected or not supported.

## Important APIs, Types, and Functions

It declares only `package cmount`; there are no functions, commands, or state.

## Control Flow

No runtime code executes. Unsupported builds rely on other mount implementations or omit cmount command registration.

## State and Persistence Behavior

No state or persistence behavior exists.

## Dependencies and Integration Points

The build expression excludes supported cgo cmount platforms and Windows cmount builds. Its integration point is the Go package loader.

## Risks and Test Signals

Risk is a build-tag gap that leaves no buildable source. Matrix builds should confirm unsupported targets compile and supported targets do not accidentally pick this placeholder.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mount_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mountpoint_other.go -->
# sources/user-network-fs/rclone/cmd/cmount/mountpoint_other.go

## Purpose

`mountpoint_other.go` validates non-Windows cmount mountpoints.

## Important APIs, Types, and Functions

`getMountpoint(f fs.Fs, mountPath string, opt *mountlib.Options)` stats the mount path, requires an existing directory, checks source/mount overlap with `mountlib.CheckOverlap`, checks non-empty policy with `mountlib.CheckAllowNonEmpty`, and returns the path.

## Control Flow

Validation is sequential and returns the first error. No mount is attempted here.

## State and Persistence Behavior

The function is read-only against the local filesystem and remote Fs metadata. It does not create directories.

## Dependencies and Integration Points

It is selected for `cmount && cgo && !windows` builds and is called by `mount.go`.

## Risks and Test Signals

Risks include rejecting useful paths because they do not exist, overlap false positives, and platform-specific non-empty semantics. Tests should cover nonexistent path, file path, empty directory, non-empty directory with/without allow flag, and local remote overlap.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mountpoint_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mountpoint_windows.go -->
# sources/user-network-fs/rclone/cmd/cmount/mountpoint_windows.go

## Purpose

`mountpoint_windows.go` handles Windows cmount path interpretation for drive-letter mounts, directory mounts, default drive selection, and UNC network-share presentation.

## Important APIs, Types, and Functions

Regex-backed helpers identify drive strings, drive roots, default markers, and network share paths. `getUnusedDrive` uses `file.FindUnusedDriveLetter`. `handleDefaultMountpath`, `handleNetworkShareMountpath`, `handleLocalMountpath`, and `handleVolumeName` normalize mountpoint and volume options. `getMountpoint` logs ignored Unix-only flags, routes the mount path to the right handler, updates network mode and volume prefix, and returns the WinFsp mountpoint.

## Control Flow

Default or `*` paths allocate a free drive. UNC paths force network mode and use the UNC as volume prefix. Local paths must not already exist; non-drive directory paths are made absolute and must have an existing parent.

## State and Persistence Behavior

The function reads local filesystem and drive state but does not create the mountpoint. It mutates `mountlib.Options` fields such as `NetworkMode` and `VolumeName`.

## Dependencies and Integration Points

It integrates with Windows cgofuse/WinFsp expectations, rclone `mountlib`, Fs overlap checks, and the local drive-letter utility.

## Risks and Test Signals

Risks include UNC parsing gaps, extended-length path rejection, unexpected option mutation, drive-letter races, parent directory checks, and network mode/volume prefix mismatches. Tests should cover each regex helper, default drive allocation failure, drive-root trimming, UNC volume handling, directory parent errors, and overlap rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/mountpoint_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/completion.go -->
# sources/user-network-fs/rclone/cmd/completion.go

## Purpose

`completion.go` provides dynamic shell argument completion for rclone paths, combining configured remotes, local filesystem entries, and remote directory entries.

## Important APIs, Types, and Functions

`compLogf` writes Cobra completion debug messages. `addRemotes` completes configured remote names. `addLocalFiles` lists local directories and appends path separators for directories. `addRemoteFiles` parses the parent remote, opens it through `cache.Get`, lists root entries, and appends slash/no-space for directories. `validArgs` is the Cobra completion callback that chooses local/remotes until a valid remote path is detected, then remote entries.

## Control Flow

Completion detects whether `toComplete` parses as a remote with a colon. Without a valid remote it returns remote names and local paths; with a remote it lists remote entries. A disabled colon workaround remains as dead compatibility code.

## State and Persistence Behavior

It reads config sections, local directories, and remote listings. It does not persist state.

## Dependencies and Integration Points

It integrates with Cobra shell completion, `fs/config`, `fspath`, Fs cache, local OS directory APIs, and remote `List`.

## Risks and Test Signals

Risks include slow or side-effecting remote completion, config secrets in debug logs, path separator inconsistencies, remote parse edge cases, and stale colon workaround behavior. Tests should cover remote-name prefixes, local directory completion, remote file/directory completion, errors from parse/cache/list, and no-space directives.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/completion.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/config/config.go -->
# sources/user-network-fs/rclone/cmd/config/config.go

## Purpose

`config.go` implements the `rclone config` command tree for interactive editing, file/path display, JSON dumps, provider listing, remote create/update/delete/password, OAuth reconnect/disconnect, user info, config encryption, and connection-string output.

## Important APIs, Types, and Functions

`init` registers all subcommands. Basic commands call `config.EditConfig`, `ShowConfigLocation`, `SaveConfig`, `ShowConfig`, `ShowRedactedConfig`, `Dump`, and `JSONListProviders`. `configCreateCommand` and `configUpdateCommand` parse key/value input with `argsToMap`, share `updateRemoteOpt`, and call `doConfig` to handle normal or non-interactive JSON output. `configPasswordCommand`, reconnect/disconnect, `configUserInfoCommand`, encryption set/remove/check, and `configStringCommand` wrap backend and config APIs.

## Control Flow

Most subcommands validate argument counts, parse or resolve remotes, then invoke config or backend feature functions. Non-interactive create/update returns a JSON `fs.ConfigOut`; interactive mode shows the resulting remote.

## State and Persistence Behavior

The file can create, update, delete, encrypt, decrypt, save, and display rclone config data. Reconnect and disconnect may mutate OAuth tokens or revoke credentials. Userinfo and string commands are read-only except backend auth side effects.

## Dependencies and Integration Points

It integrates Cobra, pflag, `fs/config`, `fs/rc.Params`, backend `Features().Disconnect/UserInfo`, `fs.ConfigFs`, JSON encoding, and command flag helpers.

## Risks and Test Signals

Risks include global `updateRemoteOpt` leakage across commands, cleartext password handling, redaction incompleteness, non-interactive protocol regressions, config encryption prompt behavior, and backend feature nil checks. Tests should cover `argsToMap`, create/update key parsing, non-interactive JSON, no-output, password obscuring flags, encryption check failures, disconnect/userinfo unsupported errors, and connection string formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/config/config_test.go -->
# sources/user-network-fs/rclone/cmd/config/config_test.go

## Purpose

`config_test.go` unit-tests the key/value parser used by config create, update, and password commands.

## Important APIs, Types, and Functions

`TestArgsToMap` exercises `argsToMap` with empty input, alternating `key value`, `key=value`, mixed forms, and dangling keys.

## Control Flow

The table-driven test converts each argument slice and asserts either an exact `rc.Params` map or an error.

## State and Persistence Behavior

No config file is touched. The test is pure parser validation.

## Dependencies and Integration Points

It depends on `fs/rc.Params`, `testify/assert`, and the unexported parser in the same package.

## Risks and Test Signals

The test signals parsing correctness but does not cover duplicate keys, empty key/value strings, shell quoting, or command-level side effects. Additional tests should cover those boundaries and non-interactive config flows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/config/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/convmv/convmv.go -->
# sources/user-network-fs/rclone/cmd/convmv/convmv.go

## Purpose

`convmv.go` implements `rclone convmv`, converting object and directory names in place with the global `--name-transform` pipeline.

## Important APIs, Types, and Functions

The command registers `--delete-empty-src-dirs` and `--create-empty-src-dirs`. Its Cobra `Run` validates one destination, resolves it with `cmd.NewFsFile`, requires `transform.Transforming(context.Background())`, and chooses `sync.Transform` for directory roots or `operations.TransformFile` for single files.

## Control Flow

Execution is under `cmd.Run(false, true, ...)`. The command refuses to run unless a name transform has been configured by global transform flags. Directory transforms can remove or create empty dirs depending on flags.

## State and Persistence Behavior

It mutates remote object and directory names in place, with potential deletes for empty source dirs and creates for empty destination dirs. No local persistent files are written.

## Dependencies and Integration Points

It integrates with the root transform option system, `fs/sync.Transform`, `operations.TransformFile`, and Fs resolution helpers.

## Risks and Test Signals

Risks include data loss from name collisions, non-idempotent transforms, Unicode normalization surprises, directory/file tag confusion, and concurrency races when many inputs map to one output. Tests should cover no-transform rejection, file vs directory paths, dry-run behavior through operations, empty directory flags, conflict handling, and reversible transform cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/convmv/convmv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/convmv/convmv_test.go -->
# sources/user-network-fs/rclone/cmd/convmv/convmv_test.go

## Purpose

`convmv_test.go` validates transform behavior across representative name transformations and Unicode normalization cases.

## Important APIs, Types, and Functions

`TestMain` initializes fstest. `TestTransform` runs a table of transform/back-transform pairs, creates local and remote files with varied names, applies `sync.Transform`, compares names with `compareNames`, and checks lossless round trips where expected. Helpers include `makeTestFiles`, `deleteDSStore`, `compareNames`, `transformItems`, and `detectEncoding`. `TestUnicodeEquivalence` verifies NFC conversion for a decomposed name.

## Control Flow

Each test creates an fstest run, prepares local/remote fixtures, sets transform options, runs transforms, lists remote entries, and compares transformed expectations.

## State and Persistence Behavior

Tests create and mutate temporary local and remote files and clean `.DS_Store` artifacts that may appear on macOS.

## Dependencies and Integration Points

It integrates fstest, all backends, filter rules, operations delete, walk listing, sync transform, `lib/transform`, and Unicode normalization.

## Risks and Test Signals

Signals include broad transform coverage and Unicode equivalence. Gaps include direct command flag plumbing, collision/race behavior, dry-run, and large trees. Tests also rely on a reduced ASCII alphabet, so non-ASCII path coverage is narrower than the commented fixture suggests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/convmv/convmv_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/copy/copy.go -->
# sources/user-network-fs/rclone/cmd/copy/copy.go

## Purpose

`copy.go` implements `rclone copy`, copying source contents to a destination without deleting extra destination files.

## Important APIs, Types, and Functions

Globals hold `createEmptySrcDirs`, `loggerOpt`, and `loggerFlagsOpt`. `init` registers the command, the empty-dir flag, and operation logger flags. The Cobra `Run` resolves source/file/destination via `cmd.NewFsSrcFileDst`, configures optional loggers, injects the sync logger into context, and calls `sync.CopyDir` for directory sources or `operations.CopyFile` for single-file sources.

## Control Flow

The command runs with retries and stats. Logger setup happens inside the retry closure, so each attempt owns its logger cleanup.

## State and Persistence Behavior

It writes or updates destination objects and optionally creates empty source directories at the destination. It can create local logger output files depending on logger flags.

## Dependencies and Integration Points

It integrates with `operationsflags`, `operations.CopyFile`, `sync.CopyDir`, Fs helper parsing, filters, and global transfer accounting.

## Risks and Test Signals

Risks include source file detection edge cases, repeated logger setup on retries, empty-directory semantics, metadata/root-directory expectations, and retrying partial copies. Tests should cover file vs directory copy, logger flag outputs, empty dirs, filters, no-traverse behavior through sync, and error/retry propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/copy/copy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/copyto/copyto.go -->
# sources/user-network-fs/rclone/cmd/copyto/copyto.go

## Purpose

`copyto.go` implements `rclone copyto`, copying a file or directory to an explicit destination path/name.

## Important APIs, Types, and Functions

The package mirrors copy's logger globals and setup. `commandDefinition.Run` validates two args, resolves source and destination with `cmd.NewFsSrcDstFiles`, configures operation loggers, and chooses `sync.CopyDir` for directory sources or `operations.CopyFile` with distinct source and destination file names for file sources.

## Control Flow

It runs under `cmd.Run(true, true, ...)` with retry and stats. Destination file parsing only applies when the source resolves as a file.

## State and Persistence Behavior

It writes destination files or directory contents and can overwrite existing files if operations deem them different. Optional logger files may be created.

## Dependencies and Integration Points

It integrates with `cmd.NewFsSrcDstFiles`, `operationsflags`, `operations.CopyFile`, and `sync.CopyDir`.

## Risks and Test Signals

Risks include ambiguous missing source paths, destination file/dir inference, logger lifecycle, and retrying partially written explicit filenames. Tests should cover file renames, directory copy behavior, destination existing as file, filters, logger flags, and overwrite/no-op cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/copyto/copyto.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/copyurl/copyurl.go -->
# sources/user-network-fs/rclone/cmd/copyurl/copyurl.go

## Purpose

`copyurl.go` implements `rclone copyurl`, streaming HTTP(S) URL content directly to a remote object, stdout, or a batch of URLs from CSV.

## Important APIs, Types, and Functions

Flag globals control auto filename, Content-Disposition filename, printed filename, stdout, no-clobber, and CSV mode. `run` handles a single URL, selecting stdout, destination directory, or destination file and calling `operations.CopyURLToWriter` or injectable `copyURL`. `runURLS` reads a CSV, rejects stdout/print-filename combinations, opens destination Fs, and uses `errgroup` with `ci.Transfers` plus `errcount` to copy entries concurrently.

## Control Flow

The Cobra command validates one or two args and dispatches under `cmd.Run(true, true, ...)`. CSV rows with one field auto-name; two fields use explicit relative filenames.

## State and Persistence Behavior

It creates remote destination objects or writes URL bytes to stdout. CSV mode reads a local file and may partially complete when some rows fail.

## Dependencies and Integration Points

It integrates with `operations.CopyURL`, `CopyURLToWriter`, Fs destination helpers, transfer concurrency config, CSV parsing, errgroup cancellation context, and rclone logging.

## Risks and Test Signals

Risks include closure capture over CSV loop variables in concurrent goroutines, partial batch success, path traversal in CSV filenames, global flag leakage in tests, stdout mutation when destination is `-`, and no-clobber race behavior. Tests should cover arg validation, auto/header filenames, CSV concurrency and aggregate errors, incompatible flags, destination path joining, and copyURL injection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/copyurl/copyurl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/copyurl/copyurl_test.go -->
# sources/user-network-fs/rclone/cmd/copyurl/copyurl_test.go

## Purpose

`copyurl_test.go` unit-tests single URL and CSV batch control flow for `copyurl` with a mocked copy function.

## Important APIs, Types, and Functions

`resetGlobals` restores package flag globals and `copyURL`. Tests cover missing destination without stdout, explicit filename success, auto filename error propagation, incompatible CSV flags, and CSV fan-out with mixed success/failure.

## Control Flow

Tests set globals, create temp files/directories, replace `copyURL`, invoke `run` or `runURLS`, then assert calls, arguments, and aggregate errors.

## State and Persistence Behavior

The tests write a temporary CSV and local destination directory only. `copyURL` is mocked, so no network or remote writes occur.

## Dependencies and Integration Points

It imports the local backend for destination Fs resolution and uses `testify`, atomics, mutexes, and temp filesystem helpers.

## Risks and Test Signals

Signals cover flag combinations and parallel CSV calls. Gaps include `--stdout` success, header filename behavior, no-clobber, actual HTTP integration, CSV malformed input, and path traversal handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/copyurl/copyurl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cryptcheck/cryptcheck.go -->
# sources/user-network-fs/rclone/cmd/cryptcheck/cryptcheck.go

## Purpose

`cryptcheck.go` implements `rclone cryptcheck`, verifying that a plaintext source matches a crypt remote's encrypted objects by comparing hashes at the underlying encrypted layer.

## Important APIs, Types, and Functions

The command registers shared check report flags. `cryptCheck(ctx, fdst, fsrc)` requires `fdst` to be `*crypt.Fs`, chooses one hash from the underlying Fs, builds `check.GetCheckOpt`, and overrides `opt.Check` to unwrap crypt destination objects, read the underlying hash, compute the expected encrypted hash with `fcrypt.ComputeHash`, and report differences.

## Control Flow

The Cobra command resolves source and crypt destination, then runs `cryptCheck` through `cmd.Run(false, true, ...)`. `operations.CheckFn` performs traversal and invokes the custom comparator.

## State and Persistence Behavior

The command is read-only against remotes but may create local report files through shared check flags.

## Dependencies and Integration Points

It integrates with `backend/crypt`, shared check options, `fs/hash`, and operations check traversal.

## Risks and Test Signals

Risks include panics if destination objects are not crypt objects, no underlying hash support, missing hashes, report writer leakage, and expensive source reads for remote sources. Tests should cover non-crypt destination, no-hash underlying Fs, matching/mismatching objects, report outputs, and hash error paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cryptcheck/cryptcheck.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cryptdecode/cryptdecode.go -->
# sources/user-network-fs/rclone/cmd/cryptdecode/cryptdecode.go

## Purpose

`cryptdecode.go` implements `rclone cryptdecode`, translating crypt remote filenames to plaintext or, with `--reverse`, plaintext names to encrypted names.

## Important APIs, Types, and Functions

`Reverse` is the flag-backed mode switch. The command validates two to eleven args, calls `fs.ConfigFs` for the crypt remote, requires backend type `crypt`, constructs a `crypt.Cipher`, and dispatches to `cryptDecode` or `cryptEncode`. Those helpers build tab-separated output lines and print once.

## Control Flow

All work happens under `cmd.Run(false, false, ...)`. Decode failures are reported per filename as "Failed to decrypt" but do not return an error; encode always returns nil.

## State and Persistence Behavior

It reads crypt config and writes stdout only. No remote calls or config writes occur.

## Dependencies and Integration Points

It integrates with `backend/crypt` cipher construction, `fs.ConfigFs`, and Cobra flags.

## Risks and Test Signals

Risks include accepting invalid config values only at cipher construction, suppressing decode errors as successful exit, tabular output parsing with filenames containing tabs/newlines, and global `Reverse` leakage. Tests should cover crypt/non-crypt remotes, decode failures, reverse mode, max argument limit, and output formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cryptdecode/cryptdecode.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/dedupe/dedupe.go -->
# sources/user-network-fs/rclone/cmd/dedupe/dedupe.go

## Purpose

`dedupe.go` implements `rclone dedupe`, resolving duplicate names or duplicate hashes through interactive or selected policies.

## Important APIs, Types, and Functions

Package globals are `dedupeMode` and `byHash`. `init` registers `--dedupe-mode` and `--by-hash`. The command accepts optional mode plus remote path, parses positional mode through `dedupeMode.Set`, resolves the target Fs with `cmd.NewFsSrc`, warns if duplicate names are unsupported and `--by-hash` is absent, then calls `operations.Deduplicate`.

## Control Flow

It runs without retries or stats. Mode parsing happens before Fs operation. The operation layer handles listing, duplicate grouping, prompts, deletes, and renames.

## State and Persistence Behavior

This command can delete or rename remote objects and merge duplicate directories. It creates no local persistent files.

## Dependencies and Integration Points

It integrates with backend `DuplicateFiles` feature signaling, operations dedupe modes, global dry-run/interactive behavior, and Fs helpers.

## Risks and Test Signals

Risks include data loss, interactive prompt deadlocks in automation, hash-less backends, duplicate directory merge semantics, and positional mode ambiguity. Tests should cover every dedupe mode, `--by-hash`, unsupported duplicate names, dry-run, hash-none behavior, and conflict/rename outcomes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/dedupe/dedupe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/delete/delete.go -->
# sources/user-network-fs/rclone/cmd/delete/delete.go

## Purpose

`delete.go` implements `rclone delete`, deleting files under a remote path while respecting filters and optionally removing empty directories.

## Important APIs, Types, and Functions

The `rmdirs` flag controls empty directory cleanup. The Cobra command validates one argument, resolves the source with `cmd.NewFsSrc`, and calls `operations.Delete` inside `cmd.Run(true, false, ...)`. If `--rmdirs` is set and delete succeeds, it calls `operations.Rmdirs` with the root-preserving argument.

## Control Flow

Delete runs first; directory cleanup is conditional and only attempted after file deletion returns nil.

## State and Persistence Behavior

It mutates remote state by deleting filtered files and possibly empty directories. Dry-run and interactive behavior are enforced by lower layers.

## Dependencies and Integration Points

It integrates with global filters, Fs source helper, operations delete/rmdirs, and retry/accounting behavior.

## Risks and Test Signals

Risks include accidental data loss from filters, retrying partial deletes, misunderstanding that directories are preserved by default, and root removal policy. Tests should cover filters, dry-run, rmdirs flag, delete errors blocking rmdirs, retries, and directory-only paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/delete/delete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/deletefile/deletefile.go -->
# sources/user-network-fs/rclone/cmd/deletefile/deletefile.go

## Purpose

`deletefile.go` implements `rclone deletefile`, removing exactly one remote object without filter processing and without deleting directories.

## Important APIs, Types, and Functions

The command validates one path, resolves it with `cmd.NewFsFile`, requires a non-empty file name, gets the object with `f.NewObject`, and calls `operations.DeleteFile`.

## Control Flow

It runs under `cmd.Run(true, false, ...)`. Directory or nonexistent paths that resolve without a file name return an `fs.ErrorObjectNotFound`-wrapped error.

## State and Persistence Behavior

It deletes one remote object. No local persistent state is created.

## Dependencies and Integration Points

It uses `cmd.NewFsFile`, backend `NewObject`, `operations.DeleteFile`, and standard retry behavior.

## Risks and Test Signals

Risks include ambiguous nonexistent vs directory errors, retrying deletes after a first successful attempt, bypassing filters unexpectedly, and backend object lookup quirks. Tests should cover existing object deletion, directory rejection, missing object, dry-run/interactive lower-layer behavior, and retry classification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/deletefile/deletefile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete.go -->
# sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete.go

## Purpose

`genautocomplete.go` defines the parent `rclone completion` command and legacy `genautocomplete` alias.

## Important APIs, Types, and Functions

`init` registers `completionDefinition` on `cmd.Root`. The Cobra command contains metadata, help text, annotations, and alias but no `Run`; shell-specific subcommands provide behavior.

## Control Flow

Invoking the parent without a shell relies on Cobra help behavior. Subcommand registration happens from sibling files' init functions.

## State and Persistence Behavior

The parent command itself creates no files and mutates no state beyond command registration.

## Dependencies and Integration Points

It integrates Cobra with bash, fish, powershell, and zsh completion subcommands.

## Risks and Test Signals

Risks are alias compatibility and missing subcommand registration due to build/package changes. Tests should verify parent help, alias availability, and shell subcommands attached.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_bash.go -->
# sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_bash.go

## Purpose

`genautocomplete_bash.go` implements `rclone completion bash`.

## Important APIs, Types, and Functions

`init` attaches `bashCommandDefinition`. The command accepts optional output file, defaults to `/etc/bash_completion.d/rclone`, writes to stdout for `-` using `cmd.Root.GenBashCompletionV2`, or writes a file using `GenBashCompletionFileV2`.

## Control Flow

Argument validation allows zero or one arg. Generation errors are fatal through `fs.Fatal`.

## State and Persistence Behavior

It writes a local completion script to the default system path, a user-supplied path, or stdout.

## Dependencies and Integration Points

It depends on Cobra's bash completion generator and the fully populated root command tree.

## Risks and Test Signals

Risks include requiring root for default path, stdout redirection assumptions, command tree drift, and fatal exits in tests. Tests should verify default/custom/stdout generation and non-empty script content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_bash.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_fish.go -->
# sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_fish.go

## Purpose

`genautocomplete_fish.go` implements `rclone completion fish`.

## Important APIs, Types, and Functions

`init` attaches `fishCommandDefinition`. The command defaults output to `/etc/fish/completions/rclone.fish`, writes stdout for `-` with `cmd.Root.GenFishCompletion(os.Stdout, true)`, or writes a file through `GenFishCompletionFile`.

## Control Flow

Zero or one argument is accepted. Errors are converted to fatal command failures.

## State and Persistence Behavior

It writes a fish completion script to a local file or stdout.

## Dependencies and Integration Points

It integrates with Cobra fish completion generation and the root command tree.

## Risks and Test Signals

Risks include privileged default path, completion generator API changes, and stale command metadata. Tests should assert custom path and stdout generation produce non-empty fish script output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_fish.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_powershell.go -->
# sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_powershell.go

## Purpose

`genautocomplete_powershell.go` implements `rclone completion powershell`.

## Important APIs, Types, and Functions

`init` attaches `powershellCommandDefinition`. The command writes to stdout when no output file is supplied or the arg is `-`, using `cmd.Root.GenPowerShellCompletion`; otherwise it writes a file with `GenPowerShellCompletionFile`.

## Control Flow

The default path is stdout, unlike bash/fish/zsh. Argument validation allows zero or one arg; errors are fatal.

## State and Persistence Behavior

It writes completion script text to stdout or a chosen local file.

## Dependencies and Integration Points

It depends on Cobra PowerShell generation and rclone command registration.

## Risks and Test Signals

Risks include profile-loading assumptions, stdout capture in tests, and unsupported shell syntax after Cobra changes. Tests should cover missing arg, `-`, custom file, and non-empty generated script.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_powershell.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_test.go -->
# sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_test.go

## Purpose

`genautocomplete_test.go` verifies completion script generation for bash, zsh, and fish file and stdout paths.

## Important APIs, Types, and Functions

Tests create temporary files, invoke shell command `Run` functions directly, read output, and assert it is non-empty. Stdout tests temporarily replace `os.Stdout` with a temp file.

## Control Flow

Each test creates a temp file, defers close/remove, runs the command with either the temp path or `-`, then reads and asserts content.

## State and Persistence Behavior

Only temporary local files are created. Global `os.Stdout` is mutated briefly and restored with defer.

## Dependencies and Integration Points

It uses `testify/assert`, OS temp files, and the package command definitions.

## Risks and Test Signals

Signals are basic generation health. Gaps include PowerShell coverage, default privileged paths, content correctness, concurrency safety around `os.Stdout`, and command tree completeness assertions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_zsh.go -->
# sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_zsh.go

## Purpose

`genautocomplete_zsh.go` implements `rclone completion zsh`.

## Important APIs, Types, and Functions

`init` attaches `zshCommandDefinition`. The command defaults to `/usr/share/zsh/vendor-completions/_rclone`, writes stdout for `-` with `cmd.Root.GenZshCompletion`, or creates the target file and generates zsh completion into it.

## Control Flow

Argument validation allows zero or one arg. File creation happens manually with `os.Create`, then a deferred close ignores close errors.

## State and Persistence Behavior

It creates or truncates a local zsh completion file or writes to stdout.

## Dependencies and Integration Points

It integrates with Cobra zsh completion generation, OS file APIs, and the root command tree.

## Risks and Test Signals

Risks include root-only default path, ignored close errors, truncating existing files before generation succeeds, and shell generator drift. Tests should cover stdout, custom files, generation errors, and close/write failures where practical.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/genautocomplete/genautocomplete_zsh.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gendocs/gendocs.go -->
# sources/user-network-fs/rclone/cmd/gendocs/gendocs.go

## Purpose

`gendocs.go` implements `rclone gendocs`, generating Hugo-compatible Markdown command documentation and a global flags page from the Cobra command tree.

## Important APIs, Types, and Functions

`frontmatter` and `frontmatterTemplate` define generated page metadata. The command creates the output tree, executes `help flags` into `flags.md`, builds command alias/annotation metadata recursively, customizes Cobra doc generation with a prepender and link handler, then walks generated files to replace inherited-option sections with grouped flag help and normalize headings.

## Control Flow

Generation proceeds in phases: create dirs, render flags, collect command details, run `doc.GenMarkdownTreeCustom`, then munge each generated command page. Certain mount docs are skipped on platforms where commands are unavailable.

## State and Persistence Behavior

It writes and rewrites many local Markdown files under the requested output directory and toggles `cmd.GeneratingDocs`.

## Dependencies and Integration Points

It integrates with Cobra docs, root command metadata, rclone flag groups, `lib/file.MkdirAll`, runtime GOOS checks, templates, regexes, and generated website frontmatter conventions.

## Risks and Test Signals

Risks include command/detail map mismatches, brittle string cut points, platform-specific skipped docs, annotation/frontmatter escaping, global command args/output mutation, and broad file rewrites. Tests should generate docs into temp dirs, verify frontmatter, flags page, aliases, group help insertion, skipped platform docs, and idempotence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gendocs/gendocs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/configparse.go -->
# sources/user-network-fs/rclone/cmd/gitannex/configparse.go

## Purpose

`configparse.go` defines the git-annex special remote configuration keys and validates the rclone remote/backend value received from git-annex.

## Important APIs, Types, and Functions

`configID` identifies remote name, prefix, and layout values. `configDefinition` stores canonical names, synonyms, descriptions, and defaults. `requiredConfigs` defines `rcloneremotename/target`, `rcloneprefix/prefix`, and `rclonelayout/rclone_layout`. `getCanonicalName` and `fullDescription` format protocol responses. `validateRemoteName` accepts an exact configured remote, a remote fspath without path, or a colon-prefixed backend with options.

## Control Flow

Validation first checks configured remote names, then parses as fspath, rejects embedded path components, checks parsed remote names, and finally validates colon-prefixed backend names with `fs.Find`.

## State and Persistence Behavior

It reads configured remote names and backend registry only. No config is written.

## Dependencies and Integration Points

It integrates with git-annex config negotiation in `gitannex.go`, `fs/config`, `fspath.Parse`, and the rclone backend registry.

## Risks and Test Signals

Risks include accepting backend strings in user contexts, rejecting valid env-defined remotes if registry/config lookup changes, whitespace preservation surprises, and synonym drift with legacy git-annex-remote-rclone. Tests should cover exact remotes, env remotes, backends with options, nonexistent backends, embedded paths, and descriptions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/configparse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/e2e_test.go -->
# sources/user-network-fs/rclone/cmd/gitannex/e2e_test.go

## Purpose

`e2e_test.go` runs integration tests against real `git-annex`, the rclone binary on PATH, and local rclone config to verify the built-in git-annex remote works and remains layout-compatible with `git-annex-remote-rclone`.

## Important APIs, Types, and Functions

Helpers verify rclone binary version, count remote files, search contents, create an isolated HOME/PATH/repo context, install the `git-annex-remote-rclone-builtin` symlink, write rclone config, and run commands in the temp repo. `skipE2eTestIfNecessary` gates short mode, fstest remotes, OS support, rclone version, and `git-annex` availability. Tests cover `testremote`, migration from externaltype `rclone`, and cross-remote layout compatibility for all layout modes.

## Control Flow

Each test creates a temp git-annex repository, initializes remotes with layout parameters, writes annexed files, runs copy/fsck/drop workflows, and checks local remote storage state.

## State and Persistence Behavior

Tests create temp repositories, configs, symlinks, git commits, and local remote storage. Cleanup is temp-dir based with explicit annex drops for read-only objects.

## Dependencies and Integration Points

They integrate with external `git`, `git-annex`, `git-annex-remote-rclone`, rclone CLI, local backend config, build tags, and layout modes.

## Risks and Test Signals

Signals are high-value end-to-end compatibility. Risks include environmental flakiness, PATH version mismatch, unsupported Windows HOME semantics, missing external tools, parallel temp repo load, and tests skipped in common developer setups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/e2e_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/gitannex.go -->
# sources/user-network-fs/rclone/cmd/gitannex/gitannex.go

## Purpose

`gitannex.go` implements `rclone gitannex`, an external special remote protocol server allowing git-annex to store, retrieve, check, and remove annex keys through rclone remotes.

## Important APIs, Types, and Functions

`maybeTransformArgs` inserts the `gitannex` subcommand when invoked through the `git-annex-remote-rclone-builtin` symlink. `messageParser` parses line protocol commands with space-delimited leading parameters and a final parameter that may contain spaces. `server` holds reader/writer, verbosity, negotiated extension booleans, and cached config. Handler methods implement `run`, `handleInitRemote`, `queryConfigs`, `handlePrepare`, `handleListConfigs`, `handleTransfer`, `handleCheckPresent`, `queryDirhash`, `handleRemove`, and `handleExtensions`. The Cobra command wires stdin/stdout to a server.

## Control Flow

The server sends `VERSION 1`, then loops over git-annex messages. It negotiates config lazily, validates remotes/layouts on init, builds per-key Fs strings by layout, uses `operations.CopyFile` for STORE/RETRIEVE, `NewObject` for presence checks, and `operations.DeleteFile` for removal.

## State and Persistence Behavior

In-process state is config and extension negotiation. Persistent remote effects are storing and deleting key objects. Local effects include retrieved files. It writes protocol messages to stdout and optional transcripts to stderr.

## Dependencies and Integration Points

It integrates git-annex's external special remote protocol, rclone Fs cache, `operations`, embedded help, layout/config helpers, and Cobra aliasing.

## Risks and Test Signals

Risks include protocol desynchronization, panics on write errors, config caching across sessions, no ASYNC implementation despite tracking extension flags, layout path mistakes, partial transfer errors, missing queryConfigs in some handlers, and stdout pollution. Tests should cover parser edges, protocol handlers, remote validation, every layout, store/retrieve/remove/check flows, symlink invocation, and real git-annex e2e behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/gitannex.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/gitannex_test.go -->
# sources/user-network-fs/rclone/cmd/gitannex/gitannex_test.go

## Purpose

`gitannex_test.go` provides unit and fstest-backed protocol coverage for the git-annex special remote server.

## Important APIs, Types, and Functions

Tests cover symlink arg transformation, `messageParser`, config description formatting, Windows filepath-relative workaround, timeout behavior, and many protocol cases. `testState` wires pipe-backed stdin/stdout to a `server`, provides read/write assertions with timeouts, preconfiguration, and fstest handles. `fstestTestCases` exercise init, list configs, prepare, invalid remote/layouts, extension negotiation, transfer store/retrieve, checkpresent, remove, unsupported export, and error handling.

## Control Flow

`TestGitAnnexFstestBackendCases` creates an fstest run per case, derives remote name/prefix, starts `server.run` in a goroutine, drives protocol lines, then checks expected server errors.

## State and Persistence Behavior

Tests create temporary local/remote files through fstest, mutate server config state, and use pipes/goroutines. Some tests alter cwd and environment variables with cleanup.

## Dependencies and Integration Points

It imports all backends, fstest, fspath, testify, OS path/runtime APIs, and the package server internals.

## Risks and Test Signals

Signals are broad protocol and storage coverage. Risks include goroutine leaks on failed pipe reads, long 30s timeouts, shared cwd mutation, backend-dependent behavior, and skipped real e2e dependencies. Gaps include stdout write failures, verbose transcript, ASYNC behavior, and malformed dirhash replies beyond selected cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/gitannex_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/layout.go -->
# sources/user-network-fs/rclone/cmd/gitannex/layout.go

## Purpose

`layout.go` maps git-annex key layout modes to rclone filesystem strings so the built-in remote can match `git-annex-remote-rclone` storage layouts.

## Important APIs, Types, and Functions

`layoutMode` constants cover `lower`, `directory`, `nodir`, `mixed`, `frankencase`, and unknown. `allLayoutModes` returns supported modes. `parseLayoutMode` validates strings. `queryDirhashFunc` abstracts protocol dirhash queries. `buildFsString` joins remote name and prefix, optionally queries `DIRHASH-LOWER` or `DIRHASH`, and appends path components according to mode.

## Control Flow

`nodir` returns the prefix path directly. Lower/directory modes request lowercase dirhash; mixed/frankencase request normal dirhash. Directory mode appends key to the dirhash path, while frankencase lowercases the returned dirhash.

## State and Persistence Behavior

The file is stateless. Its output determines where persistent key objects are stored.

## Dependencies and Integration Points

It integrates with git-annex dirhash protocol messages, `fspath.JoinRootPath`, and transfer/check/remove handlers.

## Risks and Test Signals

Risks include path compatibility regressions, bad trailing colon handling, untested unknown-mode panic paths, and differences from external helper layouts. Tests should cover all modes, dirhash query failures, remote names with/without colon, prefixes, realistic keys, and cross-compatibility e2e tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gitannex/layout.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gui/gui.go -->
# sources/user-network-fs/rclone/cmd/gui/gui.go

## Purpose

`gui.go` implements `rclone gui`, serving the embedded or user-supplied rclone web UI and a paired RC API server, then opening an authenticated browser URL.

## Important APIs, Types, and Functions

Embedded `dist.zip` and `dist.tag` provide the default UI. Flags configure GUI address, API address, credentials, no-auth, browser opening, and metrics. The command resolves a GUI source with `guiSourceFS`, creates a GUI HTTP server, computes CORS origin with `originFromURL`, configures and starts an RC server, builds an SPA handler with `guiHandler`, serves compressed static assets, builds a login URL with `buildLoginURL`, optionally opens the browser, then waits for either server to exit and shuts both down.

## Control Flow

Source validation occurs before binding sockets. GUI and RC ports default to `localhost:0`. Auth credentials are generated unless disabled or supplied. The command blocks until one server stops.

## State and Persistence Behavior

It starts local HTTP listeners, may open a browser, reads embedded/zip/dir assets, and generates an in-memory random password. It does not write config.

## Dependencies and Integration Points

It integrates `lib/http`, `rcserver`, RC options, chi compression middleware, `open-golang`, systemd notification, embedded assets, zip/filesystem APIs, and the web app login contract.

## Risks and Test Signals

Risks include exposing no-auth API on non-local addresses, credentials in logged URLs, embedded zip missing, CORS origin mismatch, zip close leaks, SPA fallback serving wrong files, browser-open failures, and shutdown races. Tests should cover source FS variants, handler static/fallback/gzip behavior, login URL escaping, auth generation, metrics forwarding, and server lifecycle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gui/gui.go -->
