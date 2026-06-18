# subset-b-000086 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/tests/helpers.bash -->
# sources/cloud-native/containers-storage/tests/helpers.bash

Purpose: shared Bats helpers for the `containers-storage` CLI test suite. It centralizes temporary storage setup, teardown, command invocation, random test-file creation, and reusable layer/diff assertions.

Important APIs and control flow: `setup` creates a random `TESTDIR` under `BATS_TMPDIR`, with `root` and `runroot` subdirectories, and disables overlay idmapped mounts for tests that expect legacy idmap behavior. `teardown` runs `storage wipe`, `storage shutdown`, and removes the temp directory. `storage`, `storagewithsorting`, and `storagewithsorting2` wrap the test binary with `--graph`, `--run`, driver, transient-store, and optional storage options. `populate` constructs three layered filesystems, capturing layer IDs in global variables; `checkchanges` and `checkdiffs` assert exact change lists and tar members from those layers.

State and persistence: state is intentionally temporary and isolated in `TESTDIR`; transient store mode changes lock-root expectations through `CONTAINERS_LOCK_ROOT` and `--transient-store`. Random files are timestamped to the epoch for deterministic archive/dedup behavior.

Dependencies and integration: depends on Bash, Bats `run/status/output/lines`, `dd`, `base64`, `touch`, `tar`, `sort`, and the `containers-storage` CLI. It is sourced by `test_runner.bash` and used by multiple Bats tests.

Risks: `eval` is not used here, but unquoted path expansion appears in several commands, so paths with spaces are not robust. `touch -d` is GNU-specific despite the comment about portability. Assertions encode exact diff ordering after sorted output, so driver-specific whiteout behavior can break tests.

Test signals: this file is itself test infrastructure; failures surface as Bats assertion failures in layer creation, diff generation, change detection, cleanup, or CLI shutdown paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/tests/helpers.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/tests/test_drivers.bash -->
# sources/cloud-native/containers-storage/tests/test_drivers.bash

Purpose: driver matrix launcher for the `containers-storage` Bats tests. It discovers supported graph drivers and invokes `test_runner.bash` once per selected driver.

Important APIs and control flow: helper functions `aufs`, `btrfs`, `overlay`, and `zfs` test availability through `modprobe`, `/proc/filesystems`, or filesystem type checks on `TMPDIR`. If `STORAGE_DRIVER` is unset, it builds a default list starting with `vfs` and conditionally appends available drivers; otherwise it uses the provided driver only. The final loop prints a Bats-style header and runs `test_runner.bash` with `STORAGE_DRIVER` exported.

State and persistence: no persistent state. It reads `TMPDIR` and `STORAGE_DRIVER`, and relies on `test_runner.bash` plus helpers to create per-test storage roots.

Dependencies and integration: Linux-focused due to `/proc/filesystems`, `modprobe`, and `stat -f -c`. Integrates with Bats through the downstream runner and with kernel storage modules for driver availability.

Risks: shell tests are unquoted around `TMPDIR`, and driver probing assumes GNU `stat`. `set -e` starts only after discovery, so probe failures before the loop are tolerated. Non-Linux platforms or minimal containers may under-detect drivers.

Test signals: its success is measured by all delegated Bats tests passing for each detected driver; discovery output also makes the active driver visible in TAP logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/tests/test_drivers.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/tests/test_runner.bash -->
# sources/cloud-native/containers-storage/tests/test_runner.bash

Purpose: thin execution wrapper for `containers-storage` Bats tests.

Important APIs and control flow: it enables `set -e`, changes to the directory containing the script using `readlink -f`, sources `helpers.bash`, defines `execute` to echo and run a command, defaults `TESTS` to all tests when no arguments are supplied, and runs `time bats --tap $TESTS`.

State and persistence: no persistence beyond the helper-supplied `TESTDIR` lifecycle. It inherits driver and storage options from the environment.

Dependencies and integration: depends on Bash, GNU `readlink -f`, `time`, and `bats`. It is called directly by `test_drivers.bash` and can also be invoked manually with test path arguments.

Risks: `execute` uses `eval`, so caller-provided test names are shell-interpreted. This is acceptable for trusted test harness use but unsafe for arbitrary input. `$TESTS` is unquoted to permit multiple tests, trading off pathname safety.

Test signals: returns the Bats process status and emits TAP output; failures propagate due to `set -e`.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/tests/test_runner.bash -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/tests/tools/Makefile -->
# sources/cloud-native/containers-storage/tests/tools/Makefile

Purpose: builds and vendors auxiliary tools used by the `containers-storage` test and verification workflows.

Important APIs and control flow: `vendor` runs `go mod tidy`, `go mod vendor`, and `go mod verify`. `all` builds the `build` directory targets. `go-build` is a make macro that builds a vendored package into `build/<basename>`. Targets build `git-validation`, `go-md2man`, and `golangci-lint`; the linter target downloads the version specified by `GOLANGCI_LINT_VERSION`.

State and persistence: writes binaries under `build/` and vendored dependencies under `vendor/`. `clean` removes `build/`.

Dependencies and integration: depends on Go modules, vendored tool packages, curl, and the upstream golangci-lint install script. It complements `tools.go`, which pins Go tool dependencies for vendoring.

Risks: `go-build` uses `$(shell ...)` during recipe expansion, which can make failures less obvious than normal recipe commands. The linter target downloads network code at build time and requires `GOLANGCI_LINT_VERSION`.

Test signals: successful target completion confirms tool binaries exist; `go mod verify` validates vendored module integrity.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/tests/tools/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/tests/tools/tools.go -->
# sources/cloud-native/containers-storage/tests/tools/tools.go

Purpose: Go tools pin file for test tooling. The `tools` build tag keeps tool dependencies in module metadata without compiling them into normal binaries.

Important APIs and control flow: it declares package `tools` and blank-imports `github.com/cpuguy83/go-md2man` and `github.com/vbatts/git-validation`. There are no runtime functions.

State and persistence: no runtime state. Its persistence effect is through `go.mod`, `go.sum`, and `vendor/`, because Go treats the imports as module requirements when the `tools` tag is considered.

Dependencies and integration: paired with `tests/tools/Makefile`, which builds the vendored tools. The file depends on Go build constraints to exclude it from ordinary builds.

Risks: tool versions are controlled indirectly by module resolution; if `go mod tidy` is run without respecting the tools pattern, dependencies can be dropped.

Test signals: `make vendor` and `go mod verify` confirm the tool imports remain resolvable and vendorable.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/tests/tools/tools.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/types/default_override_test.conf -->
# sources/cloud-native/containers-storage/types/default_override_test.conf

Purpose: small TOML fixture for testing `CONTAINERS_STORAGE_CONF` override behavior.

Important fields and flow: defines `[storage]` with an empty `driver`, `graphroot = "environment_override_graphroot"`, and `rootless_storage_path = "environment_override_rootless_storage_path"`. It is not meant to be a full storage configuration.

State and persistence: fixture-only. It simulates an explicitly selected config file whose paths should be returned or parsed by configuration helpers.

Dependencies and integration: used by `types/utils_test.go` through `t.Setenv("CONTAINERS_STORAGE_CONF", "default_override_test.conf")` to assert `DefaultConfigFile` resolves the environment override for both rootless and root contexts.

Risks: relative path assumptions mean tests must run from the `types` package directory or with Go's package test working-directory semantics.

Test signals: successful override tests show that `CONTAINERS_STORAGE_CONF` has priority over default rootful and rootless config locations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/types/default_override_test.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/types/errors.go -->
# sources/cloud-native/containers-storage/types/errors.go

Purpose: central sentinel error definitions for storage-layer, image, container, metadata, read-only, user namespace, and integrity-check failure modes.

Important APIs and control flow: exports package variables such as `ErrContainerUnknown`, `ErrDuplicateID`, `ErrIncompleteOptions`, `ErrStoreIsReadOnly`, `ErrInvalidMappings`, `ErrNoAvailableIDs`, and many layer/image/container integrity errors. There is no control flow; callers compare or wrap these values with `errors.Is` semantics.

State and persistence: no mutable state. The values are process-wide sentinels created with `errors.New`.

Dependencies and integration: used across the storage library as stable error contracts between stores, drivers, repair/check flows, and callers. Integrity errors are especially important for health-check or repair code that needs distinguishable failure classes.

Risks: because exported variables are mutable package variables, external code could technically reassign them, though Go convention treats them as constants. Message text becomes part of operator-facing diagnostics, so changing text may affect tests or integrations that match strings.

Test signals: direct tests are not in this file; coverage is indirect through storage operations, delete paths, lookup failures, read-only stores, and consistency checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/types/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/types/idmappings.go -->
# sources/cloud-native/containers-storage/types/idmappings.go

Purpose: defines ID mapping option structs and parses CLI-style UID/GID mapping inputs into storage `IDMappingOptions`.

Important APIs and control flow: `AutoUserNsOptions` describes automatic namespace sizing, passwd/group overrides, and additional mappings. `IDMappingOptions` controls host mapping, explicit maps, and auto-userns configuration. `ParseIDMapping` normalizes missing UID/GID and subuid/subgid inputs, defaults non-root users to a one-ID mapping when no subid data is provided, loads subid mappings via `idtools.NewIDMappings`, parses explicit `UIDMapSlice` and `GIDMapSlice`, appends both sources, and flips `HostUIDMapping`/`HostGIDMapping` to false when maps exist.

State and persistence: no persisted state; uses current process UID/GID to infer defaults for non-root execution.

Dependencies and integration: depends on `github.com/containers/storage/pkg/idtools` for parsing and `/etc/subuid`/`/etc/subgid` mapping resolution. Called by the top-level `storage.ParseIDMapping` wrapper in `utils.go`.

Risks: error messages for GID parsing include the UID slice in one format path, which could confuse diagnostics. Implicit mirroring of UID to GID and vice versa is convenient but can surprise callers who intended asymmetry.

Test signals: behavior is usually validated by user namespace and ID mapping tests in storage packages; key cases include rootless fallback, subid lookup failure, parse errors, and host-mapping flags.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/types/idmappings.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/types/options.go -->
# sources/cloud-native/containers-storage/types/options.go

Purpose: main configuration loader and option model for `containers/storage`. It converts TOML storage config, environment overrides, rootless heuristics, and platform defaults into `StoreOptions`.

Important APIs and control flow: `TomlConfig` mirrors storage.conf tables. `StoreOptions` carries run/graph roots, image store, rootless path, graph driver and options, ID maps, auto-userns limits, pull options, volatile and transient settings. `loadDefaultStoreOptions` initializes package defaults once, honoring `CONTAINERS_STORAGE_CONF`, `XDG_CONFIG_HOME`, override config, and system config. `loadStoreOptionsFromConfFile` starts from defaults, applies rootless options when needed, reloads explicit config, expands `$UID` and environment variables, and rejects missing roots or `ImageStore == GraphRoot`. `DefaultStoreOptions` and `UpdateStoreOptions` expose cached or refreshed values. `ReloadConfigurationFile` decodes TOML, warns on undecoded keys, resets previous options, maps config fields to driver options, handles `STORAGE_DRIVER` and `STORAGE_OPTS`, and normalizes `overlay2` to `overlay`.

State and persistence: package-level `sync.Once` values cache default and current options. `prevReloadConfig` caches parsed config by file path and modtime. `Save` removes and recreates the default config file; `StorageConfig` reads it.

Dependencies and integration: uses BurntSushi TOML, storage config helpers, homedir/runtime helpers, rootless detection, file existence checks, idtools, and logrus. Integrates with all store initialization code.

Risks: global caches make tests and long-running process reconfiguration sensitive to call order. `Save` does not close the created file explicitly. Modtime-based cache can miss changes with coarse timestamps. Environment overrides can replace config-derived driver options wholesale.

Test signals: `options_test.go` verifies rootless driver selection, environment overrides, overlay2 normalization, and malformed config warnings; broader store tests exercise final options during store initialization.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/types/options.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/types/options_bsd.go -->
# sources/cloud-native/containers-storage/types/options_bsd.go

Purpose: FreeBSD/NetBSD platform defaults for storage configuration.

Important APIs and control flow: defines `defaultRunRoot` as `/var/run/containers/storage`, `defaultGraphRoot` as `/var/db/containers/storage`, `SystemConfigFile` as `/usr/local/share/containers/storage.conf`, and `defaultOverrideConfigFile` as `/usr/local/etc/containers/storage.conf`. `canUseRootlessOverlay` always returns false.

State and persistence: no runtime state beyond constants and package variable used by `options.go`.

Dependencies and integration: selected by `//go:build freebsd || netbsd`. Feeds `DefaultConfigFile`, `loadDefaultStoreOptions`, and rootless driver selection.

Risks: rootless users on BSD always fall back away from overlay unless an explicit driver is supplied, which may affect feature parity. Defaults must track OS packaging conventions.

Test signals: platform-specific compile and config tests would catch missing symbols; functional overlay behavior is intentionally disabled here.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/types/options_bsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/types/options_darwin.go -->
# sources/cloud-native/containers-storage/types/options_darwin.go

Purpose: Darwin storage path defaults and rootless overlay capability stub.

Important APIs and control flow: defines Linux-like default run and graph roots plus system and override config paths; `canUseRootlessOverlay` returns false.

State and persistence: no mutable state beyond `defaultOverrideConfigFile`.

Dependencies and integration: selected on Darwin builds and supplies symbols consumed by shared config-loading code.

Risks: paths may be less idiomatic for macOS than for Linux, but this package is generally used in container tooling where Linux compatibility paths are expected. Overlay is unavailable by default.

Test signals: compile coverage on Darwin validates symbol availability; behavior is mainly exercised through shared option tests where supported.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/types/options_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/types/options_linux.go -->
# sources/cloud-native/containers-storage/types/options_linux.go

Purpose: Linux storage defaults and rootless overlay capability heuristic.

Important APIs and control flow: defines rootful defaults `/run/containers/storage`, `/var/lib/containers/storage`, system config `/usr/share/containers/storage.conf`, and override `/etc/containers/storage.conf`. `canUseRootlessOverlay` first checks for `fuse-overlayfs`; if absent, it reads kernel release through `unix.Uname` and returns true for kernels >= 5.13 or any 6.x+ kernel.

State and persistence: no persistence. The function reads current executable lookup state and kernel version.

Dependencies and integration: used by rootless driver selection in `getRootlessStorageOpts`. Depends on `exec.LookPath`, `golang.org/x/sys/unix`, and simple version parsing.

Risks: kernel-version heuristics can be wrong for backports or vendor kernels; comments note this is only a heuristic and packaging may install explicit config. `strings.Split(string(uts.Release[:]), ".")` includes trailing NUL data but `Atoi` on the first numeric components usually works.

Test signals: `options_test.go` accepts either `overlay` or `vfs` when capability depends on host environment; direct deterministic tests would need fakes.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/types/options_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/types/options_test.go -->
# sources/cloud-native/containers-storage/types/options_test.go

Purpose: unit tests for rootless storage option derivation and config decode warning behavior.

Important APIs and control flow: `TestGetRootlessStorageOpts` preserves and clears `STORAGE_DRIVER`, then exercises unset, valid, overlay2, unsupported, and environment-specified drivers. It expects invalid system drivers to be replaced by overlay or vfs unless overridden by `STORAGE_DRIVER`. `TestGetRootlessStorageOpts2` verifies `$HOME` and `$UID` expansion in `RootlessStoragePath`. `TestReloadConfigurationFile` captures logrus output while loading `storage_broken.conf`, then asserts both a valid runroot and the undecoded-key warning.

State and persistence: uses temporary directories and environment mutation via `t.Setenv` or manual restore. It relies on package globals in `options.go`, so test ordering and environment cleanup matter.

Dependencies and integration: uses `gotest.tools/v3/assert`, `stretchr/testify/require`, logrus, and rootless UID helpers. Test fixtures are local TOML files.

Risks: rootless overlay capability makes expected driver host-dependent. Manual environment restoration in the first test predates `t.Setenv` and must remain correct if subtests become parallel.

Test signals: coverage confirms driver normalization, environment override precedence, path expansion, and malformed config warning emission.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/types/options_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/types/options_windows.go -->
# sources/cloud-native/containers-storage/types/options_windows.go

Purpose: Windows build defaults for the storage options package.

Important APIs and control flow: provides the same default path symbols as Linux and a `canUseRootlessOverlay` stub returning false.

State and persistence: no persistence; only constants and one package variable.

Dependencies and integration: selected by Windows builds to satisfy shared `options.go` references.

Risks: POSIX-style paths are unlikely to be usable as native Windows storage roots without higher-level adaptation. Overlay rootless support is disabled.

Test signals: Windows compile coverage validates symbol availability; functional tests would need platform-specific expectations.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/types/options_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/types/storage_broken.conf -->
# sources/cloud-native/containers-storage/types/storage_broken.conf

Purpose: malformed-but-partly-valid TOML fixture for `ReloadConfigurationFile` warning tests.

Important fields and flow: includes an unexpected top-level key `foo = "bar"` and an unexpected `storage.options.graphroot` key, while still providing `[storage]`, empty `driver`, and `runroot = "/run/containers/test"`.

State and persistence: fixture-only; it should not be used as a real config.

Dependencies and integration: loaded by `TestReloadConfigurationFile`, which expects parsing to succeed, the valid `runroot` to be applied, and undecoded keys to be logged.

Risks: if TOML schema changes to include the formerly unknown keys, the warning assertion must change. Relative path use relies on Go package test working directory.

Test signals: protects tolerant parsing behavior: unknown keys warn but do not reject otherwise usable config.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/types/storage_broken.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/types/storage_test.conf -->
# sources/cloud-native/containers-storage/types/storage_test.conf

Purpose: rootless path expansion fixture for storage option tests.

Important fields and flow: `[storage]` sets empty `driver`, `runroot`, `graphroot`, and `rootless_storage_path` to `$HOME/$UID/containers/storage`. `[storage.options]` has an empty `additionalimagestores` list, and `[storage.options.overlay]` sets `mountopt = "nodev"`.

State and persistence: fixture-only. It models a config where all root paths should expand through environment and rootless UID substitution.

Dependencies and integration: consumed by `TestDefaultStoreOpts` and shared config loading code. The overlay mount option is converted through option mapping in `ReloadConfigurationFile`.

Risks: tests using this fixture skip when not in per-user storage mode, so coverage is conditional on rootless test environment.

Test signals: successful tests prove `$HOME` and `$UID` expansion and rootless storage path fallback logic.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/types/storage_test.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/types/utils.go -->
# sources/cloud-native/containers-storage/types/utils.go

Purpose: utility functions for path expansion, default config file resolution, and best-effort cached config reload.

Important APIs and control flow: `expandEnvPath` replaces `$UID`, expands environment variables, resolves symlinks when possible, and otherwise returns a cleaned path. `DefaultConfigFile` respects explicit default path, `CONTAINERS_STORAGE_CONF`, rootful override file existence, rootless `XDG_CONFIG_HOME`, or `$HOME/.config/containers/storage.conf`. `reloadConfigurationFileIfNeeded` is a non-returning helper that checks modtime and config path under a mutex, reuses cached options when unchanged, and logs warnings instead of failing.

State and persistence: reads environment and filesystem metadata. Shares `prevReloadConfig` mutable cache with `options.go`.

Dependencies and integration: uses `fileutils.Exists`, homedir resolution, logrus, and package globals such as `defaultConfigFileSet` and `defaultOverrideConfigFile`. It is called during rootless/default option loading.

Risks: symlink resolution fallback silently accepts unresolved paths. The non-returning reload helper can hide config read failures from callers. Cache assignment stores the caller's pointer in one path, which can be surprising if mutated later.

Test signals: `utils_test.go` verifies env override resolution and rootless config path behavior; `options_test.go` indirectly covers path expansion.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/types/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/types/utils_test.go -->
# sources/cloud-native/containers-storage/types/utils_test.go

Purpose: tests for default storage option path expansion and config-file override selection.

Important APIs and control flow: `TestDefaultStoreOpts` skips outside per-user storage, loads `storage_test.conf`, computes `$HOME/<rootlessUID>/containers/storage`, and asserts `RunRoot`, `GraphRoot`, and `RootlessStoragePath`. The two override tests set `CONTAINERS_STORAGE_CONF` to `default_override_test.conf` and assert `DefaultConfigFile` returns it.

State and persistence: mutates environment through `t.Setenv`; no filesystem writes beyond test package behavior.

Dependencies and integration: uses rootless detection from `unshare`, path utilities, and `gotest.tools/v3/assert`.

Risks: rootless-only test coverage means CI that runs only rootful skips a significant path. The root/rootless names on the override tests are descriptive only; both rely on the same process context.

Test signals: protects precedence of `CONTAINERS_STORAGE_CONF` and correct expansion of `$HOME`/`$UID` in config-derived paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/types/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/userns.go -->
# sources/cloud-native/containers-storage/userns.go

Purpose: Linux implementation of automatic user namespace allocation and image-derived namespace sizing for the storage package.

Important APIs and control flow: `getAdditionalSubIDs` chooses a username from rootless environment/current UID or default root auto user, then loads subuid/subgid mappings. `store.getAvailableIDs` caches those mappings and remaps rootless availability to namespace-internal IDs. `parseMountedFiles` reads passwd/group files from a mounted image or explicit override paths and returns the maximum UID/GID plus one, ignoring nobody/nogroup. `store.getMaxSizeFromImage` walks image layers to inspect stored UID/GID metadata, creates and mounts a temporary layer, parses passwd/group, then unmounts and deletes the temp layer. `store.getAutoUserNS` chooses requested or heuristic size, enforces min/max, gathers currently used container maps, and delegates to `getAutoUserNSIDMappings`. That function subtracts used and additional IDs from available/container target sets, finds available ranges, zips them into ID maps, and appends additional mappings. `secureOpen` uses securejoin to avoid path traversal while opening files in a container mount.

State and persistence: caches additional UID/GID sets on `store`. Temporarily creates, mounts, unmounts, and deletes a layer while sizing images.

Dependencies and integration: integrates store container/layer metadata, `idtools`, rootless detection, securejoin, moby passwd/group parsers, storage drivers, and logrus.

Risks: temp layer cleanup and unmount are complex deferred paths; failures are wrapped or logged. Rootless mapping depends on `/etc/subuid`/`/etc/subgid` availability. Size heuristics can over- or under-estimate if metadata or mounted passwd/group files are incomplete.

Test signals: `userns_test.go` exercises ID allocation edge cases and passwd/group parsing; integration tests are needed for real mounts and layer-store cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/userns.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/userns_test.go -->
# sources/cloud-native/containers-storage/userns_test.go

Purpose: Linux unit tests for automatic user namespace ID mapping and passwd/group size inference.

Important APIs and control flow: `TestGetAutoUserNSMapping` table-tests `getAutoUserNSIDMappings` with normal contiguous ranges, insufficient UID/GID availability, used ranges, additional mappings, and discontinuous intervals. Expected maps verify that occupied host IDs and reserved container IDs are skipped while additional mappings are appended. `TestParseMountedFiles` writes temporary passwd and group files and checks `parseMountedFiles` output for normal users, passwd-only, group-only, empty files, invalid file contents, and nobody/nogroup handling.

State and persistence: uses temporary directories and files; no persistent storage. The tests avoid mounting and layer-store operations.

Dependencies and integration: uses `idtools.IDMap`, the package's `idSet` and `interval` helpers, and Go testing. Build tag limits it to Linux.

Risks: `reflect.DeepEqual` makes ordering part of the contract. The tests cover pure allocation logic but not `getAutoUserNS` end-to-end with store locks, image layers, or cleanup failures.

Test signals: strong signal for arithmetic correctness in range subtraction/zipping and for ignoring nobody/nogroup sentinel IDs when sizing user namespaces.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/userns_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/userns_unsupported.go -->
# sources/cloud-native/containers-storage/userns_unsupported.go

Purpose: non-Linux fallback for automatic user namespace support.

Important APIs and control flow: under `//go:build !linux`, defines `store.getAutoUserNS` with the same signature as Linux but always returns nil maps and an error saying user namespaces are unsupported.

State and persistence: no state or side effects.

Dependencies and integration: imports `idtools` and `types` only to satisfy the shared method signature. Ensures the storage package compiles on unsupported platforms while callers receive a clear runtime error.

Risks: the error is a new `errors.New` value rather than `types.ErrNotSupported`, so callers cannot use a shared sentinel unless they match strings or wrap at a higher layer.

Test signals: platform compile coverage and any non-Linux tests invoking auto-userns should verify graceful failure.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/userns_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/utils.go -->
# sources/cloud-native/containers-storage/utils.go

Purpose: top-level storage package utility wrappers and small validation/name-list helpers.

Important APIs and control flow: `ParseIDMapping` delegates to `types.ParseIDMapping`, preserving the public package API. `DefaultStoreOptions` delegates to `types.DefaultStoreOptions`. `validateMountOptions` rejects unsupported image mount options, currently `rw`. `applyNameOperation` implements `setNames`, `removeNames`, and `addNames`, then deduplicates results; unknown operations return `errInvalidUpdateNameOperation`.

State and persistence: no persistent state. Name operations return new slices and do not mutate the old list in place.

Dependencies and integration: bridges callers of the root `storage` package to the `types` package. `applyNameOperation` integrates with name update flows elsewhere in the package and depends on operation constants plus `dedupeStrings`.

Risks: `addNames` prepends new names before old names, so ordering is semantically significant. `validateMountOptions` matches exact strings only; option variants or comma-composed values must be normalized before calling.

Test signals: indirect tests should cover name update operations and mount option rejection; no direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.codecov.yml -->
# sources/cloud-native/cri-o/.codecov.yml

Purpose: Codecov policy for CRI-O coverage uploads and status reporting.

Important settings and flow: Codecov notifies after one build and does not require CI to pass before processing. Coverage is displayed with precision two, rounded down, in a 50..75 range. Project and patch status checks are enabled, but thresholds are `null`, and missing reports or no uploads are treated as success while CI failure is an error. Comments use a compact `header, diff` layout and do not require changes.

State and persistence: no repository runtime state; affects external Codecov status and PR comments.

Dependencies and integration: consumed by `codecov/codecov-action` in test and integration workflows that upload Go coverage profiles.

Risks: permissive thresholds mean coverage drops may not fail PRs. Treating missing uploads as success avoids flakes but can hide broken coverage generation.

Test signals: successful workflow uploads should produce Codecov project/patch statuses and PR comments according to this policy.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.codecov.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.coderabbit.yaml -->
# sources/cloud-native/cri-o/.coderabbit.yaml

Purpose: CodeRabbit review configuration.

Important settings and flow: declares the CodeRabbit schema and configures reviews to exclude `vendor/**` through `path_filters`.

State and persistence: no runtime state; controls external automated review behavior.

Dependencies and integration: read by CodeRabbit's GitHub integration when reviewing pull requests.

Risks: only vendor is excluded, so generated files outside vendor can still receive automated comments unless separately ignored.

Test signals: practical signal is CodeRabbit review behavior on PRs; no in-repo tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.coderabbit.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.github/ISSUE_TEMPLATE/bug-report.yml -->
# sources/cloud-native/cri-o/.github/ISSUE_TEMPLATE/bug-report.yml

Purpose: structured GitHub issue form for CRI-O bug reports.

Important fields and flow: applies `kind/bug`, asks for actual behavior, expected behavior, minimal reproduction, optional extra data, CRI-O and Kubernetes versions, OS version, and environment details. Required fields force reporters to include operational context and version data. The problem description points security issues to private advisories.

State and persistence: creates issue metadata and body content in GitHub; no code state.

Dependencies and integration: used by GitHub issue forms. The collected `crio --version`, `kubectl version`, `/etc/os-release`, and `uname -a` outputs support maintainer triage.

Risks: required long text areas can deter reports, but they reduce underspecified issues. Security guidance is advisory and depends on reporter compliance.

Test signals: opening a new issue in GitHub validates form rendering; no CI tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.github/ISSUE_TEMPLATE/bug-report.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.github/ISSUE_TEMPLATE/failing-test.yml -->
# sources/cloud-native/cri-o/.github/ISSUE_TEMPLATE/failing-test.yml

Purpose: structured issue form for continuously failing CRI-O CI tests or jobs.

Important fields and flow: applies `kind/failing-test`, requires failing job names, failing tests, and when failure started; optional fields capture Testgrid link, suspected reason, and additional context.

State and persistence: produces GitHub issue body content and labels.

Dependencies and integration: supports CI triage workflows and release health tracking by collecting consistent failure metadata.

Risks: the template relies on users distinguishing continuous failures from one-off flakes. It does not enforce links to logs or workflow runs.

Test signals: GitHub issue-form rendering is the validation mechanism.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.github/ISSUE_TEMPLATE/failing-test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.github/ISSUE_TEMPLATE/org_member.yml -->
# sources/cloud-native/cri-o/.github/ISSUE_TEMPLATE/org_member.yml

Purpose: GitHub issue form for requesting CRI-O organization membership.

Important fields and flow: title template asks for the user's handle. Required inputs include GitHub username, confirmation checkboxes for community guidelines, 2FA, sponsor eligibility, prior sponsor agreement, sponsor handle, and contribution list.

State and persistence: creates a governance issue; no code state.

Dependencies and integration: references Kubernetes community membership guidelines and repository OWNERS approver lists. Maintainers use the structured data for membership decisions.

Risks: the form cannot verify 2FA, sponsor validity, or contribution claims automatically. Broken external links could reduce usefulness.

Test signals: issue-form rendering and maintainer workflow use are the only signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.github/ISSUE_TEMPLATE/org_member.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.github/ISSUE_TEMPLATE/reviewer.yml -->
# sources/cloud-native/cri-o/.github/ISSUE_TEMPLATE/reviewer.yml

Purpose: GitHub issue form for requesting CRI-O reviewer status.

Important fields and flow: mirrors the organization member template with a reviewer-specific title and description. It requires username, community/2FA/sponsor confirmations, sponsor handle, and a contribution list emphasizing PRs reviewed/authored and issues responded to.

State and persistence: creates a governance issue in GitHub.

Dependencies and integration: uses Kubernetes community membership expectations and repository OWNERS sponsor lists.

Risks: manual verification is required; the template does not distinguish reviewer-specific criteria beyond the issue title and description.

Test signals: validated by GitHub rendering and maintainer processing, not CI.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.github/ISSUE_TEMPLATE/reviewer.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.github/dependabot.yml -->
# sources/cloud-native/cri-o/.github/dependabot.yml

Purpose: Dependabot configuration for Go modules and GitHub Actions updates.

Important settings and flow: version 2 config defines daily updates for root `gomod` and repository GitHub Actions. Both use `release-note-none` labels and an open PR limit of 10. Go updates group Kubernetes-related modules under `kubernetes` and all major/minor/patch Go module updates under `gomod`. Actions updates group all update types under `actions`.

State and persistence: creates and updates dependency PRs in GitHub; no runtime state.

Dependencies and integration: depends on Dependabot's GitHub service. PRs then flow through CI, release-note labeling, and review.

Risks: broad grouping can produce large PRs with mixed dependency changes. Daily cadence can create review pressure.

Test signals: Dependabot PR creation and passing CI validate the config.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/integration.yml -->
# sources/cloud-native/cri-o/.github/workflows/integration.yml

Purpose: GitHub Actions workflow for CRI-O integration and CRI conformance-style tests.

Important jobs and flow: triggered on manual dispatch, tags, main/release/update-nixpkgs branches, and PRs. `test-binaries` builds instrumented CRI-O and helper binaries for amd64 and arm64, uploads artifacts, and caches Go dependencies. The `integration` matrix downloads those artifacts, installs packages and runtime setup, optionally swaps runtimes, then runs `sudo -E test/test_runner.sh` with matrix-controlled runtime type, critest flag, userns flag, jobs, and timeout. It converts `GOCOVERDIR` coverage data to a text profile and uploads to Codecov.

State and persistence: artifacts hold built binaries; cache stores Go build/module data; coverage files are written under `build/coverage`.

Dependencies and integration: depends on GitHub Actions, setup-go, cosign installer, CRI-O scripts, conmon/crun/runc setup, Codecov, and privileged host capabilities.

Risks: integration tests run with sudo and host-level container runtime setup, so runner environment drift matters. Several runc lanes are disabled due to nested AppArmor issues, reducing coverage.

Test signals: matrix success, coverage conversion, and Codecov upload provide strong end-to-end signals for runtime behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/integration.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/nixpkgs.yml -->
# sources/cloud-native/cri-o/.github/workflows/nixpkgs.yml

Purpose: monthly automation to update Nix flake/package inputs for CRI-O.

Important jobs and flow: runs manually or on the first day of each month. On the canonical `cri-o/cri-o` main branch, it checks out code, installs Nix, runs `make nixpkgs`, detects a non-empty git diff, and opens a signed PR on branch `nixpkgs` with labels `kind/ci`, `release-note-none`, and `ok-to-test`.

State and persistence: modifies flake-related files when updates exist and creates a PR; otherwise no persistent change.

Dependencies and integration: uses Cachix Nix installer and peter-evans/create-pull-request. Relies on `Makefile` target `nixpkgs`.

Risks: scheduled dependency drift can break static builds. Permissions allow content and PR writes only in the guarded canonical repo.

Test signals: generated PR plus downstream `test` workflow static build lanes validate the update.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/nixpkgs.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/osff.yml -->
# sources/cloud-native/cri-o/.github/workflows/osff.yml

Purpose: OpenSSF Scorecard workflow named `ossf`.

Important jobs and flow: triggers on branch protection rule changes, weekly schedule, and pushes to main. It checks out code without persisted credentials, runs `ossf/scorecard-action` to produce SARIF, publishes public results, uploads the SARIF artifact with short retention, and uploads SARIF to GitHub code scanning.

State and persistence: persists Scorecard results externally in OpenSSF and GitHub code scanning; stores a temporary workflow artifact.

Dependencies and integration: depends on GitHub Actions, OpenSSF Scorecard, upload-artifact, and CodeQL SARIF upload.

Risks: this overlaps with `scorecards.yml`, potentially duplicating supply-chain checks. Pinned action versions reduce but do not eliminate action supply-chain risk.

Test signals: successful SARIF generation/upload and visible code scanning results.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/osff.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/patch-release.yml -->
# sources/cloud-native/cri-o/.github/workflows/patch-release.yml

Purpose: scheduled/manual patch release automation.

Important jobs and flow: runs monthly or manually. On canonical main, checks out full history, sets up Go from `go.mod`, and executes `make release` with `GITHUB_TOKEN`.

State and persistence: may create release branches, tags, PRs, or other artifacts through the `scripts/release` target; this YAML only supplies workflow permissions and environment.

Dependencies and integration: depends on setup-go, repository release scripts, and GitHub token permissions for content and PR writes.

Risks: high-impact automation guarded by repo/branch condition but still capable of modifying release state. Correctness depends on `make release`.

Test signals: workflow success and resulting release artifacts/PRs are the observable signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/patch-release.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/release-branch-forward.yml -->
# sources/cloud-native/cri-o/.github/workflows/release-branch-forward.yml

Purpose: daily automation to fast-forward or reconcile release branches.

Important jobs and flow: runs manually or daily. On canonical main, checks out full history, sets up Go, and runs `make release-branch-forward` with `GITHUB_TOKEN` and `DRY_RUN=false`.

State and persistence: writes to repository branches or triggers workflows depending on the script implementation. Workflow permissions include actions and contents write.

Dependencies and integration: delegates actual behavior to the Makefile target and `scripts/release-branch-forward`.

Risks: branch-moving automation can disrupt release maintenance if script logic is wrong. The canonical-repo guard limits fork impact.

Test signals: successful run and expected branch updates; failures should block automatic forwarding.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/release-branch-forward.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/scorecards.yml -->
# sources/cloud-native/cri-o/.github/workflows/scorecards.yml

Purpose: OpenSSF Scorecard supply-chain security workflow.

Important jobs and flow: triggers on branch protection changes, weekly schedule, and pushes to main. It uses read-all default permissions, grants security-events and id-token for the analysis job, checks out without persisted credentials, runs `ossf/scorecard-action`, writes `results.sarif`, publishes public results, uploads the SARIF artifact, and uploads to GitHub code scanning.

State and persistence: produces external OpenSSF results and GitHub code scanning entries; artifact retention is five days.

Dependencies and integration: same Scorecard ecosystem as `osff.yml`, but with a different workflow name and slightly newer SARIF upload action.

Risks: duplicate Scorecard workflows can waste CI time and create duplicate code scanning alerts. Publish settings expose public scorecard results for public repos.

Test signals: successful SARIF artifact and code scanning upload.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/scorecards.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/stale.yml -->
# sources/cloud-native/cri-o/.github/workflows/stale.yml

Purpose: scheduled issue and PR stale/rotten lifecycle automation.

Important jobs and flow: runs daily and invokes `actions/stale`. It labels inactive issues and PRs after 30 days with `lifecycle/stale`, closes after 90 days with `lifecycle/rotten`, removes stale labels when updated, processes up to 300 operations per run, and exempts issues labeled `kind/feature`.

State and persistence: mutates GitHub issue/PR labels and may close issues/PRs.

Dependencies and integration: depends on `actions/stale` and GitHub issues/pull-requests write permissions.

Risks: broad automation can close still-relevant reports if maintainers do not label or update them. Feature issues are exempt; other long-lived work needs manual attention.

Test signals: action logs and expected labels/comments/closures on inactive items.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/stale.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/tag-reconciler.yml -->
# sources/cloud-native/cri-o/.github/workflows/tag-reconciler.yml

Purpose: daily/manual release tag reconciliation workflow.

Important jobs and flow: on canonical main, checks out full history, sets up Go, and runs `make tag-reconciler` with `GITHUB_TOKEN`. Permissions allow actions and contents write.

State and persistence: may create, update, or reconcile tags according to `scripts/tag-reconciler`; this workflow supplies schedule and credentials.

Dependencies and integration: delegates to Makefile target and Go script. Uses full fetch depth for tag/history visibility.

Risks: tag mutation is release-critical; incorrect reconciliation can affect downstream package consumers. Guard limits execution to main in the canonical repository.

Test signals: successful workflow logs and expected tag state after reconciliation.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/tag-reconciler.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/test.yml -->
# sources/cloud-native/cri-o/.github/workflows/test.yml

Purpose: broad build, unit, release-artifact, static-build, dependency, and security test workflow for CRI-O.

Important jobs and flow: `build` compiles CRI-O, docs, config, and cross Linux binary, then uploads artifacts. `build-freebsd` validates FreeBSD cross compilation. Validation jobs regenerate docs, completions, and NRI Bats tests from build artifacts and require clean tree status. `build-static` uses Nix/Cachix for static binaries across amd64, arm64, ppc64le, and s390x; upload jobs push static builds and VEX files to GCS on main/release/tags. `unit` runs mock generation and Ginkgo unit tests as root/rootless on amd64 and root on arm64 with coverage upload. Release jobs generate notes and GitHub releases. `dependencies`, `codeql-build`, `security-checks`, and `vex-upload` cover dependency reports, CodeQL, govulncheck, gosec, and OpenVEX artifacts.

State and persistence: produces build/docs/config/static/release/dependency/VEX artifacts, cache entries, release records, and GCS uploads.

Dependencies and integration: central integration point for Makefile targets, Nix, GCS credentials, Codecov, CodeQL, Go, and release scripts.

Risks: high workflow breadth means failures can stem from external services, credentials, Nix cache, or generated-file drift. Several jobs have write permissions and should remain guarded by branch/tag conditions.

Test signals: this is the primary CI signal for build reproducibility, generated artifacts, unit coverage, release packaging, and vulnerability checks.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/verify.yml -->
# sources/cloud-native/cri-o/.github/workflows/verify.yml

Purpose: PR and branch verification workflow for linting, formatting, documentation, dependency, typo, and generated-file checks.

Important jobs and flow: triggered on manual, tags, main/release/update-nixpkgs branches, and PRs. Jobs run golangci-lint, markdownlint, shellcheck, shfmt, trailing-space grep, docs validation, vendor verification, log capitalization, config-template validation, dependency verification, typos, mdtoc, and prettier dry-run. Concurrency cancels older runs per ref.

State and persistence: mostly read-only; some jobs generate files locally and then use tree-status checks to require committed output.

Dependencies and integration: uses Makefile verify targets, setup-go, markdownlint action, shellcheck problem matchers, typos, and prettier action.

Risks: many style gates can fail due to tool version drift, although versions are mostly pinned in Makefile or action references. Markdown lint excludes README, vendor, docs, and `.github`.

Test signals: clean workflow indicates source formatting, generated docs/config, vendor state, dependency policy, and spelling are acceptable.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.github/workflows/verify.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.gitpod.yml -->
# sources/cloud-native/cri-o/.gitpod.yml

Purpose: Gitpod workspace configuration for CRI-O development.

Important settings and flow: uses `.gitpod.Dockerfile` as workspace image and runs `make` during the init task.

State and persistence: initializes a Gitpod workspace with built artifacts generated by the default Makefile target.

Dependencies and integration: depends on Gitpod, the Dockerfile, and all dependencies required by `make`.

Risks: `make` can be heavy for workspace startup and may fail if the Gitpod image lacks host capabilities or packages needed by default targets.

Test signals: successful Gitpod startup and `make` completion.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.gitpod.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.golangci.yml -->
# sources/cloud-native/cri-o/.golangci.yml

Purpose: golangci-lint v2 configuration for CRI-O.

Important settings and flow: sets build tags for apparmor, ostree stub, openpgp, selinux, test, and btrfs exclusion, with concurrency 6. Default linters are disabled and a large curated set is enabled, including errcheck, errorlint, gocritic, govet, staticcheck, testifylint, unused, and many style/performance linters. Settings tighten errcheck, goconst, gocyclo, naked returns, revive argument limits, and whitespace layout. Formatters include gci, gofumpt, and goimports with localmodule ordering. Generated-code exclusions are strict.

State and persistence: no runtime state; affects lint output and possible local `make lint --fix` edits.

Dependencies and integration: used by `verify.yml` via golangci-lint action and by Makefile `lint`.

Risks: broad lint set can create noisy upgrades when golangci-lint changes. Several strict linters are intentionally disabled, documenting current project tolerance.

Test signals: lint workflow passing means code compiles under configured tags and satisfies the enabled static-analysis policy.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.markdownlint.yaml -->
# sources/cloud-native/cri-o/.markdownlint.yaml

Purpose: markdownlint configuration.

Important settings and flow: configures rule `MD013` line length to 80 while disabling table line-length enforcement.

State and persistence: no state; controls markdown lint results.

Dependencies and integration: used by `verify.yml` markdownlint job.

Risks: only one rule is customized, so default markdownlint behavior applies elsewhere. Tables can exceed 80 characters without failing.

Test signals: markdownlint job passing.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.markdownlint.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.muse/config.toml -->
# sources/cloud-native/cri-o/.muse/config.toml

Purpose: Muse static-analysis configuration.

Important settings and flow: sets `build = "make"`, ignores the `RESOURCE_LEAK` rule, and excludes `vendor/**` plus `internal/log/log_test.go`.

State and persistence: no state; controls external Muse analysis behavior.

Dependencies and integration: consumed by Muse tooling when run against the repository.

Risks: ignoring resource leaks and a specific log test can hide real issues in those scopes, though likely chosen to suppress false positives.

Test signals: Muse scan results under this configuration.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.muse/config.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.packit.yaml -->
# sources/cloud-native/cri-o/.packit.yaml

Purpose: Packit configuration for Fedora/CentOS downstream packaging automation.

Important settings and flow: maps upstream package `cri-o` and tags `v{version}` to downstream RPM package `cri-o`. Defines Rawhide and Fedora 40 package configs, syncing `.packit.yaml` and RPM spec files, cloning Fedora dist-git specs, removing downstream sources/patches, and updating `%global commit0`. Jobs include COPR builds for PRs across CentOS Stream and Fedora targets, downstream proposals on release for Rawhide and f40, Koji builds on commit for allowed automation authors, and Bodhi updates for branched Fedora.

State and persistence: creates downstream PRs/builds/updates and temporary `.packit_rpm` content during Packit runs.

Dependencies and integration: depends on Packit service, Fedora dist-git, RPM spec conventions, and `internal/version/version.go` for current version extraction.

Risks: shell actions manipulate spec files with sed and assume spec structure. Allowed automation authors can trigger downstream builds.

Test signals: Packit COPR/Koji/Bodhi job results and downstream PRs.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.packit.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/.typos.toml -->
# sources/cloud-native/cri-o/.typos.toml

Purpose: typo-checking policy for the `typos` tool.

Important settings and flow: excludes Go module files and vendor, ignores hidden/VCS/global/parent config files, enables filename and file checks, unicode checking, hex ignores, and English locale. It allows specific identifiers/regexes such as `writeable`, `facter`, `cpy`, `ClosID`, `CONTAINER_INCLUDED_POD_METRCIS`, and a long token. Shell files additionally ignore `rpmbuild -ba`.

State and persistence: no runtime state; controls typo scan results.

Dependencies and integration: used by `verify.yml` through `crate-ci/typos`.

Risks: allowlisted misspellings can persist intentionally for compatibility, especially the environment variable typo. Exclusions mean vendored and module checksum text is not checked.

Test signals: `typos` workflow passing.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/.typos.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/Makefile -->
# sources/cloud-native/cri-o/Makefile

Purpose: central build, install, verification, documentation, mock generation, release, and CI command contract for CRI-O.

Important APIs and control flow: defines Go commands, build tags, install prefixes, build output directories, tool versions, linker metadata, and helper macros. Build targets create `bin/crio`, `bin/pinns`, test binaries, static Nix builds, cross binaries, metrics exporter, generated `crio.conf`, manpages, completions, and docs. Install targets lay binaries, manpages, completions, systemd units, CRI-O config, oci-umount config, and crictl config into prefix paths. Verify targets run golangci-lint, shellcheck, shfmt, NRI Bats, vendor checks, Ginkgo unit tests with coverage, local integration tests, dependency validation, gosec, govulncheck/VEX, mdtoc, prettier, docs validation, log capitalization, and config-template validation. Utility targets update vendoring, Nix flake, mocks, release notes, dependencies, releases, tag reconciliation, artifact uploads, and OCI artifacts.

State and persistence: writes under `bin/`, `build/`, generated docs, `crio.conf`, vendored modules, mocks, and install destinations. `clean` removes generated local artifacts.

Dependencies and integration: integrates Go, Nix, container runtime, system tools, scripts under `hack/` and `scripts/`, Ginkgo, mockgen, go-md2man, security tools, and CI workflows.

Risks: many targets download tools at execution time. Generated-file targets depend on clean-tree checks in CI. Privileged/static build targets can modify `/nix` or require container privileges.

Test signals: most GitHub workflows delegate to this file, making target success the core build and verification signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/cmd/crio/daemon_linux.go -->
# sources/cloud-native/cri-o/cmd/crio/daemon_linux.go

Purpose: Linux systemd readiness notification for the CRI-O daemon.

Important APIs and control flow: `sdNotify` calls `watchdog.DefaultSystemd().Notify(daemon.SdNotifyReady)` and logs a warning on failure. `notifySystem` starts `sdNotify` in a goroutine after the daemon is ready to accept requests.

State and persistence: no persistent state. It sends a readiness message to systemd through the notification socket.

Dependencies and integration: depends on `coreos/go-systemd/daemon`, CRI-O internal watchdog abstraction, and logrus. Called from `main.go` after CRI services are registered and before serving loops fully settle.

Risks: asynchronous notification means failures are only logged and startup continues. Non-systemd environments will warn through the watchdog abstraction.

Test signals: integration/systemd tests or service manager behavior can confirm readiness notification; no direct test in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/cmd/crio/daemon_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/cmd/crio/daemon_unsupported.go -->
# sources/cloud-native/cri-o/cmd/crio/daemon_unsupported.go

Purpose: non-Linux no-op implementation of CRI-O daemon readiness notification.

Important APIs and control flow: `notifySystem` has the same signature as Linux and does nothing.

State and persistence: no state or side effects.

Dependencies and integration: selected by `//go:build !linux` to let `main.go` compile on unsupported platforms without systemd dependencies.

Risks: non-Linux builds receive no external readiness signal. This is expected for portability.

Test signals: cross-compilation jobs, such as FreeBSD build validation, catch missing symbol regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/cmd/crio/daemon_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/cmd/crio/main.go -->
# sources/cloud-native/cri-o/cmd/crio/main.go

Purpose: CRI-O daemon entrypoint. It defines CLI setup, logging, profiling, config validation, server construction, CRI registration, readiness notification, signal handling, and graceful shutdown.

Important APIs and control flow: `writeCrioGoroutineStacks` writes a timestamped stack dump to temp. `catchShutdown` subscribes to SIGINT, SIGTERM, SIGHUP, SIGUSR1, SIGUSR2, and SIGPIPE; SIGUSR1 dumps stacks, SIGUSR2 forces GC, SIGPIPE is ignored, and termination gracefully shuts down tracing, gRPC, HTTP, streaming server, monitors, and main server. `main` initializes klog shim and reexec, builds a urfave/cli app from `criocli`, sorts flags/commands, merges config in `Before`, sets log formatting/hooks/filter/output, and in `Action` handles CPU/HTTP profiling, rejects extra args, checks mount namespace status, validates config, logs flags/config, listens on the Unix socket, optionally initializes OpenTelemetry, creates the gRPC server with interceptors and message-size limits, creates `server.New`, writes temporary and persistent version files, manages clean-shutdown marker files, sets default runtime metrics, garbage-collects storage, registers CRI runtime/image services, notifies systemd, starts exit monitors and hook monitors, splits one listener into gRPC and HTTP via cmux, waits for server/monitor closure, shuts down, and optionally writes a heap profile.

State and persistence: writes log files, profile files, version files, clean-shutdown support files, Unix socket permissions, and storage GC side effects.

Dependencies and integration: integrates CLI/config packages, server package, Kubernetes CRI API, gRPC, cmux, OpenTelemetry, logrus hooks, system signals, kubensmnt, storage, metrics, and systemd notification.

Risks: multiple goroutines coordinate shutdown; missed channel closure can hang. `logrus.Fatal` exits immediately on several startup failures. Socket chmod assumes filesystem permissions are applicable. Clean-shutdown marker logic must remain compatible with `crio wipe`.

Test signals: unit tests likely cover subpackages; end-to-end CI validates daemon startup, CRI service behavior, signal/shutdown paths, generated docs/completions, and profile/status commands.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/cmd/crio/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/completions/fish/crio.fish -->
# sources/cloud-native/cri-o/completions/fish/crio.fish

Purpose: generated fish shell completions for the `crio` CLI.

Important APIs and control flow: defines `__fish_crio_no_subcommand`, which scans command-line tokens and returns false when known subcommands or aliases have already appeared. The bulk of the file registers `complete` entries for global flags, command aliases, and subcommand-specific options. It covers daemon configuration flags, storage/runtime/network/security/metrics/tracing/profile options, generated documentation commands, status subcommands, version JSON/verbose flags, wipe/check repair flags, and help aliases.

State and persistence: no runtime persistence. It is installed into fish completion directories by `make install.completions` and regenerated by `make completions-generation`.

Dependencies and integration: consumed by fish shell. Generated from CRI-O's CLI metadata, so it must stay aligned with `cmd/crio/main.go` and `criocli` command definitions.

Risks: generated file drift is easy when flags change; `validate-completions` regenerates and runs `hack/tree_status.sh` to catch this. Duplicated help/version completions appear in the generated output and may be harmless but noisy.

Test signals: CI `validate-completions` is the main signal; user-level signal is fish offering expected completions for CRI-O flags and subcommands.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/completions/fish/crio.fish -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/custom-node-e2e/create-ignition-config.sh -->
# sources/cloud-native/cri-o/contrib/custom-node-e2e/create-ignition-config.sh

Purpose: build CRI-O from source, upload bundle artifacts, and generate a Fedora CoreOS ignition file for Kubernetes node e2e testing with custom CRI-O.

Important APIs and control flow: parses required `-d CRIO_DIR`, `-i IGNITION_OUT_DIR`, `-b GCS_BUCKET_NAME`, optional service account and extra config paths. It cleans the repo, builds `pinns`, runs static build, detects local architecture as amd64 or arm64, copies static binaries into an arch-specific directory, builds docs and config, runs `make bundle`, uploads artifacts through `upload-artifacts.sh`, verifies bundle SHA against the latest branch marker, embeds extra config files into numbered `/etc/crio/crio.conf.d/*.conf` snippets, creates a randomized node-e2e installer script that downloads CRI-O from GCS, adjusts SELinux labels, removes podman CNI config, sets debug logging, writes runtime/infra config snippets, starts `crio.service`, uploads that installer to GCS, and writes an ignition JSON that disables Zincati updates and installs dbus-tools plus the CRI-O installer service.

State and persistence: modifies build outputs, `bin/static-$ARCH`, bundle artifacts, latest marker files, GCS bucket contents, temp installer script, and the output `.ign` file.

Dependencies and integration: requires sudo, make, Nix static build, GCS/gsutil, gcloud optional auth, git, md5sum, curl, systemd, rpm-ostree, SELinux tools, and CRI-O bundle scripts.

Risks: the script writes shell and JSON through heredocs with embedded config content; unusual config contents could break generated scripts. It assumes branch marker naming, architecture mapping, and Fedora CoreOS paths.

Test signals: successful bundle upload, SHA marker match, installer upload, and generated ignition file; real validation comes from node e2e boot/install runs.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/custom-node-e2e/create-ignition-config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/custom-node-e2e/upload-artifacts.sh -->
# sources/cloud-native/cri-o/contrib/custom-node-e2e/upload-artifacts.sh

Purpose: upload CRI-O bundle artifacts and branch/tag marker files to a Google Cloud Storage bucket for custom node e2e testing.

Important APIs and control flow: reads optional `GCS_SA_PATH` and `GCS_BUCKET_NAME` with default bucket `cri-o`. If a service account path is set, activates it with `gcloud`. It uploads `build/bundle/*.tar.gz*` to `$BUCKET/artifacts` with `gsutil -m cp -n`, computes marker from current branch or tag, writes the current commit or exact tag into `latest-$MARKER.txt`, and uploads that marker.

State and persistence: writes local latest marker file and remote GCS artifacts/marker objects.

Dependencies and integration: used by `create-ignition-config.sh`; depends on git, gsutil, optional gcloud, and bundle files created by `make bundle`.

Risks: detached HEAD assumes an exact tag and derives marker from characters 2-5 of the tag, which is version-format dependent. `cp -n` avoids overwriting bundles, so stale artifacts can persist.

Test signals: GCS upload success and marker contents matching expected commit or tag.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/custom-node-e2e/upload-artifacts.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/kube-local/examples/script -->
# sources/cloud-native/cri-o/contrib/kube-local/examples/script

Purpose: simple diagnostic helper for kube-local examples.

Important APIs and control flow: defines `execute_cmd`, which evaluates a command passed as a string, captures its output, and prints it between banner lines. It runs `kubectl get cs` and `kubectl get pods -A`.

State and persistence: no persistence; read-only Kubernetes API queries.

Dependencies and integration: depends on Bash and `kubectl` configured for a cluster. Intended for local Kubernetes/CRI-O example troubleshooting.

Risks: `cmd=$(${1})` executes the string argument through command substitution and is safe only for trusted hardcoded commands. `kubectl get cs` uses the deprecated componentstatuses API on newer Kubernetes versions.

Test signals: command output showing cluster component status and all pods; failures indicate kubeconfig or cluster health issues.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/contrib/kube-local/examples/script -->
