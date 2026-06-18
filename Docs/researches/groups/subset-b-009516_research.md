# Research Report: subset-b-009516

Grouped research for the requested syzkaller subset. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/report.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/service/report.go

This file implements `ReportService`, the service-layer coordinator for moderator and reporter-facing session reports in syz-cluster. It owns repositories for reports, sessions, jobs, session tests, and test steps, plus nested `SeriesService` and `FindingService` dependencies and a URL generator. Its public API is `NewReportService`, `Confirm`, `Upstream`, `Invalidate`, and `Next`, with helper `populatePatchTestReport` and `query`.

The control flow is repository-driven. `Confirm` updates a report's `ReportedAt` timestamp if unset and translates missing entities to `ErrReportNotFound`. `Upstream` only accepts moderation reports, then inserts a fresh non-moderation `SessionReport` for the same session/reporter, relying on a database uniqueness index to prevent duplicate concurrent upstream scheduling. `Invalidate` finds the report and invalidates all findings for the report's session. `Next` pulls one unreported item for a reporter, enriches it with short series metadata, up to five findings, session info, and either bug-report or patch-test fields. Patch-test reports load job metadata, Cc routing, tests, test steps, and infrastructure error text.

State persists through Spanner repositories and blob-backed finding/test data indirectly. Important integration points are the reporter API server, moderation/upstream email flow, job-generated patch tests, and URL generation for series, sessions, and job patches. Risks include concurrent `Upstream` calls relying on DB constraints, `Next` returning an empty response rather than an error when no report exists, and patch-test error selection using the first infra error/skipped reason encountered. Test coverage is indirect in controller/reporter workflows rather than in this file.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/report.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/series.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/service/series.go

`SeriesService` maps external patch-series API objects to persistent Spanner rows plus blob-stored patch bodies. It exposes `UploadSeries`, `GetSeries`, `GetSessionSeries`, and `GetSessionSeriesShort`; the short variant omits patch body blob reads for report previews.

`UploadSeries` builds a `db.Series` with UUID, metadata, subject tags truncated to 511 bytes, optional base-commit hint, and one `db.Patch` per API patch. Patch bodies are written to `blob.Storage` under `Series/<seriesID>/Patches/<seq>` before the repository insert callback returns patch rows. Duplicate series are converted to `UploadSeriesResp{Saved:false}` via `db.ErrSeriesExists`; other errors propagate. Reads fetch series rows, list patch rows, and optionally read each body URI back from blob storage.

Persistent state spans Spanner series/patch rows and external blob storage, so partial blob writes may remain if the later insert fails. Dependencies are `cloud.google.com/go/spanner` null strings, syz-cluster API/db/blob/app packages, and UUID generation. Integration points include the series tracker upload path, session creation, triage, reporting, and controller APIs. Risk areas are orphaned blobs, byte-based tag truncation that may cut multibyte text, and body read latency for full series fetches. The comment notes service behavior is tested through controller-level tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/series.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/session.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/service/session.go

`SessionService` manages fuzzing/testing sessions tied to uploaded patch series and optional jobs. Its public methods are `UploadSession`, `TriageResult`, and `GetSessionInfo`; construction wires session, series, job, and blob dependencies from `app.AppEnvironment`.

`UploadSession` resolves an external series ID to an internal series row, creates a session with tags and `CreatedAt`, and returns the generated session ID. `TriageResult` optionally writes triage logs to blob storage and updates session state with the triage log URI and skip reason. `GetSessionInfo` fetches full series data, reloads the session row, and includes job details when `JobID` is set.

State persists in Spanner sessions and blob storage for triage logs. Integration points are the series tracker, triage workflow action, controller HTTP API, and report-generation path. Risks include blob log writes preceding session update, session creation failing if series import has not completed, and `GetSessionInfo` doing full patch-body reads even when only metadata might be needed by some callers. Errors are normalized for missing series/session through shared service errors.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/session.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/session_test_step.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/service/session_test_step.go

`SessionTestStepService` persists fine-grained step results for a named session test. The main API is `Save(ctx, sessionID, step)`, which stores a keyed step by session, test name, title, and target.

The repository `Store` callback receives the owning session and optional old step, creates or reuses a UUID, copies finding ID, target, result, and commit timestamp, and optionally uploads step logs to blob storage under `SessionTestStep/<stepID>/log`. The use of the old ID makes repeated updates to the same logical step stable.

State is split between Spanner `SessionTestStep` rows and blob log objects. This file integrates with workflow boot/fuzz/retest reporting, report rendering in `ReportService.populatePatchTestReport`, and stats queries that count prevented bugs from passed patched-target steps. Risks include log blob orphaning if the database write fails after upload and identity collisions if title/target are not sufficiently unique for a test. Coverage is mainly through repository/controller/stats tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/session_test_step.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/sessiontest.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/service/sessiontest.go

`SessionTestService` records coarse session-test status and associated logs/artifacts. It exposes `Save` for result/log/build metadata and `SaveArtifacts` for a post-submission artifact archive.

`Save` loads or initializes the `db.SessionTest`, preserves an existing log URI unless a new log is provided, writes new logs under `Session/<sessionID>/Test/<testName>/log`, and upserts result, updated time, log URI, and optional base/patched build IDs. `SaveArtifacts` requires the test row to already exist, uploads a reader to `.../artifacts`, and writes the archive URI back to the row.

The file persists state in Spanner plus blob objects. It integrates with boot, fuzz, and retest workflow actions and with report generation for patch-test summaries. Risks include artifact uploads being rejected before a test status exists, blob writes before database success, and no explicit size guard in this service layer. Test signals come through workflow/controller paths and report assembly rather than direct unit tests here.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/service/sessiontest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/stats/worker.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/stats/worker.go

This file defines a periodic `stats.Worker` that recomputes denormalized per-series statistics. `NewWorker` accepts repositories and an interval, `Loop` ticks until context cancellation, `RunOnce` fetches outdated series in batches of ten, and `processSeries` calculates and stores stats.

The central state transition is `processSeries`: count prevented bugs for the current series, upsert a `db.SeriesStats` row with `StatsVersion: "v1"`, `PreventedBugs`, and `UpdatedAt`, then find previous versions of the same series and bulk-update their prevented bug counts to zero. This encodes the rule that only the latest version contributes prevented-bug totals.

Dependencies are `SeriesRepository`, `SeriesStatsRepository`, `StatsRepository`, context cancellation, and syzkaller logging. Integration points include dashboard/stat API queries and session-test-step data that feeds `CountPreventedBugs`. Risks include fixed batch size delaying catch-up on large backlogs, errors being logged but not retried immediately in the same tick, and stats-version changes requiring repository `ListOutdated` semantics to be correct.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/stats/worker.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/stats/worker_test.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/stats/worker_test.go

`TestWorker` is an integration-style test for the stats worker using a test app environment, controller test server, real repositories, and fake series/findings. It verifies the prevented-bugs aggregation and old-version reset behavior.

The test creates a first series with findings, uploads a patched-target passed test step tied to one finding, confirms no stats row exists before `RunOnce`, then expects one prevented bug. It creates a second version with two passed patched steps referring to the same finding across two test names, runs the worker again, and expects the first series stat to be zeroed while the second has one prevented bug. Finally it validates `PreventedBugsPerMonth` returns one series and one bug.

This is the key test signal for `pkg/stats/worker.go` and its repository queries. It exercises controller upload APIs, finding repository reads, session-test and test-step persistence, stats upsert, previous-version discovery, and monthly aggregation. Risks not fully covered include worker loop timing/cancellation and error logging paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/stats/worker_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/triage/commit.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/triage/commit.go

This file contains commit-selection logic for choosing a base kernel commit on which a patch series should be tested. It defines `TreeOps`, `CommitSelector`, `SelectResult`, public `Select`, and base-commit helpers `FromBaseCommits` and `bestCommit`.

`Select` queries the tree head, rejects series more than seven days behind head, optionally tries a recent last successful build first, then tries current head. Each candidate is accepted only if `TreeOps.ApplySeries` applies all patch bodies. Failure reasons distinguish age from non-applicability. `FromBaseCommits` ranks blob-detected base commits by trees selected from series Cc/tags first, then all configured trees; `bestCommit` prefers earlier tree order and exact branch matches.

Dependencies are abstracted through `TreeOps`, `debugtracer`, `vcs`, and syz-cluster API types. Integration points are `workflow/triage/main.go` and `GitTreeOps`. Risks include the fixed seven-day cutoff, no support yet for intentionally stale experimental sessions, and branch ranking depending on configured tree order. Unit tests cover freshness, last-build preference, non-applying patches, and base-commit/tree ranking.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/triage/commit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/triage/commit_test.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/triage/commit_test.go

This test file validates commit-selection heuristics with deterministic fake tree operations. `TestCommitSelector` covers fresh series, fresh/stale last build preference, slightly old versus too-old series, fallback from failed last-build application to head, and no-applicable-commit outcomes.

`TestFromBaseCommits` builds ordered tree/base-commit fixtures and verifies selection by exact branch, higher-priority tree among Cc-matching trees, and fallback to any tree when Cc-selected trees do not appear. Helpers include a date parser, shared `testTree`, and `testGitOps` implementing `HeadCommit` and `ApplySeries` through maps.

The tests are strong signals for branch ranking and age/apply behavior but do not exercise real git, tracer output, nil head edge cases beyond returning nil errors, or concurrent repository mutation. Real git behavior is separately tested in `git_test.go`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/triage/commit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/triage/fuzz_target.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/triage/fuzz_target.go

This file selects and merges fuzzing campaigns for a patch series. `SelectFuzzConfigs` matches series Cc addresses against configured `api.FuzzTriageTarget.EmailLists`, falling back to targets with no email lists only when no exact match exists. `MergeKernelFuzzConfigs` groups compatible kernel fuzz configs into fewer campaigns.

Merging groups configs by kernel config, track, and bug-title regexp. Within each group, `mergeFuzzConfigs` combines focus areas and corpus URLs, ORs `SkipCoverCheck`, and carries the common `BugTitleRe`; `unique` sorts/deduplicates strings using `maps.Keys` and `slices.Sorted`.

State is pure in-memory; no persistence. Integration points are triage workflow target generation and fuzz workflow configuration. Risks include configured `EmailLists` being compared case-sensitively on the target side while series Cc is lowercased, grouping assuming `BugTitleRe` equality but not validating other fields, and sorted unique output changing user-specified focus ordering. Unit tests cover selection fallback and merge semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/triage/fuzz_target.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/triage/fuzz_target_test.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/triage/fuzz_target_test.go

This file tests fuzz-target selection and merge behavior. `TestSelectFuzzConfigs` verifies single Cc match, multiple Cc matches, and default fallback. `TestMergeKernelFuzzConfigs` verifies distinct kernel configs/tracks stay split while compatible configs merge. `TestMergeFuzzConfigs` verifies focus/corpus deduplication, skip-cover OR behavior, and bug-title regexp propagation.

The test signals are focused on pure functions and avoid external state. They do not cover case normalization mismatches for configured email lists, empty config input, or order behavior across grouped keys beyond the explicit examples.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/triage/fuzz_target_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/triage/git.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/triage/git.go

`GitTreeOps` adapts syzkaller's `vcs.Git` to the `TreeOps` and base-diff operations needed by triage. `NewGitTreeOps` initializes a git checkout wrapper with environment inheritance, optional sandboxing, and a reset. `HeadCommit`, `Commit`, `ApplySeries`, and `BaseForDiff` expose tree branch lookup, commit lookup, patch application, and blob-based base detection.

The branch naming contract is tied to kernel-disk machinery: tree heads are addressed as `<tree.Name>/<tree.Branch>`, and non-hash commit references are resolved as `<treeName>/<branch>`. `ApplySeries` resets hard to the candidate commit, then applies each patch sequentially, returning the patch index on failure.

State mutation happens directly in the git worktree through reset and apply. Integration points are the triage workflow action, commit selector, and kernel repository PVC. Risks include destructive worktree mutation by design, sandbox test limitations noted in TODO, and dependence on branch naming conventions. Tests cover branch tag lookup and patch application success/failure in a temporary repo.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/triage/git.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/triage/git_test.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/triage/git_test.go

This file validates `GitTreeOps` against real temporary git repositories created by syzkaller test helpers. `TestGitTreeOpsHead` creates two commits and tags/refs that emulate kernel-disk naming, then confirms the correct tree/branch commit is resolved. `TestGitTreeOpsApply` confirms a good patch applies and a second non-applying patch produces an error after reset.

The embedded patch fixtures model realistic email-style git patches. These tests cover important integration behavior between syz-cluster triage and `pkg/vcs`, but they do not cover `BaseForDiff`, sandbox mode, or concurrent use of one checkout.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/triage/git_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/triage/tree.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/triage/tree.go

This file contains tree-selection helpers for triage. `SelectTrees` returns ordered candidate kernel trees using subject tags, series Cc, and fallback trees. `FindTree` maps a branch string like `tree/branch` to a configured tree index and branch name. `FindTreeByName` performs direct name lookup.

`SelectTrees` lowercases series Cc addresses, treats subject tags that match a tree name as forced selections, filters out trees with non-empty email lists that do not intersect Cc, includes trees with no email lists as fallback, and stable-sorts direct subject-tag matches before other selected trees. The function preserves original configured order otherwise.

State is pure in-memory. Integration points are commit selection, base-commit hint resolution, and job/series triage. Risks include subject tags requiring exact tree-name equality and fallback trees always joining selected email-list trees. Tests cover Cc matching, fallback, direct tag preference, branch parsing, and name lookup.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/triage/tree.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/triage/tree_test.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/triage/tree_test.go

`tree_test.go` validates pure tree helper behavior. `TestSelectTrees` covers single subsystem match, configured-order preservation across multiple matches, fallback to mainline, and subject-tag priority over Cc-derived trees. `TestTreeFromBranch` validates parsing `tree/branch` references. `TestFindTreeByName` validates successful and missing name lookup.

These tests are concise and deterministic. They do not cover case-insensitive configured email lists or duplicate tree names, but they provide the core signal for triage ordering semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/triage/tree_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/workflow/argo.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/workflow/argo.go

`ArgoService` implements the workflow `Service` interface using in-cluster Argo Workflows. It embeds YAML files from the package, loads `template.yaml`, creates an Argo workflow client for the `default` namespace, starts workflows labeled by session ID, and polls status/log output.

`Start` deep-copies the embedded template, sets `workflow-id=<sessionID>`, substitutes the `session-id` argument, and creates the workflow. `Status` lists workflows by label, maps Argo phases to `StatusRunning`, `StatusFinished`, or `StatusFailed`, and returns synthesized node logs. `generateLog` sorts node status by start time/name and records phase, timestamps, inputs, and outputs. `PollPeriod` recommends 30 seconds.

State is stored in Kubernetes/Argo workflow objects, not locally. Dependencies are Argo client-go types, Kubernetes in-cluster config, embedded filesystem, and YAML unmarshalling. Integration points are controller/session processing services that start and monitor workflows. Risks include hard-coded namespace, selecting the first workflow when multiple share a label, no context propagation to Kubernetes calls, and TODO image naming. Test coverage appears indirect through mock service support rather than this concrete Argo client.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/workflow/argo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/workflow/service.go -->
## sources/test-tools/syzkaller/syz-cluster/pkg/workflow/service.go

This file defines the workflow abstraction used by syz-cluster to start and monitor patch-series workflows. `Service` has `Start`, `Status`, and `PollPeriod`. `Status` is a string enum with `not_found`, `running`, `finished`, and `failed`.

`MockService` is a test helper with a mutex around `OnStart` and `OnStatus` callbacks so tests can deterministically serialize workflow callback behavior. Default `Start` succeeds, default `Status` returns `StatusNotFound`, and `PollPeriod` returns the configured delay.

The interface isolates controller/service code from Argo. There is no persistent state except callback-controlled mock state in tests. Risks are limited: callers must interpret `StatusNotFound` correctly and mock callbacks can still encode arbitrary behavior. The typo in the comment ("dong boot tests") is non-functional.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/workflow/service.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/workflow/template.yaml -->
## sources/test-tools/syzkaller/syz-cluster/pkg/workflow/template.yaml

This embedded Argo `Workflow` template orchestrates an end-to-end series workflow for one session. It starts with triage, exits early on skip, then processes each target through base build, optional base boot, patched build, patched boot, optional fuzzing, and optional retesting.

The main template has `failFast: true` and parallelism 2 for target processing. `process-target` converts JSON parameters to artifacts, calls `build-action-template`, `boot-action-template`, `fuzz-action-template`, and `retest-action-template`, and uses JSONPath expressions to pass build IDs, configs, test names, and artifacts. Fuzz and retest are conditional on triage output fields. `convert-artifact` writes parameter data to `/tmp/artifact`; `exit-workflow` exits with a configurable nonzero code.

State persists in Argo workflow status/artifacts and through each action's calls back to syz-cluster APIs. Integration depends on workflow templates in sibling directories, session-id workflow parameter, and artifact names (`kernel`, `request`, `config`, `retest-task`). Risks include shell quoting in `convert-artifact` for arbitrary JSON, expression complexity, optional base artifacts in retest, and `continueOn.failed` at target iteration possibly allowing partial workflow failure semantics. No direct tests for this YAML were observed.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/pkg/workflow/template.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/reporter-server/Dockerfile -->
## sources/test-tools/syzkaller/syz-cluster/reporter-server/Dockerfile

This Dockerfile packages the `reporter-server` binary. It uses the common `syz-cluster-build` image as a builder source, then copies `/build/syz-cluster/bin/reporter-server` into a minimal Alpine runtime, exposes port 8080, and sets the binary as entrypoint.

The image depends on build args `IMAGE_PREFIX` and `IMAGE_TAG` defaulting to `local/` and `latest`. There is no runtime package installation, so the binary must be fully self-contained for Alpine. Integration is with the reporter-server Kubernetes deployment. Risks include libc/static-link assumptions and no explicit non-root user.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/reporter-server/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/reporter-server/deployment.yaml -->
## sources/test-tools/syzkaller/syz-cluster/reporter-server/deployment.yaml

This Kubernetes deployment runs one `reporter-server` pod. It uses Terraform-defined `gke-service-ksa`, image `${IMAGE_PREFIX}reporter-server:${IMAGE_TAG}`, config-map environment from `global-config-env`, and mounts `global-config` at `/config`.

The pod exposes container port 8080 and requests/limits relatively large CPU and memory. Integration points are `reporter-server/service.yaml`, global config overlays, Spanner/blob/email configuration via env/config, and the reporter API/generator process. Risks include single replica availability, service account external definition, and high static resource requests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/reporter-server/deployment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/reporter-server/kustomization.yaml -->
## sources/test-tools/syzkaller/syz-cluster/reporter-server/kustomization.yaml

This kustomization includes `deployment.yaml` and `service.yaml` for reporter-server. It has no patches, generators, or image transformations locally, so environment-specific substitutions must happen in parent overlays or build tooling.

The file is an integration manifest with no runtime state. Risk is mainly omission: if parent overlays do not inject `${IMAGE_PREFIX}`/`${IMAGE_TAG}` or config maps, deployment manifests remain templated.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/reporter-server/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/reporter-server/main.go -->
## sources/test-tools/syzkaller/syz-cluster/reporter-server/main.go

This is the reporter-server entrypoint. It initializes the syz-cluster app environment, starts a background `reporter.Generator` loop, creates a reporter API server, and serves its mux on `:8080`.

The process has two major flows: background report generation and synchronous HTTP handling. `context.Background()` is shared and there is no explicit shutdown handling in this file. Dependencies are `pkg/app` for configuration/environment and `pkg/reporter` for generation/API logic.

Persistent state is handled by downstream repositories and blob/email integrations in the reporter package. Risks include fatal process exit on HTTP server failure, no graceful shutdown, and generator lifecycle tied only to process lifetime. Test coverage is expected in the reporter package rather than the entrypoint.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/reporter-server/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/reporter-server/service.yaml -->
## sources/test-tools/syzkaller/syz-cluster/reporter-server/service.yaml

This Kubernetes `Service` exposes reporter-server pods selected by `app: reporter-server` on TCP port 8080 with targetPort 8080. The service type is `ClusterIP`, so it is internal to the cluster.

It integrates with other in-cluster components that call reporter APIs. Risks are limited to selector/port drift from the deployment and lack of external exposure by design.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/reporter-server/service.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/run-local.sh -->
## sources/test-tools/syzkaller/syz-cluster/run-local.sh

`run-local.sh` is a helper for running a named local image in minikube. It requires the first argument as command/service image name, deletes any previous `run-local` pod, then runs `local/<name>` with `image-pull-policy=Never`, Spanner emulator env vars, local blob storage path, label `app=db-mgmt`, and attaches with `--rm`.

State is transient Kubernetes pod state. It integrates with minikube, local cluster overlays, the Spanner emulator service, and locally built syz-cluster images. Risks include the `kubectl` alias only applying in this script shell, fixed env/config values, label always being `app=db-mgmt` regardless of image, and a typo in the cleanup comment.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/run-local.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/series-tracker/Dockerfile -->
## sources/test-tools/syzkaller/syz-cluster/series-tracker/Dockerfile

This Dockerfile packages `series-tracker`. It copies the binary from the common builder image into an Ubuntu runtime and installs `git`, which is required for polling lore git archives.

Build args are `IMAGE_PREFIX` and `IMAGE_TAG`. Integration is with the series-tracker deployment and persistent git repository volume. Risks include using `ubuntu:latest`, package update variability, and running as root by default.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/series-tracker/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/series-tracker/deployment.yaml -->
## sources/test-tools/syzkaller/syz-cluster/series-tracker/deployment.yaml

This deployment runs one `series-tracker` pod. It mounts a persistent volume at `/git-repo` for polled lore git archives and `global-config` at `/config`, using image `${IMAGE_PREFIX}series-tracker:${IMAGE_TAG}` and large CPU/memory requests.

The pod has no explicit envFrom in this file, so config is expected via mounted files or app defaults. Integration points are the PVC, global config, and controller API upload endpoints. Risks include single-replica polling, persistent repo corruption/size growth, and templated image variables requiring overlay substitution.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/series-tracker/deployment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/series-tracker/git-pvc.yaml -->
## sources/test-tools/syzkaller/syz-cluster/series-tracker/git-pvc.yaml

This manifest defines `series-tracker-repo-disk-claim`, a `ReadWriteOnce` PVC requesting 25Gi on storage class `standard`. It persists git clones of lore archive epochs used by `series-tracker`.

Integration is direct through the series-tracker deployment. Risks include fixed capacity, storage-class environment dependence, and one-writer access limiting horizontal scaling.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/series-tracker/git-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/series-tracker/kustomization.yaml -->
## sources/test-tools/syzkaller/syz-cluster/series-tracker/kustomization.yaml

This kustomization includes `deployment.yaml` and `git-pvc.yaml` for the series tracker. It is a simple resource aggregator; image substitutions and environment-specific storage changes are expected elsewhere.

There is no runtime state in the file. The main risk is that overlays must provide required global config and image values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/series-tracker/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/series-tracker/main.go -->
## sources/test-tools/syzkaller/syz-cluster/series-tracker/main.go

This program polls lore.kernel.org archives, extracts patch series, uploads new series to syz-cluster, and creates a testing session for each saved series. Important types/functions are `SeriesFetcher`, `Update`, `handleSeries`, `seriesProcessor`, `archivesToPoll`, `sanitizeName`, and `logSeries`.

`main` starts a `ManifestSource` loop, initializes polling from the last week, then every 15 minutes polls archives from the previous window. `Update` waits for manifest data, resolves each configured archive to its latest epoch URL, polls a local LKML git repo under `/git-repo/<sanitizedName>`, reads recent email messages, parses them, builds `lore.PatchSeries`, and calls `handleSeries`. `handleSeries` skips corrupted series, normalizes suspicious dates to now, builds `api.Series` metadata and patch bodies, extracts Cc addresses via `seriesProcessor`, uploads the series, and requests a session.

State persists in the local git repo volume and syz-cluster database/blob storage through API calls. Dependencies include lore parsing, git polling, app config/client, and email parsing. Risks include only polling the latest epoch, repeated overlapping windows causing duplicate upload attempts, falling back to raw email when body parsing fails, trusting manifest availability, and single-threaded raw message reads. `main_test.go` covers Cc/body extraction, while manifest parsing is tested separately.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/series-tracker/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/series-tracker/main_test.go -->
## sources/test-tools/syzkaller/syz-cluster/series-tracker/main_test.go

`TestSeriesProcessor` verifies that `seriesProcessor.Process` extracts message bodies and accumulates email addresses from parsed messages. The expected address set includes From, To, and Cc addresses as returned by syzkaller's email parser, sorted by `Emails`.

The test covers the local processing helper used before `UploadSeries`. It does not cover lore polling, corrupted series handling, duplicate series, or session upload failures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/series-tracker/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/series-tracker/manifest.go -->
## sources/test-tools/syzkaller/syz-cluster/series-tracker/manifest.go

This file manages the lore manifest used to discover archive epoch git repositories. `InboxInfo` exposes `EpochURL` and `LastEpochURL`; `ParseManifest` converts `manifest.js` keys into inbox epoch counts; `QueryManifest` downloads and gunzips `manifest.js.gz`; `ManifestSource` continuously refreshes and serves the latest successful manifest.

`ParseManifest` scans JSON object keys with `/([\w-]+)/git/(\d+)\.git`, logs unexpected keys, and stores the maximum epoch plus one per inbox. `ManifestSource.Loop` retries every 15 minutes until the first successful load, closes `firstLoaded`, then refreshes every 12 hours. `Get` blocks until the first load or context cancellation and returns the latest map under a mutex.

State is in memory, refreshed from network. Integration is with `SeriesFetcher.Update`. Risks include using `http.Get` without caller context, no HTTP status validation before gzip, returning the internal map without deep copy, and callers blocking indefinitely if context never cancels and manifest never loads. Unit tests cover parsing and epoch URL construction.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/series-tracker/manifest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/series-tracker/manifest_test.go -->
## sources/test-tools/syzkaller/syz-cluster/series-tracker/manifest_test.go

`TestParseManifest` validates manifest parsing with two inboxes and multiple epochs. It asserts map length, epoch count for the first inbox, epoch count for the second, and URL construction for epoch 1.

The test is a focused signal for key parsing and max-epoch aggregation. It does not cover malformed keys beyond log-only behavior, gzip download, HTTP errors, or `ManifestSource` concurrency/blocking.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/series-tracker/manifest_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/tools/db-mgmt/Dockerfile -->
## sources/test-tools/syzkaller/syz-cluster/tools/db-mgmt/Dockerfile

This Dockerfile packages the `db-mgmt` utility. It copies `/build/syz-cluster/bin/db-mgmt` from the common builder image into Alpine and sets it as entrypoint.

Integration is with the migration job and local run helper. Risks are minimal but include Alpine runtime compatibility and root execution by default.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/tools/db-mgmt/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/tools/db-mgmt/main.go -->
## sources/test-tools/syzkaller/syz-cluster/tools/db-mgmt/main.go

`db-mgmt` is an administrative CLI for creating/checking the Spanner database, running migrations, and executing ad hoc SQL. `runSQL` opens a Spanner client, executes a query, prints column names and values for each row, and closes resources.

`main` resolves the default Spanner URI, creates an emulator instance when `SPANNER_EMULATOR_HOST` is set, ensures the database exists, and then handles optional subcommands: `migrate` runs schema migrations, `run <SQL>` executes a query, and unknown commands fatal. With no subcommand it just verifies/create resources.

State changes target Spanner instance/database/schema. Integration points are local development, the migration Kubernetes job, and `pkg/db` migration code. Risks include unrestricted SQL execution, positional CLI parsing that only accepts the SQL as one argument, and fatal exits for admin workflows. There are no direct tests in this file.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/tools/db-mgmt/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/tools/db-mgmt/migrate-job.yaml -->
## sources/test-tools/syzkaller/syz-cluster/tools/db-mgmt/migrate-job.yaml

This Kubernetes `Job` runs `db-mgmt migrate` with service account `gke-db-admin-ksa`, environment from `global-config-env`, zero retries, and one-day TTL after finish. It uses image `${IMAGE_PREFIX}db-mgmt:${IMAGE_TAG}`.

Integration is with deployment/migration operations and Terraform-defined service accounts. Risks include `backoffLimit: 0` requiring manual rerun on transient errors and templated image variables requiring overlay substitution.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/tools/db-mgmt/migrate-job.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/tools/send-test-email/Dockerfile -->
## sources/test-tools/syzkaller/syz-cluster/tools/send-test-email/Dockerfile

This Dockerfile packages the `send-test-email` tool. It copies the built binary from the common builder image into Alpine as `/bin/send-email` and uses it as entrypoint.

Integration is with the send-test-email job. Risks are Alpine compatibility and root execution by default.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/tools/send-test-email/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/tools/send-test-email/job.yaml -->
## sources/test-tools/syzkaller/syz-cluster/tools/send-test-email/job.yaml

This Kubernetes `Job` sends one test email using the `send-test-email` image. It runs with `gke-email-reporter-ksa`, mounts global config at `/config`, imports `global-config-env`, has no retries, and keeps completed job records for one day.

Integration is with email reporting configuration and service-account permissions. Risks include no retry on transient email provider failures and fixed moderation-list recipient controlled by config.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/tools/send-test-email/job.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/tools/send-test-email/main.go -->
## sources/test-tools/syzkaller/syz-cluster/tools/send-test-email/main.go

This utility loads syz-cluster config, verifies email reporting is configured, constructs an email sender, and sends a fixed test message to the moderation list. It is intended for deployment/config validation rather than application flow.

State is external to the email provider; no local persistence. Dependencies are `app.Config`, `emailclient.MakeSender`, and syzkaller email sender types. Risks include a hard-coded message body typo, fatal behavior on any config/sender error, and no explicit error handling of the final `emailSender` call return because the sender function has no checked return in this usage.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/tools/send-test-email/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/boot/Dockerfile -->
## sources/test-tools/syzkaller/syz-cluster/workflow/boot/Dockerfile

This Dockerfile builds the boot workflow action image. It supports `SMOKE_TEST=0` with Debian plus `qemu-system` and `openssh-client`, and `SMOKE_TEST=1` with a slim dependency-skipping setup. The final stage creates a `syzkaller` user, copies syzkaller binaries and `/bin/boot-action`, and sets the entrypoint.

Integration is with `boot/workflow-template.yaml`. Runtime assumptions include KVM/QEMU availability, syzkaller binaries under `/syzkaller/bin`, and action binary from the cluster builder. Risks include privileged runtime requirements handled in YAML, package variability, and smoke-test images not containing real VM dependencies.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/boot/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/boot/main.go -->
## sources/test-tools/syzkaller/syz-cluster/workflow/boot/main.go

`boot-action` runs a smoke boot test for a supplied kernel artifact and reports session-test status. Flags include session ID, test name, base/patched build IDs, output path, and whether to report boot failures as findings.

`main` uploads a running `api.SessionTest`, runs `runTest` with a timestamped tracer whose output becomes the final log, uploads passed/failed status, and optionally writes an `api.BootResult`. `runTest` generates a base fuzz config, forces VM count to three, completes the manager config, and calls `instance.RunSmokeTest` up to three times. Three consecutive reports are required before failure. When `-findings` is true, the final report is uploaded as a raw finding; otherwise report/output are logged.

State persists through controller API calls for session tests and findings. Integration is with Argo boot template, syzkaller instance smoke tests, fuzzconfig generation, and build artifacts mounted at expected paths. Risks include fatal exits leaving only the initial running state, hard-coded workdir, fixed retry policy, and reliance on global flags inside `runTest`. There are no direct tests in this file.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/boot/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/boot/workflow-template.yaml -->
## sources/test-tools/syzkaller/syz-cluster/workflow/boot/workflow-template.yaml

This Argo `WorkflowTemplate` wraps `boot-action`. It accepts base/patched build IDs, test name, report-findings flag, and a required `kernel` artifact mounted at `/base`. It writes a JSON result to `/output/result.json` and exposes it as an output parameter.

The container requests KVM by mounting host `/dev/kvm` and running privileged, with sizable CPU/memory resources and emptyDir work/output volumes. Integration is with the main workflow template's base and patched boot steps. Risks include privileged host-device access, fixed artifact path `/base`, high resource requirements, and dependence on workflow parameter `session-id`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/boot/workflow-template.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/fuzz/Dockerfile -->
## sources/test-tools/syzkaller/syz-cluster/workflow/fuzz/Dockerfile

This Dockerfile builds the fuzz action image. The normal stage installs QEMU, SSH client, curl, C preprocessor/GCC, and LLVM/Clang 20 tooling from apt.llvm.org; smoke-test mode skips heavy dependencies. The final stage creates a `syzkaller` user, copies syzkaller binaries and `/bin/fuzz-action`, and sets the entrypoint.

Integration is with the fuzz Argo template and diff-fuzz manager code. Risks include external apt key/repository availability, `apt-key` deprecation, large image size, root execution despite creating a user, and smoke-test images lacking runtime dependencies.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/fuzz/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/fuzz/main.go -->
## sources/test-tools/syzkaller/syz-cluster/workflow/fuzz/main.go

`fuzz-action` runs differential fuzzing between base and patched kernels for a triaged target. Flags supply config JSON, session/test IDs, build IDs, timeout, and workdir. It reports running status, executes diff fuzzing under a timeout, uploads findings/base findings, periodically updates logs/artifacts, and finally reports passed/skipped/error.

The run flow loads the session series, enables bounded global log caching, generates base/patched manager configs, reads symbol hashes from `/base` and `/patched`, skips fuzzing if text/data hashes are effectively identical, patches focus areas based on changed code, optionally downloads/merges corpus DBs, and starts three errgroup tasks: bug/base-crash reporting, `diff.Run`, and periodic status/artifact upload. Findings include syz and C repro data when available. Artifact upload tars the diff-fuzzer store with a 64 MB `LimitedWriter`.

State persists through controller APIs: session tests, findings, base findings, and test artifacts. Local state includes workdir subdirectories and diff-fuzzer store. Dependencies include syzkaller build hash data, manager/diff fuzzer, corpus DB merge, fuzzconfig, HTTP downloads, and API client. Risks include a likely bug in `prepareCorpus` where every URL is written to `corpusFile` rather than `downloadTo`, fatal invalid regex handling in `titleMatchesFilter`, final status defaulting to passed even for no findings, and best-effort artifact upload on size overflow. Tests cover section-hash decoding, skip decisions, and bug-title regex filtering.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/fuzz/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/fuzz/main_test.go -->
## sources/test-tools/syzkaller/syz-cluster/workflow/fuzz/main_test.go

This test file covers pure helper logic in `fuzz-action`. `TestReadSectionHashes` verifies JSON decoding into `build.SectionHashes`. `TestShouldSkipFuzzing` validates empty-symbol behavior, exact equality, ignored volatile Linux data symbols, different hashes, and different symbol counts. `TestBugTitleRe` verifies default empty regexp matches all titles and prefix regexp filtering.

The tests do not execute diff fuzzing, corpus download/merge, artifact compression, or API reporting. They are nevertheless important guards for the skip optimization that determines whether fuzzing is run at all.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/fuzz/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/fuzz/workflow-template.yaml -->
## sources/test-tools/syzkaller/syz-cluster/workflow/fuzz/workflow-template.yaml

This Argo `WorkflowTemplate` runs the fuzz action for up to four hours. It accepts base/patched build IDs, test name, base/patched kernel artifacts mounted at `/base` and `/patched`, and config JSON mounted at `/tmp/config.json`. It invokes `/bin/fuzz-action` with a three-hour fuzzing timeout and verbose logging.

The template requests 24-30 CPUs, about 90-96G memory, privileged `/dev/kvm` access, and a workdir emptyDir. Integration is with `pkg/workflow/template.yaml` fuzz-campaign steps and build outputs containing `symbol_hashes.json`. Risks include high resource needs, privileged KVM access, reliance on `--vv` being accepted by global syzkaller flags, and no declared output artifacts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/fuzz/workflow-template.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/kustomization.yaml -->
## sources/test-tools/syzkaller/syz-cluster/workflow/kustomization.yaml

This kustomization aggregates workflow resources: rebuild-kernels cron workflow, triage/build/boot/fuzz/retest workflow templates. It is the package-level manifest for installing workflow definitions.

State is in Kubernetes/Argo after application. Integration depends on the referenced build workflow template that is outside this subset. Risks include missing RBAC unless `permissions.yaml` is applied elsewhere, and no local image transformation in this kustomization.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/permissions.yaml -->
## sources/test-tools/syzkaller/syz-cluster/workflow/permissions.yaml

This RBAC `Role` named `executor` grants `create` and `patch` on Argo `workflowtaskresults`. It supports Argo executors recording task results.

The file is only a Role, not a RoleBinding, so integration requires binding it to the workflow service account elsewhere. Risks include insufficient permissions if the binding is missing and namespace scoping by whichever namespace applies the role.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/permissions.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/rebuild-kernels-cron.yaml -->
## sources/test-tools/syzkaller/syz-cluster/workflow/rebuild-kernels-cron.yaml

This Argo `CronWorkflow` periodically performs smoke builds of base kernels used by fuzz campaigns. It runs three times daily, replaces concurrent runs, queries `controller-service:8080/trees`, derives all unique kernel configs from fuzz targets, builds a request for every tree/config pair, and invokes the build workflow template with `smoke-build=true`.

State persists in Argo workflow executions and downstream build records/artifacts created by the build action. Integration points are controller `/trees`, build-action template, and tree/fuzz-target API schema. Risks include Python script JSON quoting through Argo parameters, `startingDeadlineSeconds: 0` skipping missed schedules, serial `parallelism: 1`, and hard-coded `amd64`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/rebuild-kernels-cron.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/retest/Dockerfile -->
## sources/test-tools/syzkaller/syz-cluster/workflow/retest/Dockerfile

This Dockerfile packages the retest action. The normal stage installs QEMU, SSH client, curl, compiler tools, and LLVM/Clang 20; smoke-test mode skips heavy dependencies. The final image creates a `syzkaller` user, copies syzkaller binaries plus `/bin/retest-action`, and sets the entrypoint.

Integration is with retest workflow template. Risks mirror fuzz action images: external apt repository dependency, large image, root execution by default, and smoke-test dependency mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/retest/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/retest/main.go -->
## sources/test-tools/syzkaller/syz-cluster/workflow/retest/main.go

`retest-action` reruns previous reproducers/findings against base and patched kernels. Flags specify retest-task JSON, build IDs, session ID, workdir, and test name. It reports running status, builds instance environments, runs a `retest.Runner`, and reports passed or error with cached logs.

`run` reads and decodes `api.RetestTask`, optionally builds a base instance environment when `base_build` is set, always builds a patched environment, completes configs using `fuzzconfig`, and passes both environments plus session/test IDs to `retest.Runner.Run`. Log caching is bounded to 50 KiB/1000 lines.

State persists through `UploadSessionTest` and any downstream retest runner API calls/findings. Integration is with Argo retest template and build artifacts mounted at `/base` and `/patched`. Risks include final status being only passed/error, fatal status reporting on API failure, optional base environment affecting comparison semantics, and no direct tests in this file.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/retest/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/retest/workflow-template.yaml -->
## sources/test-tools/syzkaller/syz-cluster/workflow/retest/workflow-template.yaml

This Argo template runs `retest-action` with optional base kernel, required patched kernel, and a retest task artifact. It passes base/patched build IDs, session ID, test name, and `/workdir`, with a four-hour timeout.

The container uses privileged `/dev/kvm`, an emptyDir workdir, and sizable CPU/memory resources. Integration is with main workflow retest-campaign and triage-generated `api.RetestTask`. Risks include host KVM privilege, optional base artifact handling, and no output artifact/parameter beyond status reported through APIs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/retest/workflow-template.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/triage/Dockerfile -->
## sources/test-tools/syzkaller/syz-cluster/workflow/triage/Dockerfile

This Dockerfile packages `triage-action`. It uses Ubuntu with `git`, creates a fixed UID `syzkaller` user, configures `/workdir` and `/kernel-repo` as safe git directories, copies the action binary, and sets it as entrypoint.

Integration is with triage workflow template, which clones from a kernel repository PVC into `/workdir`. Risks include root/default user interaction despite creating the user, git safe-directory broadening, and package variability from `ubuntu:latest`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/triage/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/triage/main.go -->
## sources/test-tools/syzkaller/syz-cluster/workflow/triage/main.go

`triage-action` decides what tests a session should run. It loads session series/job info from the controller, queries configured trees/fuzz targets, chooses base commits/trees, prepares build/fuzz/retest targets, uploads triage logs/skip reason, and writes a JSON verdict for Argo.

For normal series, `GetVerdict` selects fuzz configs from Cc, merges compatible campaigns, then calls `prepareFuzzingTask` per campaign. Base selection tries author base-commit hint, blob-hash base detection, then configured tree list with last successful builds and patch application. The returned `api.TestTarget` has matching base/patched build requests, patched `SeriesID`, track/fuzz config, and optional retest findings. For job sessions, `prepareJobTask` recreates patched build tasks from the job's finding groups and schedules retest when finding IDs exist.

State persists through controller API calls for triage result and later workflow outputs. Dependencies include git tree ops, triage helper package, debug tracer, and controller API. Integration is central to `pkg/workflow/template.yaml`. Risks include only `amd64` support, skip reason overwritten by later skipped campaigns until at least one target succeeds, base-commit hint branch containment cutoff of 60 days, and real git worktree mutation. Unit tests are mostly in `pkg/triage`; this action lacks direct tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/triage/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/triage/workflow-template.yaml -->
## sources/test-tools/syzkaller/syz-cluster/workflow/triage/workflow-template.yaml

This Argo template runs `triage-action`. An init container clones `/kernel-repo` into `/workdir` using a reference clone and writes a commit graph. The main container runs as UID/GID 10000, reads the cloned repo, writes `/output/result.json`, and exposes it as the `result` output parameter. It retries up to three times with five-minute backoff.

Integration points are the base kernel repo PVC `base-kernel-repo-pv-claim`, workflow `session-id`, and triage-action image. Risks include PVC freshness, git clone cost, privileged-ish filesystem ownership issues handled with `HOME`, and failure if output JSON is not produced. It requires `GIT_DISCOVERY_ACROSS_FILESYSTEM=1` for git behavior across mounts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/workflow/triage/workflow-template.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-hub/http.go -->
## sources/test-tools/syzkaller/syz-hub/http.go

This file implements the syz-hub summary web page. `Hub.httpSummary` locks hub state, aggregates global corpus/repro counts and per-manager counters, sorts managers by name, prepends a total row, and renders an HTML template containing a manager table and cached log textarea.

The UI data types are `UISummaryData` and `UIManager`; `compileTemplate` injects static CSS into the HTML template. State is read under `hub.mu` from `state.State`, including manager HTTP URLs, domains, corpus sizes, add/delete/new counters, and repro counters.

Integration is with `hub.go` HTTP setup and syzkaller log cache. Risks include holding the hub lock while executing the template, minimal escaping relying on `html/template`, and total row not filling all fields in the same semantic way as managers. There are no direct tests for the HTML.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-hub/http.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-hub/hub.go -->
## sources/test-tools/syzkaller/syz-hub/hub.go

`syz-hub` is an RPC/HTTP process that exchanges corpus programs and reproducers among syz-manager clients. `Config` defines HTTP/RPC/workdir and authorized clients. `Hub` holds a mutex, persistent `state.State`, client keys, and an auth endpoint.

`main` loads config, enables log caching, loads state, builds the client-key map, serves HTTP summary, starts hourly old-manager purging, and serves RPC as `Hub`. `Connect` authenticates manager identity then records manager metadata, supported calls, and initial corpus. `Sync` authenticates, applies added/deleted corpus entries, returns pending inputs, records incoming repros, and optionally returns a pending repro. Authentication supports static keys and OAuth magic expected subjects, and manager names must be empty or prefixed by client name.

State persists through `syz-hub/state`. Integration points are syz-manager `HubConnector`, HTTP dashboard, auth package, and rpctype RPC. Risks include one global mutex around potentially heavy state operations, generic "unauthorized manager" errors for all auth failures, and reliance on clients periodically reconnecting/purging. Tests cover static-key manager authentication.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-hub/hub.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-hub/hub_test.go -->
## sources/test-tools/syzkaller/syz-hub/hub_test.go

`TestAuth` validates `Hub.checkManager` for static keys. It covers missing client/key, wrong key, wrong client's key, exact manager name, prefixed manager name, empty manager defaulting to client, and manager names without the client prefix.

This is a focused auth test. It does not cover OAuth-token keys, RPC `Connect`/`Sync`, state persistence, or HTTP behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-hub/hub_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-hub/state/state.go -->
## sources/test-tools/syzkaller/syz-hub/state/state.go

This file implements syz-hub's persistent state engine. `State` owns global corpus/repro DBs, sequence counters, workdir, and managers. `Manager` stores per-manager corpus, domain, supported calls, sequence files, repro ownership, connection time, and counters.

`Make` creates directories, loads/validates global DBs, recreates managers from disk, purges stale managers, and prunes unused corpus. `Connect` creates/updates a manager, writes domain and sequence files, rebuilds the manager corpus DB from the supplied corpus, stores supported calls, and repurges global corpus. `Sync` applies deletes/adds, computes pending inputs by sequence and call compatibility, updates counters, and advances sequence files. `AddRepro` validates and deduplicates repro programs, tracks ownership, increments global repro sequence, and persists to repro DB. `PendingRepro` sends the earliest compatible repro not owned by the requester and advances repro sequence. `PurgeOldManagers` renames inactive manager dirs to `.purged` after 30 days and trims global corpus.

Persistence is file-backed: `corpus.db`, `repro.db`, per-manager `corpus.db`, `seq`, `repro.seq`, and `domain`. Dependencies include syzkaller DB/hash/prog parsing and filesystem helpers. Integration is with syz-hub RPC and manager hub connector. Risks include `log.Fatal` inside state loading helpers, returning internal maps/data structures by reference via callers, corpus distribution caps and sequence rounding affecting catch-up, and purging based on seq-file mtime. Tests cover basic connection, repro exchange/persistence, and domain tagging.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-hub/state/state.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-hub/state/state_test.go -->
## sources/test-tools/syzkaller/syz-hub/state/state_test.go

This file tests syz-hub state persistence and exchange semantics. `TestBasic` ensures unconnected managers cannot sync and a connected manager can sync. `TestRepro` validates repro delivery only to compatible managers that did not originate the repro, duplicate handling, call-set filtering, and persistence after reload. `TestDomain` validates domain-tag propagation for shared corpus inputs across managers and after reload.

Helpers create temp-backed states, connect managers, sync sorted outputs, add repros, and reload state. Coverage is strong for core state behavior but does not test stale-manager purge, large pending-input caps, invalid corpus cleanup, or concurrent hub access.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-hub/state/state_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-kfuzztest/main.go -->
## sources/test-tools/syzkaller/syz-kfuzztest/main.go

`syz-kfuzztest` is a Linux-only CLI wrapper for the KFuzzTest manager. It accepts flags for `vmlinux`, cooldown, thread count, and display interval, plus optional enabled target names. It builds `kfuzztest-manager.Config`, installs interrupt handling, constructs a manager, and runs it.

State is managed by the KFuzzTest manager; this file only owns process-level context cancellation. Dependencies are `pkg/kfuzztest-manager`, `osutil.HandleInterrupts`, and standard flag parsing. Risks include panic on manager creation error instead of formatted fatal logging and Linux-only build constraints limiting availability. There are no direct tests here.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-kfuzztest/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-manager/hub.go -->
## sources/test-tools/syzkaller/syz-manager/hub.go

This file implements syz-manager's client-side connector to syz-hub. It handles auth-key retrieval, initial connect with corpus and supported calls, periodic sync, processing incoming programs/repros, and domain-based candidate flags.

`pickGetter` returns a static key getter or OAuth token-cache getter. `hubSyncLoop` constructs a `HubConnector` with manager view methods, enabled calls, domain, leak mode, fresh state, repro queue, and stats. `HubConnector.loop` connects, syncs when candidate triage is ready, marks hub unreachable after early repeated failures, and reconnects every 30 hours to resend corpus. `connect` caps initial corpus at 100k programs and uses a transient RPC connection for the large request. `sync` sends queued repros, processes all batches until no inputs/more remain, updates stats, and clears sent repros. Incoming programs are parsed, disabled-call filtered, and flagged minimized/smashed based on domain matching. Incoming repros become external reproduction crashes.

State is mostly in-memory, with manager corpus/repro queues backing inputs. Integration points are syz-hub RPC, manager phase machine, dashboard errors, fuzzer candidate queue, and repro loop. Risks include nil `hubReproQueue` if reproduction is disabled but repros arrive, relying on manager readiness before sync, large initial connect payloads despite cap, and domain parsing subtleties. Tests cover `matchDomains` only.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-manager/hub.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-manager/hub_test.go -->
## sources/test-tools/syzkaller/syz-manager/hub_test.go

`TestMatchDomains` exercises syz-manager hub domain matching. It covers empty domains, OS-only domains, malformed/trailing slash domains, same/different first-level domains, and differing second-level fuzzing dimensions. Expected booleans control whether received programs are treated as minimized and/or smashed.

The test guards an important heuristic for cross-manager corpus handling. It does not cover RPC connection, auth, program parsing, repro queueing, or stats.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-manager/hub_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-manager/manager.go -->
## sources/test-tools/syzkaller/syz-manager/manager.go

`manager.go` is the main syz-manager process and lifecycle coordinator. It defines `Manager`, operation `Mode`s, process `main`, `RunManager`, VM/fuzzer/repro loops, crash handling, corpus management, dashboard/hub integration, and helper APIs required by rpcserver/fuzzer/repro components.

Startup loads config, validates mode, optionally disables dashboard/hub, activates KFuzzTest targets, creates VM pool, reporter, crash store, HTTP server, stats, corpus preload, RPC server, dashboard client, asset storage, benchmark output, and VM dispatcher. `MachineChecked` is the core state transition after the first fuzzer VM reports features and enabled syscalls: it filters/preloads corpus, records enabled syscalls, creates the fuzzer/corpus for fuzzing modes, starts minimization/fuzzer/dashboard loops, switches to snapshot mode if configured, or returns alternate queue sources for corpus-run, run-tests, and iface-probe modes. The phase machine advances from initial load through corpus triage, hub query, and hub triage; reproduction starts after hub triage.

Persistent state includes workdir corpus DB, crash store contents, repro artifacts, dashboard uploads, optional benchmark file, asset storage, and memory dumps. Important control flows include `processFuzzingResults`, VM instance startup/shutdown, `saveCrash`, `NeedRepro`, `RunRepro`, `saveFailedRepro`, `saveRepro`, corpus DB updates/minimization, dashboard stats/repro task polling, and used-file modification tracking. Dependencies span most syzkaller subsystems: VM, rpcserver, fuzzer/queue/corpus, dashboard, repro, report, asset/image/fsck, hub, stats, and target/prog metadata.

Risks are inherent to high concurrency and external state: many goroutines coordinate through manager mutexes/channels/atomics, fatal exits guard file mutation and invalid modes, dashboard failures are often logged and skipped, corpus minimization mutates persistent DBs, and crash/repro behavior changes by mode, dashboard availability, leak features, and phase. Test coverage for this file is mostly integration/system-level elsewhere; direct unit coverage is limited for helpers in companion files.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-manager/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-manager/snapshot.go -->
## sources/test-tools/syzkaller/syz-manager/snapshot.go

This file implements syz-manager snapshot execution mode. `snapshotInstance` marks a VM as fuzzing and calls `snapshotLoop`. `snapshotLoop` copies the executor, starts it in snapshot mode with logs to `/dev/kmsg`, then repeatedly pulls requests from a distributed source, performs one-time snapshot setup, runs requests against the VM snapshot, detects crashes, and completes queue requests.

`snapshotSetup` sends a flatbuffer handshake with coverage, pointer-size, slowdown, timeout, feature, env flag, and sandbox data. `snapshotRun` serializes a program, sends a flatbuffer request, parses executor output, normalizes call info length by filling errno 999 for missing calls, merges extra coverage/signal arrays, and returns a `queue.Result`. `parseExecResult` handles short buffers, flatbuffer parse errors, and wrong message types as execution errors rather than infrastructure panics.

State is in VM snapshot machinery, manager stats, crash channel, and queue result callbacks. Integration points are `MachineChecked` snapshot branch, flatrpc executor protocol, VM `RunSnapshot`, and fuzzer queue. Risks include panicking if env flags change, continuing after corrupted executor result as program failure, and needing executor/VM support for snapshot mode. No direct tests were observed.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-manager/snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-manager/stats.go -->
## sources/test-tools/syzkaller/syz-manager/stats.go

`stats.go` defines manager runtime stats and `initStats`. It creates counters/gauges for crashes, crash types, suppressed reports, fuzzing time, uptime, average VM restart time, Go heap/VM memory, uncompressed image memory/count, and filtered coverage.

Most stats are backed by `stat.Val` and some use functions to read atomics/runtime memory/pool boot time on demand. Prometheus export is configured for total crashes. These stats feed logs, HTTP status, and dashboard upload deltas from `dashboardReporter`.

State is in the stat registry and manager fields. Risks include stats depending on `mgr.pool` for boot time after pool initialization, unit formatting inconsistencies, and global stat registry side effects in tests. There are no direct tests here.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-manager/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-verifier/main.go -->
## sources/test-tools/syzkaller/syz-verifier/main.go

This file is the entrypoint and setup path for `syz-verifier`, a tool that compares execution behavior across multiple kernel configs. `Setup` creates a `Kernel` context with reporter, rpcserver, VM pool, dispatcher, enabled-syscall channel, feature channel, and crash channel. `main` loads at least two configs unless debug mode, ensures shared workdir, creates one plain queue per kernel, and starts `Verifier.RunVerifierFuzzer`.

The setup forces `cfg.Experimental.ResetAccState = true` so executor state resets between program executions. It uses the first config's workdir/target as verifier-wide state, and each kernel gets an ID/source queue. Dependencies include mgrconfig, rpcserver, report, VM dispatcher, queue, logging, and shutdown context.

State persists mainly through workdir corpus/crash store used by verifier internals. Integration is with `verifier.go` and syzkaller VM/rpc runner protocol. Risks include requiring same workdir, mutating config experimental fields, allowing single-kernel debug mode, and fatal exits for setup errors. There are no direct tests in this file.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-verifier/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-verifier/verifier.go -->
## sources/test-tools/syzkaller/syz-verifier/verifier.go

`verifier.go` implements the corpus-exercising verifier that runs the same programs across multiple kernels and reports errno mismatches. `Verifier` owns shared config/target, kernels, per-kernel queue sources, optional HTTP server, crash store, first-connect timestamp, and preloaded programs. `Kernel` wraps one kernel config, rpcserver, VM dispatcher, reporter, channels for machine-check data, and queue source.

`RunVerifierFuzzer` builds a pool map for HTTP, initializes crash store/HTTP server, preloads corpus, and starts `Loop`. `Loop` serves HTTP, starts each kernel loop, and runs `verifierLoop`. The verifier waits for every kernel to report enabled syscalls/features, intersects enabled calls transitively, records stats, then for each preloaded corpus program creates cloned `queue.Request`s for every kernel, submits them, waits for all results, and calls `compareResults`. Mismatches ignore executor-not-completed errno 999, generate a detailed report with the full program and per-kernel errno/flags/output, log it, and save it to crash store.

Kernel-side flow starts rpcserver listening, dispatches VMs, forwards RPC ports, copies executor, runs `executor runner`, reports enabled syscalls/features in `MachineChecked`, and returns queue sources with default execution options. Coverage/signal/bug-frame APIs are mostly no-ops because verifier exercises existing corpus rather than discovering new coverage.

State is local queue/result state plus crash-store mismatch reports. Dependencies include fuzzer queues, rpcserver, VM dispatcher, flatrpc, report/crash store, manager HTTP server, stats, and corpus seed loading. Risks include waiting indefinitely for all kernels to become ready, comparing responses by kernel ID index assumptions, only comparing errno not deeper side effects, and continuing past nil/missing result info. No direct tests were observed.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-verifier/verifier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/android/Makefile -->
## sources/test-tools/syzkaller/tools/android/Makefile

This Makefile builds and runs the Android sandbox test helper. Target `libs/arm64-v8a/sandbox_test` depends on `jni/sandbox_test.c` and invokes `ndk-build`. `push` uploads the built binary to `/data/local/tmp`, `run` pushes then executes it through adb, and `clean` removes NDK output directories.

State is local build artifacts plus device-side copied binary. Integration is with Android NDK, adb, and the JNI makefiles. Risks include assuming arm64 ABI, adb device availability, and not declaring `clean` in `.PHONY` despite declaring `all push run`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/android/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/android/jni/Android.mk -->
## sources/test-tools/syzkaller/tools/android/jni/Android.mk

This Android NDK makefile defines the `sandbox_test` executable module from `sandbox_test.c` and includes headers from `../../`, which lets it include syzkaller executor common code.

It integrates with the parent Android Makefile and NDK build system. Risks are minimal: include-path drift and reliance on NDK executable build support for the selected ABI.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/android/jni/Android.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/android/jni/Application.mk -->
## sources/test-tools/syzkaller/tools/android/jni/Application.mk

This NDK application makefile selects `APP_ABI := arm64-v8a` and `APP_PLATFORM := latest`. It also includes `CLEAR_VARS`, though that is more typical in `Android.mk`.

Integration is with `ndk-build` for the Android sandbox test. Risks include only building arm64 and using `latest`, which may differ across installed NDK versions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/android/jni/Application.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/android/jni/sandbox_test.c -->
## sources/test-tools/syzkaller/tools/android/jni/sandbox_test.c

This C helper tests syzkaller's Android untrusted-app sandbox setup. It defines executor configuration macros, simple `fail/error/debug` logging macros, `doexit`, a `loop` function that runs `id`, a temp-directory setup, includes `executor/common_linux.h`, and calls `do_sandbox_android_untrusted_app()` from `main`.

Runtime flow creates a writable temporary directory under `/data/data/syzkaller` for untrusted-app mode, chmods/chdirs into it, then enters the executor sandbox helper. Dependencies are Android libc/syscalls, syzkaller executor common code, and the expected `/data/data/syzkaller` location. Risks include permission assumptions on device, `chmod 0777`, and no explicit return after sandbox call. It is built/run by the Android Makefile rather than unit-tested.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/android/jni/sandbox_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/arm64/registers.go -->
## sources/test-tools/syzkaller/tools/arm64/registers.go

This generator converts ARM64 system-register tables into syzkaller KVM register ID descriptions for `dev_kvm.txt`. `main` reads an input table file, prints generated header/footer, system register IDs, and extra core register IDs.

`printSysRegIDs` skips comments/blank lines, expands wildcard lines, processes each line, and emits comma-separated hex IDs. `processLine` parses five binary operands, treating `-` as zero, and calls `arm64KVMRegID`. `expandLine` recursively expands `n[...]` bit wildcards into all permutations. `arm64KVMRegID` combines operands with constants from Linux KVM ARM64 UAPI. `printCoreRegs` emits hard-coded extra IDs observed from QEMU/KVM.

State is stdout-only generation. Dependencies include regexp/string parsing and syzkaller `tool.Failf`. Integration is manual code generation for syzkaller descriptions. Risks include parsing assumptions about table format, recursive expansion size, hard-coded Linux v6.10.2 constants/extra registers, and emitting parse errors into stdout alongside generated data. No tests were observed.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/arm64/registers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-commits.sh -->
## sources/test-tools/syzkaller/tools/check-commits.sh

This CI/local helper validates commit subject format and body line length. It determines the commit range from `GITHUB_PR_HEAD_SHA` and `GITHUB_PR_COMMITS`, or falls back to `master..HEAD`, or one commit if no range is found. It checks each commit subject against syzkaller's `subsystem/path: lowercase description without trailing period` style or revert format, and rejects non-dependabot commit bodies with lines over 120 characters.

State is read from git history and environment variables; output uses GitHub Actions `##[error]` annotations. Dependencies are bash, git, regex matching, and `wc`. Risks include backtick command substitution style, assumptions about `master`, subject regex strictness, and body long-line regex behavior. There are no direct tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check-commits.sh -->
