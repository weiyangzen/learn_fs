# subset-b-009514 research

Grouped research for syz-cluster dashboard, email reporter, kernel-disk workflows, smoke test, and Kubernetes overlays. Each section is source-tree-aligned and intended for deterministic split into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/dashboard/handler.go -->
# sources/test-tools/syzkaller/syz-cluster/dashboard/handler.go

## Purpose
Implements the web dashboard HTTP surface for syz-cluster. It renders series, sessions, tests, findings, builds, statistics, and raw artifacts/logs from Spanner-backed repositories and blob storage using embedded Go templates and embedded static assets.

## Important APIs, types, and functions
`dashboardHandler` is the central dependency container. It owns repositories for builds, series, sessions, session tests, test steps, findings, stats, and jobs, plus `blob.Storage` and parsed templates. `newHandler` wires the handler from `app.AppEnvironment`, parses `base.html`, common templates, and per-page templates. `Mux` registers all routes and serves embedded `/static/` assets. `seriesList`, `seriesInfo`, `sessionInfo`, and `statsPage` render HTML pages. `sessionLog`, `sessionTriageLog`, `sessionTestLog`, `sessionTestStepLog`, `sessionTestArtifacts`, `patchContent`, `jobPatchContent`, `allPatches`, `findingInfo`, and `buildInfo` expose raw blob-backed content. Helper functions include `getOffset`, `fetchSessionData`, `populateSeriesMetadata`, `groupFindings`, `makeMonthlyStats`, `renderTemplate`, `streamBlob`, and `errToStatus`.

## Control flow
Requests enter the `http.ServeMux`; route parameters are read with Go's `PathValue`. Page handlers query repositories, construct UI-specific structs, and call `renderTemplate`. `seriesList` builds a `db.SeriesFilter` from query parameters, applies a fixed page size of 100, and constructs prev/next URLs through `urlutil`. `seriesInfo` fetches the series, patches, versions, then all sessions and per-session test/finding/step metadata; job-backed sessions are collapsed by default and sessions are sorted to put non-job sessions first, then newest sessions. `sessionInfo` renders the same series template but for one session. `statsPage` collects weekly/monthly metrics from `StatsRepository` and computes totals. Raw content handlers resolve one database entity and stream the referenced blob URI to the response.

## State and persistence behavior
The file does not persist state directly. It reads all durable state from Cloud Spanner through `pkg/db` repositories and reads immutable or generated artifacts from configured `blob.Storage`. It also exposes a download content disposition for test artifact archives. Empty blob URIs are silently treated as empty responses, which is useful for optional artifacts but can hide missing data.

## Dependencies and integration points
Depends on `pkg/app` for environment/config, `pkg/db` for query contracts, `pkg/blob` for artifact reads, `pkg/service` for job links, and `pkg/html/urlutil` for query parameter rewriting. It integrates with dashboard templates under `dashboard/templates`, static assets under `dashboard/static`, Kubernetes service/deployment wiring, and API URL generation tested elsewhere through `pkg/api`.

## Risks and edge cases
Template execution writes directly to the response; if a template fails after partial output, `errToStatus` may append a 500 body after bytes have already been sent. `allPatches` concatenates patch blobs without separators beyond the stored bodies. `findingInfo` reads syz repro options and repro bodies fully into memory before writing. `getOffset` rejects negative and non-integer offsets, but page-next logic only checks whether the current page is full, not whether a next page exists. Raw blob handlers set limited content metadata, and most raw outputs rely on default content type.

## Test signals
Covered by `handler_test.go` for major generated URLs and all-patches concatenation, and by `local_ui_test.go` for manual browser-oriented data population. The tests exercise repository/blob integration using `app.TestEnvironment`, fake controller uploads, reporter-generated reports, and actual HTTP requests against an `httptest.Server`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/dashboard/handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/dashboard/handler_test.go -->
# sources/test-tools/syzkaller/syz-cluster/dashboard/handler_test.go

## Purpose
Provides integration-style tests for dashboard URL reachability and patch aggregation behavior.

## Important APIs, types, and functions
`TestURLs` creates an app test environment, starts a controller test server, uploads dummy series with findings, starts the dashboard test server, builds URLs with `api.URLGenerator`, and asserts HTTP 200 responses. `TestAllPatches` uploads a two-patch series and verifies `/series/{id}/all_patches` returns bodies in order. `testServer` constructs `dashboardHandler` and wraps it in `httptest.NewServer`.

## Control flow
The tests populate Spanner/blob state through controller helpers, then exercise the public HTTP handler surface over real HTTP. The URL set includes root, stats, series, session, build logs/configs, and finding logs/repros. Responses are read fully so failures can include response bodies.

## State and persistence behavior
State is isolated in `app.TestEnvironment`; data is persisted through the same repositories and blob storage used in production paths. The test server is closed via `t.Cleanup`.

## Dependencies and integration points
Depends on `pkg/app`, `pkg/controller`, `pkg/api`, and `pkg/db`. It validates integration between dashboard routes, URL generation, controller upload helpers, reporter/finding storage, and blob-backed content retrieval.

## Risks and edge cases
`TestURLs` calls `io.ReadAll(resp.Body)` before checking `err`; if `http.Get` failed, `resp` would be nil. In normal local test conditions the server URL is valid, so this is low risk but brittle. The tests assert successful responses, not rendered HTML details or content types.

## Test signals
Strong signal that core dashboard routes do not panic or return non-200 for representative populated data. `TestAllPatches` specifically guards ordering and concatenation semantics for patch blobs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/dashboard/handler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/dashboard/kustomization.yaml -->
# sources/test-tools/syzkaller/syz-cluster/dashboard/kustomization.yaml

## Purpose
Defines the base Kustomize resources for the dashboard component.

## Important APIs, types, and functions
Kustomize `resources` includes `deployment.yaml` and `service.yaml` from the same directory.

## Control flow
When an overlay references `../../dashboard`, this file pulls both dashboard workload and service into the rendered manifest set.

## State and persistence behavior
No runtime state is defined here; the deployment and service files define pod behavior and networking.

## Dependencies and integration points
Integrated by `overlays/common/kustomization.yaml`, which composes controller, dashboard, series tracker, kernel disk, reporter server, workflow, and network policies.

## Risks and edge cases
Any missing resource filename breaks Kustomize rendering. The file intentionally keeps the base minimal and leaves environment-specific patching to overlays.

## Test signals
Exercised indirectly by `local_cluster_test.sh`, which applies the test overlay and verifies the web dashboard service responds.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/dashboard/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/dashboard/local_ui_test.go -->
# sources/test-tools/syzkaller/syz-cluster/dashboard/local_ui_test.go

## Purpose
Provides an opt-in manual UI fixture for running the dashboard locally with realistic test data.

## Important APIs, types, and functions
Defines flags `-local-ui` and `-local-ui-addr`. `TestLocalUI` skips unless explicitly enabled, requires verbose mode and no test timeout, populates the database, starts a TCP listener, and serves `handler.Mux()`. `populateData` uploads a dummy series, triage log, build, session tests, findings, grouped test steps, reports, moderation/upstream transitions, and a patch-test job.

## Control flow
The test builds an in-process test environment and controller server, uses controller/client APIs to create dashboard data, runs reporter generation and confirmation paths so stats and reports appear, submits a job, then blocks in `http.Serve` for browser inspection.

## State and persistence behavior
All state is created in the test Spanner/blob environment. Blob storage stores the fake triage log and uploaded logs/artifacts through controller APIs. The session is explicitly marked finished so generated reports and stats can be visible.

## Dependencies and integration points
Depends on controller upload helpers, reporter generation/server helpers, dashboard handler construction, `pkg/db` repository updates, and `pkg/api` types. It integrates the dashboard with almost the full local syz-cluster data flow.

## Risks and edge cases
This is intentionally not a normal automated test. It fails if run with a timeout or without `-v`, then blocks forever until killed. It binds a configurable local address and can conflict with an existing process. Because the data is synthetic, it is useful for UI coverage but not for production-scale performance.

## Test signals
High manual signal for visual dashboard behavior across series, findings, logs, test steps, reports, and jobs. It is skipped in default test runs, so automated CI signal comes from other tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/dashboard/local_ui_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/dashboard/main.go -->
# sources/test-tools/syzkaller/syz-cluster/dashboard/main.go

## Purpose
Entry point for the dashboard binary.

## Important APIs, types, and functions
`main` creates a background context, loads an application environment with `app.Environment(ctx)`, constructs `newHandler`, creates an `http.Server` at address `:8081`, and serves the handler mux. Fatal initialization and serve errors go through `app.Fatalf`.

## Control flow
Startup is linear: environment, handler, server, listen. There is no graceful shutdown hook in this file; process termination is expected to be managed by the runtime environment.

## State and persistence behavior
No direct persistence. Runtime state is acquired from the app environment, including config, Spanner, and blob storage.

## Dependencies and integration points
Integrates with Kubernetes deployment/service expecting container port 8081 and `web-dashboard-service` mapping to port 80. Depends on the same handler/template/static files researched above.

## Risks and edge cases
Server uses `ListenAndServe` without explicit read/write timeouts. Any environment initialization failure terminates the process. The bind address is hard-coded.

## Test signals
Exercised indirectly by local cluster smoke deployment and handler tests; the `main` function itself has no direct unit test.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/dashboard/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/dashboard/service.yaml -->
# sources/test-tools/syzkaller/syz-cluster/dashboard/service.yaml

## Purpose
Exposes the dashboard deployment inside the Kubernetes cluster.

## Important APIs, types, and functions
Defines a `v1` `Service` named `web-dashboard-service` selecting pods labeled `app: web-dashboard`. It exposes service port `80` to target port `8081`.

## Control flow
Traffic to the service on port 80 is forwarded by Kubernetes to dashboard pods on port 8081, matching `main.go`.

## State and persistence behavior
No persistence. The service tracks matching endpoints dynamically through pod labels.

## Dependencies and integration points
Consumed by common and GKE overlays. The GKE common overlay patches metadata annotations for a Google Cloud NEG on exposed port 80. `local_cluster_test.sh` port-forwards this service and expects HTTP 200 from `/`.

## Risks and edge cases
Selector/label drift between deployment and service would break routing. Network policies must allow ingress to the selected pods on the effective target port.

## Test signals
The smoke test validates service reachability through `kubectl port-forward svc/web-dashboard-service 8080:80` and a curl check.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/dashboard/service.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/dashboard/static/bootstrap.bundle.min.js -->
# sources/test-tools/syzkaller/syz-cluster/dashboard/static/bootstrap.bundle.min.js

## Purpose
Vendored minified Bootstrap JavaScript bundle used by dashboard templates for client-side UI components.

## Important APIs, types, and functions
The header identifies Bootstrap v5.3.3, MIT licensed. The bundle exposes Bootstrap component constructors such as Alert, Button, Carousel, Collapse, Dropdown, Modal, Offcanvas, Popover, ScrollSpy, Tab, Toast, and Tooltip through UMD/global integration.

## Control flow
Loaded by browser pages as a static asset served from the embedded dashboard filesystem. Bootstrap registers data API event handlers, jQuery plugin bridges when jQuery is present, and component-specific DOM event listeners.

## State and persistence behavior
No server persistence. Browser-side component instances are stored in internal maps associated with DOM elements for the page lifetime.

## Dependencies and integration points
Integrated through dashboard static serving and templates. It includes Popper-related behavior because it is the Bootstrap bundle variant. It can interoperate with the vendored jQuery file but does not require it for core Bootstrap data APIs.

## Risks and edge cases
As a minified third-party asset, local review is version/header oriented rather than line-by-line semantic review. Security fixes require explicit asset updates. The source map comment references `bootstrap.bundle.min.js.map`; if the map is absent, browser devtools may report a missing source map but runtime behavior is unaffected.

## Test signals
No repository unit tests cover this asset directly. Dashboard handler tests only verify that routes render successfully; manual `TestLocalUI` can expose client-side regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/dashboard/static/bootstrap.bundle.min.js -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/dashboard/static/jquery-3.7.1.min.js -->
# sources/test-tools/syzkaller/syz-cluster/dashboard/static/jquery-3.7.1.min.js

## Purpose
Vendored minified jQuery library used by dashboard static/template code.

## Important APIs, types, and functions
The header identifies jQuery v3.7.1, OpenJS Foundation license. The bundle provides the standard `jQuery`/`$` API: selectors, traversal, event helpers, AJAX helpers, effects-related helpers, DOM manipulation, and `noConflict`.

## Control flow
Loaded by browser pages from the embedded static filesystem. It initializes in UMD style, attaches to `window.jQuery` and `window.$` in browser mode, and provides plugin integration points used by Bootstrap when available.

## State and persistence behavior
No server persistence. Client-side state is limited to jQuery's in-memory data/event caches and DOM manipulation during the page lifetime.

## Dependencies and integration points
Served by `dashboardHandler.Mux` under `/static/`. It is a shared browser dependency for dashboard UI scripts/templates.

## Risks and edge cases
Minified third-party code is difficult to audit locally; version management and vulnerability tracking are the main maintenance concerns. If templates do not load it before scripts expecting `$`, client-side behavior can fail even while server routes return 200.

## Test signals
No direct automated tests. Manual UI mode is the main signal for browser-side regressions involving jQuery-dependent behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/dashboard/static/jquery-3.7.1.min.js -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/email-reporter/Dockerfile -->
# sources/test-tools/syzkaller/syz-cluster/email-reporter/Dockerfile

## Purpose
Builds the email-reporter runtime container from a prebuilt syz-cluster builder image.

## Important APIs, types, and functions
Uses Dockerfile syntax 1.7 labs. Build args `IMAGE_PREFIX` and `IMAGE_TAG` select `${IMAGE_PREFIX}syz-cluster-build:${IMAGE_TAG}` as the builder. Runtime image is `alpine:latest`, installs `git`, copies `/build/syz-cluster/bin/email-reporter` to `/bin/email-reporter`, and sets that binary as entrypoint.

## Control flow
The binary is expected to be produced in the builder image. At runtime the container starts the email reporter directly. `git` is installed because Lore polling clones/fetches an archive repository.

## State and persistence behavior
The container itself is stateless; persistent Lore checkout state is mounted by Kubernetes at `/lore-repo`.

## Dependencies and integration points
Integrates with the build system's `syz-cluster-build` image, `email-reporter/deployment.yaml`, and `MakeLorePoller`, which uses `/lore-repo/checkout`.

## Risks and edge cases
`alpine:latest` is floating, so rebuilds may change runtime contents. The image relies on the builder path and binary name remaining stable. Missing `git` would break Lore polling.

## Test signals
Container behavior is indirectly covered by local cluster smoke tests and Go tests for the binary logic, but this Dockerfile has no direct build test in the assigned files.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/email-reporter/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/email-reporter/deployment.yaml -->
# sources/test-tools/syzkaller/syz-cluster/email-reporter/deployment.yaml

## Purpose
Defines the Kubernetes deployment for the email reporter service.

## Important APIs, types, and functions
Creates an `apps/v1` `Deployment` named `email-reporter` with one replica and pods labeled `app: email-reporter`. It uses service account `gke-email-reporter-ksa`, image `${IMAGE_PREFIX}email-reporter:${IMAGE_TAG}`, config volume from `global-config`, and PVC `reporter-lore-disk-claim` mounted at `/lore-repo`. Resource requests are 2 CPU/8G and limits are 4 CPU/16G.

## Control flow
Kubernetes maintains exactly one replica, matching the application comment that only one copy should run at the same time. The pod reads config from `/config` and persists the Lore checkout under `/lore-repo`.

## State and persistence behavior
Durable state is external: Spanner/report APIs for report state and the PVC for Lore repository checkout. The deployment itself does not define probes.

## Dependencies and integration points
Depends on `global-config`, `reporter-lore-disk-claim`, and the GKE service account expected from Terraform. Network policies allow it to contact controller, reporter-server, and the internet/email/git paths.

## Risks and edge cases
The deployment is annotated to ignore kube-linter's non-existent service account warning because Terraform owns the account. Running more than one replica risks duplicate polling/sending despite report confirmation safeguards. Lack of probes means Kubernetes only sees process liveness.

## Test signals
Go tests cover report and incoming email flow. Local or cluster deployment tests would be needed to catch volume/config/service-account regressions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/email-reporter/deployment.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/email-reporter/email_workflow_test.go -->
# sources/test-tools/syzkaller/syz-cluster/email-reporter/email_workflow_test.go

## Purpose
Tests Lore poller integration with reporter reply recording and incoming email processing.

## Important APIs, types, and functions
`TestPollerIntegration` uses `setupHandlerTest`, `lore.NewTestLoreArchive`, `MakeLorePoller`, reporter `RecordReply`, and `Handler.ProcessPolledEmail`. It covers direct replies, own-email ignoring, indirect replies through root message IDs, report identification via email context, unrelated messages, and empty bug ID handling.

## Control flow
The test first sends and confirms a report, records the outgoing message ID, writes synthetic messages to a test Lore archive, polls them, then passes `PolledEmail` instances to the handler. It verifies idempotency by attempting to record the same reply again.

## State and persistence behavior
Uses the test environment's reporter storage for report/reply state and a temporary git-backed Lore archive. The poller state is local to temporary directories.

## Dependencies and integration points
Connects `pkg/email/lore` parsing/polling, syz-cluster reporter APIs, email config context prefix handling, and email reporter command handling. It validates the same path the production `main.go` uses when `LoreArchiveURL` is set.

## Risks and edge cases
The test is synthetic and does not exercise network fetching from real lore.kernel.org. It does cover subtle reply threading and bot-own-email filtering, which are high-value correctness points for avoiding loops and duplicate command processing.

## Test signals
Strong integration signal for incoming email idempotency, root message correlation, context-derived report IDs, and ignored unknown or own messages.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/email-reporter/email_workflow_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/email-reporter/handler.go -->
# sources/test-tools/syzkaller/syz-cluster/email-reporter/handler.go

## Purpose
Implements email reporter business logic: polling pending reports, sending moderation/upstream emails, recording outgoing replies, and processing incoming `#syz` commands from email or Lore.

## Important APIs, types, and functions
`Handler` owns reporter identity, `api.ReporterClient`, controller `api.Client`, email configuration, and an `emailclient.Sender`. Sentinel errors are `ErrOwnEmail` and `ErrUnknownReport`. `PollReportsLoop` repeatedly calls `PollAndReport`. `PollAndReport` fetches the next report and calls `report`. `report` confirms the report before sending, renders email body via `pkg/report`, sends through the configured sender, and records the sent message ID when available. `IncomingEmail` interprets supported commands. `ProcessPolledEmail` records a polled reply for idempotency and delegates to `IncomingEmail`. `stripContextPrefix` normalizes dashapi context-prefixed bug IDs.

## Control flow
Outgoing flow starts with `GetNextReport`; if a report exists, `ConfirmReport` is called before rendering/sending to reduce duplicate-send risk. Moderation reports go to the moderation list with archive CC and a moderation subject prefix. Non-moderation reports are sent to report CCs, include archive/report CC, optionally include configured CI name in the subject, and preserve `InReplyTo`. Incoming flow rejects emails without bug IDs and ignores own non-forwarded emails. Supported commands are upstream, invalid, and argument-free `#syz test` with an attached patch; unsupported commands produce a reply explaining non-support. Processing polled email first calls `RecordReply`; unknown or already-seen replies are stopped before command execution.

## State and persistence behavior
Report confirmation, upstreaming, invalidation, job submission, and reply recording are persisted through reporter/controller APIs. The handler itself is stateless except for injected clients/config. The outgoing sender may or may not return a message ID; only non-empty IDs are recorded.

## Dependencies and integration points
Depends on `pkg/email`, `pkg/email/lore`, `pkg/email/sender`, `pkg/api`, `pkg/app`, `pkg/emailclient`, and `pkg/report`. Integrates with reporter server for report lifecycle, controller for patch-test job submission, dashapi/SMTP sender configuration, and Lore poller reply threading.

## Risks and edge cases
Confirm-before-send avoids duplicate emails but can drop a report if rendering or sending fails after confirmation. The TODO explicitly notes retry ambiguity when send errors may still have delivered mail. `IncomingEmail` processes commands sequentially and keeps only one reply string, so multiple commands can overwrite earlier unsupported-command replies. `#syz test` with args is rejected and patchless tests reply to the author. Only the first bug ID is used. Own forwarded emails are allowed to support dashboard forwarding.

## Test signals
`handler_test.go` covers moderation/upstream flow, invalidation, unsupported commands, own-email filtering, forwarded own email, and `#syz test` job flow/error cases. `email_workflow_test.go` covers Lore idempotency and reply identification.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/email-reporter/handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/email-reporter/handler_test.go -->
# sources/test-tools/syzkaller/syz-cluster/email-reporter/handler_test.go

## Purpose
Unit/integration tests for outgoing report emails and incoming command handling.

## Important APIs, types, and functions
Tests include `TestModerationReportFlow`, `TestReportInvalidationFlow`, `TestInvalidReply`, and `TestSyzTestFlow`. `setupHandlerTest` creates a test environment, controller server, dummy series/findings, reporter generator, reporter test server, fake sender, and configured `Handler`. `fakeSender` captures sent `sender.Email` values through a buffered channel.

## Control flow
The tests generate a moderation report, poll/send it, emulate command replies, and then verify subsequent reporting or absence of reporting. `TestSyzTestFlow` submits a patch-test command, confirms it is silent on success, fakes job completion, generates a report, and verifies the result email references the original user reply.

## State and persistence behavior
Uses in-memory/test Spanner and blob storage from `app.TestEnvironment`. Reporter state advances through real reporter APIs. Fake sender captures transient outgoing email state without external delivery.

## Dependencies and integration points
Exercises `pkg/controller`, `pkg/reporter`, `pkg/email`, `pkg/emailclient`, `pkg/db`, and API clients. It validates that email reporter behavior aligns with report generation and job submission.

## Risks and edge cases
The fake sender always returns `"email-id"` and never errors, so send-failure/ambiguous-delivery behavior is not covered. The tests validate selected email fields and body snippets but intentionally ignore full report body rendering in some paths.

## Test signals
Strong coverage for command semantics, recipient/CC/subject construction, moderation transition, invalidation, own-email suppression, forwarded own-email acceptance, and patch-test result reporting.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/email-reporter/handler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/email-reporter/kustomization.yaml -->
# sources/test-tools/syzkaller/syz-cluster/email-reporter/kustomization.yaml

## Purpose
Kustomize base for the email reporter component.

## Important APIs, types, and functions
Includes `deployment.yaml` and `lore-disk-pvc.yaml` as resources.

## Control flow
Overlays that include this directory render both the workload and persistent volume claim needed for Lore polling.

## State and persistence behavior
Delegates state definition to the PVC and deployment volume mount.

## Dependencies and integration points
Used by environment overlays when email reporting is enabled. It must be paired with global config and network policies that allow reporter/controller/email access.

## Risks and edge cases
If included in a local overlay without a compatible storage class or service accounts, deployment can fail. The base itself does not patch environment-specific service accounts.

## Test signals
Covered only through Kustomize/render/deployment smoke paths, not direct unit tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/email-reporter/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/email-reporter/lore-disk-pvc.yaml -->
# sources/test-tools/syzkaller/syz-cluster/email-reporter/lore-disk-pvc.yaml

## Purpose
Defines persistent storage for the email reporter's Lore repository checkout.

## Important APIs, types, and functions
Creates a `v1` `PersistentVolumeClaim` named `reporter-lore-disk-claim` with `ReadWriteOnce`, 16Gi request, and `standard` storage class.

## Control flow
The email reporter deployment mounts this claim at `/lore-repo`; `MakeLorePoller` uses `/lore-repo/checkout` as its repository directory.

## State and persistence behavior
Persists the cloned/fetched Lore archive state across pod restarts, reducing fetch cost and preserving poller continuity.

## Dependencies and integration points
Requires a cluster storage class named `standard`. Mounted by `deployment.yaml`.

## Risks and edge cases
`ReadWriteOnce` aligns with the single-replica design; scaling replicas would not work safely with this claim. A too-small disk could break long-running Lore archive growth.

## Test signals
No direct test; deployment smoke or production monitoring would surface storage provisioning/mount failures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/email-reporter/lore-disk-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/email-reporter/main.go -->
# sources/test-tools/syzkaller/syz-cluster/email-reporter/main.go

## Purpose
Entry point and concurrency orchestration for the email reporter process.

## Important APIs, types, and functions
`main` loads config, validates `EmailReporting`, creates an email sender, constructs `Handler`, optionally creates a Lore poller, and starts goroutines under `errgroup`. Constants define sender poll period of 30 seconds and fetcher poll period of 2 minutes. `runConsumerLoop` processes polled Lore emails with retry delays. `MakeLorePoller` builds a `lore.Poller` with own-email addresses, 48-hour lookback, and stdout debug tracing.

## Control flow
Three logical loops can run: Lore poller loop if `LoreArchiveURL` is configured, consumer loop over the buffered channel, and outgoing report polling loop. `errgroup.WithContext` ties cancellation together. Consumer retries non-terminal processing errors with 30s, 1m, and 5m delays, and stops retrying for own/unknown emails.

## State and persistence behavior
The process keeps only channel/loop state in memory. Durable state is in report APIs, controller APIs, sender backend, and Lore checkout on the mounted disk. A file-level comment states only one copy should run at the same time.

## Dependencies and integration points
Depends on `app.Config`, `emailclient.MakeSender`, default controller/reporter clients, Lore poller, debug tracer, and `Handler`. Deployment mounts `/lore-repo`, and Dockerfile installs `git` for poller operation.

## Risks and edge cases
No OS signal handling is implemented beyond a background context, so shutdown relies on process termination. `PollReportsLoop` logs errors and continues forever. The retry loop condition uses `attempt < len(delays)`, which means the final attempt still logs retrying and indexes a valid delay only because the loop ranges over delays; the intended "give up" branch is effectively unreachable in the current range shape. A blocked consumer can back up the 16-slot channel.

## Test signals
`email_workflow_test.go` exercises `MakeLorePoller` and `ProcessPolledEmail`. `handler_test.go` covers handler behavior, but the concurrent main loop itself is not directly tested.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/email-reporter/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/kernel-disk/fetch-kernels-cron.yaml -->
# sources/test-tools/syzkaller/syz-cluster/kernel-disk/fetch-kernels-cron.yaml

## Purpose
Schedules periodic kernel repository fetching through Argo Workflows.

## Important APIs, types, and functions
Defines an Argo `CronWorkflow` named `fetch-kernels-cron`, scheduled at `0 */8 * * *`, with `concurrencyPolicy: Replace`, `startingDeadlineSeconds: 0`, and a workflow template reference to `fetch-kernels-workflow-template`.

## Control flow
Argo starts the referenced workflow three times daily. If a previous run is still active, it is replaced by the new run.

## State and persistence behavior
The workflow persists fetched refs into the shared kernel repository PVC defined by overlays. The cron object itself stores only schedule/controller state.

## Dependencies and integration points
Depends on the workflow template, Argo controller installation, service accounts/RBAC, controller `/trees` endpoint, and the kernel disk PVC.

## Risks and edge cases
`Replace` can interrupt a long fetch and leave git locks or partial state; the template removes a stale `packed-refs.lock` at start as a mitigation. `startingDeadlineSeconds: 0` means missed schedules are not backfilled.

## Test signals
No direct test in this file. Cluster smoke tests include deployment of kernel-disk resources but do not necessarily wait for scheduled execution.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/kernel-disk/fetch-kernels-cron.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/kernel-disk/fetch-kernels-once.yaml -->
# sources/test-tools/syzkaller/syz-cluster/kernel-disk/fetch-kernels-once.yaml

## Purpose
Defines a manually triggerable one-shot Argo workflow for fetching kernel repositories.

## Important APIs, types, and functions
Creates an Argo `Workflow` with generated name prefix `fetch-kernels-manual-` and `workflowTemplateRef` pointing to `fetch-kernels-workflow-template`.

## Control flow
When submitted, Argo instantiates the shared fetch-kernels template once.

## State and persistence behavior
Uses the same persistent kernel repository PVC through the template. The workflow object records only run state.

## Dependencies and integration points
Requires the workflow template and Argo installation. Useful for manual refresh or debugging outside the cron cadence.

## Risks and edge cases
Manual runs can overlap scheduled runs unless operators coordinate. Overlap on the same bare repository PVC can cause git locking/contention.

## Test signals
No direct automated test; operational utility manifest.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/kernel-disk/fetch-kernels-once.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/kernel-disk/fetch-kernels-template.yaml -->
# sources/test-tools/syzkaller/syz-cluster/kernel-disk/fetch-kernels-template.yaml

## Purpose
Argo workflow template that queries configured kernel trees and fetches their branches/tags into a shared bare git repository.

## Important APIs, types, and functions
Defines `WorkflowTemplate` `fetch-kernels-workflow-template` with entrypoint `main`, workflow pod label `tier: workflow`, pod GC and TTL settings, default service account `argo-executor-ksa`, HTTP template `query-trees-template`, and container template `process-tree` using `kernel-fetcher-ksa` and `alpine/git:latest`.

## Control flow
`main` first runs `query-trees-template`, which issues `GET http://controller-service:8080/trees`. Then `iterate-trees` loops over `$.trees` from the JSON response and invokes `process-tree` for each item, continuing on failure. Each process step mounts `base-kernel-repo-pv-claim`, initializes a bare repository if needed, removes/readds the remote named by tree name, fetches the configured branch/tags into namespaced refs, and prints the latest commit.

## State and persistence behavior
Persistent git object/ref state is stored in the shared PVC mounted at `/repo.git`. The workflow deletes completed pods after 12 hours and workflow objects after 24 hours. It removes stale `packed-refs.lock` before fetches to recover from interrupted runs.

## Dependencies and integration points
Depends on controller `/trees`, Argo expression/jsonpath support, kernel fetcher service account/RBAC, network policy egress for `app: kernel-repo-update`, and the PVC from GKE/local overlays.

## Risks and edge cases
The container template does not explicitly label pods `app: kernel-repo-update`, while the egress policy selects that label; if Argo does not add it elsewhere, git egress may be denied under egress enforcement. The template uses shell interpolation of tree fields in remote names/URLs/branches; malformed config could break shell commands. Shared bare repo writes with parallelism 1 avoid concurrent fetches within one workflow but not necessarily across overlapping workflows.

## Test signals
No direct unit test. Kustomize smoke deploys resources; runtime correctness requires Argo/controller/network/storage integration.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/kernel-disk/fetch-kernels-template.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/kernel-disk/kustomization.yaml -->
# sources/test-tools/syzkaller/syz-cluster/kernel-disk/kustomization.yaml

## Purpose
Kustomize base for kernel repository fetch workflows.

## Important APIs, types, and functions
Includes `fetch-kernels-template.yaml` and `fetch-kernels-cron.yaml`. The one-shot workflow is intentionally not included by default.

## Control flow
Overlays including kernel-disk get the reusable template and scheduled cron.

## State and persistence behavior
State is provided by environment overlays that define `base-kernel-repo-pv-claim`.

## Dependencies and integration points
Pulled into `overlays/common/kustomization.yaml` and then local/GKE overlays.

## Risks and edge cases
A missing PVC or Argo installation makes rendered resources fail at runtime even if Kustomize succeeds.

## Test signals
Indirectly included in local cluster smoke deployment.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/kernel-disk/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/local_cluster_test.sh -->
# sources/test-tools/syzkaller/syz-cluster/local_cluster_test.sh

## Purpose
End-to-end smoke script for building syz-cluster containers, deploying a local test cluster with kind, and verifying dashboard reachability.

## Important APIs, types, and functions
Shell script with `set -e`, dependency checks for `kind` and `kubectl`, cluster name `syz-cluster-test`, local kubeconfig path `.test-kubeconfig`, and `cleanup` trap. It runs `make all-containers`, `kind load docker-image`, `make k8s-config-local-infra`, `make migrate-local`, and `make k8s-config-test | kubectl apply -f -`.

## Control flow
The script deletes any existing test cluster, creates a new kind cluster, builds and loads local images, deploys infrastructure, runs database migrations, deploys syz-cluster test config, waits for core deployments, port-forwards the dashboard service, curls `/`, and requires HTTP 200. On failure it dumps pod status/logs/describes and leaves the cluster intact. On success it deletes the cluster and kubeconfig.

## State and persistence behavior
Creates a temporary local Kubernetes cluster and Docker images tagged `local_smoke/`. Kubeconfig is written under the source directory. Failure intentionally preserves cluster state for debugging.

## Dependencies and integration points
Depends on Docker, kind, kubectl, Makefile targets, local overlays, database migration job, and dashboard service. It exercises dashboard, controller, reporter server, series tracker, local Spanner emulator, fake GCS, and Argo-related config enough to reach availability.

## Risks and edge cases
The script uses `grep` and unquoted `$IMAGES`; no images found or image names with unexpected whitespace would fail. Port-forward uses fixed local port 8080 and a fixed sleep. Cleanup kills the port-forward only on the explicit HTTP failure path and after success; abrupt intermediate failures rely on process cleanup by shell exit/environment.

## Test signals
Provides high-value cluster integration signal that manifests render, images start, migrations run, deployments become available, and the dashboard responds with HTTP 200.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/local_cluster_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/argo/kustomization.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/common/argo/kustomization.yaml

## Purpose
Composes upstream Argo Workflows installation with syz-cluster RBAC and controller patches.

## Important APIs, types, and functions
Kustomize `resources` includes Argo Workflows v3.6.2 `install.yaml` from GitHub and local `workflow-roles.yaml`. Patches apply `patch-argo-controller.yaml` and `patch-workflow-controller-configmap.yaml`.

## Control flow
Rendering fetches or references the remote Argo install manifest, then overlays local service account and default workflow configuration changes.

## State and persistence behavior
Installs Argo controller resources and RBAC; no application data state is defined here.

## Dependencies and integration points
Used by local common overlay; GKE common appears to rely on common resources differently. Interacts with workflow templates, service accounts, artifact repositories, and network policies.

## Risks and edge cases
Remote URL pinning to version v3.6.2 is stable by version tag but still requires network access at render time unless cached. Argo upstream manifest changes under the same tag would be unexpected but high impact. Namespace/service-account assumptions must match patches.

## Test signals
Indirectly exercised by local cluster smoke test during infrastructure deployment.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/argo/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/argo/patch-argo-controller.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/common/argo/patch-argo-controller.yaml

## Purpose
Patches the Argo workflow-controller deployment to use the expected controller service account.

## Important APIs, types, and functions
Targets `apps/v1` `Deployment` `workflow-controller` in namespace `argo` and sets `spec.template.spec.serviceAccountName` to `argo-controller-ksa`. Includes kube-linter annotation for Terraform-defined account handling.

## Control flow
Kustomize applies this patch on top of Argo's upstream install manifest.

## State and persistence behavior
No data persistence. It changes runtime identity and therefore permissions.

## Dependencies and integration points
Depends on `workflow-roles.yaml` defining role bindings for `argo-controller-ksa` and on service account creation in the selected environment.

## Risks and edge cases
If the service account does not exist, the controller pod fails admission/startup. If upstream Argo deployment name/namespace changes, the patch misses its target.

## Test signals
Smoke deployment would fail if Argo controller cannot start because of service account mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/argo/patch-argo-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/argo/patch-workflow-controller-configmap.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/common/argo/patch-workflow-controller-configmap.yaml

## Purpose
Sets Argo workflow defaults so workflows run under the expected executor service account.

## Important APIs, types, and functions
Patches `v1` `ConfigMap` `workflow-controller-configmap` in namespace `argo`, setting `data.workflowDefaults` to a YAML snippet with `spec.serviceAccountName: argo-executor-ksa`.

## Control flow
Argo controller reads this config map and applies the default service account to workflows unless overridden.

## State and persistence behavior
No app data; affects workflow execution identity.

## Dependencies and integration points
Integrates with `workflow-roles.yaml`, local service accounts, and workflow templates that may override service accounts for specialized steps.

## Risks and edge cases
Indentation inside the string must remain valid for Argo's config parser. A missing executor service account or RBAC binding breaks workflow pods.

## Test signals
Workflow execution in local smoke or manual runs validates this indirectly.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/argo/patch-workflow-controller-configmap.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/argo/workflow-roles.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/common/argo/workflow-roles.yaml

## Purpose
Defines RBAC needed by Argo workflow executors/controllers and syz-cluster service accounts.

## Important APIs, types, and functions
Creates `ClusterRole` `argo-workflow-role` for workflow CRUD/status, `ClusterRole` `argo-workflowtasks-role` for workflow task result/taskset/artifact GC operations, several `ClusterRoleBinding` and `RoleBinding` resources for executor/controller/service accounts, and a service-account-token `Secret` for `argo-executor-ksa`.

## Control flow
Kubernetes RBAC authorizes workflow creation/updates and task result publication by the specified service accounts.

## State and persistence behavior
No application data. The token secret creates credential material for the executor service account.

## Dependencies and integration points
Assumes service accounts `argo-executor-ksa`, `argo-controller-ksa`, and `gke-service-ksa` in relevant namespaces, plus upstream Argo roles `argo-cluster-role` and `argo-role`. Used by Argo patches and workflow templates.

## Risks and edge cases
Cluster-wide permissions are broad and security-sensitive. Namespace mismatches or missing upstream role names break bindings. Manually creating service-account-token secrets is version-sensitive in newer Kubernetes service account token practices.

## Test signals
Failures surface when Argo controller/executor cannot create, update, or report workflow state. No direct unit tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/argo/workflow-roles.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/kustomization.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/common/kustomization.yaml

## Purpose
Composes the shared syz-cluster base resources and common network policies.

## Important APIs, types, and functions
Includes controller, dashboard, series-tracker, kernel-disk, reporter-server, workflow, and multiple network policy resources. Applies a JSON patch to all `Deployment` resources replacing the first container's `imagePullPolicy` with `IfNotPresent`.

## Control flow
Environment-specific overlays include this common overlay, then add infra/config/storage/service-account resources.

## State and persistence behavior
No state itself, but it brings in components that use Spanner, blob storage, PVCs, and workflows.

## Dependencies and integration points
Central integration point for most syz-cluster workloads. Network policies here assume consistent pod labels across component deployments and workflow pods.

## Risks and edge cases
The imagePullPolicy patch targets `/containers/0`; multi-container deployments or reordered containers could be patched incorrectly. Omitting email-reporter from common resources means it must be included elsewhere when needed. Label drift can invalidate network policies.

## Test signals
Core manifest path for `local_cluster_test.sh` and Kustomize targets.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/network-deny-all.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/common/network-deny-all.yaml

## Purpose
Establishes a default ingress-deny baseline for pods in the default namespace.

## Important APIs, types, and functions
Defines `networking.k8s.io/v1` `NetworkPolicy` `default-deny-all` with empty `podSelector` and `policyTypes: Ingress`.

## Control flow
Once applied, all selected pods deny ingress unless another policy permits it.

## State and persistence behavior
No data state; controls network admission.

## Dependencies and integration points
Requires explicit ingress allow policies for controller, reporter-server, dashboard, fake GCS, Spanner emulator, and other services.

## Risks and edge cases
This policy denies only ingress, not egress. Components without matching allow policies become unreachable. Network policy enforcement depends on the cluster CNI.

## Test signals
Smoke tests catch major missing ingress paths such as dashboard/controller availability.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/network-deny-all.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-controller.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-controller.yaml

## Purpose
Allows selected syz-cluster components to reach controller pods.

## Important APIs, types, and functions
Defines `NetworkPolicy` `controller-access` selecting `app: controller`, with ingress allowed from pods labeled `app: series-tracker`, `app: email-reporter`, or `tier: workflow`.

## Control flow
Under default ingress deny, only these pod groups may initiate ingress to controller pods.

## State and persistence behavior
No persistence; network control only.

## Dependencies and integration points
Matches the controller service used by series tracker, email reporter job submissions, and Argo workflows such as fetch-kernels querying `/trees`.

## Risks and edge cases
Dashboard access to controller is not allowed here, likely because dashboard reads from DB/blob directly. Pod label drift breaks access. Ports are unrestricted for allowed sources.

## Test signals
Workflows and series tracker operation exercise this path; local smoke waits for controller deployment but does not deeply test all callers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-email-sender.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-email-sender.yaml

## Purpose
Allows outbound internet access for email-sending related pods.

## Important APIs, types, and functions
Defines two egress `NetworkPolicy` resources: `send-test-email-git-access` for `app: send-test-email` and `email-reporter-git-access` for `app: email-reporter`, both with unrestricted egress.

## Control flow
If egress isolation is active for these pods, the empty egress rule permits all destinations.

## State and persistence behavior
No persistence.

## Dependencies and integration points
Supports SMTP/dashapi/email sending and Lore git access from email reporter, plus test email tooling.

## Risks and edge cases
The policy is broad and allows all outbound traffic, not just SMTP/dashapi/lore. It only matters if an egress policy selects these pods; otherwise Kubernetes egress is allowed by default.

## Test signals
Email reporter tests use fake sender and do not validate network policy. Cluster-level email/lore operation validates it operationally.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-email-sender.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-git-access.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-git-access.yaml

## Purpose
Allows outbound internet/git access for components that pull repositories.

## Important APIs, types, and functions
Defines egress policies for `app: series-tracker` and `app: kernel-repo-update`, both allowing all egress.

## Control flow
When egress isolation applies, selected pods can reach remote git servers and related resources.

## State and persistence behavior
No persistence.

## Dependencies and integration points
Supports series tracker fetching patch series and kernel fetcher workflow fetching kernel trees.

## Risks and edge cases
Broad egress is less restrictive than necessary. The kernel fetch workflow template must label pods with `app: kernel-repo-update` somewhere for the policy to select them; the researched template only shows `tier: workflow`.

## Test signals
No direct tests. Runtime failures would appear as git fetch/network errors in series tracker or Argo workflow logs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-git-access.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-reporter.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-reporter.yaml

## Purpose
Allows email reporter pods to access reporter-server pods.

## Important APIs, types, and functions
Defines `NetworkPolicy` `reporter-server-access` selecting `app: reporter-server`, with ingress allowed from `app: email-reporter`.

## Control flow
Under ingress deny, email reporter can call reporter-server APIs such as get-next-report, confirm, upstream, invalidate, and record-reply.

## State and persistence behavior
No persistence; controls network reachability to the report lifecycle service.

## Dependencies and integration points
Matches `Handler` use of `api.ReporterClient` and default reporter client wiring.

## Risks and edge cases
Only email reporter is allowed here; other intended reporter clients need their own policy. Ports are unrestricted for the allowed source.

## Test signals
Go tests use in-process test servers and do not validate this policy. Deployment/runtime integration validates it.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-reporter.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-web-dashboard.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-web-dashboard.yaml

## Purpose
Allows ingress to the web dashboard pods.

## Important APIs, types, and functions
Defines `NetworkPolicy` `access-to-web-dashboard` in namespace `default`, selecting `app: web-dashboard`, allowing ingress from any source (`from: []`) to TCP port 8081.

## Control flow
Under default ingress deny, this opens the dashboard's container port to all sources in the policy scope.

## State and persistence behavior
No persistence.

## Dependencies and integration points
Matches dashboard `main.go` listening on 8081 and service target port 8081. GKE service exposes port 80 with NEG annotations.

## Risks and edge cases
Open ingress may be intended for public dashboard access, but exposure is broad at the network policy layer. Service/listener port drift would break access.

## Test signals
`local_cluster_test.sh` validates dashboard service reachability.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/network-policy-web-dashboard.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/patch-workflow-controller.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/common/patch-workflow-controller.yaml

## Purpose
Patches Argo workflow-controller service account in the common overlay outside the `argo/` suboverlay.

## Important APIs, types, and functions
Targets `apps/v1` `Deployment` `workflow-controller` in namespace `argo` and sets `serviceAccountName` to `argo-workflows-ksa`.

## Control flow
If included as a Kustomize patch, it changes the controller identity used by the Argo controller pod.

## State and persistence behavior
No application state; affects RBAC identity.

## Dependencies and integration points
Potentially overlaps with `overlays/common/argo/patch-argo-controller.yaml`, which sets `argo-controller-ksa`. The researched `overlays/common/kustomization.yaml` does not include this file directly.

## Risks and edge cases
Conflicting service account names across patch files can cause environment drift if both are ever applied. Because it appears unused by the researched common kustomization, it may be legacy or intended for another path.

## Test signals
No direct signal unless an overlay includes it. Argo controller startup would reveal service-account mismatch.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/common/patch-workflow-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/gke/common/global-config-env.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/gke/common/global-config-env.yaml

## Purpose
Provides environment variable config entries for GKE deployments.

## Important APIs, types, and functions
Defines `ConfigMap` `global-config-env` with `SPANNER_DATABASE_URI` and `BLOB_STORAGE_GCS_BUCKET` values substituted from `${SPANNER_DATABASE_URI}` and `${BLOB_STORAGE_GCS_BUCKET}`.

## Control flow
Kustomize/render tooling substitutes environment-specific values before deployment; pods consume the config map through their app environment setup.

## State and persistence behavior
No persistence itself; points services at durable Cloud Spanner and GCS resources.

## Dependencies and integration points
Used by GKE common overlay and application config loading.

## Risks and edge cases
Unsubstituted placeholders would deploy invalid config. Secrets are not handled here; bucket/database names are non-secret but environment-specific.

## Test signals
Runtime startup failures would reveal bad values. No direct unit test.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/gke/common/global-config-env.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/gke/common/kernel-disk-pvc.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/gke/common/kernel-disk-pvc.yaml

## Purpose
Defines GKE Filestore-backed shared storage for base kernel repositories.

## Important APIs, types, and functions
Creates `StorageClass` `filestore-custom` using provisioner `filestore.csi.storage.gke.io`, tier `standard`, network `gke-network`, immediate binding, and expansion support. Creates PVC `base-kernel-repo-pv-claim` with `ReadWriteMany` and 1Ti request.

## Control flow
Kernel fetch workflows mount this claim and update a shared bare git repository.

## State and persistence behavior
Persists kernel git repositories across workflow runs and supports multi-reader/multi-writer access through Filestore.

## Dependencies and integration points
Depends on GKE Filestore CSI driver, network `gke-network`, and workflow templates referencing the claim name.

## Risks and edge cases
1Ti is noted as the minimum, so cost and capacity are significant. Shared write behavior still needs workflow concurrency controls to avoid git conflicts.

## Test signals
Runtime storage provisioning and workflow execution validate this. Local smoke uses a different PVC.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/gke/common/kernel-disk-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/gke/common/kustomization.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/gke/common/kustomization.yaml

## Purpose
Common GKE overlay for syz-cluster.

## Important APIs, types, and functions
Includes `../../common`, `global-config-env.yaml`, `kernel-disk-pvc.yaml`, and `workflow-artifacts.yaml`. Applies patches adding nested-VM tolerations and node selectors to boot/fuzz/retest workflow templates, and replaces dashboard service annotations with a Google Cloud NEG annotation.

## Control flow
Production and staging GKE overlays build on this common layer, then provide concrete global config. Workflows are scheduled to nodes labeled for nested virtualization.

## State and persistence behavior
Adds cloud storage bindings for Spanner/GCS/artifacts and Filestore kernel repo storage.

## Dependencies and integration points
Depends on GKE node labels `amd64-nested-virtualization: "true"`, taint `workload=nested-vm:NoSchedule`, Google Cloud NEG controller, and workflow template names matching `(boot|fuzz|retest)-action-template`.

## Risks and edge cases
Regex target patches depend on Kustomize behavior and exact workflow template names. Missing node labels/taints can leave workflows unschedulable. The annotation patch replaces all existing service annotations.

## Test signals
Validated by GKE deployment/rendering and workflow scheduling, not local smoke.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/gke/common/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/gke/common/workflow-artifacts.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/gke/common/workflow-artifacts.yaml

## Purpose
Configures Argo's default artifact repository for GKE.

## Important APIs, types, and functions
Defines `ConfigMap` `artifact-repositories` annotated with `workflows.argoproj.io/default-artifact-repository: gcs-repo`. The `gcs-repo` entry points to GCS bucket `${WORKFLOW_ARTIFACTS_BUCKET}`.

## Control flow
Argo workflows use this default artifact repository for artifact storage unless overridden.

## State and persistence behavior
Artifact state is persisted in the configured GCS bucket.

## Dependencies and integration points
Requires Argo controller config support, GCS bucket existence, and service account permissions.

## Risks and edge cases
Unsubstituted or missing bucket values break workflow artifacts. The config has no key/credential detail, so it relies on workload identity/service account setup.

## Test signals
Workflow artifact upload/download runtime behavior validates it.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/gke/common/workflow-artifacts.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/gke/prod/global-config.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/gke/prod/global-config.yaml

## Purpose
Production syz-cluster global configuration.

## Important APIs, types, and functions
YAML config sets `URL: https://ci.syzbot.org`, `parallelWorkflows: 15`, Lore archive names, email reporting via dashapi, support/credit/archive/moderation/report CC addresses, dashapi context prefix `ci`, kernel trees, and fuzz targets grouped by subsystem mailing lists and campaigns.

## Control flow
Application components load this config from `global-config`. Controller exposes trees, series tracker/reporter use Lore/email settings, workflows use fuzz target campaigns, and dashboard/report links use the configured URL.

## State and persistence behavior
No state directly, but it controls production interactions with external systems: dashapi, mailing lists, lore.kernel.org, kernel git remotes, GCS corpus URLs, and workflow concurrency.

## Dependencies and integration points
Integrates nearly every syz-cluster service: email reporter, series tracker, controller, workflow generator, reporter, dashboard URLs, and fuzz config. Depends on external kernel repositories and mailing-list conventions.

## Risks and edge cases
This file contains production routing and recipient lists; mistakes can spam public lists, miss maintainers, or run wrong workflows. `parallelWorkflows: 15` increases resource demand. External URLs and branches must remain valid.

## Test signals
No direct test. Production behavior and config parser tests elsewhere are the main validation paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/gke/prod/global-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/gke/prod/kustomization.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/gke/prod/kustomization.yaml

## Purpose
Production GKE Kustomize overlay.

## Important APIs, types, and functions
Includes `../common` and creates a config map generator named `global-config` from `global-config.yaml`.

## Control flow
Rendering composes GKE common resources with production config data.

## State and persistence behavior
No state; config map content drives production runtime behavior.

## Dependencies and integration points
Depends on GKE common overlay and all base resources. Components mount/read the generated `global-config`.

## Risks and edge cases
ConfigMap generator name hashing behavior must align with deployment references or be disabled elsewhere. Production and staging differ primarily through their global config.

## Test signals
Kustomize build/deployment validation; no direct tests in file.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/gke/prod/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/gke/staging/global-config.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/gke/staging/global-config.yaml

## Purpose
Staging GKE global configuration.

## Important APIs, types, and functions
Sets `URL: https://staging.ci.syzbot.org`, `parallelWorkflows: 2`, email reporting via dashapi with staging client/from/support/list values, one `torvalds` tree, and a simple default KASAN fuzz target.

## Control flow
Staging services consume this config to run a smaller syz-cluster environment with fewer workflows and reduced target scope.

## State and persistence behavior
No direct persistence; controls staging external integrations and workflow volume.

## Dependencies and integration points
Same config schema as production, consumed by app environment, controller, reporter, workflows, and email reporter.

## Risks and edge cases
Staging still uses external dashapi/lists and kernel repos, so incorrect recipients or context prefix can affect real systems. Reduced config may miss production-only bugs.

## Test signals
Useful as a lower-risk deployment target; no direct tests in this file.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/gke/staging/global-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/gke/staging/kustomization.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/gke/staging/kustomization.yaml

## Purpose
Staging GKE Kustomize overlay.

## Important APIs, types, and functions
Includes `../common` and generates `global-config` from staging `global-config.yaml`.

## Control flow
Builds the GKE common stack with staging runtime config.

## State and persistence behavior
No state; generated config map drives staging behavior.

## Dependencies and integration points
Same as prod overlay but with staging-specific config.

## Risks and edge cases
Same configMapGenerator name/reference considerations as production. Staging-only config drift can hide production issues.

## Test signals
Kustomize/deployment validation only.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/gke/staging/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/cloud-spanner-emulator.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/cloud-spanner-emulator.yaml

## Purpose
Deploys a local Cloud Spanner emulator and service for local/test clusters.

## Important APIs, types, and functions
Creates `Deployment` `cloud-spanner-emulator` with one `gcr.io/cloud-spanner-emulator/emulator:latest` container exposing ports 9010 and 9020. Creates a `Service` exposing named `grpc` and `http` ports.

## Control flow
Local components use `SPANNER_EMULATOR_HOST: cloud-spanner-emulator:9010` from local config to connect to this service.

## State and persistence behavior
The emulator deployment has no persistent volume; database state is ephemeral across pod/cluster recreation.

## Dependencies and integration points
Used by local common overlay and database migration flow. Access is controlled by `network-policy-spanner.yaml`.

## Risks and edge cases
Image tag `latest` is floating. No resource limits or persistence are defined. Emulator behavior may differ from production Spanner.

## Test signals
Local cluster smoke migration and workload startup validate emulator reachability.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/cloud-spanner-emulator.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/fake-gcs.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/fake-gcs.yaml

## Purpose
Deploys fake GCS storage for local/test clusters and permits selected ingress.

## Important APIs, types, and functions
Creates `Deployment` `fake-gcs-server` with init container creating `/data/workflow-artifacts` and `/data/blobs`, container `fsouza/fake-gcs-server`, service on port 4443 of type `LoadBalancer`, and network policy `fake-gcs-server-access` allowing ingress from controller, reporter, web-dashboard, workflow pods, and workflow-controller.

## Control flow
Local config sets `STORAGE_EMULATOR_HOST` to the fake GCS service URL and `BLOB_STORAGE_GCS_BUCKET` to `blobs`. Argo workflow artifact config uses `workflow-artifacts`.

## State and persistence behavior
Uses `emptyDir`, so object state is ephemeral for the pod lifetime and lost on restart.

## Dependencies and integration points
Integrates with blob storage code, workflow artifacts, dashboard blob reads, controller uploads, reporter access, and local smoke tests.

## Risks and edge cases
Service type `LoadBalancer` may behave differently in kind/minikube. `emptyDir` means pod restart loses objects. The network policy label `app: reporter` must match actual reporter-server label; researched common policy uses `app: reporter-server`, so label consistency should be checked.

## Test signals
Local smoke exercises blob storage enough for deployments and dashboard availability; Go tests also use app test storage outside Kubernetes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/fake-gcs.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/global-config-env.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/global-config-env.yaml

## Purpose
Provides local environment variables for Spanner emulator and fake GCS.

## Important APIs, types, and functions
Defines `ConfigMap` `global-config-env` with `SPANNER_EMULATOR_HOST`, `SPANNER_DATABASE_URI`, `STORAGE_EMULATOR_HOST`, and `BLOB_STORAGE_GCS_BUCKET`.

## Control flow
Local pods read these values so app environment connects to in-cluster emulators instead of cloud services.

## State and persistence behavior
No state; points apps to ephemeral local services.

## Dependencies and integration points
Requires `cloud-spanner-emulator` and `fake-gcs-server` services from local common overlay.

## Risks and edge cases
Hard-coded fake project/instance/database names must align with migration tooling. Bucket name must match fake-gcs init-created directory.

## Test signals
Local cluster smoke migration/startup validates the values.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/global-config-env.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/kernel-disk-pvc.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/kernel-disk-pvc.yaml

## Purpose
Defines local shared storage for kernel repository cache.

## Important APIs, types, and functions
Creates PVC `base-kernel-repo-pv-claim` using storage class `standard`, access mode `ReadWriteMany`, and 32Gi request.

## Control flow
Kernel fetch workflows mount this claim at `/repo.git`.

## State and persistence behavior
Persists bare git repository data within the local cluster storage backend.

## Dependencies and integration points
Requires a local storage class that supports `ReadWriteMany`; this can be cluster-specific.

## Risks and edge cases
Many local Kubernetes defaults do not support RWX on `standard`. If unsupported, workflows remain pending. 32Gi may be too small for broad kernel mirror use.

## Test signals
Smoke deployment may catch PVC provisioning failures depending on whether workflow resources are scheduled during the test.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/kernel-disk-pvc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/kustomization.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/kustomization.yaml

## Purpose
Composes local infrastructure shared by local/minikube/test overlays.

## Important APIs, types, and functions
Includes service accounts, kernel disk PVC, common Argo overlay, local config env, fake GCS, Spanner emulator, Spanner network policy, and workflow artifact config. Applies `patch-workflow-controller-configmap.yaml`.

## Control flow
Local environment overlays include this layer before adding component bases and environment-specific global config.

## State and persistence behavior
Provides emulator-backed state and local PVC state rather than cloud Spanner/GCS/Filestore.

## Dependencies and integration points
Central integration point for local cluster tests and development. Depends on local service accounts/RBAC and fake infrastructure resources.

## Risks and edge cases
Including Argo remote install can require network at build time. Local storage and LoadBalancer behavior vary across kind/minikube.

## Test signals
Directly exercised by `local_cluster_test.sh` through `make k8s-config-local-infra`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/network-policy-spanner.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/network-policy-spanner.yaml

## Purpose
Allows selected pods to access the local Spanner emulator.

## Important APIs, types, and functions
Defines `NetworkPolicy` `cloud-spanner-access` selecting `app: cloud-spanner-emulator`, with ingress allowed from pods labeled `app: db-mgmt`, `app: controller`, `app: web-dashboard`, and `app: reporter`.

## Control flow
Under default ingress deny, only selected app pods can connect to emulator ports.

## State and persistence behavior
No persistence; controls network reachability.

## Dependencies and integration points
Supports migrations, controller, dashboard, and reporter data access in local clusters.

## Risks and edge cases
Label `app: reporter` must match actual reporter server or worker labels; if the component uses `app: reporter-server`, access may fail. Email reporter is not listed, likely because it uses reporter/controller APIs rather than direct DB.

## Test signals
Local smoke migration and dashboard availability validate at least db-mgmt/controller/dashboard access.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/network-policy-spanner.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/patch-workflow-controller-configmap.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/patch-workflow-controller-configmap.yaml

## Purpose
Adds fake GCS emulator environment to Argo executor configuration for local clusters.

## Important APIs, types, and functions
Patches `ConfigMap` `workflow-controller-configmap` in namespace `argo`, setting `data.executor` to include environment variable `STORAGE_EMULATOR_HOST=http://fake-gcs-server.default.svc.cluster.local:4443`.

## Control flow
Argo executor pods inherit this environment so artifact handling targets fake GCS.

## State and persistence behavior
No state directly; redirects workflow artifact IO to ephemeral fake GCS.

## Dependencies and integration points
Depends on fake-gcs service and Argo controller config semantics. Used together with local `workflow-artifacts.yaml`.

## Risks and edge cases
ConfigMap data replacement must coexist with other Argo config patches; replacing `data.executor` incorrectly can drop other executor settings. YAML indentation inside string is significant.

## Test signals
Workflow artifact behavior in local runs validates this.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/patch-workflow-controller-configmap.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/service-accounts.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/service-accounts.yaml

## Purpose
Defines local service accounts and RBAC bindings that GKE/Terraform would otherwise provide.

## Important APIs, types, and functions
Creates service accounts including `gke-service-ksa`, `argo-executor-ksa`, `argo-controller-ksa`, and `kernel-fetcher-ksa` in namespace `default` or `argo` as appropriate. Adds a `ClusterRoleBinding` for `kernel-fetcher-ksa` to `argo-workflowtasks-role`.

## Control flow
Local overlays create these identities before workloads and workflows refer to them.

## State and persistence behavior
No application data; establishes Kubernetes identities.

## Dependencies and integration points
Integrates with Argo RBAC in `workflow-roles.yaml`, workflow templates, local deployments, and GKE-compatible service account names.

## Risks and edge cases
The service account set must stay in sync with deployment manifests and Argo patches. Binding kernel fetcher to workflow task role is necessary for Argo executor reporting, but any missing broader permissions could break specialized workflows.

## Test signals
Local cluster smoke catches missing service accounts during pod creation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/service-accounts.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/workflow-artifacts.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/local/common/workflow-artifacts.yaml

## Purpose
Configures Argo's default artifact repository for local clusters.

## Important APIs, types, and functions
Defines `ConfigMap` `artifact-repositories` annotated as default artifact repository, with `gcs-repo` bucket `workflow-artifacts`.

## Control flow
Argo stores workflow artifacts in the fake GCS bucket initialized by `fake-gcs.yaml`.

## State and persistence behavior
Artifact state is stored in fake GCS backed by `emptyDir`, so it is ephemeral.

## Dependencies and integration points
Requires fake GCS service and executor `STORAGE_EMULATOR_HOST` patch.

## Risks and edge cases
Bucket name must match fake-gcs initialization. Artifacts disappear on fake-gcs pod restart.

## Test signals
Workflow runs in local cluster validate artifact upload/download.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/common/workflow-artifacts.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/minikube/global-config.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/local/minikube/global-config.yaml

## Purpose
Local minikube/debug runtime configuration.

## Important APIs, types, and functions
Sets `URL: http://localhost`, `parallelWorkflows: 1`, a sample Lore archive, SMTP email reporting config, one `torvalds` tree, and a small set of fuzz targets/campaigns.

## Control flow
Local services use this config for low-concurrency development runs with fake/local infrastructure.

## State and persistence behavior
No state; controls local runtime behavior and external URLs.

## Dependencies and integration points
Used by minikube overlay's configMapGenerator. Requires SMTP config to be meaningful if email sending is exercised.

## Risks and edge cases
Some values are explicitly placeholder/debug values. External corpus/kernel URLs are still real network dependencies. Email settings may send if wired to a real SMTP service.

## Test signals
Useful for manual local deployment; automated smoke uses the local test overlay instead.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/minikube/global-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/minikube/kustomization.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/local/minikube/kustomization.yaml

## Purpose
Minikube/local development Kustomize overlay.

## Important APIs, types, and functions
Includes `../common` and `../../common`, and generates `global-config` from `global-config.yaml`.

## Control flow
Builds local infrastructure plus common application resources with minikube/debug config.

## State and persistence behavior
Uses local emulator/PVC state from local common.

## Dependencies and integration points
Depends on local common infrastructure and shared app common overlay.

## Risks and edge cases
Layer ordering matters because it includes both infrastructure and app resources. ConfigMap generator naming must align with consumers.

## Test signals
Manual minikube deployment path; not the main smoke test overlay.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/minikube/kustomization.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/test/global-config.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/local/test/global-config.yaml

## Purpose
Minimal local test global configuration used by the smoke test overlay.

## Important APIs, types, and functions
Sets `URL: http://localhost` and `parallelWorkflows: 1`.

## Control flow
Smoke deployment uses this small config to start core components without broad production/staging workload definitions.

## State and persistence behavior
No state. It limits runtime behavior by omitting email/tree/fuzz configuration.

## Dependencies and integration points
Used by local test overlay configMapGenerator.

## Risks and edge cases
Because it is minimal, it may not exercise config paths for email reporting, tree fetching, or fuzz targets.

## Test signals
Directly used by `local_cluster_test.sh`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/test/global-config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/test/kustomization.yaml -->
# sources/test-tools/syzkaller/syz-cluster/overlays/local/test/kustomization.yaml

## Purpose
Kustomize overlay for automated local smoke testing.

## Important APIs, types, and functions
Includes `../common` and `../../common`, and generates `global-config` from the minimal test `global-config.yaml`.

## Control flow
The smoke script applies this rendered overlay after local infra and migrations, then waits for core deployments.

## State and persistence behavior
Uses local emulator and fake storage state from `../common`.

## Dependencies and integration points
Primary overlay consumed by `make k8s-config-test` in `local_cluster_test.sh`.

## Risks and edge cases
Minimal config means smoke coverage focuses on deployment/readiness/dashboard reachability, not full workflow/email functionality. Include order and generated config names must stay compatible with deployments.

## Test signals
High-value smoke signal through `local_cluster_test.sh`, which deploys this overlay and checks dashboard HTTP 200.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/syz-cluster/overlays/local/test/kustomization.yaml -->
