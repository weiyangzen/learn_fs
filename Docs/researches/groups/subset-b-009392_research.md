# subset-b-009392 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/asset_storage.go -->
# sources/test-tools/syzkaller/dashboard/app/asset_storage.go

Purpose: implements dashboard-side storage and lifecycle policy for uploaded build and crash assets. It appends new assets to `Build` entities, reports currently retained asset URLs to clients, periodically deprecates stale assets, and renders asset metadata into `dashapi.Asset` lists used by bug reports and UI/API responses.

Important APIs and types: `appendBuildAssets` loads a build in a transaction and appends each incoming `Asset`, allowing partial success if at least one upload is accepted. `Build.AppendAsset` validates asset type metadata via `pkg/asset.GetTypeDescription` and enforces single-instance types unless the type allows multiples. `queryNeededAssets`, `neededBuildURLs`, and `neededCrashURLs` scan datastore projections for asset download URLs. `buildAssetDeprecator` and `crashAssetDeprecator` hold deprecation state and implement `batchProcessBuilds`, `batchProcessCrashes`, `needThisBuildAsset`, `needThisCrashAsset`, and transactional update helpers. `queryLatestManagerAssets` returns the latest recent asset per manager for a type. `createAssetList` converts persisted `Asset` rows into API-facing assets, including fsck log links, reporting-priority sorting, and duplicate-title disambiguation.

Control flow: `/cron/deprecate_assets` iterates all namespaces for build asset processing, then processes crash assets globally. Build processing orders by `AssetsLastCheck`, evaluates each asset, filters unneeded URLs, and updates the entity timestamp. Fresh build assets are always kept for 14 days. Coverage reports use weekly archive thinning: older same-type reports can be dropped when a newer report exists in the same ISO week. Normal and failed build assets are retained if linked crashes belong to open or recently closed bugs, or if the build is the latest for its manager. Crash mount assets are retained while the parent bug is open or closed within the 30-day retention window.

State and persistence: datastore `Build` and `Crash` entities store `Assets` plus `AssetsLastCheck`. The deprecator caches queried bug keys and latest manager builds in memory for one handler run. Updates run in App Engine datastore transactions. Asset bytes are not deleted here; the dashboard only drops references and exposes the remaining URLs through `NeededAssetsList`, leaving external storage cleanup to clients.

Dependencies and integration points: depends on dashapi asset types, syzkaller asset metadata, target descriptions for titles, App Engine datastore/logging/context, and shared dashboard functions such as `loadBuild`, `buildKey`, `lastManagerBuild`, `externalLink`, and `timeNow`. It feeds email/report rendering and manager UI coverage links.

Risks: projection queries over repeated `Assets` fields can return partial entity data and require careful interpretation. `appendBuildAssets` may return success after only one accepted asset, which is intentional but may surprise callers. `buildArchivePolicy` only examines the first queried newer build and then scans its assets, so datastore ordering behavior matters. `updateBuild`'s transaction closure receives `ctx` but calls several functions with `ad.ctx`, which is consistent with local style but easy to misuse if transaction context semantics change. Asset deletion is reference-only, so external object lifecycle must not assume this code deletes blobs.

Test signals: `asset_storage_test.go` covers build asset lifetimes, coverage report display and weekly thinning, fresh latest-build retention, crash mount asset reporting including fsck log links, and deprecation after invalidation plus 31 days.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/asset_storage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/asset_storage_test.go -->
# sources/test-tools/syzkaller/dashboard/app/asset_storage_test.go

Purpose: integration tests for the asset storage lifecycle in `asset_storage.go`, including email rendering, UI exposure, API listing, and retention/deprecation behavior.

Important tests and helpers: `TestBuildAssetLifetime` uploads build assets, verifies they appear in a first bug report and `NeededAssetsList`, invalidates the bug, and confirms only the HTML coverage report survives after the closed-bug retention period. `TestCoverReportDisplay` verifies manager UI coverage links are absent before upload, then point to the latest coverage report per manager. `TestCoverReportDeprecation` constructs weekly coverage-report upload timelines and asserts that after the two-week embargo only one coverage report per ISO week remains. `TestFreshBuildAssets` confirms latest-build and fresh-asset protection for build assets without crashes. `TestCrashAssetLifetime` verifies multiple crash mount assets, duplicate title numbering, fsck log links/cleanliness flags, and later removal when the bug is no longer relevant.

Control flow under test: each scenario uses `NewCtx`, test API clients, time advancement, `/cron/deprecate_assets`, and `NeededAssetsList`. Email bodies are compared exactly enough to lock report formatting, download asset ordering, title rendering, fsck metadata, and the absence of attachments.

State and persistence behavior: tests exercise datastore-backed `Build`, `Crash`, and `Bug` state, plus blob/text-link storage for crash logs, kernel configs, repro data, and fsck logs. They verify deprecation changes persisted asset URL sets rather than just in-memory report lists.

Dependencies and integration points: uses `dashapi` asset and bug status APIs, `pkg/email.RemoveAddrContext`, the shared `Ctx` test harness, dashboard mail queues, external link helpers, and manager loading through `loadManagers`.

Risks covered: duplicate asset title handling for multi-asset crash reports, stale asset cleanup after bug invalidation, preservation of latest build assets with no crashes, per-manager coverage report selection, and the retention exception for coverage reports. Gaps include no direct concurrent append test and limited coverage of unknown asset type failures.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/asset_storage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/batch_coverage.go -->
# sources/test-tools/syzkaller/dashboard/app/batch_coverage.go

Purpose: cron handler for launching Google Cloud Batch jobs that merge raw syzbot coverage data into aggregated coverage periods, plus a cleanup handler for garbage rows in the coverage database.

Important APIs and functions: `handleBatchCoverage` parses `quarters`, `months`, `days`, and `steps` request parameters, selects configured namespaces, finds each namespace's main repo/branch, computes available raw coverage partitions with `nsDataAvailable`, compares them with merged coverage from `coveragedb.NsDataMerged`, and launches bounded merge jobs via `createScriptJob`. `batchCoverageScript` builds the shell script run by Batch, including syzkaller checkout, `syz-env`, optional init scripts, and repeated `tools/syz-bq.sh` invocations. `nsDataAvailable` queries BigQuery partition metadata for per-day raw coverage. `handleBatchCoverageClean` calls `coveragedb.DeleteGarbage` and writes a plain text result.

Control flow: cron URLs in `cron.yaml` run quarter jobs weekly and day/month jobs daily. For each namespace with `Coverage` config, the handler builds a list of periods to merge using day/month/quarter period ops, truncates to the newest `steps`, and starts one Batch job per namespace. Missing coverage config, missing main repo/branch, BigQuery errors, Spanner errors, and job creation failures are logged and do not stop other namespaces.

State and persistence behavior: this file does not mutate datastore directly. It reads BigQuery metadata, reads merged coverage state through the global Spanner client, creates external Batch jobs, and relies on those jobs to write merged coverage back to the coverage DB. The cleanup path mutates the coverage DB by deleting garbage rows.

Dependencies and integration points: integrates with `CoverageConfig`, `mainRepoBranch`, `coveragedb` period math, BigQuery, Cloud Batch service accounts/scopes, dashboard client credentials, and `batch_main.go`'s shared job creation helper.

Risks: request parameter parsing treats missing or malformed `steps` as a logged error and silent return; cron URLs must always include valid steps. `nsDataAvailable` interpolates namespace into a BigQuery `LIKE` pattern, relying on validated namespace config. Script generation concatenates shell fragments from config and parameters; these config values are trusted but operationally sensitive. Batch jobs are fire-and-forget, so duplicate cron runs can schedule overlapping work unless downstream coverage merge code is idempotent.

Test signals: no direct test file in this subset exercises batch coverage. Coverage behavior is indirectly tested by `coverage_test.go` for rendering/queries, and cron scheduling is represented in `cron.yaml`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/batch_coverage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/batch_db_export.go -->
# sources/test-tools/syzkaller/dashboard/app/batch_db_export.go

Purpose: weekly cron entry point for launching Cloud Batch jobs that export dashboard reproducer data for namespaces configured with an archive path.

Important APIs and functions: `handleBatchDBExport` iterates all namespace configs, skips namespaces without `ReproExportPath`, constructs a Batch service account with userinfo email scope, and calls `createScriptJob` with the `db-export` prefix and a six-hour timeout. `exportDBScript` returns the job shell script: clone syzkaller, acquire a gcloud access token, run `tools/syz-db-export` for the source namespace with parallelism `-j 10`, tar the export directory, and copy the archive to the configured storage path.

Control flow: `/cron/batch_db_export` is scheduled in `cron.yaml` every Saturday. The handler logs job creation failures per namespace and continues with the remaining namespaces.

State and persistence behavior: the app itself only reads config and schedules Batch jobs. The external job reads dashboard data through the exporter tool and writes a compressed archive to cloud storage. No datastore writes occur in this handler.

Dependencies and integration points: uses `CoverageConfig`-independent namespace field `ReproExportPath`, Cloud Batch service accounts, `createScriptJob` from `batch_main.go`, `gcloud`, and the syzkaller repository tooling. The hardcoded project for exports is `syzkaller`.

Risks: shell script construction trusts namespace and archive path from config. Export freshness and idempotency depend on external storage object semantics and the exporter tool. The service account only requests userinfo email scope here, so any future exporter authentication needs must be reflected in scopes.

Test signals: no direct test in this subset. Operational coverage comes from cron wiring and shared Batch creation code.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/batch_db_export.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/batch_main.go -->
# sources/test-tools/syzkaller/dashboard/app/batch_main.go

Purpose: shared Batch infrastructure for dashboard cron jobs that need to run long external scripts outside App Engine request limits.

Important APIs and functions: `initBatchProcessors` registers `/cron/batch_coverage`, `/cron/batch_db_export`, and `/cron/batch_coverage_clean`. `createScriptJob` creates a Google Cloud Batch job with a generated UUID suffix, one task group, one script runnable, fixed compute resources, timeout, service account, standard `e2-standard-8` VM allocation, Ops Agent installation, and Cloud Logging output.

Control flow: callers pass project ID, job-name prefix, script text, max runtime in seconds, and a service account. The function opens a Batch client, builds protobuf request structs, calls `CreateJob`, logs the created job, and returns detailed errors on client construction or job creation failure.

State and persistence behavior: no dashboard datastore state is touched. Persistent effects are external Cloud Batch jobs and their logs. Job IDs are unique by UUID to avoid name collision.

Dependencies and integration points: used by `batch_coverage.go` and `batch_db_export.go`; initialized from `installConfig` through `initBatchProcessors`. Depends on `cloud.google.com/go/batch/apiv1`, `batchpb`, `uuid`, App Engine logging, and duration protobufs.

Risks: compute shape is hardcoded for coverage workload assumptions and is shared with DB export. Standard provisioning avoids spot preemption but increases cost. Scripts are text blobs, so caller-side escaping and trusted inputs are important. There is no deduplication or checking for already-running jobs.

Test signals: no direct tests in this subset; behavior is mostly operational and external-service dependent.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/batch_main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/bisect_test.go -->
# sources/test-tools/syzkaller/dashboard/app/bisect_test.go

Purpose: broad integration test coverage for syzbot bisection workflows, including cause/fix job selection, job completion reporting, email formatting, external reporting, reliability flags, UI display, and admin invalidation.

Important tests and helpers: `TestBisectCause` is the main scenario: it verifies no bisection without repros, cause job ordering by repro quality/time/manager, failed and successful cause bisections, email links for logs/configs/repros, CC filtering, upstream propagation of bisection results, delayed fix bisections, and no extra jobs. `TestBisectCauseInconclusive`, `TestBisectCauseAncient`, and syz-repro variants cover inconclusive result rendering. `TestUnreliableBisect` and `TestBisectWrong` verify release/merge/noop/ignore flags suppress reporting and CC side effects as intended. `TestBisectCauseExternal` and `TestBisectFixExternal` verify API-poll reporting and fix-bisection auto-close. UI/admin tests assert bisection results and status show on pages, invalidated jobs are hidden, and restart reopens cause bisection. Helpers `addBuildAndCrash`, `addBisectCauseJob`, and `addBisectFixJob` set up reusable datastore/job/email state.

Control flow under test: tests move through build upload, crash reporting, email polling, job polling, `JobDone`, incoming `#syz` commands, time advancement, external `ReportingPollBugs`, and admin GET actions. They verify both immediate report emails and later report-stage emails include or suppress bisection sections based on result flags.

State and persistence behavior: exercises persisted `Bug`, `Crash`, `Build`, and `Job` entities, text blobs behind external links, `Bug.BisectCause`/fix status, bug commit lists, reporting state, and `Job.InvalidatedBy`.

Dependencies and integration points: depends on dashapi job/report types, email command processing, external link storage, reporting configuration, manager polling, admin handlers, datastore queries, and UI templates.

Risks covered: incorrect job prioritization, leaking syzbot addresses into CC, unreliable bisection results being treated as authoritative, missing bisection data in later reporting stages, automatic closure mistakes, and stale invalidated bisections in UI. Gaps are mostly around true concurrency and real worker-side bisection behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/bisect_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/cache.go -->
# sources/test-tools/syzkaller/dashboard/app/cache.go

Purpose: maintains App Engine memcache-backed summaries for dashboard pages and implements request throttling keyed by requester identity.

Important APIs and types: `Cached` stores aggregate bug stats, subsystem stats, no-subsystem stats, and missing-backport count. `CacheGet` loads a per-namespace/per-access summary from memcache or rebuilds it from bugs and backports. `cacheUpdate` refreshes summaries hourly for every namespace and public/user/admin access levels. `CachedBugGroups`, `handleMinuteCacheUpdate`, and `minuteCacheNsUpdate` cache compressed JSON UI bug groups for namespaces with `CacheUIPages`. `CachedManagerList`, `CachedUIManagers`, and generic `cachedObjectList` memoize manager-derived lists. `RequesterInfo.Record` and `ThrottleRequest` enforce sliding-window throttling using memcache CAS.

Control flow: page code calls `CacheGet` or UI cache getters; cron refreshes slow caches out-of-band. Minute cache refresh loads visible bugs and managers, prepares bug groups for each access level, marshals/compresses them, and stores them for two minutes. Throttling reads or creates a requester record, prunes old timestamps, appends the current time, stores at most `Limit+1` timestamps, and retries CAS conflicts up to five times.

State and persistence behavior: all state is in memcache with short expirations; cache misses rebuild from datastore. Cached UI bug groups are JSON compressed via `pkg/image`; other cached lists use memcache Gob. Throttle records expire after the configured window and are hashed by requester ID to avoid raw identifiers in keys.

Dependencies and integration points: uses `loadNamespaceBugs`, `loadAllBackports`, `loadVisibleBugs`, `prepareBugGroups`, `managerList`, `loadManagers`, `bug.sanitizeAccess`, `ThrottleConfig`, `timeNow`, App Engine memcache/logging, and dashboard request access-level helpers.

Risks: cache data is access-level sensitive, so key construction and sanitize checks are critical. `RequesterInfo.Record` sorts `ri.Requests` rather than `newRequests`, a likely harmless but suspicious line because `newRequests` is assigned afterward. Memcache failures bubble up to requests for some paths. CAS conflict logic intentionally avoids retrying denied requests in some cases, which favors throttling under contention.

Test signals: `cache_test.go` verifies cached bug groups match uncached fetches for public/user views and that namespace pages still render with empty cache.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/cache_test.go -->
# sources/test-tools/syzkaller/dashboard/app/cache_test.go

Purpose: tests the user-interface cache paths implemented in `cache.go`.

Important tests: `TestCachedBugGroups` creates bugs at different reporting/access stages, adds a separate namespace to guard against cross-namespace contamination, records the uncached output from `fetchNamespaceBugs`, runs `/cron/minute_cache_update`, reads `CachedBugGroups`, and asserts cached groups exactly match original groups for public and user access. It also confirms the namespace page can render after the cache is populated. `TestBugListWithoutCache` verifies pages for public, user, and admin access levels render when `CacheUIPages` is enabled but memcache has no entry.

Control flow under test: build upload, crash report, reporting poll/update, cross-namespace data creation, direct uncached fetch, authenticated cron GET, memcache retrieval, and page GET.

State and persistence behavior: tests drive datastore state for bugs/builds/reporting and memcache state for compressed bug groups. The empty-cache test asserts normal request paths fall back to datastore rather than requiring warm minute cache.

Dependencies and integration points: uses `dashapi`, `testConfig` access-public namespace behavior, `Ctx` helpers, `fetchNamespaceBugs`, `CachedBugGroups`, `/cron/minute_cache_update`, and page handlers.

Risks covered: access-level leakage, namespace mixing, stale or malformed compressed cache objects causing page failures, and accidental dependency on cache warmup. It does not cover hourly aggregate `CacheGet`, manager list caches, or throttle CAS behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/commit_poll_test.go -->
# sources/test-tools/syzkaller/dashboard/app/commit_poll_test.go

Purpose: integration test for dashboard commit polling, which tells managers/builders which fixing commit titles still need commit hashes.

Important test: `TestCommitPoll` uploads a build and two crashes, verifies initial poll returns configured repos and no pending commits, marks one bug with two fix commit titles, and checks both appear repeatedly until matching hashes are uploaded. It then uploads commit metadata with one matching title, one unrelated title associated with the second bug, and unrelated commits, confirming only unresolved titles remain. Finally it uploads the remaining hashes and verifies the pending list becomes empty.

Control flow under test: build/crash upload, global bug polling, `ReportingUpdate` with `FixCommits`, `CommitPoll`, and `UploadCommits`.

State and persistence behavior: tests persisted bug fix-commit titles and uploaded commit metadata. It verifies commit-poll output is derived from unresolved title-to-hash matching rather than simply from bug status or commit upload presence.

Dependencies and integration points: uses `dashapi.BugUpdate`, `dashapi.Commit`, namespace repo configuration from `testConfig`, manager client API methods, and sorting for deterministic assertions.

Risks covered: duplicate polling stability, unrelated commit uploads polluting pending lists, commits attached by bug ID not immediately replacing title-based fix requests unless the requested title is resolved, and repo list correctness. The test does not cover multi-namespace or branch-specific polling edge cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/commit_poll_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/config.go -->
# sources/test-tools/syzkaller/dashboard/app/config.go

Purpose: central configuration schema, installation, defaulting, and validation for the dashboard application.

Important APIs and types: `GlobalConfig` defines app-wide access, ACLs, API clients, namespaces, email addresses, monitored inboxes, discussion email mapping, throttling, upload bucket, and default/dungeon namespace. `Config` defines per-namespace behavior for reporting, API clients, repositories, AI, KCIDB, subsystems, UI caching, coverage, repro export, obsoleting-related features, and manager metadata. Additional structs describe AI stages, clients, ACLs, coverage, subsystem reminders, obsoleting, reporting stages, kernel repos, CC, KCIDB, and throttling. `installConfig` validates and installs global config, then initializes email, HTTP, API, KCIDB, Batch, and coverage DB subsystems. `getConfig` supports test-time context override and optional immutability checks.

Control flow: `checkConfig` canonicalizes email blocklist entries, validates throttle shape, client names/keys, access-level hierarchy, obsoleting settings, default and dungeon namespaces, namespace configs, global client AI namespace defaults, discussion email uniqueness, monitored inbox regexes, and ACL items. Namespace validation fills defaults for display/similarity, default hooks, validates repos/reporting/subsystems/coverage/AI/KCIDB/managers, and builds repo graph constraints. Reporting validation walks stages backward to enforce nondecreasing access restrictions, moderation flags, daily limit bounds, non-last embargo rules, filter defaults, config validation, and JSON marshalability.

State and persistence behavior: config is stored globally in `configDontUse` after validation and is expected read-only. Some validation mutates config by filling defaults such as access levels, reporting display titles, AI debounce, subsystem reminder defaults, `NeedRepro`/`TransformCrash`, global client namespace lists, and obsoleting start period.

Dependencies and integration points: every dashboard subsystem reads `getConfig`. This file integrates with `dashapi`, AI workflow types, email canonicalization, subsystem service, validator package, vcs repo validation, reporting type implementations, HTTP/API initialization, Batch cron registration, KCIDB, and coverage DB initialization.

Risks: validation panics at startup, which is desirable for bad static config but risky for dynamically altered test configs. Defaulting mutates the installed object, so immutability checks need to account for post-validation state. `APIClient.AllowedNamespace` only checks membership and assumes empty lists were expanded during validation. Many subsystems rely on config access-level inheritance being correct.

Test signals: no dedicated test in this subset, but many tests use `NewCtx`, config overrides, and `checkConfig` indirectly. Email, coverage, dungeon, cache, and batch behavior all depends on these definitions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/coverage.go -->
# sources/test-tools/syzkaller/dashboard/app/coverage.go

Purpose: serves coverage heatmaps, per-file coverage views, coverage graphs, and coverage-subsystem regeneration for the dashboard.

Important APIs and types: `initCoverageDB` initializes the global Spanner coverage client in App Engine and leaves tests to inject a mock. `getCoverageDBClient`, `setWebGit`, and `getWebGit` are context-based injection points. `coverageHeatmapParams`, `makeHeatmapParams`, `getParam`, and `extractVal` parse coverage query parameters. `handleCoverageHeatmap` and `handleSubsystemsCoverageHeatmap` render regular and subsystem heatmaps; `handleHeatmap` performs shared validation, period generation, manager/subsystem loading, and template serving. `handleFileCoverage` validates file coverage query inputs, reads hit counts from coverage DB, optionally converts to unique coverage relative to all managers, fetches source through web-git, and renders annotated HTML. `handleCoverageGraph` renders monthly/quarterly coverage ratios. `handleUpdateCoverDBSubsystems` regenerates coverage DB subsystem labels from configured subsystem services.

Control flow: coverage pages start with `commonHeader`, require namespace coverage config, parse/validate period and filtering parameters, query Spanner through `coveragedb`, use cached manager lists and subsystem service lists for UI dimensions, and return either HTML templates or JSONL external coverage. File coverage has a stricter validation path using `pkg/validator` before DB and web-git access.

State and persistence behavior: primarily read-only against Spanner coverage DB and source repositories. `handleUpdateCoverDBSubsystems` mutates coverage DB records. The global coverage client is process state; tests inject a client through context. File-provider mocks are also context state.

Dependencies and integration points: depends on `pkg/cover`, `coveragedb`, `spannerclient`, `covermerger`, `urlutil`, validators, namespace coverage config, cached manager lists, subsystem services, templates, and App Engine context/logging.

Risks: generic parameter parsing ignores conversion errors in `extractVal`, so invalid ints/bools/dates can silently become zero values before later validation catches only some cases. Heatmap period count bounds are enforced, but file coverage requires exact date parse. Unique coverage performs an extra DB read in a specific order relied upon by tests. A nil global coverage client panics outside tests if initialization is missed.

Test signals: `coverage_test.go` validates bad request handling for malformed file coverage input, empty/regular DB rendering, unique-only multi-manager behavior, mock DB ordering, and mock web-git integration.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/coverage.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/coverage_test.go -->
# sources/test-tools/syzkaller/dashboard/app/coverage_test.go

Purpose: tests per-file coverage rendering and validation paths from `coverage.go`.

Important tests and helpers: `setCoverageDBClient` injects a Spanner client mock into context. `TestFileCoverage_BadRequest` sends a malformed `dateto` parameter and asserts an HTTP 400. `TestFileCoverage` table-tests empty DB, normal DB, and unique-only multi-manager DB behavior, verifying rendered HTML contains expected annotated line/count strings. `staticFileProvider` mocks kernel source retrieval. `emptyCoverageDBFixture`, `coverageDBFixture`, `multiManagerCovDBFixture`, and `newRowIteratorMock` model Spanner row iterators and read-only transactions.

Control flow under test: namespace coverage mocks are installed, the handler receives GET requests to `/test2/coverage/file`, validates params, reads coverage rows from mocked Spanner, reads source from mocked web-git, and renders file coverage HTML.

State and persistence behavior: no real persistence is used; all DB and source state is supplied by mocks. The multi-manager fixture deliberately expects two ordered Spanner reads: selected manager first, all-manager coverage second for `unique-only`.

Dependencies and integration points: uses `coveragedb` mock types, `spannerclient` interfaces, `covermerger.FileVersProvider`, testify assertions/mocks, App Engine test context, and dashboard coverage config test helpers.

Risks covered: malformed request rejection, empty coverage rendering, hit-count alignment with source lines, and unique coverage subtraction semantics. Gaps include heatmap rendering, coverage graph rendering, JSONL output, subsystem regeneration, and real web-git/Gerrit base64 behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/coverage_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/cron.yaml -->
# sources/test-tools/syzkaller/dashboard/app/cron.yaml

Purpose: App Engine cron schedule for recurring dashboard maintenance, polling, cache warming, coverage aggregation, exports, reports, and subsystem updates.

Important entries: email polling runs every minute; full cache update hourly; dungeon preheat hourly; minute UI cache update every minute; asset deprecation every three hours; KCIDB polling and subsystem refresh every five minutes; subsystem reports every eight hours. Coverage aggregation runs quarter merges weekly on Sunday midnight and day/month merges daily midnight. Coverage garbage cleanup runs Saturday noon, intentionally away from aggregation. Reproducer DB export runs Saturday midnight. Monthly coverage emails run on the 15th, and coverage DB subsystem regeneration runs every Monday.

Control flow and integration: each URL maps to handlers registered in `main.go`, `batch_main.go`, and other dashboard files. Query parameters on `/cron/batch_coverage` determine which period types and how many newest periods are merged.

State and persistence behavior: cron itself stores no state, but it drives datastore/memcache updates, Batch job creation, KCIDB/export side effects, coverage DB writes/deletes, email sends, and asset reference deprecation.

Dependencies and integration points: depends on App Engine cron syntax and on handlers being registered during `installConfig`/HTTP initialization. Operational timing comments document coverage propagation assumptions and cleanup race avoidance.

Risks: schedules are dense for minute-level tasks, so handler idempotency and bounded runtime matter. Batch coverage cleanup must not overlap active aggregation. The monthly coverage report schedule encodes a 9-day propagation assumption with a 15-day conservative trigger. Missing handler registration would surface only at runtime.

Test signals: no direct test for `cron.yaml` in this subset. Its coverage is indirect through tests of the handlers it triggers, such as cache, asset deprecation, coverage, and dungeon preheat logic.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/cron.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/dashboard.go -->
# sources/test-tools/syzkaller/dashboard/app/dashboard.go

Purpose: production entry point for the App Engine dashboard binary.

Important APIs and functions: `enableProfiling` starts Google Cloud Profiler with default App Engine-inferred service metadata and logs failures through syzkaller's logging package. `main` calls `enableProfiling`, installs `mainConfig`, and hands control to `appengine.Main`.

Control flow: startup is deliberately minimal. Config installation is the heavy initializer: it validates config, registers HTTP/API/cron handlers, and initializes integrations. After that, App Engine serves requests.

State and persistence behavior: establishes process-wide profiler state and global dashboard config state. It does not directly touch datastore or external services except through config installation side effects.

Dependencies and integration points: depends on `cloud.google.com/go/profiler`, `google.golang.org/appengine/v2`, syzkaller logging, and `mainConfig` supplied by environment-specific config files.

Risks: profiler startup failures are logged but non-fatal. Any panic from `installConfig` prevents the app from starting, which is correct for invalid static config. Tests generally use alternate entry points and `installConfig(testConfig)`, so this file has limited direct test coverage.

Test signals: no direct tests in this subset. Broad test setup indirectly validates `installConfig` behavior used by `main`.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/dashboard.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/discussion.go -->
# sources/test-tools/syzkaller/dashboard/app/discussion.go

Purpose: stores and summarizes external discussion threads related to dashboard bugs, especially lore/email discussions and patch threads.

Important APIs and types: `saveDiscussionMessage` converts a parsed incoming email into a `dashapi.Discussion` update, deciding whether to ignore, append to an existing thread, or create a new thread using `email.NewMessageAction`. `mergeDiscussion` creates or updates a `Discussion` datastore entity, merges bug associations, deduplicates messages, and updates per-bug summaries. `mergeDiscussionSummary` updates `Bug.DiscussionInfo` for a source. `DiscussionSummary.merge`, `Bug.discussionSummary`, `Discussion.addMessages`, `messageIDs`, `link`, `discussionByMessageID`, `discussionsForBug`, `getBugKeys`, and `unique` provide supporting behavior.

Control flow: incoming email saves first identify a parent discussion by `InReplyTo` if possible, then action rules determine thread ID/type. A cross-group transaction updates the discussion entity because bug associations can span multiple bugs. Per-bug summary updates are intentionally performed afterward in separate transactions to avoid App Engine entity-group limits.

State and persistence behavior: `Discussion` entities store source, type, subject, bug key string IDs, message metadata, and summary counters. `Bug` entities store source-specific summary records. Message storage deduplicates by ID, sorts by time, preserves the first message, and caps retained messages at 1500 while summaries continue to accumulate counts.

Dependencies and integration points: integrates with `dashapi.Discussion`, email parsing/action logic, lore link generation, bug lookup by reporting ID, datastore transactions, UI code that reads discussions for bug pages, and reporting email code that calls `saveDiscussionMessage`.

Risks: `mergeDiscussion` returns nil if `getBugKeys` fails, which intentionally ignores unknown bug IDs but can hide ingestion problems. Duplicate message IDs in multiple discussion entities become an error with a TODO to merge. Summary updates outside the main transaction can leave discussion and bug summary temporarily inconsistent if a later bug update fails.

Test signals: `discussion_test.go` covers multi-bug access, own/external message counts, unrelated discussion filtering, subdiscussion creation without original parent, patch-link discovery, bot reply ignoring, and message overflow retention.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/discussion.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/discussion_test.go -->
# sources/test-tools/syzkaller/dashboard/app/discussion_test.go

Purpose: integration and unit tests for discussion ingestion, bug summary updates, UI exposure, and message retention.

Important tests: `TestDiscussionAccess` saves API discussions spanning one or more bugs and validates `getBugDiscussionsUI` plus merged `DiscussionSummary` fields. `TestEmailOwnDiscussions` verifies bot-originated reports and user replies update the same lore thread with correct own/external counts. `TestEmailUnrelatedDiscussion` ensures messages not sent to the configured discussion address are ignored. `TestEmailSubdiscussion` accepts a reply whose parent was not seen and creates a visible thread. `TestEmailPatchWithLink` detects a patch email with dashboard bug link. `TestIgnoreBotReplies` suppresses bot replies to patch testing requests. `TestMessageOverflow` unit-tests `Discussion.addMessages` retention: first message is preserved, newest messages retained, and length capped at `maxMessagesInDiscussion`.

Control flow under test: combines build/crash upload, bug email polling, App Engine incoming mail POSTs, direct `SaveDiscussion` API calls, bug lookup, and UI discussion loading.

State and persistence behavior: tests verify `Discussion` entities and `Bug.DiscussionInfo` summaries are updated consistently enough for UI, including time ordering and summary counters. Overflow testing focuses on in-memory `Discussion` mutation.

Dependencies and integration points: uses dashapi discussion types, package email parsing, lore URL conventions, test mail harness, `getBugDiscussionsUI`, and `findBugByReportingID`.

Risks covered: accidental visibility of unrelated discussions, failure to stitch replies to parent threads, bot mail loops, missing patch threads when the first message references a bug only by link, and unbounded discussion message growth. Gaps include datastore transaction failure injection and duplicate message ID conflicts across discussions.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/discussion_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/dungeon.go -->
# sources/test-tools/syzkaller/dashboard/app/dungeon.go

Purpose: implements the Syzkaller Dungeon feature, a gamified dashboard view ranking bug-fixing contributors ("heroes") and email-domain groups ("kingdoms") by fixed bug activity.

Important APIs and types: UI structs `uiDungeonBadge`, `uiDungeonPlayer`, `uiDungeonKingdom`, `uiDungeonMeta`, and `uiDungeonPage` define JSON/template data. HTTP handlers `handleDungeon`, `handleHeroProfile`, and `handleKingdomProfile` serve HTML or JSON, gated to the configured dungeon namespace. `getDungeonData` reads compressed JSON from memcache or calls `fetchDungeonData`; `handleDungeonPreheat` warms cache for public/user/admin access. Helpers `addBugToPlayerMap`, `addBugToKingdomMap`, `processPlayers`, `processKingdoms`, `extractSubsystems`, `dungeonCacheKey`, `rebuildMaps`, and `hashEmailID` build ranked data.

Control flow: data generation loads fixed bugs plus open bugs that already have commits for the dungeon namespace, filters by sanitized access level, computes XP/days-open through `pkg/dungeon`, credits unique commit author emails once per bug, adds all-time and one-year entries, derives kingdoms from email domains, processes player classes/badges/attributes/levels/ranks, then aggregates kingdoms from processed heroes. Profile handlers select `era=1y` or all-time data and return 404 for missing IDs.

State and persistence behavior: source truth is datastore `Bug` entities and their `CommitInfo`, labels, repro levels, crash counts, and fix/first times. Generated dungeon pages are stored in memcache as compressed JSON for one hour by access level; maps are omitted from JSON and rebuilt after decode.

Dependencies and integration points: uses dashboard headers/templates/routing, config `DungeonNamespace`, access control, datastore bug loaders, App Engine memcache, `pkg/dungeon` scoring/class/badge logic, syzkaller hashing, compressed image utilities, and cron preheat from `cron.yaml`.

Risks: cache keys include access level but not namespace; handlers currently only allow the single dungeon namespace, so this is acceptable but would need revisiting for multiple dungeon namespaces. JSON omits internal maps, requiring `rebuildMaps` to avoid nil profile lookups after cache hits. Contributor identity is lowercased email; name aggregation and domain kingdom derivation depend on commit metadata quality. Scoring includes open bugs with commits, which may change leaderboard semantics as bugs later fix/close.

Test signals: `dungeon_test.go` covers hash stability, player/kingdom processing, badge predicates, trophy ladder thresholds, subsystem extraction, ranking tie-breakers, multi-name aggregation, and fallback naming.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/dungeon.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/dungeon_test.go -->
# sources/test-tools/syzkaller/dashboard/app/dungeon_test.go

Purpose: unit tests for dungeon ranking, identity, badge, class, and naming behavior.

Important tests: `TestHashEmailID` locks the 16-character hash behavior. `TestProcessPlayers` verifies badges such as Dragon Vanquisher, Necromancer, Diviner, Windwalker, Sealer, and Hydra Hunter, plus scaled Str/Wis attributes. `TestProcessKingdoms` checks score aggregation, ranking, champion/guild derivation, and guild ordering by class counts. `TestIntegrationBadges` table-tests title/commit pattern badges and negative matches. `TestTrophyLadderBadges` verifies bug-count thresholds. `TestExtractSubsystems` filters only subsystem labels. `TestPlayerRankingTieBreakers` locks score/name/email sorting. `TestMultiNameAggregation` and `TestHeroNamingLogic` verify frequent-name selection, tie handling, suffix generation, and fallback to email.

Control flow under test: tests construct in-memory `Bug`, `uiDungeonPlayer`, and `uiDungeonKingdom` maps, call `processPlayers`, `processKingdoms`, `extractSubsystems`, and `hashEmailID`, then inspect computed fields.

State and persistence behavior: no datastore or memcache is used; tests focus on deterministic transformation of in-memory bug/player/kingdom state.

Dependencies and integration points: uses `dashapi.ReproLevel` constants, dashboard `Bug`/`BugLabel` types, and `pkg/dungeon` badge/class/scaling/naming rules through the production processing functions.

Risks covered: unstable rankings, unintended badge keyword matches, broken hash IDs used in URLs, incorrect kingdom guild names, attribute scaling regressions, and contributor display-name surprises. Gaps include HTTP handlers, memcache rebuilds, access-level filtering, and real datastore bug loading.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/dungeon_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/email_test.go -->
# sources/test-tools/syzkaller/dashboard/app/email_test.go

Purpose: comprehensive integration tests for syzbot email reporting, incoming command processing, mailing-list interactions, CC management, label/subsystem commands, forwarding, and anti-loop behavior.

Important tests: `TestEmailReport` is the main end-to-end scenario: first report formatting, mailing-list echo capture, opt-out/uncc, syz and C reproducer update emails, upstream transition, CC accumulation, invalid command replies, fix command persistence, builder pending commits, and new bug sequence after fix. Duplication tests cover dup/undup, cross-reporting restrictions, and title parsing variants. Error/loop tests verify replies only when syzbot is addressed appropriately and never to its own bounced replies. Other scenarios cover failed build reports, unfix behavior, manager CC/build-maintainer rules, strace wording, subject-title parsing, bug inference from mailing-list subject, report link capture, patch-testing access control, subsystem/label set/unset validation, archival forwarding for configured mailing lists/inboxes, duplicate forward suppression, and ignoring indirect commands found only through `Reported-by`.

Control flow under test: tests combine build upload, crash/build-error reports, outgoing mail polling, App Engine incoming mail POSTs, `#syz` commands, reporting-stage transitions, builder polling, commit uploads, context config overrides, and label inspections.

State and persistence behavior: heavily exercises `Bug`, `Crash`, `Build`, reporting state, CC lists, opt-out lists, labels, link/message IDs, commit-fix state, pending builder commits, and outgoing email queue. It also verifies text blobs behind external links for logs/configs/repros.

Dependencies and integration points: uses `dashapi`, `pkg/email`, target architecture metadata, test harness mail helpers, reporting/email implementation, label validation, subsystem services, manager config, monitored inbox config, and API clients.

Risks covered: malformed or indirect commands causing unwanted state changes, mail loops, wrong recipients/CC leakage, mailing-list subject ambiguity, cross-reporting dup mistakes, label validation errors, forwarded-command archival behavior, and report formatting regressions. Gaps are mostly around real mail transport and concurrent command races.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/dashboard/app/email_test.go -->
