# Research: subset-b-009768

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gui/gui_test.go -->
# sources/user-network-fs/rclone/cmd/gui/gui_test.go

Purpose: exercises the GUI HTTP-serving helpers, especially login URL construction, origin normalization, GUI asset source selection, and SPA/static asset serving. The tests are in package `gui`, so they cover unexported helpers such as `buildLoginURL`, `originFromURL`, `guiSourceFS`, and `guiHandler`.

Important functions: `writeTestDir` and `writeTestZip` create temporary GUI bundles; `handlerForSource` wraps directory/zip sources in the production handler; `newTestHandler` uses embedded assets and skips when the dist bundle is unavailable. Test cases verify directory and zip `fs.FS` handling, missing/invalid source errors, index serving, asset serving, fallback routing, and gzip content negotiation.

Control flow and state: tests allocate temporary files with `t.TempDir`, register cleanup callbacks for source filesystems, then use `httptest` with a chi router/middleware-like handler stack. Persistence is limited to temporary test fixtures and skipped embedded-bundle tests.

Dependencies/integration: standard `archive/zip`, `compress/gzip`, `io/fs`, `httptest`, chi, and testify. Risks are mostly fixture drift with the real GUI bundle and content-encoding behavior. Test signal is strong for handler behavior but intentionally conditional for embedded assets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/gui/gui_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/hashsum/hashsum.go -->
# sources/user-network-fs/rclone/cmd/hashsum/hashsum.go

Purpose: implements `rclone hashsum`, a generic hash listing/checking command for remote objects or stdin data. It also exposes reusable flags/helpers used by dedicated hash commands such as `md5sum` and `sha1sum`.

Important APIs: global flags `OutputBase64`, `DownloadFlag`, `HashsumOutfile`, `ChecksumFile`; `AddHashsumFlags`; `GetHashsumOutput`; `CreateFromStdinArg`; Cobra `commandDefinition`. `CreateFromStdinArg` detects omitted remote or `-` with piped stdin and delegates to `operations.HashSumStream`.

Control flow: command accepts zero to two args. Zero args print `hash.HelpString`; otherwise it parses `hash.Type`, handles stdin, creates the source Fs, and runs either `operations.CheckSum` against `--checkfile` or `operations.HashLister`, optionally writing to `--output-file`.

State/persistence: mutable package globals hold CLI flag state; output files are created/truncated with `os.Create`; stdin mode consumes process stdin. Dependencies include `cmd`, `fs/hash`, `operations`, pflag/cobra. Risks include package-global leakage in tests and overwrite behavior for output files. Test signals are indirect through md5sum/sha1sum and operations tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/hashsum/hashsum.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/help.go -->
# sources/user-network-fs/rclone/cmd/help.go

Purpose: defines the root Cobra command and help subcommands for rclone. It centralizes usage templates, global flag registration, backend help rendering, and command traversal/completion setup.

Important APIs/types/functions: `Root`, `GeneratingDocs`, `helpCommand`, `helpFlags`, `helpBackends`, `helpBackend`, `runRoot`, `setupRootCommand`, `traverseCommands`, `showBackends`, `showBackend`, and templates `usageTemplate`, flag templates, and `docFlagsTemplate`. It registers config/filter/rc/log global flags and attaches Cobra template functions that group flags.

Control flow: `setupRootCommand` adds globals, usage templates, help commands, flag filters, and valid-args functions recursively. `runRoot` prints version or usage and maps missing commands to `errorCommandNotFound`. Backend helpers enumerate registered backends, sort display rows, and print option metadata.

State/persistence: package-level filter state controls help output; `PersistentPostRun` logs final version/args and runs `atexit`. Dependencies include rclone config/filter/log/rc flag registries and Cobra. Risks include template/filter global state carrying across generated-doc runs. Test signals likely come from command/docs tests outside this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/help.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/link/link.go -->
# sources/user-network-fs/rclone/cmd/link/link.go

Purpose: implements `rclone link`, creating, retrieving, expiring, or removing public links for files or folders.

Important state/APIs: package globals `expire` and `unlink`; flags `--expire` and `--unlink`; Cobra `commandDefinition`. It calls `cmd.NewFsFile` to split remote path and `operations.PublicLink` to perform backend-specific public-link behavior.

Control flow: validates exactly one path, builds source filesystem plus remote leaf, then runs a non-mutating stats wrapper via `cmd.Run(false, false, ...)`. If `PublicLink` returns a non-empty link, it prints it as the final line.

State/persistence: no local persistence, but it may create or remove remote-side shared-link state depending on backend capabilities. Dependencies are `cmd`, `fs.Duration`, `operations`, Cobra. Risks center on backend capability differences, expiration support, and unlink being ignored by unsupported remotes. Tests are not in this subset; coverage is likely in backend/operations public-link tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/link/link.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/listremotes/listremotes.go -->
# sources/user-network-fs/rclone/cmd/listremotes/listremotes.go

Purpose: implements `rclone listremotes`, listing configured remotes from config files and environment definitions with filtering, sorting, long output, and JSON output.

Important APIs: filter globals (`filterName`, `filterType`, `filterSource`, `filterDescription`, `exactMatch`), output globals (`listLong`, `jsonOutput`, `orderBy`), `compileFilters`, `includeRemote`, `newLess`, and Cobra `commandDefinition`. `lessFn` composes multi-column stable sorting over `config.Remote`.

Control flow: optional positional filter applies to all attributes; named filters are converted with `filter.GlobStringToRegexp`; `config.GetRemotes` returns remotes; matching remotes are compacted in-place, optionally sorted, then printed as JSON array, tabular long rows, or `name:` lines.

State/persistence: reads rclone config/environment remote registry but does not modify it. Package globals represent flag values. Dependencies include `fs/config`, `filter`, JSON, regexp, sort. Risks include globals in unit tests, glob-vs-exact semantics, and JSON streamed manually rather than through an encoder. Test signal covers fuzzy/exact type and positional filters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/listremotes/listremotes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/listremotes/listremotes_test.go -->
# sources/user-network-fs/rclone/cmd/listremotes/listremotes_test.go

Purpose: unit-tests the filtering semantics for `listremotes`.

Important functions: `resetFilterFlags`, `TestTypeFilterDefaultIsFuzzy`, `TestTypeFilterExactMatchesWholeValue`, and `TestPositionalFilterExactAlsoMatchesWholeValue`. Tests call `compileFilters` and `includeRemote` directly against synthetic `config.Remote` values.

Control flow/state: tests mutate package-level filter globals, then use `t.Cleanup` to reset them. They assert that default matching is case-insensitive non-anchored glob matching while `--exact` matches complete values and still ignores case.

Dependencies/integration: testify assertions and rclone `config.Remote`. Risks are limited to package-global flag leakage if future tests forget cleanup. Test signal is narrow but valuable for a behavior users might misinterpret: `--type box` matching `dropbox` unless `--exact` is supplied.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/listremotes/listremotes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/ls/ls.go -->
# sources/user-network-fs/rclone/cmd/ls/ls.go

Purpose: implements `rclone ls`, the human-readable recursive object listing with size and path.

Important API: Cobra `commandDefinition` registered on `cmd.Root`. It uses shared list help from `cmd/ls/lshelp` and delegates behavior to `operations.List`.

Control flow: requires exactly one `remote:path`, creates a source filesystem via `cmd.NewFsSrc`, then runs `operations.List(context.Background(), fsrc, os.Stdout)` through `cmd.Run(false, false, ...)`.

State/persistence: read-only against the remote and writes only stdout. Dependencies are minimal: root command, list help, and operations. Risks are mainly inherited from filtering/global max-depth behavior and `operations.List` traversal. No direct tests here; behavior is covered through operations/listing tests and command integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/ls/ls.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/ls/lshelp/lshelp.go -->
# sources/user-network-fs/rclone/cmd/ls/lshelp/lshelp.go

Purpose: provides shared help text for list-family commands (`ls`, `lsl`, `lsd`, `lsf`, `lsjson`) to keep docs consistent.

Important API: exported `Help` string. The raw text uses `|` as a placeholder, then `strings.ReplaceAll` converts it to backticks for Markdown.

Control flow/state: no runtime behavior beyond package initialization. It documents recursion defaults, filtering applicability, ListR/fast-list behavior, and behavior on nonexistent directories.

Dependencies/integration: imported by command packages to append common help. Risks are documentation drift when list command behavior changes. There are no direct tests; generated docs or command help output indirectly exercise it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/ls/lshelp/lshelp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/lsd/lsd.go -->
# sources/user-network-fs/rclone/cmd/lsd/lsd.go

Purpose: implements `rclone lsd`, listing directories/containers/buckets with size, modtime, object count, and name.

Important APIs/state: package global `recurse`; Cobra command with `--recursive/-R`; `operations.ListDir`. When recursive is requested it sets `fs.GetConfig(ctx).MaxDepth = 0`.

Control flow: validates one source arg, optionally changes global config max depth, builds source Fs, and runs `operations.ListDir` to stdout.

State/persistence: read-only remote listing and stdout output, but it mutates the process-wide config `MaxDepth` for recursive behavior. Dependencies include command root, list help, `fs.GetConfig`, flags, and operations. Risks include global config mutation during tests/concurrent command contexts and backend directory-count uncertainty. Test signals are likely indirect via operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/lsd/lsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/lsf/lsf.go -->
# sources/user-network-fs/rclone/cmd/lsf/lsf.go

Purpose: implements `rclone lsf`, a script-friendly list command with configurable field order, separators, CSV mode, recursion, hash selection, IDs, encrypted names, tier, metadata, and absolute paths.

Important APIs/state: package globals `format`, `timeFormat`, `separator`, `dirSlash`, `recurse`, `hashType`, `filesOnly`, `dirsOnly`, `csv`, `absolute`; exported `Lsf(ctx, fsrc, out)`. `Lsf` builds `operations.ListFormat` and `operations.ListJSONOpt` from format characters.

Control flow: command validates one source, adjusts default separator to comma when `--csv` is used without explicit separator, then calls `Lsf`. `Lsf` maps each format rune to a ListFormat field and opt toggle; unknown runes return an error. It calls `operations.ListJSON` and prints one formatted item per line, normalizing directory size to `-1`.

State/persistence: no persistence; writes to provided writer. Risks include mutable package globals in tests and `timeFormat == "max"` rewriting the global. Dependencies include `operations.ListJSON`, hash types, and shared help. Test coverage is detailed for defaults, recursion, dir slash, format fields, separator, custom time, and max precision.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/lsf/lsf.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/lsf/lsf_test.go -->
# sources/user-network-fs/rclone/cmd/lsf/lsf_test.go

Purpose: unit-tests `Lsf` formatting behavior against local `testfiles`.

Important tests: `TestDefaultLsf`, `TestRecurseFlag`, `TestDirSlashFlag`, `TestFormat`, `TestSeparator`, `TestWholeLsf`, `TestTimeFormat`, and `TestTimeFormatMax`. They compare exact output strings and derive expected modtimes from `list.DirSorted` when timestamps are involved.

Control flow/state: tests initialize rclone test config, create a local Fs, mutate package globals for flags, call `Lsf` into a buffer, and then manually reset globals. Persistence is limited to fixture reads.

Dependencies/integration: local backend import, `fstest`, `fs.NewFs`, `list`, `operations.FormatForLSFPrecision`, testify. Risks: manual global cleanup is easy to miss and can make tests order-sensitive; exact fixture ordering depends on list sorting. Coverage is strong for the public helper but not command flag parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/lsf/lsf_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/lsjson/lsjson.go -->
# sources/user-network-fs/rclone/cmd/lsjson/lsjson.go

Purpose: implements `rclone lsjson`, outputting directory/file metadata as JSON, either as an array listing or a single `--stat` item.

Important state/APIs: global `opt operations.ListJSONOpt` and `statOnly`; flags for recursion, hashes, modtime/mimetype suppression, encrypted/original IDs, files-only/dirs-only, metadata, hash type, and stat mode. It delegates to `operations.ListJSON` and `operations.StatJSON`.

Control flow: before creating backends, it mirrors `opt.Metadata` to global config so backend metadata paths are enabled. In stat mode it uses `cmd.NewFsFile`, marshals one item with `json.MarshalIndent`, and prints. Listing mode streams a JSON array manually with comma handling and compact per-item JSON.

State/persistence: read-only remote access and stdout writes. It mutates package/global option state and config metadata flag. Risks include partial JSON output if an error occurs after opening `[`, global `opt` reuse in tests, and backend-specific optional fields. Test signal is likely in operations JSON tests, not this wrapper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/lsjson/lsjson.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/lsl/lsl.go -->
# sources/user-network-fs/rclone/cmd/lsl/lsl.go

Purpose: implements `rclone lsl`, recursively listing objects with modification time, size, and path.

Important API: Cobra `commandDefinition` and `operations.ListLong`. It appends shared list help and is marked in Filter/Listing groups.

Control flow: validates exactly one source arg, creates source Fs, and runs `operations.ListLong(context.Background(), fsrc, os.Stdout)` through `cmd.Run(false, false, ...)`.

State/persistence: read-only remote traversal, stdout only. Dependencies are command root, shared list help, and operations. Risks are inherited from backend modtime precision and recursive traversal cost. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/lsl/lsl.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/md5sum/md5sum.go -->
# sources/user-network-fs/rclone/cmd/md5sum/md5sum.go

Purpose: implements `rclone md5sum` as a dedicated wrapper around hashsum behavior with fixed `hash.MD5`.

Important APIs: Cobra `commandDefinition`; shared flags from `hashsum.AddHashsumFlags`; `hashsum.CreateFromStdinArg`, `GetHashsumOutput`, and globals; operations `CheckSum` and `HashLister`.

Control flow: accepts zero or one remote path, first allowing stdin hashing if no arg or `-` with piped data. For remote mode it creates a source Fs and either validates against `--checkfile` or lists MD5 hashes, optionally with `--download`, `--base64`, and `--output-file`.

State/persistence: can read stdin, create/truncate output files, and read checksum files. No remote mutation. Risks mirror `hashsum`: package-global shared flag state and output-file overwrite. Test signal likely comes from hashsum/operations and command integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/md5sum/md5sum.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mkdir/mkdir.go -->
# sources/user-network-fs/rclone/cmd/mkdir/mkdir.go

Purpose: implements `rclone mkdir`, creating the destination path if possible.

Important API: Cobra `commandDefinition`; uses `cmd.NewFsDir` and `operations.Mkdir`. It logs a warning when the target backend cannot have empty directories and the root contains a slash, because the operation may be a no-op.

Control flow: validates exactly one remote path, builds a directory Fs, warns on empty-directory-incapable backends, then runs `operations.Mkdir(ctx, fdst, "")` through `cmd.Run(true, false, ...)`.

State/persistence: mutates remote directory/container state when supported. Dependencies are `cmd`, `fs`, `operations`, strings, Cobra. Risks include user confusion on bucket/object stores that cannot represent empty directories. Test signals are probably in operations/backend tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mkdir/mkdir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/dir.go -->
# sources/user-network-fs/rclone/cmd/mount/dir.go

Purpose: Linux-only bazil FUSE directory node adapter for rclone VFS directories. It implements directory attributes, lookup, listing, create, mkdir, remove, rename, fsync, links, and symlinks.

Important APIs/types: `Dir` embeds `*vfs.Dir` with `*FS`; implements bazil `fusefs.Node`, `NodeSetattrer`, `NodeRequestLookuper`, `HandleReadDirAller`, `NodeCreater`, `NodeMkdirer`, `NodeRemover`, `NodeRenamer`, `NodeFsyncer`, `NodeLinker`, `NodeSymlinker`, and `NodeMknoder`.

Control flow: lookups call `vfs.Dir.Stat`, reuse cached FUSE nodes via `vfs.Node.Sys`, and set entry cache timeout. `ReadDirAll` maps VFS entries to FUSE dirents, skips names over `mountlib.MaxLeafSize`, and marks symlinks. Create/mkdir wrap VFS creation and cache new nodes. Rename delegates to VFS and invalidates the destination entry asynchronously to avoid deadlocks. Symlink creates a VFS symlink and wraps it as a file node; `Mknod` rejects device nodes but creates/closes a regular file for NFS clients that prefer mknod.

State/persistence: mutates remote/VFS namespace for create, mkdir, remove, rename, symlink, modtime, and sync. Dependencies are bazil fuse, mountlib, VFS, and error translation in `fs.go`. Risks include node-cache consistency, async invalidation races, unsupported hard links, and long-name skipping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/dir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/file.go -->
# sources/user-network-fs/rclone/cmd/mount/file.go

Purpose: Linux-only bazil FUSE file node adapter for rclone VFS files.

Important APIs/types: `File` embeds `*vfs.File` with `*FS`; implements `fusefs.Node`, `NodeSetattrer`, `NodeOpener`, `NodeFsyncer`, xattr interfaces returning `ENOSYS`, and `NodeReadlinker`.

Control flow: `Attr` fills uid/gid, mode, size, block count, and times from VFS. `Setattr` supports mtime and truncate unless VFS disables modtime. `Open` passes FUSE flags through to VFS, returns a `FileHandle`, and requests direct I/O when size is unknown or configured. `Readlink` delegates to VFS symlink support.

State/persistence: remote/VFS mutation occurs on truncate and modtime changes; open handles may later mutate via writes. No local persistence. Dependencies are bazil fuse, VFS, and package error translation. Risks include direct-IO performance tradeoffs, mode masking of append-only, xattr unsupported behavior, and backend support for truncate/modtime/symlink.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/fs.go -->
# sources/user-network-fs/rclone/cmd/mount/fs.go

Purpose: Linux-only top-level bazil FUSE filesystem wrapper around rclone VFS.

Important APIs/types: `FS` contains `*vfs.VFS`, underlying `fs.Fs`, `*mountlib.Options`, and bazil server pointer. `NewFS`, `Root`, `Statfs`, and `translateError` are the key functions.

Control flow: `Root` obtains the VFS root directory and wraps it in a `Dir`. `Statfs` maps VFS capacity to FUSE block stats and clips platform-limited block counts via `mountlib.ClipBlocks`. `translateError` maps VFS/rclone sentinel errors to errno values and logs unknown I/O errors.

State/persistence: owns references to live VFS and FUSE server but no persistent data. Dependencies are bazil fuse, rclone `fserrors`, `vfs`, and mountlib. Risks are incomplete error mapping and capacity values derived from remotes with unknown quota. No direct tests here; mount integration tests exercise it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/handle.go -->
# sources/user-network-fs/rclone/cmd/mount/handle.go

Purpose: Linux-only bazil FUSE file handle wrapper around `vfs.Handle`.

Important APIs/types: `FileHandle` embeds `vfs.Handle` and implements `HandleReader`, `HandleWriter`, `HandleFlusher`, and `HandleReleaser`.

Control flow: `Read` calls `ReadAt` into the FUSE response slice and treats `io.EOF` as successful short read. `Write` calls `WriteAt` and returns byte count. `Flush` sends buffered writes to VFS; `Release` closes the handle. All errors pass through package `translateError`.

State/persistence: handle operations may read, write, flush, and release remote object content through the VFS cache layer. Dependencies are bazil fuse and VFS. Risks include repeated flush semantics, ignored release errors by kernel, and backend writeback failures surfacing late. Test coverage comes through mount/VFS integration rather than unit tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/handle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/mount.go -->
# sources/user-network-fs/rclone/cmd/mount/mount.go

Purpose: Linux-only bazil FUSE backend for `rclone mount`.

Important APIs: `init` registers the visible `mount` command and RC mount type; `mountOptions` converts `mountlib.Options` and VFS options to bazil `fuse.MountOption`s; `mount` performs overlap/non-empty checks, mounts, starts the server goroutine, and returns async error/unmount handles.

Control flow: rejects overlapping local source/mount paths and non-empty mountpoints unless allowed, enables FUSE debug callback, calls `fuse.Mount`, creates `FS` and bazil server, serves in a goroutine, and closes the connection when serving ends. Unmount shuts down VFS before `fuse.Unmount`.

State/persistence: creates a kernel mount and VFS cache state; unmount tears both down. Dependencies are bazil fuse, mountlib lifecycle, and VFS. Risks include unsupported `--allow-root`, ignored `-o/--option` and `--fuse-flag`, serve goroutine error handling, and platform-specific FUSE behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/mount_test.go -->
# sources/user-network-fs/rclone/cmd/mount/mount_test.go

Purpose: runs the generic VFS mount test suite against the bazil `mount` backend.

Important API: `TestMount` calls `vfstest.RunTests(t, false, vfscommon.CacheModeWrites, false, mount)`.

Control flow/state: the test harness creates a mounted VFS with write cache mode and exercises filesystem operations through the OS mountpoint. Persistence is test-local but depends on kernel FUSE availability.

Dependencies/integration: `vfstest` supplies broad behavioral coverage and `vfscommon.CacheModeWrites` sets cache policy. Risks include environmental flakiness on hosts without FUSE permissions or kernel support. The file itself is small, but the integration signal is broad for read/write/list/remove behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/mount_unsupported.go -->
# sources/user-network-fs/rclone/cmd/mount/mount_unsupported.go

Purpose: build-tag stub for unsupported platforms (`!linux`) for the bazil mount package.

Important behavior: imports only `mountlib` and registers `mountlib.NewMountCommand("mount", false, nil)` during init.

Control flow/state: no actual mount function exists; the command is still present but will fail through shared mountlib behavior if invoked. No persistence.

Dependencies/integration: keeps command registration consistent across platforms. Risks are user-facing error clarity when the mount function is nil. Test coverage is platform/build-matrix dependent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/mount_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/test/seek_speed.go -->
# sources/user-network-fs/rclone/cmd/mount/test/seek_speed.go

Purpose: standalone diagnostic tool for measuring random seek/read performance on a single file, intended for mount performance experiments rather than production command behavior.

Important APIs/state: flags `--size` and `--n` configure byte range and iteration count. `randomSeekTest` repeatedly chooses random offsets, seeks, reads one byte, and reports aggregate rate.

Control flow: `main` parses flags, opens the provided file, and runs the benchmark. The test loop uses `math/rand` global source and `time.Since` for throughput.

State/persistence: read-only file access; output to stdout. Dependencies are standard `flag`, `os`, `math/rand`, `time`. Risks include non-cryptographic random, minimal error context, and synthetic one-byte reads that may not represent real workloads. No automated tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/test/seek_speed.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/test/seeker.go -->
# sources/user-network-fs/rclone/cmd/mount/test/seeker.go

Purpose: standalone correctness/performance tool comparing random seeks and byte reads between two files, useful for validating mounted files against a reference.

Important APIs/state: flags `--size` and `--n`; `randomSeekTest(size, in1, in2, file1, file2)` validates that both files return identical bytes at random offsets.

Control flow: `main` parses two filenames, opens both, and runs `n` random seeks. On seek/read mismatch it panics or exits fatally; on success it prints elapsed time and rate.

State/persistence: read-only file access. Dependencies are standard flag/log/os/rand/time. Risks include one-byte sampling missing larger-range defects and dependence on provided size rather than actual file size. No automated tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/test/seeker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/test/seekers.go -->
# sources/user-network-fs/rclone/cmd/mount/test/seekers.go

Purpose: standalone stress tool that launches many concurrent random-seek readers over files in a directory tree, intended to exercise mount concurrency and cache behavior.

Important APIs/state: flags `--size`, `--n`, `--tries`, `--maxsleep`, `--stats`; `findFiles` walks a directory; `seekTest` opens a random file, optionally sleeps, then performs random one-byte reads. A shared stats goroutine prints runtime memory stats if enabled.

Control flow: `main` discovers files, starts optional stats ticker, then launches `tries` goroutines staggered by one second. Completion is tracked by a channel.

State/persistence: read-only file access, stdout/stderr logging. Dependencies include `filepath.Walk`, random, runtime metrics. Risks include using global `math/rand` concurrently, noisy timing, and test-only fatal process exits. No automated tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount/test/seekers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount2/file.go -->
# sources/user-network-fs/rclone/cmd/mount2/file.go

Purpose: go-fuse v2 file handle adapter for rclone VFS handles.

Important APIs/types: `FileHandle` with `vfs.Handle` and `*FS`; `newFileHandle`; implementations for `FileHandle`, `FileReader`, `FileWriter`, `FileFlusher`, `FileReleaser`, `FileFsyncer`, `FileGetattrer`, and `FileSetattrer`.

Control flow: `Read`/`Write` call VFS `ReadAt`/`WriteAt`, converting EOF to success for short reads. `Flush`, `Release`, and `Fsync` forward to VFS flush/release/sync. `Getattr` and `Setattr` populate go-fuse attr structs; `Setattr` supports truncate and mtime on the underlying node.

State/persistence: handle operations read and mutate remote content through VFS cache/writeback. Dependencies are go-fuse v2 and VFS. Risks include late write errors on flush/fsync, attribute updates on handle vs node paths, and kernel ignoring release errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount2/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount2/fs.go -->
# sources/user-network-fs/rclone/cmd/mount2/fs.go

Purpose: go-fuse v2 top-level FS wrapper around rclone VFS.

Important APIs/types: `FS` holds `*vfs.VFS`, underlying `fs.Fs`, and mount options. `Root`, `SetDebug`, `getMode`, `setAttr`, `setAttrOut`, `setEntryOut`, and `translateError` are central helpers.

Control flow: `Root` wraps VFS root with `newNode`. Attribute helpers convert Go `os.FileInfo` mode/time/size to go-fuse `Attr`/`EntryOut` with mount attr timeouts. `translateError` maps VFS and fs sentinel errors to syscall errno values, returning `EIO` for unknown errors after logging.

State/persistence: owns VFS references only. Dependencies are go-fuse v2, mountlib, fserrors, VFS. Risks include mode conversion for symlinks/special files and incomplete error mapping. Test signal comes from mount2 integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount2/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount2/mount.go -->
# sources/user-network-fs/rclone/cmd/mount2/mount.go

Purpose: go-fuse v2 mount backend registered as hidden `mount2` command and RC mount type.

Important APIs: `mountOptions` builds `fuse.MountOptions`; `mount` validates mountpoint, builds `FS`, creates NodeFS/server, waits for mount readiness, and returns async error/unmount handles.

Control flow: options propagate allow-other/root, default permissions, read-only, idmapped mount, direct FUSE debug, max read-ahead/write, disabled xattrs and readdirplus. macOS-specific options set volume name and suppress Apple metadata files. `server.Serve` runs in a goroutine; `server.WaitMount` blocks until ready.

State/persistence: creates kernel FUSE mount and VFS state. Unmount shuts down VFS then calls `server.Unmount`. Dependencies are go-fuse v2, mountlib, VFS, runtime OS. Risks include unsupported writeback-cache, option differences versus bazil backend, server goroutine always sending nil, and hidden command behavior. Integration tests exercise it via `vfstest`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount2/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount2/mount_test.go -->
# sources/user-network-fs/rclone/cmd/mount2/mount_test.go

Purpose: runs generic VFS mount tests against the go-fuse `mount2` backend.

Important API: `TestMount` calls `vfstest.RunTests(t, false, vfscommon.CacheModeWrites, false, mount)`.

Control flow/state: the shared harness mounts a test filesystem with write caching and executes filesystem operations through the OS mountpoint. It depends on platform build tags (`linux || darwin/amd64`) and FUSE availability.

Dependencies/integration: `vfstest` and `vfscommon`. Risks are environment-specific failures rather than logic in this file. The test is a broad integration signal for `mount2` file, node, and fs adapters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount2/mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount2/mount_unsupported.go -->
# sources/user-network-fs/rclone/cmd/mount2/mount_unsupported.go

Purpose: build-tag stub for platforms where go-fuse mount2 is unsupported (`!linux && !(darwin && amd64)`).

Important behavior: registers hidden `mount2` command with nil mount function through `mountlib.NewMountCommand`.

Control flow/state: no real mount implementation or persistence. It keeps command registration/doc shape consistent while preventing backend use on unsupported platforms.

Dependencies/integration: mountlib command registration. Risks include nil mount function user errors if command is invoked through hidden or RC paths. Coverage comes from build matrix.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount2/mount_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount2/node.go -->
# sources/user-network-fs/rclone/cmd/mount2/node.go

Purpose: go-fuse v2 inode/node adapter for rclone VFS files and directories, implementing lookup, directory streams, create/remove/rename, symlinks, attributes, statfs, and open.

Important APIs/types: `Node` embeds `fusefs.Inode` and stores `vfs.Node`; `newNode` caches one FUSE node per VFS node via `Sys`; `dirStream` implements `DirStream` and `FileSeekdirer`.

Control flow: lookups require directory VFS nodes and create child inodes with stable mode attrs. `Readdir` opens the VFS directory, reads all entries, and returns a stream that includes `.` and `..`; `Seekdir(0)` enables repeated directory reads. Namespace mutations call VFS `Mkdir`, `Create`, `Remove`, `Rename`, and symlink APIs, then return go-fuse inodes/attrs. `Open` returns a VFS-backed file handle and direct-I/O flags when needed.

State/persistence: mutates remote namespace/content through VFS. Maintains VFS node-to-FUSE node cache in `Sys`. Dependencies are go-fuse, mountlib, VFS. Risks include stale cached nodes, no inode numbers, unsupported xattrs, directory read all-at-once memory, and rename flag ignorance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mount2/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mountlib/check_linux.go -->
# sources/user-network-fs/rclone/cmd/mountlib/check_linux.go

Purpose: Linux-specific mountpoint readiness and emptiness checks using mountinfo.

Important APIs: `CheckMountEmpty`, `singleEntryFilter`, `CheckMountReady`, and `CanCheckMountReady = true`. `CheckMountEmpty` first verifies that the mountpoint is not already a mount, then falls back to directory emptiness.

Control flow: `CheckMountReady` opens mountinfo, filters for the exact mountpoint, and expects exactly one entry; errors distinguish not mounted, duplicate entries, and mountinfo parse/open failures.

State/persistence: read-only inspection of `/proc` mount state and mountpoint directory. Dependencies include `github.com/moby/sys/mountinfo` and shared `checkMountEmpty`. Risks include path normalization/mount namespace differences and transient mountinfo races during mount startup. Tests are mostly integration via mount daemon wait behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mountlib/check_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mountlib/check_other.go -->
# sources/user-network-fs/rclone/cmd/mountlib/check_other.go

Purpose: non-Linux fallback for mount emptiness/readiness checks.

Important APIs: `CheckMountEmpty`, `CheckMountReady`, and `CanCheckMountReady = false`. `CheckMountEmpty` delegates to generic directory listing; `CheckMountReady` is a no-op because reliable mount readiness detection is unavailable.

Control flow/state: no persistent state; readiness wait on these platforms relies on fixed daemon wait timing rather than probing. Dependencies are minimal.

Risks: daemonized mounts can report readiness only by elapsed wait, so slow mounts may still not be ready and failed mounts may be detected only by daemon process death. Coverage is platform/integration dependent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mountlib/check_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mountlib/mount.go -->
# sources/user-network-fs/rclone/cmd/mountlib/mount.go

Purpose: shared mount command/lifecycle library for FUSE-like backends (`mount`, `cmount`, `mount2`, `nfsmount`). It defines options, command construction, daemon handling, VFS setup, wait, and unmount lifecycle.

Important APIs/types: embedded `mountHelp`, `OptionsInfo`, `Options`, `MountFn`, `UnmountFn`, `MountPoint`, `NewMountPoint`, global `Opt`, `AddFlags`, `WaitMountReady`, `NewMountCommand`, and `MountPoint` methods `Mount`, `Wait`, `Unmount`.

Control flow: `NewMountCommand` validates args, adjusts daemon config, sets fallback PATH, optionally starts stats, builds `MountPoint`, calls `Mount`, then either waits in foreground or waits for daemon readiness. `Mount` defaults volume/device names, optionally daemonizes, builds `vfs.New`, calls backend `MountFn`, and records actual mountpoint/time. `Wait` listens for backend errors and finalizes unmount through `atexit`.

State/persistence: creates live VFS state and OS mounts; daemon mode forks process; global `Opt` is flag-backed. Dependencies include config, daemonize, systemd, atexit, vfs flags. Risks include nil mount functions on unsupported builds, daemon readiness platform differences, cleanup on externally unmounted paths, and global option mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mountlib/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mountlib/rc.go -->
# sources/user-network-fs/rclone/cmd/mountlib/rc.go

Purpose: exposes mount lifecycle over rclone RC: create, unmount, list types, list mounts, and unmount all.

Important APIs/state: mutex `mountMu`, maps `mountFns` and `liveMounts`, `supportedMountTypes`, `ResolveMountMethod`, `AddRc`, RC handlers `mountRc`, `unMountRc`, `mountTypesRc`, `listMountsRc`, `unmountAll`, and JSON-facing `MountInfo`.

Control flow: mount backends register with `AddRc`. `mountRc` parses `fs`, `mountPoint`, optional mount/vfs options, rejects daemon mode, resolves backend, creates/mounts `MountPoint`, starts a goroutine to `Wait` and remove from `liveMounts`, then stores and returns actual mountpoint. Unmount handlers find live mounts under mutex and call `Unmount`.

State/persistence: maintains process-local live mount registry and OS mounts. Dependencies include `fs/rc` and VFS options. Risks include holding `mountMu` during potentially slow mount setup, unsynchronized captured `err` in wait goroutine, registry inconsistencies if unmount races with wait cleanup, and daemon unsupported over API. Tests cover registration, error cases, mount/list/unmount on capable systems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mountlib/rc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mountlib/rc_test.go -->
# sources/user-network-fs/rclone/cmd/mountlib/rc_test.go

Purpose: integration-tests RC mount endpoints with a local backend.

Important flow: imports local, cmount, mount, and mount2 for registration; installs config; retrieves RC calls; creates a local source with `file.txt`; calls `mount/types`; checks error cases; mounts local source; stats file through mountpoint; checks `mount/listmounts`; unmounts and verifies empty list.

State/persistence: uses temp directories and real OS mountpoints; may remove mountpoint on Windows. It sleeps briefly before unmount to avoid OS immediate-use races.

Dependencies/integration: `rc.Calls`, `configfile.Install`, platform runtime, testify, and `testy.SkipUnreliable` on Darwin. Risks are environmental: missing FUSE privileges, CI hangs, OS timing. Test signal is high-value for RC lifecycle but conditional.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mountlib/rc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mountlib/utils.go -->
# sources/user-network-fs/rclone/cmd/mountlib/utils.go

Purpose: shared mount utility helpers for capacity clipping, local path overlap checks, non-empty mountpoint enforcement, and default volume/device names.

Important APIs: `ClipBlocks`, `CheckOverlap`, `absPath`, `CheckAllowNonEmpty`, `checkMountEmpty`, `MountPoint.SetVolumeName`, `Options.SetVolumeName`, and `MountPoint.SetDeviceName`.

Control flow: `CheckOverlap` only applies to local-like remotes, normalizes symlinks/absolute paths/trailing slashes, and rejects either path being a prefix of the other. `checkMountEmpty` opens the mountpoint and attempts one directory read. Name setters default to `fs.ConfigString`, sanitize `:` and `/`, and truncate Windows volume names.

State/persistence: read-only path inspection; mutates option fields. Dependencies include filesystem path APIs and rclone `fs`. Risks include prefix-based overlap false positives for edge path normalization, mountpoint directory read permissions, and platform-specific volume limits. Coverage is indirect via mount tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/mountlib/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/move/move.go -->
# sources/user-network-fs/rclone/cmd/move/move.go

Purpose: implements `rclone move`, moving directory contents or a same-name source file into a destination.

Important APIs/state: flags `--delete-empty-src-dirs`, `--create-empty-src-dirs`, logger flag options, `operationsflags.ConfigureLoggers`, `sync.MoveDir`, and `operations.MoveFile`.

Control flow: validates two args, splits source file vs directory with `cmd.NewFsSrcFileDst`, configures optional transfer loggers, attaches logger to context if requested, then calls `sync.MoveDir` for directory roots or `MoveFile` for a single source file.

State/persistence: mutates source and destination remotes and can delete source data; may write logger outputs depending on flags. Dependencies include sync/operations and logger flags. Risks are data loss, source/destination overlap semantics, global logger option state, and empty-directory flags on backends without real directories. Test signal is likely in sync/operations integration suites.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/move/move.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/moveto/moveto.go -->
# sources/user-network-fs/rclone/cmd/moveto/moveto.go

Purpose: implements `rclone moveto`, moving or renaming a file to a specific destination path, or moving a directory to a target directory.

Important APIs/state: logger flag globals; `cmd.NewFsSrcDstFiles`; `operations.MoveFile`; `sync.MoveDir`.

Control flow: validates two args, splits source/destination filesystem and file names. After optional logger configuration, directory sources call `sync.MoveDir(ctx, fdst, fsrc, false, false)` while file sources call `operations.MoveFile(ctx, fdst, fsrc, dstFileName, srcFileName)`.

State/persistence: mutates source/destination remotes and deletes source on success. Dependencies are command parsing, operations logging, sync/move. Risks include data loss/overwrite, directory mode using fixed false empty-dir flags, and logger global state. Tests are indirect in operations/sync command coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/moveto/moveto.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/ncdu/ncdu.go -->
# sources/user-network-fs/rclone/cmd/ncdu/ncdu.go

Purpose: implements interactive terminal UI for exploring remote disk usage, modeled after ncdu.

Important APIs/types: Cobra `commandDefinition`; `helpText`; `UI` state struct; drawing helpers (`Print`, `Line`, `Box`, `Draw`); navigation/delete/sort methods; `ncduSort`; `NewUI`; `scan`; `Run`; `key`.

Control flow: command creates source Fs and runs `NewUI(fsrc).Run()`. `Run` initializes tcell, redirects logs into a bounded in-memory buffer to avoid screen corruption, starts a background scanner, and selects over root, scan errors, update notifications, and keyboard events. Drawing computes per-entry attrs, flags unread/error/unknown-size/empty dirs, optional graph/count/average/modtime columns, and popup boxes. Deletes are synchronous after confirmation using `operations.DeleteFile` or `operations.Purge`, then mutate the in-memory scan tree.

State/persistence: UI keeps cursor positions, sort flags, selections, scan cancel function, and current tree. It can permanently delete remote files/directories. Dependencies include tcell, clipboard, runewidth/uniseg, scan package, operations. Risks: synchronous deletes block UI, scan/update races with UI tree reads, selection keyed by entry string, and terminal/log redirection edge cases. Test signal is mostly scan package tests; UI itself is not directly unit-tested.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/ncdu/ncdu.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/ncdu/ncdu_unsupported.go -->
# sources/user-network-fs/rclone/cmd/ncdu/ncdu_unsupported.go

Purpose: unsupported-platform stub for `ncdu` on Plan 9, js, and AIX builds.

Important behavior: package init is empty and no command is registered.

Control flow/state: no runtime behavior and no persistence. It prevents dependencies such as tcell/clipboard from being required where unsupported.

Dependencies/integration: build tags select this file instead of the real UI. Risks are command absence on those platforms needing clear documentation. Coverage is by build matrix.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/ncdu/ncdu_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/ncdu/scan/scan.go -->
# sources/user-network-fs/rclone/cmd/ncdu/scan/scan.go

Purpose: concurrently scans an rclone Fs into an in-memory directory tree with accumulated size/count metadata for ncdu.

Important APIs/types: `Dir`, `Attrs`, `AverageSize`, `Parent`, `Path`, `newDir`, `Entries`, `Remove`, `GetDir`, `Attr`, `AttrI`, `AttrWithModTimeI`, and `Scan`.

Control flow: `Scan` starts a goroutine running `walk.Walk`; each walked directory creates a `Dir`, attaches to its parent via a map, sends root once, and signals coalesced updates. `newDir` counts file sizes, tracks unknown sizes, stores read errors, and propagates totals/error flags to parents. `Remove` updates entries, child directory map, and parent totals after UI deletions.

State/persistence: all state is in-memory and protected by per-Dir mutexes for mutable totals/entries. It reads remotes but does not mutate them. Dependencies are `fs/walk`, `fs.DirEntries`, slices, sync. Risks include sending multiple errors on a buffered channel of size one, parent lookup assumptions based on walk order, and partial tree accuracy when read errors occur. Tests cover size/count propagation, unknown sizes, attrs, removal, and scan basics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/ncdu/scan/scan.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/ncdu/scan/scan_test.go -->
# sources/user-network-fs/rclone/cmd/ncdu/scan/scan_test.go

Purpose: unit-tests ncdu scan tree construction, aggregate attributes, unknown-size behavior, read-error propagation, modtime access, and in-memory removal updates.

Important helpers/tests: `indexByName`, `fileEntry`, `TestScan`, `TestAttrsAverageSize`, `TestNewDirSizeAndCount`, `TestNewDirUnknownSize`, `TestNewDirReadErrorSetsEntriesHaveErrors`, `TestAttrIFile`, `TestAttrIDirLoaded`, `TestAttrIDirUnloaded`, `TestAttrWithModTimeI`, and removal propagation tests.

Control flow/state: tests construct mock dirs/objects or scan local fixtures, then inspect `Dir` methods. Removal tests verify parent totals and entries mutate correctly.

Dependencies/integration: local backend, `fstest`, `mockdir`, `mockobject`, testify. Risks: some tests call unexported `newDir`, tightly coupling to implementation; `TestScan` depends on fixture layout from another command directory. Coverage is strong for scan invariants and regression-prone aggregate accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/ncdu/scan/scan_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/nfsmount/nfsmount.go -->
# sources/user-network-fs/rclone/cmd/nfsmount/nfsmount.go

Purpose: Unix-only experimental mount backend that exposes the VFS through rclone’s NFS server and then invokes the system NFS mount command.

Important APIs/state: package globals `sudo` and `mountPath`; init registers `nfsmount` via mountlib and RC, adds `--sudo`, `--nfs-mount-path`, and NFS server flags. `mount` starts `nfs.NewServer`, discovers its random port, invokes `mount`, and returns unmount/async error handles.

Control flow: after NFS server starts, it builds mount options for `port`, `mountport`, `tcp`, extra `-o` options/flags, optionally prefixes `sudo`, and mounts `localhost:<mountPath>` to the mountpoint. Unmount uses `diskutil umount force` on Darwin or `umount -f`, then shuts down NFS server and VFS. `nfs.OnUnmountFunc` marks external unmount and completes async errors.

State/persistence: creates an NFS server, OS NFS mount, and VFS state. Dependencies include system `mount/umount/sudo`, `serve/nfs`, mountlib. Risks include command availability/permissions, global `nfs.OnUnmountFunc`, global `mountPath`, formatting bug using `%e` for errors, and cleanup ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/nfsmount/nfsmount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/nfsmount/nfsmount_test.go -->
# sources/user-network-fs/rclone/cmd/nfsmount/nfsmount_test.go

Purpose: integration-tests the experimental NFS mount backend, including cache modes and subpath mounting.

Important functions/tests: `commandOK`, `TestMount`, and `TestSubpathMount`. `TestMount` checks passwordless sudo mount/umount where needed, iterates NFS handle cache types, configures env vars for subprocess mount, and runs `vfstest.RunTests`. `TestSubpathMount` mounts `/sub` from a local source and verifies `hello.txt` appears at mount root.

State/persistence: uses temp directories, environment variables, actual OS mounts, and global `sudo`/`mountPath` mutation with cleanup. Dependencies include system mount tools, capabilities for symlink cache, NFS server, VFS test harness. Risks are high environmental flakiness and privilege requirements. Test signal is broad but skipped in many setups.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/nfsmount/nfsmount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/nfsmount/nfsmount_unsupported.go -->
# sources/user-network-fs/rclone/cmd/nfsmount/nfsmount_unsupported.go

Purpose: non-Unix stub for `nfsmount`.

Important behavior: init registers `nfsmount` with mountlib using a nil mount function and annotates it as introduced in v1.65.

Control flow/state: no NFS server or mount implementation. It preserves command registration shape on unsupported platforms while causing runtime failure through shared mountlib if invoked.

Dependencies/integration: mountlib. Risks include user confusion if the command appears but cannot run. Build-matrix coverage only.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/nfsmount/nfsmount_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/obscure/obscure.go -->
# sources/user-network-fs/rclone/cmd/obscure/obscure.go

Purpose: implements `rclone obscure`, transforming a plaintext password into rclone’s obscured config representation.

Important API: Cobra `commandDefinition`; it delegates to `obscure.MustObscure` and prints the result. It accepts exactly one password argument, or `-` to read the first line from stdin when stdin is piped.

Control flow: `RunE` validates args, checks `os.Stdin.Stat` for non-terminal input when arg is `-`, scans one line with `bufio.Scanner`, then obscures and prints inside `cmd.Run`. If no stdin is available, `-` is obscured literally. The long help explicitly says this is not secure encryption.

State/persistence: no file or remote mutation; stdout output only. Dependencies are `fs/config/obscure` and Cobra. Risks include shell history exposure of passwords and users misunderstanding obscuring as secure encryption. Test signals likely exist in config/obscure package, not this wrapper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/obscure/obscure.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/progress.go -->
# sources/user-network-fs/rclone/cmd/progress.go

Purpose: implements terminal progress rendering for commands using rclone accounting stats.

Important APIs/state: constants for terminal escape codes, `startProgress`, package globals `statsInterval`, `statsUnit`, and `printProgress`.

Control flow: `startProgress` intercepts log output when logs are not redirected and replaces `operations.SyncPrintf` so stdout-producing helpers can coexist with progress. A ticker prints stats at the default or configured interval; the returned stop function closes the goroutine, resets handlers, restores `SyncPrintf`, and emits a final newline. `printProgress` locks `operations.StdoutMutex`, trims stats/log text, rewinds/erases previous lines using terminal escape sequences, clips lines to terminal width, and writes through `terminal.Write`.

State/persistence: process-local goroutine/ticker and terminal output state; no files. Dependencies include accounting/stats, terminal handling, and command global flags. Risks include terminal escape issues on non-TTY/redirected output, races during shutdown, and log interleaving. Test signal likely indirect through command progress behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/progress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/purge/purge.go -->
# sources/user-network-fs/rclone/cmd/purge/purge.go

Purpose: implements `rclone purge`, deleting a path and all of its contents without obeying include/exclude filters.

Important API: Cobra `commandDefinition`; uses `cmd.NewFsDir` and `operations.Purge`.

Control flow: validates one remote path, creates directory Fs, then runs in a mutating command context. Before deletion it checks `filter.GetConfig(ctx).InActive()` and fatals if include/exclude filters are active, making the unconditional purge behavior explicit, then calls `operations.Purge(context.Background(), fdst, "")`.

State/persistence: destructive remote mutation; deletes objects/directories under the target. Dependencies are command root and operations. Risks are obvious data loss, filter bypass by design, and backend purge semantics. Test signal is mostly operations/backend integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/purge/purge.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/rc/rc.go -->
# sources/user-network-fs/rclone/cmd/rc/rc.go

Purpose: implements `rclone rc`, a CLI client for calling remote-control endpoints on a running rclone instance.

Important APIs/state: globals for URL/auth, JSON/loop/output behavior, `parseFlags`, `ParseOptions`, `setAlternateFlag`, `errorf`, `doCall`, `run`, and `list`. It supports flags for URL, method, auth, headers, options, loop/timeout, JSON input/output, and Unix socket.

Control flow: command parses flags, maps alternate flags into rc config, then `run` either lists commands or parses command path plus key/value options. `doCall` builds an HTTP client/rc client, performs calls, handles status-code errors, optionally loops until success/timeout, and prints JSON or formatted output.

State/persistence: no persistent local state; network calls can mutate the remote rclone process depending on endpoint. Dependencies include rc client/config, JSON, HTTP, timeouts. Risks include credentials on command line, option parsing ambiguity, loop retry masking transient errors, and output format assumptions. Tests are likely in rc package/client tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/rc/rc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/rcat/rcat.go -->
# sources/user-network-fs/rclone/cmd/rcat/rcat.go

Purpose: implements `rclone rcat`, streaming stdin into a remote object.

Important APIs/state: package global `size`; Cobra command with `--size` hint; delegates to `operations.RcatSize`.

Control flow: validates one destination file path, refuses terminal stdin, splits destination Fs and remote leaf, then reads from `os.Stdin` and uploads via `operations.RcatSize(context.Background(), fdst, dstFileName, os.Stdin, size, time.Now(), nil)` in a command run context.

State/persistence: consumes stdin and creates/replaces a remote object. Dependencies include cmd parsing and operations Rcat/transfer implementation. Risks include unbounded stdin, interrupted uploads that cannot always retry, incorrect `--size` causing backend failures, and destination overwrite. Test signal is likely in operations rcat tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/rcat/rcat.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/rcd/rcd.go -->
# sources/user-network-fs/rclone/cmd/rcd/rcd.go

Purpose: implements `rclone rcd`, running rclone as an RC server.

Important API: Cobra command registered on root; delegates to rclone RC server startup helpers and config flags. It is the daemon/server complement to `rclone rc`.

Control flow: validates no path args, enables RC serving configuration, and enters the RC server lifecycle through shared command/run infrastructure. It typically blocks serving requests until interrupted.

State/persistence: process-local HTTP server state; endpoints may mutate remotes/config depending on enabled RC calls. Dependencies include rc flags/server packages and command lifecycle. Risks include exposed unauthenticated control API if configured unsafely and long-running process cleanup. Test signal likely in rc server tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/rcd/rcd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/reveal/reveal.go -->
# sources/user-network-fs/rclone/cmd/reveal/reveal.go

Purpose: implements `rclone reveal`, reversing rclone’s obscured password format for inspection/debugging.

Important API: Cobra `commandDefinition`; delegates to `obscure.Reveal` and prints result.

Control flow: validates one password argument; if reveal fails, returns the error; otherwise prints plaintext to stdout.

State/persistence: no file/remote mutation, but exposes secret material on stdout. Dependencies are config obscure package and Cobra. Risks include terminal logs/shell capture leaking passwords. Tests likely live in obscure package.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/reveal/reveal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/rmdir/rmdir.go -->
# sources/user-network-fs/rclone/cmd/rmdir/rmdir.go

Purpose: implements `rclone rmdir`, removing an empty directory/path.

Important API: Cobra command; uses `cmd.NewFsDir` and `operations.Rmdir`.

Control flow: validates one remote path, creates directory Fs, then runs `operations.Rmdir(context.Background(), fdst, "")` through `cmd.Run(true, false, ...)`.

State/persistence: mutates remote directory/container state only if the target is empty and backend supports removal. Dependencies are operations and command parsing. Risks include backend differences for virtual directories and errors on non-empty paths. Test signal is in operations/backend suites.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/rmdir/rmdir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/rmdirs/rmdirs.go -->
# sources/user-network-fs/rclone/cmd/rmdirs/rmdirs.go

Purpose: implements `rclone rmdirs`, recursively removing empty directories under a path.

Important APIs/state: flags for leaving root behavior (package global in file) and Cobra command; delegates to `operations.Rmdirs`/related empty-dir removal helper.

Control flow: validates one remote path, creates source/directory Fs, and runs the recursive empty-directory removal in a mutating command context. Help explains root behavior and backend limitations.

State/persistence: destructive only for empty directories; can remove many remote directory markers. Dependencies are operations and command flags. Risks include virtual-directory backends, race with concurrent writers, and user expectations around root removal. Test signal is likely operations-level.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/rmdirs/rmdirs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate/noselfupdate.go -->
# sources/user-network-fs/rclone/cmd/selfupdate/noselfupdate.go

Purpose: build-tag alternative for `noselfupdate` builds.

Important behavior: init appends `"noselfupdate"` to `buildinfo.Tags`, exposing the build capability state in version/build metadata.

Control flow/state: no runtime command behavior and no persistence beyond mutating process build-info metadata at startup.

Dependencies/integration: `lib/buildinfo`. Risks are build-tag drift with docs/tests that assume `selfupdate` exists or that version output includes the tag. Coverage is build-matrix dependent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate/noselfupdate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate/selfupdate.go -->
# sources/user-network-fs/rclone/cmd/selfupdate/selfupdate.go

Purpose: implements `rclone selfupdate`, downloading and installing a newer rclone binary or Linux package.

Important APIs/types: `Options`, global `Opt`, Cobra `cmdSelfUpdate`, `GetVersion`, `InstallUpdate`, `installPackage`, `replaceExecutable`, `makeRandomExeName`, `downloadUpdate`, `verifyAccess`, `findFileHash`, `extractZipToFile`, and `downloadFile`.

Control flow: command validates package/check/root/platform constraints, then `InstallUpdate` rejects conflicting beta/stable flags and static cmount capability loss, resolves target version/site, handles check-only, package install, output path, temp names, access checks, download, hash verification for stable releases, zip extraction, and executable replacement. Windows replacement saves the running executable as `.old.exe` or randomized old name.

State/persistence: writes temp files, replaces target executable or installs packages with `dpkg/rpm`, makes network requests to rclone download sites, and may leave old Windows executable. Dependencies include fshttp, buildinfo, random, version command, cmount capability, zip/sha256. Risks include self-replacement failure, permissions, network/hash availability, beta lacking hash verification, package install side effects, and platform-specific executable locking. Tests cover version parsing, Linux output install, permissions/temp cleanup, and Windows rename behavior but are marked unreliable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate/selfupdate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate/selfupdate_test.go -->
# sources/user-network-fs/rclone/cmd/selfupdate/selfupdate_test.go

Purpose: integration-tests self-update version resolution and executable replacement on Linux/Windows.

Important tests: `TestGetVersion` checks beta prefixing, stable semantic validation, and minor-to-latest-micro lookup. `TestInstallOnLinux` downloads beta to a temp output path, verifies no-op same-version, non-writable errors, permission preservation, temp cleanup, and executable version. `TestRenameOnWindows` checks `.old.exe` handling while executables are running and randomized old names.

State/persistence: downloads real release artifacts, writes temp executables, changes permissions, starts subprocesses, and relies on network/download site. Dependencies include `testy.SkipUnreliable`, `os/exec`, runtime platform checks, and fs.Version.

Risks/test signal: high-value end-to-end coverage but intentionally unreliable and platform-specific. It may be skipped often; failures can indicate network, permission, package availability, or Windows file-locking behavior rather than pure code regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/selfupdate/selfupdate_test.go -->
