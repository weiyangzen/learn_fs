# Research Group subset-b-009394

This grouped report covers syzkaller dashboard application files under `sources/test-tools/syzkaller/dashboard/app`. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/main.go -->
# sources/test-tools/syzkaller/dashboard/app/main.go

## Purpose

`main.go` is the primary web UI handler and view-model assembly file for the syzkaller dashboard App Engine application. It registers public, namespace-scoped, admin, text, coverage, subsystem, manager, bug, AI, and cron routes through `initHTTPHandlers`, then implements the bulk of dashboard page controllers and UI DTO construction for templates and optional JSON output.

## Important APIs, Types, and Functions

The file defines many `ui*` structs consumed by templates and the public JSON adapter: `uiMainPage`, `uiBugFilter`, `uiManagerList`, `uiTerminalPage`, `uiBugStats`, `uiReposPage`, `uiSubsystemPage`, `uiSubsystemsPage`, `uiAdminPage`, `uiManagerPage`, `uiBugPage`, `uiBugDetails`, `uiBugGroup`, `uiBug`, `uiCrash`, `uiBuild`, `uiJob`, `uiBackportsPage`, and related small structs. These isolate datastore entities from rendered pages and allow access-sensitive fields to be removed or transformed.

Core handlers include `handleMain`, `handleFixed`, `handleInvalid`, `handleManagerPage`, `handleSubsystemPage`, `handleBackports`, `handleRepos`, `handleTerminalBugList`, `handleAdmin`, `handleBug`, `handleBugSummaries`, `handleSubsystemsList`, and `handleTextImpl`. Helper functions such as `MakeBugFilter`, `userBugFilter.MatchBug`, `fetchNamespaceBugs`, `prepareBugGroups`, `loadVisibleBugs`, `fetchTerminalBugs`, `createUIBug`, `loadCrashesForBug`, `makeUICrash`, `makeUIBuild`, `loadManagers`, and `makeUIJob` form the main data pipeline.

## Control Flow

Requests enter App Engine through `handlerWrapper` routes. Namespace pages build a `uiHeader`, parse filters, fetch managers and bugs, then group bugs by reporting stage. Bug detail pages load one bug by datastore ID or reporting extid, enforce access, assemble crashes, duplicate/similar bugs, bisection jobs, discussions, test results, AI jobs, labels, and patch versions, and render either `bug.html` or `GetJSONDescrFor` output. Terminal pages reuse the same filtering but select fixed or invalid bugs. Admin pages enforce `AccessAdmin`, optionally perform actions, and then use `errgroup` to fetch memcache stats, managers, logs, and job lists concurrently.

Text endpoints parse legacy decimal IDs or newer hex `x` IDs, call access checks, load blob-like text entities, add reproducer headers when needed, and stream plain text. Backports aggregate cross-tree fix candidate jobs by source/target repository and commit. Subsystem pages use the namespace subsystem service, redirect renamed subsystems, and show child/parent subsystem data plus bug groups.

## State and Persistence Behavior

This file mostly reads from datastore-backed helpers: bugs, crashes, builds, managers, jobs, repro tasks, reporting state, cached UI pages, subsystem cache, AI DB records, text entities, and Google Cloud logs. It writes state only in controller actions such as saving manager repro tasks, creating AI jobs, forcing manual patch iteration, admin actions, and indirectly through helper calls. It also reads memcache stats and may flush memcache from the admin page. Cached UI paths are used when no filters are active and the namespace enables page caching.

## Dependencies and Integration Points

The code integrates with App Engine datastore, memcache, user/admin identity, Cloud Logging, syzkaller dashboard config, reporting logic, discussion storage, asset storage, subsystem inference, AI patching data, coverage handlers, job/bisection helpers, and template rendering. It also delegates public JSON conversion to `public_json_api.go` through `writeJSONVersionOf`.

## Risks and Edge Cases

The file has a wide blast radius: filter behavior affects both pages and JSON, access checks must remain consistent with sanitized bug/reporting data, and datastore query constraints shape filter implementation. The `userBugFilter` applies only the first label at query level and then filters remaining labels in memory, so performance depends on result sizes. `loadVisibleBugs` runs duplicate and open bug queries in parallel and then merges dup bugs later; changes can easily hide duplicates or expose inaccessible bugs. Text serving is sensitive because it exposes logs, reproducers, configs, and reports and relies on `checkTextAccess` plus namespace access checks. Admin actions are high privilege and dispatch to many mutating helpers. Cloud log fetching uses an explicit filter with many exclusions; changes may flood or hide admin diagnostics.

## Test Signals

`main_test.go` directly covers manager-only filtering, subsystem and label filters, subsystem list/page behavior, admin job list links, subsystem redirects, throttling, manager page build filtering, and repro form access. `public_json_api_test.go` exercises the JSON path that starts from `handleBug`, `handleMain`, and terminal pages. Other dashboard tests indirectly cover bug/job/reporting helpers used here.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/main_test.go -->
# sources/test-tools/syzkaller/dashboard/app/main_test.go

## Purpose

`main_test.go` is a black-box integration-style test suite for the dashboard web UI handlers in `main.go`. It uses the local dashboard test harness to upload builds and crashes, advance fake time, poll reportings, call authenticated HTTP routes, and assert rendered page behavior.

## Important APIs, Types, and Functions

Tests use `NewCtx`, `NewSpannerCtx`, `Ctx.AuthGET`, `Ctx.GET`, test clients such as `c.client`, `c.client2`, `c.publicClient`, and helpers like `testBuild`, `testCrash`, `testCrashWithRepro`, `pollEmailBug`, `globalClient.pollBugs`, and `globalClient.updateBug`. The file defines constants `subsystemA` and `subsystemB` used by subsystem inference fixtures.

Individual tests cover:

- `TestOnlyManagerFilter` for `only_manager` filtering on open and invalid pages.
- `TestSubsystemFilterMain` and `TestSubsystemFilterTerminal` for label-based subsystem filters.
- `TestMainBugFilters` for no-subsystem, with-repro, with-AI-patch, and filter banner behavior.
- `TestSubsystemsList`, `TestSubsystemPage`, and `TestSubsystemsPageRedirect` for subsystem list filtering, per-subsystem pages, and redirect configuration.
- `TestMultiLabelFilter` for combined label filtering and drop-label link behavior.
- `TestAdminJobList` for admin bisection job list links.
- `TestNoThrottle` and `TestThrottle` for request throttling behavior.
- `TestManagerPage` and `TestReproSubmitAccess` for manager build history, unknown manager errors, and repro request access.

## Control Flow

Most tests construct datastore state by uploading builds and reporting crashes, optionally poll bugs so reporting IDs and labels are initialized, and then call dashboard routes with different access levels and query parameters. Assertions are primarily string containment checks against rendered HTML, plus `HTTPError` checks for expected redirects, bad requests, or rate limiting.

## State and Persistence Behavior

The tests exercise datastore writes for builds, crashes, bugs, reporting state, jobs, labels, subsystem cache, and repro tasks through the same client APIs used by dashboard components. `TestSubsystemsList` explicitly triggers `/cron/refresh_subsystems` before checking subsystem cache output. `TestThrottle` mutates config through `transformContext` to enable a short throttle window in the test context.

## Dependencies and Integration Points

This suite depends on the test App Engine context, dashboard config fixtures, subsystem inference fixtures that map guilty files to `subsystemA` and `subsystemB`, email/global reporting helpers, and HTTP wrapper behavior that returns `HTTPError` values. It validates the integration among `main.go`, reporting state, datastore entities, cache refresh, throttle logic, and template output.

## Risks and Test Signals

The tests catch regressions where filters disappear from query construction, multi-label filters are treated as OR instead of AND, filtered pages still show unrelated managers, subsystem redirects break, or access levels expose repro submission to public users. They are less precise about HTML structure because most assertions are content-based. They do not deeply validate JSON fields, asset links, Cloud Logging, text blob access, or all admin actions, so those remain residual risk areas.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/notifications_test.go -->
# sources/test-tools/syzkaller/dashboard/app/notifications_test.go

## Purpose

`notifications_test.go` verifies notification behavior for the backend-independent reporting logic and the email/external reporting adapters. It focuses on upstreaming notifications, bad fixing commit reminders, automatic obsoletion, and external notification polling.

## Important APIs, Types, and Functions

The tests use the same dashboard test harness plus `dashapi` update/poll types. Key test cases include `TestEmailNotifUpstreamEmbargo`, `TestEmailNotifUpstreamSkip`, `TestEmailNotifBadFix`, `TestBugObsoleting`, `TestEmailNotifObsoleted`, `TestEmailNotifNotObsoleted`, `TestEmailNotifObsoletedManager`, `TestExtNotifUpstreamEmbargo`, and `TestExtNotifUpstreamOnHold`.

## Control Flow

Email notification tests create bugs in staged reportings, poll the first bug report, advance fake time past configured periods, and then poll email again to observe notification messages and follow-up reports. The bad-fix test sends an inbound `#syz fix` command, advances past the 90-day bad commit notification period, and validates the generated body including tested tree information. Obsoletion tests upstream bugs, create activity or fresh crashes, then advance time to verify which bugs are invalidated and which remain open. External notification tests use `globalClient.pollNotifs` and `ReportingUpdate` to verify `BugNotifUpstream` behavior outside email.

## State and Persistence Behavior

These tests exercise persistent `Bug.Reporting` fields such as `Reported`, `Closed`, `OnHold`, `Auto`, `CC`, and reporting IDs; bug status transitions; commit metadata; manager/build records; discussion/activity timestamps; and reporting quota state indirectly. Time is controlled through `c.advanceTime`, which is essential because notification generation depends on embargo, resend, obsoletion, and bad-commit periods.

## Dependencies and Integration Points

The suite covers interaction among `reportingPollNotifications`, `createNotification`, `emailSendBugNotif`, `incomingCommand`, email address context encoding, `loadRepos`, manager config obsoleting overrides, and external polling APIs. It also depends on configured staged reportings and manager/repository fixtures.

## Risks and Test Signals

These tests provide strong signals for timing-sensitive behavior. They ensure embargo upstreaming does not happen early, auto-upstream respects repro/filter conditions, bad commit reminders include actionable text and repeat only after the resend period, obsoletion CC lists differ by reporting stage, new crashes can recreate obsolete bugs, and `OnHold` suppresses external upstream notifications. Gaps remain around label notifications, notification failures from missing build/crash data, and exact interactions with manually set labels or subsystem maintainers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/notifications_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/public_json_api.go -->
# sources/test-tools/syzkaller/dashboard/app/public_json_api.go

## Purpose

`public_json_api.go` converts dashboard UI page models into stable public JSON API descriptions and streams coverage data in an external coverage format. It is the bridge between template-oriented structs in `main.go` and `github.com/google/syzkaller/dashboard/api` consumers.

## Important APIs, Types, and Functions

`getExtAPIDescrForBug` maps `uiBugDetails` to `api.Bug`, including title, ID, status, crash times, optional fix/close times, discussions, fix commits, cause bisection commit, and crash descriptors. `getBugFixCommits` maps `uiCommit` to `api.Commit` and preserves optional dates. `getExtAPIDescrForBugGroups` flattens `uiBugGroup` lists into `api.BugSummary` records. Backport JSON uses local structs `publicKernelTree`, `publicBackportBug`, `publicMissingBackport`, and `publicAPIBackports` plus `getExtAPIDescrForBackports`.

`GetJSONDescrFor` is the central dispatcher. It accepts `*uiBugPage`, `*uiTerminalPage`, `*uiMainPage`, `*uiBackportsPage`, and selected dungeon/AI page types, returning indented JSON or `ErrClientNotFound`. Coverage export is handled by `writeExtAPICoverageFor`, `writeFileCoverage`, and `genFuncsCov`.

## Control Flow

For page JSON, handlers in `main.go` build the normal UI page model, then call `GetJSONDescrFor`. That function selects a conversion path and marshals with `json.MarshalIndent`. For coverage JSON, `writeExtAPICoverageFor` chooses the previous completed month, builds a `coveragedb.FunctionFinder`, streams file coverage rows for namespace/subsystem/manager scope, and delegates each file to `writeFileCoverage`. `writeFileCoverage` turns each file row into a `cover.FileCoverage` JSON object and writes one encoded object per stream item. `genFuncsCov` groups line hit counts by function name using `FunctionFinder.FileLineToFuncName`.

## State and Persistence Behavior

This file does not write persistent application state. It reads already-sanitized UI models and coverage DB data. Coverage output depends on current wall-clock month via `time.Now`, not `timeNow(ctx)`, so tests need fixture control through the coverage DB mock rather than dashboard fake time.

## Dependencies and Integration Points

It depends on `dashboard/api`, `pkg/cover`, `pkg/coveragedb`, civil dates, and the UI structs from `main.go`. Its consumers are page handlers that support `?json=1` and external API clients. Coverage streaming integrates with the coverage database client stored in context.

## Risks and Edge Cases

Because JSON is derived from UI structs, access filtering must happen before conversion; this file assumes the page model is already safe. `getExtAPIDescrForBackports` assumes each backport bug has crash data when JSON is requested by `handleBackports(loadCrashes=true)`. `writeFileCoverage` exits silently on context cancellation, which avoids noisy failures but can produce partial output. `genFuncsCov` assumes `HitCounts` and `LinesInstrumented` are aligned arrays; mismatch would panic through indexing. Map iteration over function names is not sorted, so function ordering can be unstable unless upstream data or tests constrain it.

## Test Signals

`public_json_api_test.go` covers bug page JSON, bug-group JSON, fix commit metadata, cause bisection JSON, API client integration, and coverage export formatting with mocked coverage DB rows.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/public_json_api.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/public_json_api_test.go -->
# sources/test-tools/syzkaller/dashboard/app/public_json_api_test.go

## Purpose

`public_json_api_test.go` validates the dashboard public JSON API generated by `public_json_api.go` and the handler paths in `main.go` that expose `?json=1` responses. It also tests file coverage JSON export against a mocked coverage database.

## Important APIs, Types, and Functions

The suite defines helpers `checkBugPageJSONIs`, `checkBugGroupPageJSONIs`, and `fileFuncLinesDBFixture`. Test cases include `TestJSONAPIIntegration`, `TestJSONAPIFixCommits`, `TestJSONAPICauseBisection`, `TestPublicJSONAPI`, and `TestWriteExtAPICoverageFor`.

`fileFuncLinesDBFixture` builds a mock `spannerclient.SpannerClient` with mocked read-only transactions and row iterators so `writeExtAPICoverageFor` can exercise both function-line lookup and full coverage streaming without a real coverage DB.

## Control Flow

The JSON integration tests create builds and crashes, poll bugs to enter reporting state, then fetch `/bug?...&json=1`, namespace main pages with `?json=1`, or fixed pages with `?json=1`. Expected JSON is compared as an exact string, including indentation, field names, timestamps, text links, and optional fields. Fix commit and bisection tests add commit metadata or bisection jobs before asserting that JSON includes commit hashes, authors, dates, repos, branches, and cause commit data.

`TestPublicJSONAPI` goes through the exported API client rather than raw HTTP helpers: it fetches bug groups, follows a bug link, and retrieves a text link. `TestWriteExtAPICoverageFor` configures a mocked coverage client, writes coverage JSON into a buffer, and compares the exact generated `cover.FileCoverage` object.

## State and Persistence Behavior

The tests write realistic datastore state for builds, crashes, bugs, reporting transitions, commits, jobs, and text blobs. They also install a context-scoped coverage DB client. The exact JSON comparisons assert which zero fields are omitted and which timestamps or links become visible after state changes.

## Dependencies and Integration Points

The file integrates with `dashboard/api` clients, `dashapi` reporting updates, coverage DB mocks, Spanner mock transactions, and the dashboard test context. It gives coverage for the handoff from UI handlers to `GetJSONDescrFor`, and from coverage route logic to `writeExtAPICoverageFor`.

## Risks and Test Signals

Exact JSON string comparison is a strong regression signal for public API shape, field tags, time formatting, indentation, and link generation. It can also be brittle if harmless field ordering changes occur. Coverage export testing currently uses one file and one function, so it verifies the happy path but not multiple functions, function ordering, context cancellation, or coverage DB error propagation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/public_json_api_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/reporting.go -->
# sources/test-tools/syzkaller/dashboard/app/reporting.go

## Purpose

`reporting.go` contains backend-independent bug reporting logic. It decides when bugs should be reported, builds `dashapi.BugReport` and `dashapi.BugNotification` payloads, tracks reporting quotas, applies incoming external status updates, handles duplicate validation, constructs full bug info, and provides shared datastore query helpers.

## Important APIs, Types, and Functions

Main polling functions are `reportingPollBugs`, `handleReportBug`, `needReport`, `reportingPollNotifications`, `handleReportNotif`, and `reportingPollClosed`. Notification generation is driven by `notificationGenerators`, `createLabelNotification`, `bugObsoletionReason`, `Bug.canBeObsoleted`, `Bug.obsoletePeriod`, and `createNotification`.

Report construction uses `currentReporting`, `createBugReport`, `crashBugReport`, `loadReproSyz`, `fillBugReport`, `managersToRepos`, `queryCrashesForBug`, and `findCrashForBug`. Incoming updates enter through `incomingCommand`, `incomingCommandImpl`, `incomingCommandTx`, `incomingCommandUpdate`, `incomingCommandCmd`, and `checkBugStatus`. Duplicate safety is enforced by `checkDupBug`, `allowCrossReportingDup`, `getReportingIdx`, `findBugByReportingID`, and `findDupByTitle`. Reporting configuration migration is handled by `Bug.updateReportings`. Full external detail uses `loadFullBugInfo`, `prepareBisectionReport`, `prepareFixCandidateReport`, and `representativeCrashes`.

## Control Flow

Polling loads reporting state and open bugs, sorts by `bugReportSorter`, and returns at most three reports per poll to avoid memory pressure. `needReport` checks current reporting stage, requested backend type, already-reported repro level, namespace reporting delay, repro wait, missing report policy, crash count, and daily quota. If a bug is ready, `createBugReport` selects a representative crash, optionally substitutes a bisection crash, and fills a `dashapi.BugReport`.

Notification polling scans open reported bugs and applies ordered notification generators: embargo upstreaming, filter-skip upstreaming, obsoletion, bad fix commit, and configured label messages. Incoming commands normalize fix commit quoting, resolve bug/reporting IDs and duplicates, then run a cross-group datastore transaction that validates status, updates bug/reporting fields, records crash references, merges CC, updates repro level and activity, persists `Bug`, and saves `ReportingState`.

## State and Persistence Behavior

Persistent state centers on datastore `Bug`, `BugReporting`, `Crash`, `Build`, `Job`, and singleton `ReportingState` entities. `ReportingStateEntry.Sent` enforces daily reporting limits and resets by `timeDate`. Incoming updates mutate `Bug.Status`, `Closed`, `DupOf`, `Commits`, `FixTime`, `LastActivity`, `UNCC`, `BugReporting.Reported`, `Closed`, `Auto`, `ExtID`, `Link`, `CC`, `CrashID`, `ReproLevel`, `Labels`, and `OnHold`. Crash references are added or removed so crash purge/reporting accounting remains correct.

## Dependencies and Integration Points

This file is called by email reporting, external reporting APIs, job reporting, UI status rendering, public full bug info APIs, and tests. It depends on config reporting filters, App Engine datastore transactions, text storage, build loading, bisection/job helpers, email helpers, subsystem maintainers, asset creation, kernel repo metadata, and `dashapi` status/report types.

## Risks and Edge Cases

Reporting stage ordering and filtering are subtle: `currentReporting` skips unreported stages with `FilterSkip` but keeps reported skipped stages, and `updateReportings` forbids reordering while allowing insertions/deletions with dummy stages. Duplicate handling must prevent cycles, cross-namespace dups, self-dups, and unsafe cross-reporting dups. Obsoletion is probabilistic and capped by namespace or manager config. Incoming updates intentionally use many transaction attempts because email backends may not retry. Partial failures after external systems receive reports can create repeated notifications until `incomingCommand` or `jobReported` succeeds. Report construction depends on text blobs and builds still existing.

## Test Signals

`notifications_test.go` covers notification timing, obsoletion, bad commit reminders, and external notifications. Email and reporting tests elsewhere exercise incoming commands, duplicate/fix/update flows, repro-level reporting, job reports, and reporting migration. UI tests indirectly depend on `needReport` for status text.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/reporting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/reporting_email.go -->
# sources/test-tools/syzkaller/dashboard/app/reporting_email.go

## Purpose

`reporting_email.go` implements the email backend for syzkaller reporting. It sends bug reports, job results, notifications, subsystem bug-list reminders, and coverage regression mail, and it processes inbound email commands, bounces, monitored inbox forwarding, and discussion archiving.

## Important APIs, Types, and Functions

`EmailConfig` is the reporting configuration type with `Type`, `Validate`, and `getSubject`. `initEmailReporting` registers cron and inbound mail routes and discovers configured mailing lists. Cron send paths are `handleCoverageReports`, `sendNsCoverageReport`, `coverageTable`, `handleEmailPoll`, `emailPollJobs`, `emailPollNotifications`, `emailPollBugs`, `emailPollBugLists`, `emailSendBugReport`, `emailSendBugListReport`, `emailSendBugNotif`, `emailReport`, `emailListReport`, `sendMailTemplate`, and `sendMailText`.

Inbound handling starts at `handleIncomingMail`, then routes to `processInboxEmail`, `processDiscussionEmail`, or `processIncomingEmail`. Identification and command helpers include `identifyEmail`, `loadBugInfo`, `bugInfoWithoutBugID`, `matchBugFromList`, `subjectTitleParser`, `handleBugCommand`, `handleTestCommand`, `handleSetCommand`, `handleUnsetCommand`, and `handleBugListCommand`. Address and reply utilities include `ownEmail`, `ownEmails`, `ownMailingLists`, `missingMailingLists`, `forwardEmail`, `replyTo`, `replyError`, `sanitizeCC`, `externalLink`, and `appURL`.

## Control Flow

`handleEmailPoll` checks emergency stop, sends completed job reports, sends notifications, sends new bug reports, then sends bug-list reports. Successful bug report delivery is followed by `incomingCommand` with `BugStatusOpen` and the observed repro level so the datastore records that the stage was reported. Notifications are translated into email bodies and then back into `incomingCommand` updates: upstream notifications close the current reporting stage, obsoletion marks invalid, label notifications record the label as sent, and bad commit reminders keep the bug open.

Inbound mail is parsed with syzkaller email helpers. Discussion addresses bypass emergency stop and are saved as discussion messages. Monitored inbox mail may be forwarded to required lists. Normal command mail identifies a bug by embedded reporting hash or by subject plus mailing list, filters duplicates from mailing lists, caps command counts, and applies commands through reporting updates or label mutations. `#syz test` creates patch test jobs when the bug is public and command syntax is valid. Bug-list commands operate on `SubsystemReport` stages or referenced bugs.

## State and Persistence Behavior

This file writes mail through App Engine mail and then records delivery effects in datastore through `incomingCommand`, `jobReported`, `reportingBugListCommand`, label update transactions, discussion saving, test request creation, and monitored inbox forwarding. It reads and writes no standalone email state, but it relies heavily on `Bug.Reporting`, `ReportingState`, `SubsystemReport`, `Discussion`, `Job`, and coverage DB records. `sendEmail` is a variable for test stubbing.

## Dependencies and Integration Points

The email backend integrates with App Engine mail and request contexts, `pkg/email` parsing/formatting, lore discussion typing, coverage DB, text templates from `mail_*.txt`, reporting core in `reporting.go`, subsystem bug-list reporting in `reporting_lists.go`, test job creation, discussion storage, and dashboard config.

## Risks and Edge Cases

Inbound email is adversarial input. The code defends against malformed messages, own-mail loops, duplicate mailing-list copies, missing or ambiguous bug IDs, command spam, sample command echoes, and commands not directly addressed to syzbot. Subject-based matching can be ambiguous and is intentionally conservative. Forwarding and missing-list logic mutates `msg.Cc` and can affect subsequent command updates. Sending mail before recording state means a datastore failure can cause duplicate sends on a later cron. `handleCoverageReports` logs errors per namespace but does not fail the whole HTTP request. Some error replies intentionally suppress details to avoid leaking internals.

## Test Signals

`notifications_test.go` verifies notification mail behavior and message bodies. Email-focused tests in the package cover commands, bounces, patch testing, labels, discussion handling, and report templates. `main_test.go` and `public_json_api_test.go` indirectly exercise email reporting IDs and links.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/reporting_email.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/reporting_external.go -->
# sources/test-tools/syzkaller/dashboard/app/reporting_external.go

## Purpose

`reporting_external.go` exposes the backend-independent reporting core to external dashboard API clients. It is a thin adapter between `dashapi` RPC request/response types and internal reporting, notification, closed-bug, update, and test-job functions.

## Important APIs, Types, and Functions

The exported adapter functions are `apiReportingPollBugs`, `apiReportingPollNotifications`, `apiReportingPollClosed`, `apiReportingUpdate`, and `apiNewTestJob`. They consume `dashapi.PollBugsRequest`, `dashapi.PollNotificationsRequest`, `dashapi.PollClosedRequest`, `dashapi.BugUpdate`, and `dashapi.TestPatchRequest`, and return corresponding response structs.

## Control Flow

Each polling function first checks `emergentlyStopped`; if stop is active or querying stop state fails, it returns an empty response and the error where applicable. Bug polling calls `reportingPollBugs` for the requested reporting type, then appends completed job reports from `pollCompletedJobs`. Notification polling returns `reportingPollNotifications`. Closed polling delegates to `reportingPollClosed`.

`apiReportingUpdate` has two paths. If `req.JobID` is set, it marks the job as reported with `jobReported` and returns a `BugUpdateReply` with `Error` set on failure. Otherwise it delegates to `incomingCommand` and translates `(ok, reason, err)` into `BugUpdateReply`. `apiNewTestJob` calls `handleExternalTestRequest`; user/input errors are returned in `ErrorText`, while non-input errors are also logged.

## State and Persistence Behavior

This file does not directly mutate datastore, but its delegates do. `reportingPollBugs` and `reportingPollNotifications` read bugs/reporting state. `pollCompletedJobs` reads completed jobs. `jobReported` marks job reporting state. `incomingCommand` mutates bug/reporting/crash state transactionally. `handleExternalTestRequest` creates test jobs or rejects invalid requests.

## Dependencies and Integration Points

It is integrated with the dashboard API transport layer that dispatches authenticated `dashapi` methods. It depends on emergency stop state, reporting core, job reporting, external patch-test request validation, and App Engine logging.

## Risks and Edge Cases

The adapter deliberately returns empty successful-looking poll responses during emergency stop so external pollers do not receive new work. Completed job report polling errors are logged but do not fail bug polling, which prevents one job error from blocking normal bug reports but can delay job result delivery. `apiReportingUpdate` treats job updates separately from bug updates; malformed requests containing both a `JobID` and bug fields will take the job path. External test job errors distinguish `BadTestRequestError` from internal errors to avoid over-logging invalid input.

## Test Signals

`notifications_test.go` uses the external notification path through `globalClient.pollNotifs` and `ReportingUpdate`. Broader API/reporting tests in the package exercise external bug polling, updates, job completion, and test job request behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/reporting_external.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/reporting_lists.go -->
# sources/test-tools/syzkaller/dashboard/app/reporting_lists.go

## Purpose

`reporting_lists.go` implements monthly subsystem bug-list reminders. It periodically builds `SubsystemReport` datastore entities for configured subsystems, exposes those reports to reporting backends as `dashapi.BugListReport`, and applies commands that mark stages sent, upstream reports, or request regeneration.

## Important APIs, Types, and Functions

The main producer is `handleSubsystemReports`, which creates fresh reports. The main poller is `reportingPollBugLists`. Command handling is done by `reportingBugListCommand` and `findSubsystemReportByID`. Report construction and filtering are handled by `querySubsystemReport`, `queryMatchingBugs`, `makeSubsystemReportStats`, and `makeSubsystemReport`. Backend payload conversion is `reportingBugListReport`. Persistence helpers include `makeSubsystem`, `subsystemKey`, `subsystemReportKey`, `subsystemsRegistry`, `makeSubsystemRegistry`, `subsystemsRegistry.updatePoll`, `subsystemReportRegistry`, `makeSubsystemReportRegistry`, and `storeSubsystemReport`. IDs use `bugListReportingHash` with `bugListHashPrefix`.

## Control Flow

`handleSubsystemReports` loads known subsystem state, iterates namespaces with `Subsystems.Reminder`, builds a round-robin list of configured subsystems sorted by `ListsQueried`, skips recently reported subsystems based on `PeriodDays`, queries matching bugs, updates poll timestamps, and stores up to `maxNewListsPerNs` new reports per namespace. `querySubsystemReport` selects open bugs at the configured source reporting stage, skips stale, too-new, low-priority, recently discussed, and `NoRemindersLabel` bugs, balances reproducible and non-repro bugs, sorts by priority/crashes/title, applies optional moderation skipping, and records bug keys plus total/period stats.

`reportingPollBugLists` loads `ReportingState` and a report registry, then scans configured subsystem reports in stable subsystem order. It respects the source reporting daily limit and returns only stages whose reporting config type matches the caller. `reportingBugListReport` skips closed stages, skips missing configs, stops at already-reported or different-type stages, loads referenced bugs, and builds links and stats. Commands run in a transaction and update stage `Reported`, `Closed`, `ExtID`, `Link`, reporting quota, or subsystem `LastBugList`.

## State and Persistence Behavior

The file persists `Subsystem` entities keyed by namespace/name and child `SubsystemReport` entities keyed by creation time. `Subsystem` stores `ListsQueried` and `LastBugList`; `SubsystemReport` stores encoded bug keys, total and period stats, creation time, and one or two `SubsystemReportStage` entries. `storeSubsystemReport` closes all previous active reports for the subsystem before saving the new one. `reportingBugListCommand` also updates singleton `ReportingState` when a list is sent.

## Dependencies and Integration Points

It depends on namespace subsystem service configuration, `BugListReportingConfig`, reporting configs, datastore, `dashapi.BugListReport`, `hash`, subsystem maintainers, bug labels and priority, discussion summaries, and the generic reporting state used by normal bug reporting. Email handling calls these functions to send list mail and process list commands.

## Risks and Edge Cases

The lifecycle is stateful across cron ticks: a failed store or command can leave old reports active or cause repeated sends. `reportingPollBugLists` assumes `SourceReporting` exists; missing config would panic or nil dereference through `reporting.Name`. Stage skipping is intentional when moderation config disappears, but command handling must close skipped stages to avoid stuck reports. Encoded bug keys can become stale; `reportingBugListReport` fails if `db.GetMulti` cannot load them. Reports only include bugs currently at the expected reporting stage and access level, so reporting config changes can alter eligibility.

## Test Signals

Email and subsystem reminder tests in the package exercise list creation, sending, upstream/regenerate commands, and label set/unset commands against bug-list references. `main_test.go` provides subsystem classification and page coverage that underpins reminder selection.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/reporting_lists.go -->
