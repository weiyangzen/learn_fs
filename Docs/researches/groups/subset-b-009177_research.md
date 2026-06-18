# subset-b-009177 research

Grouped research report for the rsync-bundled zlib interface/utilities and Syncthing repository automation, build tooling, development utilities, crash receiver service, and relay pool generated-asset stubs. Each section preserves the source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/zlib.h -->
# sources/sync-backup/rsync/zlib/zlib.h

Purpose: public API header for the rsync-vendored zlib 1.2.8 compression library. It defines the stable ABI used by deflate/inflate stream users, gzip file accessors, one-shot compression helpers, checksum routines, large-file variants, version checking macros, and selected undocumented/internal entry points.

Important APIs/types/functions: `z_stream` is the central caller-owned stream descriptor with input/output cursors, total counters, allocator hooks, opaque state, data type, and running checksum. `gz_header` models gzip metadata. Major exports include `deflate*`, `inflate*`, `inflateBack*`, `compress*`, `uncompress`, `gz*`, `adler32*`, `crc32*`, `zlibVersion`, `zlibCompileFlags`, and `zError`. Macros wrap `deflateInit`, `inflateInit`, `deflateInit2`, `inflateInit2`, and `inflateBackInit` to pass `ZLIB_VERSION` and `sizeof(z_stream)` for ABI validation.

Control flow: callers initialize a stream, repeatedly set `next_in`/`avail_in` and `next_out`/`avail_out`, call `deflate` or `inflate` until progress, completion, or error, then release with `deflateEnd` or `inflateEnd`. Flush constants control block boundaries and finishing behavior. Gzip helpers wrap similar state behind `gzFile` and expose open/read/write/seek/close/error operations.

State and persistence behavior: zlib keeps per-stream state behind `struct internal_state`, uses caller-provided or default allocators, updates `total_in`, `total_out`, `msg`, `data_type`, and `adler`, and persists gzip data only through `gz*` file APIs. The header also exposes 64-bit offset compatibility aliases depending on large-file macros.

Dependencies/integration: depends on `zconf.h` for platform typedefs, linkage attributes, `z_off_t`, and prefix/large-file configuration. In rsync this header forms the contract between bundled zlib sources and rsync compression code.

Risks/test signals: the file is ABI-sensitive; mismatched struct layout, version macros, `Z_PREFIX_SET`, or large-file aliasing can break callers. Correctness is normally signaled by zlib stream tests, gzip round trips, checksum vectors, and consumers checking for `Z_VERSION_ERROR`, `Z_STREAM_ERROR`, `Z_DATA_ERROR`, `Z_BUF_ERROR`, and `Z_STREAM_END`.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/zlib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/zutil.c -->
# sources/sync-backup/rsync/zlib/zutil.c

Purpose: target-dependent utility implementation for zlib. It supplies version/error helpers, compile-flag introspection, optional fallback memory functions, optional debug failure handling, and default allocation/free routines used by deflate/inflate internals when callers do not provide custom allocators.

Important APIs/types/functions: `z_errmsg` maps zlib status codes to static strings via `ERR_MSG`. `zlibVersion` returns `ZLIB_VERSION`. `zlibCompileFlags` encodes sizes of `uInt`, `uLong`, pointer, and `z_off_t`, plus compile-time features such as `DEBUG`, assembly, `ZLIB_WINAPI`, `BUILDFIXED`, `DYNAMIC_CRC_TABLE`, gzip/compress disables, PKZIP workaround, fastest mode, and printf safety variants. `zError` exposes error-string lookup. Fallback `zmemcpy`, `zmemcmp`, and `zmemzero` are built when `HAVE_MEMCPY` is absent. `zcalloc` and `zcfree` cover generic and historical 16-bit allocation paths.

Control flow: normal builds take the generic allocator path: `zcalloc` ignores `opaque`, allocates with `malloc` on wider-than-16-bit `uInt` targets or `calloc` otherwise, and `zcfree` calls `free`. Legacy Turbo C and Microsoft C paths normalize or use far allocations for 64 KiB segmented-memory constraints.

State and persistence behavior: no durable state. The only process state is the exported static error-message table, optional debug verbosity, and the Turbo C pointer table used to recover original far pointers. Allocation state belongs to the C heap or legacy heap APIs.

Dependencies/integration: includes `zutil.h` and, unless `Z_SOLO`, `gzguts.h`. It is used by zlib implementation files through `ZALLOC`, `ZFREE`, `TRY_FREE`, error-message macros, and optional memory wrappers.

Risks/test signals: integer overflow on `items * size` is inherited from the old zlib allocator contract. Legacy segmented-memory code is fragile and not thread-protected. Test signals are successful deflate/inflate initialization under default allocators, `zlibCompileFlags` matching build options, and fallback memory routines behaving like libc equivalents.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/zutil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/zlib/zutil.h -->
# sources/sync-backup/rsync/zlib/zutil.h

Purpose: internal zlib configuration and utility header. Applications are warned not to include it directly; it defines implementation-only aliases, constants, platform hooks, diagnostics, allocation macros, byte-swap helpers, and memory-function selection used across the bundled zlib sources.

Important APIs/types/functions: it sets `ZLIB_INTERNAL`, includes rsync's `../rsync.h` before `zlib.h`, defines `local`, `uch/ush/ulg` aliases, declares `z_errmsg`, and provides `ERR_MSG` plus `ERR_RETURN`. Compression constants include `DEF_WBITS`, `DEF_MEM_LEVEL`, block types, `MIN_MATCH`, `MAX_MATCH`, and `PRESET_DICT`. It selects `OS_CODE`, `F_OPEN`, `fdopen` compatibility, `zmemcpy`/`zmemcmp`/`zmemzero`, debug `Assert`/`Trace*` macros, `zcalloc`, `zcfree`, `ZALLOC`, `ZFREE`, `TRY_FREE`, and `ZSWAP32`.

Control flow: preprocessing determines platform behavior from macros such as `MSDOS`, `WIN32`, `VMS`, `MACOS`, `_WIN32_WCE`, `Z_SOLO`, `HAVE_MEMCPY`, and compiler identifiers. Runtime code includes this header to normalize target differences before using utility macros.

State and persistence behavior: no durable state. It governs how zlib code touches stream allocator state, emits debug traces, and opens files. `ZALLOC` and `ZFREE` route all internal heap state through the `z_stream` allocator hooks.

Dependencies/integration: integrates the zlib internals with rsync by including `../rsync.h`, which can affect platform definitions and libc availability. It also bridges to `zlib.h` public types and optionally C library headers through rsync configuration.

Risks/test signals: platform macro mistakes can silently change gzip OS metadata, file opening modes, memory function semantics, or allocation paths. Important tests are cross-platform zlib builds, compression/decompression round trips, gzip file I/O, and builds with/without `HAVE_MEMCPY`, `DEBUG`, `Z_SOLO`, and large-file support.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/zlib/zutil.h -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.codecov.yml -->
# sources/sync-backup/syncthing/.codecov.yml

Purpose: Codecov configuration for Syncthing coverage reporting. It turns off bot comments, makes patch and project coverage statuses informational, disables GitHub Checks annotations, and excludes generated protobuf, generated mock, and mocks-directory files.

Important APIs/types/functions: declarative Codecov keys are `comment`, `coverage.range`, `coverage.precision`, `coverage.status.patch.default.informational`, `coverage.status.project.default.informational`, `github_checks.annotations`, and `ignore`.

Control flow: Codecov consumes this file after CI uploads coverage. It computes coverage using the configured range and precision, but informational status means coverage does not block CI even when thresholds fall.

State and persistence behavior: no runtime persistence. The lasting effect is in Codecov project/patch reports and GitHub integration output.

Dependencies/integration: integrates with whatever CI path uploads `coverage.txt` or Go coverage data. The ignore patterns align with generated `.pb.go`, mocked code, and `mocks` directories so reported coverage emphasizes handwritten code.

Risks/test signals: informational status can hide coverage regressions if maintainers stop inspecting reports. Incorrect ignore globs can over- or under-count generated code. Test signal is Codecov processing without annotations or blocking statuses.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.codecov.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.deepsource.toml -->
# sources/sync-backup/syncthing/.deepsource.toml

Purpose: DeepSource static-analysis configuration for the Go repository. It excludes generated protobuf files, marks Go test files, and configures the Go analyzer with the Syncthing import path and `noassets` build tag.

Important APIs/types/functions: declarative keys include `version = 1`, `exclude_patterns`, `test_patterns`, analyzer `name = "go"`, `enabled = true`, and analyzer metadata `import_paths` plus `build_tags`.

Control flow: DeepSource scans matching repository files, omits `**/*.pb.go`, recognizes `**/*_test.go` as tests, and analyzes Go packages as `github.com/syncthing/syncthing` with asset generation disabled.

State and persistence behavior: no application state. Results persist only in the DeepSource service as issues or quality signals.

Dependencies/integration: depends on DeepSource's Go analyzer and on the repository supporting `noassets` builds via generated-asset stubs.

Risks/test signals: using `noassets` can miss issues in generated asset code but keeps analysis lightweight. Wrong import path or build tag would cause package-load failures. The test signal is successful DeepSource analysis without generated protobuf noise.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.deepsource.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.github/FUNDING.yml -->
# sources/sync-backup/syncthing/.github/FUNDING.yml

Purpose: GitHub Sponsors funding metadata for the Syncthing repository. It advertises the `syncthing` GitHub sponsor target and a custom donation URL.

Important APIs/types/functions: GitHub-recognized keys are `github` and `custom`; other platform keys remain commented examples.

Control flow: GitHub reads this file to render repository funding links. There is no project build or runtime path.

State and persistence behavior: no local state. The file changes repository UI metadata.

Dependencies/integration: integrates only with GitHub repository presentation and external donation handling at `https://syncthing.net/donations/`.

Risks/test signals: stale funding URLs or wrong sponsor handle degrade contributor funding discoverability. The signal is GitHub rendering the Sponsor/Funding link as intended.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.github/FUNDING.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.github/ISSUE_TEMPLATE/01-feature.yml -->
# sources/sync-backup/syncthing/.github/ISSUE_TEMPLATE/01-feature.yml

Purpose: GitHub issue form for feature requests. It labels new issues as `enhancement` and `needs-triage`, sets issue type `Feature`, and requires requesters to describe the desired behavior, the problem/use case, and alternatives or workarounds.

Important APIs/types/functions: issue-form fields include top-level `name`, `description`, `labels`, `type`, and three required `textarea` body entries with ids `feature`, `problem-usecase`, and `alternatives`.

Control flow: when a user chooses the feature template, GitHub renders the form, validates required fields, and creates an issue with the configured labels and type.

State and persistence behavior: no application state; submitted answers persist in GitHub issues and become triage input.

Dependencies/integration: integrates with GitHub Issues, release-note labeling, and policy/triage workflows that rely on conventional labels.

Risks/test signals: overly strict required fields may discourage reports, but they collect context needed to judge feature value. The signal is feature issues arriving with enough structured data and labels for maintainers.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.github/ISSUE_TEMPLATE/01-feature.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.github/ISSUE_TEMPLATE/02-bug.yml -->
# sources/sync-backup/syncthing/.github/ISSUE_TEMPLATE/02-bug.yml

Purpose: GitHub issue form for bug reports. It labels new issues as `bug` and `needs-triage`, sets type `Bug`, warns users away from security reports and support questions, and gathers reproduction details, Syncthing version, platform, optional browser version, and logs.

Important APIs/types/functions: body elements include a markdown warning, required textareas/inputs `what-happened`, `version`, and `platform`, optional `browser`, and shell-rendered `logs`.

Control flow: GitHub renders warnings first, then validates required fields before issue creation. Logs are formatted as shell output automatically.

State and persistence behavior: no local state. Submitted form data becomes persistent GitHub issue content used for debugging and triage.

Dependencies/integration: integrates with GitHub Issues, the forum/support split, security policy, and release-note label categories.

Risks/test signals: missing API-key redaction or private paths in user logs remain a user-submission risk. Maintainer signal is consistently labeled bug reports with version and platform fields present.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.github/ISSUE_TEMPLATE/02-bug.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.github/ISSUE_TEMPLATE/config.yml -->
# sources/sync-backup/syncthing/.github/ISSUE_TEMPLATE/config.yml

Purpose: GitHub issue-template configuration. It disables blank issues and provides contact links for support questions and Android-specific problems.

Important APIs/types/functions: `blank_issues_enabled: false` prevents unstructured issue creation. `contact_links` defines forum support and the separate `syncthing-android` tracker with names, URLs, and descriptions.

Control flow: GitHub uses this file when users open a new issue, forcing selection of templates or contact links instead of blank reports.

State and persistence behavior: no application state; affects repository issue creation UI.

Dependencies/integration: integrates with the Syncthing forum and Android repository to route non-core issues away from the main tracker.

Risks/test signals: disabling blank issues may block valid edge cases not covered by forms. The expected signal is fewer support/Android issues in the core repository and more structured incoming reports.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.github/ISSUE_TEMPLATE/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.github/dependabot.yml -->
# sources/sync-backup/syncthing/.github/dependabot.yml

Purpose: Dependabot configuration for monthly dependency updates. It covers GitHub Actions workflows and direct Go module dependencies, using cooldown periods and grouping to reduce update noise.

Important APIs/types/functions: top-level `version: 2`; two `updates` entries configure `package-ecosystem: github-actions` and `gomod`, both at `/`, monthly schedule, `cooldown.default-days: 14`, and grouped version updates. Go modules are restricted to `dependency-type: direct`.

Control flow: Dependabot periodically scans, waits out cooldown windows, groups matching updates into PRs, and avoids indirect Go dependency churn unless required by direct updates.

State and persistence behavior: no app state; Dependabot state exists in GitHub PRs and update metadata.

Dependencies/integration: integrates with GitHub Actions dependency manifests, `go.mod`, `go.sum`, labeler/policy rules for dependency PRs, and CI gates.

Risks/test signals: grouped updates can make regressions harder to isolate. Direct-only Go updates may leave vulnerable transitive dependencies until direct parents move. Signals are successful monthly PRs labeled/reviewed by automation and passing build workflows.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.github/labeler.yml -->
# sources/sync-backup/syncthing/.github/labeler.yml

Purpose: configuration for the PR metadata labeler. It maps conventional commit-style PR titles to GitHub labels used for triage and release-note categorization.

Important APIs/types/functions: `version: 1` and `labels` entries match `title` regexes: `^feat\b` to `enhancement`, `^fix\b` to `bug`, `^docs\b` to `documentation`, `^chore\b` and `^refactor\b` to `chore`, `^build\b` to `build`, and `^build\(deps\)\b` to `dependencies`.

Control flow: the PR metadata workflow runs the labeler on `pull_request_target` events and applies labels based on the title.

State and persistence behavior: no local state; labels persist on pull requests and affect release notes and policy rules.

Dependencies/integration: tied to `.github/workflows/pr-metadata.yaml`, `.github/release.yml`, and `.policy.yml` conventional-title approval rule.

Risks/test signals: regex ordering and overlaps mean dependency PRs can receive both build-related and dependency semantics depending on labeler behavior. Signal is PR labels matching title conventions and release notes grouping correctly.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.github/labeler.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.github/regsync.yml -->
# sources/sync-backup/syncthing/.github/regsync.yml

Purpose: regclient/regsync configuration for mirroring Syncthing container images from GHCR to Docker Hub.

Important APIs/types/functions: `creds` reads Docker Hub username/token from environment template functions. `defaults` sets rate-limit minimum, retry interval, and parallelism. Three `sync` entries mirror `ghcr.io/syncthing/syncthing`, `ghcr.io/syncthing/relaysrv`, and `ghcr.io/syncthing/discosrv` to matching Docker Hub repositories, allowing tags `latest`, `rc`, `edge`, major, major.minor, semver, and rc semver patterns.

Control flow: the `docker-hub` job runs regsync once with this file after GHCR images are built. Regsync authenticates, lists allowed tags, and copies matching manifests/layers.

State and persistence behavior: registry state changes on Docker Hub; no repository-local state is written.

Dependencies/integration: depends on Docker Hub credentials, GHCR image publication, and `docker://docker.io/regclient/regsync:latest`.

Risks/test signals: permissive numeric regexes can mirror broad major/minor tags intentionally, while missing tags would leave Docker Hub stale. Test signals are successful sync logs and Docker Hub tags matching GHCR for releases/nightlies/edge.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.github/regsync.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.github/release.yml -->
# sources/sync-backup/syncthing/.github/release.yml

Purpose: GitHub release-note generation configuration. It excludes dependency-labeled PRs and groups remaining changes into Fixes, Features, and Other categories.

Important APIs/types/functions: `changelog.exclude.labels` contains `dependencies`; `categories` maps `bug` to `Fixes`, `enhancement` to `Features`, and wildcard labels to `Other`.

Control flow: GitHub release tooling reads this when generating release notes, using PR labels supplied by manual triage and the labeler workflow.

State and persistence behavior: no local state; output becomes release-note text on GitHub releases.

Dependencies/integration: depends on consistent labels from `.github/labeler.yml`, PR metadata automation, and maintainer triage.

Risks/test signals: dependency work is intentionally omitted from generated notes, which can hide important security dependency bumps unless called out manually. Signal is generated releases sorted into the intended categories.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.github/release.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.github/workflows/build-infra-dockers.yaml -->
# sources/sync-backup/syncthing/.github/workflows/build-infra-dockers.yaml

Purpose: GitHub Actions workflow that builds and publishes infrastructure service container images on `infrastructure` and `infra-*` branch pushes.

Important APIs/types/functions: single matrix job `docker-syncthing` builds `stcrashreceiver`, `strelaypoolsrv`, `stupgrades`, and `ursrv`. It sets Go 1.26, `CGO_ENABLED=0`, build metadata, logs into Docker Hub and GHCR, builds linux arm64/amd64 binaries with `go run build.go`, computes branch/sha/latest tags, and uses Docker Buildx with per-package `Dockerfile.<pkg>`.

Control flow: checkout with full history, setup Go, authenticate registries, build binaries for two architectures, set tags, then build/push multi-arch images. Latest tags are added only on the `infrastructure` branch; all branches get sha tags.

State and persistence behavior: no repo files are modified. Persistent outputs are registry images in Docker Hub and `ghcr.io/syncthing/infra`.

Dependencies/integration: relies on `build.go` targets for infrastructure binaries, package-specific Dockerfiles, Docker credentials, GHCR token, QEMU, and Buildx.

Risks/test signals: branch-limited latest tagging protects production-ish images but bad credentials or Dockerfile drift breaks publishing. Test signals are successful matrix jobs and presence of both arch manifests for each infrastructure image.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.github/workflows/build-infra-dockers.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.github/workflows/build-syncthing.yaml -->
# sources/sync-backup/syncthing/.github/workflows/build-syncthing.yaml

Purpose: primary CI, packaging, signing, release, Docker, vulnerability, lint, and metadata workflow for Syncthing. It runs on pull requests, pushes except release branches, workflow calls, and manual dispatch; release-only jobs are gated to Syncthing-owned release/nightly/tag refs.

Important APIs/types/functions: jobs include `facts`, `build-test`, aggregate `basics`, platform packaging for Windows/Linux/illumos/macOS/cross/source/Debian, Windows codesigning, macOS notarization, upgrade signing, nightly publishing, release file publishing, APT publishing, GHCR Docker image build, Docker Hub sync, `govulncheck`, `golangci`, and `meta`. It uses pinned or versioned actions, `build.go` commands, Zig cross-compilers, fpm, gh, rclone, ezapt, Sentry-independent signing utilities, and GitHub artifact upload/download.

Control flow: `facts` derives version, release kind, generation, and Go version. CI tests run across OS and Go-version matrix. Packaging jobs build artifacts and upload them. Release-gated jobs download artifacts, sign them, produce checksums/attestations, sync object storage, publish GitHub releases, publish APT, and mirror Docker images.

State and persistence behavior: persistent outputs include uploaded artifacts, GHCR/Docker Hub images, object-store release/nightly files, GitHub releases, APT repository contents, provenance attestations, signatures, and Debian packages. Build metadata is injected via env and linker flags.

Dependencies/integration: deeply integrated with `build.go`, `build.sh`, `compat.yaml`, `script` tooling, release-tools checkout, repo secrets, Dockerfiles, APT signing, code-signing/notarization services, Codecov-style coverage generation, golangci config, and meta tests.

Risks/test signals: high secret and supply-chain surface. Some actions are pinned to SHAs while core GitHub actions use major tags. Conditional release paths mean PRs do not test signing/notarization/object-store publishing. Strong signals are `basics` passing, generated artifacts for all matrices, successful signature/attestation creation, and release refs producing complete published assets.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.github/workflows/build-syncthing.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.github/workflows/mirrors.yaml -->
# sources/sync-backup/syncthing/.github/workflows/mirrors.yaml

Purpose: mirrors the GitHub repository to Codeberg on push and delete events.

Important APIs/types/functions: job `codeberg` checks out full history and uses `yesolutions/mirror-action` with `REMOTE`, `GIT_SSH_PRIVATE_KEY`, and host verification disabled.

Control flow: when the repository owner is `syncthing`, checkout fetches all refs, then the mirror action pushes changes or deletions to the Codeberg remote.

State and persistence behavior: no local state. Persistent state is the remote mirrored Git repository.

Dependencies/integration: depends on `secrets.CODEBERG_PUSH_KEY`, SSH reachability to Codeberg, and the mirror action revision.

Risks/test signals: `GIT_SSH_NO_VERIFY_HOST: true` trades host verification for automation convenience. Mirror failures may leave Codeberg stale. Signal is Codeberg refs matching GitHub after push/delete events.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.github/workflows/mirrors.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.github/workflows/org-members.yaml -->
# sources/sync-backup/syncthing/.github/workflows/org-members.yaml

Purpose: scheduled/manual workflow for organization membership recommendations.

Important APIs/types/functions: job `run-recommendation` runs the `ghcr.io/calmh/github-org-members:latest` container with environment variables for organization, token, ignored users, and extra repositories.

Control flow: on monthly schedule or manual dispatch, the job starts only for the Syncthing owner and delegates all logic to the container image.

State and persistence behavior: no repository state. Any recommendations or side effects are owned by the external tool and GitHub API.

Dependencies/integration: depends on `GOM_GITHUB_TOKEN`, `GOM_IGNORE_USERS`, `GOM_ALSO_REPOS`, GHCR image availability, and GitHub org/repo APIs.

Risks/test signals: use of a floating `latest` container can change behavior without a repository diff. The workflow has sensitive org/token context. Signal is a completed monthly run producing expected recommendation output.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.github/workflows/org-members.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.github/workflows/pr-metadata.yaml -->
# sources/sync-backup/syncthing/.github/workflows/pr-metadata.yaml

Purpose: PR metadata automation, specifically label application used for release notes and policy decisions.

Important APIs/types/functions: trigger is `pull_request_target` for opened, reopened, edited, and synchronize events. Permissions are read contents and write pull requests. Job `labels` uses `srvaroa/labeler` with `GITHUB_TOKEN`.

Control flow: on eligible PR events, the workflow runs in the base repository context and applies labels according to `.github/labeler.yml`.

State and persistence behavior: labels persist on PRs. No workspace artifacts are retained.

Dependencies/integration: coupled to labeler config, GitHub PR labels, release-note generation, and policy-bot rules.

Risks/test signals: `pull_request_target` has elevated context; this workflow safely avoids checking out or running PR code, but action supply-chain trust still matters. Signal is correct labels after PR title changes or synchronization.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.github/workflows/pr-metadata.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.github/workflows/release-syncthing.yaml -->
# sources/sync-backup/syncthing/.github/workflows/release-syncthing.yaml

Purpose: release-tag automation for pushes to `release` and `release-rc*` branches.

Important APIs/types/functions: job `create-release-tag` checks out full history with `ACTIONS_GITHUB_TOKEN`, sets up stable Go, runs `script/next-version.go` with or without `--pre`, determines previous stable tag, generates notes using `script/relnotes.go`, creates an annotated tag, pushes it, then dispatches `build-syncthing.yaml` for the new tag.

Control flow: release branch chooses stable next version; release-rc branches choose prerelease version. Notes are generated before tag creation. The build workflow is explicitly triggered on `refs/tags/$NEXT`.

State and persistence behavior: creates and pushes Git tags and triggers downstream release artifact state.

Dependencies/integration: depends on release scripts, Git tag history, GitHub token permissions, and `benc-uk/workflow-dispatch`.

Risks/test signals: incorrect version calculation or notes can create bad immutable tags. Signal is an annotated tag with expected notes and a downstream build workflow run for that tag.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.github/workflows/release-syncthing.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.github/workflows/trigger-nightly.yaml -->
# sources/sync-backup/syncthing/.github/workflows/trigger-nightly.yaml

Purpose: scheduled/manual nightly release trigger.

Important APIs/types/functions: workflow runs at 01:00 UTC daily or manually, grants contents write, checks out full history with `ACTIONS_GITHUB_TOKEN`, and pushes `main` to `release-nightly`.

Control flow: the push updates the `release-nightly` branch, which in turn activates release-gated paths in the main build workflow.

State and persistence behavior: mutates the remote `release-nightly` branch and indirectly causes nightly artifacts to be produced.

Dependencies/integration: depends on the main branch, write-capable token, and `build-syncthing.yaml` jobs keyed to `release-nightly`.

Risks/test signals: force-like branch update semantics are not used, but pushing main to nightly can fail on branch protection or divergent refs. Signal is a successful branch update followed by nightly build/publish jobs.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.github/workflows/trigger-nightly.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.github/workflows/update-docs-translations.yaml -->
# sources/sync-backup/syncthing/.github/workflows/update-docs-translations.yaml

Purpose: scheduled/manual workflow for refreshing translations, documentation, contributor lists, and man pages.

Important APIs/types/functions: job checks out full history with write token, sets up stable Go, configures release automation Git identity, runs `bash build.sh translate`, then `bash build.sh prerelease`, and pushes the resulting commit. It consumes `WEBLATE_TOKEN`.

Control flow: `build.sh translate` delegates to `build.go translate`; `build.sh prerelease` runs authors/copyright scripts, Weblate update, manpage refresh, stages `gui`, `man`, and `AUTHORS`, and commits a fixed chore message.

State and persistence behavior: writes and pushes repository commits containing generated docs/translations/contributor metadata.

Dependencies/integration: depends on Go scripts under `script`, Weblate credentials, man refresh tooling, and clean commit generation.

Risks/test signals: scheduled commits can conflict with active changes or produce empty commits if no changes exist. Signal is a pushed chore commit with expected generated files, or a clear no-op/failure if nothing changed.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.github/workflows/update-docs-translations.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.golangci.yml -->
# sources/sync-backup/syncthing/.golangci.yml

Purpose: golangci-lint v2 configuration for Syncthing. It starts from all linters, disables a long list of style/noise-heavy checks, configures exclusions for generated and legacy paths, and enables `gofumpt` formatting.

Important APIs/types/functions: `linters.default: all`, `disable` list, `exclusions.generated: lax`, exclusion presets, path exclusions (`internal/gen`, `internal/db/olddb`, `cmd/dev`, `repos`, `third_party`, `builtin`, `examples`, tests), specific rule suppressions for `sloglint`, `noctx`, `errcheck`, `staticcheck`, and `contextcheck`, plus `settings.sloglint`.

Control flow: the GitHub `golangci` job first regenerates assets, then runs the golangci action with `only-new-issues: true`. Formatter settings let gofumpt enforce formatting while excluding generated/dev/vendor-like paths.

State and persistence behavior: no runtime state; lint results annotate CI/PRs. Formatting settings define expected code shape.

Dependencies/integration: integrates with `.github/workflows/build-syncthing.yaml`, generated assets, Go build tags, and repository package layout.

Risks/test signals: disabling many linters reduces noise but may miss complexity or maintainability issues. Excluding `cmd/dev` intentionally leaves development tools less linted. Signal is PR lint finding only actionable new issues.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/.policy.yml -->
# sources/sync-backup/syncthing/.policy.yml

Purpose: policy-bot approval policy for Syncthing pull requests. It requires conventional commit subjects, acceptable approval routes, and maintainer disapproval authority.

Important APIs/types/functions: top-level `policy.approval` combines subject validation, metadata/maintainer responsibility conditions, and contributor/trivial/dependency/translation approval routes. `approval_rules` define title regexes, maintainer approval for important metadata/docs, contributor approval, contributor-authored translation/dependency/compat updates, trivial small non-feature changes, and maintainer-responsibility label handling.

Control flow: policy-bot evaluates PR title, changed files, modified line count, labels, author team membership, and reviewer team membership. All commits/PRs need valid conventional title shape; project metadata requires maintainer signoff unless a maintainer claims responsibility.

State and persistence behavior: no application state; bot status checks and approval/disapproval decisions persist on PRs.

Dependencies/integration: depends on GitHub teams `syncthing/maintainers` and `syncthing/contributors`, labels from maintainers and automation, and policy-bot validation service.

Risks/test signals: policy complexity can surprise contributors, especially with title regexes and team membership. Good signals are predictable policy-bot statuses, successful validation via the documented API, and low maintainer override need.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/.policy.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/Dockerfile -->
# sources/sync-backup/syncthing/Dockerfile

Purpose: multi-stage Dockerfile for the Syncthing runtime image. It optionally builds the Syncthing binary in a Go builder stage and then packages it into an Alpine-based runtime image.

Important APIs/types/functions: build args include `GOVERSION`, `BUILD_USER`, `BUILD_HOST`, and `TARGETARCH`. The builder checks for a prebuilt `syncthing-linux-$TARGETARCH`; otherwise it runs `go run build.go -no-upgrade build syncthing` and renames the result. Runtime metadata includes OCI labels, exposed GUI/sync/discovery ports, `/var/syncthing` volume, `PUID/PGID/HOME`, `STGUIADDRESS`, and `STHOMEDIR`.

Control flow: Docker always pulls a Go image because Dockerfile sections cannot be conditional. The runtime stage installs certificates, curl, libcap, su-exec, and tzdata, copies the binary and entrypoint, defines a healthcheck against `/rest/noauth/health`, and starts `/bin/entrypoint.sh /bin/syncthing`.

State and persistence behavior: persistent container data lives under `/var/syncthing`, with config at `/var/syncthing/config`. Image build state is discarded between stages except for the copied binary and entrypoint.

Dependencies/integration: integrated with GitHub Docker jobs, `build.go`, `script/docker-entrypoint.sh`, Alpine packages, and multi-arch `TARGETARCH`.

Risks/test signals: relying on `TARGETARCH` naming requires buildx/platform consistency. `CGO_ENABLED=0` in builder affects sqlite/build-tag choices compared to CGO release packages. Signals are successful multi-arch image builds, a healthy container endpoint, and correct persisted config ownership through entrypoint handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/buf.gen.yaml -->
# sources/sync-backup/syncthing/buf.gen.yaml

Purpose: Buf code generation configuration for Syncthing protobuf definitions.

Important APIs/types/functions: `version: v2`; managed mode is enabled with `go_package_prefix` override set to `github.com/syncthing/syncthing/internal/gen`. The Go plugin uses remote `buf.build/protocolbuffers/go:v1.35.1`, outputs into `.`, and sets `module=github.com/syncthing/syncthing`. Input directory is `proto`.

Control flow: `buf generate` reads `proto` definitions, applies managed Go package settings, and writes generated Go files under paths consistent with the module prefix.

State and persistence behavior: generation mutates checked-in generated files under the repository, especially `internal/gen`.

Dependencies/integration: used by `build.go proto` and `updateDependencies`; relies on Buf and the remote protocolbuffers Go plugin.

Risks/test signals: plugin version drift changes generated code. Wrong prefix or module option can put code in unexpected packages. Signal is reproducible `buf generate` output and successful Go builds importing `internal/gen`.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/buf.gen.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/buf.yaml -->
# sources/sync-backup/syncthing/buf.yaml

Purpose: Buf module, lint, and breaking-change policy for Syncthing protobuf definitions.

Important APIs/types/functions: `version: v2`; module path `proto` with name `github.com/syncthing/syncthing`; lint uses `STANDARD`; breaking checks use `WIRE_JSON`.

Control flow: Buf commands load the `proto` module, apply standard lint rules, and check compatibility at wire and JSON levels when a breaking-change baseline is supplied.

State and persistence behavior: no runtime state. It defines validation constraints for protobuf source evolution.

Dependencies/integration: paired with `buf.gen.yaml`, `build.go proto`, generated Go code, and CI or developer commands that run Buf.

Risks/test signals: `WIRE_JSON` focuses compatibility on encoded contracts but may not catch every generated-API compatibility concern. Signal is Buf lint/generate passing after proto changes.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/buf.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/build.go -->
# sources/sync-backup/syncthing/build.go

Purpose: Go-based build orchestration tool for Syncthing. It centralizes target metadata, builds, installs, tests, benchmarks, integration tests, asset/protobuf/mock generation, translations, packaging, Debian package creation, version metadata, code signing, archives, dependency updates, and changelog extraction.

Important APIs/types/functions: `target` describes binaries, Debian names/dependencies/scripts, build packages, archive files, systemd service, install files, and build tags. `archiveFile` carries source, destination, and permissions. `targets` covers `syncthing`, `stdiscosrv`, `strelaysrv`, infrastructure services, and `all`. Major functions include `initTargets`, `runCommand`, `parseFlags`, `test`, `bench`, `integration`, `install`, `build`, `appendParameters`, `buildTar`, `buildZip`, `buildDeb`, `shouldBuildSyso`, `copyFile`, `rebuildAssets`, `lazyRebuildAssets`, `updateDependencies`, `proto`, `translate`, `ldflags`, `getVersion`, `getGitVersion`, `buildStamp`, archive writers, signing helpers, and changelog helpers.

Control flow: `main` parses flags, initializes targets, defaults to `install all` with no args, otherwise executes a command for an explicit or default `syncthing` target. Build/test paths regenerate assets lazily, set `GOOS`, `GOARCH`, and `CC`, append tags/race/pkgdir/install-suffix/ldflags, and invoke external commands. Packaging builds binaries, optionally signs, rewrites archive paths, emits tar/zip/deb artifacts, and writes compatibility JSON for archive builds.

State and persistence behavior: writes binaries, `bin`, `deb`, archives, generated assets, generated protobuf/mock files, `compat.json`, Windows `versioninfo.json`/`resource.syso`, translations, and Debian maintainer scripts. Version state comes from `VERSION`, `RELEASE`, Git tags/describe/branch, build timestamp, user, host, tags, and `EXTRA_LDFLAGS`.

Dependencies/integration: wraps Go toolchain, Git, Buf, fpm, goversioninfo, codesign/security, translation scripts, Weblate/Transifex scripts, release compatibility YAML, and package-specific files under `etc`, `extra`, `man`, `assets`, and `cmd`.

Risks/test signals: many commands call `log.Fatal`, making partial generated files possible on failure. Version derivation and Debian arch normalization are release-sensitive. Zip text files get CRLF conversion while binaries copy verbatim. Strong signals are `go run build.go`, `go run build.go test`, packaging jobs, meta lint, and release workflow artifacts.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/build.sh -->
# sources/sync-backup/syncthing/build.sh

Purpose: shell wrapper around `build.go` and selected scripts. It provides short commands for test, benchmark, prerelease maintenance, and default build delegation.

Important APIs/types/functions: helper `script()` runs `go run script/<name>.go`; helper `build()` runs `go run build.go`. Cases are `test`, `bench`, `prerelease`, and default passthrough.

Control flow: strict Bash mode is enabled. `test` and `bench` set `LOGGER_DISCARD=1` before invoking build commands. `prerelease` regenerates authors, copyrights, Weblate translations, man pages, stages generated docs/translations/contributors, and commits a fixed chore message.

State and persistence behavior: default/test/bench mostly produce build/test artifacts. `prerelease` mutates `gui`, `man`, and `AUTHORS`, and creates a Git commit.

Dependencies/integration: used by the docs/translations workflow and by developers. It depends on Go scripts, `build.go`, manpage refresh script, Git, and Weblate credentials for translation updates.

Risks/test signals: `prerelease` assumes a clean worktree and may fail on no changes or conflicts. The signal is successful wrapper execution and, for prerelease, a generated commit containing only intended maintenance outputs.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stcompdirs/main.go -->
# sources/sync-backup/syncthing/cmd/dev/stcompdirs/main.go

Purpose: development utility that compares multiple directory trees and reports the first content, metadata, symlink, or presence mismatch.

Important APIs/types/functions: `compareDirectories`, `fileInfo`, `startWalker`, and `sha256file`. `fileInfo` captures relative name, mode, modification time, and SHA-256 hash; symlink hash is the link target, directories omit hash and mtime.

Control flow: `main` parses positional dirs and logs `compareDirectories`. One walker goroutine per directory sends sorted `filepath.Walk` results through a channel. The comparator reads one item from each channel, compares against the first directory, aborts other walkers on errors or mismatches, and returns nil only when all walkers finish together.

State and persistence behavior: read-only filesystem traversal. Transient state is channels, abort signal, and SHA-256 hashes.

Dependencies/integration: uses standard library filesystem APIs. It ignores `.stversions` and `.stfolder`, aligning with Syncthing folder internals.

Risks/test signals: `filepath.Walk` ordering is lexical on most platforms but comparison assumes walkers advance in matching order. Hash read errors abort. Signal is nil for identical trees and clear missing/mismatch errors for divergent trees.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stcompdirs/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stdisco/main.go -->
# sources/sync-backup/syncthing/cmd/dev/stdisco/main.go

Purpose: development utility for observing and optionally stimulating Syncthing local discovery announcements over multicast and broadcast beacons.

Important APIs/types/functions: flags `-all`, `-fake`, `-mc`, and `-bc`; globals `randomPrefix` and `myID`; functions `runbeacon`, `recv`, `send`, and `randomDeviceID`. It uses `beacon.Interface`, `discoproto.Announce`, `discover.Magic`, and `protocol.DeviceID`.

Control flow: `main` starts multicast and broadcast beacon servers, starts receive loops for both, and optionally starts fake announcement senders. `recv` validates magic, unmarshals protobuf announcements, filters its own fake ID, suppresses duplicate device/source pairs unless `-all`, and logs device addresses. `send` emits a fake announce every second.

State and persistence behavior: no persistence. Runtime state includes a seen map per receiver and generated fake device ID.

Dependencies/integration: integrates with Syncthing beacon/discovery/protocol libraries and protobuf-generated discovery messages.

Risks/test signals: malformed packets can be dropped silently after unchecked protobuf unmarshal errors. Infinite goroutines run until process exit. Signal is visible announcement logs or fake probes causing peers to respond.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stdisco/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stevents/main.go -->
# sources/sync-backup/syncthing/cmd/dev/stevents/main.go

Purpose: command-line utility that tails Syncthing REST events and prints them as indented JSON.

Important APIs/types/functions: `event` struct models REST event fields `id`, `type`, `time`, and `data`. Flags are `-target`, `-types`, and required `-apikey`.

Control flow: after validating API key, it loops forever issuing `GET http://<target>/rest/events?since=<id>[&events=...]` with `X-API-Key`, decodes the JSON event array, prints each event, and advances `since` to the last event ID.

State and persistence behavior: no persistence. Runtime cursor is the `since` integer, held only in memory.

Dependencies/integration: depends on a running Syncthing GUI/API endpoint and the events REST API. It uses Go's default HTTP client without custom timeout.

Risks/test signals: missing timeout can hang; fatal errors exit on transient HTTP or JSON failures. Signal is continuous JSON event output and monotonically increasing event IDs.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stevents/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stfileinfo/main.go -->
# sources/sync-backup/syncthing/cmd/dev/stfileinfo/main.go

Purpose: development inspection tool for filesystem metadata and Syncthing block hashing of a single path.

Important APIs/types/functions: flag `-s` selects standard block sizing. It uses `os.Lstat`, optional `os.Stat`, `protocol.MinBlockSize`, `protocol.BlockSize`, and `scanner.Blocks`.

Control flow: validates a path argument, prints cleaned path and lstat size/mode/time. For non-directory non-regular paths, it follows with `Stat` output. For regular files it opens the file, chooses whole-file block size unless `-s` or small size triggers standard Syncthing block sizing, then prints scanner block metadata.

State and persistence behavior: read-only filesystem access. No durable state.

Dependencies/integration: integrates with Syncthing protocol block sizing and scanner hashing logic, making it useful for comparing real filesystem observations with Syncthing index data.

Risks/test signals: large files without `-s` may be hashed as one block, which is intentional but not representative of normal indexing. Signal is metadata plus block list output or fatal error on inaccessible paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stfileinfo/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stfinddevice/main.go -->
# sources/sync-backup/syncthing/cmd/dev/stfinddevice/main.go

Purpose: development utility for querying global discovery servers for a device ID and printing advertised addresses.

Important APIs/types/functions: flags `-server` and `-timeout`; `checkResult`, `checkServers`, `checkServer`, and `usage`. It uses `protocol.DeviceIDFromString`, `config.DefaultDiscoveryServers`, `discover.NewGlobal`, and `Lookup`.

Control flow: parses exactly one device ID, chooses either one supplied server or the default discovery server list, launches one goroutine per server, and prints each result with elapsed time, errors, and addresses. Each `checkServer` races lookup against a `time.AfterFunc` timeout.

State and persistence behavior: no persistence. Runtime state is per-server goroutine result channels and timeout timers.

Dependencies/integration: depends on Syncthing discovery libraries, TLS configuration, global discovery server URLs, and network reachability.

Risks/test signals: timeout goroutine can race with lookup result and write to buffered channel; the first result wins. Signal is printed addresses or timeout/error messages per discovery server.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stfinddevice/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stfindignored/main.go -->
# sources/sync-backup/syncthing/cmd/dev/stfindignored/main.go

Purpose: development utility that lists ignored files under a Syncthing folder root using the project's real ignore engine.

Important APIs/types/functions: uses `fs.NewFilesystem`, `fs.NewWalkFilesystem`, `ignore.New`, `Load(".stignore")`, `Walk`, and `Match(path).IsIgnored()`.

Control flow: defaults root to `.`, creates a walkable filesystem rooted there, loads `.stignore`, walks all paths, warns and skips directories on walk errors, and prints paths that match ignore rules.

State and persistence behavior: read-only filesystem traversal. Runtime state is the loaded ignore matcher.

Dependencies/integration: exercises Syncthing's filesystem abstraction and ignore parser/matcher, so behavior should match application ignore semantics more closely than shell glob tools.

Risks/test signals: fatal if `.stignore` is missing or invalid; warnings skip inaccessible subtrees. Signal is printed ignored paths for a real folder.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stfindignored/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stgenfiles/main.go -->
# sources/sync-backup/syncthing/cmd/dev/stgenfiles/main.go

Purpose: development utility that generates a randomized directory tree of files for sync/scanner testing.

Important APIs/types/functions: flags `-dir`, `-files`, `-maxexp`, and `-src`; functions `generateFiles`, `generateOneFile`, `randomName`, `readRand`, and `infiniteReader.Read`.

Control flow: opens a data source, then for each file generates a hex name, sometimes prefixes dotfile marker, creates nested directories based on name bytes, chooses size around a random power of two up to `maxexp`, copies from a looping source reader, chmods random permissions with owner-read forced, and sets mtime within the last 30 days.

State and persistence behavior: creates directories and files, changes permissions and timestamps. Randomness uses `math/rand` without explicit seeding, so generated sequences are deterministic across process starts unless Go runtime seeding changes.

Dependencies/integration: standard library only. Useful for Syncthing scanner/indexer stress data.

Risks/test signals: default `~/files` is not shell-expanded by Go, so it creates a literal path component if not overridden. `log.Fatal` inside helper exits on mkdir errors. Signal is a populated test tree with varied sizes, modes, mtimes, and dotfiles.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stgenfiles/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stsigtool/main.go -->
# sources/sync-backup/syncthing/cmd/dev/stsigtool/main.go

Purpose: development/release utility for generating signing keys, signing data, and verifying Syncthing upgrade signatures.

Important APIs/types/functions: commands `gen`, `sign <privkeyfile> [datafile]`, and `verify <signaturefile> <datafile> [pubkeyfile]`; functions `gen`, `sign`, `verifyWithFile`, and `verifyWithKey`. It uses `lib/signature` and the built-in `upgrade.SigningKey`.

Control flow: command dispatch is based on first argument. `gen` writes private then public key bytes to stdout. `sign` reads a private key, reads data from file or stdin, signs, and writes signature to stdout. `verify` reads signature and data, using either supplied public key or built-in upgrade key, and logs success.

State and persistence behavior: reads key/data files and writes binary output to stdout; no durable files unless shell redirection is used.

Dependencies/integration: used by release workflow to sign archives and by upgrade verification logic through shared signature APIs.

Risks/test signals: usage text does not exit early, so missing args can fall through without an explicit error for unknown command. Binary stdout must be redirected carefully. Signal is successful signature verification or fatal error.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stsigtool/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stvanity/main.go -->
# sources/sync-backup/syncthing/cmd/dev/stvanity/main.go

Purpose: development utility that brute-forces a Syncthing TLS certificate whose derived device ID starts with a requested prefix.

Important APIs/types/functions: `result`, `generatePrefixed`, `printProgress`, `saveCert`, `pemBlockForKey`, and `timeStr`. It uses ECDSA P-384 keys, X.509 self-signed certificates, `protocol.NewDeviceID`, goroutines, `sync.WaitGroup`, and atomic counters.

Control flow: normalizes requested prefix, starts progress reporting, launches one certificate generator per `GOMAXPROCS`, waits for the first result, stops workers, then writes `cert.pem` and `key.pem`. Workers reuse one generated private key and repeatedly create certificates with the fixed template until the device ID prefix matches.

State and persistence behavior: writes `cert.pem` and mode-0600 `key.pem` in the current directory. Runtime state includes stop channel, found channel, and generated certificate attempts.

Dependencies/integration: integrates with Syncthing device ID derivation from certificates.

Risks/test signals: search cost grows exponentially at roughly five bits per base32-like prefix character; long prefixes are refused above 63 bits. Reusing the private key while varying certificate DER is intentional but may surprise users. Signal is a matching printed device ID and saved PEM files.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stvanity/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stwatchfile/main.go -->
# sources/sync-backup/syncthing/cmd/dev/stwatchfile/main.go

Purpose: small polling utility that watches one file for existence, size, mtime, and SHA-256 content changes.

Important APIs/types/functions: flag `-period`, main polling loop, and `sha256file`.

Control flow: validates a path, then sleeps for the configured period, stats the file, reports appearance/disappearance, rejects directories, hashes file content, and prints a line whenever size, modification time, or hash changes.

State and persistence behavior: read-only file access. In-memory state tracks last existence, size, mtime, and hash.

Dependencies/integration: standard library only; useful for observing filesystem behavior during Syncthing sync/scanner/debug scenarios.

Risks/test signals: full-file hashing every period can be expensive for large files. It can race with writers and report transient hash errors. Signal is printed change lines with current size, mtime, and hash.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/dev/stwatchfile/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/diskstore.go -->
# sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/diskstore.go

Purpose: asynchronous compressed disk-backed storage for crash reports, with inventory and retention limits by file count and byte size.

Important APIs/types/functions: `diskStore`, `diskEntry`, `currentFile`, methods `Serve`, `Put`, `Get`, `Exists`, `clean`, `inventory`, and `fullPath`. It stores reports as gzip files under a two-character shard directory.

Control flow: `Serve` creates the directory, inventories existing `.gz` files, cleans over-budget files, then loops on inbox writes, minute cleanup ticks, daily inventory ticks, and context cancellation. Incoming reports are gzip-compressed into a reusable buffer and written to disk. `Put` is non-blocking and returns false when the queue is full. `Get` reads and decompresses. `clean` deletes oldest files until under limits.

State and persistence behavior: persists compressed reports on disk. In-memory `currentFiles` and `currentSize` cache inventory and are updated by writes/clean/inventory.

Dependencies/integration: used by `crashReceiver` HTTP handlers and metrics gauges. Relies on `os`, `gzip`, `filepath.Walk`, `slices.SortFunc`, and Prometheus metrics.

Risks/test signals: newly appended `currentFile.size` uses uncompressed `len(entry.data)` while `currentSize` adds compressed length, so cleanup accounting can drift until inventory. Paths assume report IDs have at least two characters. Signals are successful PUT/GET round trips, retention deleting oldest reports, and diskstore metrics matching inventory after daily refresh.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/diskstore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/main.go -->
# sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/main.go

Purpose: entrypoint and failure-report handling for the Syncthing crash receiver HTTP service. It accepts crash report storage/check requests and, when configured with Sentry DSN, failure report uploads.

Important APIs/types/functions: `cli` config parsed by Kong; `maxRequestSize`; `main`; `handleFailureFn`; `saveFailureWithGoroutines`; `ignorePatterns`, `loadIgnorePatterns`, and `match`. CLI/env settings cover report dir, Sentry DSN, listen addresses, disk and Sentry queue sizes, disk retention limits, and ignore-pattern file.

Control flow: `main` creates disk and Sentry services, loads ignore regexes, wires `crashReceiver` at `/`, `/ping`, optional `/metrics` and pprof, and optional `/newcrash/failure`. Failure handler reads up to 1 MiB, applies ignore patterns, decodes `contract.FailureReport` JSON, parses version, builds Sentry packets, optionally stores goroutine data compressed, fingerprints sanitized message, and sends reports.

State and persistence behavior: persists crash reports under `crash_reports` and failure goroutine dumps under `failure_reports`; exposes metrics; caches Sentry clients elsewhere.

Dependencies/integration: integrates with Kong, raven-go, Prometheus, Syncthing build/version parsing, usage-report contracts, diskStore, sentryService, and ignore regex files.

Risks/test signals: `io.LimitReader` does not explicitly reject over-1MiB bodies, it truncates. `saveFailureWithGoroutines` writes without ensuring parent directories, depending on caller path layout. Signals are `/ping`, metrics, successful crash PUT/HEAD/GET, failure JSON reaching Sentry, and ignore counters incrementing.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/metrics.go -->
# sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/metrics.go

Purpose: Prometheus metric definitions for the crash receiver service.

Important APIs/types/functions: promauto counters/gauges include `crash_reports_total{result}`, `failure_reports_total{result}`, `diskstore_files_total`, `diskstore_bytes_total`, `diskstore_oldest_age_seconds`, `sentry_reports_total{result}`, `ignore_matches_total{pattern}`, `source_code_loads_total{result}`, and `source_code_cache_size`.

Control flow: metrics are registered at package initialization. Other files increment or set them during HTTP handling, disk inventory/cleanup, Sentry send/parse, ignore matching, and source-code loading/cache hits.

State and persistence behavior: metrics are in-memory process state exposed through `/metrics` when metrics listening is enabled. Counters reset on process restart.

Dependencies/integration: uses Prometheus client_golang and `promauto`, and is served from `main.go` via `promhttp.Handler`.

Risks/test signals: high-cardinality `ignore_matches_total` can grow with many regex patterns, but patterns are admin-supplied. Signal is expected metric names and labels appearing in Prometheus scrape output after corresponding operations.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/sentry.go -->
# sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/sentry.go

Purpose: Sentry integration for crash reports and failure reports. It parses Go panic dumps into Sentry packets with stack traces, tags, source context, fingerprints, and user identity.

Important APIs/types/functions: global `loader`, `clients` map and mutex; `sentryService`, `sentryRequest`, methods `Serve` and `Send`; functions `sendReport`, `parseCrashReport`, `sanitizeMessageLDB`, `crashReportFingerprint`, and `packet`. Regexes normalize indexes, sizes, LevelDB positions/checksums/files/internal keys, and local LevelDB paths.

Control flow: `Serve` consumes queued crash reports, parses them, sends to Sentry, and updates result metrics. `parseCrashReport` splits first version line, finds panic/fatal subject, uses `panicparse` to scan goroutines, locks source loader to commit/tag/main, creates reversed Sentry stack frames from the first goroutine, adds report URL, and sets fingerprint. `sendReport` caches Sentry clients per DSN and copies release/environment onto the client before capture.

State and persistence behavior: in-memory Sentry client cache, source-loader lock/cache, and queue. No disk writes here.

Dependencies/integration: raven-go, panicparse, Syncthing build version parsing, sourcecodeloader, crashreceiver HTTP storage, metrics, and Sentry grouping rules.

Risks/test signals: global loader locking serializes source-context loading per parsed report. Empty DSN or Sentry errors surface as send failures. Fingerprint sanitation is crucial to avoid over-splitting corruption reports. Tests cover parsing sample logs and fingerprint normalization.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/sentry.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/sentry_test.go -->
# sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/sentry_test.go

Purpose: tests for crash report parsing and fingerprint normalization in the crash receiver Sentry integration.

Important APIs/types/functions: `TestParseReport` loads `_testdata/*.log`, calls `parseCrashReport`, serializes packet JSON, and prints it. `TestCrashReportFingerprint` table-tests panic messages, expected sanitized fingerprint text, and whether LevelDB-specific grouping should collapse to one fingerprint element.

Control flow: parse test iterates all fixture logs and fails on glob/read/parse/JSON errors. Fingerprint test calls `crashReportFingerprint`, checks expected length (`1` for LevelDB-sanitized messages, `2` for default-plus-message fingerprints), and compares sanitized message.

State and persistence behavior: read-only fixture access; test output prints packet JSON but writes no files.

Dependencies/integration: exercises `parseCrashReport`, Sentry packet JSON generation, version parsing, panicparse, source loader behavior, and regex sanitizers.

Risks/test signals: `TestParseReport` has weak assertions beyond parse/JSON success, so packet content regressions may require golden tests to catch. Fingerprint cases are strong regression signals for known LevelDB and runtime panic patterns.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/sentry_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/sourcecodeloader.go -->
# sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/sourcecodeloader.go

Purpose: raven-go source-code loader that fetches Syncthing source context from GitHub for stack frames in crash reports.

Important APIs/types/functions: constants `urlPrefix`, `httpTimeout`, and `maxCacheEntries`; `cacheKey`; `githubSourceCodeLoader` with mutex, current version, 2Q LRU cache, and HTTP client; methods `LockWithVersion`, `Unlock`, and `Load`; helper `getLineFromLines`.

Control flow: Sentry parsing locks the loader to a version. `Load` normalizes filename, checks cache, identifies `/lib/` or `/cmd/` path segment, fetches raw GitHub content at version plus repo-relative suffix, splits into lines, caches success or nil failure, updates metrics, then returns requested context lines and the target-line index.

State and persistence behavior: in-memory LRU cache keyed by version and file; current version protected by mutex; metrics track loads/cache size.

Dependencies/integration: integrated with raven-go via `raven.SetSourceCodeLoader`, GitHub raw content, panic stack frames, and Prometheus metrics.

Risks/test signals: only `/lib/` and `/cmd/` paths get source context, so other packages are ignored. Network failures are cached as nil for that key, avoiding repeated requests but hiding transient recovery until eviction. Signals are `loaded`, `cached`, and `failed` metrics plus source context appearing in Sentry events.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/sourcecodeloader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/stcrashreceiver.go -->
# sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/stcrashreceiver.go

Purpose: HTTP handler for crash report storage, retrieval, existence checks, filtering, metrics, and Sentry queueing.

Important APIs/types/functions: `crashReceiver` holds `diskStore`, `sentryService`, and optional `ignorePatterns`. Methods are `ServeHTTP`, `serveGet`, `serveHead`, and `servePut`.

Control flow: `ServeHTTP` extracts the final path component, lowercases it, validates it is exactly 64 hex characters, then dispatches GET, HEAD, PUT, or 405. GET returns the uncompressed stored report. HEAD checks existence. PUT reads up to 1 MiB, records first line for logs, applies ignore patterns, stores report asynchronously, sends it to Sentry asynchronously, logs receipt, and increments crash report metrics with the final result.

State and persistence behavior: PUT persists compressed reports through diskStore and enqueues Sentry processing. GET reads persisted reports. Metrics counters capture receive, ignored, queue, and sentry failures.

Dependencies/integration: main mux mounts this handler at `/`; it depends on diskstore, sentry service, ignore matching, `userIDFor`, and standard HTTP semantics.

Risks/test signals: truncated oversized bodies can still be accepted. If disk queue succeeds but Sentry queue fails, result becomes `sentry_failure` even though report was stored. Signal is correct status codes for bad IDs/methods, successful PUT/HEAD/GET round trip, and metrics labels reflecting outcomes.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/stcrashreceiver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/util.go -->
# sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/util.go

Purpose: utility functions for crash receiver user bucketing, report path layout, and gzip file writing.

Important APIs/types/functions: `userIDFor`, `dirFor`, `fullPathCompressed`, and `compressAndWrite`.

Control flow: `userIDFor` chooses `X-Forwarded-For` if present, strips port when possible, combines a fixed salt, address, and current month `YYYYMM`, hashes with SHA-256, and returns the first eight bytes as hex. `dirFor` shards a report ID into two path components. `fullPathCompressed` appends `.gz`. `compressAndWrite` gzip-compresses bytes into a buffer and writes the target file.

State and persistence behavior: `compressAndWrite` writes compressed report data to disk. User IDs rotate monthly and are not persisted here.

Dependencies/integration: used by failure-report storage, Sentry user tagging, and path generation for report URLs.

Risks/test signals: `X-Forwarded-For` may contain multiple IPs and is trusted as-is, so proxy configuration matters. `compressAndWrite` does not create parent directories. Signals are deterministic monthly user IDs for a given source and readable gzip files at expected sharded paths.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/stcrashreceiver/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/auto/doc.go -->
# sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/auto/doc.go

Purpose: package documentation and go-generate directive for generated relay pool server web assets.

Important APIs/types/functions: `//go:generate go run ../../../../script/genassets.go -o gui.files.go ../gui` and package declaration `auto`.

Control flow: `go generate` for this package invokes the repository asset generator to embed files from `cmd/infra/strelaypoolsrv/gui` into `gui.files.go`.

State and persistence behavior: generation writes or updates `gui.files.go` in this package. The source file itself has no runtime state.

Dependencies/integration: used by `build.go rebuildAssets`, which generates this package alongside API GUI assets. Consumers import `auto` to access generated assets.

Risks/test signals: stale generated assets can occur if `go generate` is not run after GUI changes. Signal is generated `gui.files.go` present and builds succeeding without the `noassets` tag.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/auto/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/auto/noassets.go -->
# sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/auto/noassets.go

Purpose: build-tagged stub for relay pool server assets when building with `noassets`.

Important APIs/types/functions: build constraint `//go:build noassets`; `Assets() map[string]assets.Asset` returns nil.

Control flow: when the `noassets` tag is active, this file is compiled instead of relying on generated asset content, allowing static analysis or lightweight builds that do not require embedded GUI files.

State and persistence behavior: no state. It deliberately provides no assets at runtime.

Dependencies/integration: imports `github.com/syncthing/syncthing/lib/assets` for the return type and aligns with DeepSource `noassets` build tag plus build tooling that can avoid asset generation.

Risks/test signals: binaries built with `noassets` will not serve relay pool GUI assets through this package. Signal is successful package compilation with `-tags noassets` and expected nil asset map behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/syncthing/cmd/infra/strelaypoolsrv/auto/noassets.go -->
