# subset-b-007592 Research

Grouped research for selected Kubo CI, build, packaging, RPC client, and CLI daemon files. Each section preserves the original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/gateway-conformance.yml -->
# sources/distributed-fs/ipfs-kubo/.github/workflows/gateway-conformance.yml

## Purpose
This workflow validates Kubo's HTTP gateway behavior against `ipfs/gateway-conformance` fixtures on pushes to `master`, pull requests except Markdown-only changes, and manual dispatch. It has two jobs: a regular gateway conformance run over TCP port 8080 and an experimental trustless gateway-over-libp2p run exposed through a local HTTP-over-libp2p proxy.

## Important APIs, Types, And Functions
The workflow uses reusable actions from `ipfs/gateway-conformance`, `actions/checkout`, `actions/setup-go`, and `actions/upload-artifact`. It configures `Gateway.PublicGateways`, runs `make build`, initializes `cmd/ipfs/ipfs`, imports CAR/IPNS/DNSLink fixtures, starts `ipfs daemon`, and invokes the conformance test action with JSON, XML, HTML, and Markdown outputs.

## Control Flow
Both jobs fetch fixtures, build Kubo, initialize a repo, load fixture data, start the daemon, run conformance tests, and always upload summaries/artifacts. The libp2p job also enables `Experimental.GatewayOverLibp2p` and `Experimental.Libp2pStreamMounting`, starts a second proxy node, connects it to the gateway node, and forwards `/http/1.1` over libp2p.

## State And Persistence Behavior
State is temporary GitHub runner state: Kubo repos under checkout directories, imported blocks, IPNS/DNSLink fixtures, daemon processes, `$GITHUB_ENV` DNS map, and generated conformance reports. No repository source is modified.

## Dependencies And Integration Points
It integrates Kubo's gateway config, DAG import, routing put, daemon startup, libp2p p2p forwarding, DNSLink fixture environment, and external gateway-conformance specs. `jq` is assumed in startup readiness checks.

## Risks And Test Signals
Risks include conformance action version drift, daemon readiness races, skipped CAR content-length coverage, port conflicts, and libp2p forwarding instability. Test signals are conformance action status plus uploaded JSON/HTML/Markdown reports and GitHub step summary output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/gateway-conformance.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/generated-pr.yml -->
# sources/distributed-fs/ipfs-kubo/.github/workflows/generated-pr.yml

## Purpose
This scheduled/manual workflow delegates cleanup of generated pull requests to `ipdxco/unified-github-workflows`.

## Important APIs, Types, And Functions
It grants `issues: write` and `pull-requests: write` and runs a single `stale` job using `reusable-generated-pr.yml@v1`.

## Control Flow
The workflow triggers daily at midnight UTC or by manual dispatch, then the reusable workflow performs all policy logic externally.

## State And Persistence Behavior
It can mutate GitHub PR/issue state through the reusable workflow. The local repository tree is not touched.

## Dependencies And Integration Points
The file depends entirely on the external reusable workflow contract and GitHub token permissions.

## Risks And Test Signals
The main risk is external workflow behavior changing or requiring additional permissions. Signals are scheduled job success and generated PRs being closed or updated as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/generated-pr.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/gobuild.yml -->
# sources/distributed-fs/ipfs-kubo/.github/workflows/gobuild.yml

## Purpose
This CI workflow verifies that `./cmd/ipfs` cross-builds for every platform listed in `.github/build-platforms.yml`.

## Important APIs, Types, And Functions
The single `go-build` job uses `actions/checkout`, `actions/setup-go` with `go.mod`, and a shell loop that parses platform names into `GOOS` and `GOARCH`, then runs `go build -o /dev/null ./cmd/ipfs`.

## Control Flow
On master pushes, pull requests, or manual dispatch, the job runs only in `ipfs/kubo` unless manually dispatched. It uses self-hosted runners for canonical repo CI and `ubuntu-latest` elsewhere.

## State And Persistence Behavior
Only Go module/build caches and ephemeral compiled output are used. No artifacts are persisted.

## Dependencies And Integration Points
It integrates the platform manifest, Go module version, build tags/ldflags from normal Go build behavior, and environment flags used by Kubo's resource-manager checks.

## Risks And Test Signals
Risks include brittle `grep` parsing of YAML, unsupported platform names with extra hyphens, and platform-specific compile breakage. Success is every listed platform compiling `cmd/ipfs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/gobuild.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/golang-analysis.yml -->
# sources/distributed-fs/ipfs-kubo/.github/workflows/golang-analysis.yml

## Purpose
This workflow enforces Go source hygiene: tidy module files, `go fmt`, `go fix`, and `go vet`.

## Important APIs, Types, And Functions
It uses `protocol/multiple-go-modules@v1.4` for multi-module `go mod tidy` and `go vet`, plain `go fmt ./...`, and `go fix ./...` followed by `git diff` checks.

## Control Flow
After checkout with recursive submodules and Go setup, the job runs tidy, formatting, fix, and vet steps. Later steps use `if: always()` so multiple classes of hygiene failures can be reported in one run.

## State And Persistence Behavior
The workflow intentionally detects generated local modifications to `go.mod`, `go.sum`, or source files and fails instead of persisting them.

## Dependencies And Integration Points
It integrates Go tooling, all Go modules in the repository, Git diff state, and submodule checkout.

## Risks And Test Signals
Risks include `go fix` behavior changes across Go versions and multi-module action drift. Signals are empty formatter output, no post-tidy/post-fix diff, and successful vet.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/golang-analysis.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/golint.yml -->
# sources/distributed-fs/ipfs-kubo/.github/workflows/golint.yml

## Purpose
This workflow runs the repository lint target for Go code.

## Important APIs, Types, And Functions
The job sets Kubo test/lint environment variables, checks out the repo, sets up Go from `go.mod`, and runs `make -O test_go_lint`, which is backed by the Make rules and `.golangci.yml`.

## Control Flow
It runs on master pushes, pull requests except Markdown-only changes, and manual dispatch, gated to the canonical repo unless manually triggered.

## State And Persistence Behavior
Linting is read-only aside from Go/action caches and temporary build outputs.

## Dependencies And Integration Points
It integrates Make rules, `golangci-lint`, the Go module graph, and Kubo's resource manager default check environment.

## Risks And Test Signals
Risks include linter version changes in Make dependencies and repository-specific runner differences. The test signal is `make test_go_lint` exiting successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/golint.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/gotest.yml -->
# sources/distributed-fs/ipfs-kubo/.github/workflows/gotest.yml

## Purpose
This workflow runs Kubo's main Go test lanes: unit tests with coverage, CLI integration tests, FUSE tests, and example tests.

## Important APIs, Types, And Functions
Jobs call `make test_unit`, `make test_cli`, `make test_fuse`, and `make test_examples`. They use Codecov, `ipdxco/gotest-json-to-junit-xml`, `ipdxco/junit-xml-to-html`, and `actions/upload-artifact` to convert and publish reports.

## Control Flow
Unit and CLI jobs install `zsh`; CLI and FUSE tests set `IPFS_PATH` to runner temp dirs. FUSE tests install `fuse3` when needed, clean stale mounts before and after tests, and run with `GOTRACEBACK=all`. Each report-generation/upload step runs on success or failure.

## State And Persistence Behavior
The workflow creates coverage profiles, JSON test logs, JUnit XML, HTML/Markdown reports, temporary repos, and temporary FUSE mounts. Artifacts and coverage are persisted externally.

## Dependencies And Integration Points
It integrates Kubo Make targets, test harnesses, FUSE kernel/userland tools, Codecov, report conversion tools, and GitHub self-hosted runner labels.

## Risks And Test Signals
Risks include FUSE mount leakage, self-hosted runner state, report conversion failures hiding raw test context, and Make target coupling. Signals include no failed entries in `gotest.json`, successful CLI/FUSE/example targets, uploaded reports, and coverage artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/gotest.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/interop.yml -->
# sources/distributed-fs/ipfs-kubo/.github/workflows/interop.yml

## Purpose
This workflow tests Kubo interoperability with Helia and the IPFS WebUI.

## Important APIs, Types, And Functions
`interop-prep` builds `cmd/ipfs/ipfs` and uploads it as an artifact. `helia-interop` downloads the binary, installs the current `@helia/interop`, and runs `npx aegir test`. `ipfs-webui` checks out `ipfs/ipfs-webui`, installs Node dependencies and Playwright, builds the WebUI test app, and runs E2E tests with `IPFS_GO_EXEC`.

## Control Flow
Both interop jobs depend on the built Kubo artifact. Caches are keyed by npm package versions, lockfiles, Playwright browser metadata, and WebUI sources. A known Helia MFS CID mismatch test is excluded pending IPIP-499 alignment.

## State And Persistence Behavior
The workflow persists the Kubo binary artifact and caches Node modules, Playwright browsers, and WebUI build output. Failure artifacts include WebUI test results.

## Dependencies And Integration Points
It integrates Kubo's daemon/binary behavior with external JS IPFS implementations, Playwright/browser dependencies, GitHub commit status via `gh api`, and WebUI E2E configuration.

## Risks And Test Signals
Risks include latest `@helia/interop` drift, external repo instability, network/npm failures, and the explicit skip masking one compatibility gap. Signals are successful Helia Aegir tests and WebUI E2E tests against the local Kubo binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/interop.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/sharness.yml -->
# sources/distributed-fs/ipfs-kubo/.github/workflows/sharness.yml

## Purpose
This workflow runs the legacy sharness integration suite and publishes coverage plus rich HTML reports.

## Important APIs, Types, And Functions
It calls `make -O -j "$PARALLEL" test_sharness coverage/sharness_tests.coverprofile test/sharness/test-results/sharness.xml`, aggregates `.counts` files with `aggregate-results.sh`, converts JUnit XML to one-page and frames HTML reports, and uploads via custom S3 artifact action for canonical repo runs.

## Control Flow
The job checks out Kubo into `kubo`, installs Go and shell/network utilities, caches sharness report-generation dependencies, runs tests with Docker enabled and FUSE/plugin disabled, verifies the aggregate summary contains zero failures, and uploads reports regardless of success.

## State And Persistence Behavior
It creates test result XML, counts, summaries, coverage profiles, and HTML report directories under `kubo/test/sharness/test-results`; reports and coverage are persisted externally.

## Dependencies And Integration Points
It integrates Make sharness rules, Docker-backed sharness tests, Codecov, S3/custom artifact upload, and report conversion workflows.

## Risks And Test Signals
Risks include parallel sharness flakiness, Docker/service dependencies, custom upload failures, and summary parsing coupled to text format. Signals are zero failed counts, successful Make target, coverage upload, and generated reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/sharness.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/spellcheck.yml -->
# sources/distributed-fs/ipfs-kubo/.github/workflows/spellcheck.yml

## Purpose
This workflow delegates repository spell checking to a unified reusable workflow.

## Important APIs, Types, And Functions
It grants read-only contents access and runs `ipdxco/unified-github-workflows/.github/workflows/reusable-spellcheck.yml@v1`.

## Control Flow
It runs on pull requests, master pushes, and manual dispatch. All spellcheck implementation details live in the reusable workflow.

## State And Persistence Behavior
The workflow is read-only with respect to repository contents.

## Dependencies And Integration Points
It depends on the external unified workflow and whatever spelling dictionaries/configuration that workflow expects from this repository.

## Risks And Test Signals
Risks are external workflow drift and false positives from project-specific vocabulary. The signal is the reusable spellcheck job status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/spellcheck.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/stale.yml -->
# sources/distributed-fs/ipfs-kubo/.github/workflows/stale.yml

## Purpose
This scheduled/manual workflow delegates stale issue handling to a unified reusable workflow.

## Important APIs, Types, And Functions
It grants write permissions to issues and pull requests and invokes `reusable-stale-issue.yml@v1`.

## Control Flow
The workflow runs daily at midnight UTC or by manual dispatch. The downstream reusable workflow owns all labeling/commenting/closing policy.

## State And Persistence Behavior
It can mutate GitHub issue and PR metadata but does not modify repository files.

## Dependencies And Integration Points
It integrates with GitHub Issues and PR APIs through the reusable workflow and token permissions.

## Risks And Test Signals
Risks include incorrect stale policy inherited from the external workflow and permission drift. Signals are successful scheduled runs and expected stale issue transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/stale.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/sync-release-assets.yml -->
# sources/distributed-fs/ipfs-kubo/.github/workflows/sync-release-assets.yml

## Purpose
This workflow syncs missing binary release assets from `dist.ipfs.tech` into the latest GitHub releases.

## Important APIs, Types, And Functions
It starts an IPFS daemon via `ipfs/start-ipfs-daemon-action`, uses `actions/github-script` to call `github.rest.repos.listReleases` and `uploadReleaseAsset`, runs `ipfs ls/get` against `/ipns/dist.ipfs.tech/kubo/<tag>`, and verifies downloaded files with `sha512sum`.

## Control Flow
For up to five recent releases, it compares GitHub asset names to dist assets, skips files lacking both `.sha512` and `.cid` companions, downloads missing triples, validates checksums, and uploads the file plus checksum sidecars to the GitHub release.

## State And Persistence Behavior
State includes local downloaded artifacts, release asset lists, IPFS daemon repo state, and GitHub release assets. Successful runs persist uploaded assets to GitHub.

## Dependencies And Integration Points
It integrates GitHub Releases, IPNS resolution for `dist.ipfs.tech`, Kubo distribution naming, checksum conventions, and Node/GitHub Script APIs.

## Risks And Test Signals
Risks include IPNS/network unavailability, asset parsing assumptions around `ipfs ls`, off-by-one sync count behavior, and partial uploads. Signals are checksum success and uploaded assets appearing on recent releases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/sync-release-assets.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/test-migrations.yml -->
# sources/distributed-fs/ipfs-kubo/.github/workflows/test-migrations.yml

## Purpose
This workflow validates repository migration and update behavior across Linux, Windows, and macOS.

## Important APIs, Types, And Functions
It builds Kubo with `make build`, adds `cmd/ipfs` to `PATH`, runs `go test ./repo/fsrepo/migrations/...`, `go test ./test/cli/migrations/...`, and `go test -run "TestUpdate" ./test/cli/...`.

## Control Flow
It runs on manual dispatch and on changes to migration, repo, update, CLI migration, or workflow files. A matrix covers `ubuntu-latest`, `windows-latest`, and `macos-latest`; macOS runs a DNS reconfiguration step before update tests to mitigate resolver flakiness.

## State And Persistence Behavior
It creates built binaries, temporary IPFS repos under runner temp, logs, and uploaded failure/success artifacts containing test logs and temp repo contents.

## Dependencies And Integration Points
It integrates fsrepo migration code, CLI migration tests, update command tests that may use GitHub APIs, OS-specific shell behavior, and runner DNS configuration.

## Risks And Test Signals
Risks include path/PATH differences on Windows, real-network update tests, and broad artifact uploads exposing temp state. Signals are successful migration package tests, CLI migration tests, and `TestUpdate` on all OSes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/test-migrations.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.golangci.yml -->
# sources/distributed-fs/ipfs-kubo/.golangci.yml

## Purpose
This file configures `golangci-lint` for the Kubo Go lint target.

## Important APIs, Types, And Functions
It enables `stylecheck`, turns on all stylecheck checks, disables `ST1003`, and permits dot imports from `github.com/ipfs/kubo/test/cli/testutils`.

## Control Flow
The configuration is consumed by `make test_go_lint` and the `golint.yml` workflow.

## State And Persistence Behavior
It is static lint policy with no runtime state.

## Dependencies And Integration Points
It integrates with GolangCI-Lint's stylecheck linter and repository test helper conventions.

## Risks And Test Signals
Risks include stylecheck option changes or `ST1003` exceptions hiding naming issues. Test signal is lint passing under this configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.hadolint.yaml -->
# sources/distributed-fs/ipfs-kubo/.hadolint.yaml

## Purpose
This file configures Dockerfile linting for the Kubo container image.

## Important APIs, Types, And Functions
It ignores Hadolint rule `DL3008` for pinned apt package versions and trusts base images from `docker.io` and `gcr.io`.

## Control Flow
Hadolint consumes this file when Docker image lint checks run.

## State And Persistence Behavior
It is static configuration only.

## Dependencies And Integration Points
It integrates with the repository `Dockerfile`, Hadolint, and the image supply chain policy.

## Risks And Test Signals
The accepted risk is looser apt package pinning in exchange for stable base images and smaller layers. Signals are Dockerfile lint checks passing except for intentionally ignored DL3008.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.hadolint.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/Dockerfile -->
# sources/distributed-fs/ipfs-kubo/Dockerfile

## Purpose
The Dockerfile builds and packages Kubo into a minimal `busybox:stable-glibc` runtime image with the `ipfs` binary, FUSE helper, TLS certificates, `tini`, `gosu`, and container startup scripts.

## Important APIs, Types, And Functions
It has three stages: `builder` based on `golang:${GO_VERSION}`, `utilities` based on Debian for runtime helper binaries, and final BusyBox runtime. Build args include `GO_VERSION`, `TARGETOS`, `TARGETARCH`, `IPFS_PLUGINS`, and `MAKE_TARGET`.

## Control Flow
The builder caches Go modules/build output, copies the tree, creates `.git/objects` for version metadata, and runs `make ${MAKE_TARGET}`. The final stage copies helpers and scripts, creates the `ipfs` user and repo/mount directories, exposes swarm/API/gateway ports, sets healthcheck, and defaults to `daemon --migrate=true --agent-version-suffix=docker`.

## State And Persistence Behavior
`/data/ipfs` is the persistent volume via `IPFS_PATH`; `/ipfs`, `/ipns`, `/mfs`, and `/container-init.d` are runtime directories. Health checks query the local RPC API.

## Dependencies And Integration Points
It integrates Make build targets, `bin/container_daemon`, `bin/container_init_run`, FUSE, runtime privilege drop via `gosu`, and daemon health semantics.

## Risks And Test Signals
Risks include Go version drift, glibc/helper compatibility, FUSE SUID security, and API healthcheck assumptions. Signals are successful multi-stage build, runnable daemon, and passing `ipfs diag healthy`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/FUNDING.json -->
# sources/distributed-fs/ipfs-kubo/FUNDING.json

## Purpose
This metadata file declares an Optimism Retro Funding project identifier for Kubo.

## Important APIs, Types, And Functions
It contains a single `opRetro.projectId` string.

## Control Flow
There is no code flow; consumers parse the JSON metadata.

## State And Persistence Behavior
It is static project funding metadata.

## Dependencies And Integration Points
It integrates with funding/indexing systems that understand the `opRetro` schema.

## Risks And Test Signals
Risks are invalid JSON or an incorrect project ID. Test signals are successful JSON parsing and correct recognition by funding tooling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/FUNDING.json -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/GNUmakefile -->
# sources/distributed-fs/ipfs-kubo/GNUmakefile

## Purpose
This wrapper makes GNU Make behavior available when the user invokes `gmake`.

## Important APIs, Types, And Functions
It sets `SHELL`, enables `.SECONDEXPANSION`, includes `Rules.mk`, and defines `all` plus `.DEFAULT` to delegate to `gmake`.

## Control Flow
Targets flow into the common Make rule graph in `Rules.mk`.

## State And Persistence Behavior
It only influences build invocation state; generated files are owned by included rules.

## Dependencies And Integration Points
It integrates with GNU Make and all included `mk/*.mk` fragments.

## Risks And Test Signals
Risks are recursive/delegation confusion on systems where `make` and `gmake` differ. Signal is standard targets resolving through `Rules.mk`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/GNUmakefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/Makefile -->
# sources/distributed-fs/ipfs-kubo/Makefile

## Purpose
This small wrapper delegates ordinary `make` invocations to GNU Make.

## Important APIs, Types, And Functions
It defines `all` and `.DEFAULT` targets that execute `gmake $@`.

## Control Flow
Any target requested through `make` is handed to `gmake`, which then loads `GNUmakefile`/`Rules.mk`.

## State And Persistence Behavior
It creates no state directly.

## Dependencies And Integration Points
It assumes `gmake` exists and is the intended build engine.

## Risks And Test Signals
Risks are missing `gmake` or recursive make edge cases. Signal is `make build`, `make test`, and other targets dispatching to GNU Make successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/Rules.mk -->
# sources/distributed-fs/ipfs-kubo/Rules.mk

## Purpose
This is Kubo's central Make rule file. It initializes target accumulators, imports shared Make fragments, selects tags, includes subdirectory rules, and defines top-level build/test/clean/help targets.

## Important APIs, Types, And Functions
Key variables include `TGT_BIN`, `CLEAN`, `COVERAGE`, `DISTCLEAN`, `TEST`, `TEST_SHORT`, `GOCC`, `PROTOC`, `GOTAGS`, and `LIBP2P_TCP_REUSEPORT`. Targets include `build`, `clean`, `mod_tidy`, `coverage`, `distclean`, `test`, `test_short`, `nofuse`, `install`, `uninstall`, `supported`, and `help`.

## Control Flow
It includes `mk/git.mk`, `mk/tarball.mk`, `mk/util.mk`, and `mk/golang.mk`, then sub-rules for `bin`, `plugin`, `test`, and `cmd/ipfs`. Coverage rules are included only when coverage-related goals are requested.

## State And Persistence Behavior
Rules create binaries, generated protobuf files, coverage output, test output, and cleanup sets. `distclean` is destructive for untracked build products through `git clean -ffxd`.

## Dependencies And Integration Points
It integrates Go, protoc, plugin/test/cmd rule fragments, `.github/build-platforms.yml`, and repo-wide environment flags.

## Risks And Test Signals
Risks include target accumulator ordering, conditional coverage inclusion, and destructive `distclean`. Signals are successful top-level build/test targets and accurate `help`/`supported` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/Rules.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/assets/assets.go -->
# sources/distributed-fs/ipfs-kubo/assets/assets.go

## Purpose
This package embeds the default init documentation and seeds it into a newly initialized Kubo node.

## Important APIs, Types, And Functions
`Asset embed.FS` embeds `init-doc`. `SeedInitDocs` calls `addAssetList` over fixed paths such as `about`, `readme`, `help`, and `quick-start`. `addAssetList` creates a CoreAPI, loads embedded files, builds a `files.NewMapDirectory`, adds it through `Unixfs().Add`, pins the resulting path, and returns the root CID.

## Control Flow
Initialization code calls `SeedInitDocs`; every embedded path is read into a bytes file, added as a directory, then pinned.

## State And Persistence Behavior
It persists embedded docs into the node blockstore and pinset. Failure before pinning can leave partially added blocks depending on lower-level add behavior.

## Dependencies And Integration Points
It integrates Go `embed`, Kubo `coreapi`, Boxo `files`, UnixFS add, and pin APIs. `cmd/ipfs/kubo/init.go` uses this for non-empty repo initialization.

## Risks And Test Signals
Risks include missing embedded asset paths, add/pin failures, and initialization relying on a live in-process node. Signals are `ipfs init` printing a readable `/ipfs/<cid>/readme` path and the returned CID being pinned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/assets/assets.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/Rules.mk -->
# sources/distributed-fs/ipfs-kubo/bin/Rules.mk

## Purpose
This Make fragment defines helper binaries and path setup for the `bin` directory.

## Important APIs, Types, And Functions
It sets a distribution root, adds `bin` to `PATH`, creates a `bin/protoc` wrapper/symlink target, builds `bin/protoc-gen-gogofaster` via Go, and appends generated files to `CLEAN`/`DISTCLEAN`.

## Control Flow
Included from root `Rules.mk`, it participates in the shared Make target accumulator pattern using `mk/header.mk` and `mk/footer.mk`.

## State And Persistence Behavior
It creates local helper binaries/symlinks under `bin` and temporary distribution cache under `bin/tmp`.

## Dependencies And Integration Points
It integrates Make utility macros, Windows-specific copy behavior, Go build of `github.com/gogo/protobuf/protoc-gen-gogofaster`, and protobuf generation targets.

## Risks And Test Signals
Risks include stale symlinks, Windows executable suffix handling, and external tool version drift. Signals are generated protobuf rules finding `protoc` and `protoc-gen-gogofaster`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/Rules.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/archive-branches.sh -->
# sources/distributed-fs/ipfs-kubo/bin/archive-branches.sh

## Purpose
This maintenance script moves inactive branches from the main GitHub repo to an archive repository and deletes them from origin after confirmation.

## Important APIs, Types, And Functions
Functions include `gh_api_next` for paginated GitHub API responses, `gh_api`, `pr_branches`, `origin_refs`, and `active_branches`. It uses `curl`, `jq`, `git for-each-ref`, `awk`, `comm`, and `git push`.

## Control Flow
The script adds an `archived` remote, computes branches that are neither active within the last month nor attached to PRs nor excluded, prints them, requires a yes confirmation, pushes each branch to the archive under a date suffix, then deletes the origin branch.

## State And Persistence Behavior
It mutates Git remotes by adding `archived`, creating archive refs, and deleting branches from origin.

## Dependencies And Integration Points
It integrates GitHub REST API, local remote-tracking refs, and SSH access to `ipfs/go-ipfs-archived`.

## Risks And Test Signals
Risks are high because it deletes branches, assumes old repo names, and relies on correct API pagination/filtering. Signals are the printed branch list and successful archive push before origin delete.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/archive-branches.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/container_daemon -->
# sources/distributed-fs/ipfs-kubo/bin/container_daemon

## Purpose
This shell entrypoint initializes or opens the container's IPFS repo, drops root privileges to the `ipfs` user, configures API/gateway binding, loads optional swarm keys, runs init hooks, and execs `ipfs`.

## Important APIs, Types, And Functions
It uses `gosu`, `$IPFS_PATH`, `$IPFS_PROFILE`, `$IPFS_SWARM_KEY`, `$IPFS_SWARM_KEY_FILE`, `ipfs init`, `ipfs config`, `install`, `find`, `sort`, `xargs`, and `container_init_run`.

## Control Flow
When run as root it ensures repo ownership and re-execs as `ipfs`. As the unprivileged user it prints `ipfs version`, initializes the repo if missing, writes network defaults, copies swarm key material if supplied, executes `/container-init.d/*.sh`, and finally `exec ipfs "$@"`.

## State And Persistence Behavior
It persists repo config and optional `swarm.key` under `$IPFS_PATH`, changes ownership, and executes arbitrary container init scripts.

## Dependencies And Integration Points
It integrates the Dockerfile entrypoint, container volume layout, private swarm configuration, and Kubo daemon command.

## Risks And Test Signals
Risks include recursive chown cost, secrets passed through environment, hook script failures aborting startup, and API binding to all interfaces. Signals are initialized config, copied swarm key permissions, hook execution logs, and successful daemon start.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/container_daemon -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/container_init_run -->
# sources/distributed-fs/ipfs-kubo/bin/container_init_run

## Purpose
This helper runs one container initialization script from `/container-init.d`.

## Important APIs, Types, And Functions
It accepts one script path. Executable scripts are run as child processes; non-executable scripts are sourced into the current shell.

## Control Flow
The script prints whether it is executing or sourcing, then runs the script under `set -e`.

## State And Persistence Behavior
Executable scripts mutate only their child process environment and external state; sourced scripts can mutate the current shell environment before the daemon exec.

## Dependencies And Integration Points
It is invoked by `container_daemon` via sorted `find`/`xargs`.

## Risks And Test Signals
Risks include arbitrary hook behavior, sourced script side effects, and startup aborts on failures. Signal is each hook's printed execution line and container startup continuing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/container_init_run -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/dist_get -->
# sources/distributed-fs/ipfs-kubo/bin/dist_get

## Purpose
This portable shell script downloads and extracts a named binary distribution from the IPFS distribution site for the current or specified Go platform.

## Important APIs, Types, And Functions
Functions include `die`, `have_binary`, `check_writable`, `try_download`, `download`, `unarchive`, `get_go_vars`, and `mkurl`. It supports `wget`, `curl`, `fetch`, `http`, `ftp`, `tar`, and `unzip`.

## Control Flow
The script validates `<distroot> <distname> <outpath> <version>`, requires `v*` versions, determines `GOOS-GOARCH`, selects `tar.gz` or `zip`, downloads to `bin/tmp`, extracts the binary named after the distribution, and chmods it executable.

## State And Persistence Behavior
It writes archives into `bin/tmp` and the extracted executable to `outpath`, including `.exe` suffix on Msys/Cygwin.

## Dependencies And Integration Points
It integrates Make helper downloads, Go environment detection, and `https://ipfs.io` distribution URL layout.

## Risks And Test Signals
Risks include `eval`-based downloader commands, dependency on Go for platform detection, unsupported OS strings, and no checksum verification. Signals are a downloaded archive and executable output file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/dist_get -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/gencmdref -->
# sources/distributed-fs/ipfs-kubo/bin/gencmdref

## Purpose
This Python utility generates a Markdown command reference by running `--help` for command lines supplied on stdin.

## Important APIs, Types, And Functions
`main` reads stdin lines, prints a top-level title/date/table of contents, then for each command runs `check_output((line + ' --help').split(' '))` and embeds the output in a fenced code block.

## Control Flow
With `-h` or `--help`, it prints usage. Otherwise it processes every input command in order.

## State And Persistence Behavior
It is a stdout generator only; callers redirect output to a Markdown file.

## Dependencies And Integration Points
It integrates with `ipfs commands` output and the local `ipfs` executable/command help system.

## Risks And Test Signals
Risks include Python 2 style print syntax, naive space splitting, and command help failures aborting generation. Signal is a complete Markdown command reference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/gencmdref -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/get-docker-tags.sh -->
# sources/distributed-fs/ipfs-kubo/bin/get-docker-tags.sh

## Purpose
This script computes Docker image tags that should be published for a build, without performing any Docker operations.

## Important APIs, Types, And Functions
It consumes build number, commit SHA, branch, optional Git tag, and `$IMAGE_NAME`. `echoImageName` emits `IMAGE_NAME:tag`.

## Control Flow
Release candidates emit their version tag. Stable semver tags emit version, `latest`, and `release`. `bifrost-*` branches emit sanitized branch/build/SHA tags. `master` and `staging` emit build/SHA and `*-latest` tags. Other branches print "Nothing to do."

## State And Persistence Behavior
The script is read-only and writes computed tags to stdout.

## Dependencies And Integration Points
It integrates Git metadata, CI build numbers, and Docker tag naming policy.

## Risks And Test Signals
Risks include regex policy drift and branch sanitization collisions. Signals are expected tag lists for release, RC, master, staging, and no-op branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/get-docker-tags.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/graphmd -->
# sources/distributed-fs/ipfs-kubo/bin/graphmd

## Purpose
This shell utility emits Graphviz DOT edges for the recursive MerkleDAG references under an IPFS path.

## Important APIs, Types, And Functions
It calls `ipfs refs -r --format="$fmt"` with node and edge templates, wraps output in `digraph { ... }`, and suggests piping to `dot`.

## Control Flow
The script requires exactly one IPFS path argument, prints usage otherwise, then emits graph attributes and indented edge lines.

## State And Persistence Behavior
It is read-only against the daemon/blockstore and writes DOT to stdout.

## Dependencies And Integration Points
It integrates `ipfs refs`, Graphviz, and recursive DAG traversal.

## Risks And Test Signals
Risks include large DAG output volume and needing a running API for `ipfs refs`. Signal is valid DOT renderable by `dot`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/graphmd -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/ipns-republish -->
# sources/distributed-fs/ipfs-kubo/bin/ipns-republish

## Purpose
This operational helper repeatedly republishes an IPNS name for a target IPFS/IPNS path every 20 minutes.

## Important APIs, Types, And Functions
It validates online daemon state with `ipfs swarm peers`, validates content with `ipfs dag stat`, then loops over `ipfs name publish "$1"` and `sleep 1200`.

## Control Flow
The script requires one path argument, exits if offline or content is missing, then runs an infinite publish loop.

## State And Persistence Behavior
It mutates the node's IPNS record and publishes it to the network on each loop.

## Dependencies And Integration Points
It integrates the local daemon, swarm connectivity, DAG availability, and IPNS publishing.

## Risks And Test Signals
Risks include infinite foreground execution, no signal cleanup, no retry/backoff, and repeated publish failures. Signals are successful initial checks and repeated `ipfs name publish` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/ipns-republish -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/maketarball.sh -->
# sources/distributed-fs/ipfs-kubo/bin/maketarball.sh

## Purpose
This release helper creates a source tarball with vendored Go dependencies and normalized permissions.

## Important APIs, Types, And Functions
It uses `mktemp`, `cp -r`, `go mod vendor`, `git describe`, `chmod -R`, and `tar -czf`, with output defaulting to `go-ipfs-source.tar.gz`.

## Control Flow
The script resolves output to an absolute path, copies the working tree to a temp dir, vendors modules, writes `.tarball` metadata, normalizes permissions, creates a gzipped tar excluding `.git`, then removes the temp dir.

## State And Persistence Behavior
It writes the output tarball and transient temp tree. It does not modify the source checkout.

## Dependencies And Integration Points
It integrates Go modules, Git metadata, and release source distribution packaging.

## Risks And Test Signals
Risks include copying untracked local files into the tarball and no trap cleanup on interruption. Signals are a tarball containing vendored dependencies and `.tarball` metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/maketarball.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/mkreleaselog -->
# sources/distributed-fs/ipfs-kubo/bin/mkreleaselog

## Purpose
This Bash release tool generates changelog and contributor statistics for a Kubo release range, including selected dependency changes.

## Important APIs, Types, And Functions
It defines module include/exclude regexes, ignored pathspecs, GitHub handle cache helpers, handle resolution from noreply emails/merge commits/GitHub API, dependency diff helpers (`mod_deps`, `dep_changes`, `resolve_commits`), changelog generation (`release_log`, `recursive_release_log`), stats extraction (`statlog`, `statsummary`), and repository fetching (`ensure`).

## Control Flow
`recursive_release_log` chooses start/end refs, loads handle cache, creates a temp workspace, snapshots old/new `go.mod`, computes dependency changes, emits main-module changelog, ensures changed dependency repos are available, appends dependency changelogs, builds stats JSON, prints a contributor table, and saves the GitHub handle cache.

## State And Persistence Behavior
It reads Git history across Kubo and dependency repos, may clone/fetch dependencies under `$GOPATH/src`, writes temporary JSON in a temp dir, and persists `~/.cache/mkreleaselog/github-handles.json` atomically.

## Dependencies And Integration Points
It depends on `git`, `go`, `jq`, optional authenticated `gh`, semver-ish Go module versions, `.mailmap`, and GitHub repository naming conventions.

## Risks And Test Signals
Risks include API rate limits, dependency repo fetch failures, fragile commit subject parsing, ignored-file pathspec mistakes, and cache corruption. Signals are a Markdown changelog, dependency sections, contributor table, and cache load/save diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/mkreleaselog -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/push-docker-tags.sh -->
# sources/distributed-fs/ipfs-kubo/bin/push-docker-tags.sh

## Purpose
This legacy CI script tags and pushes Docker images based on branch or release tag policy.

## Important APIs, Types, And Functions
It accepts build number, commit SHA, branch, optional tag, and optional dry-run marker. `pushTag` either prints or runs `docker tag` and `docker push` from `$IMAGE_NAME:$WIP_IMAGE_TAG`.

## Control Flow
Tag selection mirrors `get-docker-tags.sh`: RC tags get version only, stable releases get version/latest/release, `bifrost-*` gets sanitized branch/build/SHA, and master/staging get build/SHA plus `*-latest`.

## State And Persistence Behavior
In non-dry-run mode it mutates local Docker image tags and pushes remote Docker registry tags.

## Dependencies And Integration Points
It integrates CI-provided Git metadata, Docker CLI, and Docker Hub naming policy.

## Risks And Test Signals
Risks include legacy status, accidental pushes, branch regex policy drift, and missing local `wip` image. Signals are expected dry-run output or successful pushed Docker tags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/push-docker-tags.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/test-go-build-platforms -->
# sources/distributed-fs/ipfs-kubo/bin/test-go-build-platforms

## Purpose
This script locally reproduces the cross-platform Go build check for Kubo.

## Important APIs, Types, And Functions
It reads `.github/build-platforms.yml`, extracts lines beginning with `  - `, splits each into `GOOS` and `GOARCH`, and runs `go build -o /dev/null ./cmd/ipfs`.

## Control Flow
The script validates the platform manifest exists, loops over non-empty platform entries, builds each target, and prints completion.

## State And Persistence Behavior
Only Go build cache is affected; output is discarded.

## Dependencies And Integration Points
It integrates the platform manifest, Go compiler, and `cmd/ipfs` package.

## Risks And Test Signals
Risks include simplistic YAML parsing and hyphenated platform format assumptions. Signal is all platform builds completing successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/test-go-build-platforms -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/test-go-fmt -->
# sources/distributed-fs/ipfs-kubo/bin/test-go-fmt

## Purpose
This script checks Go formatting across the repository.

## Important APIs, Types, And Functions
It uses `find` to select `*.go` files while pruning `test/sharness` and `plugin/loader/preload.go`, runs `gofmt -s -l`, and reports any paths listed.

## Control Flow
It writes gofmt output to a temp file, prints a formatted failure message if non-empty, cleans up, and exits nonzero.

## State And Persistence Behavior
It creates and removes a temporary file; it does not rewrite source files.

## Dependencies And Integration Points
It supports Make/CI format checks and relies on Go's `gofmt`.

## Risks And Test Signals
Risks include skipped paths hiding formatting issues and temp-file cleanup on interruption. Signal is empty gofmt output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/bin/test-go-fmt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/blocks/blockstoreutil/remove.go -->
# sources/distributed-fs/ipfs-kubo/blocks/blockstoreutil/remove.go

## Purpose
This utility package removes blocks from a GC-capable blockstore while protecting pinned content.

## Important APIs, Types, And Functions
`RemovedBlock` reports a CID hash plus optional error. `RmBlocksOpts` carries `Prefix`, `Quiet`, and `Force`. `RmBlocks` returns an asynchronous channel of results. `FilterPinned` calls `pin.Pinner.CheckIfPinned` and emits pinned errors.

## Control Flow
`RmBlocks` creates a buffered result channel, takes the blockstore GC lock, filters pinned CIDs, checks block existence unless forced, deletes blocks, and emits successes unless quiet. Fatal pin-check failures emit a result with empty hash and stop removal.

## State And Persistence Behavior
It mutates the blockstore by deleting blocks under the GC lock. Pin state is read-only but authoritative for skip decisions.

## Dependencies And Integration Points
It integrates Boxo `GCBlockstore`, Kubo/Boxo pinner semantics, CIDs, and go-ipld-format not-found errors.

## Risks And Test Signals
Risks include asynchronous callers not draining results, stale pin state, existence checks retained for compatibility, and partial deletion after per-block errors. Signals are result objects for pinned, missing, failed, and successfully removed blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/blocks/blockstoreutil/remove.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/api.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/api.go

## Purpose
This file implements the top-level HTTP CoreAPI client used to talk to a running Kubo daemon.

## Important APIs, Types, And Functions
`HttpApi` stores base URL, `http.Client`, headers, global request option hook, IPLD decoder, and cached remote version. Constructors include `NewLocalApi`, `NewPathApi`, `ApiAddr`, `NewApi`, `NewApiWithClient`, and `NewURLApiWithClient`. Interface accessors return `Unixfs`, `Block`, `Dag`, `Name`, `Key`, `Pin`, `Object`, `Swarm`, `PubSub`, and `Routing` sub-APIs.

## Control Flow
Local constructors resolve `$IPFS_PATH/api`; multiaddr constructors select Unix socket handling or HTTP/HTTPS based on protocols; URL constructor creates a decoder with dag-pb/raw support and disables redirects. `Request` copies headers into a request builder. `loadRemoteVersion` fetches `/version` once under a mutex.

## State And Persistence Behavior
State is client-side only: headers, cached semantic version, and decoder registry. It reads the local API file but does not write it.

## Dependencies And Integration Points
It integrates multiaddr dialing, fsutil home expansion, Kubo version response, go-ipld legacy decoder, dag-pb/raw codecs, and `coreiface`.

## Risks And Test Signals
Risks include URL scheme inference mistakes, redirect rejection breaking unusual proxies, global codec assumptions, and stale cached remote versions. Tests cover full CoreAPI behavior, header propagation, and TLS/HTTPS multiaddr conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/api_test.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/api_test.go

## Purpose
This test file validates the HTTP CoreAPI client against real harness nodes and focused URL/header behavior.

## Important APIs, Types, And Functions
`NodeProvider.MakeAPISwarm` creates harness nodes, initializes empty repos, enables filestore, sets provide strategy to roots, starts daemons with optional online connectivity, builds `NewApi` clients, and removes the default empty-node pin. Tests include `TestHttpApi`, `Test_NewURLApiWithClient_With_Headers`, and `Test_NewURLApiWithClient_HTTP_Variant`.

## Control Flow
`TestHttpApi` runs the shared `coreiface/tests.TestApi`. Header testing uses an `httptest.Server` and calls `api.Pin().Rm` to assert custom headers reach HTTP requests. Scheme testing checks TCP, TLS, HTTPS, and TLS/HTTP multiaddrs map to expected URLs.

## State And Persistence Behavior
It creates temporary harness repos and running daemons; test cleanup is owned by the harness.

## Dependencies And Integration Points
It integrates RPC client construction, CLI harness nodes, `coreiface` conformance tests, config mutation, pubsub startup, and multiaddr URL handling.

## Risks And Test Signals
Risks are harness flakiness and broad shared API test failures being hard to localize. Signals are complete CoreAPI conformance, expected custom header receipt, and correct URL scheme decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/apifile.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/apifile.go

## Purpose
This file adapts remote UnixFS paths returned by the HTTP API into Boxo `files.Node`, `files.File`, `files.Directory`, and symlink abstractions.

## Important APIs, Types, And Functions
`UnixfsAPI.Get` resolves mutable paths, calls `files/stat`, parses mode/mtime/type, and dispatches to `getFile`, `getDir`, or `getSymlink`. `apiFile` supports `Read`, `ReadAt`, `Seek`, `Close`, `Mode`, `ModTime`, and `Size`. `apiDir` returns an `apiIter` over streaming `ls` output.

## Control Flow
Files are read through `cat`, with small forward seeks optimized by discarding from the existing stream and random reads done with offset/length requests. Directories issue streaming `ls`, buffer the response, and lazily build child nodes from each decoded link. Symlinks read target content via `cat`.

## State And Persistence Behavior
State is client-side stream position, open HTTP response, stat metadata, and buffered directory listing. Remote block/repo state is read-only.

## Dependencies And Integration Points
It integrates `files/stat`, `cat`, `ls`, Boxo UnixFS type constants, path resolution, and JSON streaming.

## Risks And Test Signals
Risks include directory buffering despite stream mode, response leak on early error, seek behavior on closed streams, and unsupported UnixFS types. Signals come from RPC CoreAPI UnixFS tests exercising reads, seeks, directories, symlinks, sizes, modes, and mtimes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/apifile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/auth/auth.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/auth/auth.go

## Purpose
This package provides an HTTP transport wrapper that injects an Authorization header into RPC requests.

## Important APIs, Types, And Functions
`AuthorizedRoundTripper` stores an authorization string and base `http.RoundTripper`. `NewAuthorizedRoundTripper` defaults a nil base to `http.DefaultTransport`. `RoundTrip` sets `Authorization` then delegates.

## Control Flow
The wrapper is constructed by CLI startup when `--api-auth` is provided and used by the HTTP client for remote command execution.

## State And Persistence Behavior
State is the in-memory authorization string. No persistence occurs.

## Dependencies And Integration Points
It integrates with `cmd/ipfs/kubo/start.go`, Kubo `API.Authorizations`, and standard `net/http`.

## Risks And Test Signals
Risks include mutating the caller's request header in place and overwriting existing Authorization values. Signals are authenticated API calls succeeding when the header is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/auth/auth.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/block.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/block.go

## Purpose
This file implements `coreiface.BlockAPI` over Kubo's HTTP RPC endpoints.

## Important APIs, Types, And Functions
`BlockAPI` wraps `HttpApi`. `blockStat` implements size and immutable path. `Put` maps CID prefix options to `block/put` flags, `Get` fetches block bytes, `Rm` removes a block with optional force, and `Stat` returns block metadata.

## Control Flow
`Put` validates multihash type, chooses `format=v0` for CIDv0 dag-pb or `cid-codec` otherwise, uploads a multipart body, decodes `Key` and `Size`, and parses the CID. `Get`, `Rm`, and `Stat` normalize not-found text into IPLD-compatible errors where possible.

## State And Persistence Behavior
`Put` and `Rm` mutate the remote blockstore/pin behavior according to options. `Get` and `Stat` are read-only.

## Dependencies And Integration Points
It integrates coreiface block options, multicodec/multihash mappings, HTTP request builders, and error parsing helpers.

## Risks And Test Signals
Risks include typoed error text, codec string compatibility, buffering full block data in memory, and not-found parsing brittleness. Signals are block add/get/stat/remove behavior in CoreAPI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/block.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/dag.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/dag.go

## Purpose
This file implements an IPLD DAG service over the block HTTP API.

## Important APIs, Types, And Functions
Types include `HttpDagServ`, `httpNodeAdder`, and `pinningHttpNodeAdder`. Methods include `Get`, `GetMany`, `Add`, `AddMany`, `Pinning`, `Remove`, and `RemoveMany`.

## Control Flow
`Get` retrieves raw block bytes through `Block().Get`, wraps them in a block with the requested CID, and decodes with the API's IPLD decoder. `add` uploads `format.Node.RawData()` through `Block().Put`, preserving CID codec/hash details and verifying the remote CID matches. Multi operations loop sequentially except `GetMany`, which starts one goroutine per CID.

## State And Persistence Behavior
Adds and removes mutate the remote blockstore and optionally pin added nodes. Gets are read-only.

## Dependencies And Integration Points
It integrates go-ipld-format, go-block-format, CID prefixes, block API, and the registered decoder from `api.go`.

## Risks And Test Signals
Risks include unbounded `GetMany` goroutines, sequential add/remove inefficiency, and codec mismatch causing CID verification failure. Signals are CoreAPI DAG add/get/remove tests and CID equality checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/dag.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/errors.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/errors.go

## Purpose
This file converts textual HTTP API error messages back into ABI-compatible Go errors, especially IPLD not-found errors.

## Important APIs, Types, And Functions
`prePostWrappedNotFoundError` wraps an `ipld.ErrNotFound` while preserving surrounding text. `parseErrNotFoundWithFallbackToMSG`, `parseErrNotFoundWithFallbackToError`, `parseIPLDErrNotFound`, and `parseBlockstoreNotFound` implement parsing. `blockstoreNotFoundMatchingIPLDErrNotFound` makes old blockstore text match `ipld.IsNotFound`.

## Control Flow
Parsing first handles empty strings, then searches for `ipld: could not find`, extracts a CID or `node`, validates CID encoding, preserves pre/post text, and falls back to blockstore text matching.

## State And Persistence Behavior
No state or persistence; pure error conversion.

## Dependencies And Integration Points
It integrates CID parsing, multibase expectations, go-ipld-format error matching, and block/RPC methods that need typed not-found errors.

## Risks And Test Signals
Risks include fragile string parsing, future error wording changes, and rejecting valid but differently encoded CIDs. Dedicated tests cover wrapping, break characters, CID versions, undefined CIDs, and blockstore compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/errors_test.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/errors_test.go

## Purpose
This test file validates RPC not-found error reconstruction and compatibility with `ipld.IsNotFound`.

## Important APIs, Types, And Functions
`doParseIpldNotFoundTest` compares original and rebuilt messages and `ipld.IsNotFound` behavior. `TestParseIPLDNotFound` builds valid and invalid IPLD not-found variants. `TestBlockstoreNotFoundMatchingIPLDErrNotFound` checks blockstore text compatibility.

## Control Flow
Tests iterate multiple wrapping formats, CID break characters, CIDv0/CIDv1/base encodings, undefined CIDs, invalid CIDs, and unrelated errors.

## State And Persistence Behavior
No persistent state; all tests are pure functions.

## Dependencies And Integration Points
It integrates Go error wrapping, CID/multibase/multihash libraries, and the RPC error parser.

## Risks And Test Signals
Risks are that tests mirror current parser assumptions and may miss future API error variants. Signals are exact message preservation and matching `ipld.IsNotFound` results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/errors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/key.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/key.go

## Purpose
This file implements key management, signing, and verification over the HTTP API.

## Important APIs, Types, And Functions
`KeyAPI` wraps `HttpApi`. `key` implements `iface.Key` with `Name`, `Path`, and `ID`. Methods include `Generate`, `Rename`, `List`, `Self`, `Remove`, `Sign`, and `Verify`.

## Control Flow
RPC responses with name and peer ID are converted by `newKey` into peer IDs and `/ipns/<name>` paths. Signing uploads data to `key/sign` and decodes the returned multibase signature. Verification sends key/name, multibase signature, and data to `key/verify`.

## State And Persistence Behavior
Generate, rename, remove, sign, and verify act on remote key material; signing/verification read private/public key state through the daemon. Client state is transient.

## Dependencies And Integration Points
It integrates Kubo key commands, IPNS name derivation, peer ID decoding, coreiface key options, and shared multibase encoding.

## Risks And Test Signals
Risks include unexpected key count on remove, malformed peer IDs, and signature multibase compatibility. Signals are CoreAPI key tests for lifecycle and signature validity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/key.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/name.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/name.go

## Purpose
This file implements IPNS publish and resolve operations over HTTP RPC.

## Important APIs, Types, And Functions
`NameAPI` has `Publish`, `Search`, and `Resolve`. `ipnsEntry` models publish output. It uses coreiface name options and Boxo namesys resolve option processing.

## Control Flow
`Publish` sends `name/publish` with key, offline allowance, lifetime, TTL, and `resolve=false`, then converts the returned name string. `Search` and `Resolve` reject unsupported depths, map cache/recursive/DHT options to RPC flags, and decode streamed or single resolve outputs into paths.

## State And Persistence Behavior
Publish mutates IPNS records and may publish them depending on options. Resolve/search are read-only but may use or bypass resolver cache.

## Dependencies And Integration Points
It integrates IPNS, namesys depth semantics, Kubo `name/*` commands, and streaming JSON responses.

## Risks And Test Signals
Risks include unsupported custom depths, silent stream termination on path parse errors, and resolver option mismatch. Signals are CoreAPI name publish/resolve/search tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/name.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/object.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/object.go

## Purpose
This file implements legacy object patch and diff operations over HTTP RPC.

## Important APIs, Types, And Functions
`ObjectAPI` exposes `AddLink`, `RmLink`, and `Diff`. `objectOut` carries returned hashes, and `change` maps JSON diff entries to `iface.ObjectChange`.

## Control Flow
Patch methods call `object/patch/add-link` or `object/patch/rm-link`, pass UnixFS validation options, parse returned hashes, and return immutable paths. `Diff` calls `object/diff`, then maps before/after CIDs to immutable paths when defined.

## State And Persistence Behavior
Patch methods create new DAG objects in the remote repo. Diff is read-only.

## Dependencies And Integration Points
It integrates legacy object commands, coreiface object options, CIDs, and path wrappers.

## Risks And Test Signals
Risks include legacy object API drift, UnixFS validation option mismatch, and undefined CID handling in diffs. Signals are object link add/remove/diff CoreAPI tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/object.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/path.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/path.go

## Purpose
This file resolves mutable or IPLD paths through the HTTP API into immutable paths and nodes.

## Important APIs, Types, And Functions
`HttpApi.ResolvePath` returns an immutable path plus remaining path segments. `ResolveNode` resolves a path and then fetches the root DAG node.

## Control Flow
IPNS paths are first resolved through `Name().Resolve`. All paths then call `dag/resolve`, rebuild a path from namespace, returned CID, and remaining path, convert it to an immutable path, and return string segments.

## State And Persistence Behavior
The file is read-only against the daemon, though resolver caches may be involved server-side.

## Dependencies And Integration Points
It integrates name resolution, `dag/resolve`, Boxo path constructors, CID JSON decoding, and DAG service fetching.

## Risks And Test Signals
Risks include incorrect handling of remaining path segments and `ResolveNode` only fetching the root CID rather than traversed remainder. Signals are CoreAPI path/node resolution tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/path.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/pin.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/pin.go

## Purpose
This file implements local pin operations over the HTTP API.

## Important APIs, Types, And Functions
`PinAPI` exposes `Add`, `Ls`, `IsPinned`, `Rm`, `Update`, and `Verify`. `pin` implements `iface.Pin`; `pinVerifyRes` and `badNode` implement pin verification status interfaces.

## Control Flow
Add/remove/update map options to `pin/*` commands. `Ls` streams JSON pin entries and sends converted pins to a caller-provided channel. `IsPinned` queries `pin/ls` with a target arg and treats "is not pinned" text as a negative result. `Verify` streams verbose verification responses in a goroutine.

## State And Persistence Behavior
Add, remove, and update mutate the daemon pinset. List/is/verify read pin state and may traverse pinned DAGs.

## Dependencies And Integration Points
It integrates Kubo pin commands, coreiface pin options, streaming JSON, CID parsing, and path wrappers.

## Risks And Test Signals
Risks include brittle string matching for not-pinned errors, channel close ownership, and decode errors represented as status messages. Signals are CoreAPI pin lifecycle/list/is/verify tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/pin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/pubsub.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/pubsub.go

## Purpose
This file implements pubsub topic listing, peer listing, publishing, and subscriptions over HTTP RPC.

## Important APIs, Types, And Functions
`PubsubAPI` exposes `Ls`, `Peers`, `Publish`, and `Subscribe`. `pubsubSub` implements subscription lifecycle. `pubsubMessage` implements `iface.PubSubMessage`. `toMultibase` encodes bytes as URL-safe base64 multibase.

## Control Flow
Topics and messages are encoded/decoded using multibase because RPC transports topic/data fields as text. `Subscribe` opens `pubsub/sub`, starts a decoder goroutine feeding a message channel, and `Next` decodes peer ID, data, sequence, and topics for callers.

## State And Persistence Behavior
Publish sends data into the node's pubsub system; subscribe holds an open HTTP response until closed or canceled.

## Dependencies And Integration Points
It integrates Kubo pubsub commands, libp2p peer IDs, coreiface pubsub APIs, multibase encoding, and streaming JSON.

## Risks And Test Signals
Risks include subscription goroutine leaks if `Close` is not called, multibase decode failures, and close-once handling via nil `done`. Signals are CoreAPI pubsub tests for topic/peer discovery and message delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/pubsub.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/request.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/request.go

## Purpose
This file defines the low-level HTTP RPC request object used by the request builder.

## Important APIs, Types, And Functions
`Request` stores context, API base URL, command, args, options, body, and headers. `NewRequest` normalizes a base URL and initializes default options `encoding=json` and `stream-channels=true`.

## Control Flow
Higher-level builders construct `Request` objects before sending them in `response.go`.

## State And Persistence Behavior
State is per-request only; no persistence.

## Dependencies And Integration Points
It integrates with all RPC API files through `requestBuilder.Send`.

## Risks And Test Signals
Risks include treating non-`http` URL prefixes as plain HTTP and relying on later URL encoding. Signals are all RPC requests reaching `/api/v0/<command>` with expected defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/request.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/requestbuilder.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/requestbuilder.go

## Purpose
This file provides the fluent request builder used by all HTTP RPC sub-APIs.

## Important APIs, Types, And Functions
`RequestBuilder` defines argument/body/option/header/send/exec methods. `requestBuilder` stores command state and shell pointer. `FileBody` wraps readers into multipart `files.MultiFileReader`; `encodedAbsolutePathVersion` controls compatibility for multipart path encoding.

## Control Flow
Callers add args, options, headers, or body, then `Send` applies global API options, builds a `Request`, and sends it. `Exec` sends and decodes JSON or drains/closes response when no result is expected.

## State And Persistence Behavior
State is accumulated builder data plus a deferred `buildError` when remote version lookup fails during `FileBody`.

## Dependencies And Integration Points
It integrates Boxo `files`, remote version negotiation, API offline options, and `Response.decode`.

## Risks And Test Signals
Risks include hidden network call in `FileBody`, reversed/fragile encoded-path compatibility logic, stringification of arbitrary options, and overwriting duplicate option keys. Signals are upload APIs working against old and new daemon versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/requestbuilder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/response.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/response.go

## Purpose
This file sends low-level HTTP requests and decodes Kubo command responses.

## Important APIs, Types, And Functions
`Response` wraps output and command error. `trailerReader` turns stream error trailers into read errors. `Response.Close`, `Cancel`, and `decode` manage response bodies. `Request.Send` creates POST requests, sets multipart headers, maps HTTP errors to `cmds.Error`, and `getURL` builds query strings.

## Control Flow
`Send` posts to `/api/v0/<command>?arg=...`, copies custom headers, performs the request, parses content type, wraps successful bodies, and handles error bodies as text, JSON, not found, rate-limited, forbidden, or implementation errors.

## State And Persistence Behavior
State is per-response body/trailer state. `Close` drains bodies to support connection cleanup; `Cancel` aborts without draining.

## Dependencies And Integration Points
It integrates go-ipfs-cmds HTTP conventions, stream error trailers, Boxo multipart readers, and all RPC sub-APIs.

## Risks And Test Signals
Risks include failing on missing/invalid content type, body drain behavior, stderr warnings from library code, and trailer-only errors surfacing late. Signals are correct error codes/messages and clean streaming response closure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/response.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/routing.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/routing.go

## Purpose
This file implements routing record and provider operations over HTTP RPC.

## Important APIs, Types, And Functions
`RoutingAPI` exposes `Get`, `Put`, `FindPeer`, `FindProviders`, and `Provide`.

## Control Flow
`Get` decodes the first routing query event's base64 `Extra`. `Put` uploads value bytes to `routing/put` with optional offline allowance. `FindPeer` reads query events until `FinalPeer`. `FindProviders` resolves the path to a root CID, streams provider query events, and emits provider addr infos. `Provide` resolves a path and calls `routing/provide`.

## State And Persistence Behavior
Put and provide mutate routing/DHT state. Get/find operations read network routing state and may block on network activity.

## Dependencies And Integration Points
It integrates Kubo routing commands, libp2p routing query events, peer addr infos, path resolution, and coreiface routing options.

## Risks And Test Signals
Risks include limited error propagation from provider streams, assuming `FinalPeer` has a response, and base64 `Extra` coupling. Signals are CoreAPI routing tests for record get/put, peer lookup, provider lookup, and provide.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/routing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/swarm.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/swarm.go

## Purpose
This file implements libp2p swarm operations over HTTP RPC.

## Important APIs, Types, And Functions
`SwarmAPI` exposes `Connect`, `Disconnect`, `Peers`, `KnownAddrs`, `LocalAddrs`, and `ListenAddrs`. `connInfo` implements `iface.ConnectionInfo`.

## Control Flow
`Connect` encapsulates each address with `/p2p/<peer>` and sends them to `swarm/connect`. Peer/listener methods decode JSON strings into peer IDs, multiaddrs, durations, directions, and protocol IDs.

## State And Persistence Behavior
Connect/disconnect mutate live swarm connections. Address and peer listing are read-only views of libp2p state.

## Dependencies And Integration Points
It integrates Kubo `swarm/*` commands, libp2p peer/network/protocol types, and multiaddr parsing.

## Risks And Test Signals
Risks include parse failures aborting whole result sets, ignored latency parse errors, and connect behavior with empty address lists. Signals are CoreAPI swarm connect/list/address tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/swarm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/unixfs.go -->
# sources/distributed-fs/ipfs-kubo/client/rpc/unixfs.go

## Purpose
This file implements UnixFS add and directory listing over HTTP RPC.

## Important APIs, Types, And Functions
`UnixfsAPI` exposes `Add` and `Ls`. `addEvent` models streaming add events. `lsLink`, `lsObject`, and `lsOutput` model `ls` responses.

## Control Flow
`Add` maps coreiface options to `add` flags, builds a multipart directory with the supplied node, negotiates multipart path encoding by remote version, streams add events, forwards optional progress events, and returns the last event CID. `Ls` streams `ls` output, validates one object/link per event, maps UnixFS data types to file types, and sends `iface.DirEntry` values until EOF or context cancellation.

## State And Persistence Behavior
Add mutates the remote blockstore and optionally pins. Ls is read-only.

## Dependencies And Integration Points
It integrates Kubo `add`/`ls`, Boxo files and UnixFS types, multihash code names, CID parsing, and progress event channels.

## Risks And Test Signals
Risks include returning the last add event only, upload compatibility with older daemons, channel blocking on progress/listing outputs, and a likely bug returning `err` instead of `resp.Error` in `Ls`. Signals are CoreAPI UnixFS add/list tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/client/rpc/unixfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/Rules.mk -->
# sources/distributed-fs/ipfs-kubo/cmd/ipfs/Rules.mk

## Purpose
This Make fragment builds, installs, and coverage-instruments the `cmd/ipfs` binary.

## Important APIs, Types, And Functions
It defines `IPFS_BIN_$(d)`, appends it to `TGT_BIN`, adds command directory to `PATH`, sets ldflags for `CurrentCommit`, `taggedRelease`, and `buildOrigin`, defines install target, and creates `ipfs-test-cover` with `testrunmain` tag.

## Control Flow
Included by root `Rules.mk`, it builds the package target with Go deps and always rebuild semantics. Coverage target computes Kubo package dependencies, joins them for `-coverpkg`, and compiles a test binary.

## State And Persistence Behavior
It creates `cmd/ipfs/ipfs`, optional installed binary under `$GOBIN`, and `cmd/ipfs/ipfs-test-cover`.

## Dependencies And Integration Points
It integrates Make Go macros, Git metadata macros, package dependency discovery, and `runmain_test.go` coverage entrypoint.

## Risks And Test Signals
Risks include shell quoting in ldflags, package list size for coverage, and PATH shadowing. Signals are version metadata embedded in binaries and coverage binary creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/Rules.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/add_migrations.go -->
# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/add_migrations.go

## Purpose
This file caches or pins migration binaries fetched during repo migration into the running IPFS node.

## Important APIs, Types, And Functions
`addMigrations` dispatches by fetcher type. `addMigrationFiles` adds downloaded local files through UnixFS. `addMigrationPaths` connects to a temporary migration peer and pins or reads fetched IPFS paths. `ipfsGet` reads a UnixFS file to force block import.

## Control Flow
Multi-fetchers are flattened. IPFS fetchers provide peer info and paths; HTTP fetchers scan `migrations.DownloadDirectory`. Files are added one by one, optionally pinned. IPFS paths require connecting to the migration peer first.

## State And Persistence Behavior
It mutates the node blockstore and optionally pinset. It reads migration download directories and network-fetched paths but does not manage cleanup itself.

## Dependencies And Integration Points
It integrates fsrepo migration fetchers, `coreapi`, UnixFS add/get, swarm connect, remote pinning of migration artifacts, and daemon migration flow.

## Risks And Test Signals
Risks include unknown fetcher types, empty path/address errors, file descriptor cleanup, and expensive reads. Signals are printed "Added migration file" messages and successful cached/pinned artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/add_migrations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/daemon.go -->
# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/daemon.go

## Purpose
This file defines and implements `ipfs daemon`, the long-running Kubo node process that opens the repo, migrates if necessary, builds the core node, starts plugins, RPC API, gateway, optional FUSE mounts, optional GC, libp2p gateway, metrics, MFS remote pinning, version checks, and graceful shutdown.

## Important APIs, Types, And Functions
The central command is `daemonCmd`; `daemonFunc` is the orchestration entrypoint. Helper functions include `defaultMux`, `serveHTTPApi`, `serveHTTPGateway`, `serveTrustlessGatewayOverLibp2p`, `mountFuse`, `checkFusePath`, `maybeRunGC`, `merge`, `YesNoPrompt`, `printVersion`, `printLibp2pPorts`, `rewriteMaddrToUseLocalhostIfItsAny`, and `startVersionChecker`.

## Control Flow
Startup injects Prometheus/OpenTelemetry metrics, prints version, manages fd limits, optionally initializes a repo, opens/migrates the repo, loads config, validates AutoConf/private network constraints, constructs routing, sets agent suffix, creates `core.IpfsNode`, starts plugins, binds API and gateway listeners, mounts FUSE if requested, runs GC, starts libp2p gateway and MFS pinning, marks readiness, then fans in long-running error channels until shutdown.

## State And Persistence Behavior
It owns the fsrepo lock, config reads/writes, API/gateway address files, repo migrations, blockstore/datastore state, pinsets, network connections, metrics registrations, FUSE mounts, systemd readiness notifications, and daemon lifecycle. Deferred cleanup closes the node, plugins, mounts, listeners, and migration fetchers.

## Dependencies And Integration Points
It integrates almost every runtime subsystem: config, fsrepo, migrations, libp2p routing, AutoTLS/private network checks, corehttp API/gateway, socket activation, Prometheus/OTel, plugins, FUSE, GC, remote pinning, systemd notification, and version detection.

## Risks And Test Signals
Risks include startup ordering, listener readiness races, fatal config deprecations, private network routing leaks, global metric registration panics, shutdown hangs, and many asynchronous goroutines. Signals are daemon startup text, API/gateway address files, WebUI URL, "Daemon is ready", metrics endpoint, successful shutdown, and integration tests around daemon behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/daemon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/daemon_linux.go -->
# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/daemon_linux.go

## Purpose
This Linux-only file sends systemd readiness and stopping notifications for the daemon.

## Important APIs, Types, And Functions
`notifyReady` calls `daemon.SdNotifyReady`; `notifyStopping` calls `daemon.SdNotifyStopping`.

## Control Flow
`daemon.go` calls these helpers after daemon readiness and when shutdown begins.

## State And Persistence Behavior
It mutates systemd service state through the notification socket when available.

## Dependencies And Integration Points
It integrates `github.com/coreos/go-systemd/v22/daemon` and the Linux build tag.

## Risks And Test Signals
Risks are silent ignored notification errors and environment/socket absence. Signals are systemd units observing READY=1 and STOPPING=1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/daemon_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/daemon_other.go -->
# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/daemon_other.go

## Purpose
This non-Linux file provides no-op daemon notification functions.

## Important APIs, Types, And Functions
`notifyReady` and `notifyStopping` are empty functions behind the `!linux` build tag.

## Control Flow
The same calls in `daemon.go` compile on non-Linux platforms without systemd behavior.

## State And Persistence Behavior
No state is changed.

## Dependencies And Integration Points
It integrates Go build tags with cross-platform daemon startup.

## Risks And Test Signals
Risk is simply that non-Linux supervisors get no readiness notification. Signal is successful non-Linux compilation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/daemon_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/debug.go -->
# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/debug.go

## Purpose
This file registers an HTTP debug endpoint that dumps all goroutine stacks.

## Important APIs, Types, And Functions
`init` registers `/debug/stack` on `http.DefaultServeMux` and writes `profile.WriteAllGoroutineStacks` to the response.

## Control Flow
Registration happens at package init time. `daemon.go` exposes the default mux under the API debug routes.

## State And Persistence Behavior
It mutates global `http.DefaultServeMux` handler registration.

## Dependencies And Integration Points
It integrates Kubo profiling utilities, `net/http`, and daemon debug API serving.

## Risks And Test Signals
Risks include exposing sensitive goroutine stacks on the RPC API and global mux collisions. Signal is `/debug/stack` returning stack dumps when API debug routes are available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/debug.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/dnsresolve_test.go -->
# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/dnsresolve_test.go

## Purpose
This test file verifies DNS multiaddr resolution used for API endpoint selection.

## Important APIs, Types, And Functions
`makeResolver` builds a mock multiaddr DNS resolver for `example.com`. Tests cover one result, multiple results, and no results by calling `resolveAddr`.

## Control Flow
Each test replaces package variable `dnsResolver`, resolves `/dns4/example.com/tcp/5001`, and asserts either the first `192.0.2.x` result or a `non-resolvable API endpoint` error.

## State And Persistence Behavior
It mutates the package-level resolver for the test process only.

## Dependencies And Integration Points
It integrates `cmd/ipfs/kubo/start.go` API address resolution, multiaddr DNS mock resolver, and multiaddr equality.

## Risks And Test Signals
Risks include global resolver mutation affecting parallel tests if added later. Signals are deterministic first-address selection and correct error on empty DNS results.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/dnsresolve_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/init.go -->
# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/init.go

## Purpose
This file implements `ipfs init`, creating a new fsrepo config, identity, optional profile transforms, optional default docs, and initial IPNS keyspace state.

## Important APIs, Types, And Functions
`initCmd` defines options for key algorithm, RSA bits, empty repo, and profiles. Helpers include `applyProfiles`, `doInit`, `checkWritable`, `addDefaultAssets`, and `initializeIpnsKeyspace`.

## Control Flow
The command optionally decodes a provided config file, otherwise generates an identity and default config, applies profiles, initializes the repo, seeds default assets unless empty, and publishes an empty directory to the node's IPNS keyspace.

## State And Persistence Behavior
It creates the repo directory/config/datastore, writes private key material, pins init docs and empty directory state, and publishes initial IPNS record. It refuses to overwrite an initialized repo.

## Dependencies And Integration Points
It integrates config profiles, fsrepo init/open, embedded assets, core node construction, pinning, UnixFS empty directory, and namesys publish.

## Risks And Test Signals
Risks include permission checks creating a repo directory before full init, profile errors after identity generation, and init docs add failures. Signals are repo config existence, seeded docs CID output, and usable initial IPNS/MFS state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/init.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/ipfs.go -->
# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/ipfs.go

## Purpose
This file assembles the local CLI root command by combining daemon/init/local command overrides with the shared core command tree.

## Important APIs, Types, And Functions
`Root` starts with core root options/help. `commandsClientCmd` exposes local `ipfs commands`. `localCommands` maps `daemon`, `init`, and `commands`. `init` fills `Root.Subcommands` with local overrides plus all non-conflicting core commands.

## Control Flow
Package initialization avoids literal initialization loops by assigning subcommands in `init`.

## State And Persistence Behavior
It mutates the global command tree during process init.

## Dependencies And Integration Points
It integrates `core/commands` with the local-only CLI commands implemented in this package.

## Risks And Test Signals
Risks include subcommand collisions and initialization-order assumptions. Signal is `ipfs` exposing local daemon/init while still exposing normal core commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/ipfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/pinmfs.go -->
# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/pinmfs.go

## Purpose
This file implements the daemon background service that periodically pins the current MFS root to configured remote pinning services.

## Important APIs, Types, And Functions
Types include `lastPin`, `pinMFSContext`, `pinMFSNode`, and `ipfsPinMFSNode`. Functions include `startPinMFS`, `pinMFSOnChange`, `pinAllMFS`, and `pinMFS`.

## Control Flow
The daemon starts a polling goroutine. On each interval it reloads config, reads the MFS root CID, skips disabled services, parses repin intervals, skips unchanged/recent pins, and starts parallel pin attempts. `pinMFS` lists existing remote pins by name, reuses non-failed current pins, replaces older pins, or creates a new pin with optional origin multiaddrs.

## State And Persistence Behavior
It maintains in-memory `lastPins` per service and mutates remote pinning services through add/replace calls. It reads current MFS root and config repeatedly.

## Dependencies And Integration Points
It integrates daemon lifecycle, config remote pinning policy, Boxo remote pinning client, MFS root node, libp2p host addresses, and logging.

## Risks And Test Signals
Risks include expensive MFS root reads, remote service hangs/errors, channel waits for all goroutines, invalid intervals, and duplicate pin-name assumptions. Tests assert config/root-node errors and service policy error logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/pinmfs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/pinmfs_test.go -->
# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/pinmfs_test.go

## Purpose
This file tests MFS remote pinning error paths and policy handling.

## Important APIs, Types, And Functions
Test doubles include `testPinMFSContext` and `testPinMFSNode`. Helpers include `isErrorSimilar`, `testPinMFSServiceWithError`, and `readLogLine`. Tests cover config errors, root node errors, disabled services, invalid intervals, unnamed pins, and named pins.

## Control Flow
Tests create short-lived contexts, start `pinMFSOnChange` in a goroutine, read structured log lines from `logging.NewPipeReader`, and assert error level plus message content.

## State And Persistence Behavior
No real remote pinning service is used; failed client calls produce expected log errors. Logging pipe state is the primary observable.

## Dependencies And Integration Points
It integrates the MFS pinning polling loop, config structs, logging pipeline, and merkledag raw node test double.

## Risks And Test Signals
Risks include tests depending on log timing and exact message substrings. Signals are expected logged errors for config read failure, root node failure, invalid interval, and empty remote service response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/pinmfs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/start.go -->
# sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/start.go

## Purpose
This file implements Kubo CLI process startup: tracing, plugin loading, environment construction, interrupt handling, local-vs-remote executor selection, profiling, API address resolution, and remote version negotiation.

## Important APIs, Types, And Functions
Important functions include `loadPlugins`, `BuildDefaultEnv`, `BuildEnv`, `Start`, `checkDebug`, `apiAddrOption`, `makeExecutor`, `tracingWrappedExecutor.Execute`, `getRepoPath`, `startProfiling`, `profileIfEnabled`, `resolveAddr`, and `getRemoteVersion`.

## Control Flow
`Start` initializes tracing, optional profiling, interrupt handler, command aliases (`--version`, `help`), GUI no-arg daemon fallback, stable `os.Args[0]`, then runs the CLI with `BuildEnv` and `makeExecutor`. `makeExecutor` decides local execution, explicit or repo-discovered daemon API use, fallback behavior, TCP/Unix transports, API auth headers, remote version lookup, and multipart compatibility.

## State And Persistence Behavior
It loads plugins from the repo path, may open fsrepo lazily, writes CPU/heap profile files when enabled, mutates global logging/tracing providers, and reads the repo API file.

## Dependencies And Integration Points
It integrates go-ipfs-cmds CLI/HTTP clients, Kubo command tree, fsrepo path detection, plugin loader, tracing/OTel, DNS multiaddr resolver, API authorization, and signal handling.

## Risks And Test Signals
Risks include remote/local fallback surprises, remote version fetch before command execution, Unix socket transport handling, profiler goroutine leak, and global `os.Args` rewriting. Tests cover DNS resolution and coverage-time main execution; broader signals come from CLI integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/kubo/start.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/main.go -->
# sources/distributed-fs/ipfs-kubo/cmd/ipfs/main.go

## Purpose
This is the `ipfs` binary entrypoint.

## Important APIs, Types, And Functions
`main` calls `kubo.Start(kubo.BuildDefaultEnv)` and exits with the returned code.

## Control Flow
All CLI parsing, execution, and cleanup are delegated to `cmd/ipfs/kubo/start.go`.

## State And Persistence Behavior
It only sets the process exit code.

## Dependencies And Integration Points
It integrates the compiled binary with the Kubo CLI package.

## Risks And Test Signals
Risks are minimal; failures come from delegated startup. Signal is the binary invoking Kubo startup and returning correct exit codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/runmain_test.go -->
# sources/distributed-fs/ipfs-kubo/cmd/ipfs/runmain_test.go

## Purpose
This coverage-only test file lets `go test -tags testrunmain` execute the real CLI startup path from a test binary.

## Important APIs, Types, And Functions
`TestRunMain` rebuilds `os.Args` from `flag.Args`, calls `kubo.Start(kubo.BuildDefaultEnv)`, writes the return code to `$IPFS_COVER_RET_FILE` if set, and redirects stdout/stderr to `/dev/null`.

## Control Flow
It is included only under the `testrunmain` build tag, matching the Make coverage binary target.

## State And Persistence Behavior
It mutates global `os.Args`, may write a return-code file, and replaces process stdout/stderr file handles.

## Dependencies And Integration Points
It integrates `cmd/ipfs/Rules.mk` coverage target with normal CLI startup.

## Risks And Test Signals
Risks include global output mutation and comments acknowledging unconventional test abuse. Signal is a coverage binary capable of driving real command execution and reporting exit status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/runmain_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/signal.go -->
# sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/signal.go

## Purpose
This non-WASM utility handles OS interrupts for the CLI and daemon.

## Important APIs, Types, And Functions
`IntrHandler` stores a closing channel and wait group. `NewIntrHandler`, `Close`, and `Handle` manage signal listeners. `SetupInterruptHandler` returns an `io.Closer` plus a derived context canceled on first SIGHUP/SIGINT/SIGTERM and force-exits on subsequent signals.

## Control Flow
`Handle` registers signals, starts a goroutine counting received signals, and invokes a callback. The default callback cancels context on first signal and exits with `-1` on later signals.

## State And Persistence Behavior
It mutates process signal notification state and derived context cancellation. No files are written.

## Dependencies And Integration Points
It integrates `cmd/ipfs/kubo/start.go` startup and daemon graceful shutdown behavior with `os/signal` and `syscall`.

## Risks And Test Signals
Risks include repeated `Close` panic due to closing an already closed channel, hard exit on second signal bypassing defers, and no WASM build. Signals are first Ctrl-C triggering graceful shutdown text and second Ctrl-C terminating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/cmd/ipfs/util/signal.go -->
