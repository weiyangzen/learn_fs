# subset-b-009560 research

Grouped research report for Blobfuse2 release, build, command, mount, config, health monitor, and migration helpers under `sources/user-network-fs/blobfuse2`. Each section preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/blobfuse2-release.yaml -->
# sources/user-network-fs/blobfuse2/blobfuse2-release.yaml

Purpose: Azure Pipelines release definition for building, signing, testing, optionally creating a GitHub release, and optionally publishing Blobfuse2 packages into Microsoft Linux package repositories. The pipeline is manually triggered only and is parameterized by release tag, unit-test execution, GitHub release posting, package publishing, draft/prerelease status, and version update.

Important APIs/types/functions: pipeline parameters, stages `BuildArtifacts`, `SignArtifacts`, `TestArtifacts`, `ReleaseArtifacts`, and conditional `PublishArtifacts`; Azure DevOps tasks `PublishBuildArtifacts@1`, `DownloadBuildArtifacts@0`, ESRP code-signing tasks, `GithubRelease@1`, `PipAuthenticate@1`, and `AzureCLI@2`; shared variable group `NightlyBlobFuse`; package tooling `fpm`, `rpm`, `dpkg`, `pmc-cli`, and `packages.csv`.

Control flow: build jobs clone `Azure/azure-storage-fuse`, check out the source branch, install Go/build/fpm dependencies, call `azure-pipeline-templates/build-release.yml`, assemble package roots, and create deb/rpm artifacts for fuse2/fuse3 and x86_64/ARM variants. Signing downloads the temporary artifacts, signs deb/rpm packages, makes signed outputs executable, and republishes them. Test jobs download signed artifacts, rename them to distro-specific package names, install them on Ubuntu, Debian-compatible, RHEL, CentOS, Oracle, SUSE, Mariner, Rocky, and ARM images, run release distro tests, and build/publish containers where configured. Release creates or edits a GitHub release only when `post_release` is true. Publishing, gated by `publish_artifacts`, uploads signed packages with `pmc`, associates package IDs to repos listed in `setup/packages.csv`, adjusts Mariner preview repository names for preview builds, and publishes non-ARM repos.

State/persistence behavior: persistent artifacts flow through Azure DevOps artifact names `blobfuse2-temp`, `blobfuse2-signed`, and `blobfuse2`. Release assets are attached to the GitHub tag supplied by the user. Linux repository state is mutated by `pmc repo package update` and `pmc repo publish`; those operations depend on current package filenames and the downloaded `packages.csv`. Build outputs are repeatedly renamed to include distro, architecture, fuse flavor, preview, or Mariner `cm2` naming.

Dependencies/integration: integrates private Azure DevOps agent pools, Microsoft packages feed, ESRP signing, GitHub release service connection, Azure WIF subscription `WIF_MI_ESRP_V5`, container publication scripts, release distro test templates, and package repository ingestion. It assumes specific hosted or custom images and distro labels are available.

Risks/test signals: risk is high because the file mixes build, signing, test, and publication side effects. Shell globs, `ls | grep`, branch extraction with `cut`, preview-name heuristics, and package ID variable indirection are brittle. The main test signal is successful package installation and release-distro tests across the matrix before publish stages run; repository publication still depends on external PMC success and the correctness of `packages.csv`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/blobfuse2-release.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/build.sh -->
# sources/user-network-fs/blobfuse2/build.sh

Purpose: local build helper for producing the main `blobfuse2` binary or the health monitor `bfusemon` binary. It selects fuse2, fuse3/default, or health-monitor builds based on the first argument.

Important APIs/types/functions: shell argument `$1`, `go version`, environment variables `CGO_ENABLED=1` and `GOTOOLCHAIN=local`, `go build -tags fuse2 -o blobfuse2`, `go build -o bfusemon ./tools/health-monitor/`, and default `go build -o blobfuse2`.

Control flow: print the Go version, force CGO and local toolchain use for FIPS-sensitive packaging, then branch on `$1`. `fuse2` removes old binary/source-directory artifacts and builds with the `fuse2` tag. `health` removes `bfusemon` and builds the health monitor tool. Any other argument builds the default fuse3-capable Blobfuse2 binary.

State/persistence behavior: writes `blobfuse2` or `bfusemon` in the repository root and removes old `blobfuse2`, `bfusemon`, or `azure-storage-fuse` paths before some builds. It intentionally prevents Go's automatic toolchain download so package builds do not silently switch to an upstream non-FIPS toolchain.

Dependencies/integration: depends on the installed local Go toolchain, CGO-capable C build environment, fuse build tags, and the `tools/health-monitor` package. It is used by release/build pipelines and local developer workflows.

Risks/test signals: destructive `rm -rf azure-storage-fuse` is safe in the release clone layout but risky if run from an unexpected directory. There is no `set -e`, so future multi-command edits could mask failures. The direct signal is whether `go build` exits successfully and the expected binary appears.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/componentGenerator.sh -->
# sources/user-network-fs/blobfuse2/cmd/componentGenerator.sh

Purpose: developer-only generator for adding a new Blobfuse2 pipeline component from `internal/component.template` and then regenerating blank-import registration in `cmd/imports.go`.

Important APIs/types/functions: shell parameter `$1`, derived variables `comp_name`, `comp_name_C`, `comp_path`, and `comp_file`; template copy from `./internal/component.template`; `sed -i` replacement of `<component>` and `<component_C>`; and delegation to `./cmd/importGenerator.sh`.

Control flow: print a banner, normalize the component name into a Go-style class name, fail if `./component/<name>` already exists, create the component directory, copy the template into `<name>.go`, replace placeholders, then regenerate component imports.

State/persistence behavior: creates a new `component/<name>/<name>.go` file and mutates `cmd/imports.go` through the import generator. It does not roll back partial changes if placeholder replacement or import regeneration fails.

Dependencies/integration: assumes it is executed from the repository root, uses GNU-style `sed -r` and `${1^}` capitalization, and depends on `internal/component.template` matching the placeholder contract. The hidden Cobra `generate` command wraps this script.

Risks/test signals: whitespace or unusual component names can break paths/imports. The script uses `exit` without an explicit nonzero status when a component exists, so callers may treat that failure as success. There are no tests in this subset; success is visible through the generated component and updated imports compiling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/componentGenerator.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/doc.go -->
# sources/user-network-fs/blobfuse2/cmd/doc.go

Purpose: hidden Cobra command that generates Markdown documentation for the complete Blobfuse2 command tree.

Important APIs/types/functions: `docCmdInput.outputLocation`, hidden `docCmd`, `os.Stat`, `os.MkdirAll`, `cobra/doc.GenMarkdownTree`, and `rootCmd.AddCommand(docCmd)`. The `--output-location` persistent flag defaults to `./doc`.

Control flow: `RunE` validates the output path. If the path is absent it creates the directory, if it is inaccessible it returns a wrapped access error, and if it is a file it rejects it. After validation it calls `doc.GenMarkdownTree(rootCmd, outputLocation)` and returns a user-facing error if generation fails.

State/persistence behavior: creates or populates the documentation output directory with Markdown files for the whole command tree, including hidden commands. It does not remove stale docs before generation, so repeated runs can leave obsolete files if commands are renamed.

Dependencies/integration: integrates with the global Cobra root command and every registered command/flag in package `cmd`. It depends on filesystem permissions for the output path.

Risks/test signals: because it walks the whole mutable command tree, invalid command metadata or output permissions can fail generation. Tests cover successful generation, directory creation/access failures, generation failure under `/var`, and rejection of a file as output location.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/doc_test.go -->
# sources/user-network-fs/blobfuse2/cmd/doc_test.go

Purpose: testify suite validating the hidden `doc` command's filesystem handling and Markdown generation error paths.

Important APIs/types/functions: `docTestSuite`, `SetupTest`, `cleanupTest`, `executeCommandC`, `resetCLIFlags`, `randomString`, `os.ReadDir`, `os.CreateTemp`, and tests `TestDocsGeneration`, `TestOutputDirCreationError`, `TestDocsGenerationError`, and `TestOutputDirIsFileError`.

Control flow: setup resets `docCmdInput` and mount options, installs a silent logger, and each test invokes the Cobra command through `executeCommandC`. The success case creates a temp output directory under `/tmp`, runs `doc`, and asserts files exist. Negative cases use unwritable or invalid paths and assert returned output contains expected error fragments.

State/persistence behavior: creates temporary directories and files, removes them with defers, and resets CLI flags after tests to avoid cross-test Cobra state leakage.

Dependencies/integration: depends on root command registration, Cobra doc generation, test helper `executeCommandC`, and filesystem permissions that make `/var/docs_*` unwritable in normal test environments.

Risks/test signals: tests assert error text fragments, so wording changes can break them. Running as root may alter permission assumptions for `/var/docs_*`. The suite's main signal is command behavior before and during Markdown tree generation rather than content correctness of generated docs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/doc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/gen-config.go -->
# sources/user-network-fs/blobfuse2/cmd/gen-config.go

Purpose: user-facing `gen-config` command that emits a default Blobfuse2 YAML configuration for file-cache, block-cache, direct-IO, and read-only scenarios.

Important APIs/types/functions: `genConfigParams`, global `optsGenCfg`, Cobra command `generatedConfig`, `internal.GetComponent(component).GenConfig()`, `config.Set`, `common.WriteToFile`, and flags `--block-cache`, `--tmp-path`, `--direct-io`, `--o`, and `--ro`.

Control flow: if no flags are supplied the command shows help. File-cache mode requires `--tmp-path`; block-cache mode does not. It records read-only/direct-IO/tmp-path settings into config state, builds a pipeline beginning with `libfuse`, selecting `block_cache` or `file_cache`, optionally adding `attr_cache` when direct-IO is off, and ending with `azstorage`. It emits top-level direct-IO/read-only fields, logger comments, component list, each component's generated config, and commented required `azstorage` guidance. Output goes to `./blobfuse2.yaml`, a user file, or console when `--o console`.

State/persistence behavior: mutates global config state and writes/truncates a YAML file unless console output is selected. It uses absolute paths in the success message but does not validate that the cache path itself exists.

Dependencies/integration: relies on every selected component being registered in `internal` and providing stable `GenConfig()` output. It is coupled to command flag state and package-global `optsGenCfg`.

Risks/test signals: direct-IO removes `attr_cache`, and missing file-cache tmp path is intentionally an error. The custom flag error function prints help and returns nil, which may hide unknown-flag failures. Tests cover missing tmp path, file-cache and block-cache content, direct-IO content, custom output file, and console output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/gen-config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/gen-config_test.go -->
# sources/user-network-fs/blobfuse2/cmd/gen-config_test.go

Purpose: testify suite for the `gen-config` command's generated YAML shape and required-flag behavior.

Important APIs/types/functions: `genConfig` suite, `SetupTest`, `cleanupTest`, `getDefaultLogLocation`, `executeCommandC`, and tests for file-cache, block-cache, direct-IO, custom output, console output, and missing temp path.

Control flow: each test invokes `rootCmd gen-config` with a particular flag combination, then reads the generated file when one is expected and checks for component names, temp path inclusion, direct-IO setting, and absence of cache path text in direct-IO cases. Cleanup removes `./blobfuse2.yaml` and resets `optsGenCfg`.

State/persistence behavior: writes `./blobfuse2.yaml` or `1.yaml` in the current working directory and removes those files. It creates temporary cache directories for tests that need a path but does not depend on their contents.

Dependencies/integration: depends on component `GenConfig()` output containing strings such as `file_cache` and `block_cache`, the shared command execution helper, and local filesystem write permission.

Risks/test signals: `TestConsoleOutput` asserts the captured command output is empty even though `fmt.Println` writes to process stdout rather than Cobra output, so it is testing the helper's capture behavior as much as command behavior. The suite is narrow but catches regressions in required tmp-path checks, pipeline selection, and file output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/gen-config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/gen-test-config.go -->
# sources/user-network-fs/blobfuse2/cmd/gen-test-config.go

Purpose: hidden test helper command that expands template config files by replacing placeholders with environment values, a container name, and a temp path.

Important APIs/types/functions: `configGenOptions`, global `opts`, `templatesDir`, hidden Cobra command `generateTestConfig`, `os.ReadFile`, regexp `{.*?}`, `os.Getenv`, and `os.WriteFile`.

Control flow: read the template either from the provided path when it already contains `testdata/config/` or from `testdata/config/<config-file>`. Find every `{ ... }` token. Replace `{ 0 }` with `--container-name`, `{ 1 }` with `--temp-path`, and all other tokens with the environment variable whose name is inside the braces. Write the expanded config to `--output-file` with mode `0700`.

State/persistence behavior: creates or overwrites the output config file. It reads process environment variables but does not validate that replacements are non-empty. It stores command options in package-global `opts`.

Dependencies/integration: used by tests and automation that need runtime credentials or temp paths injected into config templates. It depends on the template placeholder format with spaces inside braces.

Risks/test signals: regexp replacement treats placeholders as regular expressions and can behave unexpectedly if placeholder contents gain regex metacharacters. Missing flags are not explicitly validated, and empty environment variables silently become empty config values. No direct test file is included in this work item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/gen-test-config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/generator.go -->
# sources/user-network-fs/blobfuse2/cmd/generator.go

Purpose: hidden Cobra command that exposes the component generator script through the Blobfuse2 CLI for developer use.

Important APIs/types/functions: hidden `generateCmd`, `cobra.ExactArgs(1)`, `exec.Command("./cmd/componentGenerator.sh", componentName)`, and stdout/stderr forwarding to the current process.

Control flow: accept one component name, run `./cmd/componentGenerator.sh <component>`, mirror script output to stdout, and return a wrapped error if the script exits unsuccessfully.

State/persistence behavior: the Go file itself only starts a subprocess, but the subprocess creates component files and rewrites `cmd/imports.go`. No state cleanup or transactionality is provided if generation is partial.

Dependencies/integration: depends on repository-root current working directory, executable shell scripts, and the template/import generator contract. It is integrated into the root Cobra command but hidden from normal users.

Risks/test signals: running from a different working directory fails because the script path is relative. There is no validation of component name before shelling out. No tests are included here; compile-time command registration and successful subprocess execution are the available signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/generator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/health-monitor.go -->
# sources/user-network-fs/blobfuse2/cmd/health-monitor.go

Purpose: hidden `health-monitor` command that launches the external Blobfuse monitor binary for a running Blobfuse2 mount using the mount's config and process ID.

Important APIs/types/functions: `monitorOptions`, globals `pid` and `cacheMonitorOptions`, `resetMonitorOptions`, hidden `healthMonCmd`, `validateHMonOptions`, `buildCliParamForMonitor`, `parseConfig`, `config.UnmarshalKey`, `file_cache.FileCacheOptions`, and external command `hmcommon.BfuseMon`.

Control flow: reset monitor state, validate that `--pid` and `--config-file` are non-empty, parse the config, unmarshal `file_cache` and `health_monitor`, build bfusemon CLI parameters, execute `bfusemon`, log stdout if any, and disable monitoring on failure. `buildCliParamForMonitor` always passes the target pid, cache path, and max cache size, conditionally adds poll/output flags, and translates disable-list entries into `--no-*` flags.

State/persistence behavior: reads mount config and spawns a separate monitor process. It mutates `common.EnableMonitoring` to false on start failure and relies on the monitor binary for any output-path persistence. It uses package-global mount options shared with the mount command.

Dependencies/integration: started by `mount.go` through `startMonitor`, relies on `bfusemon` being installed or in PATH, and shares constants with `tools/health-monitor/common`. It depends on valid file-cache config even when file-cache monitoring is disabled.

Risks/test signals: missing `bfusemon`, invalid config, or empty pid/config flags produce command errors. Disable-list values that are not recognized are only debug logged. Tests cover option validation, CLI param construction, invalid config paths, external-start failure, and stop command failure paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/health-monitor.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/health-monitor_stop.go -->
# sources/user-network-fs/blobfuse2/cmd/health-monitor_stop.go

Purpose: `health-monitor stop` subcommand that kills the health monitor associated with a specific Blobfuse2 process ID.

Important APIs/types/functions: global `blobfuse2Pid`, Cobra command `healthMonStop`, helper `getPid(blobfuse2Pid)`, helper `stop(pid)`, `ps aux`, regexp PID extraction, and `kill -9`.

Control flow: trim and validate `--pid`; scan `ps aux` output for a line containing `bfusemon` and `--pid=<blobfuse2Pid>`; extract the first numeric token as the monitor PID; call `kill -9 <pid>`; print success messages or return wrapped failure messages.

State/persistence behavior: mutates operating-system process state by forcibly killing the matched monitor. It does not update any Blobfuse config or pid file.

Dependencies/integration: registered under `healthMonCmd` and also attaches `healthMonStopAll`. It depends on Unix `ps` and `kill`, process command-line visibility, and the monitor binary name containing `bfusemon`.

Risks/test signals: matching by substring can select an unintended process, and the first-number regex assumes `ps aux` output starts with the PID after the user column. `kill -9` prevents graceful cleanup. Tests cover empty pid, nonexistent monitor pid, and direct kill failure for random PIDs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/health-monitor_stop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/health-monitor_stop_all.go -->
# sources/user-network-fs/blobfuse2/cmd/health-monitor_stop_all.go

Purpose: `health-monitor stop all` subcommand that terminates all running health monitor binaries.

Important APIs/types/functions: Cobra command `healthMonStopAll`, helper `stopAll`, `exec.Command("killall", hmcommon.BfuseMon)`, and `hmcommon.BfuseMon`.

Control flow: run `killall <bfusemon-binary-name>`, return a wrapped error if the command fails, and print a success message otherwise.

State/persistence behavior: mutates OS process state by killing all monitor processes with the configured binary name. It does not inspect mount ownership or update monitor state files.

Dependencies/integration: depends on Unix `killall` behavior and the shared health monitor binary-name constant. It is registered as a child of `health-monitor stop`.

Risks/test signals: broad process-name termination may affect monitors for unrelated Blobfuse2 mounts or tests. It returns an error when no matching process exists on systems where `killall` exits nonzero; the included test expects this failure path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/health-monitor_stop_all.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/health-monitor_test.go -->
# sources/user-network-fs/blobfuse2/cmd/health-monitor_test.go

Purpose: unit tests for health-monitor option validation, bfusemon CLI construction, invalid start conditions, and stop subcommands.

Important APIs/types/functions: `configHmonTest`, `hmonTestSuite`, `generateRandomPID`, `validateHMonOptions`, `buildCliParamForMonitor`, `executeCommandC`, `stop`, and constants from `tools/health-monitor/common`.

Control flow: setup installs a silent debug logger. Tests validate empty pid/config messages, construct monitor options with all disable-list variants plus an invalid option and assert the generated CLI length, run the hidden command with empty or nonexistent config, run it with a valid config but expect external `bfusemon` startup failure, and exercise stop-all, empty pid, nonexistent monitor pid, and direct kill failure.

State/persistence behavior: writes a temporary config file for the startup-failure case and resets health-monitor CLI flags after most tests. It uses random PIDs intended not to correspond to live processes.

Dependencies/integration: depends on command helpers, file-cache option structs, common logger, Unix process commands used by stop helpers, and absence of a matching `bfusemon` process for negative tests.

Risks/test signals: random PID generation uses `os.FindProcess`, which does not reliably prove nonexistence on Unix; tests are still mostly negative-path checks. If `bfusemon` is installed and accepts the generated config, the expected failure test could change behavior. The suite is useful for parameter translation and error contracts, not for monitoring correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/health-monitor_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/importGenerator.sh -->
# sources/user-network-fs/blobfuse2/cmd/importGenerator.sh

Purpose: shell generator that rewrites `cmd/imports.go` with blank imports for every component directory so component packages self-register.

Important APIs/types/functions: `loader_file="./cmd/imports.go"`, shell redirection, `find . -type d`, `grep "component/"`, `cut -c 3-`, `sort -u`, and generated import path `github.com/Azure/azure-storage-fuse/v2/$i`.

Control flow: print a banner, truncate/write `package cmd`, start an import block, iterate sorted component directories, append one blank import per directory, and close the block.

State/persistence behavior: overwrites `cmd/imports.go` in place. It has no atomic write, no formatting step, and no rollback on failure.

Dependencies/integration: used by `componentGenerator.sh`; expected output is compiled by the `cmd` package to trigger component registration side effects. It assumes repository-root execution and component paths without whitespace.

Risks/test signals: the comment notes whitespace will break the loop. The `find | grep` pattern can include nested directories below a component, producing invalid imports if components gain internal subdirectories. The generated file compiling is the primary signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/importGenerator.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/imports.go -->
# sources/user-network-fs/blobfuse2/cmd/imports.go

Purpose: generated component loader that blank-imports all Blobfuse2 component packages so their init-time registration is linked into the CLI binary.

Important APIs/types/functions: blank imports for `attr_cache`, `azstorage`, `block_cache`, `custom`, `entry_cache`, `file_cache`, `libfuse`, `loopback`, and `xload` component packages.

Control flow: no runtime functions are defined in this file. Go evaluates imported packages for side effects during program initialization.

State/persistence behavior: no direct runtime persistence. The build artifact's available component registry depends on this file containing the expected imports.

Dependencies/integration: tightly coupled to the component registration mechanism used by `internal.GetComponent`, `internal.NewPipeline`, and config generation. Regenerated by `cmd/importGenerator.sh`.

Risks/test signals: if a component import is missing, pipelines or generated config that reference that component can fail at runtime. If stale or nested invalid imports are generated, the project fails to compile. Existing tests indirectly exercise registration through `gen-config`, mount pipeline validation, and config conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/imports.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mount.go -->
# sources/user-network-fs/blobfuse2/cmd/mount.go

Purpose: core `mount [path]` command that parses Blobfuse2 config/flags, validates mount settings, builds an internal component pipeline, starts it in foreground or daemon mode, handles logging/profiling/monitoring, and exposes mount subcommands.

Important APIs/types/functions: `LogOptions`, `mountOptions`, global `options`, `validate`, `OnConfigChange`, `parseConfig`, `mountCmd`, `monitorChild`, `ignoreFuseOptions`, `runPipeline`, `startMonitor`, `tempCacheCleanup`, `cleanupCachePath`, `sigusrHandler`, `setGOConfig`, `startDynamicProfiler`, `internal.NewPipeline`, `pipeline.Start/Stop`, `go-daemon`, `config`, `common`, and `log`.

Control flow: `RunE` expands the input mount path, finds or reads the config file, decrypts secure configs when requested, unmarshals options, and synthesizes a default component pipeline if none is configured. It inserts `entry_cache` for entry-cache config, validates component order, applies block-cache or preload pipeline overrides, converts v1 `libfuse-options` into v2 config keys, rejects direct-IO plus kernel-cache disabling, supplies default logging, validates mount path/work dir/log paths, initializes logging, runs version check, logs unsupported v1 flags, enables monitoring flags, removes `attr_cache` for direct-IO, optionally cleans cache directories, and creates the pipeline. In background mode it daemonizes, writes pid/trace files, waits for child success, timeout, or early child exit, and reads child trace output on failure. In foreground mode it optionally runs CPU/memory profiles and blocks in `runPipeline`.

State/persistence behavior: reads YAML or encrypted config, writes/locks daemon pid files under the default work dir, creates trace files, creates default work/log directories, updates global config keys such as `mount-path` and `direct-io`, can delete cache directory contents when cleanup flags are set, starts monitor processes, and writes logs. Signal handling reloads config/logging on `SIGUSR1`.

Dependencies/integration: integrates Cobra flags with the custom config layer, common filesystem/mount helpers, component pipeline construction, libfuse component behavior, secure config crypto helpers, go-daemon, Go pprof HTTP server, and health-monitor command invocation. `mount list` and `mount all` are registered as child commands here.

Risks/test signals: package-global `options` and viper/config state require careful reset in tests. Background daemon control depends on signals, pid files, trace files, and mount timing. FUSE option parsing rejects unknown options and accepts a selected compatibility subset. Direct-IO modifies pipeline state by removing `attr_cache`. Tests cover missing/invalid config, mount path validation, non-empty mount handling, component order, direct-IO config propagation, v1 fuse option parsing, invalid uid/gid/umask, cleanup-on-start, log goroutine defaults, and many command error paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mount_all.go -->
# sources/user-network-fs/blobfuse2/cmd/mount_all.go

Purpose: `mount all [path]` subcommand that enumerates all containers in an Azure Storage account and starts a separate Blobfuse2 mount for each allowed container.

Important APIs/types/functions: `containerListingOptions`, global `mountAllOpts`, Cobra command `mountAllCmd`, `processCommand`, `getContainerList`, `filterAllowedContainerList`, `mountAllContainers`, `updateCliParams`, `writeConfigFile`, `buildCliParamForMount`, `ignoreCliParam`, `azstorage.AzStorage`, `viper`, and `yaml`.

Control flow: `processCommand` reads the default or supplied config, unmarshals mount options, validates the base mount path while allowing non-empty directories, initializes logging, sets `mount-path` and `mount-all-containers`, unmarshals `mountall` allow/deny lists, validates secure-config passphrase if needed, lists containers through an `azstorage` component, filters the list, and mounts each remaining container. `mountAllContainers` derives per-container mount paths and config filenames, creates mount directories, sets container-specific config keys, writes plain or encrypted per-container config files when an input config exists, or injects container/tmp-path CLI flags when running from environment/defaults, then invokes the current blobfuse2 binary with `mount` arguments and disables version checks.

State/persistence behavior: creates one subdirectory per mounted container under the requested path, writes per-container config files under `common.DefaultWorkDir`, mutates viper state between containers, and starts daemonized child mounts. It accumulates failure count but returns nil after per-container failures unless config writing or setup fails.

Dependencies/integration: depends on Azure storage credentials/config sufficient for `azstorage.Configure`, `Start`, and `ListContainers`; reuses `parseConfig`, `options.validate`, log setup, secure config crypto, and the main `mount` command via subprocess. Allow/deny lists come from the `mountall` config section.

Risks/test signals: map iteration in `filterAllowedContainerList` returns containers in nondeterministic order. Reusing mutable global viper state across containers can leak settings if not reset carefully. Shelling out to `os.Args[0]` assumes the current binary path is executable. Tests in `mount_test.go` cover validation failures and `updateCliParams`; full multi-container behavior depends on live Azure integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mount_all.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mount_list.go -->
# sources/user-network-fs/blobfuse2/cmd/mount_list.go

Purpose: `mount list` subcommand that prints currently known Blobfuse2 mount points.

Important APIs/types/functions: Cobra command `mountListCmd`, `common.ListMountPoints`, and `fmt.Println`.

Control flow: call `common.ListMountPoints`; return a wrapped error if listing fails; otherwise print numbered mount paths starting at 1.

State/persistence behavior: read-only command. It does not alter mounts or config.

Dependencies/integration: registered as a child of `mountCmd` and depends on the common mount discovery implementation, likely reading platform mount tables.

Risks/test signals: output format is simple text and may be consumed by users/scripts. Errors are only as precise as `common.ListMountPoints`. There is no dedicated test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mount_list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mount_test.go -->
# sources/user-network-fs/blobfuse2/cmd/mount_test.go

Purpose: broad unit/integration-style test suite for the main mount command, mount-all validation, fuse option parsing, cleanup-on-start, default config discovery, direct-IO behavior, and logging defaults.

Important APIs/types/functions: config fixtures `configMountTest`, `configPriorityTest`, `configDirectIOTest`; `mountTestSuite`; `SetupSuite`, `SetupTest`, `cleanupTest`; `executeCommandC`; `resetCLIFlags`; `viper.Reset`; `ignoreFuseOptions`; `updateCliParams`; `mountOptions.validate`; `tempCacheCleanup`; and `TestMountCommand`.

Control flow: the suite creates temporary config files and mount directories, invokes `rootCmd mount` or `rootCmd mount all`, and generally expects failure after validation or pipeline initialization because real storage/FUSE is not available. It verifies error text for missing directories, non-empty mount points, empty mount path, unsupported config type, missing config, missing default config, wrong component order, invalid log level, v1 compatibility flags, direct-IO/kernel-cache conflicts, invalid fuse options, invalid uid/gid/umask, unknown flags, ignored fuse options, CLI param replacement, mount option validation, cache cleanup for file_cache/block_cache/xload, and default goroutine-id behavior for log levels.

State/persistence behavior: creates/removes temp mount dirs, temp configs, default `config.yaml`, cache directories and files under `/tmp`, and resets global default work/log paths. It mutates global `options`, viper state, and config keys and must reset them to avoid cross-test contamination.

Dependencies/integration: depends on many shared helpers from the command test harness, common filesystem helpers, component pipeline validation, and local OS behavior for directory emptiness and path expansion. Some tests intentionally proceed to pipeline initialization and assert failure rather than mounting.

Risks/test signals: several assertions rely on exact error fragments. The suite does not validate successful live mounts, daemon behavior, or Azure connectivity, but it provides strong regression coverage for preflight validation and option translation. Global-state resets are essential; adding tests without cleanup can create flakes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mount_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mountgen1.go -->
# sources/user-network-fs/blobfuse2/cmd/mountgen1.go

Purpose: hidden `mountgen1` command that converts Blobfuse2-style config into an `adlsgen1fuse` JSON file and optionally runs the external ADLS Gen1 fuse binary.

Important APIs/types/functions: globals `azStorageOpt`, `libFuseOpt`, `fileCacheOpt`, `requiredFreeSpace`, `configFile`, `generateJsonOnly`, `gen1ConfigFilePath`; `resetGenOneOptions`; Cobra command `gen1Cmd`; `generateAdlsGenOneJson`; `runAdlsGenOneBinary`; `azstorage.AzStorageOptions`; `libfuse.LibfuseOptions`; and `file_cache.FileCacheOptions`.

Control flow: reset Gen1-specific options, parse the supplied config, unmarshal mount/logging options, validate the mount path, unmarshal `azstorage`, require account name, tenant ID, and client ID, default auth mode to `spn` when empty, unmarshal `libfuse` and `file_cache`, parse log level, generate the JSON config, and run `adlsgen1fuse <json>` unless `--generate-json-only` is true. JSON generation maps SPN auth to servicePrincipal credentials, sets authority/resource URLs, copies fuse timeout and allow-other settings, logging, retry/cache/free-space options, cache path, resource ID, and mount directory.

State/persistence behavior: writes the JSON file at `--output-file` or `/tmp/adlsgen1fuse.json` with mode `0777`. It intentionally omits the client secret because `adlsgen1fuse` reads `ADL_CLIENT_SECRET` from the environment. Running without generate-only starts an external mount process.

Dependencies/integration: depends on `parseConfig`, mount option validation, config unmarshalling for azstorage/libfuse/file_cache, and the `adlsgen1fuse` binary. It is also used by `mountv1 --enable-gen1` after converting v1 config.

Risks/test signals: only SPN auth is supported; other auth modes fail. The JSON file permission is broad. External binary absence is an expected failure in tests. Tests verify JSON creation, required config validation, invalid auth mode, and external-run failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mountgen1.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mountgen1_test.go -->
# sources/user-network-fs/blobfuse2/cmd/mountgen1_test.go

Purpose: tests for ADLS Gen1 JSON generation and mountgen1 error handling.

Important APIs/types/functions: `genOneConfigTestSuite`, fixtures `configGenOne`, `invalidConfig`, `invalidAuthMode`, `executeCommandC`, `config.ReadFromConfigFile`, `config.UnmarshalKey`, `viper.SetConfigFile`, and `resetCLIFlags`.

Control flow: setup installs a silent logger. `TestConfigCreation` writes a full SPN config, runs `mountgen1` with `--generate-json-only`, reads the output JSON through the config layer, and verifies client ID, tenant ID, cache dir, and mount dir. Negative tests write configs missing required fields or using auth mode `key` and expect errors. `TestGen1FuseMount` omits generate-only and expects failure because the external `adlsgen1fuse` binary is not available or cannot mount in the test environment.

State/persistence behavior: creates temp config files, temp JSON output files, and temp mount directories, removes them after each test, and resets `generateJsonOnly` and CLI flags.

Dependencies/integration: depends on config parser support for JSON after generation, command helper execution, and mountgen1's global state. The suite intentionally avoids persisting secrets; client secret is not checked.

Risks/test signals: `viper.SetConfigFile("json")` is unusual global state and can leak if not reset elsewhere. Assertions cover a representative subset of JSON fields, not the entire generated schema. The external-binary failure test could change if `adlsgen1fuse` is installed and runnable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mountgen1_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mountv1.go -->
# sources/user-network-fs/blobfuse2/cmd/mountv1.go

Purpose: `mountv1` command that converts legacy Blobfuse v1 config files and CLI flags into Blobfuse2 YAML, then optionally mounts with either the normal v2 mount path or the Gen1 mount path.

Important APIs/types/functions: `blobfuseCliOptions`, `ComponentsConfig`, `PipelineConfig`, many package-global v2 option structs, `resetOptions`, Cobra command `generateConfigCmd`, `parseFuseConfig`, `convertBfConfigParameter`, `convertBfCliParameters`, `yaml.Marshal`, and flags for v1 cache/storage/log/fuse options plus `--convert-config-only`, `--enable-gen1`, and `--required-free-space-mb`.

Control flow: optional version check runs first. The command resets conversion state, records an optional mount path, opens the v1 config file when supplied, scans it line-by-line, strips comments, requires `key value` pairs, and maps supported keys into v2 option structs. CLI flags are then converted and override overlapping file config. `-o` fuse options are parsed separately. The component list starts with `libfuse`, conditionally adds `stream`, `file_cache`, and `attr_cache`, then `azstorage`. If endpoint is not explicitly provided, it builds one from account name, account type, and HTTP/HTTPS settings, falling back to the storage account environment variable. It sets virtual-directory mode, marshals a `PipelineConfig` YAML to `--output-file`, and if not conversion-only invokes either `mountgen1` or `mount` through `rootCmd.Execute`.

State/persistence behavior: writes the converted YAML output file with mode `0700`. When not conversion-only it starts a mount command and may create normal mount/daemon state through `mount.go` or JSON/external process state through `mountgen1.go`. Conversion uses many package-global variables that persist until reset.

Dependencies/integration: integrates legacy config syntax, Cobra/pflag changed-state checks, syslog warnings for unsupported v1 flags, component option structs, Azure storage endpoint rules, environment variable `AZURE_STORAGE_ACCOUNT`, and the main command dispatcher. It shares `ignoreFuseOptions` with mount behavior.

Risks/test signals: scanner-based parsing rejects values split across whitespace and only supports a fixed key set. Some unsupported v1 flags are silently logged and ignored. Streaming cache math can divide by zero if block size/buffer size are not supplied consistently. Endpoint synthesis fails when account name is absent and environment fallback is missing. The broader `mountv1_test.go` suite, though outside this work item, covers config-file and CLI conversions, invalid fuse options, invalid account type/name, unsupported option warnings, and component ordering.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/cmd/mountv1.go -->
