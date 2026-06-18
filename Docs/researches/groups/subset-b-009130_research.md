# subset-b-009130 research

Grouped research report for Git LFS locking, SSH transport, subprocess helpers, release scripts, and integration-test tools. Each section preserves the exact source path and is wrapped for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/locks.go -->
# sources/sync-backup/git-lfs/locking/locks.go

Purpose: implements the high-level Git LFS locking client that commands use to create, remove, search, verify, cache, and apply local filesystem policy for locks.

Important APIs/types/functions: `LockCacher`, `Client`, `NewClient`, `SetupFileCache`, `Close`, `LockFile`, `UnlockFile`, `UnlockFileById`, `Lock`, `SearchLocks`, `SearchLocksVerifiable`, `searchLocalLocks`, `searchRemoteLocks`, `lockIdFromPath`, `IsFileLockedByCurrentCommitter`, `EncodeLocks`, `EncodeLocksVerifiable`, and `nilLockCacher`. `ErrNoMatchingLocks` and `ErrLockAmbiguous` are the main resolution errors.

Control flow: `NewClient` wires a generic HTTP/SSH-capable `lockClient`, config, local paths, and a no-op cache. `SetupFileCache` swaps in an on-disk lock cache and establishes a separate JSON cache directory. Lock and unlock calls send ref-aware API requests, translate server messages into user errors, update local cache state, and toggle local write permissions when required. Search either reads local cache, reads JSON cache, or pages the remote endpoint and optionally writes unfiltered unlimited results back to cache. Verifiable search clears the cache, pages `/locks/verify`, partitions ours/theirs, and writes a verifiable cache when unlimited.

State/persistence behavior: persistent state lives in `lockcache.db` via `LockCacher` and in JSON cache files under `<cacheDir>/locks/<refspec>/{remote,verifiable}`. File writability is also stateful: locked files are made writable after lock acquisition, and unlocked lockable files can be made read-only.

Dependencies/integration: depends on config paths, `git.Ref` refspecs, `lfsapi` clients, `filepathfilter` lockability helpers elsewhere in the package, `tools` filesystem helpers, `kv` storage registration, and `tracerx` request-id tracing.

Risks: `RemoteRef` is dereferenced in several paths and must be set by callers. Cache reads reject filters/limits, so callers must avoid treating cached search as a full query API. Cache directory names include refspecs, which can contain slashes and therefore intentionally form nested paths.

Test signals: `locks_test.go` covers remote caching, cache refresh, pagination, and verifiable cache behavior. API/schema tests in the package validate wire compatibility.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/locks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/locks_test.go -->
# sources/sync-backup/git-lfs/locking/locks_test.go

Purpose: verifies the locking client's remote search and cache refresh behavior against local HTTP test servers.

Important APIs/types/functions: `LocksById` provides deterministic sorting. `TestRemoteLocksWithCache`, `TestRefreshCache`, and `TestSearchLocksVerifiableWithCache` exercise `NewClient`, `SetupFileCache`, `prepareCacheDirectory`, `SearchLocks`, and `SearchLocksVerifiable`.

Control flow: each test creates a temp cache and `httptest.Server`, configures an `lfsapi.Client` with `lfs.url`, sets `RemoteRef`, then asserts when network calls happen and when cache files appear. Remote search with filters or limits must not create cache files; unlimited remote search must create them. Verifiable search walks two cursor pages before caching.

State/persistence behavior: tests inspect cache-file existence and fixed encoded sizes, then read the cached data back without incrementing the remote query counter. `TestRefreshCache` also confirms verifiable search repopulates the local in-memory lock cache.

Dependencies/integration: uses `lfshttp.NewContext`, `config.New`, `git.Ref`, JSON encoding of lock response structs, and testify assertions.

Risks: fixed byte-size assertions are sensitive to JSON formatting and struct shape. Tests sort only after collecting data, so ordering is intentionally not part of the remote contract.

Test signals: failures indicate regressions in cache gating, pagination, ref-scoped cache paths, local cache refresh, or cached verifiable result decoding.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/locks_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/schemas/http-lock-create-request-schema.json -->
# sources/sync-backup/git-lfs/locking/schemas/http-lock-create-request-schema.json

Purpose: JSON Schema draft-04 contract for Git LFS HTTPS lock creation requests.

Important API fields: top-level object with required `path` string and optional `ref` object. `ref`, when present, contains required `name` string.

Control flow: not executable; consumed by API tests to validate serialized lock creation payloads.

State/persistence behavior: no local state. It defines the client-to-server wire shape used before a lock exists on the server.

Dependencies/integration: aligns with `lockRequest` and `lockRef` in the locking API implementation.

Risks: the schema does not constrain path format, ref namespace, or additional properties. Servers must enforce semantic validation separately.

Test signals: schema validation should fail if `path` is absent or a provided `ref` lacks `name`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/schemas/http-lock-create-request-schema.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/schemas/http-lock-create-response-schema.json -->
# sources/sync-backup/git-lfs/locking/schemas/http-lock-create-response-schema.json

Purpose: JSON Schema draft-04 contract for Git LFS HTTPS lock creation responses.

Important API fields: required top-level `lock` object. A lock requires `id`, `path`, and `locked_at`; optional `owner.name` can identify the creator. Optional top-level error/context fields are `message`, `request_id`, and `documentation_url`.

Control flow: not executable; validates the response shape that `LockFile` decodes into `lockResponse` and then caches.

State/persistence behavior: successful responses become local `Lock` records in cache and may influence file writability.

Dependencies/integration: mirrors `Lock`, `User`, and response message handling in the locking client.

Risks: `locked_at` is only typed as string, not format-checked as RFC3339. Owner is not required, while SSH parsing requires owner fields, so transport contracts are not identical.

Test signals: schema tests should catch missing `lock`, missing core lock fields, or type drift.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/schemas/http-lock-create-response-schema.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/schemas/http-lock-delete-request-schema.json -->
# sources/sync-backup/git-lfs/locking/schemas/http-lock-delete-request-schema.json

Purpose: JSON Schema draft-04 contract for Git LFS HTTPS unlock/delete requests.

Important API fields: optional `force` boolean and optional `ref` object with required `name` when `ref` is present. There are no top-level required properties.

Control flow: not executable; validates the body sent by `Unlock`.

State/persistence behavior: no direct persistence. Server response determines whether local lock cache is updated and file permissions are changed.

Dependencies/integration: aligns with `unlockRequest` and ref-aware unlock behavior.

Risks: the schema permits an empty object, so callers can omit both force and ref. Semantic authorization and branch/ref enforcement are server responsibilities.

Test signals: schema validation catches wrong `force` type or malformed `ref`, but not missing lock id because the id is encoded in the URL path, not this body.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/schemas/http-lock-delete-request-schema.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/schemas/http-lock-list-response-schema.json -->
# sources/sync-backup/git-lfs/locking/schemas/http-lock-list-response-schema.json

Purpose: JSON Schema draft-04 contract for HTTPS lock list responses.

Important API fields: required `locks` array, with each item carrying optional `id`, `path`, `locked_at`, and `owner.name`. `next_cursor` supports pagination.

Control flow: not executable; validates list responses consumed by `SearchLocks` and remote pagination.

State/persistence behavior: unlimited unfiltered list responses can be persisted into the `remote` JSON cache file.

Dependencies/integration: maps to `lockList` and `Lock` structures used by the HTTP lock client.

Risks: item fields are not required in this schema, so structurally valid but semantically incomplete locks may pass validation and then cause downstream ambiguity. `locked_at` format is not constrained.

Test signals: schema validation catches missing `locks` or non-array response shapes.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/schemas/http-lock-list-response-schema.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/schemas/http-lock-verify-response-schema.json -->
# sources/sync-backup/git-lfs/locking/schemas/http-lock-verify-response-schema.json

Purpose: JSON Schema draft-04 contract for HTTPS lock verification responses.

Important API fields: required `ours` and `theirs` arrays of lock objects. Defined locks require `id` and `path`; `locked_at` and `owner.name` are optional. `next_cursor` supports pagination.

Control flow: not executable; validates responses used by `SearchLocksVerifiable`.

State/persistence behavior: unlimited verify results can be encoded into the `verifiable` JSON cache and also repopulate the in-memory lock cache.

Dependencies/integration: maps to `lockVerifiableList`, `Lock`, and pre-push/verify workflows that distinguish current-user locks from conflicting locks.

Risks: `owner` and `locked_at` are optional for compatibility, so callers must not assume complete metadata. Pagination correctness depends on server-provided `next_cursor`.

Test signals: schema tests catch missing `ours`/`theirs` arrays and incompatible lock field types.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/schemas/http-lock-verify-response-schema.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/ssh.go -->
# sources/sync-backup/git-lfs/locking/ssh.go

Purpose: adapts the locking `lockClient` interface to the pure SSH Git LFS transfer protocol using pkt-line commands instead of HTTP.

Important APIs/types/functions: `sshLockClient`, `connection`, `parseLockResponse`, `owner`, `lockData`, `parseListLockResponse`, `Lock`, `Unlock`, `Search`, and `SearchVerifiable`.

Control flow: each public method obtains transfer connection 0, locks the connection mutex, sends a pkt-line command (`lock`, `unlock <id>`, or `list-lock`), reads status/args/lines, and converts protocol data into the same response structs used by HTTP. Lock responses parse key-value args for id, path, owner name, and RFC3339 timestamp. List responses parse `lock`, `path`, `owner`, `ownername`, and `locked-at` lines, plus `next-cursor` args.

State/persistence behavior: the SSH client itself stores only a pointer to `ssh.SSHTransfer`; lock state remains server-side and is cached by `locks.go`.

Dependencies/integration: integrates with `github.com/git-lfs/git-lfs/v3/ssh` `PktlineConnection`, `git.Ref`, shared response types, and translated errors.

Risks: list parsing is order-sensitive and rejects interspersed or incomplete lock data. A map is used before returning locks, so all-lock ordering is not guaranteed. The `force` unlock flag is accepted by the interface but not encoded in this SSH command implementation.

Test signals: coverage is mostly indirect through SSH transfer/integration tests and locking API parity. Parser regressions would surface as protocol errors or missing locks.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/locking/ssh.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/script/build-git -->
# sources/sync-backup/git-lfs/script/build-git

Purpose: CI helper that installs build dependencies, builds Git from a provided source directory, installs it, and prints version/library diagnostics.

Important commands/functions: OS dispatch on `uname`, Ubuntu deb-src enablement, `apt-get build-dep git`, Homebrew curl prefix discovery, `config.mak` generation, optional curl macro patch, `make -j4`, `sudo make install`, `git --version --build-options`, `otool`, and `ldd`.

Control flow: receives the Git source directory as `$1`, performs platform-specific dependency setup, changes into that directory, conditionally patches old Git `http.h` curl compatibility macros, writes build flags disabling gettext/OpenSSL and setting prefix, builds, installs, and prints diagnostics for HTTP transport linkage.

State/persistence behavior: mutates package source lists on Linux, writes `config.mak`, may patch Git source in place, installs into `GIT_INSTALL_DIR` or `/usr/local`, and uses sudo for dependencies/install.

Dependencies/integration: used by CI jobs that need a freshly built Git binary compatible with Git LFS tests.

Risks: modifies system apt source configuration and requires sudo/network access. The patch is heuristic and may fail if Git source context changes.

Test signals: successful build, installed `git --version`, and expected curl-linked binary dependencies.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/script/build-git -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/script/changelog -->
# sources/sync-backup/git-lfs/script/changelog

Purpose: generates release changelog entries from merge commits or patch commits, either interactively or in an uncategorized noninteractive form.

Important APIs/functions: `commit_summary`, `revisions_in`, `noninteractive`, option handling for `--noninteractive` and `--patch`, Git commands, GitHub Pull Request API calls, `jq`, `curl`, and manual category selection.

Control flow: validates a commit range, chooses merge-only or patch revision traversal, then either prints uncategorized entries plus category headings or prompts the user to classify each revision as feature, bug, misc, or skip. `commit_summary` extracts a PR number from the commit, fetches PR metadata, strips backport prefixes, and emits a markdown bullet.

State/persistence behavior: no repository writes. Network requests depend on `.netrc` or curl auth configuration.

Dependencies/integration: feeds release notes consumed by the upload/release workflow.

Risks: assumes commits mention a single `#NNN` PR, depends on GitHub API availability and `jq`, and interactive mode is unsuitable for unattended CI.

Test signals: no direct tests. Usable output requires correct PR titles/numbers/authors and correctly categorized markdown sections.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/script/changelog -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/script/cibuild -->
# sources/sync-backup/git-lfs/script/cibuild

Purpose: top-level CI build and validation script for Git LFS.

Important steps: unsets most `GIT*`/`GITHUB*` variables, detects Windows-style environments, installs `scutiger-lfs`, installs `goimports`, runs `make` and `make test`, reruns Git package tests with `GIT_TRACE=1`, runs shell integration tests under `t/`, checks trailing whitespace, runs formatting, and asserts a clean git status.

Control flow: fail-fast bash script. It builds tool dependencies first, runs Go tests, then integration tests, then repository hygiene gates.

State/persistence behavior: installs tools into `t/scutiger` and `$GOPATH/bin`, builds binaries, cleans integration test state, formats files in place, and reads git status.

Dependencies/integration: depends on cargo, Go toolchain, make, prove, bash, and the `t/Makefile` integration test harness.

Risks: `go install ...@latest` can introduce toolchain/network variability. Formatting in place means local modifications are expected if formatting drifts. Environment stripping must preserve required hash settings.

Test signals: CI success means Go unit tests, Git-trace leakage checks, integration tests, whitespace, formatting, and clean tree all pass.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/script/cibuild -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/script/distro-tool -->
# sources/sync-backup/git-lfs/script/distro-tool

Purpose: command-line wrapper for distro metadata, implemented as the same Ruby source as `script/lib/distro.rb`.

Important APIs/classes: `DistroMap`, `DistroMapProgram`, `--image-names`, and `--distro-markdown`.

Control flow: builds a distro map, parses exactly one mode option, and either prints Docker image names or PackageCloud download markdown for each supported distro.

State/persistence behavior: read-only, no persistent state.

Dependencies/integration: invoked by release scripts such as `script/upload` to populate package links in GitHub release notes and by packaging jobs to enumerate build images.

Risks: hard-coded distro lifecycle metadata must be kept current. The tool returns status 2 when no mode is specified.

Test signals: `script/spec/distro_spec.rb` exercises image output, markdown formatting, missing-mode errors, and map-derived distro names.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/script/distro-tool -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/script/gen-i-reverse -->
# sources/sync-backup/git-lfs/script/gen-i-reverse

Purpose: generates a pseudo-translation file by reversing words in gettext `msgid` strings, useful for i18n layout/testing.

Important functions/state: global parser state `:idle`, `:copy`, `:msgid`, `:msgid_multi`, `:msgid_plural_multi`; `reset_state`; `translate`.

Control flow: validates input/output arguments, then streams a PO-like file line by line. It copies empty msgids, captures singular/plural msgids including xgotext backtick-delimited multiline strings, and fills empty `msgstr` entries with reversed translated text while preserving printf-style chunks beginning with `%`.

State/persistence behavior: writes the output file incrementally and stores current singular/plural message state in globals.

Dependencies/integration: used by localization/test tooling around generated gettext catalogs.

Risks: parser is intentionally narrow and uses globals. It assumes specific PO syntax and can silently omit unexpected line forms. It fixes nonstandard backtick strings from xgotext rather than implementing a complete PO parser.

Test signals: no direct tests in this subset; useful signals are generated msgstr entries, preserved placeholders, and valid output syntax.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/script/gen-i-reverse -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/script/hash-files -->
# sources/sync-backup/git-lfs/script/hash-files

Purpose: prints multiple cryptographic digest lines for one or more files in a stable order.

Important APIs/classes: `DIGESTS` maps OpenSSL digest names to output labels; `Hasher` initializes digest contexts, updates all digests per chunk, and formats BSD-style hash lines.

Control flow: requires Ruby 3+, iterates `ARGV`, reads each file in 64 KiB chunks, updates all digest contexts, collects formatted output, sorts first by digest order then filename, and prints.

State/persistence behavior: read-only over input files. All digest results are accumulated in memory as output lines.

Dependencies/integration: used by `script/upload` finalization to create a signed multi-hash asset manifest.

Risks: digest availability depends on OpenSSL/Ruby build support. Very large file sets produce in-memory result arrays, though each file is streamed.

Test signals: stable output order and correct digest labels are the main observable behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/script/hash-files -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/script/install-git-source -->
# sources/sync-backup/git-lfs/script/install-git-source

Purpose: small CircleCI macOS helper to build and install Git from a checked-out `git-source` directory at a requested ref.

Important commands: `git checkout "$1"`, `make --jobs=2`, and `make install`.

Control flow: changes into `git-source`, checks out the argument ref, builds with two jobs, installs, then returns to the parent directory.

State/persistence behavior: mutates the `git-source` checkout and installs Git into whatever prefix the Git build uses.

Dependencies/integration: used by macOS CI setups that need a specific Git version before running Git LFS tests.

Risks: no argument validation, no explicit `set -e`, and install permissions/prefix are inherited from the environment.

Test signals: downstream CI detects success by the installed Git version and subsequent test pass.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/script/install-git-source -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/script/install.sh -->
# sources/sync-backup/git-lfs/script/install.sh

Purpose: installs Git LFS binaries from the script directory into a chosen prefix and runs `git lfs install`.

Important behavior: prefix selection from `PREFIX`, `BOXEN_HOME`, default `/usr/local`, or `--local` for `$HOME/.local`; write-permission check; `install` of every `git*` file in the script directory.

Control flow: parse options, validate prefix writability, create `$prefix/bin`, remove existing `git-lfs*`, install matching binaries, append prefix bin to `PATH`, and run `git lfs install`.

State/persistence behavior: modifies the chosen bin directory, removes old Git LFS binaries there, and updates the user's global/system Git LFS filter configuration through `git lfs install`.

Dependencies/integration: distributed installer entrypoint for packaged Git LFS archives.

Risks: broad `rm -rf "$prefix/bin/git-lfs*"` can remove all matching files in prefix. The glob `git*` depends on script directory contents. Requires write permission and a functional Git.

Test signals: installed `git-lfs` on PATH and successful `git lfs install`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/script/install.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/script/lib/distro.rb -->
# sources/sync-backup/git-lfs/script/lib/distro.rb

Purpose: authoritative Ruby metadata and CLI implementation for supported package distribution targets.

Important APIs/classes: `DistroMap.builtin_map`, `DistroMap#distro_name_map`, `DistroMap#image_names`, `DistroMapProgram#image_names`, `#distro_markdown`, and `#run`.

Control flow: `builtin_map` defines source distro keys with package component, Docker image, package type, package tag, and equivalent PackageCloud distro names. Program mode parsing selects image-name output or markdown link output and returns status 2 for missing mode.

State/persistence behavior: no persistence. Output is deterministic based on insertion order of the map.

Dependencies/integration: used by package upload and release-note generation. `packagecloud.rb` uses `distro_name_map`; `upload` uses markdown output.

Risks: distro equivalents and EOL comments are manual release engineering data. Incorrect package tags/components lead to wrong package URLs or uploads. Markdown uses fixed amd64/x86_64 arch labels.

Test signals: `script/spec/distro_spec.rb` validates program outputs and derived maps against a fixture map.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/script/lib/distro.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/script/macos/manifest.json -->
# sources/sync-backup/git-lfs/script/macos/manifest.json

Purpose: manifest for macOS notarization tooling.

Important fields: `apple_id.password` reads from `DARWIN_DEV_PASS`; `notarize.path` targets `git-lfs`; `bundle_id` is `com.github.git-lfs`; `staple` is false.

Control flow: declarative JSON, not executable.

State/persistence behavior: no local state. It instructs notarization tooling how to submit the Git LFS binary and where to obtain credentials.

Dependencies/integration: pairs with macOS release/notarization scripts and CI secrets.

Risks: depends on environment secret naming and assumes the artifact path is exactly `git-lfs`. `staple: false` means notarization tickets are not stapled by this manifest.

Test signals: successful notarization submission in macOS release jobs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/script/macos/manifest.json -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/script/notarize -->
# sources/sync-backup/git-lfs/script/notarize

Purpose: submits a single artifact to Apple notarization without echoing credentials into CI logs.

Important command: `xcrun notarytool submit "$1" --apple-id "$DARWIN_DEV_USER" --password "$DARWIN_DEV_PASS" --team-id "$DARWIN_DEV_TEAM" --wait`.

Control flow: receives artifact path as `$1` and blocks until notarization completes.

State/persistence behavior: no repository writes. It sends artifact data and Apple credentials to Apple's notarization service.

Dependencies/integration: macOS release pipeline with `xcrun`, notarytool, and `DARWIN_DEV_*` environment secrets.

Risks: comment warns not to run on multi-user systems because secrets are passed as process arguments. No argument validation or retry behavior.

Test signals: notarytool exit status and notarization logs in CI.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/script/notarize -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/script/packagecloud.rb -->
# sources/sync-backup/git-lfs/script/packagecloud.rb

Purpose: uploads built `.rpm` and `.deb` packages under `repos/` to PackageCloud distro targets.

Important APIs/functions: `DistroMap#distro_name_map`, global `$client`, `$distro_id_map`, `distro_names_for`, `Packagecloud::Credentials`, `Packagecloud::Client`, and `Packagecloud::Package`.

Control flow: validates `PACKAGECLOUD_TOKEN`, loads `packagecloud-ruby`, constructs credentials, discovers package files, skips `repo-release`, maps each filename to equivalent distro names by substring pattern, caches distribution IDs, and uploads each package. Duplicate filename errors are ignored; other upload failures raise.

State/persistence behavior: no local writes beyond gem loading. Remote PackageCloud package state is mutated by uploads.

Dependencies/integration: release packaging pipeline, `script/lib/distro.rb`, PackageCloud credentials, and package naming conventions that include distro keys.

Risks: filename substring matching can misclassify packages if paths change. Duplicate handling depends on exact PackageCloud error JSON. Global variables make isolated testing harder.

Test signals: upload logs, PackageCloud package presence, and failure on missing distro IDs or non-duplicate API errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/script/packagecloud.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/script/spec/distro_spec.rb -->
# sources/sync-backup/git-lfs/script/spec/distro_spec.rb

Purpose: RSpec coverage for distro metadata formatting and derived maps.

Important APIs/functions: `test_map`, `DistroMapProgram#run`, `DistroMap#distro_name_map`, and `DistroMap#image_names`.

Control flow: builds a small fixture map, captures `stdout`/`stderr` with `StringIO`, and asserts `--image-names`, `--distro-markdown`, no-option error status, equivalent distro map, and image list.

State/persistence behavior: no persistence; tests operate entirely in memory.

Dependencies/integration: validates `script/lib/distro.rb`, and indirectly protects `script/upload` release body links and PackageCloud upload mapping.

Risks: fixture data intentionally differs from current builtin data, so tests cover formatting logic rather than current distro support. They assume Ruby hash insertion order.

Test signals: failing expectations indicate output formatting drift or option-handling changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/script/spec/distro_spec.rb -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/script/update-version -->
# sources/sync-backup/git-lfs/script/update-version

Purpose: release helper that updates Git LFS version declarations across Go, Debian, RPM, and Windows version metadata.

Important functions: `rfc822_datestamp`, `user_id`, `update_go`, `update_debian`, `update_rpm`, `update_versioninfo`, and `main`.

Control flow: validates `NEW-VERSION`, strips leading `v`, updates `config/version.go`, prepends a Debian changelog entry if needed, rewrites RPM `Version:`, and updates `versioninfo.json` major/minor/patch/product fields.

State/persistence behavior: writes four tracked files. Debian changelog uses a deterministic 14:29 UTC-ish timestamp and current Git committer identity.

Dependencies/integration: release process before packaging and upload; uses sed, ruby, git, date, and mktemp.

Risks: sed/ruby regexes assume simple numeric dotted versions and fixed file formats. Debian update is idempotent only by grep for `git-lfs ($version)`.

Test signals: git diff after running should show consistent version bumps and no duplicate Debian changelog entry.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/script/update-version -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/script/upload -->
# sources/sync-backup/git-lfs/script/upload

Purpose: orchestrates GitHub draft release creation/update, asset upload/download, final signing, body generation, and verification.

Important functions: `say`, `abort`, `uri_encode`, custom `curl`, `categorize_os`, `categorize_arch`, `categorize_asset`, `content_type`, `format_release_json`, `create_release`, `patch_release`, `release_files`, `finalize_body_message`, `filter_files`, `upload_assets`, `download_assets`, `verify_assets`, `extract_changelog`, `finalize`, `usage`, `sanity_check`, and `main`.

Control flow: parses `--inspect`, `--skip-verify`, and `--finalize`. Normal mode extracts changelog, generates a release body with PackageCloud links and SHA-256 hashes, creates or reuses a draft release, uploads new assets, then verifies downloaded signatures. Finalize mode downloads release assets, optionally opens a shell for inspection, regenerates signed hash manifests, patches the release body, uploads final signature assets, and verifies unless skipped.

State/persistence behavior: uses a temp workdir removed by trap, reads `bin/releases`, creates/patches GitHub releases, uploads assets to GitHub, downloads assets for verification, and generates signed manifests using local GPG keys.

Dependencies/integration: GitHub API, `GITHUB_TOKEN` or `.netrc`, curl, jq, ruby, shasum, gpg, optional sha3sum/b2sum, `script/distro-tool`, and `script/hash-files`.

Risks: release discovery searches by release name; repeated API listing can race or become slow. Filename globs encode supported asset patterns. Final signing depends on local GPG configuration. Duplicate asset filtering only compares names already present.

Test signals: successful draft/final release with expected labels/content types, signed manifests verifying after download, and body text with correct changelog/package/hash sections.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/script/upload -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/ssh/connection.go -->
# sources/sync-backup/git-lfs/ssh/connection.go

Purpose: manages long-lived pure-SSH pkt-line transfer connections, including lazy extra connections and OpenSSH control-master multiplexing.

Important APIs/types/functions: `SSHTransfer`, `NewSSHTransfer`, `startConnection`, `IsMultiplexingEnabled`, `Connection`, `ConnectionCount`, `SetConnectionCount`, `SetConnectionCountAtLeast`, `spawnConnection`, `setConnectionCount`, and `Shutdown`.

Control flow: `NewSSHTransfer` starts connection 0 immediately. `startConnection` builds the SSH command with `GetLFSExeAndArgs`, starts the subprocess, wraps stdin/stdout in pkt-line support, negotiates protocol version, and annotates failures with stderr. Additional connections are represented by nil slots and spawned lazily by `Connection(n)` under a double-checked lock.

State/persistence behavior: in-memory state tracks connection slots, mutex, config environments, metadata, operation, multiplex enabled flag, and control path. Shrinking connection counts sends `quit` and waits. Setting count to zero shuts down connection 0 and clears control path.

Dependencies/integration: uses `subprocess.ExecCommand`, pktline, tracing, `config.Environment`, and command construction in `ssh.go`.

Risks: connection slot 0 is preserved when reducing to nonzero counts. Lazy nil slots mean count is not equal to live subprocess count. Failure paths must close pipes and wait to avoid leaked processes.

Test signals: integration tests using `lfs-ssh-echo` and SSH multiplexing validate control path creation/reuse and shutdown behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/ssh/connection.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/ssh/pktline.go -->
# sources/sync-backup/git-lfs/ssh/pktline.go

Purpose: defines the minimal pkt-line interface used by Git LFS SSH transfer and adds optional packet tracing.

Important APIs/types/functions: `pktlineReader`, `Pktline` interface, `TraceablePktline`, `ReadPacketList`, `ReadPacketTextWithLength`, `WritePacket`, `WritePacketText`, `WriteDelim`, and `WriteFlush`.

Control flow: normal `pktline.Pktline` instances are used directly unless `GIT_TRACE_PACKET` is enabled, in which case `TraceablePktline` logs readable packet direction/length and delegates to the underlying pktline implementation. Binary `WritePacket` is intentionally not traced.

State/persistence behavior: no persistence; state is the connection id and underlying pktline pointer.

Dependencies/integration: wraps `github.com/git-lfs/pktline` and `tracerx`. `pktlineReader` bridges response binary data into an `io.Reader`.

Risks: `pktlineReader` type-asserts to either `*pktline.Pktline` or `*TraceablePktline`; any third implementation of `Pktline` would panic. Trace output may include protocol text but avoids binary payloads.

Test signals: packet tracing can be observed under `GIT_TRACE_PACKET`; protocol tests indirectly depend on correct delimiter/flush logging and delegation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/ssh/pktline.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/ssh/protocol.go -->
# sources/sync-backup/git-lfs/ssh/protocol.go

Purpose: implements the Git LFS SSH pkt-line protocol framing, version negotiation, command sending, and status/data/line response parsing.

Important APIs/types/functions: `PktlineConnection`, `Lock`, `Unlock`, `Start`, `End`, `negotiateVersion`, `SendMessage`, `SendMessageWithLines`, `SendMessageWithData`, `ReadStatus`, `ReadStatusWithData`, and `ReadStatusWithLines`.

Control flow: `Start` negotiates `version=1`: read capabilities, send `version 1`, then require status 200. Send methods write a command, args, optional delimiter plus lines/data, then flush. Read methods require the first packet to be `status NNN`, collect args before a delimiter, then either return a streaming data reader or text lines until flush.

State/persistence behavior: connection state consists of stdin/stdout pipes, subprocess, mutex, and pktline wrapper. `End` sends `quit`, reads status, closes pipes, and waits for the process.

Dependencies/integration: used by SSH transfer and SSH lock client. Depends on `subprocess.Cmd`, translated protocol errors, and pktline framing semantics.

Risks: callers of `ReadStatusWithData` must exhaust the returned reader before further reads. `SendMessageWithData` stops on any read error and then flushes without distinguishing EOF from non-EOF errors, so upstream readers should be reliable.

Test signals: failures appear as protocol errors during SSH transfer, lock commands, or version negotiation.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/ssh/protocol.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/ssh/ssh.go -->
# sources/sync-backup/git-lfs/ssh/ssh.go

Purpose: constructs SSH executable names and arguments for Git LFS authentication/transfer commands across OpenSSH, plink, tortoiseplink, and custom shell commands.

Important APIs/types/functions: `sshVariant`, `SSHMetadata`, `FormatArgs`, `GetLFSExeAndArgs`, `parseShellCommand`, `findVariant`, `autodetectVariant`, `getVariant`, `findRuntimeDir`, `getControlDir`, `GetExeAndArgs`, `defaultSSHCmd`, and `sshOptPrefixRE`.

Control flow: command selection honors `GIT_SSH_COMMAND` before `GIT_SSH`, then `core.sshcommand`, then `ssh`. Variant is selected by `GIT_SSH_VARIANT`, `ssh.variant`, or basename autodetection. Args add tortoise `-batch`, optional OpenSSH multiplexing options/control path, variant-specific port flags, host separator/stripping for option-looking hostnames, then the remote command.

State/persistence behavior: may create a temporary control socket directory under `XDG_RUNTIME_DIR`, `/tmp` on Darwin, or default temp. It otherwise only returns command data.

Dependencies/integration: used by `connection.go`, URL parsing in `lfshttp`, shell quoting in `subprocess`, and tests covering option injection.

Risks: `GIT_SSH_COMMAND` and `core.sshcommand` require shell wrapping, so quoting correctness is security-sensitive. Hostnames beginning with dashes are guarded with `--` for OpenSSH and stripped for other variants to prevent option injection.

Test signals: `ssh_test.go` has broad table-style coverage for variants, ports, multiplexing, precedence, shell commands, custom SSH, and malicious option-like host/path input.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/ssh/ssh.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/ssh/ssh_test.go -->
# sources/sync-backup/git-lfs/ssh/ssh_test.go

Purpose: verifies SSH command construction and SSH URL metadata handling.

Important tests: `TestSSHGetLFSExeAndArgs`, many `TestSSHGetExeAndArgs*` cases for OpenSSH/plink/tortoiseplink/simple variants, multiplexing master/extra/no-multiplexing cases, command precedence tests, custom SSH tests, invalid option-like host/path tests, and bare SSH URL parsing.

Control flow: tests construct `lfshttp.Client` instances with controlled OS/Git environment maps, fill `ssh.SSHMetadata`, call `GetExeAndArgs` or `GetLFSExeAndArgs`, normalize with `FormatArgs` when needed, and assert exact executable/argument arrays.

State/persistence behavior: no filesystem persistence except temporary control paths generated in multiplexing cases. Tests assert non-empty control path or exact provided path.

Dependencies/integration: covers `lfshttp.EndpointFromSshUrl`, `EndpointFromBareSshUrl`, `ssh.FormatArgs`, and environment/config precedence.

Risks: exact argument assertions are intentionally brittle; legitimate command-line behavior changes need test updates. Multiplexing tests avoid platform-specific socket validation and focus on generated args.

Test signals: protects against regressions in command precedence, port flag selection, OpenSSH control options, shell wrapping, and option-injection vulnerabilities.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/ssh/ssh_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/buffered_cmd.go -->
# sources/sync-backup/git-lfs/subprocess/buffered_cmd.go

Purpose: defines `BufferedCmd`, a convenience wrapper for subprocesses with buffered stdin/stdout/stderr handles.

Important APIs/types: `stdoutBufSize` constant and `BufferedCmd` struct embedding `*Cmd` with `Stdin`, `Stdout`, and `Stderr` fields.

Control flow: no functions in this file; instances are constructed by `BufferedExec` and `StdoutBufferedExec`.

State/persistence behavior: holds pipe handles and readers for a running subprocess. Persistence is external to the child process.

Dependencies/integration: part of the `subprocess` package used by Git LFS helpers that need interactive child processes.

Risks: consumers must still call `Wait`/close paths through `Cmd` to avoid process and pipe leaks.

Test signals: indirect through callers; no direct unit tests for this struct.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/buffered_cmd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/cmd.go -->
# sources/sync-backup/git-lfs/subprocess/cmd.go

Purpose: wraps `exec.Cmd` to centralize tracing and pipe cleanup.

Important APIs/types/functions: `Cmd`, `Run`, `Start`, `Output`, `CombinedOutput`, `StdoutPipe`, `StderrPipe`, `StdinPipe`, `Wait`, `trace`, and `newCmd`.

Control flow: execution methods trace before delegating to `exec.Cmd`. Pipe factory methods append created pipes to an internal slice. `Wait` closes all recorded pipes before waiting on the child process.

State/persistence behavior: in-memory tracking of pipes associated with a command. Child process side effects are determined by the command.

Dependencies/integration: used by all subprocess spawning in Git LFS, including SSH transfer.

Risks: pipe methods append even if `exec.Cmd` returns an error, which can append nil closers if a future Go version does so. Closing pipes before `Wait` is intentional but can surprise code expecting to read after wait.

Test signals: no direct tests; subprocess behavior and tracing are exercised throughout integration tests.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/cmd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/path.go -->
# sources/sync-backup/git-lfs/subprocess/path.go

Purpose: custom executable lookup derived from Go's `exec.LookPath` behavior, with platform-specific extension handling.

Important API: `LookPath(file string)`.

Control flow: if the file contains a path separator, it checks that path directly with `findExecutable`. Otherwise it iterates `PATH`, treats empty Unix path entries as `.`, skips empty Windows entries, joins each dir with the file, and returns the first executable.

State/persistence behavior: reads `PATH`; no writes.

Dependencies/integration: used by `ExecCommand` on all platforms before assigning `cmd.Path`.

Risks: behavior intentionally diverges by platform. On Unix, empty PATH elements execute from current directory; on Windows they do not. It returns `exec.ErrNotFound` rather than preserving detailed permission errors.

Test signals: platform command spawning and Windows extension lookup indirectly validate this path logic.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/path.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/path_nix.go -->
# sources/sync-backup/git-lfs/subprocess/path_nix.go

Purpose: Unix implementation of executable detection for `LookPath`.

Important APIs/functions: `findPathExtensions` returns nil; `findExecutable` checks `os.Stat`, not-directory, and any execute bit.

Control flow: direct stat of candidate path. A regular executable path is returned; missing/stat errors propagate; non-executable or directory returns `os.ErrPermission`.

State/persistence behavior: read-only filesystem metadata inspection.

Dependencies/integration: compiled on non-Windows platforms and used by `subprocess.ExecCommand`.

Risks: execute permission check uses any execute bit (`0111`) rather than effective user access evaluation. Symlink handling is delegated to `os.Stat`.

Test signals: command execution failures on Unix would surface if lookup incorrectly rejects executable tools.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/path_nix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/path_windows.go -->
# sources/sync-backup/git-lfs/subprocess/path_windows.go

Purpose: Windows implementation of executable lookup with `PATHEXT` support.

Important functions: `chkStat`, `hasExt`, `findExecutable`, and `findPathExtensions`.

Control flow: `findPathExtensions` normalizes `PATHEXT` entries to lowercase dotted extensions or defaults to `.com`, `.exe`, `.bat`, `.cmd`. `findExecutable` checks the exact path if extensions are disabled or the filename already has an extension, then tries each extension. `chkStat` rejects directories.

State/persistence behavior: reads `PATHEXT` and filesystem metadata only.

Dependencies/integration: compiled only on Windows for `subprocess.LookPath`.

Risks: lowercasing `PATHEXT` assumes case-insensitive filesystem behavior. `hasExt` must distinguish drive/path separators from file extensions.

Test signals: Windows CI command spawning and test tool discovery validate this behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/path_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/subprocess.go -->
# sources/sync-backup/git-lfs/subprocess/subprocess.go

Purpose: central subprocess helper package for command execution, shell quoting, trace logging, and sanitized environment construction.

Important APIs/functions: `BufferedExec`, `StdoutBufferedExec`, `SimpleExec`, `Output`, `ShellQuoteSingle`, `ShellQuote`, `FormatForShell`, `FormatForShellQuotedArgs`, `FormatPercentSequences`, `Trace`, `quotedArgs`, `fetchEnvironment`, `fetchEnvironmentInternal`, and `ResetEnvironment`.

Control flow: exec helpers construct `Cmd`, create pipes/readers, start processes, and return wrappers. `Output` normalizes successful stdout trimming and expands `exec.ExitError` into a command/error-output message. Quoting helpers produce shell-safe single-quoted args. Environment fetching caches `os.Environ` minus `GIT_TRACE` and `GIT_INTERNAL_SUPER_PREFIX`.

State/persistence behavior: package-level cached environment guarded by `envMu`; resettable for tests or environment changes.

Dependencies/integration: used broadly by Git LFS for Git commands, SSH commands, and custom tool execution.

Risks: `FormatForShell` intentionally does no quoting and should be avoided with untrusted args. Cached environment can become stale unless `ResetEnvironment` is called after env changes. `Output` discards stdout on nonzero exit by design.

Test signals: `subprocess_test.go` covers quoting, shell command formatting, and percent sequence replacement.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/subprocess.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/subprocess_nix.go -->
# sources/sync-backup/git-lfs/subprocess/subprocess_nix.go

Purpose: non-Windows subprocess constructor.

Important API: `ExecCommand(name string, arg ...string)`.

Control flow: creates `exec.Command`, resolves the executable with package `LookPath`, assigns sanitized cached environment, wraps in `Cmd`, and returns.

State/persistence behavior: no direct persistence; reads environment through `fetchEnvironment`.

Dependencies/integration: all non-Windows command execution in Git LFS uses this path.

Risks: returns early if lookup fails, so callers do not get a partially constructed command. Environment filtering removes trace and super-prefix variables from all child commands.

Test signals: Unix CI and integration tests exercise command discovery/execution.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/subprocess_nix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/subprocess_test.go -->
# sources/sync-backup/git-lfs/subprocess/subprocess_test.go

Purpose: unit tests for shell quoting and command formatting utilities.

Important test types/functions: `ShellQuoteTestCase`, `TestShellQuote`, `FormatForShellQuotedArgsTestCase`, `TestFormatForShellQuotedArgs`, `FormatForShellTestCase`, `TestFormatForShell`, `FormatPercentSequencesTestCase`, and `TestFormatPercentSequences`.

Control flow: table-driven tests assert exact quoting for spaces, backslashes, quotes, mixed quotes, shell-wrapped command strings, and percent replacement with shell quoting.

State/persistence behavior: no persistence.

Dependencies/integration: protects `ssh.FormatArgs`, merge-tool command formatting, and any shell invocation built from these helpers.

Risks: tests do not execute a shell; they validate string construction only. `FormatForShell` is deliberately unquoted and tested as such.

Test signals: failures indicate changed quoting contracts that can affect custom SSH commands or file-name handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/subprocess_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/subprocess_windows.go -->
# sources/sync-backup/git-lfs/subprocess/subprocess_windows.go

Purpose: Windows subprocess constructor.

Important API: `ExecCommand(name string, arg ...string)`.

Control flow: creates `exec.Command`, resolves executable via package `LookPath`, sets `SysProcAttr.HideWindow = true`, assigns sanitized cached environment, wraps in `Cmd`, and returns.

State/persistence behavior: no persistence; influences child-process window behavior and environment.

Dependencies/integration: all Windows Git LFS subprocess execution goes through this path.

Risks: hidden-window behavior is Windows-specific and important for GUI/no-console use. Command lookup relies on `PATHEXT` handling in `path_windows.go`.

Test signals: Windows CI/integration tests cover executable lookup and hidden child execution behavior indirectly.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/subprocess/subprocess_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/Makefile -->
# sources/sync-backup/git-lfs/t/Makefile

Purpose: builds integration-test helper binaries and runs shell test suites.

Important targets/variables: `TEST_CMDS`, `TEST_SRCS`, `TEST_API_SRCS`, `test-commands`, `test`, per-test shell targets, `clean`, pattern rule `../bin/%$X : cmd/%.go`, and `../bin/git-lfs-test-server-api$X`.

Control flow: detects Windows executable suffix, lists all Go helper tools, builds them with `go build`, runs `testenv.sh` setup, executes `prove` over `t-*.sh`, then shuts down. Per-test targets run one script with verbose prove.

State/persistence behavior: creates binaries under `../bin`, removes `remote` and test count/lock files, and uses `GOTOOLCHAIN=local` to prevent automatic Go downloads.

Dependencies/integration: called by `script/cibuild` and local integration-test workflows.

Risks: helper list must stay in sync with `t/cmd`. Cleanup is limited to known test state and binaries.

Test signals: successful target proves helper compilation and shell integration tests pass.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/git-credential-lfsnoop.go -->
# sources/sync-backup/git-lfs/t/cmd/git-credential-lfsnoop.go

Purpose: placeholder credential helper binary built for test tooling.

Important API: empty `main`.

Control flow: exits successfully without reading input or producing output.

State/persistence behavior: no state and no persistence.

Dependencies/integration: included in `t/Makefile` helper builds under the `testtools` build tag, likely used where the presence of a credential helper executable matters.

Risks: any test expecting behavior from this helper would fail silently because it intentionally does nothing.

Test signals: build success and zero exit status.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/git-credential-lfsnoop.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/git-credential-lfstest.go -->
# sources/sync-backup/git-lfs/t/cmd/git-credential-lfstest.go

Purpose: test credential helper implementing Git credential `get`, `store`, and `erase` behavior for HTTP auth scenarios.

Important APIs/types/functions: `credential`, `Serialize`, `fill`, `discoverCapabilities`, `credsForHostAndPath`, `parseOneCredential`, `credsFromFilename`, `log`, and `firstEntryForKey`.

Control flow: `main` dispatches by command. `get` parses key/value stdin into multi-value maps, resolves a credentials file by host or host/path under `CREDSDIR`, supports Windows drive path rewriting, filters credentials by advertised capabilities and username/state, optionally validates `wwwauth[]`, and emits credential key/value pairs plus capabilities. `store` and `erase` only log.

State/persistence behavior: reads static credential files; does not write credential stores. Uses `CREDSDIR` and `LFS_TEST_CREDS_WWWAUTH` environment variables.

Dependencies/integration: used by integration tests for Basic, bearer/authtype, stateful multistage auth, path-specific credentials, and www-authenticate propagation.

Risks: file format is compact and colon-delimited, so credentials containing colons are not supported. Scanner line length defaults apply.

Test signals: stderr logs `CREDS RECV/SEND`; exit status and stdout credentials drive client auth behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/git-credential-lfstest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfs-askpass.go -->
# sources/sync-backup/git-lfs/t/cmd/lfs-askpass.go

Purpose: deterministic askpass helper for integration tests.

Important API: `main`.

Control flow: joins prompt args, returns username when prompt contains `Username`, password when prompt contains `Password`, and allows overrides via `LFS_ASKPASS_USERNAME` and `LFS_ASKPASS_PASSWORD`.

State/persistence behavior: reads environment only; no persistence.

Dependencies/integration: used by tests that exercise Git credential prompts or HTTP auth fallback.

Risks: prompt matching is substring-based and case-sensitive.

Test signals: stdout contains the selected answer.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfs-askpass.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfs-ssh-echo.go -->
# sources/sync-backup/git-lfs/t/cmd/lfs-ssh-echo.go

Purpose: fake SSH executable for integration tests, emulating SSH argument parsing, multiplex control path checks, Git command forwarding, and LFS auth JSON responses.

Important APIs/types/functions: `sshResponse`, `shell`, `spawnCommand`, `checkSufficientArgs`, and `main`.

Control flow: parses optional OpenSSH control-master/control-path args, optional `-p`, optional `--`, validates host `git@127.0.0.1`, then inspects the remote command. `git-lfs-transfer`, `git-upload-pack`, and `git-receive-pack` are executed through a shell. `git-lfs-authenticate` returns JSON with an LFS href and optional expired `expires_at`/`expires_in` for special repos.

State/persistence behavior: creates/removes a control path file for multiplex master mode and reads no persistent repo state directly except through spawned commands.

Dependencies/integration: validates SSH command construction, auth endpoint generation, transfer protocol, and multiplexing behavior.

Risks: relies on positional args; malformed input exits with diagnostic. Shell execution is acceptable here because the tool is test-only.

Test signals: exact stderr errors, generated JSON, and successful forwarded Git/LFS subprocess execution.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfs-ssh-echo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfs-ssh-proxy-test.go -->
# sources/sync-backup/git-lfs/t/cmd/lfs-ssh-proxy-test.go

Purpose: minimal executable used to prove SSH proxy command invocation.

Important API: `main`.

Control flow: prints `SSH PROXY TEST called` and exits.

State/persistence behavior: none.

Dependencies/integration: used by tests that configure proxy-like SSH commands.

Risks: no argument validation; it is intentionally only a sentinel.

Test signals: stdout string confirms the configured command was invoked.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfs-ssh-proxy-test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-badpathcheck.go -->
# sources/sync-backup/git-lfs/t/cmd/lfstest-badpathcheck.go

Purpose: deliberately suspicious test command for path/execution safety tests.

Important API: `main`.

Control flow: prints `exploit` to stdout and stderr, then attempts to create a file named `exploit`.

State/persistence behavior: may create `./exploit` in the current directory.

Dependencies/integration: used to verify Git LFS does not execute untrusted path components or bad hooks/tools unexpectedly.

Risks: intentionally has side effects; should only be run in isolated test directories.

Test signals: presence or absence of output/file indicates whether a path execution vulnerability was triggered.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-badpathcheck.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-caseinverterextension.go -->
# sources/sync-backup/git-lfs/t/cmd/lfstest-caseinverterextension.go

Purpose: test Git LFS pointer extension that swaps character case during clean/smudge.

Important functions/state: `gitDir`, `main`, `openLog`, and `logErrorAndExit`.

Control flow: validates args are `clean -- <path>` or `smudge -- <path>`, requires `.git` to exist and be a directory, optionally logs operation/path to `LFSTEST_EXT_LOG`, reads stdin rune by rune, swaps upper/lowercase Unicode runes, writes stdout, and exits.

State/persistence behavior: reads `.git` metadata, appends to optional log file, otherwise streams data only.

Dependencies/integration: used by integration tests for extension filters and clean/smudge behavior.

Risks: validates `.git` in current working directory only, so tests must run from repo root. Unicode case conversion may expand some runes but writes strings directly.

Test signals: transformed content and optional log entries.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-caseinverterextension.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-count-tests.go -->
# sources/sync-backup/git-lfs/t/cmd/lfstest-count-tests.go

Purpose: coordinates integration-test server lifetime by maintaining a shared active-test count.

Important APIs/functions: `countFn`, `main`, `acquire`, `release`, `callWithCount`, `path`, and `fatal`.

Control flow: acquires an exclusive lock file with a 5 second timeout. With no args it prints the current count. `increment` starts `lfstest-gitserver` when transitioning from zero to one and increments otherwise. `decrement` decrements while count remains above one, or posts `/shutdown` to the server and writes zero when the last test exits.

State/persistence behavior: stores `test_count` and `test_count.lock` adjacent to `LFSTEST_DIR`, creates `gitserver.log`, starts a background server process, and reads `LFS_URL_FILE` for shutdown.

Dependencies/integration: invoked by shell test setup/teardown to share one server across parallel tests.

Risks: stale lock files can block for the timeout. `fatal` attempts release even when acquire may have failed. Shutdown POST ignores errors after reading URL.

Test signals: count file values, server process/log existence, and successful shutdown when count reaches zero.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-count-tests.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-customadapter.go -->
# sources/sync-backup/git-lfs/t/cmd/lfstest-customadapter.go

Purpose: test custom transfer adapter that proxies upload/download requests to normal LFS storage URLs.

Important APIs/types/functions: `main`, `writeToStderr`, `sendResponse`, `sendTransferError`, `sendProgress`, `performDownload`, `performUpload`, and protocol structs `request`, `action`, `transferResponse`, `progressResponse`, `transferError`.

Control flow: reads line-oriented JSON events from stdin. `init` acknowledges; `download` performs authenticated GET to `action.href`, copies to a temp file with progress callbacks, and returns a completion path; `upload` opens the source path, builds an authenticated PUT with headers/content length or chunked transfer, streams with progress callbacks, and returns completion; `terminate` logs.

State/persistence behavior: creates temporary download files and reads upload source files. Network side effects mutate the test LFS server storage.

Dependencies/integration: exercises Git LFS custom transfer adapter protocol, `lfsapi.Client`, and `tools.CopyWithCallback`/`NewBodyWithCallback`.

Risks: if upload auth fails with nil response, `res.StatusCode` can panic in one error path. The terminate case breaks only the switch, so the scanner loop continues until stdin closes.

Test signals: JSON progress/complete events, stderr protocol logs, and server-stored object content.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-customadapter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-genrandom.go -->
# sources/sync-backup/git-lfs/t/cmd/lfstest-genrandom.go

Purpose: emits cryptographically random bytes for integration tests, optionally base64/base64url encoded.

Important behavior: parses `--base64` or `--base64url`, optional byte count, defaults to maximum `uint64`, reads 32-byte chunks from `crypto/rand`, encodes if requested, and writes exactly up to the requested count.

Control flow: validates at most one size arg after option, loops while `count > 0`, handles read/write errors with distinct exit codes.

State/persistence behavior: writes random data to stdout only.

Dependencies/integration: used by shell tests needing arbitrary object data.

Risks: default unbounded output can run indefinitely if no size is supplied. Encoded output count is in output bytes, not raw bytes.

Test signals: exit status, output length, and encoding alphabet.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-genrandom.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-getnumcpu.go -->
# sources/sync-backup/git-lfs/t/cmd/lfstest-getnumcpu.go

Purpose: prints Go's detected CPU count for shell tests.

Important API: `main` calls `runtime.NumCPU`.

Control flow: single print with no newline.

State/persistence behavior: none.

Dependencies/integration: allows shell tests to adapt parallelism or expectations to the runtime.

Risks: value reflects Go runtime/container view, not necessarily physical CPUs.

Test signals: stdout integer.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-getnumcpu.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-gitserver.go -->
# sources/sync-backup/git-lfs/t/cmd/lfstest-gitserver.go

Purpose: comprehensive in-process HTTP/HTTPS Git and Git LFS test server used by integration tests.

Important APIs/types/functions: server bootstrap in `main`; LFS structs `lfsObject`, `lfsLink`, `lfsError`; handlers `lfsHandler`, `lfsBatchHandler`, `storageHandler`, `verifyHandler`, `gitHandler`, `locksHandler`, `redirect307Handler`, `limitsHandler`; lock structs `Lock`, `LockRequest`, `LockList`, `VerifiableLockList`; storage type `lfsStorage`; auth helpers `extractAuth`, `skipIfBadAuth`, `missingRequiredCreds`; TLS helpers `generateCARootCertificates`, `generateClientCertificates`, `CertTemplate`, and `CreateCert`.

Control flow: starts HTTP, TLS, and client-cert TLS `httptest` servers on one mux, writes URL/cert/key paths to state files, and blocks until `/shutdown`. Requests under `/info/lfs` go to LFS batch/lock handlers after accept/content-type/auth checks. Other Git requests are forwarded to `git http-backend`. Storage endpoints implement PUT/GET/HEAD/PATCH, including retries, rate limits, range resume, gzip/zstd encoding, TUS uploads, corruption, redirects, and status injection triggered by magic object contents.

State/persistence behavior: in-memory maps store complete/incomplete LFS objects, locks, retry counters, rate-limit tokens, expired-action state, and verify counts. State files expose URLs/certs to shell tests; Git repository data lives under `LFSTEST_DIR` and is served through `git http-backend`.

Dependencies/integration: central fixture for batch API, storage API, locks API, auth, netrc, custom transfers, chunked/TUS transfers, redirects, retry logic, hash-algorithm handling, TLS/client-cert tests, and Git smart HTTP.

Risks: large mutable global state means tests must isolate repo names/OIDs. Some branches call `log.Fatal`, killing the whole server. Lock pagination appears to cap size with `min(len(locks), 3)` instead of requested limit, so behavior is fixture-specific.

Test signals: integration tests observe HTTP status codes, LFS JSON bodies, stored object data, locks, retry behavior, logs, and generated cert/url files.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-gitserver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-nanomtime.go -->
# sources/sync-backup/git-lfs/t/cmd/lfstest-nanomtime.go

Purpose: prints a file modification timestamp with nanosecond precision.

Important API: `main`.

Control flow: requires one path arg, stats it, then prints `<unix>.<nanoseconds padded to 9 digits>`.

State/persistence behavior: read-only filesystem stat.

Dependencies/integration: used by shell tests that need precise mtime comparisons across platforms.

Risks: filesystem timestamp resolution may be lower than nanoseconds despite Go's representation.

Test signals: stdout timestamp or distinct exit codes for usage/stat failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-nanomtime.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-realpath.go -->
# sources/sync-backup/git-lfs/t/cmd/lfstest-realpath.go

Purpose: canonicalizes a path similarly to `realpath`, while tolerating missing trailing components.

Important functions: `canonicalize` and `main`.

Control flow: converts the argument to an absolute path, then repeatedly tries `filepath.EvalSymlinks` on the existing left side. If a component is missing, it walks left upward and accumulates the unresolved suffix on the right until an existing prefix can be canonicalized, then rejoins.

State/persistence behavior: read-only filesystem metadata inspection.

Dependencies/integration: shell tests use it for symlink/canonical path comparisons where the final path may not exist yet.

Risks: loop correctness depends on eventually finding an existing ancestor. Permission errors abort, while nonexistence is tolerated.

Test signals: stdout canonical absolute path and exit codes for bad usage/abs/canonicalization failures.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-realpath.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-standalonecustomadapter.go -->
# sources/sync-backup/git-lfs/t/cmd/lfstest-standalonecustomadapter.go

Purpose: standalone custom transfer adapter that copies uploads/downloads to a local backup directory instead of proxying HTTP storage.

Important APIs/types/functions: `backupDir`, `main`, `writeToStderr`, `sendResponse`, `sendTransferError`, `sendProgress`, `performCopy`, `performDownload`, `performUpload`, and custom adapter protocol structs.

Control flow: requires `TEST_STANDALONE_BACKUP_PATH`, logs arguments, reads line-oriented JSON events. Upload copies request path to `<backupDir>/<oid>` with progress events. Download copies from backup to a temp file and returns the temp path. Init and terminate are acknowledged/logged.

State/persistence behavior: persists object bytes as files in the configured backup directory and creates temp download files.

Dependencies/integration: tests standalone custom transfer mode and progress reporting using `tools.CopyWithCallback`.

Risks: backup path is global and must be isolated by tests. Terminate only breaks the switch, not the scanner loop. Existing backup files are overwritten by `os.Create`.

Test signals: JSON complete/progress events, backup file contents, and stderr logs.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-standalonecustomadapter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-testutils.go -->
# sources/sync-backup/git-lfs/t/cmd/lfstest-testutils.go

Purpose: command-line bridge exposing Go test utility repo helpers to shell tests.

Important APIs/types/functions: `TestUtilRepoCallback`, `main`, and `AddCommits`.

Control flow: dispatches subcommands, currently `addcommits`. It verifies the current directory contains `.git`, wraps it as a util `Repo`, reads JSON `[]*CommitInput` from stdin, calls `repo.AddCommits`, and writes JSON `[]*CommitOutput` to stdout.

State/persistence behavior: mutates the current Git repository by adding commits/files/tags/branches according to JSON input. Does not call `Cleanup` because shell tests own the repo.

Dependencies/integration: imports `t/cmd/util` to share Go repo-construction logic with shell tests.

Risks: refuses to run outside repo root, but still modifies the current repo directly. JSON errors or Git failures exit with nonzero codes.

Test signals: stdout commit metadata and repository history changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/lfstest-testutils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/util/testutils.go -->
# sources/sync-backup/git-lfs/t/cmd/util/testutils.go

Purpose: reusable Go utilities for creating and manipulating Git LFS test repositories.

Important APIs/types/functions: `RepoType`, `RepoCreateSettings`, `RepoCallback`, `Repo`, `NewRepo`, `NewBareRepo`, `WrapRepo`, `RunGitCommand`, `FileInput`, `CommitInput`, `CommitOutput`, `Repo.AddCommits`, `Repo.AddRemote`, `PlaceholderDataReader`, and sort helpers `RefsByName`, `WorktreesByName`, `WrappedPointersByOid`, `PointersByOid`.

Control flow: init prepends the checkout `bin` directory to PATH. Repo creation initializes temp Git repos, configures user identity, and constructs Git LFS config/filter/filesystem helpers. `AddCommits` checks out/creates branches, performs merges when requested, writes LFS pointer files and media objects via the clean filter, commits at optional dates/identities, creates annotated tags, and returns commit summaries.

State/persistence behavior: creates temp repos and bare remotes, writes `.git/lfs/objects`, pointer files, commits, tags, and remotes. `Cleanup` removes temp repo/gitdir trees and nested remotes while avoiding deletion from inside the target directory.

Dependencies/integration: used by Go tests and `lfstest-testutils`; depends on Git CLI plus Git LFS config/fs/lfs/git packages.

Risks: global deterministic random source is shared and not locked. `RunGitCommand` shells out without custom env isolation. `Cleanup` uses prefix checks that can be imprecise for similarly prefixed paths.

Test signals: generated repositories with expected commits, parents, tags, LFS pointer OIDs, and deterministic placeholder content.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/cmd/util/testutils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/fixtures/completions/git-lfs-completion.bash -->
# sources/sync-backup/git-lfs/t/fixtures/completions/git-lfs-completion.bash

Purpose: bash completion fixture for Git LFS, generated in Cobra-style completion protocol format and used by tests.

Important functions: `__git-lfs_debug`, `__git-lfs_init_completion`, `__git-lfs_get_completion_results`, `__git-lfs_process_completion_results`, `__git-lfs_extract_activeHelp`, `__git-lfs_handle_completion_types`, `__git-lfs_handle_standard_completion_case`, `__git-lfs_handle_special_char`, `__git-lfs_format_comp_descriptions`, `__start_git-lfs`, and `_git_lfs`.

Control flow: completion setup initializes `cur/prev/words/cword`, rewrites `git lfs` invocations to `git-lfs`, calls `git-lfs __completeNoDesc` via eval, separates output from the trailing directive, applies directive bits for nospace, no file completion, file-extension filtering, directory filtering, and keep-order, then builds `COMPREPLY` with description formatting and active help rendering.

State/persistence behavior: no persistence except optional debug appends to `BASH_COMP_DEBUG_FILE`. It mutates shell variables and completion options.

Dependencies/integration: depends on bash-completion helpers `_init_completion`, `_get_comp_words_by_ref`, `_filedir`, `compopt`, and the Git LFS binary's completion protocol.

Risks: uses `eval` to invoke the completion request, so quoting of words is sensitive. Bash version differences affect `nosort`, prompt rendering, and `compopt` behavior.

Test signals: shell completion tests can assert `COMPREPLY`, directive behavior, active help, special `:`/`=` handling, and registration for `git-lfs`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/fixtures/completions/git-lfs-completion.bash -->
