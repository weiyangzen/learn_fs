# Research Group subset-b-009757

This grouped report covers the exact source files assigned to `subset-b-009757`. Each file section is bounded by `BEGIN_FILE_RESEARCH` / `END_FILE_RESEARCH` markers so the reconciliation lane can split the content into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/yandex/yandex.go -->
# sources/user-network-fs/rclone/backend/yandex/yandex.go

Purpose: implements the rclone Yandex Disk backend, registering `yandex` with OAuth configuration, Yandex-specific options, REST clients, pacing, object metadata, uploads, downloads, server-side copy/move, public links, cleanup, and quota reporting. The main exported implementation types are `Options`, `Fs`, and `Object`; interface assertions cover `fs.Fs`, `fs.Purger`, `fs.Copier`, `fs.Mover`, `fs.DirMover`, `fs.PublicLinker`, `fs.CleanUpper`, `fs.Abouter`, `fs.Object`, and `fs.MimeTyper`.

Important flow: `NewFs` parses config, upgrades old OAuth token type, optionally spoofs an official Yandex user agent, constructs the root path as `disk:/...`, configures `rest.Client` with `errorHandler`, and detects whether the root is actually a file. Listing pages through `/resources` with limit/offset and maps Yandex resource records into rclone `Dir` or `Object` entries. Writes use a two-step upload URL lookup then `PUT`; reads use a two-step download URL lookup then `GET`. Delete/copy/move may return 202 async operations, which are polled by `waitForJob` until success or timeout.

State and persistence: the backend persists configuration through rclone config only; object modtime is persisted remotely in Yandex custom property `rclone_modified`, falling back to the Yandex `Modified` timestamp. `Fs` keeps in-memory root, disk-root, pacer, REST client, and config info. Hash support is MD5 when returned by metadata. Risks include Yandex API error-name coupling, async polling latency, path encoding edge cases around colons and `disk:` prefixes, custom-property modtime failures after upload, and `Hash` returning cached `md5sum` without forcing metadata refresh. Tests are integration-only via `yandex_test.go`, so unit coverage for error handling and async paths is limited.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/yandex/yandex.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/yandex/yandex_test.go -->
# sources/user-network-fs/rclone/backend/yandex/yandex_test.go

Purpose: declares the Yandex backend integration test entry point. `TestIntegration` calls `fstests.Run` with `RemoteName: "TestYandex:"` and a nil object typed as `*yandex.Object`, exercising the standard rclone backend contract against a configured live Yandex remote.

Control flow is intentionally minimal: the test package imports the backend under test and delegates all behavior checks to `fstest/fstests`, which will cover list, object create/update/read/delete, directory operations, metadata expectations, and optional features according to the backend capabilities. State is external: the test requires a configured `TestYandex:` remote and therefore depends on OAuth credentials and Yandex service availability. Risks are mainly coverage shape: it gives strong end-to-end signal when configured, but no local unit tests for REST error decoding, async job polling, custom modtime property behavior, or path encoding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/yandex/yandex_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/zoho/api/types.go -->
# sources/user-network-fs/rclone/backend/zoho/api/types.go

Purpose: defines JSON models for the Zoho WorkDrive backend API. It includes `Time`, OAuth/user/team/workspace response structs, file/folder item models, cursor links, upload responses, and write-metadata request bodies used by create, rename, move, copy, and delete operations.

Important APIs: `Time.UnmarshalJSON` accepts either numeric JSON or quoted numeric milliseconds since Unix epoch. `UploadInfo.GetUploadFileInfo` and `LargeUploadInfo.GetUploadFileInfo` decode Zoho's nested JSON string field into `UploadFileInfo`. `UploadFileInfo.GetModTime` chooses a usable timestamp from audit resource created time, status-change time, or current time fallback. The write types (`WriteMetadataRequest`, `WriteMultiMetadataRequest`, `WriteMetadata`, `WriteAttributes`) are the shared request shape for mutating WorkDrive records.

State and dependencies: all types are transient JSON adapters; no persistence is owned here. The file depends only on Go JSON, formatting, string-to-int conversion, and time. Risks include brittle field names for Zoho's inconsistent upload JSON (`File INFO`, `file_info`, `notes.txt`, `RessourceID` spelling), silent use of current time when upload audit timestamps are missing, and integer millisecond parsing failures. Test signal comes indirectly through Zoho backend integration tests and upload paths; there are no direct unit tests for the custom time or embedded JSON decoding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/zoho/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/zoho/zoho.go -->
# sources/user-network-fs/rclone/backend/zoho/zoho.go

Purpose: implements the rclone Zoho WorkDrive backend. It registers `zoho`, drives OAuth setup including region-specific endpoints, configures team/private-space/workspace selection, and implements rclone filesystem operations over Zoho's ID-based WorkDrive APIs. Core types are `Options`, `Fs`, `Object`, and local `workspaceInfo`; interface assertions cover filesystem, purge, copy, move, dir move, about, dir-cache flushing, object, and object ID support.

Control flow: `setupRegion` rewrites OAuth, account, API, upload, and download roots from the configured Zoho TLD. The config state machine obtains OAuth, rewrites token type to `Zoho-oauthtoken`, reads user/team/workspace info, and stores `root_folder_id`. `NewFs` validates upload cutoff, creates REST clients and a `dircache.DirCache`, and handles a root that names a file by returning `fs.ErrorIsFile` with the parent Fs. Directory traversal uses `dirCache` plus paginated `listAll`. Upload dispatch chooses multipart upload below `upload_cutoff` and stream upload at or above it. Server-side copy/move operate through Zoho metadata endpoints and sometimes require separate rename steps.

State and persistence: persistent state is rclone config (`region`, OAuth token, `root_folder_id`, `upload_cutoff`); runtime state includes region-global URLs, REST clients, pacer, and directory ID cache. Objects cache ID, size, and modtime; hashes are unsupported and precision is `ModTimeNotSupported`. Risks include package-level mutable endpoint globals, dependency on exact Zoho status codes and response shapes, root purge prohibition, soft-delete status `51`, possible incomplete metadata in copy/move responses, no SetModTime support, and limited validation of path traversal because IDs rather than paths are authoritative. Test signal is primarily the standard integration suite in `zoho_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/zoho/zoho.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/zoho/zoho_test.go -->
# sources/user-network-fs/rclone/backend/zoho/zoho_test.go

Purpose: declares the Zoho WorkDrive integration test entry point. `TestIntegration` delegates to `fstests.Run` with `RemoteName: "TestZoho:"`, `SkipInvalidUTF8: true`, and a nil object typed as `*zoho.Object`.

Control flow and state are intentionally externalized to rclone's shared backend test suite. The test requires a configured live Zoho remote with valid OAuth, region, and workspace root. The `SkipInvalidUTF8` option is a backend-specific signal that the Zoho encoding/API path cannot represent all invalid UTF-8 cases expected by the generic suite. Risks are the same as most live backend tests: failures can reflect provider availability, quota, or account setup rather than code regressions. There are no unit tests here for region setup, token rewriting, upload response decoding, dir-cache behavior, or copy/move rename edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/zoho/zoho_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/backend-versions.sh -->
# sources/user-network-fs/rclone/bin/backend-versions.sh

Purpose: release/documentation helper that inserts `versionIntroduced` metadata into backend documentation pages based on git history. It iterates top-level backend directories, skips special backends, finds the earliest relevant commit, finds the earliest version tag containing that commit, echoes backend/version, and uses `sed -i~` to insert front matter into `docs/content/<backend>.md`.

Dependencies are `bash`, `find`, `git`, `grep`, `sort`, and GNU/BSD-compatible `sed` behavior. State changes are direct edits to docs plus backup files. Risks include numeric `sort -n` being weak for semantic tags, insertion at fixed line 4 regardless of front matter shape, unquoted shell expansions around backend names, and creation of `~` backups. Test signal is manual; no automated test wraps this script.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/backend-versions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/bisect-go-rclone.sh -->
# sources/user-network-fs/rclone/bin/bisect-go-rclone.sh

Purpose: example `git bisect run` helper for bisecting Go compiler/runtime regressions that affect rclone. It is meant to run from the Go source tree, build the checked-out Go version, switch shell environment to a specific Go toolchain path, build rclone, and run a failing race test.

State and dependencies are deliberately user-local: it assumes Go source layout, `~/bin/use-go1.11`, a rclone checkout under `~/go/src/github.com/rclone/rclone`, `make`, and a local `race.go`. Exit `125` on Go build failure tells git-bisect to skip that revision. Risks are hard-coded personal paths and stale Go version naming; this is a template rather than general automation. Test signal is the bisect result itself.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/bisect-go-rclone.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/bisect-rclone.sh -->
# sources/user-network-fs/rclone/bin/bisect-rclone.sh

Purpose: example `git bisect run` helper for locating rclone regressions. It documents the bisect setup sequence, builds the current revision with `make`, prints `rclone version`, and leaves commented sample reproduction commands for backend copy/download failures.

State is the checked-out repository state controlled by git bisect. Dependencies are shell, `make`, and the locally built `rclone`. Compile failures exit `125` to mark revisions untestable. Risks include the script being checked into the repo and overwritten during bisect unless copied to `/tmp`, and the actual regression test must be manually edited in. No automated test exists because this is an operator template.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/bisect-rclone.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/build-xgo-cgofuse.sh -->
# sources/user-network-fs/rclone/bin/build-xgo-cgofuse.sh

Purpose: tiny release/build helper that builds and pushes a Docker image named `rclone/xgo-cgofuse` from the upstream `winfsp/cgofuse` GitHub repository. It runs `docker build`, lists images, then pushes the image.

State changes are Docker-local image cache mutations and a remote registry push. Dependencies are Docker, network access, permissions to push `rclone/xgo-cgofuse`, and availability of the GitHub Docker build context. Risks include building an unpinned remote repository state, pushing over an existing tag, and no validation beyond Docker command success. There is no test signal in the repo.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/build-xgo-cgofuse.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/check-merged.go -->
# sources/user-network-fs/rclone/bin/check-merged.go

Purpose: standalone Go tool, excluded from normal builds, that helps determine whether local branches may already be merged into a target branch. It parses `git branch -v`, extracts branch name, revision, and log line, searches target branch history for the same commit subject, and when a match is found prints candidate evidence plus a diff-of-diffs between the branch revision and matched commit.

Important functions: `gitBranch` streams branch lines through regex `reLine`; `gitLogGrep` invokes `git log --grep`; `gitDiffDiff` shells through bash process substitution to compare `git show` output. State is read-only against git history, with stdout reporting. Dependencies include git and bash. Risks include commit-subject matching false positives/negatives, shelling with formatted revision arguments, and branch output format assumptions. Test signal is manual execution; no unit tests cover regex parsing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/check-merged.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/check_autogenerated_edits.py -->
# sources/user-network-fs/rclone/bin/check_autogenerated_edits.py

Purpose: CI/local guard that prevents unauthorized edits to autogenerated markdown files or marked autogenerated sections. It compares markdown files changed between a base and head ref, detects whole-file generated markers or `<!-- autogenerated options start ... -->` / stop regions, and emits GitHub Actions error annotations for changed generated lines.

Important functions: `run_git`, `get_changed_files`, `get_diff`, `get_file_content`, `find_regions`, `in_region`, `show_error`, and `check_file`. Control flow uses `git diff -U0` hunks and line counters to map added/removed lines against old/new generated regions. State is read from git refs only. Risks: `check_file` currently reads `HEAD` and `HEAD~1` for region content rather than the passed base/head refs, which can diverge from PR merge-base checks; generated markers must be exact; binary/renamed files are not specially handled. Test signal is CI usage, with no direct unit tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/check_autogenerated_edits.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/ci.rclone.conf -->
# sources/user-network-fs/rclone/bin/ci.rclone.conf

Purpose: encrypted rclone configuration file for CI use. It contains the `RCLONE_ENCRYPT_V0` header and one encrypted blob, which rclone can decrypt with the appropriate config password/environment supplied in CI.

State and persistence are entirely the encrypted config payload. There are no functions or control flow in this file. Dependencies are rclone's encrypted config format and CI secret provisioning. Risks include config staleness, opaque credential scope, inability to review contents without secrets, and accidental exposure if the decrypting password is mishandled. Test signal is indirect: CI jobs depending on configured remotes will fail if this config cannot be decrypted or no longer works.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/ci.rclone.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/config.py -->
# sources/user-network-fs/rclone/bin/config.py

Purpose: demonstration and test utility for rclone's remote configuration APIs. It simulates `rclone config create` and `rclone config update` either through `rclone rc --loopback` or a running RC server, then drives the state-machine prompts by reading returned options and submitting user-selected results.

Important APIs: `rpc` dispatches local loopback or HTTP RC calls; `parse_parameters` parses `name=value`; `ask` renders option help/examples and handles exclusive choices; `create_or_update` loops until returned `State` is empty. `password` and `authorize` are placeholders. State changes occur through rclone config APIs, potentially writing real remote configuration. Dependencies include `rclone`, optional `requests`, JSON, and interactive stdin. Risks include clear-text parameter handling, manual prompt behavior, unimplemented subcommands, and local RC authentication assumptions. Test signal is manual/API experimentation rather than automated tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/config.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/cross-compile.go -->
# sources/user-network-fs/rclone/bin/cross-compile.go

Purpose: release build tool that cross-compiles rclone for many GOOS/GOARCH pairs, builds zip archives, builds Linux deb/rpm packages via nfpm, embeds Windows resources, and optionally aliases artifacts to a release name. It is excluded from normal builds via `//go:build ignore`.

Important functions: `compile` fans out builds with a worker pool; `compileArch` sets `GOOS`, `GOARCH`, optional CGO/macOS flags, build tags, ldflags version, and packaging; `buildZip` collects manual/manpage assets; `buildDebAndRpm` renders `bin/nfpm.yaml`; `generateResourceWindows` runs `resource_windows.go`. State changes occur under `build/`, with generated binaries, archives, package files, `version.txt`, and temporary Windows `.syso` files. Dependencies include Go, zip, nfpm, docs artifacts, optional xcrun/macOS SDK, and filesystem links. Risks include unpinned host toolchain behavior, concurrent builds sharing source-level `.syso` files, packaging failures after successful compile, and platform-specific environment correctness. Validation is command success plus failure aggregation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/cross-compile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/decrypt_names.py -->
# sources/user-network-fs/rclone/bin/decrypt_names.py

Purpose: diagnostic helper that rewrites encrypted crypt remote names in an rclone log back to plaintext using a mapping generated by `rclone ls --crypt-show-mapping`.

Important functions: `read_crypt_map` parses lines matching `NOTICE: <plain>: Encrypts to "<cipher>"`, splitting path components and building cipher-to-plain substitutions; `map_log_file` streams a log and performs direct string replacements for each mapping. State is read-only except stdout output. Dependencies are Python regex and input file formats. Risks include O(N*M) replacement cost for large maps/logs, accidental replacement of matching substrings outside path contexts, and reliance on exact notice text. Test signal is manual comparison of rewritten logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/decrypt_names.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/fetch-gui-dist.sh -->
# sources/user-network-fs/rclone/bin/fetch-gui-dist.sh

Purpose: fetches the latest `dist.zip` from `rclone/rclone-web` GitHub releases into `cmd/gui/dist.zip` and records the release tag in `cmd/gui/dist.tag`. It supports `--commit` to commit changed GUI assets.

Control flow: parses arguments, optionally adds GitHub token auth, calls the releases API with retrying curl, extracts `tag_name` and the `dist.zip` asset URL via Python JSON snippets, skips if local zip/tag already match, downloads via a temp file, atomically moves it into place, writes tag, and optionally stages/commits. State changes are the embedded GUI zip/tag and optional git commit. Risks include relying on latest release mutability, GitHub rate limits, Python availability, partial state if tag write succeeds but commit fails, and zip contents not independently verified. Test signal is command success and reproducible build behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/fetch-gui-dist.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/get-github-release.go -->
# sources/user-network-fs/rclone/bin/get-github-release.go

Purpose: standalone installer/fetcher for the latest GitHub release asset matching the current OS/architecture and a user-provided asset-name regex. It can use the GitHub API or scrape the releases page, download the asset to temp, optionally install a `.deb`, or extract a named binary from a tar archive into a writable bin directory.

Important functions: `defaultBinDir` selects a writable PATH directory; `getAsset` uses API JSON and optional `GITHUB_USER`/`GITHUB_TOKEN`; `getAssetFromReleasesPage` parses HTML; `isOurOsArch` applies OS/arch aliases; `getFile` downloads; `untar` extracts a matching regular file from gzip/bzip2/plain tar; `run` executes installer commands. State changes include temp downloads, optional sudo package installation, and file extraction into bindir. Risks include HTML scraping fragility, unauthenticated rate limits, matching the wrong asset by regex, no checksum verification, and extracting files with broad permissions. Validation is fatal-on-error command flow.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/get-github-release.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/make-test-certs.sh -->
# sources/user-network-fs/rclone/bin/make-test-certs.sh

Purpose: generates a local CA plus server and password-protected client TLS certificates for testing rclone servers with TLS and mutual TLS. Configuration is environment-driven (`OUT_DIR`, subjects, CNs, passwords, validity days).

Control flow creates OpenSSL extension configs, creates/reuses CA key, creates CA CSR/cert, creates server key/CSR/cert with localhost SAN, creates encrypted client key/CSR/cert with clientAuth EKU, verifies the chain, and prints example `rclone serve http` and client commands. State is written under `OUT_DIR`, including private keys and CSRs. Dependencies are bash and OpenSSL. Risks include predictable default client key password, overwriting server/client keys, generated CA trust scope, and shell-created OpenSSL config files. Test signal is `openssl verify` success plus manual rclone commands.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/make-test-certs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/make_backend_docs.py -->
# sources/user-network-fs/rclone/bin/make_backend_docs.py

Purpose: regenerates autogenerated backend option and backend command documentation sections in `docs/content/<backend>.md` or backend `_index.md` files. It shells out to a built `./rclone` to render `help backend` and `backend help`.

Important functions: `find_backends`, `output_docs`, `output_backend_tool_docs`, and `alter_doc`. `alter_doc` locates the autogenerated marker region, writes a `~new~` replacement file, substitutes generated output, renames the original to `~`, and moves the new file into place. State changes are markdown docs plus backup files. Dependencies include a built rclone binary and marker comments. Risks include marker mismatch, doc file path assumptions, partial backup churn, backend command help errors suppressed on stderr, and no atomic replacement beyond rename sequence. Test signal is command output and later doc diffs/CI linting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/make_backend_docs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/make_bisync_docs.go -->
# sources/user-network-fs/rclone/bin/make_bisync_docs.go

Purpose: regenerates selected autogenerated sections of bisync documentation: ignored backends/tests and currently failing bisync integration tests. It is a standalone `go run` tool.

Important functions: `replaceBetween` edits `bisync.md` between marker strings; `getIgnores` reads `fstest/test_all/config.yaml` and formats bisync-specific ignores; `getFailures` downloads the current integration-test JSON index and formats bisync failures with links; `parseConfig` YAML-decodes test config. State changes are direct writes to docs. Dependencies include rclone test config, public integration-test server, YAML decoding, and markers. Risks include network dependency for failures, marker drift, writing docs with mode `0777`, and only including first few failures per run. Test signal is successful doc generation and reviewed diffs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/make_bisync_docs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/make_changelog.py -->
# sources/user-network-fs/rclone/bin/make_changelog.py

Purpose: generates a new top section for `docs/content/changelog.md` from git commit subjects between two version refs. It categorizes commits by prefix, normalizes backend aliases, strips issue references, splits remaining items into new features versus fixes, and writes a complete changelog to stdout.

Important functions: `process_log` parses `git log --pretty` lines into category buckets; `make_out` renders selected categories; `main` reads old changelog, updates build date, inserts compare link and generated sections. State is stdout only unless caller redirects. Dependencies are git, docs layout, backend directory names, regex conventions in commit subjects. Risks include malformed commit messages containing unexpected `|`, category misclassification, duplicate `protondrive.md` elsewhere not relevant here, and manual release-edit needs. Test signal is manual review of generated changelog.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/make_changelog.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/make_manual.py -->
# sources/user-network-fs/rclone/bin/make_manual.py

Purpose: builds the monolithic `MANUAL.md` by concatenating selected Hugo markdown docs and generated command docs, normalizing front matter, shortcodes, icons, image URLs, and absolute links. It also embeds `rclone help` output and uses `SOURCE_DATE_EPOCH` for reproducible build dates.

Important functions: `read_doc`, `check_docs`, `read_command`, `read_commands`, and `main`. State changes are writes to `MANUAL.md`. Dependencies include doc file ordering, `rclone` in PATH, commands docs, and regex transformations for Hugo shortcodes. Risks include strict front matter splitting, docs list drift, duplicated docs entry (`protondrive.md` appears twice), broad shortcode regex removal, and failures when docs exist on disk but not in `docs`. Test signal is successful generation plus downstream manual/manpage build checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/make_manual.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/make_rc_docs.sh -->
# sources/user-network-fs/rclone/bin/make_rc_docs.sh

Purpose: regenerates autogenerated remote-control documentation in `docs/content/rc.md`. It installs rclone, starts a temporary cache remote mounted with `--rc`, captures `rclone rc` output, splices it between autogenerated markers, and cleans temp files.

State changes include Go install cache/binary, temporary `/tmp/rclone` directories, a background mount process, and docs rewrite. Dependencies include Go, rclone, FUSE mount support, cache backend, `awk`, and unmount tools. Risks include fixed sleep for mount readiness, background process cleanup failures, platform/FUSE assumptions, marker drift, and docs replacement with partial output if RC capture fails after mount. Test signal is command success and resulting doc diff.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/make_rc_docs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/manage_backends.py -->
# sources/user-network-fs/rclone/bin/manage_backends.py

Purpose: manages backend metadata YAML files under docs/data/backends. Verbs create default files, update canonical/default fields, or fetch live feature/hash/precision data via `rclone backend features`.

Important pieces: canonical key ordering and defaults, `test_server` context manager for optional local test server startup, `wait_for_tcp`, YAML load/save, `fetch_rclone_features`, `do_create`, `do_update`, and `do_features`. State changes are YAML writes and temporary environment variables for test server configuration. Dependencies include PyYAML, rclone, optional init scripts, sockets, subprocesses, and test servers. Risks include modifying docs metadata in place, environment leakage if server setup fails outside context, simplistic remote-name derivation, Unicode YAML output, and requiring reachable test servers. Test signal is command output and updated YAML diffs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/manage_backends.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/markdown-lint -->
# sources/user-network-fs/rclone/bin/markdown-lint

Purpose: local wrapper around the same markdownlint globs defined in `.github/workflows/build.yml`. It extracts globs from the `Check Markdown format` workflow step with `awk` and runs `davidanson/markdownlint-cli2` in Docker with the repository mounted at `/workdir`.

State changes are limited to Docker image pulls/cache and container execution. Dependencies are Docker, workflow file structure, `awk`, and a working current directory at repo root. Risks include brittle YAML parsing with awk, unquoted `$PWD` and globs, Docker user mapping issues, and mismatch if workflow structure changes. Test signal is markdownlint exit status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/markdown-lint -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/nfpm.yaml -->
# sources/user-network-fs/rclone/bin/nfpm.yaml

Purpose: nfpm package template used by `cross-compile.go` to build Linux `.deb` and `.rpm` artifacts. Template fields `{{.Arch}}` and `{{.Version}}` are substituted into package metadata.

Content maps the built `rclone` binary to `/usr/bin/rclone`, manual/readme files to `/usr/share/doc/rclone`, and `rclone.1` to the manpage path. State is not mutated by this template itself; generated per-build copies are placed in release build directories. Dependencies are nfpm's YAML schema and the artifact layout created by cross-compilation. Risks include package metadata drift, missing license/changelog fields if distro policy requires them, and template/schema incompatibility with nfpm upgrades. Test signal comes from successful package builds and installation checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/nfpm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/not-in-stable.go -->
# sources/user-network-fs/rclone/bin/not-in-stable.go

Purpose: release helper that prints commits present on `master` but not on the previous minor stable branch. It reads `VERSION`, computes the previous stable prefix with semver, reads git logs from `<stable>.0..master` and `<stable>.0..<stable>-stable`, and compares commit subjects.

Important function: `readCommits` runs `git log --oneline`, parses hash/message with `logRe`, and returns both map and ordered list. State is read-only against git/VERSION; output is stdout. Dependencies are git and `coreos/go-semver`. Risks include matching by commit subject rather than patch identity, assuming branch names `master` and `vX.Y-stable`, and semver minor underflow if used near initial versions. Test signal is manual release review; no unit tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/not-in-stable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/resource_windows.go -->
# sources/user-network-fs/rclone/bin/resource_windows.go

Purpose: Go generate/tool binary that creates Windows `.syso` resource files embedding version metadata and optionally an icon for `rclone.exe` or `librclone.dll`. It uses source-location discovery to default paths into the repository tree.

Control flow parses flags (`binary`, `arch`, `version`, `icon`, `dir`, `syso`), computes output filename, parses semver, chooses Windows file type based on `.exe` or `.dll`, fills `goversioninfo.VersionInfo`, builds/walks it, and writes the `.syso`. State changes are generated `resource_windows_<arch>.syso` files. Dependencies are `goversioninfo`, semver parsing, icon path, and rclone `fs.Version`. Risks include invalid prerelease version parsing if semver library rejects release suffixes, stale icon path, architecture support limited by goversioninfo, and generated files being consumed by later `go build`. Test signal is generation success and Windows binary metadata inspection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/resource_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/rules.go -->
# sources/user-network-fs/rclone/bin/rules.go

Purpose: ruleguard custom lint rules for gocritic/golangci-lint. The `useFsLog` matcher suggests rewriting standard-library `log.Print/Fatal/Panic` calls to rclone `fs.Log/Fatal/Panic` variants, wrapping non-string variadic arguments with `fmt.Sprint` when needed.

State is declarative lint configuration only; it is excluded from normal builds with `//go:build ruleguard`. Dependencies are `github.com/quasilyte/go-ruleguard/dsl` and golangci-lint gocritic integration. Risks are documented in comments: cache invalidation is manual, suggestions can require import cleanup, and suggestions are wrong inside the `fs` package or in scopes where `fs`/`fmt` names collide. Test signal is lint execution; no standalone unit tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/rules.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/test-all-commits-compile.sh -->
# sources/user-network-fs/rclone/bin/test-all-commits-compile.sh

Purpose: branch hygiene helper that checks every commit on the current branch since `master` compiles with `go install ./...`. It is adapted for rebased feature branches.

Control flow rejects running on `master`, lists commits in reverse, checks out each commit, runs install, reports pass/fail, and returns to the original branch on failure or completion. State changes are destructive to the working tree checkout state and can disrupt uncommitted work. Dependencies are git and Go. Risks include no dirty-tree guard, branch name assumptions, stopping without nonzero explicit exit in one path, and potential generated/build-cache side effects. Test signal is compile success at each commit.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/test-all-commits-compile.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/test-repeat-vfs.sh -->
# sources/user-network-fs/rclone/bin/test-repeat-vfs.sh

Purpose: convenience wrapper that repeatedly runs selected VFS and mount-related test directories through `bin/test-repeat.sh`, defaulting to 100 iterations and enabling race detector plus `cmount` tags.

State changes are compiled test binaries and failure logs in each test directory. Dependencies are bash, realpath, Go test, race support, and mount/cmount build prerequisites. Risks include long runtime, large log buildup on repeated failures, and platform-specific cmount/FUSE requirements. Test signal is repeated successful test execution with intermittent failures retained as logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/test-repeat-vfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/test-repeat.sh -->
# sources/user-network-fs/rclone/bin/test-repeat.sh

Purpose: generic helper for repeatedly running a compiled Go test binary to catch flaky tests. It accepts iteration count, binary name, log prefix, `-race`, `-tags`, and passes other flags to the test binary.

Control flow parses flags manually, compiles with `go test -c`, then loops `seq -w` iterations, writing each run's output to a log and deleting logs for successful runs. State changes are the test binary and failure log files. Dependencies are bash and Go. Risks include simplistic option parsing, unquoted expansions, logs accumulating on frequent failures, and treating unknown `--flag=value` by stripping before pass-through. Test signal is per-iteration OK/FAIL plus retained logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/test-repeat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/test_backend_sizes.py -->
# sources/user-network-fs/rclone/bin/test_backend_sizes.py

Purpose: estimates binary size contribution of each backend by compiling rclone with all backends, then repeatedly commenting one backend import out of `backend/all/all.go` and measuring size difference.

Important functions: `read_backends`, `write_all`, `compile`, and `main`. State changes are direct rewrites of `backend/all/all.go` and creation of `rclone` binary; the original file is restored at the end. Dependencies are Go build and backend import file format. Risks include leaving `all.go` modified if interrupted, special-case coupling for `s3`/`pikpak`, no dirty-tree guard, and measuring compile/linker interactions rather than exact isolated backend size. Test signal is produced CSV-like size output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/test_backend_sizes.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/test_independence.go -->
# sources/user-network-fs/rclone/bin/test_independence.go

Purpose: standalone diagnostic tool that checks whether integration subtests can pass independently. It runs `go test -v <package>`, extracts `TestIntegration/...` names, then reruns each test individually with `-run`.

Important functions: `findTests` parses verbose test output with regex; `runTest` invokes a targeted test and logs OK/FAILED while printing failing output. State is read-only except build/test caches and any backend test side effects. Dependencies are Go test output format and test package behavior. Risks include regex only matching `TestIntegration/`, full initial suite must pass before independent checks start, and remote tests may mutate shared state. Test signal is the individual rerun status log.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/test_independence.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/test_metadata_mapper.py -->
# sources/user-network-fs/rclone/bin/test_metadata_mapper.py

Purpose: sample metadata mapper for rclone metadata migration workflows. It reads JSON from stdin, modifies the `Metadata` object by appending a migration tag to `description` and replacing `domain1.com` with `domain2.com` in `owner`, then writes JSON to stdout.

State is pure stdin/stdout transformation. Dependencies are Python JSON and expected input shape containing `Metadata`. Risks include KeyError on missing `Metadata`, simplistic owner replacement, and no schema validation. Test signal is manual invocation or use as a fixture/demo in metadata mapper tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/test_metadata_mapper.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/test_proxy.py -->
# sources/user-network-fs/rclone/bin/test_proxy.py

Purpose: sample dynamic backend proxy for rclone serve modes. It reads JSON credentials from stdin and returns an rclone remote config JSON for an SFTP backend on localhost, marking `pass` for obscuring.

State is pure stdin/stdout transformation. Dependencies are Python JSON and input fields `user` and `pass`. Risks include assuming localhost SFTP, passing credentials through process pipes, no validation, and only demonstrating a minimal config shape. Test signal is manual/demo use with rclone serve proxy functionality.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/test_proxy.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/tidy-beta -->
# sources/user-network-fs/rclone/bin/tidy-beta

Purpose: release maintenance script for deleting old beta artifacts from `beta.rclone.org:` matching a version prefix. It defaults to dry-run and requires a second argument `delete` to actually delete.

Control flow validates version argument, sets `--dry-run` unless deletion is confirmed, then runs `rclone delete` with progress, concurrency, fast-list, and include filters for root and branch beta paths. State changes are remote deletions only when confirmed. Dependencies are configured `beta.rclone.org:` remote and rclone. Risks include overly broad include patterns if version is wrong, remote credential scope, and dry-run output needing review before actual deletion. Test signal is dry-run listing and delete command success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/tidy-beta -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/update-authors.py -->
# sources/user-network-fs/rclone/bin/update-authors.py

Purpose: updates `docs/content/authors.md` with contributors found in git history, committing each new author entry. It considers both commit author emails and `Co-authored-by:` trailers, excluding emails already present or listed in `bin/.ignore-emails`.

Important functions: `load`, `add_email`, and `main`. State changes are appending to authors docs and creating git commits. Dependencies are git, author file format, ignore file format, and commit trailer conventions. Risks include one commit per author, no dry-run mode, no dirty-tree guard, name/email parsing by simple delimiters, and possible duplicate people with different emails. Test signal is resulting commits and reviewed authors diff.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/update-authors.py -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/upload-github -->
# sources/user-network-fs/rclone/bin/upload-github

Purpose: publishes an rclone GitHub release using the `gh` CLI. It creates temporary release notes linking to the latest changelog anchor, creates a draft release, uploads build artifacts, marks the release non-draft, views it, and prints done.

State changes are remote GitHub release creation and artifact uploads; local state includes a temp release-notes file. Dependencies are `gh`, authenticated permissions on `rclone/rclone`, populated `build/`, and changelog heading format. Risks include uploading unintended build files except explicit `current`/`testbuilds` skips, clobbering assets, immediately publishing after upload, and anchor derivation mismatch. Test signal is `gh release view` success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/upload-github -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/bin/use-deadlock-detector -->
# sources/user-network-fs/rclone/bin/use-deadlock-detector

Purpose: temporary debugging script that rewrites Go source to use `github.com/sasha-s/go-deadlock` mutex types. It refuses to run if tracked files have uncommitted changes, installs the dependency, replaces `sync.RWMutex` and `sync.Mutex` occurrences with `deadlock` equivalents, and runs `goimports`.

State changes are broad source rewrites, module changes from `go get`, and import formatting. Dependencies are git, Go, find, sed, xargs, and goimports. Risks are intentionally high: pattern replacement is broad, user must undo with `git reset --hard HEAD`, untracked/generated files are not checked, and it can affect comments or non-target contexts. Test signal is subsequent test runs under deadlock detector.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/bin/use-deadlock-detector -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/about/about.go -->
# sources/user-network-fs/rclone/cmd/about/about.go

Purpose: implements `rclone about remote:` for printing backend quota/usage information. It registers a Cobra command with `--json` and `--full` flags, creates a source Fs, invokes the backend `Features().About` optional interface, and formats `fs.Usage` fields.

Important functions: `printValue` handles nil values, byte/count formatting, and full numeric output; the command `Run` wraps execution through `cmd.Run`, checks backend support, handles nil usage, and either JSON-encodes with indentation or prints Total/Used/Free/Trashed/Other/Objects. State is read-only against the remote. Dependencies are `fs.Abouter`, `fs.Usage`, command flag helpers, and Cobra. Risks include unsupported backends, partial usage fields, backend-specific stale quota, and global package flags in tests. Test signal is likely command integration elsewhere; this file has no local unit test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/about/about.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/all/all.go -->
# sources/user-network-fs/rclone/cmd/all/all.go

Purpose: aggregate import package that registers all active rclone commands by blank-importing each command package. Importing `cmd/all` gives a complete CLI command tree through each package's `init` registration.

Control flow is entirely Go import side effects; there are no functions. State mutation happens through command registration into the root Cobra command and any package-level flag variables initialized by imported packages. Dependencies are every listed command package. Risks include missing a new command from this list, importing platform-specific packages with build constraints, and global initialization order/side effects. Test signal is build coverage: if any imported command fails to compile, the aggregate package fails.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/all/all.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/archive.go -->
# sources/user-network-fs/rclone/cmd/archive/archive.go

Purpose: non-Plan 9 root command for `rclone archive`. It registers `archive.Command` and provides help text directing users to subcommands such as `list`, `create`, and `extract`.

Control flow: `init` adds the command to `cmd.Root`; `RunE` returns an explicit error when no action is provided or an unknown action is used, leaving real work to subcommands. State is command registration only. Dependencies are Cobra and rclone command root. Risks are mostly UX: root command does no subcommand dispatch beyond Cobra and returns generic unknown action. Test signal is indirect through archive command tests and command docs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/archive.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/archive_test.go -->
# sources/user-network-fs/rclone/cmd/archive/archive_test.go

Purpose: end-to-end tests for archive create/list/extract flows over local, remote, and memory backends. It validates destination checking, archive creation in many formats, listing archive entries, purging source, extracting back, and comparing restored listings.

Important helpers: `TestCheckValidDestination`, `testArchiveRemote`, `testArchive`, `TestIntegration`, and `TestMemory`. State is created through `fstest.NewRun`, local/remote files, generated archives, and purge operations. Dependencies include `mholt/archives`, local/memory backends, operations, and archive subpackages. Risks covered include format support, directory entries, file sizes, subdirectory extraction, and source/destination direction. Gaps include dry-run, metadata preservation, filters, stdout archive output, and error paths. Test signal is strong for supported formats and standard file restore semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/archive_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/archive_unsupported.go -->
# sources/user-network-fs/rclone/cmd/archive/archive_unsupported.go

Purpose: Plan 9 build stub for the archive root package. It prevents "no buildable Go source files" on unsupported platforms while excluding archive functionality there.

There are no functions, state changes, or runtime control flow. Dependency is only the Go build tag `plan9`. Risk is that Plan 9 builds compile without registering the archive command, which is intentional given archive dependencies. Test signal is platform build success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/archive_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/create/create.go -->
# sources/user-network-fs/rclone/cmd/archive/create/create.go

Purpose: implements `rclone archive create`, converting a source Fs tree into a compressed archive written to stdout or a destination Fs object. It supports multiple archive/compression formats, `--format`, `--prefix`, and `--full-path`.

Important APIs: `getCompressor` maps explicit format or destination extension to `archives.CompressedArchive`; `CheckValidDestination` allows overwrite of files but rejects directory destinations; `loadMetadata` fetches optional metadata; `ArchiveCreate` walks the source, filters dirs/files, wraps entries with `files.NewArchiveFileInfo`, sorts entries, archives to discard/stdout/pipe, and writes remote output via `operations.Rcat`. State changes are archive object creation and optional read accounting/log totals. Dependencies include `mholt/archives`, rclone filters, walk, operations, metadata, and archive files adapter. Risks include a debug `fmt.Printf` in command path, extension guessing ambiguity, no path traversal concern on create but prefix can produce odd names, goroutine pipe error propagation, and metadata defaults. Tests cover many formats via `archive_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/create/create.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/create/create_unsupported.go -->
# sources/user-network-fs/rclone/cmd/archive/create/create_unsupported.go

Purpose: Plan 9 build stub for `cmd/archive/create`, keeping the package buildable when the real archive create implementation is excluded.

There is no runtime behavior. State is limited to build selection via `//go:build plan9`. Dependencies are none beyond package identity. Risk is intentional absence of the create subcommand on Plan 9. Test signal is platform compile success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/create/create_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/extract/extract.go -->
# sources/user-network-fs/rclone/cmd/archive/extract/extract.go

Purpose: implements `rclone archive extract`, reading an archive object from a source Fs, auto-identifying its format, and extracting included entries into a destination Fs directory.

Control flow: command parsing obtains source file and destination dir; `ArchiveExtract` verifies source is an object, creates destination directory, opens the source with accounting and download headers, obtains a read-at seeker for `archives.Identify`, checks the identified format supports `archives.Extraction`, then iterates entries. It strips exactly one leading `./`, skips the root `./` directory entry, prefixes with destination dir, applies filters, creates dirs, and writes files with `operations.Rcat` unless dry-run. State changes are destination directories/files and accounting transfer state. Risks include archive path traversal still possible for `../` entries, reliance on archive library identification, read-at-seeker buffering cost, and no explicit closing of each archive entry reader after `Rcat` unless handled by library/reader. Tests cover `./` stripping and archive round trips.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/extract/extract.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/extract/extract_test.go -->
# sources/user-network-fs/rclone/cmd/archive/extract/extract_test.go

Purpose: unit test for the path normalization rule used by archive extraction. `TestStripDotSlashPrefix` verifies that `strings.TrimPrefix(input, "./")` strips a single leading `./`, leaves normal paths unchanged, preserves `../` traversal-looking paths, converts `./` to empty, and strips only once.

State is none beyond table-driven assertions. Dependencies are `testing`, `strings`, and testify assert. This is a focused regression test for the extraction behavior that avoids creating a spurious encoded `.` directory from common tar entries. Risk not solved by the test: it explicitly confirms `../` is not stripped, so path traversal prevention must come from other layers or remains a concern. Additional integration coverage comes from archive round-trip tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/extract/extract_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/extract/extract_unsupported.go -->
# sources/user-network-fs/rclone/cmd/archive/extract/extract_unsupported.go

Purpose: Plan 9 build stub for `cmd/archive/extract`, keeping the package buildable when extraction support is excluded.

There are no functions or runtime state. Dependency is the `plan9` build tag. Risk is intentional absence of the extract subcommand on Plan 9. Test signal is build success on unsupported platform targets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/extract/extract_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/files/countwriter.go -->
# sources/user-network-fs/rclone/cmd/archive/files/countwriter.go

Purpose: provides `CountWriter`, an `io.Writer` wrapper used by archive creation to count compressed bytes written. It wraps nil writers as `io.Discard` and tracks count with `atomic.Uint64`.

APIs: `NewCountWriter`, `Write`, and `Count`. `Write` delegates to the wrapped writer and increments by the returned byte count when positive, even if the writer also returns an error. State is the wrapped writer and atomic byte counter. Dependencies are `io` and `sync/atomic`. Risks are limited: concurrent `Write` safety is only as good as the wrapped writer, but count reads are atomic. Tests cover initial count, nil writer, partial writes, errors, and concurrent writes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/files/countwriter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/files/countwriter_test.go -->
# sources/user-network-fs/rclone/cmd/archive/files/countwriter_test.go

Purpose: unit tests for `CountWriter`. It defines `stubWriter` for short/partial/error writes and validates counting semantics across normal writes, nil writer behavior, zero-length writes, partial writes with errors, short successful writes, and concurrent write/count safety.

State is in-memory only. Dependencies are `io`, `sync`, `testing`, and testify. Test signal is strong for byte accounting behavior and confirms that the counter adds exactly the `n` returned by the wrapped writer. It does not test behavior when the wrapped writer itself is unsafe under concurrent writes, which is documented as outside `CountWriter`'s responsibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/files/countwriter_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/files/files.go -->
# sources/user-network-fs/rclone/cmd/archive/files/files.go

Purpose: adapts rclone `fs.DirEntry` and `fs.Object` values into `mholt/archives.FileInfo` / `io/fs` compatible objects for archive creation. It also maps selected rclone metadata into tar headers.

Important APIs: `metadataToHeader` fills tar mode, uid, gid, names, atime/ctime defaults; `newFileInfo` constructs an `io/fs.FileInfo` with archive name and optional prefix; `newFile` opens an rclone object through `operations.Open`, attaches accounting transfer, and obtains a read-at seeker; `NewArchiveFileInfo` returns an `archives.FileInfo` with an `Open` callback for files. State includes per-file transfer accounting and cached tar header fields. Dependencies include archive/tar, `mholt/archives`, rclone metadata/accounting/operations. Risks include permissive fallback metadata, directory `Open` returning an error, read-at-seeker buffering cost, missing close on error path after `WithReadAtSeeker`, and platform semantics for uid/gid/mode. Tests are indirect through archive create/list/extract integration.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/files/files.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/list/list.go -->
# sources/user-network-fs/rclone/cmd/archive/list/list.go

Purpose: implements `rclone archive list`, opening an archive object, auto-identifying its format, and printing entries in size/name, long timestamp, or plain modes with optional files-only/dirs-only filtering.

Important APIs: command flags (`--long`, `--plain`, `--files-only`, `--dirs-only`), `listFile`, and `ArchiveList`. `ArchiveList` opens the source object with accounting and download headers, obtains a read-at seeker, identifies the archive with `archives.Identify`, requires `archives.Extraction`, and calls `Extract` with a file handler for listing. `listFile` applies rclone filters, normalizes directory display with trailing slash, and writes synchronized output. State is read-only remote access plus accounting transfer. Dependencies include `mholt/archives`, filters, operations, and Cobra. Risks include using extraction interface for listing, full/partial buffering for read-at seeker, unsupported formats, and global flag state. Archive integration tests exercise listing after create.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/list/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/list/list_unsupported.go -->
# sources/user-network-fs/rclone/cmd/archive/list/list_unsupported.go

Purpose: Plan 9 build stub for `cmd/archive/list`, keeping the package buildable when list support is excluded with the real archive implementation.

No APIs, state, or runtime flow exist here. Dependency is build tag selection. Risk is intentional command absence on Plan 9. Test signal is platform build success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/archive/list/list_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/authorize/authorize.go -->
# sources/user-network-fs/rclone/cmd/authorize/authorize.go

Purpose: implements `rclone authorize`, the command used to authorize remotes for headless/config workflows. It registers flags to suppress browser opening and to select a custom HTML template, then delegates actual OAuth/config authorization to `config.Authorize`.

Control flow is simple: `init` registers command and flags; `RunE` checks for 1-3 args and calls `config.Authorize(context.Background(), args, noAutoBrowser, template)`. State changes happen inside config authorization, usually local token/config output or browser/listener flows. Dependencies are Cobra, rclone config, and command flag helpers. Risks include global flag variables, template path handling delegated elsewhere, and provider-specific authorization complexity outside this file. Tests check usage/help text formatting only.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/authorize/authorize.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/authorize/authorize_test.go -->
# sources/user-network-fs/rclone/cmd/authorize/authorize_test.go

Purpose: focused test for the authorize command's public help/usage surface. It asserts the `Use` string exactly matches the expected argument form and executes `authorize --help` through a throwaway Cobra parent command, checking the help output mentions `authorize <backendname>`.

State is in-memory command output buffer only. Dependencies are testing, strings, bytes, and Cobra. The test guards documentation/CLI UX but does not execute OAuth authorization, browser suppression, template rendering, or config writes. It is useful for preventing accidental regression of the argument synopsis.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/authorize/authorize_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/backend/backend.go -->
# sources/user-network-fs/rclone/cmd/backend/backend.go

Purpose: implements `rclone backend`, a generic frontend for backend-specific commands plus built-in `help` and `features` actions. It supports repeated `-o/--option` values and `--json`.

Control flow: after argument validation, `help <backendname>` can show help without instantiating a remote. Otherwise it resolves `remote:path` with `fs.ConfigFs`, constructs the Fs, dispatches `help`, `features` (`operations.GetFsInfo`), or a backend `Features().Command` call with parsed options and extra args. Output is printed as string/lines or JSON depending on type or `--json`. `showHelp` renders backend command help, sorting option names. State can be read-only or mutating depending on backend command invoked. Dependencies include fs registry, RC option parser, operations fs info, and Cobra. Risks include backend commands with side effects, option parsing ambiguity for key-only options, overlay remotes requiring underlying backend commands, and global flag state. Test signal is indirect command/integration coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/backend/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/bilib/canonical.go -->
# sources/user-network-fs/rclone/cmd/bisync/bilib/canonical.go

Purpose: provides canonical naming/path helpers shared by bisync implementation and tests. It converts `fs.Info` values into rclone argument-like paths, normalizes those paths into filesystem-safe session names, and handles backward-compatible migration from old canonical names containing `{hex}` suffixes.

Important APIs: `FsPath`, `CanonicalPath`, `SessionName`, `StripHexString`, `HasHexString`, and `BasePath`. `BasePath` builds listing-file base paths under a work directory and, if legacy suffixed listing files exist, renames them to the new non-suffixed paths unless destructive operations are skipped. State changes are local file renames of listing files. Dependencies include OS path rules, runtime GOOS, regex normalization, and `operations.SkipDestructive`. Risks include path collisions after character replacement/hex stripping, Windows path handling, and partial migration when one listing exists. Test signal is likely bisync tests using stable session names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/bilib/canonical.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/bilib/files.go -->
# sources/user-network-fs/rclone/cmd/bisync/bilib/files.go

Purpose: local filesystem utility functions for bisync code/tests. It detects local versus remote-looking paths, checks file existence, copies files preserving mode/mtime, and recursively copies directories while skipping symlinks.

Important APIs: `IsLocalPath`, `FileExists`, `CopyFileIfExists`, `CopyFile`, and `CopyDir`. State changes are local file/directory creation, chmod, and chtimes. Dependencies are OS path semantics and regexes for local, Windows drive, and rclone remote syntax. Risks include remote/local ambiguity (`c:dir` differs by OS), no symlink copying, destination directory must not preexist, and recursive copy stops on first error. Test signal is indirect through bisync tests and debug helpers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/bilib/files.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/bilib/names.go -->
# sources/user-network-fs/rclone/cmd/bisync/bilib/names.go

Purpose: small set utilities for bisync filename tracking plus alias mapping for normalized/case-equivalent names. `Names` is a map-backed set; `AliasMap` stores bidirectional equivalence pairs.

APIs: `ToNames`, `Add`, `Has`, `NotEmpty`, `ToList`, `Save`, `SaveList`, `AliasMap.Add`, and `AliasMap.Alias`. `SaveList` writes sorted, quoted names with secure `0600` permissions. State changes are local list-file writes. Dependencies are bytes, sort, strconv quoting, and OS writes. Risks include map value type `any` being larger than needed, write not atomic, and alias map supporting only one alternate per name. Test signal is indirect through bisync list/state tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/bilib/names.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/bilib/output.go -->
# sources/user-network-fs/rclone/cmd/bisync/bilib/output.go

Purpose: test/helper utility to capture rclone log output emitted during a function call. `CaptureOutput` temporarily sets log level to INFO and replaces the log handler output callback with a buffer writer guarded by a mutex.

State changes are global log handler level/output mutation, restored with defer. Dependencies are rclone `fs/log`, `log/slog`, bytes, and sync. Risks include global logging interference in concurrent tests, missed lower-level output because level is forced to INFO, and capture scope depending on defer restoration after panics. Test signal is indirect: consumers can assert log output deterministically.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/bilib/output.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/bisync_debug_test.go -->
# sources/user-network-fs/rclone/cmd/bisync/bisync_debug_test.go

Purpose: test-side helper for generating VS Code debug launch configurations for bisync integration cases. It reads `fstest/test_all/config.yaml`, enumerates bisync testdata cases, and writes a large `testdata/bisync_vscode_debuggers_launch.json` with launch entries for LocalRemote, RemoteLocal, and RemoteRemote variations.

Important structures mirror test config (`Config`, `Test`, `Backend`). `parseConfig` YAML-decodes the shared config; `(*bisyncTest).generateDebuggers` builds launch JSON from configured backends and test cases, skipping empty test dirs and local-only impossible variations. State change is writing the generated launch JSON with secure permissions. Dependencies include bisync test harness methods, YAML, bilib `PermSecure`, and fs logging. Risks include too many launch configs for VS Code, stale generated output when config/testdata changes, and no JSON escaping beyond `fmt.Sprintf` `%q` for selected fields. Test signal is assertion that the file write succeeds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/bisync/bisync_debug_test.go -->
