# Research: subset-b-009393

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/entities_datastore.go -->
# sources/test-tools/syzkaller/dashboard/app/entities_datastore.go

## Purpose
`entities_datastore.go` is the dashboard datastore model layer. It defines the App Engine datastore entities used by managers, builds, bugs, crashes, reports, jobs, text blobs, subsystem reports, discussions, and reproduction tasks, plus key construction, loading, migration, and small domain helpers shared across dashboard flows.

## Important APIs, Types, And Functions
Core entity structs are `Manager`, `ManagerStats`, `Build`, `Bug`, `Crash`, `BugReporting`, `Job`, `Text`, `ReproTask`, `SubsystemReport`, `Discussion`, and `EmergencyStop`. Important enum-like constants include bug statuses, `BuildType`, `JobType`, text entity kind names, and `BisectStatus`.

Key helpers include `mgrKey`, `buildKey`, `Bug.key`, `bugKeyHash`, `loadManager`, `updateManager`, `loadBuild`, `lastManagerBuild`, `loadBuilds`, `loadBug`, `canonicalBug`, `loadSimilarBugs`, `addCrashReference`, `removeCrashReference`, and `runInTransaction`. `dependencyLoader[T]` batches unique datastore key loads and fans the loaded entities back into callbacks.

## Control Flow
Most flows start by constructing deterministic keys from namespace/config data, loading entities, applying domain transforms, then writing entities through transactions when state can race. `updateManager` loads or initializes both a manager and the current-day `ManagerStats` under a manager ancestor, calls a caller-provided mutator, and writes both. `updateSingleBug` and `runInTransaction` centralize bug updates and retry behavior.

`Bug.Load` strips legacy `Tags.*` properties, loads the modern struct, converts legacy subsystem tags into `BugLabel` entries, and backfills `HeadReproLevel` when older entities lack the field. `Crash.Load` converts legacy `Reported` state into a reference entry so newer ref-counted reporting logic can safely clear individual references.

## State And Persistence
Entities are persisted in Google App Engine datastore. `Build` keys are hashes of namespace and build ID; `Bug` keys are hashes of namespace config key, namespace, title, and sequence. `Crash` and `Job` entities are children of `Bug`; `ManagerStats` is a child of `Manager`. Large mutable blobs are stored as `Text` entities referenced by integer IDs.

Bug state combines lifecycle fields (`Status`, `Closed`, `FixTime`, `LastActivity`), reproducer fields (`ReproLevel`, `HeadReproLevel`, `ReproAttempts`), reporting slots, fixing commit metadata, subsystem/label data, daily crash history, tree-test state, and AI job queue hints. Crash state stores report/log/repro references, parsed report elements, report references, asset metadata, and repro revocation state.

## Dependencies And Integration Points
The file depends on `dashapi` for API enum/value compatibility, `pkg/hash` for stable key IDs, `pkg/subsystem` for subsystem labels, App Engine datastore, and dashboard config helpers such as `getNsConfig`. It is directly consumed by upload/reporting/job/graph/UI code and by tests via `Ctx` helpers.

## Risks
Schema migration hooks in `Bug.Load` and `Crash.Load` are easy to break because they must preserve behavior for old datastore rows. Hash key generation depends on namespace config keys, so config key changes can orphan data. `canonicalBug` follows duplicate chains without explicit cycle protection. `runInTransaction` contains a test-only emulator retry workaround that can mask emulator pressure but not production transaction failure. `BugDailyStats` trimming preserves only five years of history.

## Test Signals
`entities_datastore_test.go` directly validates old subsystem tag conversion. Wider coverage comes from job, reporting, fix, graph, subsystem, and app tests that persist and reload bugs, crashes, jobs, builds, labels, text blobs, and manager stats.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/entities_datastore.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/entities_datastore_test.go -->
# sources/test-tools/syzkaller/dashboard/app/entities_datastore_test.go

## Purpose
This test file protects backward compatibility for datastore `Bug` loading after subsystem labels moved from legacy `Tags.Subsystems` properties to the unified `Bug.Labels` representation.

## Important APIs, Types, And Functions
The only test is `TestOldBugTagsConversion`. It constructs an anonymous legacy bug struct with `Namespace`, `Title`, and `Tags BugTags202304`, serializes it with `db.SaveStruct`, then loads those properties through `Bug.Load`.

## Control Flow
The test writes two legacy subsystem tag entries, one user-set and one automatic. It then calls the modern `Bug.Load` path and compares the whole resulting `Bug` struct with the expected modern value using `require.Equal`.

## State And Persistence Behavior
No live datastore instance is used. The test exercises datastore property serialization/deserialization in memory, which is enough to verify that properties named under `Tags.` are filtered out of the normal load path, parsed through the legacy structs, and appended to `Labels`.

## Dependencies And Integration Points
It depends on the App Engine datastore property API, `BugTags202304`, `BugTag202304`, `Bug.Load`, `BugLabel`, and `SubsystemLabel`.

## Risks
The test only covers subsystem tag migration, not the `HeadReproLevel` backfill path in `Bug.Load` or crash reference migration in `Crash.Load`. It also uses full struct equality, so new default-valued `Bug` fields generally do not disturb it, but non-zero defaults added to `Load` could require test updates.

## Test Signals
This is a focused regression signal: legacy `Tags.Subsystems` entries with `Name` and optional `SetBy` must become `BugLabel{Label: SubsystemLabel, Value: Name, SetBy: SetBy}`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/entities_datastore_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/entities_spanner.go -->
# sources/test-tools/syzkaller/dashboard/app/entities_spanner.go

## Purpose
`entities_spanner.go` contains the dashboard's Spanner-backed coverage history entity model and aggregation query. It complements datastore entities with coverage data stored in Cloud Spanner via the syzkaller coverage database abstraction.

## Important APIs, Types, And Functions
`CoverageHistory` stores merged coverage as maps keyed by date string: `instrumented`, `covered`, and the set of accepted `coveragedb.TimePeriod` values. `MergedCoverage(ctx, client, ns, periodType)` is the main API. It resolves min/max duration and period validation operations for the requested period type, runs a Spanner SQL aggregation, validates periods, and returns the merged history.

## Control Flow
`MergedCoverage` calls `coveragedb.MinMaxDays` and `coveragedb.PeriodOps`, constructs a parameterized statement joining `merge_history` and `files`, filters by namespace, duration range, and synthetic manager `'*'`, then groups by target date and duration. It iterates rows, converts each row to a local struct, constructs a `TimePeriod`, skips periods rejected by the period ops, and records summed instrumented/covered counts. Duplicate valid periods for the same date/duration are treated as a database consistency error.

## State And Persistence Behavior
The function is read-only against Spanner. It does not mutate Spanner or datastore. The returned state is in-memory and intentionally keyed by `civil.Date.String()` for graph/report consumers that work at date granularity.

## Dependencies And Integration Points
It depends on `spannerclient.SpannerClient`, `cloud.google.com/go/spanner`, `civil.Date`, `coveragedb`, and `iterator.Done`. It is likely consumed by coverage UI/reporting code that needs namespace-level merged coverage over daily/weekly/monthly periods.

## Risks
The SQL string uses positional placeholders while parameters are populated as `p1`, `p2`, and `p3`; this is correct for the Spanner client style in use but fragile if rewritten. Duplicate period detection is strict and can turn unexpected database shape into user-visible errors. The aggregation stores one value per date string, so if multiple valid durations for the same target date are allowed by a future period type, the maps would overwrite even before duplicate-period detection catches same-date/same-duration duplicates.

## Test Signals
There is no dedicated test in this subset. Coverage-related tests elsewhere use Spanner mock clients; key test needs are query row parsing, invalid period filtering, duplicate-period errors, and min/max duration failures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/entities_spanner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/fix_test.go -->
# sources/test-tools/syzkaller/dashboard/app/fix_test.go

## Purpose
`fix_test.go` is an integration-style regression suite for the dashboard's fixed-bug lifecycle. It verifies how manual fix commits and build-reported `Reported-by` fix tags propagate through pending builder commits, multi-manager closure, duplicate bugs, and creation of follow-up bug sequences.

## Important APIs, Types, And Functions
Tests use `NewCtx`, API clients, `UploadBuild`, `ReportCrash`, `BuilderPoll`, `NeedRepro`, `ReportingUpdate`, and helper methods such as `pollBug`, `updateBug`, and `loadBug`. The covered behavior is implemented outside this file, but important state surfaces are `Bug.Commits`, `Bug.CommitInfo`, `Bug.NeedCommitInfo`, `Bug.FixTime`, `Bug.LastActivity`, `Bug.PatchedOn`, manager build commit lists, and `dashapi.Commit.BugIDs`.

## Control Flow
The tests start by uploading builds and crashes, polling the bug report, marking fixes through reporting updates or build fix tags, then checking builder poll responses and subsequent crash deduplication. A bug is considered fixed only when all relevant managers have observed all required fixing commits. When a fixed bug reproduces again, the dashboard creates a new bug sequence with the display title suffix `(2)`.

## State And Persistence Behavior
Manual fix updates store commit titles on the bug and reset patching state so builders receive pending commits until their builds include them. Multi-manager tests ensure the bug remains open while any manager that has seen the bug has not picked up the fix. Duplicate tests ensure fixes reported against duplicate IDs are associated with canonical bugs and, after unduplication, can also close non-canonical bugs.

## Dependencies And Integration Points
This suite integrates reporting APIs, builder polling, crash ingestion, duplicate handling, bug sequencing, and build upload fix tag parsing. It relies on datastore persistence through the test App Engine context.

## Risks
The area is race-prone because fix state can arrive from users, from commit tags in builds, and from duplicate/canonical bug transitions. The tests document current behavior that upstreaming a bug with existing fix commits fails. Multi-manager logic can regress if `PatchedOn` or `HappenedOn` semantics change. Duplicate fix propagation must avoid livelock when both dup and canonical IDs appear in fix tags.

## Test Signals
Coverage includes single-commit fixes, two-commit fixes, re-fixing with a different commit, LastActivity/FixTime semantics, two-manager propagation, commit-tag-driven fixes, and three duplicate scenarios.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/fix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/graphs.go -->
# sources/test-tools/syzkaller/dashboard/app/graphs.go

## Purpose
`graphs.go` implements UI data preparation for dashboard graph pages: kernel health, bug lifetimes, found bugs per month, manager fuzzing metrics, and crash statistics. It converts datastore entities into simple `uiGraph` structures consumed by HTML templates.

## Important APIs, Types, And Functions
UI structs include `uiGraph`, `uiGraphHeader`, `uiGraphColumn`, `uiGraphValue`, `uiManagersPage`, `uiCrashesPage`, and crash/lifetime table structs. HTTP handlers are `handleKernelHealthGraph`, `handleGraphLifetimes`, `handleFoundBugsGraph`, `handleGraphFuzzing`, and `handleGraphCrashes`. Data builders include `loadGraphBugs`, `loadStableGraphBugs`, `isStableBug`, `createBugsGraph`, `createFoundBugs`, `createBugLifetimes`, `createManagersGraph`, `extractMetric`, `createCrashesTable`, and `createCrashesGraph`.

## Control Flow
Handlers call `commonHeader`, load namespace-scoped bugs or manager stats, create UI filters from form data, and render templates. Bug graph loading filters unreleased bugs, auto-obsoleted invalid bugs, and duplicate fixing commits for health graphs. Stable found-bug graphs preserve more historical records by using `isStableBug`. Manager graphs prefill a date grid, load child `ManagerStats` per selected manager, fill selected metrics, and normalize values when multiple metrics are displayed. Crash graphs build day buckets, compile user regexps, count matching crash titles, and convert counts to percentages of all crashes for the day.

## State And Persistence Behavior
The file is read-only. It queries datastore `Bug`, `Job`, and `ManagerStats` entities, derives graph/table values in memory, and writes no persistent state. Form state is reflected in UI structs but not stored.

## Dependencies And Integration Points
It depends on `commonHeader`, `serveTemplate`, bug/reporting helpers, `managerList`, datastore, namespace config, `pkg/report/crash` title classification, and the HTML templates named by each handler.

## Risks
User-provided regexps can be expensive or invalid; invalid regexps return errors, and the manager metric checkbox explicitly rejects unknown values. `createFoundBugs` computes current-month projection by dividing by elapsed month duration, which assumes `now` is after the first instant of the month. `createManagersGraph` normalization appears to divide by `maxVal * 100`, which may make normalized values unexpectedly small if the intended range is 0..100. Several graph tests only verify handlers return OK, not visual/content correctness.

## Test Signals
`graphs_test.go` exercises graph endpoints with populated manager stats/crashes and verifies bad metric selector input becomes a bad request. More precise assertions would be useful for graph values, regex handling, and projection math.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/graphs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/graphs_test.go -->
# sources/test-tools/syzkaller/dashboard/app/graphs_test.go

## Purpose
`graphs_test.go` verifies that dashboard graph endpoints can render from realistic test data and that fuzzing metric query parameters reject malformed values.

## Important APIs, Types, And Functions
`TestManagersGraphs` populates builds, manager stats, crashes, and email/reporting state before requesting `/graph/bugs`, `/graph/lifetimes`, `/graph/fuzzing`, `/graph/crashes`, and `/graph/found-bugs`. `managersGraphFixture` creates a smaller fixture for metric validation. `TestManagersGraph_FuzzingMetric_OK_OnValidInput` and `TestManagersGraph_FuzzingMetric_BadRequest_OnMalformedInput` target `createCheckBox` validation through the HTTP route.

## Control Flow
The main test uploads two builds, records several days of manager stats, advances mocked time, reports crashes, drains reporting emails, and performs authenticated admin GETs against graph endpoints. The security/regression tests request the fuzzing graph with a valid `Metrics=MaxCorpus` selector and then with an injection-like malformed metric selector.

## State And Persistence Behavior
The tests use the App Engine test datastore through `NewCtx`. Manager stats are persisted as child `ManagerStats` entities by upload APIs; crash and bug history are persisted through crash reporting; graph handlers then query that persisted state.

## Dependencies And Integration Points
The tests integrate API upload endpoints, email/reporting cron, authentication helpers, graph handlers, manager stats persistence, and bad-request handling.

## Risks
Most endpoint checks contain TODO comments and do not assert response content, so graph shape regressions can pass as long as handlers return success. The bad metric test is valuable because selector validation prevents arbitrary form values from reaching `extractMetric`, where unknown metrics panic.

## Test Signals
Signals are liveness and validation rather than exact graph correctness: all graph pages must render for admin users with realistic data; known metrics must be accepted; malformed metric values must produce a bad request.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/graphs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/handler.go -->
# sources/test-tools/syzkaller/dashboard/app/handler.go

## Purpose
`handler.go` provides common HTTP middleware and UI helpers for dashboard routes: context wrapping, access checks, throttling/backpressure, template serving, common page headers, namespace cookies, client-facing errors, redirects, and buffered gzip response handling.

## Important APIs, Types, And Functions
Key entry points are `handlerWrapper`, `handleContext`, `handleAuth`, `serveTemplate`, `commonHeaderRaw`, `commonHeader`, `decodeCookie`, `encodeCookie`, and `newGzipResponseWriterCloser`. Error types are `ErrClient` and `ErrRedirect`, with predefined `ErrClientNotFound` and `ErrClientBadRequest`. Throttling helpers are `isRobot`, `backpressureRobots`, `throttleRequest`, and `throttlingErrorMessage`.

## Control Flow
`handlerWrapper` composes access checking and context/error handling. `handleContext` stores the current URL in context, throttles unauthenticated users, adds robot backpressure after handler completion, sets HTML content type, writes handler output into a gzip buffer, and only flushes the compressed or decompressed response if the handler succeeds. On errors it handles access redirects, explicit redirects, client/internal status mapping, logging, and `error.html` rendering.

`commonHeader` determines namespace from the route or cookie, filters namespace choices by access level and decommissioned state, redirects to a valid namespace when needed, populates namespace-specific header fields, persists the namespace cookie, and loads cached bug stats.

## State And Persistence Behavior
The file does not directly persist datastore entities, but it writes a long-lived `syzkaller` cookie containing base64-encoded JSON with the selected namespace. It also invokes throttling/cache layers that may have their own persistence outside this file.

## Dependencies And Integration Points
It depends on App Engine user/log APIs, dashboard access/config/cache helpers, `pkg/html` template globbing, standard `gzip`, JSON/base64, and every UI handler that uses `contextHandler`.

## Risks
Because output is buffered, handlers that call `WriteHeader` before returning errors can still interact subtly with final error rendering. `Accept-Encoding` is checked with substring matching. Non-gzip responses larger than the App Engine limit produce a client bad-request error after full handler work has already completed. Cookie decode silently ignores malformed values. Throttling relies on headers that may be unavailable in local or proxy contexts.

## Test Signals
`handler_test.go` specifically validates gzip response behavior, including decompression, compression headers, header forwarding, and status preservation. Broader route/auth behavior is covered by app/main tests outside this subset.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/handler_test.go -->
# sources/test-tools/syzkaller/dashboard/app/handler_test.go

## Purpose
`handler_test.go` tests the `gzipResponseWriterCloser` adapter used by UI middleware to buffer compressed responses and conditionally serve gzip or plain output.

## Important APIs, Types, And Functions
Tests cover `newGzipResponseWriterCloser`, `Write`, `Header`, `WriteHeader`, `writeResult`, and the helper `httpRequestWithAcceptedEncoding`.

## Control Flow
The no-compression test writes `test`, calls `writeResult` with no accepted encoding, and expects a plain body and no `Content-Encoding`. The compression test writes the same payload, requests gzip, checks the gzip header, and manually decompresses the recorded body. Header and status tests verify that wrapper header mutations and status codes are forwarded to the underlying recorder.

## State And Persistence Behavior
No persistent state is involved. The test uses `httptest.ResponseRecorder` and in-memory gzip buffers.

## Dependencies And Integration Points
It depends on standard `compress/gzip`, `net/http`, `httptest`, and `testify/assert`. Its integration point is `handleContext`, which uses this response writer for successful UI responses.

## Risks
The test reads a fixed-size decompression buffer and ignores read errors, which is sufficient for the short payload but less robust for larger payloads. It does not test oversized plain responses, close idempotency, or error paths from invalid gzip buffers.

## Test Signals
The adapter must preserve semantic response content for both gzip and non-gzip clients, propagate headers, and not lose explicit status codes.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/handler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/index.yaml -->
# sources/test-tools/syzkaller/dashboard/app/index.yaml

## Purpose
`index.yaml` declares the composite App Engine datastore indexes required by the dashboard's non-trivial queries. It is operational infrastructure for entity queries across bugs, builds, crashes, discussions, jobs, repro tasks, assets, labels, subsystems, and AI workflow state.

## Important Index Groups
Bug indexes cover namespace/status, happened-on manager membership, status plus happened-on plus commits, title/sequence ordering, merged/alternate title lookup, closed status, commit-info polling, bisection candidate selection by repro and time, subsystem refresh by time/revision, labels (`Labels.Label`, `Labels.Value`, `Status`), fix-candidate jobs, and AI job check/pending workflows.

Build indexes cover namespace/manager lookups, build type ordered by time, asset deprecation scans by asset type/create date, and namespace asset last-check scans. Crash indexes are ancestor indexes under `Bug`, supporting report/repro filters and priority/time ordering. Job indexes cover pending job polling, completed unreported jobs, recent finished jobs, ancestor job type histories, and namespace/type views. ReproTask indexes support manager/namespace queues.

## Control Flow And Integration
There is no executable control flow. The file must match query shapes in Go code. For example, `jobs.go` pending job polling requires `Finished`, `IsRunning`, `Attempts`, `Created`; bisection queries require repro/status/time combinations; graph and manager pages require manager stats and bug filters; discussion lookup requires source plus message ID.

## State And Persistence Behavior
The indexes define how datastore maintains query acceleration structures for persisted entities. They do not define entity schemas, but missing or stale indexes can break production queries even when tests pass in local emulators.

## Dependencies And Integration Points
This file is consumed by App Engine deployment tooling. It is tightly coupled to datastore filters and ordering in `entities_datastore.go`, `jobs.go`, reporting, asset storage, subsystem, main UI, AI, and discussion code.

## Risks
Index drift is the major risk: changing a query filter/order without updating this file can cause runtime query failures in App Engine. Duplicate-looking build indexes exist and should be treated carefully because historical deployment/index state may depend on them. Composite indexes on repeated properties such as `Commits`, `HappenedOn`, labels, and assets can have write amplification implications.

## Test Signals
Local tests exercise many query shapes but may not faithfully enforce all production index requirements. Deployment/index validation is the real signal for this file.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/index.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/jobs.go -->
# sources/test-tools/syzkaller/dashboard/app/jobs.go

## Purpose
`jobs.go` implements dashboard job orchestration for syz-ci: user-requested patch tests, automatic reproducer retests, cause/fix bisections, tree-origin/cross-tree jobs, job polling/reset/done APIs, result reporting, invalidation, and backport tracking.

## Important APIs, Types, And Functions
Request structs are `testReqArgs` and `testJobArgs`. Core creation APIs are `handleTestRequest`, `addTestJob`, `saveJob`, `patchTestJobArgs`, `checkTestJob`, `createBisectJob`, `createBisectJobForBug`, and retest/tree job helpers. Polling/completion APIs are `pollPendingJobs`, `getNextJob`, `loadPendingJob`, `createJobResp`, `resetJobs`, and `doneJob`. Reporting APIs include `pollCompletedJobs`, `createBugReportForJob`, `bisectFromJob`, and `jobReported`. Utility APIs include `invalidateBisection`, `activeManager`, `extJobID`, `jobID2Key`, `makeJobInfo`, `queryBugJobs`, and backport helpers.

## Control Flow
Patch test requests validate blocklists, locate a representative crash, fill missing repo/branch from the crash build, validate repro/repo/branch/status constraints, store patch/config text, deduplicate by email `ExtID`, create a child `Job`, and add a crash reference. Job polling first returns already pending jobs matching a manager's declared capabilities. If none are pending, it throttles generation per manager and alternates between sampled bug jobs and bisection creation.

`createJobResp` loads patch, crash, build, config, and repro data, then transactionally marks the job running and increments attempts before returning a `dashapi.JobPollResp`. `doneJob` reloads the job, optionally updates retested repro state, stores result text blobs and build data, copies commit metadata, updates bisection state, saves the job/bug in an XG transaction, then runs post-job tree/cross-tree handlers.

## State And Persistence Behavior
Jobs are datastore children of bugs. They reference `Text` blobs for patches, logs, errors, reports, and configs. Job state transitions through pending (`Finished` zero, `IsRunning` false), running (`IsRunning` true, attempts/started set), finished (`Finished` set, result fields populated), and reported (`Reported` true). Bisection jobs also mutate bug `BisectCause`, `BisectFix`, `LastCauseBisect`, `FixCandidateJob`, and sometimes fixing commits.

## Dependencies And Integration Points
The file integrates with dashapi job/reporting endpoints, email parsing/reporting, datastore, namespace manager config, build/crash/text storage, tree-origin and cross-tree code, reporting pipelines, VCS validation/linking, and access/UI job info.

## Risks
This is high-concurrency code: polling, resets, duplicate email delivery, and job completion can race. Datastore transaction group restrictions force some reads outside transactions. Generated job throttling mutates the input manager map by dropping managers. `loadPendingJob` delays bisection retries for three days based on both creation and last start, which can surprise operations. `doneJob` rejects duplicate completion and relies on post-job handlers after the transaction. `jobID2Key` trusts the external ID shape. Bisection reporting intentionally suppresses unreliable or non-single-commit results.

## Test Signals
`jobs_test.go` extensively covers patch testing, malformed requests, blocklists, duplicate emails, external jobs, no-patch jobs, restricted managers, retest repro revocation, delegated managers, bisection timing/retries, reset/re-poll behavior, already-fixed suppression, and alias repo resolution. Bisect/tree tests outside this subset cover adjacent post-job paths.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/jobs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/jobs_test.go -->
# sources/test-tools/syzkaller/dashboard/app/jobs_test.go

## Purpose
`jobs_test.go` is the primary integration test suite for job lifecycle behavior, covering email-triggered and external patch tests, syz-ci polling/completion, bisection creation and retry rules, reproducer retesting, manager delegation, reset handling, and job result reporting.

## Important APIs, Types, And Functions
Tests use `sampleGitPatch`, `syzTestGitBranchSamplePatch`, `NewCtx`, API clients, email fixtures, `pollJobs`, `pollSpecificJobs`, `JobDone`, `JobReset`, `NewTestJob`, `ReportingPollBugs`, `ReportingUpdate`, and datastore inspection helpers such as `loadJob` and `loadBug`.

## Control Flow
The main `TestJob` walks through a full email patch-test lifecycle: reject no-repro crashes, accept boot/test error exceptions, reject malformed repo/branch input, block listed users, deduplicate by message ID, poll a job, complete it with crash/error/success variants, and verify generated email bodies and text links. Other tests isolate no-patch commit tests, external API-created jobs, parallel job polling and reset, bisection timing, fix-bisection retry, and cause-bisection infra retry.

## State And Persistence Behavior
Tests populate datastore via upload/reporting APIs and assert persistent job/build/bug state through follow-up polls and direct loads. They verify `IsRunning` behavior via parallel job tests and reset, `HeadReproLevel` changes after retests, fix bisection state transitions, and that completed jobs are not reissued.

## Dependencies And Integration Points
The suite spans email command handling, reporting stages, builder/build upload, text blob links, bisection logic, manager config, decommissioned manager delegation, and external dashboard API methods. It also uses the fake email sink as a reporting oracle.

## Risks
The tests are intentionally broad and can be sensitive to exact email text. Several behaviors are time-dependent and use mocked time advances for reporting windows and retry freezes. Because they are integration-style, failures may require tracing through email/reporting/build/job code rather than this file alone.

## Test Signals
Strong signals include bad request text, job poll payload fields, text link content, no unexpected emails, retry/no-retry timing, `JobReset` reissuing running jobs, and reporting suppression when a bug is already fixed.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/jobs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/kcidb.go -->
# sources/test-tools/syzkaller/dashboard/app/kcidb.go

## Purpose
`kcidb.go` publishes eligible dashboard bugs to KCIDB through a cron handler. It scans configured namespaces and exports public, reported kernel bug reports while marking each bug's KCIDB publication status.

## Important APIs, Types, And Functions
`initKcidb` registers `/cron/kcidb_poll`. `handleKcidbPoll` iterates namespace configs with `Kcidb` settings. `handleKcidbNamespce` creates a `kcidb.Client`, scans open bugs, and caps publications at 30 per run. `publishKcidbBug` applies eligibility checks, loads a `dashapi.BugReport`, publishes it when required fields exist, and updates `Bug.KcidbStatus`.

## Control Flow
The cron handler creates an App Engine context, loops over namespaces, and logs namespace-level failures without aborting other namespaces. For each namespace, the code queries open bugs, calls `publishKcidbBug`, increments the local reported count only when an actual publish happened, and stops publishing after 30 successful publishes.

## State And Persistence Behavior
The code mutates `Bug.KcidbStatus` in datastore: `1` means published, `2` means intentionally not published because the report lacked critical publishable data such as kernel commit/config. Bugs with non-zero status are skipped on future runs. Publishing itself is external side effect through the KCIDB REST client.

## Dependencies And Integration Points
It depends on `pkg/kcidb`, namespace `KcidbConfig`, bug scanning helpers, access sanitization, reporting state, `loadBugReport`, datastore transactions, and App Engine cron routing.

## Risks
The function name `handleKcidbNamespce` contains a typo but is internally consistent. Eligibility logic combines access, final reporting, open/stale closed state, and report completeness, so changes in reporting semantics can affect KCIDB exports. Marking incomplete reports with status `2` prevents retry if missing data becomes available later. External publish succeeds before datastore status update, so transaction failure may cause duplicate publish attempts later.

## Test Signals
No direct tests are in this subset. Useful coverage would mock `kcidb.Client`, exercise eligibility branches, enforce the 30-publish cap, and verify status transitions for publishable and non-publishable reports.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/kcidb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/label.go -->
# sources/test-tools/syzkaller/dashboard/app/label.go

## Purpose
`label.go` defines dashboard bug labels, validation rules, help rendering, and mutation/query helpers. Labels support priority, subsystems, reminders, origin/backport state, race classification, and AI/actionability metadata.

## Important APIs, Types, And Functions
Label constants include `SubsystemLabel`, `PriorityLabel`, `NoRemindersLabel`, `OriginLabel`, `MissingBackportLabel`, `RaceLabel`, and `ActionableLabel`. Priority values are `LowPrioBug`, `NormalPrioBug`, and `HighPrioBug`. Rule marker types are `oneOf`, `subsetOf`, and `trueFalse`. Important methods include `makeLabelSet`, `labelSet.FindLabel`, `labelSet.ValidateValues`, `labelSet.Help`, `Bug.HasLabel`, `Bug.LabelValues`, `Bug.SetLabels`, `Bug.UnsetLabels`, `Bug.HasUserLabel`, `Bug.prio`, and `BugPrio.LessThan`.

## Control Flow
`makeLabelSet` builds allowed labels dynamically from bug title and namespace config. KCSAN data-race titles enable race labels. Namespaces with subsystem services allow subsystem subsets. Repositories with origin labels add allowed origin values. `SetLabels` requires all provided values to share one label type, validates them, removes existing labels of that type, and appends the new values.

## State And Persistence Behavior
Labels are stored on `Bug.Labels` as repeated `BugLabel` structs. `SetBy` distinguishes user labels from automatic labels and is used to avoid overwriting user subsystem choices. `UnsetLabels` returns the requested label names that were not found, which callers can use for feedback.

## Dependencies And Integration Points
It depends on namespace config, subsystem service lists, `pkg/report/crash` title classification, `subsystemListURL`, and helper functions from the datastore entity file. Reporting, subsystem reminders, Linux reporting, tree-origin, and UI filters consume these labels.

## Risks
Unknown labels return no validation error because `ValidateValues` returns empty when no rules exist; callers must use `FindLabel` where strict label existence matters. `Bug.prio` trusts stored priority label values and can map unknown values to zero ordering. `writeWrapped` uses byte length, not display width, which is acceptable for current ASCII label help.

## Test Signals
No dedicated tests are in this subset. Label behavior is indirectly exercised by subsystem, Linux reporting, tree-origin, and UI tests.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/label.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/linux_reporting.go -->
# sources/test-tools/syzkaller/dashboard/app/linux_reporting.go

## Purpose
`linux_reporting.go` collects small Linux-specific reporting helpers that would otherwise live in configuration: identifying likely VFS/filesystem bugs and suppressing low-value monthly reports.

## Important APIs, Types, And Functions
`canBeVfsBug(bug *Bug)` checks subsystem label values and treats both legacy `"vfs"` and current `"fs"` as VFS-compatible. `isWorthMonthlyReport(bugs []*Bug)` returns true when at least one bug title does not start with `INFO:`.

## Control Flow
Both functions are simple scans. `canBeVfsBug` iterates `bug.LabelValues(SubsystemLabel)` and returns on the first `vfs` or `fs` value. `isWorthMonthlyReport` iterates the bug list and returns true on the first non-INFO title; empty or all-INFO lists return false.

## State And Persistence Behavior
The file is read-only. It uses labels already stored on bugs and does not mutate bug/reporting state.

## Dependencies And Integration Points
It depends on `Bug.LabelValues`, `SubsystemLabel`, and standard string prefix matching. It integrates with Linux namespace reporting filters and monthly subsystem/reporting decisions.

## Risks
The VFS test is label-name based and depends on subsystem extraction accuracy. The monthly report heuristic is intentionally simple: any title that does not literally start with `INFO:` makes a report worthwhile, so whitespace or differently cased prefixes are not suppressed.

## Test Signals
`linux_reporting_test.go` validates filesystem/VFS reporting flow and `isWorthMonthlyReport` truth table behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/linux_reporting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/linux_reporting_test.go -->
# sources/test-tools/syzkaller/dashboard/app/linux_reporting_test.go

## Purpose
`linux_reporting_test.go` verifies Linux filesystem reporting policy: possible VFS bugs can be delayed until reproducers provide better filesystem-specific subsystem attribution, and monthly reports are skipped when all bugs are informational.

## Important APIs, Types, And Functions
`TestFsSubsystemFlow` covers non-fs, specific filesystem, and possible VFS bugs that later get a mount-image reproducer. `TestVfsSubsystemFlow` covers possible VFS bugs with reproducers that do not identify a narrower filesystem. `TestIsWorthMonthlyReport` is a table test for `isWorthMonthlyReport`.

## Control Flow
The flow tests create a filesystem-configured context, upload a build, report crashes with guilty files and maintainers, inspect outgoing email/reporting behavior, then report additional repro crashes. For the VFS-delayed case, the bug is first held in an earlier stage, then a reproducer triggers notification/upstreaming, and the email subject/recipients are checked for either a specific filesystem (`ntfs3`) or generic `fs`.

## State And Persistence Behavior
The tests persist builds, crashes, bugs, labels, reporting state, and email notifications in the test context. They verify that bug state can remain pending until repro data updates subsystem labels and reporting readiness.

## Dependencies And Integration Points
They integrate crash guilty-file parsing, subsystem services, syz repro analysis, reporting filters, email recipient selection, notification polling, and the Linux helper functions.

## Risks
These tests are sensitive to subsystem database/config content and expected maintainer lists. They assert exact email subjects and recipient sets, which is useful for policy stability but can require updates when subsystem metadata changes.

## Test Signals
Signals include immediate reporting for non-fs bugs, correct nilfs recipients, delayed VFS reporting without repro, specific filesystem extraction from `syz_mount_image$ntfs3`, fallback to `[fs?]`, and monthly report suppression for all-INFO lists.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/linux_reporting_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/local_ui_test.go -->
# sources/test-tools/syzkaller/dashboard/app/local_ui_test.go

## Purpose
`local_ui_test.go` is a developer fixture and optional local server for manually exploring the dashboard UI with realistic synthetic data, including bugs, builds, crashes, fixed bugs, manual repro tasks, and AI job/trajectory/report flows.

## Important APIs, Types, And Functions
Flags are `-local-ui`, `-local-ui-addr`, and `-local-ui-user`. `TestLocalUI` initializes a Spanner-capable test context, installs `localUIConfig`, populates data, and optionally serves the app. `populateBuildsAndCrashes`, `populateLocalUIDB`, and `tickRandom` generate fixture data. `localUIConfig` defines one public Linux namespace with email reporting, AI config, repository metadata, and test clients.

## Control Flow
When `-local-ui` is not set, the test only populates the database and exits. When enabled, it listens on the requested address, optionally opens `/upstream`, serves static files directly, converts incoming HTTP requests into App Engine test requests, injects local IP/config/request registration, applies optional admin/user login, and delegates to `http.DefaultServeMux`.

Fixture population uploads multiple builds and crashes, creates fixed bugs and acknowledges reports, uploads fix builds across managers, submits a manual repro request, creates AI jobs and trajectory spans, completes AI assessment/patch jobs, simulates lore report publication/commenting, advances time for patch iteration, and leaves AI workflows available for UI exploration.

## State And Persistence Behavior
The file intentionally creates substantial datastore and Spanner-backed test state. It mutates bugs through reporting updates and fix builds, creates AI jobs/reports, and stores trajectory logs. The serving mode uses the same in-memory/test context for interactive inspection.

## Dependencies And Integration Points
It integrates nearly the whole app: test context setup, App Engine `aetest`, HTTP mux, dashboard config, reporting, builds/crashes, manual repro APIs, AI workflow APIs, trajectory logging, lore-style external reports, Spanner context setup, and target metadata.

## Risks
The local server path requires `-timeout=0 -v` when enabled and can run indefinitely. It starts `xdg-open` best-effort. Randomized trajectory timing/token data means UI details vary between runs. Since it uses broad app integration, failures can originate from many subsystems. The `filepath.Join(".", url)` static-file check uses the URL string including query if present, but only for static serving.

## Test Signals
This is more fixture than assertion-heavy test. Its main automated signal is that a rich local dataset can be created without errors. Manual signal comes from browsing the generated dashboard and checking pages/rendering interactively.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/local_ui_test.go -->
