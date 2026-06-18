# subset-b-009127 research

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/pull.go -->
# sources/sync-backup/git-lfs/commands/pull.go

## Research

This file implements the checkout side used after LFS objects are fetched. `newSingleCheckout` inspects `filter.lfs.clean`, moves to the working tree root when possible, and returns either `singleCheckout` or `noOpCheckout` for bare/disabled-filter cases. The public surface in this package is the `abstractCheckout` contract: `Manifest`, `Skip`, `Run`, `RunToPath`, and `Close`.

`singleCheckout.Run` validates that the worktree path is safe to write, decodes any existing pointer, avoids overwriting non-pointer content or a pointer for a different OID, creates missing directories, smudges content through `lfs.GitFilter.SmudgeToFile`, then stages the path through `gitIndexer`. State is local process state: a lazily-created transfer manifest and a long-lived `git update-index --stdin` subprocess guarded by a mutex. Dependencies include `config.Environment`, `git`, `lfs`, `tools.DirWalker`, `tq.Manifest`, and command-level error reporting. Risks are race-prone worktree mutations, preserving user edits, deleted-index paths, and correct cleanup of the update-index process. There is no direct test file here; behavior is indirectly signaled by checkout/fetch integration and by `gitIndexer` subprocess failure handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/pull.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/run.go -->
# sources/sync-backup/git-lfs/commands/run.go

## Research

`run.go` builds and executes the root `git-lfs` Cobra command. `NewCommand` attaches a default HTTP logging `PreRun`; `RegisterCommand` stores command factory callbacks under a mutex; `Run` initializes translation, root/help/completion commands, canonicalizes environment, creates global `cfg`, attaches all registered commands, and returns `0` or `127`.

The control flow is mostly command assembly. Shell completion generation has custom bash and zsh rewrites so completion works when invoked as `git lfs`. Help and usage are backed by generated `ManPages` content. `setupHTTPLogger` creates `cfg.LocalLogDir()/http/http-<unix>.log` when `GIT_LOG_STATS` is set and wires the API client to record HTTP stats. State is global package state: command registrations, `rootVersion`, and `cfg`. Integration points include every command package `init`, Cobra, generated man content, translation, filesystem config, and the API client. Risks include global initialization order, concurrent registration, completion string patch drift after Cobra changes, and log creation before repository config is usable. Test signals are mainly CLI/integration tests for help, completion, version, and HTTP stat logging.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/run.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/uploader.go -->
# sources/sync-backup/git-lfs/commands/uploader.go

## Research

`uploader.go` coordinates push-time LFS uploads. `uploadForRefUpdates` verifies locks, computes remote SHAs to exclude, creates a transfer queue per ref update, scans either all reachable objects or multi-range differences, collects transfer errors, and reports deferred errors. `uploadContext` owns remote selection, transfer manifest, dry-run behavior, uploaded-OID deduplication, progress logger/meter, lock verifier, committer identity, and maps for missing/corrupt objects.

Key APIs are `newUploadContext`, `NewQueue`, `buildGitScanner`, `gitScannerCallback`, `prepareUpload`, `UploadPointers`, `CollectErrors`, `ReportErrors`, `uploadTransfer`, `supportsLockingAPI`, and `disableFor`. Control flow moves from GitScanner callbacks to `prepareUpload`, then to `tq.TransferQueue.Add`; missing local media files are either marked as malformed or allowed by `lfs.allowincompletepush`. Persistent effects are local object reads, stdout progress, process-exit decisions, and `cfg.SetGitLocalKey` when disabling lock verification. Dependencies include `git`, `lfs`, `tq`, `tasklog`, lock verification, config, and `tracerx`. Risks include duplicate scanner results, lock-verification policy differences, dry-run deduplication, exit-code behavior, missing/corrupt upload handling, and hard-coded known locking hosts. `uploader_test.go` covers locking host URL matching.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/uploader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/uploader_test.go -->
# sources/sync-backup/git-lfs/commands/uploader_test.go

## Research

This test file validates the small but security-relevant `supportsLockingAPI` helper from `uploader.go`. `LockingSupportTestCase` wraps a URL and expected result, and `TestSupportedLockingHosts` exercises HTTPS and SSH GitHub URLs with root paths, `/info/lfs` suffixes, and SSH usernames.

The test signal is that only `https://github.com/...` and `ssh://github.com/...` match the known locking support list; `http://github.com/...` is rejected. It indirectly confirms that `url.URL.Hostname()` ignores usernames and that path-prefix matching accepts both repository root URLs and batch API URLs. The file has no persistence or external I/O. Risks left uncovered include malformed URLs, ports, enterprise GitHub hostnames, host case normalization, trailing slash behavior, and lock-verification config writes in `disableFor`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/commands/uploader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/config.go -->
# sources/sync-backup/git-lfs/config/config.go

## Research

`config.go` is the main Git LFS configuration façade. `Configuration` combines OS environment, delayed Git config, Git command wrapper, repository/worktree discovery, remotes, extensions, filesystem paths, permission masks, and cached author/committer data. Constructors `New`, `NewIn`, and `NewFrom` support real repositories and tests.

Important APIs include transfer/fetch flags, `Remote`, `PushRemote`, remote setters/validators, `Remotes`, `Extensions`, `SortedExtensions`, `HookDir`, `LocalWorkingDir`, `LocalGitDir`, `Filesystem`, git config find/set/unset wrappers, identity/timestamp helpers, and `RepositoryPermissions`. Control flow is lazy and mutex-protected: Git config and git/work dirs load on demand; `.lfsconfig` is read through `git.Configuration.Sources`; remotes/extensions are parsed by `readGitConfig`; filesystem directories are constructed only when requested. Persistent effects include reading Git config/environment, creating LFS/log/tmp directories through `fs.New`, and writing Git config through wrapper methods. Risks include deadlocks around `PushRemote` temporarily unlocking to call `Remote`, cached stale config, nil `c.fs` in `Cleanup`, Git date parsing compatibility, unsafe `.lfsconfig` filtering, and platform-specific umask behavior. `config_test.go` covers remote precedence, transfer booleans, extension loading, fetch path cleanup, permissions, identity, timestamps, and dotted remote names.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/config_test.go -->
# sources/sync-backup/git-lfs/config/config_test.go

## Research

This file exercises the main `Configuration` behavior using `NewFrom` maps rather than real Git config files. It covers default remote fallback, branch remote precedence, push-remote precedence, `remote.lfsdefault` and `remote.lfspushdefault`, basic/tus transfer booleans including invalid values, extension parsing, fetch include/exclude cleanup, repository permissions from `core.sharedrepository`, committer/author identity precedence, timestamp parsing, and remote names containing dots.

The tests are pure unit tests with no persistent state beyond process maps and the captured `timestamp` field. They provide strong signals for precedence and conversion rules but do not cover real Git command failures, delayed config source loading, filesystem initialization, hook path expansion, config writes, concurrency, or `.lfsconfig` unsafe key warnings. They also intentionally rely on current process `umask()` for expected permission defaults.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/delayed_environment.go -->
# sources/sync-backup/git-lfs/config/delayed_environment.go

## Research

`delayed_environment.go` implements `delayedEnvironment`, an `Environment` wrapper that defers expensive Git config parsing until the first read. Its `Load` method is mutex-protected and idempotent; `Get`, `GetAll`, `Bool`, `Int`, `Int64`, and `All` all call `Load` before delegating to the realized environment.

The only state is the cached `env`, a mutex, and a callback supplied by `Configuration.NewIn` or `NewFrom`. This is the bridge between old code that expected `Configuration.loadGitConfig()` side effects and newer code that consumes an `Environment`. Dependencies are only `sync` and the local `Environment` interface. Risks include callback panics, callback returning nil, recursive load paths if the callback reads the same delayed environment, and stale cached config after repository config changes. It is tested indirectly by all configuration tests that use `cfg.Git`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/delayed_environment.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/environment.go -->
# sources/sync-backup/git-lfs/config/environment.go

## Research

`environment.go` defines the typed configuration access layer. `Environment` wraps a `Fetcher` and adds `Bool`, `Int`, `Int64`, and `All`; `EnvironmentOf` adapts any fetcher. Standalone conversion helpers parse booleans and integers, returning supplied defaults for blank or malformed numeric values.

Control flow is direct delegation: `Get`/`GetAll` forward to the fetcher, while typed methods fetch the raw string then call conversion helpers. State lives entirely in the underlying fetcher. Dependencies are `strconv` and `strings`. Integration points include OS, Git, map, delayed, URL, credential, filepath-filter, and filesystem configuration consumers. Risks are semantic compatibility: unknown boolean strings return `false` rather than the default, `Get` returns the fetcher’s last value convention, and `All` must be a defensive copy when the fetcher has mutable state. `environment_test.go` covers delegation, boolean truthy/falsy values, default handling, and integer parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/environment.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/environment_test.go -->
# sources/sync-backup/git-lfs/config/environment_test.go

## Research

This unit test file validates the `Environment` wrapper and conversion helpers. It confirms that `Get` returns the last value from a multi-value `MapFetcher`, `GetAll` preserves the value slice, unset booleans use their default, recognized truthy/falsy strings map correctly, and integer parsing returns defaults for blank or malformed values.

There is no persistence or external dependency. The tests are important because the same conversion rules drive LFS behavior flags such as transfer selection, prompts, cache credentials, and repository permissions. Remaining gaps include `Int64`, `All`, delayed environments, OS fetch caching, case sensitivity, and the intentionally surprising behavior where unknown boolean strings return `false` instead of the caller default.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/environment_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/extension.go -->
# sources/sync-backup/git-lfs/config/extension.go

## Research

`extension.go` models configured Git LFS clean/smudge extensions. `Extension` stores `Name`, `Clean`, `Smudge`, and integer `Priority`. `SortExtensions` converts a map of extensions into an ascending-priority slice and rejects duplicate priorities.

There is no persistent state; the function builds local maps/slices and returns an error translated through `tr` for collisions. Integration is through `Configuration.SortedExtensions()` after `readGitConfig` parses `lfs.extension.<name>.*` keys. The main risk is that the temporary `map[int]Extension` makes priority unique by design, so two extensions cannot share a priority; this is tested and may be stricter than some users expect. Test coverage in `extension_test.go` checks deterministic ordering and duplicate-priority rejection.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/extension.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/extension_test.go -->
# sources/sync-backup/git-lfs/config/extension_test.go

## Research

This file tests `SortExtensions`. `TestSortExtensions` builds three extension entries out of map order and expects output sorted by priorities `0`, `1`, and `2` with names and command strings intact. `TestSortExtensionsDuplicatePriority` verifies that duplicate priority values return an error and no sorted result.

The tests are pure and cover the main contract. They do not cover nil maps, negative priorities from parser behavior, or how `Configuration.readGitConfig` ignores unsafe extension command keys from `.lfsconfig`. Their value is preventing nondeterministic extension ordering in clean/smudge pipelines.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/extension_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/fetcher.go -->
# sources/sync-backup/git-lfs/config/fetcher.go

## Research

`fetcher.go` defines the minimal `Fetcher` interface used by configuration environments. It requires `Get`, `GetAll`, and `All`, allowing OS variables, Git config, delayed sources, and maps to be consumed uniformly.

The interface’s semantics matter: `Get` returns one string and presence, `GetAll` returns all values or an empty slice, and `All` must return a copy of key/value pairs for sources where mutation matters. There is no control flow or state in the file. Integration points are `EnvironmentOf`, `GitFetcher`, `mapFetcher`, `OsFetcher`, `URLConfig`, and tests. Risks are implementation-specific differences: `OsFetcher.All` returns nil, `MapFetcher.GetAll` can return nil, and `GitFetcher` canonicalizes keys before lookup.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/fetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/git_fetcher.go -->
# sources/sync-backup/git-lfs/config/git_fetcher.go

## Research

`git_fetcher.go` parses Git config output into a thread-safe fetcher and extracts LFS extensions and remotes. `readGitConfig` consumes `git.ConfigurationSource` values, splits `key=value` lines, applies `.lfsconfig` safe-key policy, records ignored unsafe keys, parses `lfs.extension.<name>.<prop>`, and collects remote names including names with dots.

`GitFetcher.Get` returns the last value; `GetAll` uses Git-compatible case folding where the middle part of three-or-more-part keys remains case-sensitive; `All` returns a copy. Persistent behavior is limited to warning output on stderr for clashes or ignored unsafe keys. Dependencies include `git.ConfigurationSource`, translation, and synchronization. Integration is central to `Configuration.Git`, URL matching, credential config, remotes, and extension sorting. Risks include line parsing by first `=`, safe-key drift, ignored-key warnings leaking to stderr, remote names with complex dots, and correctness of Git key canonicalization. `git_fetcher_test.go` targets mixed-case branch and URL keys.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/git_fetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/git_fetcher_test.go -->
# sources/sync-backup/git-lfs/config/git_fetcher_test.go

## Research

This unit test verifies `GitFetcher.caseFoldKey` through public `GetAll` calls. It asserts that ordinary two-part keys are case-insensitive, while the middle component of branch and URL-scoped keys remains case-sensitive and the final key segment is case-insensitive.

The test is pure and has no persistence. It is an important regression signal because URL-scoped config such as `http.https://example.com/BIG-TEXT.git.extraheader` and branch names can be case-sensitive. Gaps include `.lfsconfig` safe-key filtering, extension parsing, duplicate warnings, remotes with dots, and `All` copy behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/git_fetcher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/map_fetcher.go -->
# sources/sync-backup/git-lfs/config/map_fetcher.go

## Research

`map_fetcher.go` provides test/in-memory `Fetcher` implementations. `MapFetcher` wraps `map[string][]string`; `UniqMapFetcher` adapts `map[string]string` into a single-value map. `Get` returns the last entry for a key, `GetAll` returns the stored slice, and `All` deep-copies the slice values into a new map.

There is no synchronization, so this fetcher is intended for immutable test/config data. It integrates with `NewFrom`, environment tests, URL config tests, and any caller needing synthetic configuration. Risks are nil maps returning nil slices, callers mutating `GetAll` slices because they are not copied, and case-sensitive lookups unlike `GitFetcher`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/map_fetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/os_fetcher.go -->
# sources/sync-backup/git-lfs/config/os_fetcher.go

## Research

`os_fetcher.go` implements `OsFetcher`, a mutex-protected cached wrapper around `os.LookupEnv`. `Get` caches both present values and misses using `map[string]*string`; `GetAll` returns either a one-element slice or an empty slice; `All` returns nil because the OS environment is not enumerated here.

State persists for the lifetime of the fetcher, so environment changes after first lookup are intentionally not observed. Integration points include `Configuration.Os`, credential askpass and prompt behavior, filesystem alternates, and all environment-based flags. Risks include stale values in long-running processes, nil `All` surprising generic callers, pointer-to-local-string escape semantics being safe but subtle, and no cache invalidation for tests that modify environment variables.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/os_fetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/url_config.go -->
# sources/sync-backup/git-lfs/config/url_config.go

## Research

`url_config.go` implements Git’s URL-scoped config matching for keys such as `http.<url>.<key>` and `credential.<url>.<key>`. `URLConfig.Get`, `GetAll`, and `Bool` search URL-specific keys first and fall back to `<prefix>.<key>`. `getAll` parses all config keys, compares scheme, host/wildcard host, port, path prefix, and optional username, then chooses the highest-scoring match.

Supporting helpers include `portForURL`, `compareHosts`, `comparePaths`, `hostsAndPaths`, `hosts`, `paths`, and `isDefaultLFSUrl`, which treats `/repo.git/info/lfs` as matching `/repo`. State is just the wrapped Git environment. Integration is used by credentials and HTTP/LFS API configuration. Risks include regex matching over raw config keys, URL parse failures silently producing fallback behavior, wildcard host scoring, path score precedence over username only after host, and special `.git/info/lfs` matching edge cases. `url_config_test.go` covers roots, users, ports, HTTP vs HTTPS, SSH ports, wildcards, and `.git` default LFS URLs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/url_config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/url_config_test.go -->
# sources/sync-backup/git-lfs/config/url_config_test.go

## Research

This test file verifies URL-scoped config selection. It builds a synthetic environment with root, host, user, path, port, `.git`, HTTP, SSH, and wildcard host keys, then checks both `Get` and `GetAll` behavior for representative URLs.

The test signal is strong for Git-compatible matching precedence: host/path-specific values override root config, username-specific values override host-only when paths tie, explicit ports matter, default ports match, `.git/info/lfs` can match a repository path without `.git`, and malformed prefix/key patterns are ignored. Gaps include invalid raw URLs, multiple wildcard specificity cases, credential-specific skip/protect booleans, and `Bool` conversion.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/url_config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/util_nix.go -->
# sources/sync-backup/git-lfs/config/util_nix.go

## Research

This Unix-only file provides `umask()` for permission calculations. It calls `syscall.Umask(022)` to retrieve the current process mask, immediately restores the original value, and returns it.

The function integrates with `Configuration.getMask` and repository file/directory permission decisions. Its side effect is process-global but brief; concurrent code changing umask could race because POSIX umask is process-wide. Tests in `config_test.go` use this helper indirectly when computing expected defaults. The platform split pairs with `util_windows.go`, where no syscall exists.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/util_nix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/util_windows.go -->
# sources/sync-backup/git-lfs/config/util_windows.go

## Research

This Windows-only file implements `umask()` as a constant `077` because Windows lacks a POSIX umask syscall and owner bits are the meaningful chmod component. It feeds the same `Configuration.getMask` and `RepositoryPermissions` paths as Unix.

There is no mutable state or external I/O. The risk is semantic approximation: shared repository modes on Windows cannot mirror Unix group/world semantics exactly, and tests relying on exact modes must account for build tags.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/util_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/config/version.go -->
# sources/sync-backup/git-lfs/config/version.go

## Research

`version.go` defines build/version metadata. `Version` is `3.7.0`; variables `GitCommit`, `VersionDesc`, and `Vendor` can be populated at build time. `init` defaults `Vendor` to `GitHub`, appends Git commit metadata if present, and constructs a user-agent-like `VersionDesc` containing version, vendor, OS, architecture, Go runtime, and optional commit.

State is package-global and initialized once. Integration includes CLI version output and HTTP user-agent/version reporting elsewhere. Risks are build flag drift, runtime `strings.Replace(runtime.Version(), "go", "", 1)` assumptions, and global variables being mutable after init. There are no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/config/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/access.go -->
# sources/sync-backup/git-lfs/creds/access.go

## Research

`access.go` defines authentication access modes and the `Access` value object. Modes include `none`, `basic`, `private`, `negotiate`, and empty. `NewAccess` constructs an access descriptor, `Upgrade` returns a copy with a new mode while preserving URL, and getters expose mode and URL. `AllAccessModes` returns the order attempted: none, negotiate, basic.

There is no persistence or I/O. Integration is with LFS API authentication negotiation and credential helper selection. Risks are policy-related: `PrivateAccess` and `EmptyAccess` are not returned by `AllAccessModes`, so callers must handle them separately, and adding a new mode requires updating negotiation order consistently.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/access.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/creds.go -->
# sources/sync-backup/git-lfs/creds/creds.go

## Research

`creds.go` implements Git LFS credential handling. It defines `CredentialHelper`, `CredentialHelperWrapper`, the multi-value `Creds` map, `CredentialHelperContext`, askpass integration, `commandCredentialHelper` for `git credential`, an in-memory `credentialCacher`, a chained `CredentialHelpers`, `NullCreds`, and `FirstEntryForKey`.

Control flow starts with `NewCredentialHelperContext`, which configures netrc, askpass, cache, URL config, and command helper. `GetCredentialHelper` builds Git credential input from URL, `credential.usehttppath`, auth headers, and state fields, then composes helpers. `FillCreds` errors if no helper yields credentials. `Creds.buffer` emits Git credential protocol data with capability lines and rejects LF, NUL, and optionally CR injection. `commandCredentialHelper.exec` shells out to `git credential fill|approve|reject`; the helper chain skips helpers that error and clears cached approvals on downstream approve failure. Persistent behavior includes subprocess calls, in-memory credential cache, and helper skip state. Dependencies include URL config, netrc, subprocess, path translation, translation, and tracer logging. Risks are credential protocol injection, prompt suppression semantics, skipped helper lifetime, cache key granularity, multistage credentials, stderr pass-through, and askpass command trust. `creds_test.go` covers protocol formatting/protection and helper chain/cache error behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/creds.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/creds_test.go -->
# sources/sync-backup/git-lfs/creds/creds_test.go

## Research

This file tests credential protocol formatting and the helper-chain state machine. `TestCredsBufferFormat` asserts capability lines and multi-value `wwwauth[]` output. `TestCredsBufferProtect` verifies LF and NUL are always rejected and CR is rejected only when protocol protection is enabled. The remaining tests use fake helpers plus `credentialCacher` to cover fill success, fill errors causing helper skip, approve errors, combined fill/approve errors, reject errors, cache population, cache clearing, and all-fill-error aggregation.

The tests are pure and do not invoke real `git credential` or askpass programs. They provide strong coverage for in-memory helper composition and injection protection. Gaps include `CredentialHelperContext` URL input construction, netrc integration, multistage `continue`, actual command helper exit-code handling, and askpass prompt behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/creds_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/netrc.go -->
# sources/sync-backup/git-lfs/creds/netrc.go

## Research

`netrc.go` provides `.netrc` credential support. `ParseNetrc` resolves `$HOME/.netrc`, falls back to `_netrc` on Windows, parses via `github.com/git-lfs/go-netrc/netrc`, and returns a `NetrcFinder`, filename, and error. `netrcCredentialHelper` implements `CredentialHelper` using a finder plus a per-host skip map.

`Fill` strips any port from the credential host, skips hosts previously rejected, and returns username/password plus protocol/host/path/source fields when a matching machine is found. `Approve` clears skip state only for credentials whose source is `netrc`; `Reject` marks the host skipped. State is process-local and mutex-protected. Integration is early in the credential helper chain before cache, askpass, and Git credential helpers. Risks include HOME absence, Windows basename differences, parse errors disabling netrc, host:port parsing failures, indexing `what["host"][0]` in `Reject`, and source-field trust. `netrc_test.go` covers host with port, host without port, and no-op on unknown host.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/netrc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/netrc_test.go -->
# sources/sync-backup/git-lfs/creds/netrc_test.go

## Research

This test file uses `fakeNetrc` to validate `netrcCredentialHelper.Fill`. It verifies that a host with a port is normalized before lookup, a bare host lookup works, and an unmatched host returns the sentinel `credHelperNoOp`.

The tests are pure and avoid filesystem parsing. They confirm the key integration behavior needed before the helper chain falls through to other credential sources. Remaining gaps include actual `.netrc` file discovery/parsing, Windows `_netrc`, reject/approve skip state, login-name-specific matching, malformed host:port values, and missing input keys.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/creds/netrc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/debian/postinst -->
# sources/sync-backup/git-lfs/debian/postinst

## Research

This Debian maintainer script runs `git lfs install --skip-repo --system` after package installation. Its purpose is to install system-level Git LFS filters/hooks while avoiding accidental mutation of `/` if the root directory happens to be a Git repository.

The script has no branching or local state. Persistent effects are system Git config/filter installation performed by `git lfs install`. Dependencies are `/bin/sh`, the packaged `git-lfs` binary, Git, and sufficient privileges for system config. Risks are install-time failure propagating to package configuration, path lookup of `git`, and behavior changes in `git lfs install`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/debian/postinst -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/debian/prerm -->
# sources/sync-backup/git-lfs/debian/prerm

## Research

This Debian pre-removal script runs `git lfs uninstall --skip-repo --system`. It removes system-level Git LFS configuration while avoiding repository-local changes in `/`, preserving user intent if replacing the package with another installation.

There is no local state or control flow. Persistent effects are system Git config/filter removal. Dependencies mirror `postinst`: `/bin/sh`, `git-lfs`, Git, and permissions. Risks include uninstall failure blocking package removal and assumptions that system config should be removed for every pre-removal action.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/debian/prerm -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/debian/rules -->
# sources/sync-backup/git-lfs/debian/rules

## Research

`debian/rules` drives Debian packaging through debhelper and `dh_golang`. It maps Debian architectures to Go `GOARCH`, sets `DH_GOPKG`, vendor excludes, module/vendor flags, `FORCE_LOCALIZE`, `PATH`, and Go cache, then defines overrides for clean, build, strip, golang metadata, install, and tests.

The build flow runs localization generation, `dh_auto_build`, cross-build binary copy fixups, manpage generation, installs `git-lfs` into `debian/git-lfs/usr/bin`, and creates temporary symlinks for tests so `dh_auto_test` sees expected repo paths. Persistent effects are build artifacts, generated man files, package staging files, and temporary symlinks removed after tests. Risks include Debian architecture mapping drift, excluded vendored packages, disabled stripping, cross-build path assumptions, symlink cleanup after failed tests, and reliance on `/tmp/gocache`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/debian/rules -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-batch-request-schema.json -->
# sources/sync-backup/git-lfs/docs/api/schemas/http-batch-request-schema.json

## Research

This JSON Schema documents the Git LFS HTTPS Batch API request. The top-level object may contain `transfers`, required `operation`, and required `objects`. Each object requires `oid` and nonnegative numeric `size`, may include `authenticated`, and disallows additional properties.

It has no runtime state, but acts as an integration contract for clients, servers, tests, and documentation. Risks are schema/spec drift, loose `operation` string validation, no OID pattern enforcement, and using `number` rather than integer for sizes. Test signals would be schema validation of sample requests and compatibility with actual batch API structs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-batch-request-schema.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-batch-response-schema.json -->
# sources/sync-backup/git-lfs/docs/api/schemas/http-batch-response-schema.json

## Research

This schema defines the Git LFS HTTPS Batch API response. It requires `objects`; each object requires `oid` and nonnegative `size`, can carry `authenticated`, `actions`, or `error`. An `action` requires `href` and may include headers, `expires_in`, and `expires_at`. Top-level response metadata includes `transfer`, `message`, `request_id`, and `documentation_url`.

The schema is documentation/validation state only. Integration points are batch transfer clients/servers and API docs. Risks include permissive string fields, `expires_at` not date-formatted, `expires_in` allowing negative values, numeric sizes/codes rather than integers, no OID pattern, and `additionalProperties: false` potentially rejecting future protocol extensions unless versioned.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-batch-response-schema.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-create-request-schema.json -->
# sources/sync-backup/git-lfs/docs/api/schemas/http-lock-create-request-schema.json

## Research

This schema documents lock creation requests. The request is an object requiring `path`; it may include `ref` with required `name`. Additional properties are not explicitly disabled at the top level or inside `ref`.

It is a contract artifact for Git LFS locking API documentation and validators. Risks include no path format constraints, optional ref behavior depending on server support, and permissive additional properties that may hide client mistakes. Test signals are schema validation of lock create examples and parity with lock API structs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-create-request-schema.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-create-response-schema.json -->
# sources/sync-backup/git-lfs/docs/api/schemas/http-lock-create-response-schema.json

## Research

This schema defines lock creation responses. The top-level object requires `lock`; `lock` requires `id`, `path`, and `locked_at`, and may include an `owner` object with `name`. Error-style metadata fields `message`, `request_id`, and `documentation_url` are also allowed.

There is no runtime state. Integration is API documentation and compatibility validation for lock clients/servers. Risks are no date-time format validation for `locked_at`, owner not required, no `additionalProperties: false`, and overlap between success and error metadata in the same schema.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-create-response-schema.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-delete-request-schema.json -->
# sources/sync-backup/git-lfs/docs/api/schemas/http-lock-delete-request-schema.json

## Research

This schema documents lock deletion request bodies. It allows optional `force` boolean and optional `ref` object with required `name` if present. No top-level fields are required.

The schema is used as API documentation/validation and has no executable state. Risks include permissive additional properties, no explicit lock ID because the ID is typically in the URL path, and no constraints on ref naming. Test signals should validate force and non-force examples against client/server request structs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-delete-request-schema.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-list-response-schema.json -->
# sources/sync-backup/git-lfs/docs/api/schemas/http-lock-list-response-schema.json

## Research

This schema defines lock list responses. The response requires `locks`, an array of lock objects with optional `id`, `path`, `locked_at`, and `owner.name`, and may include `next_cursor` for pagination.

It is a non-executable API contract artifact. Risks include weak lock item requirements compared with create/verify schemas, no date format, no pagination type beyond string, and permissive additional properties. Test signals are validation of list responses with and without pagination and parity with API documentation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-list-response-schema.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-verify-response-schema.json -->
# sources/sync-backup/git-lfs/docs/api/schemas/http-lock-verify-response-schema.json

## Research

This schema defines lock verification responses. It requires `ours` and `theirs` arrays, each containing lock objects from a shared definition. A lock requires `id` and `path`, and may include `locked_at` and `owner.name`. `next_cursor` supports pagination.

The schema has no runtime state but is central to push lock verification semantics because `theirs` drives upload rejection/warnings and `ours` can prompt unlock hints. Risks include `locked_at` optionality, no owner requirement, no date format, and permissive additional properties. Test signals should cover empty arrays, paginated responses, and responses containing unowned locks.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/api/schemas/http-lock-verify-response-schema.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/man/asciidoctor-extensions/manpage-extension.rb -->
# sources/sync-backup/git-lfs/docs/man/asciidoctor-extensions/manpage-extension.rb

## Research

This Ruby extension customizes Asciidoctor manpage conversion for Git LFS docs. `GitLFSManPageConverter` subclasses `Asciidoctor::Converter::ManPageConverter`, registers for `manpage`, and overrides `convert_listing`. For listing blocks with role `synopsis`, it removes `.RS` and `.RE` indentation macros, optionally preceded by `.if n`, then drops empty lines.

State is local to conversion. Integration is the documentation build pipeline that renders manpages. Risks include Asciidoctor internal output changing, regex over-removing legitimate lines in synopsis blocks, and only handling listing blocks rather than other synopsis representations. Test signals would be generated manpage diffs for synopsis indentation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/man/asciidoctor-extensions/manpage-extension.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/man/mangen.go -->
# sources/sync-backup/git-lfs/docs/man/mangen.go

## Research

`mangen.go` is a generator that converts `docs/man/git-lfs*.adoc` files into Go string literals in `commands/mancontent_gen.go`. It finds the docs root, creates the generated file, scans matching AsciiDoc files, derives command keys, and writes an `init` function assigning `ManPages[...]`.

The scanner transforms headings, skips `Name`, trims `Description`, renders `Options`, stops at `See also`, resolves xrefs/man links, skips anchors, strips source block delimiters and invisible markup, de-emphasizes synopsis source formatting, and indents list continuations. Persistent effects are generated Go source and stderr warnings. Dependencies are filesystem layout, regexp patterns, and `go generate`/Makefile invocation. Risks include raw backtick string escaping if docs contain backticks in unexpected contexts, scanner token limits for long lines, regex drift with AsciiDoc syntax, skipped close errors, and root fallback to `/tmp/docker_run/git-lfs`. Test signals are deterministic generated `ManPages`, CLI help output, and man generation in Debian rules.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/docs/man/mangen.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/context.go -->
# sources/sync-backup/git-lfs/errors/context.go

## Research

`context.go` defines helpers for contextual metadata on wrapped errors. The unexported `withContext` interface requires `Set`, `Get`, `Del`, and `Context`. Exported helpers `SetContext`, `GetContext`, `DelContext`, and `Context` no-op or return empty values for ordinary errors.

State lives inside `wrappedError.context` maps in `types.go`. Integration is used by smudge and clean pointer errors to attach OID, filename, pointer, or byte data, and by callers that need diagnostic details without type assertions. Risks include no synchronization around context maps, value receiver methods sharing the same map, `GetContext` returning empty string while `Context` returns nil for non-wrapped errors, and context not propagating through Go 1.20 joined errors. `errors_test.go` covers context on plain and wrapped errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/context.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/errors.go -->
# sources/sync-backup/git-lfs/errors/errors.go

## Research

`errors.go` is the public entrypoint for Git LFS error construction. It wraps `github.com/pkg/errors` for stack-bearing `New`, `Errorf`, `Wrap`, and `Wrapf`, provides `Join` through the standard library, and recursively unwraps `Cause`.

The control flow in `Wrap`/`Wrapf` creates `wrappedError` values from `types.go`, preserving context support and behavioral marker methods. `Wrapf(nil, ...)` creates an empty underlying error. There is no persistent state. Integration is broad across Git LFS packages for fatal, auth, smudge, retriable, and protocol errors. Risks include mixed unwrap models (`pkg/errors.Cause`, standard `errors.Join`, and custom `parentOf`), nil wrapping behavior, and stack formatting compatibility. Tests in `errors_test.go` validate behavior marker detection and context interactions.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/errors_test.go -->
# sources/sync-backup/git-lfs/errors/errors_test.go

## Research

This test file validates high-level behavior of the custom error system. It confirms plain Go errors do not satisfy LFS behavior checks, wrapped fatal errors do, nested behavior wrappers preserve both outer and inner markers, and context helpers are inert for plain errors but functional for wrapped errors.

The tests are pure and exercise the recursive behavior inspection path in `types.go` plus context helpers in `context.go`. Gaps include joined errors, retriable URL errors, Retry-After parsing, protocol/auth/smudge/clean constructors, `ExitStatus`, and stack formatting.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/errors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/types.go -->
# sources/sync-backup/git-lfs/errors/types.go

## Research

`types.go` defines the concrete wrapped error hierarchy and inspection helpers. It includes behavior predicates for fatal, not implemented, auth, smudge, clean pointer, not-a-pointer, pointer scan, bad pointer key, protocol, download declined, unprocessable entity, retriable, and retriable-later errors. `wrappedError` embeds a `pkg/errors` cause/formatter plus a context map.

Constructors wrap underlying errors and attach marker methods. `NewRetriableLaterError` parses Retry-After as seconds or RFC1123 time; `IsRetriableError` also recognizes temporary/timeout `url.Error` causes; `ExitStatus` extracts process exit status. `parentOf` recursively inspects `Cause` to let outer wrappers inherit inner marker behavior. State is per-error context and optional retry timestamp. Dependencies include `net/url`, `exec`, `syscall`, `time`, translation, and `pkg/errors`. Risks include brittle type assertion in `StandardizeBadPointerError`, joined error incompatibility, `parentOf` skipping only through cause chains, mutable unsynchronized contexts, and platform-specific wait status. Tests cover marker nesting and URL temporary/timeout retry classification.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/types_test.go -->
# sources/sync-backup/git-lfs/errors/types_test.go

## Research

This file tests retriable classification for `*url.Error`. Custom `TemporaryError` and `TimeoutError` types implement the legacy `Temporary()` and `Timeout()` methods; the tests assert they are retriable, while a generic wrapped error is not.

The tests are focused and pure. They protect the fallback path in `IsRetriableError` that uses `Cause(err).(*url.Error)` and checks network-transient methods. Gaps include explicit `NewRetriableError`, retry-after parsing, nested wrappers, joined errors, and modern `net.Error` behavior beyond the small fake types.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/errors/types_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/filepathfilter/filepathfilter.go -->
# sources/sync-backup/git-lfs/filepathfilter/filepathfilter.go

## Research

`filepathfilter.go` implements include/exclude path filtering for Git LFS fetch and attribute behavior. `Pattern` abstracts matchers; `Filter` stores include/exclude patterns, a default value, and optional LRU cache; `PatternType` distinguishes GitIgnore and GitAttributes semantics. Options configure default value and cache.

`New` converts raw patterns to `wildmatch.Wildmatch`; `Allows` returns true for nil filters, consults cache, then applies include-first/exclude-second logic. If include patterns exist and none match, the file is rejected. If default is false and no include matched, excludes are skipped. `NewPattern` configures wildmatch flags and optional case folding from `core.ignorecase`. State includes slices of patterns and a mutex-protected groupcache LRU. Dependencies are `git-lfs/wildmatch`, `groupcache/lru`, config-like environment, and tracer logging. Risks include cache size semantics, path separator normalization, GitIgnore vs GitAttributes behavior differences, nil environment, and cached results if config/patterns change externally. Tests cover many pattern and filter reporting cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/filepathfilter/filepathfilter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/filepathfilter/filepathfilter_test.go -->
# sources/sync-backup/git-lfs/filepathfilter/filepathfilter_test.go

## Research

This test file validates path matching behavior through `NewPattern` and `Filter` accessors. It covers wildcards, filename-only matches in subfolders, directory-specific matches, absolute/rooted patterns, directory suffix behavior differences between GitAttributes and GitIgnore, dot/path cases, and reporting of include/exclude pattern strings.

The tests are pure and heavily exercise the external wildmatch integration. They are important because LFS include/exclude behavior controls which objects are fetched or skipped. Remaining gaps include `Filter.Allows` include/exclude combinations beyond reporting, cache behavior, `DefaultValue(false)`, `core.ignorecase`, and Windows path separator cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/filepathfilter/filepathfilter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/fs/cleanup.go -->
# sources/sync-backup/git-lfs/fs/cleanup.go

## Research

`cleanup.go` prunes stale temporary LFS files. `Filesystem.cleanupTmp` resolves the temp directory, ignores missing directories, walks it with `tools.FastWalkDir`, tracks traversed directory metadata, removes temp files whose prefix is a 64-character OID when the final object already exists, and removes files older than one hour while sparing young subdirectories.

Persistent effects are deletions under `.git/lfs/tmp`. State is walk-local plus the filesystem’s path helpers. Integration is `Filesystem.Cleanup` and `Configuration.Cleanup`, also called from process shutdown. Risks include concurrent transfers using temp files, reliance on directory mtime to protect hard-linked active files, walk error handling through a shared variable, OID prefix heuristic, and `os.RemoveAll` errors ignored. There is no direct test in this subset; integration should verify active downloads are not pruned and old complete temp files are removed.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/fs/cleanup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/fs/fs.go -->
# sources/sync-backup/git-lfs/fs/fs.go

## Research

`fs.go` models local LFS storage. `Filesystem` stores Git storage dir, LFS storage dir, reference object dirs, cached object/tmp/log dirs, repository permissions, and a mutex. It exposes object enumeration/existence/pathing, path decode helpers, repository permissions, object reference paths, lazy directory creation, cleanup, constructor `New`, alternate resolution, worktree/common-dir handling, and Git redirect file parsing.

Control flow maps OIDs to `objects/aa/bb/<oid>`, treats the empty SHA-256 object as `os.DevNull`, decodes quoted octal paths, reads `GIT_ALTERNATE_OBJECT_DIRECTORIES` and `.git/objects/info/alternates`, and resolves `commondir` indirection for worktrees. Persistent effects are directory creation and cleanup deletion. Dependencies include `tools.FastWalkDir`, `tools.MkdirAll`, path utilities, environment, tracer logging, and OS filesystem calls. Risks include OID length assumptions in `ObjectReferencePaths`, `EachObject` ignoring callback errors, path decode byte/string encoding, alternate quoting, symlink/common-dir correctness, and permission propagation. `fs_test.go` covers octal path decoding and executable/non-executable permissions.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/fs/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/fs/fs_test.go -->
# sources/sync-backup/git-lfs/fs/fs_test.go

## Research

This test file covers two `fs.go` behaviors. The decode tests verify that non-octal paths remain unchanged and octal byte escapes are converted back into bytes/characters, including multiple escapes. `TestRepositoryPermissions` verifies executable permissions are derived from stored non-executable repository permissions.

Tests are pure except for mode constants. They protect Windows/Git quoted path decoding used when Git escapes non-ASCII filenames. Gaps include object path creation, empty object handling, alternate reference resolution, cleanup pruning, common-dir redirects, callback error propagation, and repository permission interactions with real directories.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/fs/fs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git-lfs.go -->
# sources/sync-backup/git-lfs/git-lfs.go

## Research

This is the Git LFS executable entrypoint. `main` registers for interrupt and kill signals, starts a goroutine that runs `commands.Cleanup`, reports the signal, and exits with `128 + signal number` when possible. Normal execution calls `commands.Run`, then `commands.Cleanup`, and exits with the returned code.

State is limited to the signal channel and process exit path. Integration is with the full `commands` package lifecycle, translation, and OS signal handling. Risks include `os.Kill` not being catchable on Unix, cleanup racing with command execution, repeated signals triggering repeated cleanup attempts, and exit code portability across platforms. Tests would need process-level integration rather than unit tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git-lfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git-lfs_windows_386.go -->
# sources/sync-backup/git-lfs/git-lfs_windows_386.go

## Research

This Windows/386 build-tag file contains only `//go:generate goversioninfo` and `package main`. It participates in Windows executable metadata generation for 32-bit builds.

There is no runtime code or state. Integration is the Go generate/build pipeline and the `goversioninfo` tool. Risks are stale metadata generation, missing tool installation, and architecture-specific build tags not matching packaging expectations.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git-lfs_windows_386.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git-lfs_windows_amd64.go -->
# sources/sync-backup/git-lfs/git-lfs_windows_amd64.go

## Research

This Windows/amd64 build-tag file contains `//go:generate goversioninfo -64=true` and `package main`. It exists to generate Windows version resources for 64-bit x86 builds.

There is no executable logic. Integration is with `go generate` and release packaging. Risks are metadata drift, missing `goversioninfo`, and ensuring the correct architecture flag is used for amd64 artifacts.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git-lfs_windows_amd64.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git-lfs_windows_arm64.go -->
# sources/sync-backup/git-lfs/git-lfs_windows_arm64.go

## Research

This Windows/arm64 build-tag file contains `//go:generate goversioninfo -arm=true -64=true` and `package main`. It provides architecture-specific resource generation for Windows ARM64 builds.

There is no runtime state or control flow. Integration is the release build/generation pipeline. Risks include `goversioninfo` support for ARM64 metadata and keeping build tags aligned with Go’s target names.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git-lfs_windows_arm64.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/config.go -->
# sources/sync-backup/git-lfs/git/config.go

## Research

`git/config.go` wraps `git config`. `Configuration` stores workdir, gitdir, cached version, read-only flag, and mutex. Constructors support normal and read-only configs. It exposes find/set/unset methods for global, system, local, worktree, and file scopes; parses config output into `ConfigurationSource`; and resolves source ordering for `.lfsconfig` plus normal Git config.

Control flow shells out to `git config --includes`, optionally setting `cmd.Dir` to `GitDir`. `Sources` loads regular config, then safe optional config from working tree, index, or `HEAD`, depending on bare status and file existence. Persistent effects occur only through write methods unless `readOnly` returns `ErrReadOnly`. Dependencies include subprocess execution, Git repository state, and config safety flags consumed by `config.GitFetcher`. Risks include command failures swallowed by `Find*`, read-only bypass if callers use other Git APIs, `.lfsconfig` source precedence, worktree config support, and running commands from `GitDir` instead of worktree. `config_test.go` verifies read-only writes fail.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/config_test.go -->
# sources/sync-backup/git-lfs/git/config_test.go

## Research

This test file validates the read-only guard in `git.Configuration`. It creates `NewReadOnlyConfig`, attempts `SetLocal`, and expects `ErrReadOnly`.

The test is intentionally narrow and avoids invoking real Git. It protects the mutation guard used when code needs a config reader that cannot write. Gaps include all find/set/unset command construction, source loading, `.lfsconfig` fallbacks, file/worktree scopes, and version caching.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/filter_process_scanner.go -->
# sources/sync-backup/git-lfs/git/filter_process_scanner.go

## Research

`filter_process_scanner.go` implements Git filter-process pkt-line protocol scanning. `FilterProcessScanner` owns a `pktline.Pktline`, current `Request`, and last error. `Init` performs the `git-filter-client`/`git-filter-server` version=2 handshake. `NegotiateCapabilities` requires clean and smudge, accepts delay when Git offers it, and writes selected capabilities.

`Scan` reads one request header packet list and exposes a payload reader backed by pkt-line until flush. `Request` and `Err` report the last scan result. `WriteList` and `WriteStatus` write response lists/status values. State is sequential and not synchronized; callers must consume each payload before scanning the next request. Dependencies include `pktline`, custom errors, translations, slices, and tracer logging. Risks include protocol desynchronization if payloads are not fully read, unsupported capability handling, scanner lifecycle around EOF, and header parsing that ignores malformed pairs without `=`. Tests cover handshake, capability negotiation, request/payload reading, invalid packet errors, and list writing.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/filter_process_scanner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/filter_process_scanner_test.go -->
# sources/sync-backup/git-lfs/git/filter_process_scanner_test.go

## Research

This file tests the filter-process scanner with in-memory pkt-line buffers. It verifies successful initialization writes server/version packets, invalid welcome messages and unsupported versions are rejected without output, supported capabilities are negotiated, unsupported capability sets fail, request headers and multi-packet payloads are read, invalid packet length is surfaced, and `WriteList` emits correct pkt-line framing.

The tests provide strong protocol regression coverage without invoking Git. Remaining gaps include delay capability acceptance, `WriteStatus`, EOF behavior, malformed header key/value pairs, reading multiple sequential requests, and payload-not-drained desynchronization.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/filter_process_scanner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/filter_process_status.go -->
# sources/sync-backup/git-lfs/git/filter_process_status.go

## Research

`filter_process_status.go` defines `FilterProcessStatus` constants for pkt-line filter responses: success, delayed, and error. `String` converts them to protocol values `success`, `delayed`, and `error`, and panics through translated text for unknown statuses.

There is no state or I/O. Integration is `FilterProcessScanner.WriteStatus` and any clean/smudge filter-process handler. Risks are panic on invalid values, protocol spelling drift, and lack of direct tests for every status string.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/filter_process_status.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/git/git.go -->
# sources/sync-backup/git-lfs/git/git.go

## Research

`git.go` is the broad Git subprocess integration layer. It defines `RefType`, `Ref`, object ID constants/regexes, `IndexStage`, `CommitSummary`, `Worktree`, `CloneFlags`, and many helpers for invoking Git with LFS filters disabled or enabled. Core APIs cover ref parsing/resolution, current/remote refs, remote lists/URLs, ref updates, clone/checkout/fetch, worktree enumeration, repository directory discovery, tracked/changed/modified files, dirty checks, object database construction, and remote inference for a treeish.

Control flow is mostly thin subprocess orchestration around `git rev-parse`, `show-ref`, `for-each-ref`, `ls-remote`, `worktree list`, `clone`, `checkout`, `diff-index`, `diff-tree`, `status`, `ls-files`, `hash-object`, and `cat-file`. `gitConfigNoLFS` disables smudge/clean/filter-process for operations that must not trigger LFS downloads. State includes cached empty tree OID guarded by a mutex and global object ID metadata. Persistent effects include updating refs/index, cloning, fetching, checkout mutations, and possible object database writes through `gitobj`. Dependencies include `subprocess`, `tools`, custom errors, `gitobj`, OS/filesystem, URL parsing, time parsing, and tracer logging. Risks include subprocess portability, Git version feature gates, SHA-1/SHA-256 length assumptions, scanner error handling, ambiguous remotes with slashes, command output parsing, worktree fallback assumptions about absolute gitdir files, and path quoting/special character behavior. Test coverage in this subset is limited; many helpers require integration tests with real repositories.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/git/git.go -->
