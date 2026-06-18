# subset-b-009771 research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/makefiles/speed.go -->
# sources/user-network-fs/rclone/cmd/test/makefiles/speed.go

## Purpose

`speed.go` implements `rclone test speed`, a destructive benchmark command that uploads, downloads, and verifies generated files against a remote. It is a test/support command rather than normal sync behavior, but it exercises core copy, cache, check, and cleanup paths.

## Important APIs, Types, and Functions

The command registers `speedCmd` under `cmd/test.Command`. Flags tune `testTime`, `fcap`, `small`, `medium`, `large`, and JSON-only output. `Stats` and `TestResult` describe file size, file count, bytes, duration, and computed `fs.SizeSuffix` speed. `measure` wraps a timed operation, and `speedTest` owns the benchmark lifecycle.

## Control Flow

`RunE` validates one remote, initializes shared test settings, runs an initial four-file 1 MiB probe, then estimates file counts for small, medium, and large test sizes from the slower measured upload/download speed. `speedTest` creates a random remote directory, local generation directory, and local download directory; generates files with `makefiles`; uploads via `sync.CopyDir`; downloads via `sync.CopyDir`; and verifies with `operations.CheckDownload`.

## State and Persistence Behavior

State is temporary but deliberately touches user remotes. Remote and local temporary directories are registered with `atexit.OnError` and purged/removed only when the error sentinel is not overwritten. Successful paths leave no intended durable state; interrupted runs can leave `rclone-speed-test-*` remote directories.

## Dependencies and Integration Points

It integrates with Cobra, rclone test common flags, `cmd.NewFsDir`, fs cache creation, random naming, file generation helpers in the same package, sync copy logic, and operations checking/purge. JSON output is produced with `encoding/json`.

## Risks and Test Signals

Risks include destructive remote writes, cleanup failure on process death, inaccurate sizing when initial samples are noisy, large local disk use from high caps, and divide-by-zero/zero-file skips for very slow remotes. Tests should use small temporary remotes, verify cleanup, cap behavior, JSON shape, integrity check failures, and remote paths with unusual separators.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/makefiles/speed.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/memory/memory.go -->
# sources/user-network-fs/rclone/cmd/test/memory/memory.go

## Purpose

`memory.go` implements `rclone test memory`, a diagnostic command that lists all objects under a remote, retains them in memory, optionally reads metadata, and reports allocation/system-memory deltas per object.

## Important APIs, Types, and Functions

The file exposes only its Cobra `commandDefinition`. The run function uses `operations.Count`, `operations.ListFn`, `runtime.GC`, `runtime.ReadMemStats`, and `fs.GetMetadata`. Formatting depends on `ConfigInfo.HumanReadable` and feature detection through `fsrc.Features().ReadMetadata`.

## Control Flow

The command validates one source remote, counts objects to size the slice, snapshots memory after a GC, lists objects into a mutex-protected slice, optionally fetching metadata to include cached metadata cost, then snapshots memory again and logs object count, allocation delta, bytes/object, and Go runtime `Sys` delta.

## State and Persistence Behavior

The command stores listed `fs.Object` instances only for the process lifetime. It does not mutate the remote, but it can warm backend metadata caches and use significant heap on large remotes. Global config is read, not modified.

## Dependencies and Integration Points

It lives under `rclone test`, uses the standard command runner, and integrates with backend listing, metadata feature flags, rclone logging, and Go runtime memory statistics.

## Risks and Test Signals

Risks include divide-by-zero when a remote has zero objects, high memory use on very large remotes, concurrent callback ordering, and backend-specific metadata side effects. Tests should cover empty remotes, metadata-supported and unsupported backends, human and raw formatting, count/list errors, and large-count capacity behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/memory/memory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/test.go -->
# sources/user-network-fs/rclone/cmd/test/test.go

## Purpose

`test.go` defines the parent `rclone test` command, a namespace for diagnostic and benchmark subcommands that may perform unusual or destructive operations.

## Important APIs, Types, and Functions

The exported `Command` is a `*cobra.Command` registered into `cmd.Root` during `init`. It contains usage/help text and version-introduction annotations; subpackages attach themselves by importing `github.com/rclone/rclone/cmd/test`.

## Control Flow

There is no execution body here. Cobra dispatch resolves a concrete subcommand such as `memory` or `speed`; this parent command primarily enforces discoverability and shared help text.

## State and Persistence Behavior

No runtime state is stored. The only state mutation is global command-tree registration during package initialization.

## Dependencies and Integration Points

It depends on rclone's root command package and Cobra. Integration is import-order driven: subcommand packages call `test.Command.AddCommand`.

## Risks and Test Signals

Risks are mostly registration or documentation drift. Tests should ensure `rclone test --help` lists expected subcommands and that annotations remain compatible with generated command docs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/touch/touch.go -->
# sources/user-network-fs/rclone/cmd/touch/touch.go

## Purpose

`touch.go` implements `rclone touch`, creating empty objects or updating modification times for files and directory contents on any rclone backend.

## Important APIs, Types, and Functions

Global flags are `notCreateNewFile`, `timeAsArgument`, `localTime`, and `recursive`. Helpers include `newFsDst`, `parseTimeArgument`, `timeOfTouch`, and `createEmptyObject`. The main API is `Touch(ctx, f, remote) error`, which is directly testable apart from Cobra.

## Control Flow

The command splits the destination path into a parent fs and basename. `Touch` chooses a timestamp, probes `f.NewObject`, handles missing objects by optionally creating an empty object, handles directories via `operations.TouchDir` with recursive or shallow mode, and updates existing files with `SetModTime` after dry-run/interactive destructive checks.

## State and Persistence Behavior

The command mutates remote object modtimes and may create zero-byte objects with metadata-derived open options. Global flag variables persist across tests/commands in process. Recursive mode deliberately never creates missing files.

## Dependencies and Integration Points

It integrates with `cmd.Run`, `fspath.Split`, backend `Put`/`NewObject`/`SetModTime`, `object.NewStaticObjectInfo`, metadata flags, and operations destructive-skip logic.

## Risks and Test Signals

Risks include global flag leakage between tests, timestamp layout ambiguity by string length, timezone surprises with `--localtime`, backend precision differences, and directory/nonexistent path behavior. Tests should cover creation, no-create, timestamp formats, recursive directories, empty remotes, dry-run, metadata creation, and unsupported modtime backends.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/touch/touch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/touch/touch_test.go -->
# sources/user-network-fs/rclone/cmd/touch/touch_test.go

## Purpose

`touch_test.go` validates `Touch` command behavior against the fstest remote harness and local backend registration.

## Important APIs, Types, and Functions

The test helper `checkFile` compares remote contents and modtime using `timeOfTouch`. `TestMain` initializes fstest. Individual tests cover new-file creation, `--no-create`, timestamp parsing, updating existing objects, nested path creation, empty names/directories, shallow and recursive directory touching, and metadata creation.

## Control Flow

Each test creates an isolated `fstest.NewRun`, mutates global command flags as needed, calls `Touch` directly, and validates remote listing/object metadata. Metadata tests temporarily modify `fs.ConfigInfo.Metadata` and `MetadataSet` and restore them with `t.Cleanup`.

## State and Persistence Behavior

The file intentionally manipulates package globals (`notCreateNewFile`, `timeAsArgument`, `recursive`) and global config. Some flag resets are manual, making isolation important when tests fail early.

## Dependencies and Integration Points

It depends on `fstest`, `backend/local`, `fs.Metadata`, and testify `require`. It exercises user-visible command logic without Cobra parsing.

## Risks and Test Signals

The suite signals expected behavior for missing paths, existing files, directories, recursion, and metadata. Gaps include explicit invalid timestamp errors, `--localtime`, dry-run/interactive skip paths, and backend precision variations beyond `fs.ModTimeNotSupported` checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/touch/touch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/tree/tree.go -->
# sources/user-network-fs/rclone/cmd/tree/tree.go

## Purpose

`tree.go` implements `rclone tree`, adapting rclone directory listings to the `github.com/a8m/tree` renderer to print a Unix-tree-like view of remotes.

## Important APIs, Types, and Functions

The command stores global `tree.Options`, output filename, report toggle, sort selector, and OS path encoder. `Tree(fsrc, outFile, opts)` is the main callable API. `FileInfo` adapts `fs.DirEntry` to `os.FileInfo`, and `Fs` adapts `dirtree.DirTree` to `tree.Fs`.

## Control Flow

The Cobra run path creates the source fs, opens output or terminal output, maps rclone flags into tree options, defaults depth from `--max-depth`, and calls `Tree`. `Tree` walks the remote into a `dirtree.DirTree`, installs the adapter on options, visits and prints the synthetic root, then optionally appends directory/file counts.

## State and Persistence Behavior

The command reads remote listings but does not mutate backends. Output may be persisted when `--output` is used. Package-level options are mutated by Cobra parsing and reused in process.

## Dependencies and Integration Points

It integrates with rclone filtering and fast-list through `walk.NewDirTree`, terminal color handling, OS filename encoding, and the external tree renderer.

## Risks and Test Signals

Risks include global option leakage, path encoding mismatches, missing output-file close handling, directory cache lookup failures, and external renderer behavior changes. Tests should cover sorting flags, depth, output files, encoding, dirs-only, hidden files, and filter interaction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/tree/tree.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/tree/tree_test.go -->
# sources/user-network-fs/rclone/cmd/tree/tree_test.go

## Purpose

`tree_test.go` gives a focused golden-output test for `Tree` rendering over the repository's `testfiles` fixture.

## Important APIs, Types, and Functions

The sole `TestTree` initializes fstest, opens a local fs for `testfiles`, calls `Tree` with a fresh `tree.Options`, and compares the exact text output.

## Control Flow

The test bypasses Cobra and global flags, writes output into a `bytes.Buffer`, and expects the root, three files, one subdirectory, two nested files, and footer counts.

## State and Persistence Behavior

It performs read-only fixture access and has no persistent state. It depends on the local backend being registered by blank import.

## Dependencies and Integration Points

The test verifies integration among `fs.NewFs`, `walk.NewDirTree`, the tree adapter, and external renderer formatting.

## Risks and Test Signals

The golden string is sensitive to renderer glyphs and ordering. It does not cover command flags, output files, color, filters, path encoding, or sort modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/tree/tree_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/version/version.go -->
# sources/user-network-fs/rclone/cmd/version/version.go

## Purpose

`version.go` implements `rclone version`, including normal build/runtime version display, online update checks, and dependency/build-info dumping.

## Important APIs, Types, and Functions

Flags are `check` and `deps`. `stripV` normalizes semver strings. `GetVersion` fetches `version.txt`, trims rclone/beta decorations, parses `Last-Modified`, and returns a semver. `CheckVersion` compares current, latest, and beta versions. `printModule` and `printDependencies` format Go build info.

## Control Flow

The command accepts no args. With `--deps` it reads build info from `os.Args[0]`. With `--check` it performs HTTP GETs through rclone's configured HTTP client. Otherwise it delegates to `cmd.ShowVersion`.

## State and Persistence Behavior

The file is read-only except stdout/stderr output and network requests. It consumes global `fs.Version`, process args, and HTTP config but does not persist data.

## Dependencies and Integration Points

It integrates with Cobra, `cmd.ShowVersion`, `fshttp`, `coreos/go-semver`, Go `debug/buildinfo`, and rclone config-aware HTTP behavior.

## Risks and Test Signals

Risks include network failures, malformed version text, missing `Last-Modified`, beta suffix trimming, semver incompatibility for dev versions, and build-info absence in unusual binaries. Tests should mock update endpoints and cover `--deps`, dev versions, inaccessible config files, and stdout handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/version/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/version/version_test.go -->
# sources/user-network-fs/rclone/cmd/version/version_test.go

## Purpose

`version_test.go` verifies that executing `rclone version` does not require a readable config file.

## Important APIs, Types, and Functions

`TestVersionWorksWithoutAccessibleConfigFile` creates a temporary config path, removes permissions on non-Windows systems, rewires `config.SetConfigPath`, nils `os.Stdout`, runs `cmd.Root` with `version`, and restores global state.

## Control Flow

The test simulates an unreadable config before invoking the Cobra root command. It asserts no panic and no returned error for the normal version path.

## State and Persistence Behavior

It mutates global config path, global stdout, and root command args, with defers restoring state. It creates and removes a temp file.

## Dependencies and Integration Points

It covers integration between the version command, config path handling, and root command execution.

## Risks and Test Signals

The test signals that version display must remain independent of config loading. It does not cover `--check`, `--deps`, network failures, or repeated root command state after execution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/version/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmdtest/cmdtest.go -->
# sources/user-network-fs/rclone/cmdtest/cmdtest.go

## Purpose

`cmdtest.go` provides a `main` entry point for end-to-end tests that execute rclone's real CLI inside the test binary.

## Important APIs, Types, and Functions

The file's `main` imports all backends and commands for side effects, calls `fsfile.Init`, initializes rclone's runtime with `cmd.Init`, sets `siginfo.SigInfoHandler` to dump goroutines, then invokes `cmd.Main`.

## Control Flow

`cmdtest_test.go` re-executes the test binary with `RCLONE_TEST_MAIN`; `TestMain` then calls this `main` so the child process behaves like the real rclone binary.

## State and Persistence Behavior

It creates normal rclone process-global state in the child process. No durable state is written here directly, though invoked commands may create configs or files.

## Dependencies and Integration Points

It integrates all command packages, all backends, fsfile initialization, signal handling, and rclone's CLI startup path.

## Risks and Test Signals

Risks are side-effect import drift and differences between test binary and production binary initialization. End-to-end tests should catch missing command/backend imports and initialization regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmdtest/cmdtest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmdtest/cmdtest_test.go -->
# sources/user-network-fs/rclone/cmdtest/cmdtest_test.go

## Purpose

`cmdtest_test.go` supplies the process-reexecution harness used by rclone CLI integration tests.

## Important APIs, Types, and Functions

`TestMain` switches between parent test mode and child CLI mode using `RCLONE_TEST_MAIN`. Helpers include `rcloneExecMain`, `rcloneEnv`, `rclone`, `getEnvInitial`, `createTestEnvironment`, `createTestFile`, `createTestFolder`, and `createSimpleTestData`.

## Control Flow

Parent tests set `RCLONE_TEST_MAIN=true` and run normal tests. Child invocations are spawned with `exec.Command(os.Args[0], args...)`, a cleaned environment without unrelated `RCLONE_` variables, optional semicolon-delimited overrides, and a test config path. The demonstration test checks version output, debug flags, unknown flag errors, env-driven logging, config creation, and local listing.

## State and Persistence Behavior

State is isolated under `t.TempDir`, with `testFolder` and `testConfig` globals set per test. Child process state is isolated by environment construction.

## Dependencies and Integration Points

It tests the real Cobra/root command path, environment parsing, local backend config, and command output/error behavior.

## Risks and Test Signals

Risks include semicolon env parsing limitations, global `envInitial` reuse across changed parent env, and platform differences in child process execution. Signals include successful real command execution, debug logging behavior, error exit status, and config-backed local listing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmdtest/cmdtest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmdtest/environment_test.go -->
# sources/user-network-fs/rclone/cmdtest/environment_test.go

## Purpose

`environment_test.go` is an end-to-end suite for rclone environment-variable parsing and precedence.

## Important APIs, Types, and Functions

The sole test uses the cmdtest harness to run actual rclone commands with controlled `RCLONE_*` variables. It validates non-backend flags, backend remote names, option precedence, alias/reference behavior, JSON logging, and string-array filter variables.

## Control Flow

The test creates local data and a config, invokes child rclone processes with different semicolon-delimited environments, and inspects command output. It covers global flags such as `RCLONE_MAX_DEPTH`, conflict handling for quiet/log-level, default help text changes, command-line overrides, remote names containing hyphens/underscores, symlink handling precedence across connection string, CLI flag, remote env, backend env, generic env, and config file values.

## State and Persistence Behavior

All data and config live under a test temp directory. The test creates symlinks when supported, rewrites `myLocal` and `myAlias` remotes, and relies on child process isolation for environment changes.

## Dependencies and Integration Points

It integrates with config creation, local and alias backends, environment-to-config conversion, flag default rendering, logging formats, JSON logging, and filter dumping.

## Risks and Test Signals

This is a high-value regression suite for option precedence. Risks include OS symlink policy, output-format brittleness, semicolon environment encoding, and global config interactions. It does not cover every backend option type, but it exercises string arrays and key precedence layers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmdtest/environment_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker-plugin/managed/Dockerfile -->
# sources/user-network-fs/rclone/contrib/docker-plugin/managed/Dockerfile

## Purpose

This Dockerfile builds the managed Docker volume plugin image for rclone by copying the rclone binary from a base image into a small Alpine runtime.

## Important APIs, Types, and Functions

The build arg `BASE_IMAGE` defaults to `rclone/rclone:latest`. Runtime setup installs `ca-certificates`, `fuse3`, and `tzdata`, creates `/data/config`, `/data/cache`, and `/mnt`, enables `user_allow_other`, and sets rclone-related environment variables.

## Control Flow

The first stage exposes `/usr/local/bin/rclone`; the final Alpine stage copies it to `/usr/bin/rclone`, prepares FUSE/config/cache/mount paths, verifies `rclone version`, sets `/data` as workdir, and launches `rclone serve docker`.

## State and Persistence Behavior

Plugin state is expected in mounted `/data/config`, `/data/cache`, and propagated `/mnt`. The image itself contains only the binary and package/runtime configuration.

## Dependencies and Integration Points

It integrates with Docker managed plugin packaging, FUSE device access, rclone Docker volume serving, proxy environment variables, and the companion `config.json`.

## Risks and Test Signals

Risks include mutable `latest` base image drift, Alpine package changes, FUSE permission requirements, and proxy/config defaults. Tests should build with pinned base images, run `rclone version`, and exercise plugin mount/create/remove flows.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker-plugin/managed/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker-plugin/managed/config.json -->
# sources/user-network-fs/rclone/contrib/docker-plugin/managed/config.json

## Purpose

`config.json` is the Docker managed-plugin manifest for the rclone volume driver.

## Important APIs, Types, and Functions

It declares the `docker.volumedriver/1.0` interface on `rclone.sock`, grants `CAP_SYS_ADMIN`, exposes `/dev/fuse`, uses host networking, sets `entrypoint` to `rclone serve docker`, and defines configurable args/env/mounts plus propagated mount `/mnt`.

## Control Flow

Docker reads this manifest when installing/enabling the plugin, creates bind mounts for config and cache, injects env vars, and starts the plugin process.

## State and Persistence Behavior

Persistent state resides in host bind mounts under `/var/lib/docker-plugins/rclone/config` and `/var/lib/docker-plugins/rclone/cache`; rclone mounts are propagated from `/mnt`.

## Dependencies and Integration Points

It couples Docker plugin metadata, rclone serve docker, host FUSE, host network namespace, and configurable proxy values.

## Risks and Test Signals

Risks include broad `CAP_SYS_ADMIN`, host networking exposure, bind mount path assumptions, and propagated mount correctness. Tests should validate Docker plugin install, settable env/args, config/cache persistence, and FUSE device availability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker-plugin/managed/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker-plugin/systemd/docker-volume-rclone.service -->
# sources/user-network-fs/rclone/contrib/docker-plugin/systemd/docker-volume-rclone.service

## Purpose

This systemd service runs rclone as a Docker volume plugin outside the managed plugin packaging flow.

## Important APIs, Types, and Functions

The unit requires Docker and the matching socket, orders itself before Docker startup, prepares volume/plugin config/cache directories, sets `RCLONE_CONFIG`, `RCLONE_CACHE_DIR`, and verbosity, and runs `/usr/bin/rclone serve docker`.

## Control Flow

systemd socket activation creates `/run/docker/plugins/rclone.sock`; the service starts before Docker so Docker can discover the volume plugin endpoint.

## State and Persistence Behavior

Persistent config and cache live under `/var/lib/docker-plugins/rclone`; volumes are under `/var/lib/docker-volumes/rclone`.

## Dependencies and Integration Points

It integrates systemd, Docker startup ordering, rclone's Docker volume server, and host filesystem directories.

## Risks and Test Signals

Risks include service ordering loops, missing FUSE permissions, stale sockets, and absent rclone binary. Tests should verify `systemctl start`, socket creation, Docker volume operations, restart behavior, and log output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker-plugin/systemd/docker-volume-rclone.service -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker-plugin/systemd/docker-volume-rclone.socket -->
# sources/user-network-fs/rclone/contrib/docker-plugin/systemd/docker-volume-rclone.socket

## Purpose

This socket unit exposes the Docker plugin Unix socket for rclone's volume driver service.

## Important APIs, Types, and Functions

It listens on `/run/docker/plugins/rclone.sock` and is installable under `sockets.target`.

## Control Flow

systemd creates the socket before the service starts, allowing Docker to connect to the rclone volume driver endpoint.

## State and Persistence Behavior

The socket is runtime state under `/run`; it is not persistent across boots.

## Dependencies and Integration Points

It pairs with `docker-volume-rclone.service` and Docker's plugin discovery path.

## Risks and Test Signals

Risks include socket path mismatch, permissions, and stale runtime files. Tests should enable/start the socket and confirm Docker can reach the plugin endpoint.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker-plugin/systemd/docker-volume-rclone.socket -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker/docker-compose.dlna-server.yml -->
# sources/user-network-fs/rclone/contrib/docker/docker-compose.dlna-server.yml

## Purpose

This compose example runs `rclone serve dlna` in a container against `remote:/`.

## Important APIs, Types, and Functions

It defines a single `rclone-dlna-server` service using `rclone/rclone`, passes command-line arguments for verbose DLNA serving, custom DLNA name, and read-only mode, uses host networking for broadcast discovery, and mounts the host rclone config read-only.

## Control Flow

Compose starts the container with host network access; rclone reads config from `/root/.config/rclone` and serves the selected remote via DLNA until stopped.

## State and Persistence Behavior

The example is read-only by default and stores no container state except logs. Host config is mounted read-only.

## Dependencies and Integration Points

It integrates Docker Compose, rclone serve dlna, host-network multicast/broadcast behavior, and host rclone remotes.

## Risks and Test Signals

Risks include old compose syntax, host-network portability, exposing media over the LAN, and missing local-volume mappings for remotes that reference local paths. Tests should run compose config validation and a DLNA discovery/client smoke test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker/docker-compose.dlna-server.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker/docker-compose.webdav-server.yml -->
# sources/user-network-fs/rclone/contrib/docker/docker-compose.webdav-server.yml

## Purpose

This compose example runs `rclone serve webdav` in a container against `remote:/`.

## Important APIs, Types, and Functions

It defines `rclone-webdav-server`, uses `rclone/rclone`, enables verbose read-only WebDAV serving, documents optional address/port mappings, uses host networking by default, and mounts the host rclone config read-only.

## Control Flow

Compose starts rclone in serve-webdav mode; with host networking, the default loopback bind remains accessible on the host. Users can uncomment `--addr 0.0.0.0:8080` and port mapping for bridge networking.

## State and Persistence Behavior

The example serves data read-only and persists no container data. Host config is mounted read-only.

## Dependencies and Integration Points

It integrates Docker Compose, rclone serve webdav, host network or port mapping, and host-configured remotes.

## Risks and Test Signals

Risks include accidental network exposure if binding to `0.0.0.0`, missing local path mounts, and legacy compose syntax. Tests should validate compose syntax, confirm WebDAV listing/read, and verify read-only write rejection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/contrib/docker/docker-compose.webdav-server.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/config.json -->
# sources/user-network-fs/rclone/docs/config.json

## Purpose

`docs/config.json` is the Hugo site configuration for rclone.org documentation.

## Important APIs, Types, and Functions

It defines taxonomy index names, base URL, title/description, ignored files, Git info, disabled taxonomy kind, table-of-contents bounds, Goldmark parser/renderer settings, and syntax-highlighting class output.

## Control Flow

Hugo reads this config during docs builds, applies ignored-file filters, renders markdown with configured heading IDs and unsafe HTML disabled, and builds menus/tags/groups from indexes.

## State and Persistence Behavior

No runtime state is stored. Build output depends on this config and source content.

## Dependencies and Integration Points

It integrates with Hugo, Goldmark, rclone docs layouts, data files, and generated command/backend pages.

## Risks and Test Signals

Risks include broken anchors from heading-ID changes, missing taxonomy output expected by templates, unsafe HTML behavior changes, and base URL drift. Tests should run the Hugo build and check generated links, TOC, and backend data pages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/config.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/content/install.sh -->
# sources/user-network-fs/rclone/docs/content/install.sh

## Purpose

`install.sh` is the public curl-piped installer for rclone release or beta binaries.

## Important APIs, Types, and Functions

It accepts an optional `beta` argument, detects unzip tools (`unzip`, `7z`, `busybox`), compares installed and current versions, detects OS/architecture, downloads the matching zip, extracts it, installs binary and man page, and exits with documented status codes.

## Control Flow

The script creates a temp directory, chooses an unzip tool, sets `XDG_CONFIG_HOME` to avoid root-owned user config, fetches release metadata, exits if current, maps `uname` OS/arch to rclone download names, downloads and extracts, installs into platform-specific locations, refreshes man databases where available, removes the temp directory, and prints a success message.

## State and Persistence Behavior

It mutates system paths such as `/usr/bin/rclone`, `/usr/local/bin/rclone`, and man directories. Temporary files are removed only on the normal path; early errors may leave temp dirs because no trap is installed.

## Dependencies and Integration Points

It depends on Bash, curl, one unzip implementation, uname, root permissions, optional mandb/makewhatis, and rclone download endpoints.

## Risks and Test Signals

Risks include curl-pipe trust, partial installs, missing cleanup trap, unsupported OS/arch mappings, beta/release endpoint failures, and permission differences. Tests should shellcheck, run in Linux/macOS/BSD containers where possible, mock download endpoints, and verify exit codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/content/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/alias.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/alias.yaml

## Purpose

`alias.yaml` is a Hugo data record describing the rclone `alias` backend as `Alias` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=alias`, `name=Alias`, `tier=Tier 1`, `maintainers=Core`, `features_score=7`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=True`, `remote=None`, `features` (0 entries), `hashes` (0 entries), and `precision=None`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/alias.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/archive.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/archive.yaml

## Purpose

`archive.yaml` is a Hugo data record describing the rclone `archive` backend as `Archive` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=archive`, `name=Archive`, `tier=Tier 3`, `maintainers=Core`, `features_score=3`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=True`, `remote=TestArchive:`, `features` (14 entries), `hashes` (13 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/archive.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/azureblob.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/azureblob.yaml

## Purpose

`azureblob.yaml` is a Hugo data record describing the rclone `azureblob` backend as `Azure Blob` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=azureblob`, `name=Azure Blob`, `tier=Tier 1`, `maintainers=Core`, `features_score=7`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestAzureBlob:`, `features` (17 entries), `hashes` (1 entries), and `precision=1`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/azureblob.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/azurefiles.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/azurefiles.yaml

## Purpose

`azurefiles.yaml` is a Hugo data record describing the rclone `azurefiles` backend as `Azure Files` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=azurefiles`, `name=Azure Files`, `tier=Tier 2`, `maintainers=Core`, `features_score=6`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestAzureFiles:`, `features` (13 entries), `hashes` (1 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/azurefiles.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/b2.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/b2.yaml

## Purpose

`b2.yaml` is a Hugo data record describing the rclone `b2` backend as `B2` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=b2`, `name=B2`, `tier=Tier 1`, `maintainers=Core`, `features_score=6`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestB2:`, `features` (14 entries), `hashes` (1 entries), and `precision=1000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/b2.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/box.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/box.yaml

## Purpose

`box.yaml` is a Hugo data record describing the rclone `box` backend as `Box` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=box`, `name=Box`, `tier=Tier 1`, `maintainers=Core`, `features_score=6`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestBox:`, `features` (15 entries), `hashes` (1 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/box.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/cache.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/cache.yaml

## Purpose

`cache.yaml` is a Hugo data record describing the rclone `cache` backend as `Cache` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=cache`, `name=Cache`, `tier=Tier 5`, `maintainers=None`, `features_score=7`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=True`, `remote=TestCache:`, `features` (11 entries), `hashes` (13 entries), and `precision=1`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/cache.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/chunker.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/chunker.yaml

## Purpose

`chunker.yaml` is a Hugo data record describing the rclone `chunker` backend as `Chunker` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=chunker`, `name=Chunker`, `tier=Tier 4`, `maintainers=None`, `features_score=7`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=True`, `remote=TestChunkerLocal:`, `features` (0 entries), `hashes` (0 entries), and `precision=None`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/chunker.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/cloudinary.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/cloudinary.yaml

## Purpose

`cloudinary.yaml` is a Hugo data record describing the rclone `cloudinary` backend as `Cloudinary` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=cloudinary`, `name=Cloudinary`, `tier=Tier 3`, `maintainers=Core`, `features_score=3`, `integration_tests=Failing`, `data_integrity=Hash`, `performance=High`, `adoption=Often used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestCloudinary:`, `features` (1 entries), `hashes` (1 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/cloudinary.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/combine.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/combine.yaml

## Purpose

`combine.yaml` is a Hugo data record describing the rclone `combine` backend as `Combine` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=combine`, `name=Combine`, `tier=Tier 1`, `maintainers=Core`, `features_score=7`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Often used`, `docs=Full`, `security=High`, `virtual=True`, `remote=TestCombine:dir1`, `features` (20 entries), `hashes` (13 entries), and `precision=1`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/combine.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/compress.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/compress.yaml

## Purpose

`compress.yaml` is a Hugo data record describing the rclone `compress` backend as `Compress` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=compress`, `name=Compress`, `tier=Tier 4`, `maintainers=Core`, `features_score=5`, `integration_tests=Failing`, `data_integrity=Hash`, `performance=Medium`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=True`, `remote=TestCompress:`, `features` (22 entries), `hashes` (1 entries), and `precision=1`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/compress.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/crypt.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/crypt.yaml

## Purpose

`crypt.yaml` is a Hugo data record describing the rclone `crypt` backend as `Crypt` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=crypt`, `name=Crypt`, `tier=Tier 1`, `maintainers=Core`, `features_score=7`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=True`, `remote=TestCryptLocal:`, `features` (0 entries), `hashes` (0 entries), and `precision=None`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/crypt.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/doi.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/doi.yaml

## Purpose

`doi.yaml` is a Hugo data record describing the rclone `doi` backend as `Doi` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=doi`, `name=Doi`, `tier=Tier 2`, `maintainers=External`, `features_score=0`, `integration_tests=N/A`, `data_integrity=Other`, `performance=High`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=None`, `features` (0 entries), `hashes` (0 entries), and `precision=None`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/doi.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/drime.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/drime.yaml

## Purpose

`drime.yaml` is a Hugo data record describing the rclone `drime` backend as `Drime` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=drime`, `name=Drime`, `tier=Tier 1`, `maintainers=Core`, `features_score=4`, `integration_tests=Passing`, `data_integrity=High`, `performance=High`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestDrime:`, `features` (12 entries), `hashes` (0 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/drime.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/drive.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/drive.yaml

## Purpose

`drive.yaml` is a Hugo data record describing the rclone `drive` backend as `Drive` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=drive`, `name=Drive`, `tier=Tier 1`, `maintainers=Core`, `features_score=7`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestDrive:`, `features` (29 entries), `hashes` (3 entries), and `precision=1000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/drive.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/dropbox.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/dropbox.yaml

## Purpose

`dropbox.yaml` is a Hugo data record describing the rclone `dropbox` backend as `Dropbox` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=dropbox`, `name=Dropbox`, `tier=Tier 1`, `maintainers=Core`, `features_score=6`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestDropbox:`, `features` (12 entries), `hashes` (1 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/dropbox.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/fichier.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/fichier.yaml

## Purpose

`fichier.yaml` is a Hugo data record describing the rclone `fichier` backend as `Fichier` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=fichier`, `name=Fichier`, `tier=Tier 3`, `maintainers=Core`, `features_score=2`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=Medium`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestFichier:`, `features` (9 entries), `hashes` (1 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/fichier.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/filefabric.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/filefabric.yaml

## Purpose

`filefabric.yaml` is a Hugo data record describing the rclone `filefabric` backend as `Filefabric` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=filefabric`, `name=Filefabric`, `tier=Tier 4`, `maintainers=Core`, `features_score=3`, `integration_tests=Failing`, `data_integrity=Modtime`, `performance=Medium`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestFileFabric:`, `features` (10 entries), `hashes` (0 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/filefabric.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/filelu.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/filelu.yaml

## Purpose

`filelu.yaml` is a Hugo data record describing the rclone `filelu` backend as `Filelu` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=filelu`, `name=Filelu`, `tier=Tier 1`, `maintainers=Core`, `features_score=1`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestFileLu:`, `features` (5 entries), `hashes` (0 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/filelu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/filen.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/filen.yaml

## Purpose

`filen.yaml` is a Hugo data record describing the rclone `filen` backend as `Filen` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=filen`, `name=Filen`, `tier=Tier 1`, `maintainers=External`, `features_score=6`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestFilen:`, `features` (12 entries), `hashes` (1 entries), and `precision=1000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/filen.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/filescom.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/filescom.yaml

## Purpose

`filescom.yaml` is a Hugo data record describing the rclone `filescom` backend as `Filescom` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=filescom`, `name=Filescom`, `tier=Tier 1`, `maintainers=Core`, `features_score=5`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestFilesCom:`, `features` (11 entries), `hashes` (2 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/filescom.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/ftp.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/ftp.yaml

## Purpose

`ftp.yaml` is a Hugo data record describing the rclone `ftp` backend as `FTP` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=ftp`, `name=FTP`, `tier=Tier 1`, `maintainers=Core`, `features_score=4`, `integration_tests=Passing`, `data_integrity=Modtime`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=Varies`, `virtual=False`, `remote=TestFTPProftpd:`, `features` (6 entries), `hashes` (0 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/ftp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/gofile.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/gofile.yaml

## Purpose

`gofile.yaml` is a Hugo data record describing the rclone `gofile` backend as `Gofile` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=gofile`, `name=Gofile`, `tier=Tier 1`, `maintainers=Core`, `features_score=5`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Often used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestGoFile:`, `features` (17 entries), `hashes` (1 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/gofile.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/googlecloudstorage.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/googlecloudstorage.yaml

## Purpose

`googlecloudstorage.yaml` is a Hugo data record describing the rclone `googlecloudstorage` backend as `Google Cloud Storage` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=googlecloudstorage`, `name=Google Cloud Storage`, `tier=Tier 1`, `maintainers=Core`, `features_score=6`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestGoogleCloudStorage:`, `features` (9 entries), `hashes` (1 entries), and `precision=1`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/googlecloudstorage.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/googlephotos.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/googlephotos.yaml

## Purpose

`googlephotos.yaml` is a Hugo data record describing the rclone `googlephotos` backend as `Google Photos` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=googlephotos`, `name=Google Photos`, `tier=Tier 5`, `maintainers=None`, `features_score=0`, `integration_tests=Failing`, `data_integrity=Other`, `performance=Low`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestGooglePhotos:`, `features` (4 entries), `hashes` (0 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/googlephotos.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/hasher.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/hasher.yaml

## Purpose

`hasher.yaml` is a Hugo data record describing the rclone `hasher` backend as `Hasher` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=hasher`, `name=Hasher`, `tier=Tier 4`, `maintainers=Core`, `features_score=7`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=True`, `remote=None`, `features` (0 entries), `hashes` (0 entries), and `precision=None`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/hasher.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/hdfs.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/hdfs.yaml

## Purpose

`hdfs.yaml` is a Hugo data record describing the rclone `hdfs` backend as `HDFS` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=hdfs`, `name=HDFS`, `tier=Tier 2`, `maintainers=Core`, `features_score=4`, `integration_tests=Passing`, `data_integrity=Modtime`, `performance=Medium`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestHdfs:`, `features` (6 entries), `hashes` (0 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/hdfs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/hidrive.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/hidrive.yaml

## Purpose

`hidrive.yaml` is a Hugo data record describing the rclone `hidrive` backend as `Hidrive` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=hidrive`, `name=Hidrive`, `tier=Tier 1`, `maintainers=Core`, `features_score=5`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=Medium`, `adoption=Often used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestHiDrive:`, `features` (8 entries), `hashes` (1 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/hidrive.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/http.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/http.yaml

## Purpose

`http.yaml` is a Hugo data record describing the rclone `http` backend as `HTTP` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=http`, `name=HTTP`, `tier=Tier 3`, `maintainers=Core`, `features_score=0`, `integration_tests=N/A`, `data_integrity=Other`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=Varies`, `virtual=False`, `remote=:http,url=''http://downloads.rclone.org'':`, `features` (4 entries), `hashes` (0 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/http.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/huaweidrive.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/huaweidrive.yaml

## Purpose

`huaweidrive.yaml` is a Hugo data record describing the rclone `Huaweidrive` backend as `Huaweidrive` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=Huaweidrive`, `name=Huaweidrive`, `tier=Tier 3`, `maintainers=External`, `features_score=4`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestHuaweiDrive:`, `features` (18 entries), `hashes` (1 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/huaweidrive.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/iclouddrive.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/iclouddrive.yaml

## Purpose

`iclouddrive.yaml` is a Hugo data record describing the rclone `iclouddrive` backend as `Iclouddrive` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=iclouddrive`, `name=Iclouddrive`, `tier=Tier 4`, `maintainers=External`, `features_score=3`, `integration_tests=Flaky`, `data_integrity=Modtime`, `performance=Low`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestICloudDrive:`, `features` (0 entries), `hashes` (0 entries), and `precision=None`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/iclouddrive.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/imagekit.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/imagekit.yaml

## Purpose

`imagekit.yaml` is a Hugo data record describing the rclone `imagekit` backend as `Imagekit` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=imagekit`, `name=Imagekit`, `tier=Tier 1`, `maintainers=External`, `features_score=0`, `integration_tests=Passing`, `data_integrity=Other`, `performance=High`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestImageKit:`, `features` (7 entries), `hashes` (0 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/imagekit.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/internetarchive.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/internetarchive.yaml

## Purpose

`internetarchive.yaml` is a Hugo data record describing the rclone `internetarchive` backend as `Internet Archive` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=internetarchive`, `name=Internet Archive`, `tier=Tier 3`, `maintainers=Core`, `features_score=5`, `integration_tests=Failing`, `data_integrity=Hash`, `performance=Medium`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestIA:rclone-integration-test`, `features` (9 entries), `hashes` (3 entries), and `precision=1`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/internetarchive.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/internxt.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/internxt.yaml

## Purpose

`internxt.yaml` is a Hugo data record describing the rclone `internxt` backend as `Internxt` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=internxt`, `name=Internxt`, `tier=Tier 2`, `maintainers=External`, `features_score=0`, `integration_tests=Passing`, `data_integrity=Other`, `performance=High`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestInternxt:`, `features` (3 entries), `hashes` (0 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/internxt.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/jottacloud.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/jottacloud.yaml

## Purpose

`jottacloud.yaml` is a Hugo data record describing the rclone `jottacloud` backend as `Jottacloud` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=jottacloud`, `name=Jottacloud`, `tier=Tier 2`, `maintainers=Core`, `features_score=6`, `integration_tests=Flaky`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestJottacloud:`, `features` (15 entries), `hashes` (1 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/jottacloud.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/koofr.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/koofr.yaml

## Purpose

`koofr.yaml` is a Hugo data record describing the rclone `koofr` backend as `Koofr` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=koofr`, `name=Koofr`, `tier=Tier 2`, `maintainers=Core`, `features_score=5`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestKoofr:`, `features` (8 entries), `hashes` (1 entries), and `precision=1000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/koofr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/linkbox.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/linkbox.yaml

## Purpose

`linkbox.yaml` is a Hugo data record describing the rclone `linkbox` backend as `Linkbox` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=linkbox`, `name=Linkbox`, `tier=Tier 5`, `maintainers=Core`, `features_score=2`, `integration_tests=Failing`, `data_integrity=Modtime`, `performance=High`, `adoption=Often used`, `docs=Basic`, `security=High`, `virtual=False`, `remote=TestLinkbox:`, `features` (4 entries), `hashes` (0 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/linkbox.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/local.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/local.yaml

## Purpose

`local.yaml` is a Hugo data record describing the rclone `local` backend as `Local` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=local`, `name=Local`, `tier=Tier 1`, `maintainers=Core`, `features_score=7`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=.`, `features` (21 entries), `hashes` (13 entries), and `precision=1`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/local.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/mailru.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/mailru.yaml

## Purpose

`mailru.yaml` is a Hugo data record describing the rclone `mailru` backend as `Mailru` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=mailru`, `name=Mailru`, `tier=Tier 1`, `maintainers=External`, `features_score=6`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=Medium`, `adoption=Often used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestMailru:`, `features` (10 entries), `hashes` (1 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/mailru.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/mega.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/mega.yaml

## Purpose

`mega.yaml` is a Hugo data record describing the rclone `mega` backend as `Mega` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=mega`, `name=Mega`, `tier=Tier 2`, `maintainers=Core`, `features_score=3`, `integration_tests=Flaky`, `data_integrity=Other`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestMega:`, `features` (11 entries), `hashes` (0 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/mega.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/memory.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/memory.yaml

## Purpose

`memory.yaml` is a Hugo data record describing the rclone `memory` backend as `Memory` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=memory`, `name=Memory`, `tier=Tier 1`, `maintainers=Core`, `features_score=4`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=:memory:`, `features` (8 entries), `hashes` (1 entries), and `precision=1`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/memory.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/netstorage.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/netstorage.yaml

## Purpose

`netstorage.yaml` is a Hugo data record describing the rclone `netstorage` backend as `Netstorage` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=netstorage`, `name=Netstorage`, `tier=Tier 1`, `maintainers=Core`, `features_score=3`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestnStorage:`, `features` (5 entries), `hashes` (1 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/netstorage.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/onedrive.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/onedrive.yaml

## Purpose

`onedrive.yaml` is a Hugo data record describing the rclone `onedrive` backend as `Onedrive` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=onedrive`, `name=Onedrive`, `tier=Tier 1`, `maintainers=Core`, `features_score=6`, `integration_tests=Flaky`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestOneDrive:`, `features` (21 entries), `hashes` (1 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/onedrive.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/opendrive.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/opendrive.yaml

## Purpose

`opendrive.yaml` is a Hugo data record describing the rclone `opendrive` backend as `Opendrive` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=opendrive`, `name=Opendrive`, `tier=Tier 1`, `maintainers=Core`, `features_score=5`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Often used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestOpenDrive:`, `features` (8 entries), `hashes` (1 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/opendrive.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/oracleobjectstorage.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/oracleobjectstorage.yaml

## Purpose

`oracleobjectstorage.yaml` is a Hugo data record describing the rclone `oracleobjectstorage` backend as `Oracle Object Storage` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=oracleobjectstorage`, `name=Oracle Object Storage`, `tier=Tier 1`, `maintainers=Core`, `features_score=6`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestOracleObjectStorage:`, `features` (15 entries), `hashes` (1 entries), and `precision=1000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/oracleobjectstorage.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/pcloud.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/pcloud.yaml

## Purpose

`pcloud.yaml` is a Hugo data record describing the rclone `pcloud` backend as `Pcloud` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=pcloud`, `name=Pcloud`, `tier=Tier 1`, `maintainers=Core`, `features_score=5`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Often used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestPcloud:`, `features` (13 entries), `hashes` (2 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/pcloud.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/pikpak.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/pikpak.yaml

## Purpose

`pikpak.yaml` is a Hugo data record describing the rclone `pikpak` backend as `Pikpak` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=pikpak`, `name=Pikpak`, `tier=Tier 1`, `maintainers=External`, `features_score=5`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Often used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestPikPak:`, `features` (13 entries), `hashes` (1 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/pikpak.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/pixeldrain.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/pixeldrain.yaml

## Purpose

`pixeldrain.yaml` is a Hugo data record describing the rclone `pixeldrain` backend as `Pixeldrain` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=pixeldrain`, `name=Pixeldrain`, `tier=Tier 1`, `maintainers=Core`, `features_score=7`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestPixeldrain:`, `features` (12 entries), `hashes` (1 entries), and `precision=1000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/pixeldrain.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/premiumizeme.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/premiumizeme.yaml

## Purpose

`premiumizeme.yaml` is a Hugo data record describing the rclone `premiumizeme` backend as `Premiumizeme` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=premiumizeme`, `name=Premiumizeme`, `tier=Tier 3`, `maintainers=Core`, `features_score=2`, `integration_tests=Passing`, `data_integrity=Other`, `performance=High`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestPremiumizeMe:`, `features` (11 entries), `hashes` (0 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/premiumizeme.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/protondrive.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/protondrive.yaml

## Purpose

`protondrive.yaml` is a Hugo data record describing the rclone `protondrive` backend as `Proton Drive` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=protondrive`, `name=Proton Drive`, `tier=Tier 4`, `maintainers=Community`, `features_score=4`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Often used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestProtonDrive:`, `features` (10 entries), `hashes` (1 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/protondrive.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/putio.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/putio.yaml

## Purpose

`putio.yaml` is a Hugo data record describing the rclone `putio` backend as `Putio` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=putio`, `name=Putio`, `tier=Tier 2`, `maintainers=Core`, `features_score=5`, `integration_tests=Flaky`, `data_integrity=Hash`, `performance=Low`, `adoption=Often used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestPutio:`, `features` (11 entries), `hashes` (1 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/putio.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/qingstor.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/qingstor.yaml

## Purpose

`qingstor.yaml` is a Hugo data record describing the rclone `qingstor` backend as `Qingstor` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=qingstor`, `name=Qingstor`, `tier=Tier 3`, `maintainers=Core`, `features_score=3`, `integration_tests=Disabled`, `data_integrity=Hash`, `performance=High`, `adoption=Often used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestQingStor:`, `features` (8 entries), `hashes` (1 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/qingstor.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/quatrix.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/quatrix.yaml

## Purpose

`quatrix.yaml` is a Hugo data record describing the rclone `quatrix` backend as `Quatrix` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=quatrix`, `name=Quatrix`, `tier=Tier 3`, `maintainers=Core`, `features_score=3`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Often used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestQuatrix:`, `features` (8 entries), `hashes` (0 entries), and `precision=1000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/quatrix.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/s3.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/s3.yaml

## Purpose

`s3.yaml` is a Hugo data record describing the rclone `s3` backend as `S3` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=s3`, `name=S3`, `tier=Tier 1`, `maintainers=Core`, `features_score=7`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestS3:`, `features` (20 entries), `hashes` (1 entries), and `precision=1`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/s3.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/seafile.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/seafile.yaml

## Purpose

`seafile.yaml` is a Hugo data record describing the rclone `seafile` backend as `Seafile` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=seafile`, `name=Seafile`, `tier=Tier 3`, `maintainers=Core`, `features_score=3`, `integration_tests=Failing`, `data_integrity=Other`, `performance=Medium`, `adoption=Some use`, `docs=Basic`, `security=High`, `virtual=False`, `remote=TestSeafile:`, `features` (12 entries), `hashes` (0 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/seafile.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/sftp.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/sftp.yaml

## Purpose

`sftp.yaml` is a Hugo data record describing the rclone `sftp` backend as `SFTP` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=sftp`, `name=SFTP`, `tier=Tier 1`, `maintainers=Core`, `features_score=5`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestSFTPOpenssh:`, `features` (11 entries), `hashes` (2 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/sftp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/shade.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/shade.yaml

## Purpose

`shade.yaml` is a Hugo data record describing the rclone `shade` backend as `Shade` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=shade`, `name=Shade`, `tier=Tier 1`, `maintainers=External`, `features_score=0`, `integration_tests=Passing`, `data_integrity=Other`, `performance=High`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestShade:`, `features` (4 entries), `hashes` (0 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/shade.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/sharefile.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/sharefile.yaml

## Purpose

`sharefile.yaml` is a Hugo data record describing the rclone `sharefile` backend as `Sharefile` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=sharefile`, `name=Sharefile`, `tier=Tier 5`, `maintainers=Core`, `features_score=4`, `integration_tests=Disabled`, `data_integrity=Modtime`, `performance=Medium`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestSharefile:`, `features` (0 entries), `hashes` (1 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/sharefile.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/sia.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/sia.yaml

## Purpose

`sia.yaml` is a Hugo data record describing the rclone `sia` backend as `Sia` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=sia`, `name=Sia`, `tier=Tier 4`, `maintainers=Core`, `features_score=1`, `integration_tests=Failing`, `data_integrity=Other`, `performance=Medium`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestSia:`, `features` (2 entries), `hashes` (0 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/sia.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/smb.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/smb.yaml

## Purpose

`smb.yaml` is a Hugo data record describing the rclone `smb` backend as `SMB` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=smb`, `name=SMB`, `tier=Tier 2`, `maintainers=External`, `features_score=5`, `integration_tests=Passing`, `data_integrity=Modtime`, `performance=Medium`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestSMB:rclone`, `features` (10 entries), `hashes` (0 entries), and `precision=1000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/smb.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/storj.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/storj.yaml

## Purpose

`storj.yaml` is a Hugo data record describing the rclone `storj` backend as `Storj` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=storj`, `name=Storj`, `tier=Tier 1`, `maintainers=Core`, `features_score=4`, `integration_tests=Passing`, `data_integrity=Modtime`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestStorj:`, `features` (8 entries), `hashes` (0 entries), and `precision=1`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/storj.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/sugarsync.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/sugarsync.yaml

## Purpose

`sugarsync.yaml` is a Hugo data record describing the rclone `sugarsync` backend as `Sugarsync` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=sugarsync`, `name=Sugarsync`, `tier=Tier 3`, `maintainers=Core`, `features_score=3`, `integration_tests=Passing`, `data_integrity=Other`, `performance=Medium`, `adoption=Some use`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestSugarSync:Test`, `features` (10 entries), `hashes` (0 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/sugarsync.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/swift.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/swift.yaml

## Purpose

`swift.yaml` is a Hugo data record describing the rclone `swift` backend as `Swift` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=swift`, `name=Swift`, `tier=Tier 1`, `maintainers=Core`, `features_score=4`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestSwiftAIO:`, `features` (11 entries), `hashes` (1 entries), and `precision=1`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/swift.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/ulozto.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/ulozto.yaml

## Purpose

`ulozto.yaml` is a Hugo data record describing the rclone `ulozto` backend as `Ulozto` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=ulozto`, `name=Ulozto`, `tier=Tier 3`, `maintainers=Core`, `features_score=3`, `integration_tests=Failing`, `data_integrity=Hash`, `performance=Medium`, `adoption=Often used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestUlozto:`, `features` (7 entries), `hashes` (2 entries), and `precision=1000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/ulozto.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/union.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/union.yaml

## Purpose

`union.yaml` is a Hugo data record describing the rclone `union` backend as `Union` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=union`, `name=Union`, `tier=Tier 1`, `maintainers=Core`, `features_score=7`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Often used`, `docs=Full`, `security=High`, `virtual=True`, `remote=TestUnion:`, `features` (18 entries), `hashes` (13 entries), and `precision=1`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/union.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/webdav.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/webdav.yaml

## Purpose

`webdav.yaml` is a Hugo data record describing the rclone `webdav` backend as `WebDAV` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=webdav`, `name=WebDAV`, `tier=Tier 1`, `maintainers=Core`, `features_score=5`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=Low`, `adoption=Widely used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestWebdavNextcloud:`, `features` (7 entries), `hashes` (1 entries), and `precision=1000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/webdav.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/yandex.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/yandex.yaml

## Purpose

`yandex.yaml` is a Hugo data record describing the rclone `yandex` backend as `Yandex` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=yandex`, `name=Yandex`, `tier=Tier 1`, `maintainers=External`, `features_score=5`, `integration_tests=Passing`, `data_integrity=Hash`, `performance=High`, `adoption=Often used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestYandex:`, `features` (10 entries), `hashes` (1 entries), and `precision=1`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/yandex.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/zoho.yaml -->
# sources/user-network-fs/rclone/docs/data/backends/zoho.yaml

## Purpose

`zoho.yaml` is a Hugo data record describing the rclone `zoho` backend as `Zoho` for the documentation site's backend index, JSON data export, and feature/status tables.

## Important APIs, Types, and Functions

The record fields form a data contract rather than executable APIs: `backend=zoho`, `name=Zoho`, `tier=Tier 3`, `maintainers=External`, `features_score=2`, `integration_tests=Failing`, `data_integrity=Other`, `performance=Medium`, `adoption=Often used`, `docs=Full`, `security=High`, `virtual=False`, `remote=TestZoho:`, `features` (7 entries), `hashes` (0 entries), and `precision=3153600000000000000`.

## Control Flow

Hugo loads this YAML under `hugo.Data.backends`; templates and generated JSON consume it to display backend status, capabilities, default integration-test remote names, hash support, and timestamp precision. No code executes inside the YAML file.

## State and Persistence Behavior

The file is static documentation/build metadata. Changes persist in generated docs and may affect user expectations about backend support, tests, and reliability.

## Dependencies and Integration Points

It integrates with `docs/layouts/backends/single.json`, backend documentation pages, feature comparison tables, and any tooling that reads docs backend data to summarize rclone capabilities.

## Risks and Test Signals

Risks include stale integration-test status, incorrect tier/maintainer/security labels, `remote` names that do not match CI secrets, capability drift from backend code, and null versus empty-list ambiguity for virtual/wrapper backends. Test signals are Hugo build success, JSON parseability, and comparison against backend feature declarations/integration-test results.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/data/backends/zoho.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/i18n/en.toml -->
# sources/user-network-fs/rclone/docs/i18n/en.toml

## Purpose

`en.toml` is a minimal Hugo i18n file used to quiet monolingual-site translation warnings.

## Important APIs, Types, and Functions

It defines the `[wordCount]` translation with `other = "{{ .WordCount }} words"`.

## Control Flow

Hugo loads the file during site generation when templates request localized word-count text.

## State and Persistence Behavior

No runtime or persistent state is created beyond generated site text.

## Dependencies and Integration Points

It integrates with Hugo's i18n subsystem and any template using `i18n "wordCount"`.

## Risks and Test Signals

Risks are low: syntax errors can break docs builds, and missing keys may reintroduce warnings. A Hugo build is the main test signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/i18n/en.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/layouts/backends/single.json -->
# sources/user-network-fs/rclone/docs/layouts/backends/single.json

## Purpose

This Hugo template emits backend data as JSON for backend pages or data endpoints.

## Important APIs, Types, and Functions

It renders `hugo.Data.backends` through `jsonify` with two-space indentation.

## Control Flow

During a matching backend page render, Hugo evaluates the template and serializes all backend YAML data.

## State and Persistence Behavior

The template has no state. Output determinism depends on Hugo's data-map serialization order and the contents of `docs/data/backends`.

## Dependencies and Integration Points

It integrates with Hugo data loading and the backend YAML files in this subset.

## Risks and Test Signals

Risks include invalid JSON if template context changes or data contains unexpected values. Tests should build docs and parse the generated JSON.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/layouts/backends/single.json -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/layouts/rss.xml -->
# sources/user-network-fs/rclone/docs/layouts/rss.xml

## Purpose

`rss.xml` is the Hugo RSS feed template for rclone documentation pages.

## Important APIs, Types, and Functions

It emits RSS 2.0 with Atom namespace, site/page title, permalink, language, author, rights, updated timestamp, and the first 15 pages as feed items containing title, link, pubDate, author, guid, and HTML-rendered content.

## Control Flow

Hugo evaluates `.Data.Pages`, formats dates with RFC-like layout, and serializes `.Content | html` into item descriptions.

## State and Persistence Behavior

No state is stored. Feed content is generated from site pages during build.

## Dependencies and Integration Points

It integrates with Hugo page collections, site metadata, and feed consumers.

## Risks and Test Signals

Risks include invalid XML from unescaped content, stale author/rights metadata, and overly large descriptions. Tests should validate generated RSS XML and feed item ordering/count.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/layouts/rss.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/layouts/sitemap.xml -->
# sources/user-network-fs/rclone/docs/layouts/sitemap.xml

## Purpose

`sitemap.xml` is the Hugo sitemap template for rclone.org.

## Important APIs, Types, and Functions

It emits a standard sitemap URL set, iterating `.Data.Pages` and writing location, last modification timestamp, optional change frequency, and optional priority.

## Control Flow

Hugo provides page metadata; the template formats dates as ISO-like timestamps and conditionally renders sitemap attributes.

## State and Persistence Behavior

No runtime state is stored. Output depends on page dates and sitemap metadata.

## Dependencies and Integration Points

It integrates with search engine indexing expectations and Hugo page metadata.

## Risks and Test Signals

Risks include malformed XML, missing safe escaping for URLs, and bad dates. Tests should run Hugo and validate the sitemap against XML parsing and expected URL counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/layouts/sitemap.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/docs/static/js/rclone.js -->
# sources/user-network-fs/rclone/docs/static/js/rclone.js

## Purpose

`rclone.js` is the custom browser behavior layer for rclone.org, replacing Bootstrap/jQuery/Popper interactions with vanilla JavaScript.

## Important APIs, Types, and Functions

It implements navbar collapse, dropdown open/close, mega-menu mobile headers and filtering, header anchor injection, TOC overlay and active-section tracking, scrollable table wrapping with sticky headers/arrows, copy-to-clipboard buttons, and global `on_search`.

## Control Flow

An IIFE registers delegated click handlers, decorates dropdowns and headings, builds TOC maps and an `IntersectionObserver`, wraps overflowing tables by cloning headers and synchronizing scroll positions, injects copy buttons into `pre` blocks, and uses the Clipboard API on copy clicks. `on_search` rewrites the search query to exclude the forum domain.

## State and Persistence Behavior

State is client-side DOM state: `.show`, `.filter-hidden`, `.toc-open`, `.toc-active`, `.visible`, and `.copied` classes plus transient filter input values and scroll positions. Nothing is persisted across page loads.

## Dependencies and Integration Points

It depends on DOM APIs, `closest`, `querySelectorAll`, `IntersectionObserver`, `navigator.clipboard`, CSS classes defined by the docs theme, SVG icon symbols, and a form named `search_form`.

## Risks and Test Signals

Risks include unsupported browser APIs, duplicate wrapping if executed twice, table layout mismatch after fonts/images load, clipboard permission failures, unclosed dropdown states, and missing SVG symbols. Tests should use browser smoke tests for nav/dropdown/search, TOC scrolling, table overflow on mobile, copy buttons, and pages without TOC/tables.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/docs/static/js/rclone.js -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/accounting.go -->
# sources/user-network-fs/rclone/fs/accounting/accounting.go

## Purpose

`accounting.go` implements the per-transfer accounting reader used to count bytes, enforce bandwidth and max-transfer limits, expose current progress, and wrap or unwrap stream chains.

## Important APIs, Types, and Functions

Key exports are `Start`, `Account`, `AccountSeeker`, `AccountReaderAt`, `AccountReadAtSeeker`, `Accounter`, `WrapFn`, `UnWrap`, and `UnWrapAccounting`. Error sentinels distinguish hard max-transfer limit failures from graceful no-retry stop conditions. `newAccountSizeName` constructs accounts for `Transfer`.

## Control Flow

`Start` initializes global token buckets, scheduled bandwidth updates, TPS limiting, and `fs.CountError`. An `Account` wraps an `io.ReadCloser`, optionally adds `asyncreader` buffering, records bytes on `Read`, `ReadAt`, `WriteTo`, explicit accounting, and server-side copy/move callbacks, then removes itself from in-progress state on `Done`.

## State and Persistence Behavior

State is in memory: per-account byte counters, moving average samples, current reader, async buffer, closed flag, exit channel, per-file limiter, and pointers into `StatsInfo`. The max-transfer limit reads global stats bytes, so per-account reads can be clipped to process/group state.

## Dependencies and Integration Points

It integrates with `StatsInfo`, `Transfer`, global `TokenBucket`, per-file `BwLimitFile`, `asyncreader`, `fserrors`, remote-control stats, and transfer accounter callbacks for server-side operations.

## Risks and Test Signals

Risks include Read/Close races, goroutine leaks when `Done` is not called, accounting over/under-count around max-transfer clipping, async-buffer replacement bugs in `UpdateReader`, lock-order deadlocks, and Unicode shortening edge cases. Tests cover buffering, reader updates, max transfer, stream wrapping, seeker/reader-at wrappers, `WriteTo`, and name shortening; race tests are especially valuable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/accounting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/accounting_other.go -->
# sources/user-network-fs/rclone/fs/accounting/accounting_other.go

## Purpose

`accounting_other.go` supplies the non-Unix implementation of token-bucket signal handling.

## Important APIs, Types, and Functions

It defines `(*tokenBucket).startSignalHandler` as a no-op for builds that are not Darwin, DragonFly, FreeBSD, Linux, NetBSD, OpenBSD, or Solaris.

## Control Flow

When `StartTokenBucket` calls `startSignalHandler` on non-Unix builds, no goroutine or signal registration is created.

## State and Persistence Behavior

No state is mutated. Runtime bandwidth controls remain available through config and rc APIs, but SIGUSR2 toggling is unavailable.

## Dependencies and Integration Points

It is selected by Go build tags and pairs with `accounting_unix.go`.

## Risks and Test Signals

Risks are low but build-tag coverage matters. Cross-compilation should confirm exactly one signal-handler implementation is selected per target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/accounting_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/accounting_test.go -->
# sources/user-network-fs/rclone/fs/accounting/accounting_test.go

## Purpose

`accounting_test.go` validates the per-transfer `Account` reader and stream-wrapper behavior.

## Important APIs, Types, and Functions

Tests cover `newAccountSizeName`, `WithBuffer`, `GetReader`, `UpdateReader`, `Read`, `WriteTo`, `String`, `Accounter`/`UnWrap`, max-transfer hard cutoff, context cancellation, `shortenName`, and optional `Seek`, `ReadAt`, and combined wrappers through custom test readers.

## Control Flow

Each test constructs a `StatsInfo` and in-memory readers, wraps them in an account, drives reads/writes/seeks, and asserts byte counters, errors, and wrapper behavior. Global config fields such as `MaxTransfer` and `CutoffMode` are saved and restored around limit tests.

## State and Persistence Behavior

All state is process-local. Tests intentionally exercise global config mutation, account goroutines, async buffers, and stats in-progress maps; correct `Close`/`Done` handling is part of leak prevention.

## Dependencies and Integration Points

It integrates with `asyncreader`, `readers.NewPatternReader`, `fserrors`, `fs.ConfigInfo`, and the accounting transfer/stat machinery.

## Risks and Test Signals

The suite signals byte-accurate accounting across Reader, WriterTo, ReaderAt, Seeker, and wrapping modes. Watch for race detector failures, goroutine leaks, and changed max-transfer semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/accounting_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/accounting_unix.go -->
# sources/user-network-fs/rclone/fs/accounting/accounting_unix.go

## Purpose

`accounting_unix.go` implements SIGUSR2-driven bandwidth-limit toggling for Unix-like builds.

## Important APIs, Types, and Functions

`(*tokenBucket).startSignalHandler` registers `syscall.SIGUSR2`, starts a goroutine, and on each signal swaps current and previous token buckets while toggling `toggledOff`.

## Control Flow

On signal receipt, the handler locks the token bucket, ignores the signal if no current bandwidth schedule is configured, flips the toggle state, swaps `curr` and `prev`, and logs whether limits are enabled or disabled.

## State and Persistence Behavior

State is process memory: signal subscription, goroutine lifetime, `toggledOff`, and token bucket sets. No settings are persisted.

## Dependencies and Integration Points

It depends on Go signal handling and Unix build tags. It integrates with scheduled bandwidth updates in `token_bucket.go`, which may update `prev` while toggled off.

## Risks and Test Signals

Risks include unbounded goroutine lifetime, signal handler duplication if start is called repeatedly, lock contention, and confusing schedule changes while toggled off. Tests are mostly integration/manual: start with bwlimit, send SIGUSR2, and observe rc/logged limiter state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/accounting_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/inprogress.go -->
# sources/user-network-fs/rclone/fs/accounting/inprogress.go

## Purpose

`inprogress.go` stores the mapping from remote names to live `Account` objects for progress display and remote-control stats.

## Important APIs, Types, and Functions

The `inProgress` type wraps a mutex and `map[string]*Account`. Methods create the map sized from `ci.Transfers`, set, clear, get, and merge entries from another in-progress map.

## Control Flow

`newAccountSizeName` inserts an account on start, `Account.Done` clears it, and stats/reporting code consults the map to enrich `transferMap` output with byte/speed/ETA data.

## State and Persistence Behavior

State is process-local and keyed by remote path. Duplicate remote names overwrite each other, so concurrent same-name transfers can hide one progress entry.

## Dependencies and Integration Points

It integrates with `StatsInfo`, `transferMap`, stats group aggregation, and rc stats rendering.

## Risks and Test Signals

Risks include same-name collisions, map copying while transfers mutate, and stale entries if `Done` is skipped. Tests should cover set/clear/get/merge and duplicate remote behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/inprogress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/prometheus.go -->
# sources/user-network-fs/rclone/fs/accounting/prometheus.go

## Purpose

`prometheus.go` exposes rclone transfer statistics as a Prometheus collector.

## Important APIs, Types, and Functions

`RcloneCollector` stores descriptors for transferred bytes, speed, errors, checked/transferred files, deletes, deleted dirs, renames, listed entries, fatal error, and retry error. `NewRcloneCollector`, `Describe`, `Collect`, and `bool2Float` implement the collector surface.

## Control Flow

On collection, it builds a summed `StatsInfo` across groups, locks it, emits counters/gauges through `prometheus.MustNewConstMetric`, and unlocks.

## State and Persistence Behavior

The collector itself stores descriptors and context only. Metric values are snapshots of in-memory stats groups.

## Dependencies and Integration Points

It integrates with `github.com/prometheus/client_golang/prometheus`, stats-group aggregation, and any rclone rc/metrics server that registers the collector.

## Risks and Test Signals

Risks include metric-name compatibility, counter resets after stats reset, summed speed semantics, and lock contention during scrape. Tests should register the collector, mutate stats, gather metrics, and verify boolean gauges and counter values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/prometheus.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/stats.go -->
# sources/user-network-fs/rclone/fs/accounting/stats.go

## Purpose

`stats.go` is the central accounting state machine for rclone operations. It tracks bytes, checks, transfers, deletes, renames, listings, errors, retry/fatal flags, queues, elapsed transfer time, current/completed transfer records, and server-side copy/move counters.

## Important APIs, Types, and Functions

`StatsInfo` is the main type. Important APIs include `NewStats`, `RemoteStats`, `String`, `Log`, byte/error counters, `DeleteFile`, reset methods, transfer lifecycle methods, queue setters, transfer pruning, and server-side counters. Helper types/functions include moving-average state, `timeRange`, `eta`, `etaString`, `percent`, and `transferStats`.

## Control Flow

Transfers/checks are added through `NewTransfer` or `NewCheckingTransfer`, update byte counters through `Account`, and finish through `DoneTransferring`/`DoneChecking`. `calculateTransferStats` combines queue, completed, and in-progress data. The average loop starts when transfers begin and stops when no transfer/check remains. `String` and `RemoteStats` render consistent human/rc views.

## State and Persistence Behavior

All state is in memory and protected by `StatsInfo.mu`, nested average mutexes, and transfer maps. Completed transfers are retained up to `maxCompletedTransfers`; old time ranges are merged/cull-pruned to keep duration accounting bounded. Reset methods clear counters and carefully stop/restart the average goroutine only when needed.

## Dependencies and Integration Points

It integrates with `fs.ConfigInfo`, `fserrors`, `rc.Params`, terminal title updates, `Transfer`, `transferMap`, `inProgress`, stats groups, Prometheus, and `fs.CountError`.

## Risks and Test Signals

Risks include lock-order deadlocks with transfer maps, goroutine leaks after reset, inaccurate ETA/duration for overlapping transfers, stale last errors, max-delete threshold off-by-one errors, and retention pruning mistakes. Tests cover ETA, percent, error classification, duration merging/culling, remote stats, and pruning; race testing is important.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/stats_groups.go -->
# sources/user-network-fs/rclone/fs/accounting/stats_groups.go

## Purpose

`stats_groups.go` manages named stats groups and registers remote-control endpoints for listing, querying, resetting, deleting, and retrieving completed transfers.

## Important APIs, Types, and Functions

Exports include `WithStatsGroup`, `StatsGroupFromContext`, `Stats`, `StatsGroup`, `GlobalStats`, and `NewStatsGroup`. Internal `statsGroups` stores group map/order and supports set/get/names/sum/reset/delete. rc handlers are registered for `core/group-list`, `core/stats`, `core/transferred`, `core/stats-reset`, and `core/stats-delete`.

## Control Flow

Contexts may carry a stats group name. `Stats(ctx)` returns group stats or global stats, lazily creating groups as needed. rc handlers parse optional group/short parameters and either operate on a named group or a summed snapshot. `set` enforces `MaxStatsGroups` by evicting oldest non-global names.

## State and Persistence Behavior

Group state is in memory only. The global `groups` variable is initialized at package load. Reset clears all maps/order; delete removes one group after clearing its counters.

## Dependencies and Integration Points

It integrates with rclone rc, context propagation from operations/jobs, `StatsInfo`, global config, and Prometheus aggregation.

## Risks and Test Signals

Risks include returning the mutable `order` slice from `names`, group eviction surprises, aggregate snapshots starting goroutines via `NewStats`, and lock nesting between groups and stats. Tests cover group operations, rc calls, count-error routing, and memory behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/stats_groups.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/stats_groups_test.go -->
# sources/user-network-fs/rclone/fs/accounting/stats_groups_test.go

## Purpose

`stats_groups_test.go` validates stats group storage, aggregation, rc endpoints, memory behavior, and `fs.CountError` routing.

## Important APIs, Types, and Functions

The suite exercises `newStatsGroups`, set/get/names/sum/reset/delete behavior, `NewStatsGroup`, rc calls for `core/group-list`, `core/stats`, `core/transferred`, `core/stats-reset`, `core/stats-delete`, and helper `percentDiff`.

## Control Flow

Tests construct independent group containers, add `StatsInfo` instances, mutate counters/transfers, call rc handlers through `rc.Calls`, and compare results. `TestCountError` temporarily replaces the global `groups` container and calls `Start` to install `fs.CountError`.

## State and Persistence Behavior

The tests manipulate global `groups` and global error-count hook, so cleanup/isolation is important. Memory-oriented assertions compare heap object counts after many groups.

## Dependencies and Integration Points

It integrates with `mockobject`, rc call registry, contexts carrying stats group names, and global accounting initialization.

## Risks and Test Signals

Signals include correct grouping, aggregate rc values, completed-transfer reporting, reset/delete effects, and error attribution. Race tests should watch global group replacement and rc calls in parallel.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/stats_groups_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/stats_test.go -->
# sources/user-network-fs/rclone/fs/accounting/stats_test.go

## Purpose

`stats_test.go` covers core `StatsInfo` helper math and lifecycle behavior.

## Important APIs, Types, and Functions

Tests target `eta`, `etaString`, `percent`, `StatsInfo.Error`, `_totalDuration`, `RemoteStats`, `timeRanges.merge`, `timeRanges.cull`, `timeRanges.total`, `PruneTransfers`, and `RemoveDoneTransfers`.

## Control Flow

The test file builds synthetic stats, transfers, and time ranges to verify edge cases such as invalid ETA inputs, overflow caps, overlapping transfer windows, retry-after/fatal/no-retry classification, and completed-transfer retention limits.

## State and Persistence Behavior

Tests are process-local but temporarily modify `MaxCompletedTransfers` and config values. Transfer/time-range state simulates active and completed operations without remote IO.

## Dependencies and Integration Points

It integrates with `fserrors`, `fs.ConfigInfo`, `Transfer`, and rc stats rendering.

## Risks and Test Signals

The tests protect user-visible stats formatting and accounting math. They should be extended when adding counters to `StatsInfo`, changing ETA semantics, or changing transfer retention behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/stats_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/token_bucket.go -->
# sources/user-network-fs/rclone/fs/accounting/token_bucket.go

## Purpose

`token_bucket.go` implements global bandwidth limiting for rclone accounting and transport paths.

## Important APIs, Types, and Functions

Exports include global `TokenBucket`, `TokenBucketSlot`, and slot constants for accounting, transport RX, and transport TX. Internal `buckets` and `tokenBucket` hold current/previous limiters and schedule state. Key methods are `StartTokenBucket`, `StartTokenTicker`, `LimitBandwidth`, `SetBwLimit`, and rc handler `rcBwlimit`.

## Control Flow

Startup reads `ConfigInfo.BwLimit`, creates `rate.Limiter` buckets when limits are set, empties initial bursts, starts optional signal handling, and may start a minute ticker for scheduled limit changes. Read/accounting paths call `LimitBandwidth`; rc calls can query or replace the current single limit.

## State and Persistence Behavior

State is process-local: current and previous limiter arrays, current timetable slot, and toggle flag. Scheduled updates replace `curr` or `prev` depending on SIGUSR2 toggle state.

## Dependencies and Integration Points

It depends on `golang.org/x/time/rate`, `fs.BwPair`/`BwTimetable`, rc, logging, and the Unix/non-Unix signal-handler files.

## Risks and Test Signals

Risks include burst-size overflow, schedule/toggle confusion, blocking on context.Background, rc accepting only one schedule entry, and inconsistent accounting versus transport limits. Tests cover rc set/query modes; integration tests should verify actual throttling and SIGUSR2 behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/token_bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/token_bucket_test.go -->
# sources/user-network-fs/rclone/fs/accounting/token_bucket_test.go

## Purpose

`token_bucket_test.go` validates the remote-control interface for bandwidth limits.

## Important APIs, Types, and Functions

`TestRcBwLimit` retrieves the `core/bwlimit` rc call and tests setting/querying rates such as `1M`, `off`, and asymmetric pairs.

## Control Flow

The test calls the rc handler with different `rc.Params`, checks returned `rate`, `bytesPerSecond`, `bytesPerSecondTx`, and `bytesPerSecondRx`, and verifies state persists for subsequent query calls.

## State and Persistence Behavior

It mutates the global `TokenBucket` state in process. Tests that run afterward can observe the last configured limit unless they reset it.

## Dependencies and Integration Points

It integrates with rc call registration, `fs.BwTimetable` parsing, and token bucket state.

## Risks and Test Signals

The test protects rc API shape but does not measure real throttling, scheduled timetables, or signal toggling. Additional tests should reset global state and cover invalid rates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/token_bucket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/tpslimit.go -->
# sources/user-network-fs/rclone/fs/accounting/tpslimit.go

## Purpose

`tpslimit.go` implements a global transactions-per-second limiter, typically used by HTTP transaction paths.

## Important APIs, Types, and Functions

Global `tpsBucket` is a `*rate.Limiter`. `StartLimitTPS(ctx)` creates it when `ConfigInfo.TPSLimit` is positive, using `TPSLimitBurst` or at least one. `LimitTPS(ctx)` waits on the limiter and logs non-cancel errors.

## Control Flow

Accounting startup calls `StartLimitTPS`. Transaction paths call `LimitTPS` before making requests; if no limiter exists, the call is a no-op.

## State and Persistence Behavior

State is process-global and in memory. Starting multiple times can replace the limiter.

## Dependencies and Integration Points

It depends on `fs.ConfigInfo`, logging, and `golang.org/x/time/rate`. It complements bandwidth limiting but controls request rate rather than bytes.

## Risks and Test Signals

Risks include global state leakage across tests, context cancellation behavior, and unexpected serialization of unrelated backends. Tests should verify timing with configured limits and no-op behavior when disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/tpslimit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/tpslimit_test.go -->
# sources/user-network-fs/rclone/fs/accounting/tpslimit_test.go

## Purpose

`tpslimit_test.go` checks that TPS limiting delays operations within expected timing bounds.

## Important APIs, Types, and Functions

`TestLimitTPS` uses an inner `timeTransactions` helper to call `LimitTPS` repeatedly and compare elapsed time to expected min/max windows.

## Control Flow

The test configures `tpsBucket` directly or via start logic, times transactions, and resets `tpsBucket` to nil afterward.

## State and Persistence Behavior

It mutates the package-global limiter and relies on wall-clock timing, making it sensitive to scheduler load.

## Dependencies and Integration Points

It integrates with the rate limiter and context handling.

## Risks and Test Signals

The test is a timing signal rather than a deterministic functional proof. CI slowness can cause flaky upper-bound failures; race tests should confirm no concurrent global-state surprises.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/tpslimit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/transfer.go -->
# sources/user-network-fs/rclone/fs/accounting/transfer.go

## Purpose

`transfer.go` models one logical transfer or check and connects object-level lifecycle events to `StatsInfo` and `Account`.

## Important APIs, Types, and Functions

`TransferSnapshot` is the JSON/rc view of a transfer. `Transfer` stores immutable identity fields plus mutable account, error, and completion time under a mutex. Constructors create check or transfer records, and methods include `Done`, `Reset`, `Account`, `TimeRange`, `IsDone`, `Snapshot`, and `rcStats`.

## Control Flow

Creating a transfer adds it to `StatsInfo.startedTransfers` and to checking/transferring maps via caller methods. `Account` creates or updates the accounting reader. `Done` records errors, closes and finalizes the account, marks completion, updates check/transfer counters, removes live maps, and prunes old completed transfers.

## State and Persistence Behavior

Transfer records remain in memory after completion until pruned. Snapshots include source/destination fs config strings when available. Errors are stored for completed-transfer reporting.

## Dependencies and Integration Points

It integrates with `StatsInfo`, `Account`, `fs.DirEntry`, `fs.ObjectInfo`, remote-control output, and JSON marshaling.

## Risks and Test Signals

Risks include lock misuse in `Reset`, double `Done`, account close errors, retaining fs config strings, and completed-transfer pruning. Tests cover snapshot fields, done behavior, checking transfers, and rc stats.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/transfer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/transfer_test.go -->
# sources/user-network-fs/rclone/fs/accounting/transfer_test.go

## Purpose

`transfer_test.go` validates `Transfer` lifecycle and snapshot/rc output.

## Important APIs, Types, and Functions

`TestTransfer` creates a transfer with a mock object, checks snapshots before and after completion, verifies rc stats, and covers checking-transfer snapshots.

## Control Flow

The test constructs `StatsInfo`, mock source/destination fs values, calls `newTransfer`, inspects `Snapshot`, calls `Done`, and validates completion timestamps and fields.

## State and Persistence Behavior

All state is in memory. The test exercises stats counters and transfer retention indirectly.

## Dependencies and Integration Points

It integrates with `mockobject`, fs config strings, and `StatsInfo`.

## Risks and Test Signals

It signals stable JSON/rc-visible transfer fields. Additional coverage would be useful for `Account`, `Reset`, error snapshots, and double completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/transfer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/transfermap.go -->
# sources/user-network-fs/rclone/fs/accounting/transfermap.go

## Purpose

`transfermap.go` manages live transfer/check maps and renders their human and rc progress views.

## Important APIs, Types, and Functions

`transferMap` wraps a mutex, map, and display name. Methods add/delete/merge entries, test emptiness/count, sort transfers by start time/name, render strings, compute aggregate progress from `inProgress`, list remotes, and build rc stat arrays.

## Control Flow

Stats code adds transfers when operations begin and deletes them on completion. Reporting paths sort current transfers, optionally exclude duplicates, look up active accounts for detailed byte/speed/ETA information, and otherwise print only the transfer purpose.

## State and Persistence Behavior

State is in memory and keyed by remote name. Merge copies transfer pointers for aggregate group views.

## Dependencies and Integration Points

It integrates with `StatsInfo.String`, `RemoteStats`, `inProgress`, `Transfer.rcStats`, and config-driven filename width.

## Risks and Test Signals

Risks include remote-name collisions, mutable pointer sharing in aggregate maps, lock nesting with exclude maps, and reporting stale/no-progress entries. Tests should cover sorting, exclusion, progress aggregation, and rc output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/transfermap.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/asyncreader/asyncreader.go -->
# sources/user-network-fs/rclone/fs/asyncreader/asyncreader.go

## Purpose

`asyncreader.go` implements an asynchronous read-ahead `io.ReadCloser` used to buffer object reads independently from consumers.

## Important APIs, Types, and Functions

Exports are `BufferSize`, `ErrorStreamAbandoned`, `AsyncReader`, and `New`. Methods include `Read`, `WriteTo`, `SkipBytes`, `StopBuffering`, `Abandon`, and `Close`. Internal `buffer` objects hold pooled byte slices, terminal errors, and offsets.

## Control Flow

`New` validates input, initializes buffered channels and tokens, then starts a goroutine. The goroutine consumes tokens, gets pool buffers, soft-starts buffer size from 4 KiB up to `pool.BufferSize`, fills buffers with `readers.ReadFill`, sends them on `ready`, and exits on error or stop. Consumers call `fill`, serve data, return exhausted buffers, and propagate stored errors after buffered bytes are consumed.

## State and Persistence Behavior

State is per-reader memory: input stream, ready/token channels, current buffer, error, shutdown channels, pool reference, and closed flag. No data is persisted, but buffers are borrowed from a global pool and must be returned through `Abandon`/`Close`.

## Dependencies and Integration Points

It integrates with accounting buffering, `lib/pool`, `lib/readers`, `fs.ConfigInfo`, and any code that benefits from `io.WriterTo` acceleration or limited forward seeking with `SkipBytes`.

## Risks and Test Signals

Risks include deadlocks when stopping during reads, buffer leaks on abandon/error paths, `SkipBytes` token accounting mistakes, duplicate close behavior, and returning `ErrorStreamAbandoned` versus stored EOF/error correctly. Tests should cover short reads, EOF after buffered bytes, `WriteTo`, backward/forward skips, abandon/close races, and pool return.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/asyncreader/asyncreader.go -->
