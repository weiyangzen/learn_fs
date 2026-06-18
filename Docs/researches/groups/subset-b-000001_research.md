# subset-b-000001 Research

Grouped research for the listed BuildKit files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/ISSUE_TEMPLATE/bug.yml -->
# sources/cloud-native/buildkit/.github/ISSUE_TEMPLATE/bug.yml

## Purpose
Defines the GitHub issue form for BuildKit bug reports. It classifies issues as `bug`, applies `status/triage`, sends security issues to Docker security, and forces reporters through contribution/reporting checks before accepting a required bug description textarea.

## APIs, Flow, And State
The file is declarative GitHub Issue Forms YAML. Its public “API” is the issue-form schema: `name`, `description`, `type`, `labels`, and `body` entries using `markdown`, `checkboxes`, and `textarea`. Control flow is GitHub UI validation: required checkbox options must be checked and the textarea must be filled before issue submission. No repository state is persisted except GitHub issue metadata and the submitted body.

## Dependencies And Integration
Links to `SECURITY.md`, `CONTRIBUTING.md`, the issue reporting guide, and commands for collecting BuildKit, buildx, Docker Engine, and environment info. It integrates with GitHub label automation through the initial `status/triage` label.

## Risks And Test Signals
The main risk is stale links or collection commands, which can reduce report quality. Test signal is indirect: GitHub validates the YAML schema when rendering templates; maintainers can smoke-check by opening the issue chooser.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/ISSUE_TEMPLATE/bug.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/ISSUE_TEMPLATE/config.yml -->
# sources/cloud-native/buildkit/.github/ISSUE_TEMPLATE/config.yml

## Purpose
Configures the GitHub issue template chooser. It allows blank issues and provides contact links for questions, documentation, and Docker community Slack.

## APIs, Flow, And State
Uses GitHub’s issue-template config schema: `blank_issues_enabled` and `contact_links`. GitHub reads this at issue creation time; selecting a contact link navigates users outside the issue-form path. It has no runtime code and no local persistence.

## Dependencies And Integration
Depends on GitHub Discussions, the repository docs path, and the Docker Slack short link. It complements `bug.yml` and `feature.yml` by routing support/discussion/documentation traffic away from bug/feature issue forms.

## Risks And Test Signals
Broken or obsolete URLs would misroute users. Blank issues being enabled can bypass structured forms, trading accessibility for less normalized triage data. The practical test is rendering the issue chooser in GitHub.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/ISSUE_TEMPLATE/config.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/ISSUE_TEMPLATE/feature.yml -->
# sources/cloud-native/buildkit/.github/ISSUE_TEMPLATE/feature.yml

## Purpose
Defines a minimal GitHub issue form for feature/enhancement requests. It applies `status/triage` and classifies the issue as `enhancement`.

## APIs, Flow, And State
The declarative schema exposes one required textarea with id `description`. GitHub validates the required field and persists the resulting issue title/body/labels. There is no code execution or local state.

## Dependencies And Integration
Integrated with GitHub issue forms and repository triage labeling. It intentionally has fewer gates than `bug.yml`, relying on maintainers to classify scope after submission.

## Risks And Test Signals
The low-friction form can admit underspecified requests. Schema test signal is GitHub form rendering; operational test signal is whether feature issues consistently include enough context for triage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/ISSUE_TEMPLATE/feature.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/dependabot.yml -->
# sources/cloud-native/buildkit/.github/dependabot.yml

## Purpose
Configures Dependabot updates for GitHub Actions dependencies. It schedules daily checks, limits concurrent open PRs to ten, groups `crazy-max/.github/*`, applies a two-day cooldown, and labels update PRs as dependency bot work.

## APIs, Flow, And State
Uses Dependabot v2 YAML. Dependabot’s service scans the repository root action references, creates PRs, and stores PR state in GitHub. No local runtime state is created by this file.

## Dependencies And Integration
Only `package-ecosystem: github-actions` is configured. The `groups` entry affects reusable workflows/actions from `crazy-max/.github`, which this repo uses in several workflows. Labels integrate with `area/dependencies` and `bot` triage.

## Risks And Test Signals
Pinned action SHAs mean Dependabot PRs must update exact references; grouped updates can combine unrelated action changes. The cooldown slows emergency updates. Test signal is Dependabot’s update log and generated PR metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/labeler.yml -->
# sources/cloud-native/buildkit/.github/labeler.yml

## Purpose
Defines path-based pull request labels for BuildKit areas. Labels cover project metadata, CI, testing, API, storage/cache, client, LLB, buildctl/buildkitd, CDI, dependencies, docs, Dockerfile frontend, examples, executor/exporter/frontend/hack/session/solver/source/sourcepolicy/util/worker, and Windows-specific changes.

## APIs, Flow, And State
The file is consumed by `actions/labeler`. Each top-level key is a label and each value is a matcher using `changed-files`, `any-glob-to-any-file`, `all-globs-to-all-files`, or `all` clauses. Matching occurs during PR workflow execution and persists only through GitHub labels.

## Dependencies And Integration
Tied to `.github/workflows/labeler.yml`. It mirrors the repository’s directory structure, so ownership and CI routing depend on these glob boundaries. `area/project` explicitly excludes workflow changes so `.github/workflows/**` maps to `area/ci`.

## Risks And Test Signals
Glob drift is the main risk: moved files may stop labeling, and broad globs can over-label PRs. Negated patterns in `all` blocks require careful validation because a small syntax mistake can change label scope. Test signal is labeler workflow output on PRs and synthetic PRs that touch representative paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/labeler.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/.test.yml -->
# sources/cloud-native/buildkit/.github/workflows/.test.yml

## Purpose
Reusable workflow for BuildKit integration-style test matrices. Callers provide cache scope, package list, test kinds, optional tags, Codecov flags, and matrix include overrides.

## APIs, Flow, And State
The public API is `workflow_call` inputs and optional `codecov_token`. `prepare` converts newline inputs into JSON matrices with `actions/github-script`, builds `integration-tests-base` through `docker/bake-action`, and exposes outputs. `run` fans out across worker backends, packages, kinds, tags, and includes; it derives `TESTFLAGS`, builds the `integration-tests` image, runs `./hack/test`, uploads coverage to Codecov, emits gotest annotations, and uploads short-lived test reports.

## Dependencies And Integration
Depends on QEMU, Buildx, BuildKit image `moby/buildkit:latest`, GitHub Actions cache, `docker/bake-action`, `js-yaml`, Codecov, and `crazy-max` annotation action. Called by `buildkit.yml` and `frontend.yml`.

## Risks And Test Signals
Large matrix fan-out is expensive and cache-sensitive. Dynamic YAML parsing of `includes` makes caller formatting important. Persistent state includes GHA cache entries, artifacts, and Codecov uploads. The workflow itself is the primary test signal for core and frontend integration coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/.test.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/buildkit.yml -->
# sources/cloud-native/buildkit/.github/workflows/buildkit.yml

## Purpose
Main BuildKit CI, image, binary, vulnerability, scout, and release workflow. It runs on schedule, manual dispatch, pushes to master/release branches/tags, and PRs except docs-only paths.

## APIs, Flow, And State
Jobs prepare bake platform matrices, build signed/SBOM release binaries via reusable `docker/github-builder`, finalize artifacts, invoke `.test.yml`, run `govulncheck`, compute image tag matrices, build/push BuildKit images, run Docker Scout on master images, and draft GitHub releases for version tags. Control flow is mostly `needs`: binaries feed tests/finalization; tests gate images and releases; images gate scout.

## Dependencies And Integration
Depends on Buildx, bake targets (`release`, `integration-tests`, `govulncheck`, `image-cross`), DockerHub secrets, Codecov, GitHub OIDC signing, SARIF upload, Docker Scout, and `softprops/action-gh-release`. It integrates with Docker image tagging conventions for latest, nightly, master, semver, rootless, and ubuntu variants.

## Risks And Test Signals
Risks include tag-generation mistakes, accidental image pushes, secret availability, cache poisoning/misses, and release artifact renaming assumptions. Test signals are matrix test results, artifact presence, SARIF uploads, Scout SARIF, SBOM/provenance outputs, and draft release creation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/buildkit.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/buildx-image.yml -->
# sources/cloud-native/buildkit/.github/workflows/buildx-image.yml

## Purpose
Manual workflow to create Buildx compatibility tags from BuildKit images, e.g. mapping `moby/buildkit:latest` to `moby/buildkit:buildx-stable-1` variants.

## APIs, Flow, And State
Inputs are `source-tag` and boolean `dry-run`. A matrix covers destination tag `buildx-stable-1` with base, rootless, and ubuntu/gpu flavors. GitHub Script computes source/destination tag names and executes `docker buildx imagetools create`, optionally with `--dry-run`.

## Dependencies And Integration
Depends on Docker Buildx imagetools, DockerHub credentials when not dry-run, and the tag layout produced by `buildkit.yml`. This workflow does not build images; it creates/updates manifests/tags.

## Risks And Test Signals
Because it can retag public images, incorrect `source-tag`, flavor mapping, or dry-run handling can move compatibility tags unexpectedly. Test signal is dry-run output and DockerHub manifest inspection after non-dry-run execution.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/buildx-image.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/compatibility-releases.yml -->
# sources/cloud-native/buildkit/.github/workflows/compatibility-releases.yml

## Purpose
Runs compatibility tests against BuildKit release combinations. It triggers on manual dispatch, PRs, and pushes to master/release branches.

## APIs, Flow, And State
Single `compatibility` job checks out code, exposes GitHub runtime for cache, sets up arm64 QEMU and Buildx, builds `integration-tests-base` and `integration-tests`, then runs `./hack/test-compatibility-releases` with a fixed test image name and disabled test image build.

## Dependencies And Integration
Depends on Buildx, bake targets, QEMU arm64, GitHub Actions cache, and the `hack/test-compatibility-releases` script. It shares cache scope with integration tests.

## Risks And Test Signals
Compatibility signal is only as good as the release list in the hack script and the current test image. Cache or emulation issues can mask compatibility failures. The workflow produces pass/fail logs rather than persistent artifacts.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/compatibility-releases.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/dockerd.yml -->
# sources/cloud-native/buildkit/.github/workflows/dockerd.yml

## Purpose
Manual workflow for testing BuildKit against a specified Docker daemon version or source URL.

## APIs, Flow, And State
Input `version` is interpreted as a URL if parseable; URLs are built with `docker/build-push-action`, while version strings download static Docker binaries. The `prepare` job uploads a `dockerd` artifact. The `test` job downloads it, fixes permissions, then runs `./hack/test` across dockerd worker modes and selected packages with Docker daemon network flags.

## Dependencies And Integration
Depends on Buildx, Docker binary archives or source build contexts, QEMU, GitHub runtime cache, and BuildKit integration tests. Matrix workers are `dockerd` and `dockerd-containerd`.

## Risks And Test Signals
Running user-supplied URLs as build contexts is powerful and should remain manual. Network settings are fixed to avoid address conflicts but may still collide in runner environments. Signals are integration test results plus the uploaded daemon artifact.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/dockerd.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/docs-upstream.yml -->
# sources/cloud-native/buildkit/.github/workflows/docs-upstream.yml

## Purpose
Validates BuildKit docs against Docker’s upstream documentation validation workflow when relevant docs or this workflow change.

## APIs, Flow, And State
On selected pushes and PR paths, the `validate` job calls `docker/docs/.github/workflows/validate-upstream.yml@main` with `module-name: moby/buildkit`. No local steps run in this repo.

## Dependencies And Integration
Depends on the external `docker/docs` reusable workflow and intentionally uses `@main` so validation follows current Docker docs rules. Zizmor unpinned-use warning is explicitly ignored in the comment because freshness is desired.

## Risks And Test Signals
External workflow changes can break BuildKit PRs without local changes. Test signal is upstream docs validation status; persistence is limited to workflow logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/docs-upstream.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/frontend.yml -->
# sources/cloud-native/buildkit/.github/workflows/frontend.yml

## Purpose
CI, image publishing, security scanning, and release workflow for the Dockerfile frontend images.

## APIs, Flow, And State
Triggers on manual dispatch, master/release pushes, `dockerfile/*` tags, and PRs except docs-only paths. It calls `.test.yml` for frontend packages/kinds, computes image matrix entries for `mainline` and `labs` channels, builds/pushes `docker/dockerfile-upstream` images with SBOMs and metadata, scans master tags with Docker Scout, and drafts GitHub releases for Dockerfile tags.

## Dependencies And Integration
Uses Buildx/bake target `frontend-image-cross`, DockerHub secrets, reusable `docker/github-builder`, Codecov, Scout, SARIF upload, and `softprops/action-gh-release`. Tag logic handles semver major/minor/latest tags plus channel suffixes.

## Risks And Test Signals
Channel parsing is a critical risk: malformed `dockerfile/*` tags can publish unexpected tags or releases. Persistent effects are DockerHub images, SARIF uploads, and draft releases. Test signals are frontend integration tests, image build outputs, Scout reports, and release draft metadata.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/frontend.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/labeler.yml -->
# sources/cloud-native/buildkit/.github/workflows/labeler.yml

## Purpose
Runs the GitHub labeler on pull requests to apply path-derived labels.

## APIs, Flow, And State
Triggered by `pull_request_target` with a concurrency group by PR number. It grants `pull-requests: write` only to the job and invokes `actions/labeler` with `sync-labels: true`, so labels are updated to match current changed files.

## Dependencies And Integration
Consumes `.github/labeler.yml`. The `pull_request_target` trigger is annotated as safe because the workflow does not checkout or execute PR code.

## Risks And Test Signals
`sync-labels` can remove manually adjusted area labels if they overlap configured labels. Security risk stays low as long as no untrusted checkout/commands are added. Test signal is PR label changes and workflow logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/labeler.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/pr-assign-author.yml -->
# sources/cloud-native/buildkit/.github/workflows/pr-assign-author.yml

## Purpose
Automatically assigns pull request authors on opened or reopened PRs.

## APIs, Flow, And State
Triggered by `pull_request_target` for `opened` and `reopened`. It delegates to the reusable `crazy-max/.github` workflow and grants `pull-requests: write` for assignment updates. State persists as GitHub assignee metadata.

## Dependencies And Integration
Depends on the pinned external reusable workflow. It complements labeler and triage automation by ensuring a PR has an assignee.

## Risks And Test Signals
The external workflow owns behavior, so changes require updating the pinned SHA. The same `pull_request_target` safety principle applies: avoid adding untrusted code checkout. Test signal is assignee mutation on new/reopened PRs.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/pr-assign-author.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/test-os.yml -->
# sources/cloud-native/buildkit/.github/workflows/test-os.yml

## Purpose
Builds and tests BuildKit on non-default operating systems, mainly Windows and FreeBSD, and performs sandbox Linux builds.

## APIs, Flow, And State
The `build` job cross-builds `windows/amd64` and `freebsd/amd64` binaries via bake and uploads artifacts. `test-windows-amd64` downloads binaries, shards package tests, runs `gotestsum`, uploads Codecov and test reports. `test-freebsd-amd64` downloads FreeBSD binaries, installs Vagrant/libvirt, boots a FreeBSD VM, retries smoke provisioning, and prints BuildKit/containerd logs. `sandbox-build` verifies integration test base builds on linux/amd64 and arm64 for the canonical repo.

## Dependencies And Integration
Depends on Buildx, QEMU indirectly through bake images, GitHub cache/artifacts, Codecov, gotest annotations, Vagrant, libvirt, and `hack/Vagrantfile.freebsd`.

## Risks And Test Signals
High flake risk from Windows runners, Vagrant/libvirt installation, FreeBSD VM boot, and cache state. Persistent state includes artifacts, test reports, Codecov data, and runner cache. Strong test signals cover cross-compiled binaries, Windows integration/unit behavior, FreeBSD smoke behavior, and Linux sandbox buildability.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/test-os.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/validate.yml -->
# sources/cloud-native/buildkit/.github/workflows/validate.yml

## Purpose
Runs BuildKit validation bake targets across platforms selected from the bake definition.

## APIs, Flow, And State
`prepare` checks out the repo, asks `docker/bake-action/subaction/matrix` for the `validate` target platforms, then enriches entries with either arm or x86 runners based on platform and repository privacy. `validate` sets up Buildx and executes the target/platform pair.

## Dependencies And Integration
Depends on bake target `validate`, Buildx, the BuildKit setup image, and optional public `ubuntu-24.04-arm` runners. Environment toggles enable multi-platform lint/archutil validation only for `moby/buildkit`.

## Risks And Test Signals
Dynamic bake matrices can hide validation gaps if bake target metadata drifts. Runner selection must avoid unavailable arm runners for private repositories. Test signal is each bake validation target status.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/validate.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/zizmor.yml -->
# sources/cloud-native/buildkit/.github/workflows/zizmor.yml

## Purpose
Runs Zizmor security analysis for GitHub Actions workflows.

## APIs, Flow, And State
Triggered on manual dispatch, pushes, tags, and PRs. Delegates to `crazy-max/.github/.github/workflows/zizmor.yml` with medium severity/confidence thresholds and `pedantic` persona. Grants SARIF upload permission.

## Dependencies And Integration
Depends on the external reusable workflow and integrates with GitHub code scanning through `security-events: write`.

## Risks And Test Signals
Findings depend on the external workflow version and Zizmor rule set. The workflow itself helps police risks visible in files in this subset, including dangerous triggers and unpinned actions. Test signal is SARIF/code-scanning output and workflow status.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.github/workflows/zizmor.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.golangci.yml -->
# sources/cloud-native/buildkit/.golangci.yml

## Purpose
Configures `golangci-lint` for BuildKit. It disables default linters and opts into a curated set focused on correctness, error handling, dependency hygiene, security, import aliases, test assertions, and formatting.

## APIs, Flow, And State
The configuration is consumed by the lint bake target. `run.modules-download-mode: vendor` enforces vendored module use. Depguard rejects deprecated/misleading imports. Forbidigo blocks direct use of older context, logging, platform, and `fmt.Errorf` patterns. Import alias rules require aliases for key packages. Generated `.pb.go` and `examples` are excluded for lint/format.

## Dependencies And Integration
Integrated with `Makefile lint`, bake validation, generated protobuf files, and vendored dependencies. It encodes project policy for logging (`bklog`), context cancellation causes, error wrapping, and package aliases.

## Risks And Test Signals
Overly broad exclusions can hide generated-file problems; strict forbid rules can block legitimate exceptions unless locally suppressed. Test signal is lint target success across packages and platforms.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.protolint.yaml -->
# sources/cloud-native/buildkit/.protolint.yaml

## Purpose
Defines protobuf lint policy for BuildKit.

## APIs, Flow, And State
Uses protolint v2 config. It disables defaults, then enables syntax consistency, quote consistency, tab indentation, sorted imports, lowercase package names, and upper-camel RPC/service names. The `/vendor` path is ignored. No runtime state is persisted.

## Dependencies And Integration
Applies to `.proto` files such as `api/services/control/control.proto`, likely through bake validation/generated-file targets. It works with the protobuf generation pipeline that creates `.pb.go`, `_grpc.pb.go`, and vtproto outputs.

## Risks And Test Signals
The rules intentionally focus on style and naming, not API compatibility. A proto can pass lint while still breaking wire/backward compatibility. Test signals are protolint success and generated-file validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.protolint.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/.yamllint.yml -->
# sources/cloud-native/buildkit/.yamllint.yml

## Purpose
Configures YAML linting for workflow/configuration files.

## APIs, Flow, And State
Extends yamllint defaults for `*.yaml` and `*.yml`, disabling truthy, line-length, document-start, and trailing-spaces checks while requiring comment spacing. This affects CI/config quality only and creates no runtime state.

## Dependencies And Integration
Applies to issue templates, workflow files, Dependabot config, labeler config, and other YAML in the repository. It likely runs through the validation bake target.

## Risks And Test Signals
Disabled `truthy` is practical for GitHub Actions syntax but reduces detection of ambiguous YAML booleans. Line-length disabled permits long links and commands. Test signal is yamllint success in validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/.yamllint.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/Dockerfile -->
# sources/cloud-native/buildkit/Dockerfile

## Purpose
Multi-stage BuildKit build definition. It builds BuildKit binaries/images, release archives, rootless/debug variants, integration-test images, and supporting test tools such as runc, containerd variants, registry, CNI plugins, stargz snapshotter, nydus, minio, gotestsum, and delve.

## APIs, Flow, And State
Public inputs are build args for tool versions, base image selection, Go version, debug mode, build tags, target platform, and output base. Stages derive from `golang`, `alpine`, `ubuntu`, Docker binaries, and external source repositories. Control flow is stage composition: compile toolchain helpers, compute version ldflags from Git, build `buildctl`/`buildkitd`, package OS-specific binaries, assemble runtime images, assemble integration-test images, and expose final target `buildkit`.

## Dependencies And Integration
Heavily integrated with `docker-bake.hcl`, Makefile targets, CI workflows, `hack/test`, release workflows, and DockerHub publishing. It depends on vendored Go modules, `tonistiigi/xx`, BuildKit Dockerfile frontend features, remote Git `ADD --keep-git-dir`, pinned image/tool versions, QEMU/binfmt helpers, rootlesskit, CNI, Docker Engine/CLI, Buildx, and fixture scripts.

## State And Persistence
Build cache mounts persist compiler/module/cache data in BuildKit cache. Resulting artifacts persist as local outputs, release tarballs, OCI images, DockerHub images, test images, and mounted volumes (`/var/lib/buildkit`, rootless state dirs).

## Risks And Test Signals
Risks include supply-chain drift in remote Git/image downloads, platform-specific static linking failures, emulation flakes, version metadata failures when `.git` is absent, and large test image complexity. Test signals include `xx-verify`, `--version` checks, bake target success, integration tests, release artifact contents, SBOM/provenance generation, and image runtime smoke tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/Makefile -->
# sources/cloud-native/buildkit/Makefile

## Purpose
Developer and CI convenience wrapper around Docker Buildx Bake and repository scripts. It provides standard targets for binaries, cross builds, images, frontend images, install, release, clean, tests, lint, validations, vendoring, generated files, archutil, authors, doctoc, and docs.

## APIs, Flow, And State
The Makefile resolves `BUILDX_CMD` from `BUILDX_BIN`, `docker buildx`, standalone `buildx`, or defaults to `docker buildx`. Most targets call `$(BUILDX_CMD) bake <target>`. `release` flattens `bin/release`; `vendor` writes a temporary bake output, replaces `./vendor`, and cleans the temp dir; `install` copies `bin/build/*` to `DESTDIR$(bindir)`; `clean` removes `./bin`.

## Dependencies And Integration
Depends on Docker Buildx, bake target names in `docker-bake.hcl`, `hack/test`, shell utilities, and environment variables such as `DESTDIR`, `BUILDX_BIN`, `IMAGE_TARGET`, and `FRONTEND_CHANNEL`.

## Risks And Test Signals
`vendor` is destructive to `./vendor` by design, so interrupted runs can leave a partial vendor tree. `release` assumes a nested output layout. Test signals are target exit codes and artifact/tree changes under `bin`, `vendor`, generated files, docs, and author lists.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/api/services/control/control.pb.go -->
# sources/cloud-native/buildkit/api/services/control/control.pb.go

## Purpose
Generated Go protobuf model for the BuildKit Control API defined in `control.proto`. It provides message structs, enum constants, getters, reflection descriptors, dependency indexes, and type initialization for clients and servers.

## APIs, Types, And Flow
Exports `BuildHistoryEventType` with `STARTED`, `COMPLETE`, and `DELETED`; message structs for disk usage/prune (`PruneRequest`, `DiskUsageRequest`, `UsageRecord`), solving (`SolveRequest`, `CacheOptions`, `CacheOptionsEntry`, `Exporter`, `SolveResponse`), progress (`StatusRequest`, `StatusResponse`, `Vertex`, `VertexStatus`, `VertexLog`, `VertexWarning`), session (`BytesMessage`), workers/info (`ListWorkersRequest`, `ListWorkersResponse`, `InfoRequest`, `InfoResponse`), and build history (`BuildHistoryRequest`, `BuildHistoryEvent`, `BuildHistoryRecord`, `UpdateBuildHistoryRequest`, `Descriptor`, `BuildResultInfo`). Each struct has `Reset`, `String`, `ProtoReflect`, deprecated `Descriptor`, and nil-safe `Get*` methods. Initialization builds one enum, thirty-nine messages, and one service descriptor through `protoimpl.TypeBuilder`.

## Dependencies And Integration
Imports BuildKit worker types, solver pb definitions, source policy pb definitions, Google timestamps, and Google RPC status. `client` and `cmd/buildctl` code use these structs via the generated gRPC client. Fast `MarshalVT`/`UnmarshalVT` methods are not in this file; they are generated in adjacent `control_vtproto.pb.go`, which `control_bench_test.go` benchmarks.

## State, Risks, And Test Signals
State is serialized protobuf data crossing gRPC boundaries; compatibility depends on stable field numbers and reserved/deprecated fields. Risks include editing generated code directly, changing field numbers, map key type drift, and forgetting to regenerate vtproto/grpc outputs after proto changes. Test signals include generated-file validation, Go compile, protobuf reflection use, gRPC integration tests, and vtproto benchmarks.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/api/services/control/control.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/api/services/control/control.proto -->
# sources/cloud-native/buildkit/api/services/control/control.proto

## Purpose
Authoritative protobuf/gRPC contract for the BuildKit control plane. It describes how clients ask a BuildKit daemon to solve builds, stream progress, manage sessions, inspect/prune storage, list workers, query daemon info, and listen/update build history.

## APIs, Types, And Control Flow
Service `Control` defines unary RPCs `DiskUsage`, `Solve`, `ListWorkers`, `Info`, and `UpdateBuildHistory`; server-streaming RPCs `Prune`, `Status`, and `ListenBuildHistory`; and bidirectional streaming RPC `Session`. `SolveRequest` ties together LLB definitions, frontend settings, cache imports/exports, entitlements, source policy, multiple exporters, session IDs, compatibility version, and proxy network behavior. `StatusResponse` multiplexes vertex metadata, transfer/status updates, logs, and warnings. Build history messages model events, records, descriptors for logs/traces/errors, exporter responses, result descriptors, pinning, and step counts.

## Dependencies And Integration
Imports worker records, solver operation protobufs, source policy protobufs, timestamps, and `google.rpc.Status`. Generated outputs include `control.pb.go`, `control_grpc.pb.go`, and vtproto helpers. Clients in `client/*` and `cmd/buildctl/debug/*` consume this contract; servers implement it in the daemon control path.

## State, Risks, And Test Signals
Persistent/remote state includes cache records, build refs, sessions, build history records, log/trace descriptors, and worker metadata. API compatibility is the critical risk: field numbers must remain stable, deprecated fields must be honored for old clients, and streaming semantics must not regress. Test signals are proto lint, generated-file validation, compile, client integration tests, build history tests, and gRPC stream behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/api/services/control/control.proto -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/api/services/control/control_bench_test.go -->
# sources/cloud-native/buildkit/api/services/control/control_bench_test.go

## Purpose
Benchmarks vtproto marshal/unmarshal performance for hot progress messages: `Vertex`, `VertexStatus`, and `VertexLog`.

## APIs, Flow, And State
Benchmark functions construct sample messages, then loop over `MarshalVT` or `UnmarshalVT`. Global sinks `Buf`, `VertexOutput`, `VertexStatusOutput`, and `VertexLogOutput` prevent compiler optimization from discarding results. Samples use `time.Now`, `opencontainers/go-digest`, protobuf timestamps, and representative fields for digests, names, byte counts, streams, and log bytes.

## Dependencies And Integration
Depends on generated vtproto methods in `control_vtproto.pb.go`, standard protobuf marshal for creating encoded buffers, and `testify/require` for benchmark-time error checks. It exercises message types generated from `control.proto`.

## Risks And Test Signals
This is performance coverage, not semantic test coverage. It does not benchmark every Control message, map-heavy structures, or streaming gRPC. It can catch vtproto generation/compatibility failures at compile time and provides benchmark signals for progress serialization hot paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/api/services/control/control_bench_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/api/services/control/control_grpc.pb.go -->
# sources/cloud-native/buildkit/api/services/control/control_grpc.pb.go

## Purpose
Generated gRPC bindings for the BuildKit Control service. It exposes typed clients, server interfaces, registration, stream aliases, method handlers, and `grpc.ServiceDesc`.

## APIs, Types, And Flow
Exports full method-name constants, `ControlClient`, concrete `controlClient`, `NewControlClient`, `ControlServer`, `UnimplementedControlServer`, `UnsafeControlServer`, `RegisterControlServer`, stream aliases, unary handlers, streaming handlers, and `Control_ServiceDesc`. Client methods use `cc.Invoke` for unary calls and `cc.NewStream` plus generic client streams for server/bidi streams. Server handlers decode requests, invoke interceptors for unary calls, and wrap streams in generic server stream types. Registration verifies `UnimplementedControlServer` is embedded by value to avoid nil pointer panics.

## Dependencies And Integration
Requires gRPC-Go v1.64+ (`SupportPackageIsVersion9`) and the message types from `control.pb.go`. BuildKit clients call `NewControlClient`; daemon-side control implementations register with `RegisterControlServer`.

## State, Risks, And Test Signals
No state is stored here beyond stream lifetimes; runtime state is in the server implementation and gRPC transport. Risks include direct edits to generated code, mismatched gRPC/protobuf generator versions, changed service methods without server implementation updates, and streaming cancellation/CloseSend regressions. Test signals are Go compile, gRPC integration tests for solve/status/session/history/prune, and generated-file validation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/api/services/control/control_grpc.pb.go -->
