# Research: subset-b-009391

This grouped report covers the syzkaller dashboard App Engine API, AI job/reporting persistence layer, and the associated integration tests listed in subset-b-009391. Each section is source-tree aligned for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/ai_report_test.go -->
# sources/test-tools/syzkaller/dashboard/app/ai_report_test.go

## Purpose

`ai_report_test.go` is an integration-heavy test suite for the dashboard's AI patch reporting lifecycle. It exercises how finished AI patching jobs become external report drafts, how reports are confirmed as published, how reviewer commands approve/reject/unreject patches, and how review comments create patch-iteration jobs. The file targets the newer Spanner-backed AI tables through public dashboard API clients and the existing App Engine test context.

## Important helpers, tests, and APIs

- `(*Ctx).setupAIPatchJob` creates a build, reports a reproducible crash, registers the patching workflow with an agent, and creates a Spanner AI job tied to the resulting bug.
- `(*Ctx).finishAIPatchJob` completes an AI job with default patch results (`PatchDescription`, `PatchDiff`, `KernelRepo`, `KernelCommit`) and optional overrides.
- `TestAIExternalReporting` covers the full moderation-to-public reporting path, including `AIPollReport`, `AIConfirmReport`, `AIReportCommand` upstream/reject/unreject commands, `LoadUIJobReviewHistory`, and `aidb.LoadJob`.
- `TestAINoParallelReports`, `TestAIUpstreamTwice`, `TestAIUpstreamIdempotency`, and `TestAIUpstreamConcurrent` cover exclusivity, stage ordering, idempotency by external message ID, and races between iteration and upstream commands.
- `TestAIPatchIterationSuccess`, `testExtendedPatchIteration`, `TestAIPatchIterationBackoff`, `TestAIPatchIterationReplySuccess`, `TestAIPatchIterationEmptyResult`, and `TestAIManualIteration` validate comment ingestion, debounce, patch history construction, changelog/version propagation, reply-only outputs, backoff, stale-thread handling, and manual iteration.
- `TestAIManualPushToReporting`, `TestAIAssessmentNoReport`, `TestAIPatchFilter`, and `TestAIActionEmailsAuth` validate UI-driven reporting pushes, non-patch assessment behavior, bug-list filtering for pending AI patches, and command authorization/DKIM checks.

## Control flow and state behavior

Most tests set an `AIConfig` on namespace `ains`, then simulate a crash to create a bug and a patching job. Completion through `AIJobDone` writes job results to Spanner. Reporting poll calls then materialize `JobReporting` rows into `dashapi.ReportPollResult` values. Confirmation calls set `ReportedAt` and `ExtID`, and command calls use the external ID to locate the active reporting thread.

Patch iteration tests follow a stricter sequence: publish an initial report, submit external comments with root/message IDs, advance mocked time past the 30-minute debounce, poll an agent for `ai.WorkflowPatchIteration`, then finish that job with either a new patch, replies, or empty output. A new patch creates another `JobReporting` row with incremented patch version; replies create reply-only report payloads; empty results mark comments processed without producing an outgoing report.

The tests intentionally check persistence through `aidb.LoadJob`, `aidb.LoadJobReportings`, `aidb.LoadJobComments`, `aidb.LoadBugIDsWithPendingPatch`, and `aidb.RunInTransaction`. They verify `Job.Correct` transitions among unset, true, and false; `Journal` review history ordering; `JobComment.Processed` transitions; and `JobReporting.Version`, `ReportedAt`, and external message links.

## Dependencies and integration points

The suite integrates `dashboard/dashapi`, `dashboard/app/aidb`, `pkg/aflow/ai`, Cloud Spanner emulator context from `NewSpannerCtx`, App Engine mock context, and dashboard UI handlers reached through `GET`, `POSTForm`, and authenticated variants. It also depends on lore-style external report IDs because `JobReporting.ExternalLink` and report command lookup treat `Source: lore` specially.

## Risks and edge cases

The highest-risk behavior is concurrency and idempotency. The tests guard against duplicate upstream commands, duplicate or out-of-order stage transitions, parallel reports for exclusive stages, stale patch-version threads generating reports, and comments arriving while an iteration job is already running. Authorization risk is covered by checking allowed author lists and DKIM before accepting external commands, with failed command attempts journaled so retries are idempotent. Patch-version risk is covered by validating changelog entries and resetting version when a patch is promoted to the next stage.

## Test signals

This file itself is a strong test signal for AI reporting. It asserts complete response payloads, persisted Spanner fields, UI history, authorization errors, and lack of pending reports in terminal states. It also uses mocked time to make debounce/backoff behavior deterministic and uses repeated calls to prove idempotency.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/ai_report_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/ai_test.go -->
# sources/test-tools/syzkaller/dashboard/app/ai_test.go

## Purpose

`ai_test.go` validates the dashboard's AI job creation, polling, namespace authorization, UI actions, trajectory logging, workflow registration, stale job recovery, and manual job creation paths. It sits above the AIDB package and below real external services, using dashboard clients to exercise the API and UI surfaces end to end.

## Important tests and APIs

- `TestAIMigrations` validates Spanner DDL up/down statements are syntax-correct and idempotent.
- `TestAIBugWorkflows` verifies active workflow discovery for bugs based on available agents, workflow type, and agent freshness.
- `TestAIRestrictedClient` and `TestAIJobNamespaces` cover API client restrictions by workflow suffix and namespace allowlists, including trajectory and completion authorization.
- `TestAIJob`, `TestAIAssessmentKCSAN`, `TestAIJobActions`, and `TestAIJobCustomCommit` validate created job args, UI review actions, trajectory spans, finished result handling, and custom base commit propagation.
- `TestAIJobAutoCreate`, `TestAIPendingJobs`, and `TestAIJobParallelPoll` cover automatic job creation, pending workflow fast-path behavior, and transactional duplicate prevention under concurrent polling.
- `TestAIAgentLastActive`, `TestAIAgentRestart`, and `TestAIAgentJobOvertake` validate agent heartbeat, restarted-agent recovery, and stale-job reassignment after inactivity.
- `TestAIManualJobCreate`, `TestAIReproCJobCreateFromBugPage`, `TestAIJobRestart`, and `TestManualAIWorkflows` cover manual UI-created jobs, restart restrictions, and empty manual workflow config behavior.

## Control flow and state behavior

The tests generally create a Spanner-enabled context, upload a build to App Engine datastore, report crashes to create dashboard bugs, then use `AIJobPoll` to register active workflows and claim jobs. When a workflow applies to a bug, a Spanner `Jobs` row is created or claimed and returned as `dashapi.AIJobPollResp` with structured `Args`. The tests verify these args include crash data, repro data, target platform, kernel and syzkaller revisions, and AI base repository settings.

Agent polling persists `Agents.LastActive` and `Workflows` rows. Job claiming updates `Jobs.Started`, `AgentName`, and `CodeRevision`. Completion through `AIJobDone` sets `Finished`, `Error`, and `Results`; UI correctness actions set `Correct` and write journal history. Stale job tests advance mocked time to trigger `NextStaleJob`, which aborts the old job and clones a replacement with equivalent workflow and args.

Manual job creation validates form input before writing jobs without an existing bug. Restart tests only allow failed non-iteration jobs to clone into a fresh job and reject running, successful, public, and patch-iteration restarts.

## Dependencies and integration points

The file uses `aidb` CRUD calls, `dashapi` AI methods, `pkg/aflow/ai` workflow constants, `pkg/aflow/trajectory`, `prog.GitRevision`, App Engine/datastore-backed dashboard helpers, and `errgroup` for concurrent poll validation. It integrates both HTTP UI routes (`/ai_job`, `/ains/ai`, `/bug`) and API methods (`AIJobPoll`, `AIJobDone`, `AITrajectoryLog`).

## Risks and edge cases

Key risks include duplicate job creation under concurrent polling, restricted clients seeing jobs outside their namespace or workflow suffix, stale running jobs never being recovered, and incorrect job args causing agents to work on the wrong source. The tests also cover subtle UI authorization behavior: public users are redirected, regular users can create/review in allowed contexts, and restricted API clients are blocked from trajectory or completion on unauthorized namespaces.

## Test signals

The file is broad regression coverage for AI jobs. It checks both successful and negative paths, uses direct Spanner reads to confirm persisted fields, validates JSON/export output for job pages, and uses concurrent goroutines to verify transactional uniqueness of job assignment.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/ai_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/aidb/crud.go -->
# sources/test-tools/syzkaller/dashboard/app/aidb/crud.go

## Purpose

`aidb/crud.go` is the Spanner persistence layer for dashboard AI agents, workflows, jobs, trajectories, external report state, review journals, report comments, and patch iteration orchestration. It provides typed CRUD helpers and transactional command handlers used by the dashboard API/UI code.

## Important APIs, types, and functions

- Connection and query helpers: `dbClient`, `CloseClient`, `selectAll`, `selectOne`, `readRow`, `RunInTransaction`, `saveEntity`, `selectAllFrom`, and null conversion helpers.
- Agent/workflow APIs: `LoadActiveWorkflows`, `UpdateWorkflows`, `AgentIsAlive`, and `LoadAgent`.
- Job APIs: `CreateJob`, `StartJob`, `NextStaleJob`, `RestartJob`, `LoadNamespaceJobs`, `LoadBugJobs`, `LoadBugIDsWithPendingPatch`, `LoadJob`, and `SetJobDone`.
- Trajectory APIs: `StoreTrajectorySpan` and `LoadTrajectory`.
- Reporting APIs: `AddJobReportingTransactional`, `LoadPendingJobReportingBySource`, `LoadJobReportings`, `LoadBugJobReportings`, `LoadJobReporting`, `LoadJobReportingByExtID`, and `JobReportingPublished`.
- Command APIs: `UpstreamReportCommand`, `RejectReportCommand`, `UnrejectReportCommand`, `LogCommandError`, and `IsCommandProcessed`.
- Comment/iteration APIs: `SaveJobComment`, `LoadJobComments`, `LoadJobCommentsByReporting`, `LoadPendingCommentGroups`, `CreatePatchIterationJob`, `IterationJobDone`, `hasRunningIterationJob`, `isNewestReport`, `checkBackoff`, `getUnprocessedComments`, and `markCommentsProcessedTx`.
- Structured errors: `ErrNotFound`, `ErrDuplicateComment`, `ErrCannotUpstream`, `ErrCannotReject`, `ErrCannotUnreject`, and `ErrNotAuthorized`.

## Control flow and persistence behavior

The file uses Cloud Spanner read-write transactions where uniqueness, correctness, or multi-row state changes matter. `StartJob` selects the oldest unstarted job matching requested workflows and allowed namespaces, then marks it started in the same transaction. `NextStaleJob` first checks whether the same agent has unfinished work, then checks jobs whose assigned agent is inactive past an eight-hour cutoff; it aborts the original job and inserts a cloned replacement.

External reporting commands are journaled transactionally with job correctness changes and optional `JobReporting` creation. `UpstreamReportCommand` refuses rejected jobs, checks no-parallel conflicts when configured, marks the job correct, writes an approve journal row, and optionally inserts a next-stage reporting row. `RejectReportCommand` marks `Correct=false`; `UnrejectReportCommand` clears correctness. Duplicate command insert conflicts are treated as idempotent no-ops.

Patch iteration creation loads the parent reporting, requires unprocessed comments, rejects already running iteration jobs, drains stale threads when a newer report exists, honors exponential backoff after failed iteration jobs, clones parent args, injects `TargetCommentIDs`, and inserts a `WorkflowPatchIteration` job. `IterationJobDone` marks comments processed, checks staleness again, and inserts a new reporting only when the iteration produced a patch or replies.

## State model

Spanner tables are selected via reflected entity fields: `Agents`, `Workflows`, `Jobs`, `TrajectorySpans`, `Journal`, `JobReporting`, and `JobComments`. JSON data is stored in `spanner.NullJSON` with Spanner configured to decode numbers as `json.Number`. Job lifecycle fields are `Created`, nullable `Started`, nullable `Finished`, `Error`, `Aborted`, `Correct`, `Args`, and `Results`. Reporting lifecycle fields are `CreatedAt`, nullable `ReportedAt`, nullable `UpstreamedAt`, `ExtID`, `Version`, `Stage`, and `Source`. Comments are keyed by generated IDs and carry external IDs, author/body metadata, `Processed`, and DKIM verification.

## Dependencies and integration points

The layer depends on `cloud.google.com/go/spanner`, App Engine app IDs for per-app client caching, `dashapi` request/response types, `pkg/aflow/ai` workflow constants, `pkg/aflow/trajectory`, `pkg/email/lore`, and UUID generation. It is consumed by dashboard AI API handlers, UI handlers, and tests. `dbClient` uses a background context so Spanner clients survive request contexts and are keyed by App Engine app ID.

## Risks and edge cases

Important risks include transaction retries returning stale local variables, which the code explicitly handles by resetting `job` inside transaction closures. Reflection-based `selectAllFrom` can silently change SQL column order when entity structs change, so migrations and tests must stay aligned. `SaveJobComment` maps any Spanner `AlreadyExists` to duplicate comment, but generated IDs make true duplicates unlikely unless schema uniqueness includes external IDs. Patch iteration logic has several race points, so stale-report checks are performed both when creating and finishing iteration jobs. `checkBackoff` relies on completed failed jobs being ordered by `Created`, and version increments depend on parent `Version` being valid when prior reports exist.

## Test signals

The behavior is covered primarily by `ai_test.go` and `ai_report_test.go`: migration idempotency, parallel job polling uniqueness, stale/restarted agents, namespace authorization, external report idempotency, no-parallel reporting, comment processing, patch iteration backoff, and stale-thread draining.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/aidb/crud.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/aidb/entities.go -->
# sources/test-tools/syzkaller/dashboard/app/aidb/entities.go

## Purpose

`aidb/entities.go` defines the Cloud Spanner entity structs and workflow/action constants for the AI subsystem. These types are used by `aidb/crud.go` for reflection-based select lists, Spanner struct inserts/updates, and by dashboard UI/API code for display and behavior decisions.

## Important types and constants

- Action constants: `ActionJobReview` (legacy), `ActionApprove`, `ActionReject`, and `ActionUnreject`.
- Workflow filter constants: `WorkflowAll` and `WorkflowNeedsModeration`.
- `ActiveWorkflow`, `Workflow`, and `Agent` model available agent workflows and last active times.
- `Job` models an AI job, including workflow type/name, namespace, bug linkage, external/manual bug ID, display description/link, lifecycle timestamps, code revision, assigned agent, args/results JSON, correctness, abort state, and optional parent reporting.
- `TrajectorySpan` mirrors `trajectory.Span` for storing ordered agent execution traces.
- `Journal` records user or external-source actions, details, errors, source IDs, and reporting linkage.
- `JobReporting` models external report state for a job and stage, including source, publication timestamps, upstream user, external ID, version, and creation time.
- `JobComment` stores external comments tied to a reporting, including subject, author, body URI, timestamp, own-email flag, processing state, and DKIM verification.
- `JobReporting.ExternalLink` converts lore report external IDs into lore thread URLs.

## State and persistence behavior

All structs are plain exported-field records so Spanner's struct mapping can persist and hydrate them. Nullable fields use Spanner null wrapper types to distinguish unset from zero values. `Job.Args`, `Job.Results`, and `Journal.Details` are JSON-valued fields; tests and API code depend on these maps carrying patch diffs, patch metadata, base commit overrides, review details, and iteration targets.

`JobReporting.ExternalLink` is the only behavior method in this file. It returns an empty string if no valid external ID exists, and currently only knows how to construct a link for `dashapi.AIJobSourceLore` using `lore.LinkToThread`.

## Dependencies and integration points

The types depend on `cloud.google.com/go/spanner`, `dashboard/dashapi`, `pkg/aflow/ai`, and `pkg/email/lore`. They are referenced by AIDB CRUD operations, AI API handlers, UI rendering, review history loading, and external report polling/command handling.

## Risks and edge cases

Because `crud.go` builds `SELECT` lists by reflecting visible fields, adding or renaming fields here requires corresponding Spanner schema migration and careful update of tests. The `ExternalLink` method is source-specific; new external integrations will need explicit link support or will display without links. Nullable wrappers must be used consistently to avoid confusing unset correctness, unset publication, and empty string values.

## Test signals

The entity definitions are indirectly covered by Spanner DDL migration tests, AI job tests, reporting tests, and review history assertions. `ExternalLink` behavior is exercised through report UI/link payload expectations where lore external IDs are used.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/aidb/entities.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/api.go -->
# sources/test-tools/syzkaller/dashboard/app/api.go

## Purpose

`api.go` is the main App Engine dashboard API dispatcher and a large set of handlers for syzkaller manager, reporting, bug, build, crash, repro, asset, email, upload, and coverage operations. It also defines authentication/namespace enforcement wrappers that every `/api` method uses.

## Important APIs and functions

- API setup and wrappers: `initAPIHandlers`, `apiHandlers`, `handleJSON`, `handleAPI`, `gcsPayloadHandler`, `nsHandler`, `globalHandler`, `anyHandler`, and `typedHandler`.
- Authentication and context: `APIContext`, `apiContext`, and `checkClient`.
- Build/commit paths: `apiBuilderPoll`, `apiCommitPoll`, `apiUploadCommits`, `addCommitInfo`, `apiUploadBuild`, `uploadBuild`, `addCommitsToBugs`, and manager update helpers.
- Crash/bug paths: `apiReportBuildError`, `apiReportCrash`, `reportCrash`, `saveCrash`, `purgeOldCrashes`, `findExistingBugForCrash`, `findBugForCrash`, `createBugForCrash`, `apiBugList`, `apiLoadBug`, `apiLoadFullBug`, and `loadBugReport`.
- Repro paths: `apiReportFailedRepro`, `saveFailedReproLog`, `saveReproAttempt`, `apiNeedRepro`, `needRepro`, `apiLogToReproduce`, `saveReproTask`, `loadReproTasks`, `takeReproTask`, and `apiReproTaskDone`.
- Text/asset utilities: `putText`, `getText`, `parseIncomingAsset`, `parseCrashAssets`, `apiAddBuildAssets`, and `apiNeededAssetsList`.
- Miscellaneous handlers: `apiManagerStats`, `apiUpdateReport`, `apiSaveDiscussion`, `recordEmergencyStop`, `emergentlyStopped`, `apiCreateUploadURL`, `apiSendEmail`, and `apiSaveCoverage`.

## Control flow and state behavior

`handleAPI` reads `client`, `method`, and `key` form values, derives an OAuth subject from the `Authorization` header, validates the client through `checkClient`, installs an `APIContext`, optionally ungzips the form `payload`, dispatches to `apiHandlers`, and verifies that handlers used the correct namespace wrapper. `nsHandler` rejects global clients for namespace-only methods; `globalHandler` rejects namespace clients for global methods; `anyHandler` marks namespace checking complete for methods allowed in either context.

Build uploads validate string lengths, parse assets, store kernel configs in compressed text entities, put `Build` entities in datastore, update current manager build state, and associate fix commits with bugs. Crash reports are gated by emergency stop, build existence, namespace transforms, canonicalized titles, existing bug lookup, optional new bug creation, crash saving, subsystem inference, and transactional bug counter updates. Text blobs are gzip-compressed and sometimes deduplicated by hash, with large crash logs truncated until compressed data fits datastore limits.

Repro and reporting handlers mutate datastore entities such as `Bug`, `Crash`, `Build`, `Manager`, `EmergencyStop`, `Text`, and `ReproTask`. Coverage upload is the main streaming/GCS path: the handler accepts a GCS URL payload, opens and ungzips the object, decodes JSONL records, and writes to `coveragedb`.

## Dependencies and integration points

The file integrates App Engine datastore, mail, user, and logging APIs; `dashapi` wire types; auth token validation; gzip/JSON payload transport; GCS; coverage database writes; crash asset metadata; subsystem inference; email address merging; syzkaller target metadata; and dashboard config. It is also the central integration point for AI methods registered in `apiHandlers`, although many AI-specific handler bodies live in other files.

## Risks and edge cases

The dispatcher has security-sensitive namespace checking: every handler must go through the correct wrapper or `handleAPI` returns an error. `checkClient` uses constant-time comparisons for API keys and OAuth magic subjects, but method allowlists and namespace lookup must remain correct. Crash reporting has many datastore transaction boundaries; stale reads are rechecked inside transactions for updates. `putText` truncates and recompresses large payloads, which preserves storage limits but can drop leading log data. `takeReproTask` knowingly avoids strict transactional claiming, so duplicate repro attempts are possible but bounded. Emergency stop blocks new crash/job intake but must be consistently checked by handlers that create externally visible work.

## Test signals

`api_test.go` covers credential and namespace enforcement, emergency stop behavior, reporting priority, and upload URL format. `app_test.go` covers end-to-end build/crash/reporting paths, crash purging, failed build manager state, status codes, and linkification. Many additional dashboard test files outside this subset exercise handlers registered in `apiHandlers`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/api_test.go -->
# sources/test-tools/syzkaller/dashboard/app/api_test.go

## Purpose

`api_test.go` focuses on API authentication/authorization helpers, emergency-stop effects, crash reporting priority calculation, and upload URL generation. It provides targeted coverage for security and operational behavior around `api.go`.

## Important tests and covered functions

- `TestClientSecretOK`, `TestClientOauthOK`, `TestClientSecretFail`, and `TestClientSecretMissing` test `checkClient` for API key and OAuth-subject authentication.
- `TestClientNamespaceOK`, `TestClientMethodOK`, `TestClientMethodNotOK`, and `TestClientNamespaceAccess` validate namespace client lookup, method allowlists, and global-vs-namespace wrapper behavior.
- `TestEmergentlyStoppedEmail`, `TestEmergentlyStoppedReproEmail`, `TestEmergentlyStoppedExternalReport`, `TestEmergentlyStoppedEmailJob`, and `TestEmergentlyStoppedCrashReport` test the dashboard's emergency stop behavior across email, repro, external reporting, patch testing jobs, and crash ingestion.
- `TestUpdateReportingPriority` checks `Crash.UpdateReportingPriority` ordering based on revoked/non-revoked repros, title match, manager priority, repository priority, and architecture.
- `TestCreateUploadURL` verifies `apiCreateUploadURL` returns a configured bucket plus UUID-like upload object path.

## Control flow and state behavior

The client tests construct temporary `GlobalConfig` values and call `checkClient` directly, asserting returned namespace and error values. Namespace access tests call real client methods to ensure `nsHandler` and `globalHandler` reject clients in the wrong scope.

Emergency-stop tests create dashboard state, trigger `/admin?action=emergency_stop`, then verify no subsequent email, report, job notification, or bug creation occurs. These tests rely on datastore persistence of `EmergencyStop` and mocked time advancement to trigger scheduled or asynchronous dashboard processing.

Reporting priority tests construct synthetic crashes and call the method directly, then assert priority ordering after compaction. Upload URL tests mutate config with `transformContext` and call the global API client.

## Dependencies and integration points

This file depends on `NewCtx`, test API clients, App Engine test context, `dashapi`, target architecture constants, and testify assertions. It integrates with admin UI actions, email polling helpers, job polling/completion helpers, and the global dashboard config.

## Risks and edge cases

Security regressions in `checkClient` could allow namespace clients to call global methods, global clients to mutate namespace state, or clients to bypass method allowlists. Emergency stop is broad operational safety state; incomplete coverage in handlers could still allow work to leak after stop. Priority scoring uses large additive constants, so future changes could accidentally collapse ordering between repro class, title match, manager priority, and architecture.

## Test signals

The file gives high-signal negative tests for auth and stop behavior. It complements broader end-to-end tests by directly checking error identity (`ErrAccess`), error text for wrapper violations, and exact absence of downstream side effects after emergency stop.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/app.yaml -->
# sources/test-tools/syzkaller/dashboard/app/app.yaml

## Purpose

`app.yaml` is the Google App Engine Standard configuration for the syzkaller dashboard application. It selects the Go runtime, App Engine API compatibility, instance size, inbound mail services, and URL handler routing/security policy.

## Important configuration

- `runtime: go126` selects the Go 1.26 App Engine runtime.
- `app_engine_apis: true` enables legacy App Engine services used by the dashboard code, including datastore, mail, user, and log APIs.
- `instance_class: f4` increases memory relative to `f2`; the comment notes `f2` had soft memory limit crashes.
- `inbound_services` enables `mail` and `mail_bounce`.
- Static handlers serve `/favicon.ico`, `/robots.txt`, and `/static` with `secure: always`.
- Admin-only dynamic handlers cover `/admin`, `/debug/...`, and `/cron/...`.
- `/_ah/mail/...` and `/_ah/bounce` are routed to the app with admin login.
- The catch-all dynamic handler covers root, `/api`, `/bug`, `/text`, `/x/...`, and all other paths with HTTPS required.

## Control flow and integration behavior

Handler order matters: static assets are matched before dynamic catch-all routes, admin/debug/cron routes require admin login, and API/UI/text routes are served by the Go app. The mail routes enable App Engine to deliver inbound email and bounces into registered handlers, which is required by dashboard reporting workflows and tests that simulate incoming email.

## Dependencies and risks

The configuration depends on App Engine Standard semantics for URL handler ordering, login requirements, secure transport, and inbound service names. Misrouting `/api` or `/text` would break manager clients and UI text retrieval. Removing admin protection from debug/cron/admin paths would be a security risk; applying admin login to the catch-all would break public dashboard access and API clients. Reducing instance class could reintroduce memory crashes under request load.

## Test signals

This YAML is not directly unit tested, but the Go test harness depends on equivalent route registration and App Engine API availability. End-to-end tests for API, UI, admin emergency stop, text routes, and email flows provide indirect coverage of the route model represented here.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/app.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/app_test.go -->
# sources/test-tools/syzkaller/dashboard/app/app_test.go

## Purpose

`app_test.go` defines the dashboard test configuration, shared test data builders, and core end-to-end tests for App Engine dashboard behavior. It is foundational test infrastructure for the other files in this subset because it installs `testConfig`, registers namespaces/clients, and provides canonical build/crash factories.

## Important setup, helpers, and tests

- `init` sets App Engine version environment variables, resets mock globals, installs local/test config, and copies local UI namespaces into `testConfig`.
- `testConfig` is a large `GlobalConfig` with ACLs, global clients, namespace clients, reporting configs, AI namespace `ains`, repository configs, managers, subsystem services, coverage config, and access-level test namespaces.
- `testSubsystems`, client/key constants, `skipWithRepro`, `skipWithRepro2`, and `TestConfig` support reporting and subsystem tests.
- `testBuild`, `testCrash`, `testCrashWithRepro`, and `testCrashID` create deterministic `dashapi` objects.
- `TestApp` exercises basic routing, client auth failures, build upload idempotency, namespace isolation, crash reporting, crash purging trigger, failed repro reporting, polling, and reporting update.
- `TestRedirects` and `TestResponseStatusCode` check UI redirect/status behavior.
- `TestPurgeOldCrashes` validates crash retention policy for reported, repro, and non-repro crashes.
- `TestManagerFailedBuild` and helper checks validate manager current build and failed kernel/syzkaller build bug state.
- `TestLinkifyReport` verifies source file/line references in reports are converted to repository links while escaping angle-bracket frames.

## Control flow and state behavior

The initialization path modifies process environment and global dashboard config before tests run. `testConfig` creates multiple namespaces with different access levels and reporting pipelines, so tests can verify cross-namespace isolation and access semantics. The core tests use dashboard clients to write datastore entities through real API handlers, then read bugs, managers, builds, crashes, and report state through test helpers.

Crash retention tests rely on repeated crash reports and mocked time advancement to trigger `purgeOldCrashes`. Manager failed-build tests transition from good builds to failed kernel and syzkaller builds, then back to good builds, verifying manager fields are reset only when the corresponding kernel or syzkaller commit changes. Linkification is a pure text transformation test but protects UI rendering of crash reports.

## Dependencies and integration points

This file depends on `dashapi`, `pkg/auth`, `pkg/subsystem`, subsystem list registration, `targets`, App Engine user APIs, and broad dashboard globals. Its config is used by `api_test.go`, `ai_test.go`, and `ai_report_test.go`, especially namespace `ains` with AI base repository settings and AI-capable clients.

## Risks and edge cases

Because `testConfig` is global and mutable through `transformContext`/`SetAIConfig`, tests must isolate contexts and avoid leaking config mutations. The `init` environment workaround is necessary to prevent metadata fetch hangs in local tests; removing it could make the whole package hang or panic. The large config can mask missing production config validation unless `checkConfig` stays strict. Crash purging is sensitive to reported crash preservation, repro-level buckets, manager/title uniqueness, and text blob deletion.

## Test signals

This file is both infrastructure and regression coverage. Passing tests signal that the dashboard can register handlers, authenticate clients, isolate namespaces, ingest builds/crashes, update reporting state, enforce access redirects/statuses, purge old crash data without deleting important reports, track failed builds, and linkify source locations correctly.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/app_test.go -->
