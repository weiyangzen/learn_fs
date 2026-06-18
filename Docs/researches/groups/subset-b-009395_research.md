# subset-b-009395 Research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/reporting_test.go -->
# sources/test-tools/syzkaller/dashboard/app/reporting_test.go

Purpose: broad integration coverage for syzbot dashboard external reporting, bug lifecycle transitions, reproducer reporting, duplicate handling, machine info links, alternate-title merging, full bug loading, report updates, decommissioning, obsoletion, coverage-regression email, and skipped reporting stages. It is a test file, but it is one of the clearest executable specifications for dashboard reporting semantics.

Important APIs and fixtures: `TestReportBug`, `TestInvalidBug`, quota tests, duplicate tests, `TestAltTitles*`, `TestFullBugInfo`, `TestUpdateReportApi`, `TestReportRevokedRepro`, `TestReportRevokedBisectCrash`, and `TestSkipStage` drive `dashapi` clients from `util_test.go`. They call `UploadBuild`, `ReportCrash`, `ReportingPollBugs`, `ReportingUpdate`, `ReportingPollClosed`, `LoadFullBug`, `UpdateReport`, `JobPoll`, `JobDone`, `BugList`, and HTTP endpoints such as namespace index pages, bug pages, text links, and `/cron/email_coverage_reports`.

Control flow: tests create isolated `Ctx` instances, upload builds and crashes, poll reporting queues, mutate external status through `BugUpdate`, and then assert the next observable API or UI response. The basic reporting path verifies first report construction, repro report upgrade, movement between reporting stages, moderation flags, links to text blobs, maintainers, subsystem metadata, crash IDs, repro links, and rejection of invalid upstream transitions from a final stage. Later tests cover daily quota refill by advancing mocked time, dup-to-open and dup-to-closed behavior, prevention of dup cycles, cross-reporting dup constraints, reporting filters, detach-from-external-tracker behavior, and stability of alternate-title bug merging.

State and persistence: the tests exercise datastore-backed `Bug`, `Crash`, `Build`, `Job`, and text blob records. They confirm `Bug.Reporting` stage records are advanced or marked dummy by config changes, crash text blobs are addressable through external links, machine info is persisted and rendered, closed/decommissioned bugs appear in `ReportingPollClosed`, repro revocation updates report content without causing infinite report loops, and `ReportElements.GuiltyFiles` can be mutated via update API.

Dependencies and integration points: depends on App Engine test harness helpers in `util_test.go`, dashboard client packages `dashapi` and `api`, target metadata, coverage DB mocks, email parsing, and testify assertions. It integrates with cron endpoints, coverage regression reporting, discussion/email side effects, bisection job completion, and namespace/reporting configuration callbacks.

Risks: many assertions compare full `dashapi.BugReport` structs, so harmless field additions may require test updates. The tests encode nuanced lifecycle invariants; changes to reporting stage filtering, duplicate resolution, or repro revocation can easily break backwards compatibility with external trackers. Time-driven quota and obsoletion tests depend on mocked clock consistency. Coverage regression uses mocks and email body formatting, making it sensitive to query ordering and textual presentation.

Test signals: this file itself is the signal. Passing it indicates the public reporting API, moderation flow, lifecycle state transitions, external links, full bug info composition, coverage email regression path, and skipped reporting stage rules still match existing contracts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/reporting_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/repro_test.go -->
# sources/test-tools/syzkaller/dashboard/app/repro_test.go

Purpose: integration tests for reproducer request policy, failed reproducer accounting, log-to-reproduce task selection, reproduction logs for mismatched titles, and manually submitted reproduction tasks.

Important APIs and helpers: `testNeedRepro1/2/3`, `normalCrash`, `dupCrash`, `closedCrash`, `closedWithReproCrash`, `TestNeedReproMissing`, `TestNeedReproIsolated`, `TestFailedReproLogs`, `TestLogToReproduce`, `TestReproForDifferentCrash`, and `TestReproTask`. The tests drive `ReportCrash`, `NeedRepro`, `ReportFailedRepro`, `LogToRepro`, and `ReproTaskDone`, plus admin form submission to `/test1/manager/<manager>` with `send-repro`.

Control flow: the main scenarios upload crashes with no repro, syz repro, and C repro and verify the `NeedRepro` bit returned from both `ReportCrash` and `NeedRepro`. Variants exercise normal bugs, duplicates, invalid/closed bugs, and closed bugs with existing reproducers. Failed-repro loops advance the mocked time to verify daily retry throttling. `TestNeedReproIsolated` directly checks `needReproForBug` on hand-built `Bug` values for corrupted/suppressed titles, syz-only repros, stale C repros, failed attempt limits, SYZFATAL/SYZFAIL exceptions, and revoked repro state.

State and persistence: failed repro attempts store bounded `ReproAttempts` with text blobs for logs; when `maxReproLogs` is exceeded, the oldest text object must be removed and newer logs remain fetchable. `LogToRepro` chooses eligible crash logs without repros by build, suppresses logs after a failed attempt, and returns manual repro tasks until they succeed or exhaust explicit failed attempts. Reporting a repro for a different crash title stores the reproduction log on the original bug through `OriginalTitle`.

Dependencies and integration points: uses dashboard API objects from `dashapi`, test context helpers, bug/crash factories from the broader test package, HTTP form helpers, and text serving. It integrates with reporting state because some setup closes, duplicates, or polls bugs before testing repro decisions.

Risks: repro throttling is time-sensitive and depends on constants such as `maxReproPerBug`, `maxReproLogs`, and `reproStalePeriod`. The `MayBeMissing` flag intentionally changes error handling for missing crashes, so API clients rely on that distinction. Manual repro tasks are retried only when `ReproTaskDone` reports failures; silent workers that never call completion keep the task available.

Test signals: passing tests show that the dashboard asks managers for repros only when useful, avoids unbounded failed-log growth, serves repro logs through text links, and handles manual repro task retries without starving or duplicating work.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/repro_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/static/common.js -->
# sources/test-tools/syzkaller/dashboard/app/static/common.js

Purpose: shared browser-side helpers for dashboard pages: sortable tables, dynamic repeated input groups, collapsible blocks, and conditional display of AI job form fields.

Important functions: `sortTable`, `findColumnByName`, `isSorted`, sorting converters (`textSort`, `numSort`, `floatSort`, `reproSort`, `patchedSort`, `lineSort`, `timeSort`), `findAncestorByClass`, `deleteInputGroup`, `addInputGroup`, `displayAICreateJobArgs`, and `showManualWorkflowFields`.

Control flow: `sortTable` walks from the clicked item to the containing table, finds a column by header text, extracts cell text or explicit `sort-value`, toggles ascending/descending based on current sortedness, sorts row references, and appends them back to the tbody. Input helpers clone or remove `.input-group` elements, preserving at least one blank input. DOM listeners initialize collapsible sections on `DOMContentLoaded` and AI workflow field visibility on `load`.

State and persistence: state is only DOM state. Sorting mutates row order in the current table. Collapsible sections toggle CSS classes. AI form helpers set `style.display` and `disabled` on input groups so hidden manual workflow fields are not submitted. No local storage or server persistence is used.

Dependencies and integration points: plain browser DOM APIs; expected markup includes table headers, `.input-values`, `.input-group`, `.collapsible`, `.head`, `select[name="ai-job-create"]`, `#ai-set-base-commit`, `#base_commit_custom`, `#base_commit_input`, `#ai-job-create`, and `#workflow-fields-<workflow>`.

Risks: variables are implicitly global in several functions because `let`/`const` is omitted, which can cause collisions. `sortTable` depends on a fixed DOM ancestor depth and exact header text. `timeSort` parses compact strings such as `1d2h` and falls back to a large value for unknown formats; presentation changes can alter ordering. Cloned input groups copy any extra attributes/events not reset beyond the first input value.

Test signals: no direct JS tests in this subset. Coverage is likely indirect through dashboard UI tests/manual use; regressions would show as broken table sorting, duplicate form values, or missing AI manual workflow fields.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/static/common.js -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/static/coverage.js -->
# sources/test-tools/syzkaller/dashboard/app/static/coverage.js

Purpose: browser-side behavior for coverage report pages, including collapsible file-tree navigation, query-parameter-backed update form initialization, and asynchronous file coverage detail display.

Important functions: `initTogglers`, `initUpdateForm`, and `onShowFileContent`.

Control flow: document-ready handlers register click toggles on `.caret` elements and update the `#unique-only` checkbox when `#target-manager` changes. `initUpdateForm` reads current URL query parameters and pushes `period`, `period_count`, `subsystem`, `manager`, and `unique-only` into form controls. `onShowFileContent` appends selected subsystem/manager/unique-only query values to the requested detail URL, fetches HTML with jQuery, shifts current file content/details into “previous” containers, and writes the fetched response and source parameter summary into the current containers.

State and persistence: all state is DOM and URL-derived. No persistent client storage is used. The previous/current panels preserve one step of viewing history by copying HTML between `#file-content-prev`, `#file-content-curr`, `#file-details-prev`, and `#file-details-curr`.

Dependencies and integration points: depends on jQuery, coverage page markup IDs, `.caret`/`.nested` CSS classes, and server endpoints that return HTML fragments for file coverage content. It integrates with the coverage report query language by preserving subsystem, manager, and unique-only filters.

Risks: URL concatenation assumes the incoming `url` already has a query string and appends unescaped parameter values. The unique-only checkbox is disabled when manager is `*`/empty, but stale URL values can still be displayed. The HTML response is inserted directly into the page, so the endpoint must return trusted/sanitized markup.

Test signals: no direct JS test file here. Server-side `TestCoverageRegression` validates related coverage-report email generation, but interactive file-content behavior depends on browser/manual coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/static/coverage.js -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/stats.go -->
# sources/test-tools/syzkaller/dashboard/app/stats.go

Purpose: collects bug-level statistics for syzbot reporting stages and converts dashboard datastore objects into `syzbotstats.BugStatSummary` objects.

Important APIs and types: `bugInput` bundles `Bug`, selected `BugReporting`, reported `Crash`, and `Build`; methods/functions include `fixedAt`, `bugStatus`, `allBugInputs`, generic `getAllMulti[T]`, and `getBugSummaries`.

Control flow: `allBugInputs` loads all bugs in a namespace, selects `lastReportedReporting`, asynchronously batches crash dependencies for reporting records with a `CrashID`, then batches corresponding build dependencies. `getBugSummaries` filters bugs that reached the requested reporting stage, builds summary fields from bug/crash/build state, includes all external reporting IDs and fix hashes, optionally adds repro and cause-bisection timestamps, prefers fixing commit dates over close time when earlier, computes status, estimates hits per day for enough/fresh crashes, and copies subsystem label values.

State and persistence: reads datastore `Bug`, child `Crash`, and `Build` entities; it does not mutate state. `getAllMulti` works around App Engine datastore multi-get limits by chunking at 1000 keys and returns the first failing key for `MultiError` cases.

Dependencies and integration points: App Engine datastore, `loadAllBugs`, `dependencyLoader`, `lastReportedReporting`, `buildKey`, `bugReportingByName`, `queryBestBisection`, `dashapi.CrashFlags`, and `syzbotstats`. The output feeds statistics generation outside this file.

Risks: `bugStatus` returns an error for unexpected status combinations, which can fail the entire summary generation for one malformed bug. The `HitsPerDay` guard appears inverted against its comment: it computes when crashes are at least the minimum or the span is short, so careful review is needed before changing. Missing crash/build dependencies abort the entire load. Summary correctness depends on `lastReportedReporting` and stage names matching config.

Test signals: no dedicated test in this subset, but reporting tests create the same bug/crash/build/reporting states. Stats behavior should be tested with fixed, dup, invalid, auto-invalidated, bisection, repro, and subsystem-labeled bugs.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/stats.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/subsystem.go -->
# sources/test-tools/syzkaller/dashboard/app/subsystem.go

Purpose: automatic subsystem assignment and maintainer lookup for dashboard bugs. It refreshes bug subsystem labels from the configured `subsystem.Service`, preserves user-set labels, and exposes helpers for subsystem links and maintainer lists.

Important APIs and types: `reassignBugSubsystems`, `bugsToUpdateSubsystems`, `checkOutdatedSubsystems`, marker types `autoInference` and `updateRevision`, `updateBugSubsystems`, `logSubsystemChange`, constants `crashesForInference` and `openBugsUpdateTime`, `inferSubsystems`, `subsystemMaintainers`, `getSubsystemService`, and `subsystemListURL`.

Control flow: `reassignBugSubsystems` exits when the namespace has no subsystem service. Otherwise it queries candidate bugs in priority order: open bugs with stale revision, open bugs older than the periodic refresh interval, fixed bugs with stale revision, then all remaining stale revisions. User-subsystem bugs are not overwritten; they are checked for obsolete names and stamped with the latest revision. Auto-assigned bugs load up to seven crashes, convert guilty files and syz repro text into `subsystem.Crash` records, run `Service.TracedExtract`, and update labels/time/revision. Changes are logged when the sorted subsystem name set differs.

State and persistence: reads namespace config and datastore `Bug`/`Crash` entities plus repro text blobs. Mutates `Bug` labels, `SubsystemsRev`, and `SubsystemsTime` through `updateSingleBug`. User labels are preserved, but stale revision is still recorded to avoid repeat processing.

Dependencies and integration points: `pkg/subsystem`, `debugtracer`, App Engine datastore/logging, dashboard bug label APIs (`LabelValues`, `SetAutoSubsystems`, `hasUserSubsystems`), crash query/text helpers, and app URL generation. Cron endpoint `/cron/refresh_subsystems` in surrounding app code likely calls `reassignBugSubsystems`.

Risks: query priority can return duplicate bugs across query classes if earlier results do not exhaust `count`; callers need to tolerate possible repeated updates. Inference uses only the first guilty file per crash and up to seven crashes, so broad or later evidence can be missed. Missing repro text aborts inference. User subsystem labels that no longer exist are only logged, not repaired.

Test signals: `subsystem_test.go` validates maintainer lookup, revision and time-based refresh, closed/invalid bug refresh, preservation of user labels, no overwrite when later repros point elsewhere, and monthly subsystem report behavior built on assigned labels.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/subsystem.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/subsystem_test.go -->
# sources/test-tools/syzkaller/dashboard/app/subsystem_test.go

Purpose: integration tests for subsystem maintainer lookup, automatic subsystem refresh, user override preservation, and monthly subsystem reminder/report email generation and moderation.

Important tests: `TestSubsytemMaintainers`, `TestPeriodicSubsystemRefresh`, `TestOpenBugRevRefresh`, `TestClosedBugSubsystemRefresh`, `TestInvalidBugSubsystemRefresh`, `TestUserSubsystemsRefresh`, `TestNoUserSubsystemOverwrite`, `TestPeriodicSubsystemReminders`, `TestSubsystemRemindersModeration`, `TestSubsystemRemindersSkipModeration`, `TestSubsystemReportGeneration`, `TestSubsystemRemindersNoReport`, `TestNoRemindersWithDiscussions`, `TestSkipSubsystemReminders`, and `TestRemindersPriority`.

Control flow: setup creates builds/crashes with guilty files mapping to test subsystems, polls reports/emails, manually changes labels via inbound `#syz` email commands, advances mocked time, invokes `/cron/refresh_subsystems` and `/cron/subsystem_reports`, then asserts labels and exact email subjects/bodies. Reminder tests create multiple bugs across subsystems with different crash counts, repro levels, fix states, discussions, priorities, and no-reminder settings to validate sorting and filtering.

State and persistence: exercises datastore bug labels, subsystem revision/time fields, email sink state, monthly report history/regeneration, discussion records from `SaveDiscussion`, fix commit upload state, and user label overrides. Moderation flow first sends reports to moderation, then accepts `#syz upstream` to send public subsystem reports.

Dependencies and integration points: depends on `subsystem.go`, email parser and address context helpers, dashboard reporting APIs, cron handlers, discussion API, subsystem config in test namespaces, and `Ctx` time/config mutation helpers.

Risks: many assertions compare full email bodies, making wording/layout changes visible. Monthly report behavior is sensitive to time windows, active-vs-old crashes, discussion suppression, priority filtering, and exact recipient/moderation config. User-issued `#syz set` commands must map report references correctly even when quoted text surrounds commands.

Test signals: passing tests indicate automatic subsystem inference and monthly report generation remain stable, user subsystem choices are respected, moderation and skip-moderation hooks work, and reports avoid noise from inactive bugs, recent discussions, no-reminder labels, and unsupported subsystem configurations.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/subsystem_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/tree.go -->
# sources/test-tools/syzkaller/dashboard/app/tree.go

Purpose: determines a bug's origin/spread across configured kernel repository graphs, labels bugs with origin and missing-backport labels, creates cross-tree patch-test and fix-bisection jobs, and exposes tree-test job details.

Important APIs and types: `generateTreeOriginJobs`, `treeOriginJobDone`, `pollTreeJobResult` variants, `bugTreeContext`, `pollBugTreeJobs`, `setOriginLabels`, `selectRepoLabels`, `labelsCanBeSet`, `missingBackports`, `runRepro`/`doRunRepro`, `Bug.findResult`, `Bug.matchingTreeTests`, `loadCrashInfo`, `isCrashRelevant`, `BugTreeTest.applyPending`, `treeTestJobs`, `crossTreeBisection`, `lazyJobList.lastMatch`, `doneCrossTreeBisection`, `repoGraph`, `repoNode`, and reachability helpers.

Control flow: `generateTreeOriginJobs` runs in a datastore transaction, loads a bug, builds a context, polls tree jobs with manager capabilities, records `NextPoll`/`NeedPoll`, and returns one newly created job if any. `treeOriginJobDone` re-polls after a job finishes with `noNewJobs` so state is updated without spawning recursively. `pollBugTreeJobs` picks a relevant repro crash, clears stale tree tests when crash ID changes, applies pending job results, then combines origin-label and missing-backport workflows.

State and persistence: bug `TreeTests.List` stores per-repo test records with crash ID, repo/branch, optional merge base, pending job key, first/last/firstOK/firstCrash/error job keys. `Bug` labels are mutated for origin and missing-backport results. `Job` entities are created for patch tests and cross-tree fix bisections. Successful cross-tree bisection can set `Bug.FixCandidateJob`.

Dependencies and integration points: App Engine datastore/logging, dashboard job helpers (`addTestJob`, `fetchJob`, `saveJob`, `queryBugJobs`), crash/build helpers, active manager mapping, namespace `KernelRepo` config, `dashapi.ManagerJobs`, and full-bug info job rendering.

Key algorithms: repo graph construction maps aliases, adds inbound/outbound edges from `CommitInflow`, and rejects cycles. Reachability prioritizes merge-only paths before non-merge paths and annotates whether a reachable node is connected only through merge edges. Origin labels are selected by running repros on reachable source and destination trees, then pruning trees whose upstream/downstream neighbors also crash. Missing-backport detection looks for a prior crashing result and a later OK result on inflow trees, then verifies the current repo still crashes before labeling.

Risks: behavior depends on accurate repository aliases, branches, merge semantics, and manager `TestPatches`/`BisectFix` capabilities. Stale manager builds or changed repos make old results misleading, so `isCrashRelevant` rejects deprecated managers and changed manager trees. Retry periods for failed and fixed tree tests are hard-coded. Cross-tree bisection assumes callers do not concurrently create the same job for a manager set.

Test signals: `tree_test.go` covers downstream/lts/upstream origin labels, merge-base testing, repo changes, missing backports, bisection candidate emails, backports pages, commit polling, append config propagation, and repo graph reachability.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/tree.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/tree_test.go -->
# sources/test-tools/syzkaller/dashboard/app/tree_test.go

Purpose: integration and unit tests for cross-tree bug presence analysis, missing-backport detection, cross-tree fix bisection, repo graph reachability, and test harness behavior for tree-origin jobs.

Important tests and fixtures: `TestTreeOriginDownstream`, `TestTreeOriginDownstreamEmail`, `TestTreeOriginBetterReport`, `TestTreeOriginLts`, `TestTreeOriginLtsBisection`, `TestNonfinalFixCandidateBisect`, `TestTreeBisectionBeforeOrigin`, `TestTreeOriginErrors`, `TestOriginTreeNoMerge*`, `TestTreeOriginRepoChanged`, `TestOriginNoNext*`, `TestMissing*Backport`, `TestTreeConfigAppend`, `TestRepoGraph`, and `TestRepoGraphMergeFirst`. Fixture types include `treeTestCtx`, `treeTestEntry`, `treeTestResult`, and `treeTestEntryPeriod`.

Control flow: tests configure namespace `KernelRepo` graphs, upload builds/crashes with repros, define synthetic per-repo job outcomes by day, advance time through `moveToDay`, poll and complete patch-test jobs, then assert bug labels, emails, full-bug tree job lists, bisection job requests, backports page visibility, commit polling, and follow-up emails after commit upload. `treeTestCtx.doJob` maps `JobPollResp` repo/merge-base fields to expected fixture entries and returns OK, crash, or error results.

State and persistence: uses datastore bugs/jobs/builds/crashes through the dashboard test harness, email sink for origin and backport messages, bug label state, bisection fix candidate state, and namespace repo config mutations. The tests check that old tree-test records are reused or cleared when the tested crash/repo changes.

Dependencies and integration points: relies on `tree.go`, reporting/email flows, `dashapi.ManagerJobs`, admin/public HTTP access checks for `/tree-tests/backports` and related namespace pages, commit polling/upload APIs, and test helpers from `util_test.go`.

Risks: the tests intentionally model complex time-dependent workflows; small changes to retry windows, label selection, result ordering, email wording, or bisection eligibility can fail many assertions. Fixture matching sorts repo/branch/merge-base fields, so it verifies semantic targets rather than exact field order. Public/admin visibility expectations for backports pages are part of the security contract.

Test signals: passing tests demonstrate that repo graph logic, origin labels, missing-backport labels, cross-tree bisection creation/dedup/retry, fix-candidate display, and notification/commit flows remain coherent.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/tree_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/util_test.go -->
# sources/test-tools/syzkaller/dashboard/app/util_test.go

Purpose: central App Engine/dashboard test harness for the `dashboard/app` package. It creates isolated app instances, mocked time/email, API clients, HTTP helpers, datastore loaders, config patchers, Spanner test setup, and common assertions.

Important APIs and types: `Ctx`, `NewCtx`, `NewSpannerCtx`, DDL loading/sorting helpers, assertion helpers, `Close`, time/config mutation helpers (`advanceTime`, `setSubsystems`, `setCoverageMocks`, `setKernelRepos`, `setNoObsoletions`, `updateReporting`, `decommission*`, `setWaitForRepro`, `SetAIConfig`), HTTP helpers (`GET`, `AuthGET`, `POST`, `POSTForm`, `AuthPOSTForm`, `ContentType`, `httpRequest`), datastore loaders, email helpers, `apiClient`, `makeClient`, API polling helpers, `incomingEmail`, `createAIJob`, `initMocks`, request-context mapping, and config replacement helpers.

Control flow: `NewCtx` starts `aetest.NewInstance`, initializes clients with dashboard keys, registers an initial request, and sets mocked time to 2000-01-01. HTTP/API helpers register requests so app code can recover the active `Ctx` and mocked time. `Close` validates rendered pages, drains email and external report queues, renders AI job pages when needed, closes clients, unregisters context, and validates global config. `NewSpannerCtx` creates a unique fake Spanner DB URI and applies migrations loaded from `aidb/migrations`.

State and persistence: maintains per-test App Engine datastore instance, mocked time, email sink channel, optional context transformer for config/mocks, request ID to context map guarded by a mutex, and generated API clients. It reads/writes datastore entities indirectly through app handlers and loader helpers. It patches global functions in `initMocks` for time, email sending, and max crash count.

Dependencies and integration points: App Engine `aetest`, datastore, mail, dashboard API client, `dashapi`, Spanner admin test DB, coverage DB client, covermerger, email parser, subsystem service, AI DB, testify, and the package's HTTP `DefaultServeMux`.

Risks: tests are skipped when `dev_appserver.py` is unavailable unless CI-like env is set; this can hide coverage locally. Request-context mapping is global and must unregister to avoid cross-test contamination. `Close` performs broad invariant checks only when `transformContext == nil`, so tests using config transforms bypass some final rendering/drain checks. DDL splitting assumes semicolons only terminate statements. Global mock functions affect the whole package test process.

Test signals: this file enables most integration tests in the package. Failures here usually indicate test environment setup, config mutation, request registration, or harness-level cleanup issues rather than a single feature regression.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/util_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/android/generate.sh -->
# sources/test-tools/syzkaller/dashboard/config/android/generate.sh

Purpose: generates an Android kernel config file from an Android kernel checkout, currently supporting kernel version `5.4`.

Important APIs and commands: Bash script with `usage`, arguments `SRC_DIR` and `VERSION`, variables `KERNEL_SOURCE`, `DEFCONFIG`, `SCRIPT_DIR`, `CC`, sourced `../util.sh`, and helper calls `util_add_usb_bits` and `util_add_syzbot_bits`.

Control flow: validates that the Android GKI defconfig exists, selects a prebuilt clang path for `5.4`, sources shared config utility functions, copies `gki_defconfig` to `.config`, adds Android USB and syzbot config fragments, merges `config-bits` with `scripts/kconfig/merge_config.sh -m`, runs `make olddefconfig`, and copies the resulting `.config` to `config-5.4`.

State and persistence: writes into the Android kernel source tree `.config` and the dashboard config directory output file. It also depends on mutable environment from `util.sh` such as `MAKE_VARS`.

Dependencies and integration points: Android kernel source layout with `common`, prebuilts clang path for 5.4, Linux kernel kconfig scripts, make, and dashboard config utility scripts/fragments. Intended for maintainers refreshing checked-in Android kernel configs.

Risks: hard-coded compiler path and single supported version make it fragile for newer Android branches. `set -eux` is useful for fail-fast but can expose paths/commands in logs. Arguments are not quoted consistently around `cd`, `cp`, and script paths, so spaces in checkout paths would break. It overwrites `.config` in the kernel tree.

Test signals: no automated test in this subset. Successful run producing `config-5.4` after `olddefconfig` is the practical validation.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/android/generate.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/freebsd/syz-ci-service.sh -->
# sources/test-tools/syzkaller/dashboard/config/freebsd/syz-ci-service.sh

Purpose: FreeBSD rc.d service wrapper for running `syz-ci` at boot.

Important APIs and variables: rc.d metadata `PROVIDE: syz_ci`, `REQUIRE: LOGIN`, `/etc/rc.subr`, variables `command`, `name`, `pidfile`, `rcvar`, `start_cmd`, `stop_cmd`, and configurable rc.conf variables `syz_ci_enable`, `syz_ci_chdir`, `syz_ci_flags`, `syz_ci_log`, and `syz_ci_path`.

Control flow: `syz_ci_start` changes to the configured working directory and launches `syz-ci` under `daemon -f`, redirecting output to the configured log and writing a pidfile. `syz_ci_stop` reads the pidfile, sends `SIGINT`, and waits up to 120 seconds with `pwait`. The script loads rc config and dispatches `run_rc_command "$1"`.

State and persistence: persistent state is the pidfile under `/var/run` and the configured syz-ci log. The service itself does not manage syz-ci state files.

Dependencies and integration points: FreeBSD rc system, `daemon`, `pwait`, `/usr/local/bin` in PATH for Go, an installed syz-ci binary, and rc.conf setup documented in comments.

Risks: `stop` assumes pidfile exists and contains a valid pid; missing/stale pidfiles may produce confusing failures. Variables are not always quoted in command arguments. The service uses `daemon -f`, so supervision semantics depend on FreeBSD daemon behavior and syz-ci signal handling.

Test signals: no automated tests. Operational validation is `service syz_ci start`, pidfile creation, log writes, and graceful `service syz_ci stop`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/freebsd/syz-ci-service.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/allyes.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/allyes.yml

Purpose: config fragment for broad `allyes`-style Linux builds that disables known build/boot hazards, heavyweight debugging, and self-tests to make maximally enabled kernels usable for syzbot fuzzing.

Important keys: top-level `config` list with Kconfig symbols and conditional tags. It disables problematic boot/build options such as `SERIAL_NUVOTON_MA35D1_CONSOLE`, `MAXSMP`, MSI-related drivers, `GPIB_CB7210`, numerous sanitizers/debug features, fault injection, KUnit/runtime tests, and many subsystem self-tests.

Control flow: consumed by the syzkaller dashboard config generator/merger; entries either force symbols on/off, append command-line text, or use modifiers like `[override]`. There is no executable flow in the file itself.

State and persistence: declarative only. It contributes to generated kernel `.config` output and boot command line through `CMDLINE` append.

Dependencies and integration points: Linux Kconfig symbol names across versions, base config fragments, and syzkaller's YAML config-bit parser. Comments document why specific features are disabled due to boot slowness, runtime crashes, or build failures.

Risks: symbol names age quickly; disabled lists can silently stop matching or hide coverage. Overriding sanitizers/debug/fault-injection accelerates boot but reduces bug-finding depth. The broad MSI disable block is intentionally imprecise and may mask useful drivers.

Test signals: generated allyes configs should build and boot. Failures are usually kernel build errors, boot hangs, or syzbot infrastructure timeouts.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/allyes.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/android-5.10.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/android-5.10.yml

Purpose: Android 13 5.10 LTS kernel fragment selecting the Android common repo/tag, GKI defconfig, and Android-5.10-specific mitigations.

Important keys: `kernel.repo` is `https://android.googlesource.com/kernel/common`, `kernel.tag` is `3a582928e6d19`, `shell` runs `make gki_defconfig`, and `config` disables `IO_URING` plus handles Android's `KASAN_STACK_ENABLE` to `KASAN_STACK` rename with override tags.

Control flow: declarative input to config generation. The generator checks out the given tag, runs the shell defconfig command, then applies config entries.

State and persistence: contributes selected repo/tag and final `.config`; no local state itself.

Dependencies and integration points: Android common kernel, GKI config, syzkaller config-bit parser, and version/tag labels. The io_uring comment documents a policy decision based on unbackportable 5.10 bugs.

Risks: pinning an old tag may miss security/stability updates. Disabling `IO_URING` reduces syscall coverage but avoids known noisy/unfixed crashes. KASAN rename overrides are branch-specific and may need removal when branch config changes.

Test signals: successful Android 5.10 build/boot and reduced io_uring false-positive/noise rate.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/android-5.10.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/android-5.15.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/android-5.15.yml

Purpose: Android 13 5.15 LTS kernel source and defconfig selector.

Important keys: `kernel.repo` points to Android common, `kernel.tag` is `241da2ad56013`, and `shell` runs `make gki_defconfig`.

Control flow: the config pipeline checks out the tag and starts from GKI defconfig before applying shared Android/base fragments.

State and persistence: declarative only; affects generated kernel source selection and `.config`.

Dependencies and integration points: Android common 5.15 branch/tag and the dashboard Linux config generator.

Risks: no branch-specific config overrides are present, so this relies entirely on shared fragments. If Android 5.15 needs special disables, build/boot failures will surface downstream.

Test signals: generated Android 5.15 config should build and boot under syzbot managers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/android-5.15.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/android-5.4.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/android-5.4.yml

Purpose: Android 12 5.4 LTS kernel source and defconfig selector.

Important keys: Android common repo, tag `9d0640602d7e666873e78b3d1877b8eadf529027`, and `make gki_defconfig`.

Control flow: declarative selection of checkout and initial config before shared fragments are merged.

State and persistence: contributes repo/tag/defconfig to generated kernel configs.

Dependencies and integration points: Android common 5.4 branch, GKI defconfig, config generator, and `generate.sh` for Android 5.4 config generation.

Risks: old branch compatibility with current config fragments and toolchains is the primary risk. No local overrides are present in this fragment.

Test signals: successful generated config, build, and boot on Android 5.4 syzbot setup.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/android-5.4.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/android-6.1.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/android-6.1.yml

Purpose: Android 14 6.1 kernel source and defconfig selector.

Important keys: Android common repo, tag `80ac9236949e7`, and `make gki_defconfig`.

Control flow: consumed by the config generator as checkout metadata and base defconfig command.

State and persistence: declarative only.

Dependencies and integration points: Android common 6.1 branch/tag, GKI defconfig, shared Android/base fragments.

Risks: no branch-specific overrides; shared fragments must handle symbol availability and Android branch quirks.

Test signals: generated config should build and boot for Android 6.1 fuzzing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/android-6.1.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/android-6.12.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/android-6.12.yml

Purpose: Android 16 6.12 kernel source selector with a Rust Binder boot-argument tweak.

Important keys: Android common repo, tag `5150a2974c100f8aa5cbfa9a09d804ee4369f61e`, `make gki_defconfig`, and `CMDLINE: [append, "binder.impl=rust"]`.

Control flow: generator checks out/tag configures GKI, then appends Binder implementation selection to the kernel command line.

State and persistence: declarative; affects generated config and boot command line.

Dependencies and integration points: Android 6.12 common kernel, GKI defconfig, Android subsystem fragment where Rust Binder can be enabled with tags.

Risks: forcing `binder.impl=rust` depends on kernel support and matching `ANDROID_BINDER_IPC_RUST` config. If the branch changes default Binder implementations, this can alter fuzzing coverage or boot behavior.

Test signals: build/boot should confirm Rust Binder availability and stable boot with the appended command line.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/android-6.12.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/android-subsystems.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/android-subsystems.yml

Purpose: enables Android-specific subsystems on full, non-basefile Android kernels that are absent from `gki_defconfig` but important for fuzzing Android behavior.

Important keys: config list enables `INCREMENTAL_FS`, USB configfs/gadget functions, Android accessory/audio aliases split across pre/post 6.12 symbol names, Binder IPC selection, optional Rust Binder, and `ANDROID_BINDER_DEVICES`.

Control flow: declarative config fragment with version and feature tags such as `[-v6.12]`, `[v6.12]`, `[android-6.12]`, and `[rust]`.

State and persistence: contributes Kconfig values and Binder device string to generated configs.

Dependencies and integration points: Android common kernel Kconfig symbol history, USB gadget/configfs, Binder, syzkaller config tags, and Android full-kernel manager configs.

Risks: symbol rename handling must stay synchronized with Android branches. Disabling classic Binder IPC for `android-6.12` while enabling Rust Binder under `rust` requires tag combinations to be correct; wrong tags can leave Binder unavailable.

Test signals: generated Android full configs should expose USB gadget functions and Binder devices and boot on target managers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/android-subsystems.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/android.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/android.yml

Purpose: common config bits for all Android kernels tested by syzbot.

Important keys: enables `KERNEL_GZIP`, appends Android GKI command-line settings for pressure and memory cgroups, disables `KVM_WERROR`, sets `SERIAL_8250_RUNTIME_UARTS: 4`, enables `NET_VENDOR_GOOGLE`, and overrides `BOOTPARAM_SOFTLOCKUP_PANIC`.

Control flow: declarative fragment merged after branch defconfig.

State and persistence: affects generated kernel `.config` and command line.

Dependencies and integration points: Android GKI defaults, syzbot distro package availability, qemu serial behavior, Google network drivers, and shared softlockup panic policy.

Risks: `KERNEL_GZIP` trades off compression behavior because lz4 is unavailable in syzbot distros. Serial UART count is a boot workaround that may be branch/platform-specific. Appended cgroup args must remain compatible with kernel versions.

Test signals: Android kernels build without missing lz4, boot under qemu, and retain softlockup panic behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/android.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/android14-5.15.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/android14-5.15.yml

Purpose: Android 14 5.15 kernel source and defconfig selector.

Important keys: Android common repo, tag `0772c040aea2`, and `make gki_defconfig`.

Control flow: declarative checkout and defconfig metadata for the config generator.

State and persistence: no runtime state; contributes to generated configs.

Dependencies and integration points: Android 14 5.15 common kernel branch, GKI defconfig, shared Android fragments.

Risks: no local overrides, so build/boot stability depends on shared fragments and the pinned tag.

Test signals: successful Android 14 5.15 build and boot in syzbot.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/android14-5.15.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/apparmor.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/apparmor.yml

Purpose: selects AppArmor as the primary Linux security module for configs that fuzz AppArmor behavior.

Important keys: disables SELinux and Smack, enables `SECURITY_APPARMOR`, introspection policy on v5.19+, hashing/debug/assert options, `DEFAULT_SECURITY_APPARMOR`, and sets the `LSM` order string ending with AppArmor and BPF.

Control flow: declarative Kconfig fragment.

State and persistence: modifies generated kernel security module configuration.

Dependencies and integration points: Linux security module Kconfig, LSM ordering, syzkaller security-manager configurations.

Risks: LSM ordering is semantically important; missing a required LSM in the string can change boot/runtime behavior. Debug/assert options increase coverage but may affect performance and noise.

Test signals: generated kernels should boot with AppArmor as default security module and expose AppArmor policy/debug surfaces.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/apparmor.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/arm.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/arm.yml

Purpose: ARM32 kernel config fragment for syzbot, selecting vexpress/kvm guest defaults and enabling ARM-specific coverage while avoiding known boot/parser hazards.

Important keys: shell runs `make vexpress_defconfig` and `make kvm_guest.config`. Config appends root/console/vmalloc command line, enables `ARM_LPAE`, frame-pointer unwinder, verbose backtraces, highmem options, big.LITTLE/NEON/VFP, flat binary formats, selected device drivers, and disables `HARDEN_BRANCH_PREDICTOR`.

Control flow: shell commands establish a base config; config list is then merged with version/tag conditionals such as `[-v6.19]`, `[-baseline]`, and `[-onlyusb]`.

State and persistence: contributes ARM-specific `.config` and command line.

Dependencies and integration points: ARM vexpress qemu platform, kernel version symbol history, syzbot parser expectations for oops stack traces, and known issue #3249 around `smp_processor_id`.

Risks: KASAN inline and unwinder choices are fragile on ARM32. Disabling branch hardening avoids a known fuzzing blocker but reduces mitigation coverage. ARM_LPAE selection intentionally excludes non-LPAE coverage.

Test signals: ARM kernels should build, boot under qemu, produce parseable oopses, and avoid the known preemptible `smp_processor_id` blocker.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/arm.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/arm64.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/arm64.yml

Purpose: common ARM64 config fragment for syzbot.

Important keys: optional shell defconfig/kvm guest commands gated by `[-nodefconfig]`, command-line root/console settings, command-line source compatibility symbols across versions, ARM64 features `TAGGED_ADDR_ABI`, `PMEM`, `MTE`, and vexpress clock/platform symbols disabled for `arm64_gce`.

Control flow: establishes defconfig unless `nodefconfig` tag is set, then applies config entries with version/platform guards.

State and persistence: affects generated ARM64 `.config` and boot command line.

Dependencies and integration points: ARM64 qemu/GCE platforms, kernel command-line Kconfig symbol history, and memory-tagging coverage.

Risks: command-line symbol changes (`CMDLINE_EXTEND`, `CMDLINE_FROM_BOOTLOADER`) are version-sensitive. Enabling MTE/tagged address support changes syscall/runtime behavior and requires compatible hardware/emulation.

Test signals: ARM64 configs should build and boot on both emulated and GCE variants, with expected command-line handling.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/arm64.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/arm64_emu.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/arm64_emu.yml

Purpose: large ARM64 emulation-focused fragment that disables broad sets of hardware drivers and platform menus to reduce qemu boot time, build size, and irrelevant crash noise.

Important keys: top-level `config` list disables PCMCIA, display/DRM panels, SPI/MMC/PWM/RC/HWMON/regulator/watchdog/memstick/COMEDI, many platform `ARCH_*` selections, PCI controller drivers, special HID drivers, bus devices, I2C controllers, MFD drivers, camera sensors, backlight/LCD drivers, RPMSG, ADC/light/pressure sensors, PHY drivers, and additional platform-specific blocks through the end of the file.

Control flow: declarative deny-list applied after ARM64 base config. Comments group related Kconfig menu families, making the file a curated pruning layer rather than a feature-enabling profile.

State and persistence: only affects generated `.config`; no executable state.

Dependencies and integration points: ARM64 defconfig symbol names across kernel versions, qemu emulation performance constraints, syzkaller config parser, and other ARM64 fragments such as `arm64.yml`.

Risks: a huge explicit disable list is maintenance-heavy. Renamed/removed symbols can become inert, while new hardware menu symbols may reintroduce boot slowness. Disabling whole driver classes improves signal-to-noise but loses coverage for emulated/virtual devices that could be fuzzable. Some symbols are duplicated with other fragments, so override order matters.

Test signals: practical validation is ARM64 emulated kernel build and boot time, plus lower rate of unrelated platform-driver crashes. There are no direct unit tests for this YAML.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/arm64_emu.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/arm64_gce.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/arm64_gce.yml

Purpose: ARM64 GCE pruning fragment that disables noisy or unsupported drivers/platforms to make cloud ARM64 fuzzing practical.

Important keys: disables sound, several DRM/GPU drivers, Hisilicon networking, storage filesystems/drivers, many ARM64 platform `ARCH_*` selections, remaining clock drivers, camera/video, Mellanox/Intel networking, Atheros WLAN, and selects size optimization over performance.

Control flow: declarative config list layered on ARM64 GCE builds.

State and persistence: affects generated `.config` only.

Dependencies and integration points: ARM64 GCE manager configs, Linux platform Kconfig menus, and shared ARM64 fragment that excludes some vexpress-only symbols when `arm64_gce` tag is present.

Risks: disabling broad vendor/platform support can hide bugs in cloud-available hardware paths if assumptions change. `CC_OPTIMIZE_FOR_SIZE` may alter compiler behavior and coverage/performance tradeoffs. Symbol list needs periodic refresh as ARM64 platforms are added.

Test signals: ARM64 GCE kernels should build, boot, and avoid known irrelevant platform-driver failures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/arm64_gce.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/base.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/base.yml

Purpose: foundational Linux kernel config fragment required by syzbot across most kernels. It enables debugging, coverage, namespace/sandbox support, deterministic boot behavior, text/debug metadata, and disables unsafe or noisy facilities.

Important keys: top-level `verbatim` preserves special debug symbols. `config` enables `EXPERT`, `DEBUG_KERNEL`, namespaces, cgroups, KALLSYMS, debug checks, KCOV/KCOV comparisons, debugfs, fault injection, root filesystem/boot support, ext4, and selected platform/network basics. It disables `WERROR`, tracing slowdown features, CPU mitigations, dangerous `/dev/mem` style devices, Magic SysRq, KGDB, Hyper-V/Xen, legacy USB gadget drivers, samples, and Rust by default.

Control flow: declarative fragment with many version/arch/tag conditions (`v6.1`, `-arm`, `-s390`, `-kmsan`, `clang`, `x86_64`, etc.). The config generator merges this with arch/product fragments and applies `CMDLINE` values.

State and persistence: produces generated `.config` and kernel command line. It is central to persistence of syzbot's fuzzing assumptions because many managers inherit it.

Dependencies and integration points: Linux Kconfig across many versions, syzkaller executor sandbox requirements, KCOV coverage, crash parser expectations, qemu boot images, and feature-tag semantics in dashboard config generation.

Risks: this file has high blast radius. Disabling mitigations/tracing improves fuzzing speed but changes production-like behavior. Enabling fault injection and debug checks increases bug-finding but can add noise. Version guards must track symbol renames/removals; wrong guards can break builds. The long `CMDLINE` includes many runtime knobs, so appending incompatible args can break boot.

Test signals: every generated syzbot Linux config effectively validates this file through build, boot, executor sandbox setup, KCOV availability, and crash report quality.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/base.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/baseline.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/baseline.yml

Purpose: trims baseline Linux configs below defconfig by disabling subsystems that are not needed for baseline fuzzing.

Important keys: disables DRM, integrity/EVM/IMA families with weak tags, joystick/LED/mouse/tablet/touchscreen, KCOV with weak tags, Macintosh/PS2 mouse, NetLabel, PCCARD, `PREEMPT_VOLUNTARY` except ARM, RFKILL, sound, TPM, wireless, and related wireless extension symbols.

Control flow: declarative list applied to baseline-tagged generated configs.

State and persistence: modifies generated `.config` only.

Dependencies and integration points: baseline manager profiles, Kconfig weak override semantics, and architecture tags.

Risks: weak disables depend on generator semantics; if dependencies re-enable symbols strongly, baseline size/noise may grow. Disabling KCOV in baseline changes coverage expectations compared with full fuzzing configs. Excluding ARM from `PREEMPT_VOLUNTARY` reflects arch defaults and must be revisited if defaults change.

Test signals: baseline kernels should be smaller/faster while still booting and supporting intended baseline tasks.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/baseline.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/bluetooth.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/bluetooth.yml

Purpose: enables Bluetooth stack and common controller/protocol drivers for Bluetooth fuzzing.

Important keys: `BT`, BR/EDR, RFCOMM/TTY, BNEP filters, HIDP, LE, HS conditionals, 6LoWPAN, LEDs, Microsoft extensions, USB/uart/virtual HCI drivers, and newer LE/poll-sync options with version guards.

Control flow: declarative feature-enabling fragment.

State and persistence: affects generated `.config`.

Dependencies and integration points: Linux Bluetooth Kconfig, USB/UART HCI driver availability, syzkaller Bluetooth descriptions and manager profiles.

Risks: version guards (`BT_CMTP`, `BT_HS`, `BT_LE_L2CAP_ECRED`, `BT_HCIBTUSB_POLL_SYNC`) need maintenance. Enabling broad Bluetooth support increases attack surface and boot/device initialization paths.

Test signals: configs should build with Bluetooth enabled and syzkaller should see relevant Bluetooth devices/syscalls.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/bluetooth.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/bpf.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/bpf.yml

Purpose: enables BPF syscall and optional JIT/preload coverage for BPF-focused syzbot managers.

Important keys: `BPF_SYSCALL`, tag-gated `BPF_JIT` and `BPF_JIT_ALWAYS_ON`, snapshot-gated `BPF_STREAM_PARSER`, and x86_64 v5.10-gated `BPF_PRELOAD`/`BPF_PRELOAD_UMD`.

Control flow: declarative Kconfig fragment with feature and arch/version tags.

State and persistence: changes generated `.config` for BPF managers.

Dependencies and integration points: Linux BPF Kconfig, syzkaller BPF programs, manager tags such as `bpfjit` and `snapshot`, and host/cross build dependencies for BPF preload.

Risks: BPF JIT changes execution and bug surface compared with interpreter mode, so it is tag-limited. BPF preload cross-build dependencies are known fragile and intentionally limited to x86_64.

Test signals: BPF-enabled kernels should build and expose BPF syscall/JIT paths as expected for selected managers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/bpf.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-5.10.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-5.10.yml

Purpose: ChromeOS 5.10 kernel source and prepareconfig selector.

Important keys: ChromiumOS kernel repo, tag `ea6af77b55e49ce0cfbdd5543fe75fc8744cbd92`, and shell commands using `CHROMEOS_KERNEL_FAMILY=chromeos chromeos/scripts/prepareconfig chromiumos-x86_64-generic ${BUILDDIR}/.config` followed by `make olddefconfig`.

Control flow: generator checks out the tag and runs ChromeOS prepareconfig to seed `.config`.

State and persistence: declarative source/defconfig metadata for generated configs.

Dependencies and integration points: ChromiumOS kernel tree layout, prepareconfig script, `BUILDDIR`, and shared ChromeOS fragments.

Risks: prepareconfig command and board name are branch-specific. Pinned tag can become stale relative to ChromeOS branch fixes.

Test signals: successful ChromeOS 5.10 config generation, build, and boot.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-5.10.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-5.15.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-5.15.yml

Purpose: ChromeOS 5.15 kernel source and prepareconfig selector.

Important keys: ChromiumOS kernel repo, tag `e931c5c3244d7ebba8856dc6aed54a5d1a85975e`, prepareconfig for `chromiumos-x86_64-generic`, and `make olddefconfig`.

Control flow: declarative checkout and shell setup before shared fragments.

State and persistence: contributes generated config base.

Dependencies and integration points: ChromeOS 5.15 kernel tree, prepareconfig tooling, shared ChromeOS subsystem/common fragments.

Risks: no local overrides; any ChromeOS 5.15-specific build break must be handled elsewhere.

Test signals: generated config builds and boots on ChromeOS 5.15 managers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-5.15.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-5.4.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-5.4.yml

Purpose: ChromeOS 5.4 kernel source selector with a branch-specific DRM workaround.

Important keys: ChromiumOS kernel repo, tag `659b005fb0dcc1747094201a14945a6af734be50`, prepareconfig for `chromiumos-x86_64`, `make olddefconfig`, and `DRM_I915: n`.

Control flow: generator prepares the 5.4 ChromeOS config and disables `DRM_I915` to avoid a documented build error.

State and persistence: affects generated config only.

Dependencies and integration points: ChromeOS 5.4 tree, prepareconfig script, shared fragments, and DRM Kconfig/build behavior.

Risks: disabling i915 removes important GPU coverage but avoids build failure. The workaround should be revisited if the branch/compiler changes.

Test signals: build should avoid the documented `i915_selftest.h` statement-with-no-effect error.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-5.4.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-6.1.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-6.1.yml

Purpose: ChromeOS 6.1 kernel source selector with io_uring enabled.

Important keys: ChromiumOS kernel repo, tag `ebea4d55ca782539782702c2e5e86033b9f86bd2`, prepareconfig for `chromiumos-x86_64-generic`, `make olddefconfig`, and config `IO_URING`.

Control flow: checkout/prepareconfig followed by config merge enabling io_uring.

State and persistence: declarative generated-config input.

Dependencies and integration points: ChromeOS 6.1 tree, prepareconfig, and syzkaller io_uring coverage.

Risks: explicitly enabling io_uring increases coverage but can expose branch-specific io_uring bugs. If prepareconfig already sets a conflicting value, merge order matters.

Test signals: ChromeOS 6.1 configs should build/boot and expose io_uring.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-6.1.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-6.6.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-6.6.yml

Purpose: ChromeOS 6.6 kernel source selector with io_uring enabled.

Important keys: ChromiumOS kernel repo, tag `3f6e68d242bb045866ae04a9f5890aacd987d2bb`, ChromeOS prepareconfig command, `make olddefconfig`, and `IO_URING`.

Control flow: declarative checkout and shell preparation, then config merge.

State and persistence: generated config input only.

Dependencies and integration points: ChromeOS 6.6 tree, prepareconfig, io_uring fuzzing coverage.

Risks: pinned tag freshness and branch-specific io_uring stability. Explicit enablement may conflict with future branch defaults.

Test signals: successful build/boot and io_uring availability on ChromeOS 6.6 managers.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-6.6.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-subsystems.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-subsystems.yml

Purpose: enables ChromeOS-specific and device-relevant subsystems on full ChromeOS kernels beyond what prepareconfig enables.

Important keys: package list/configfs, ESD/Incremental FS conditionals, Virtio FS/WL, USB configfs gadget functions, BinderFS/devices, KVM/AMD/Intel virtualization, vsockets, virtio block/net/console/pci, and `VIRTUALIZATION`.

Control flow: declarative config fragment with branch guards like `[-chromeos-6.6]`, `[chromeos-5.10]`, and generic symbol enables.

State and persistence: generated `.config` and Binder device string.

Dependencies and integration points: ChromeOS kernel backports, USB gadget stack, Android Binder on ChromeOS, virtualization stack, and syzkaller manager tags.

Risks: ChromeOS branches diverge; guards for ESD/Incremental FS must track feature removal/addition. Enabling virtualization and many USB gadget functions broadens coverage but can introduce build/boot noise.

Test signals: full ChromeOS configs should include ChromeOS-specific filesystems, Binder, USB gadget, and virtio/KVM surfaces and still boot.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos-subsystems.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos.yml

Purpose: common config bits for all ChromeOS kernels.

Important keys: disables `SECURITY_CHROMIUMOS_NO_UNPRIVILEGED_UNSAFE_MOUNTS`, appends ChromeOS boot command-line flags, disables several cros_ec sensor drivers due to build warnings, sets `FRAME_WARN: 0`, and overrides `BOOTPARAM_SOFTLOCKUP_PANIC`.

Control flow: declarative fragment layered on ChromeOS branch configs.

State and persistence: affects generated `.config` and command line.

Dependencies and integration points: ChromeOS-specific security options, syzkaller executor mount setup, ChromeOS EC sensor drivers, and softlockup panic policy.

Risks: disabling ChromeOS unprivileged mount protection is necessary for executor setup but changes security posture. Historical command-line flags have unclear origins and may need pruning. Sensor build warnings may be fixed in later branches, so disables can hide coverage.

Test signals: ChromeOS kernels should permit syzkaller tmpfs mounts, build without the noted cros_ec fallthrough errors, and boot with expected softlockup behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/chromeos.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/comedi.yml -->
# sources/test-tools/syzkaller/dashboard/config/linux/bits/comedi.yml

Purpose: enables COMEDI subsystem coverage, including legacy manual device configuration and selected USB, misc, PCI, PCMCIA, and x86 ISA drivers.

Important keys: appends `comedi.comedi_num_legacy_minors=4` to the command line, enables `COMEDI`, USB drivers (`COMEDI_DT9812`, `NI_USB6501`, `USBDUX*`, `VMK80XX`), misc drivers, selected PCI/PCMCIA drivers, and many ISA drivers gated to `x86_64` with `ISA_BUS`.

Control flow: declarative Kconfig fragment.

State and persistence: affects generated `.config` and boot command line.

Dependencies and integration points: Linux COMEDI Kconfig, syzkaller COMEDI descriptions/ioctls, USB/PCI/ISA bus support, and x86_64 manager profiles.

Risks: broad legacy driver enablement can expose old code with unusual dependencies and boot/build issues. ISA gating avoids non-x86 architectures but still relies on x86_64 Kconfig availability. The legacy minors command-line setting changes device namespace and must match fuzzing expectations.

Test signals: generated kernels should build with COMEDI drivers and expose configurable COMEDI devices/ioctls for fuzzing.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/config/linux/bits/comedi.yml -->
