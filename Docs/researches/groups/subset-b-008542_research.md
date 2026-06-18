# subset-b-008542 Research

Grouped research for Pebble replay, scan/snapshot, scripts, and blob/sstable files. Each section preserves the source path for source-tree-aligned reconciliation.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/replay/replay_test.go -->
# sources/storage-engines/pebble/replay/replay_test.go

## Purpose
This file is the main datadriven and regression test harness for Pebble workload replay. It builds captured workloads, replays them through `Runner`, validates replayed DB contents, exercises pacing modes, and covers capture/replay variants for ordinary flushes, value separation, ingestion, and ingest-and-excise metadata.

## Important APIs, Types, and Functions
`runReplayTest` interprets datadriven commands such as `corpus`, `replay`, `scan-keys`, `wait-for-compactions`, `wait`, and `close` over a shared in-memory VFS. It constructs `Runner` with `RunDir`, `WorkloadFS`, `WorkloadPath`, `Pacer`, and test `pebble.Options`.

`TestReplay`, `TestReplayPaced`, `TestReplayValSep`, and `TestReplayIngest` are thin entry points over separate replay testdata files.

`TestLoadFlushedSSTableKeys` validates that flushed SSTable contents can be loaded into a batch representation, including point keys, range deletions, range key sets/unsets/deletes, and blob-aware reader provider setup.

`collectCorpus` builds workload directories from datadriven corpus scripts. It drives `WorkloadCollector`, `Checkpoint`, `Flush`, `Ingest`, `IngestAndExcise`, file creation, file discovery, and manifest-start discovery.

`TestBenchmarkString` verifies benchmark metric formatting from `Metrics`.

`TestCompactionsQuiesce` and `TestFlushEndNotifiesRefreshMetrics` are hang-regression tests around replay completion and metric refresh signaling.

`buildFlushOnlyWorkload`, `getHeavyWorkload`, and `buildHeavyWorkload` synthesize replay workloads with controlled flush and compaction behavior.

## Control Flow
The replay tests first build or clone a workload checkpoint into a run directory, configure deterministic DB options, start a `Runner`, then inspect output through iterators, filesystem listings, or `Runner.Wait`. Corpus capture tests open a DB with a `WorkloadCollector`, start capture after checkpointing, mutate the DB, wait for collector copy completion, and stop collection.

`TestLoadFlushedSSTableKeys` tracks flushed table numbers through `FlushEnd`, flushes the DB, sets up a blob reader provider, calls `loadFlushedSSTableKeys`, and then decodes the resulting batch with `batchrepr`.

The quiescing tests run replay asynchronously and use `require.Eventually` to detect deadlocks in `Wait`, with timeout adjustments for slow or invariants builds.

## State and Persistence Behavior
All persistence is modeled through `vfs.MemFS`, cloned checkpoints, manifest and SST files, and captured workload directories. The collector tests depend on copied manifests, SSTables, and blob files matching original source files. The heavy workload cache uses `sync.Once` to avoid rebuilding expensive test data.

## Dependencies and Integration Points
The file integrates with Pebble `DB`, batches, iterators, `WorkloadCollector`, replay `Runner`, `Pacer` implementations, `sstable` writer test helpers, range-key decoding, blob reader provider setup, and `datatest` batch/SST command utilities. It uses `datadriven` files under replay testdata as the behavioral contract.

## Risks
The tests are sensitive to deterministic file names, manifest sizes, iterator stack selection, compaction scheduling, and timing around asynchronous replay and collector goroutines. Randomized heavy workload generation makes compaction coverage realistic but requires generous eventual timeouts. Value-separation replay relies on captured blob-reference files being copied by the collector.

## Test Signals
Strong coverage exists for replay success, paced replay, value separation, ingestion, corpus capture, batch reconstruction from SSTables, benchmark output formatting, quiescence termination, and flush-only metric notification. Failures usually indicate replay ordering bugs, collector copy omissions, manifest parsing issues, or missed completion notifications.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/replay/replay_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/replay/sampled_metric.go -->
# sources/storage-engines/pebble/replay/sampled_metric.go

## Purpose
This file defines `SampledMetric`, a lightweight time-series helper used by replay metrics to record sampled values and render summaries or ASCII graphs over replay time.

## Important APIs, Types, and Functions
`SampledMetric` stores `samples []sample` and the first sample time. `sample` records elapsed duration and int64 value.

`record` lazily initializes the first timestamp and appends an elapsed-time sample.

`Plot` buckets values through `Values`, scales them, and renders with `asciigraph`.

`PlotIncreasingPerSec` converts monotonically increasing counter samples into per-second bucket deltas before rendering.

`Mean`, `Min`, and `Max` compute simple aggregate statistics. `Values` and internal `values` project irregular samples into a fixed number of equally spaced time buckets.

## Control Flow
Samples are appended in observation order. Bucket projection computes the total duration from the last sample, divides it by the requested bucket count, and writes the latest sample value into the corresponding bucket, filling gaps with the next observed value.

## State and Persistence Behavior
The type is in-memory only. It keeps no locks and assumes single-threaded or externally synchronized recording and reads. The first timestamp anchors all future sample durations.

## Dependencies and Integration Points
The only external rendering dependency is `github.com/guptarohit/asciigraph`. Replay metric formatting code consumes `SampledMetric` for graphs and aggregate benchmark fields.

## Risks
`values` divides by `bucketDur`, which is `totalDur / buckets`; if all samples have zero elapsed duration and buckets is positive, this can produce a zero duration and a division panic. Empty samples and nonpositive bucket counts return nil safely. `Min` returns `math.MaxInt64` for no samples, unlike `Mean` and `Max`, so callers should avoid interpreting an empty minimum as meaningful.

## Test Signals
The paired datadriven test covers bucket projection, scaling, plotting, and per-second increasing deltas with synthetic durations.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/replay/sampled_metric.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/replay/sampled_metric_test.go -->
# sources/storage-engines/pebble/replay/sampled_metric_test.go

## Purpose
This file provides datadriven tests for `SampledMetric` bucketization and graph rendering.

## Important APIs, Types, and Functions
`TestSampledMetric` supports `init`, `values`, `plot`, and `plot-increasing-per-sec` commands. `init` parses value/duration lines into cumulative sample timestamps without relying on wall-clock time.

## Control Flow
Each datadriven command updates or reads a shared `SampledMetric`. `values` prints fixed-width bucket output with one decimal place. Plot commands parse width, height, and scale and return the raw ASCII graph.

## State and Persistence Behavior
State is test-local and reset by `init` by reusing the existing sample slice capacity. The testdata file is the persisted expected-output contract.

## Dependencies and Integration Points
The test uses `datadriven`, `crstrings.LinesSeq`, `require`, and Go duration parsing. It directly exercises `SampledMetric.Values`, `Plot`, and `PlotIncreasingPerSec`.

## Risks
Because graph output is textual, small changes to bucket selection or `asciigraph` behavior can cause large golden diffs. The tests construct samples manually and do not exercise `record`'s wall-clock behavior.

## Test Signals
The file is itself the primary signal that replay metric graphs stay stable and that increasing counters are turned into bucketed rates as intended.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/replay/sampled_metric_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/replay/workload_capture.go -->
# sources/storage-engines/pebble/replay/workload_capture.go

## Purpose
This file implements `WorkloadCollector`, a Pebble event-listener and cleaner wrapper that captures the manifest, flushed SSTables, ingested SSTables, and referenced blob files needed to replay a workload later.

## Important APIs, Types, and Functions
`workloadCaptureState` is a bitset with `obsolete`, `readyForProcessing`, and `capturedSuccessfully` flags.

`WorkloadCollector` owns mutex-protected file state, pending copy queues, manifest descriptors, test condition variables, atomic current manifest and enabled flags, source/destination filesystem config, and a copier condition with stop/done state.

`NewWorkloadCollector` initializes buffers, source directory, state map, and condition variables.

`Attach` adds Pebble event hooks for `FlushEnd`, `ManifestCreated`, and `TableIngested`, then replaces `Options.Cleaner` with a deferring wrapper that calls `w.clean`.

`onFlushEnd`, `onTableIngest`, and `onManifestCreated` enqueue files or manifests while running.

`copyFiles` runs as a background goroutine, draining pending SST/blob paths and manifest updates.

`copyManifests` incrementally copies manifest bytes and closes older rotated manifests when no more bytes can be read.

`copySSTablesAndBlobs` copies queued files and then cleans any that were marked obsolete before capture completed.

`Start`, `WaitAndStop`, `Stop`, and `IsRunning` provide lifecycle control.

## Control Flow
After `Attach`, Pebble events update collector queues. `Start` records destination FS/dir, seeds the current manifest if already known, sets enabled with compare-and-swap, and launches `copyFiles`. The copier waits on a condition, snapshots pending work while holding the mutex, drops the mutex for actual I/O, copies manifest deltas first, then table/blob files, updates copied counts, and broadcasts test waiters. `Stop` flips enabled off, signals the copier, and waits for `done`.

Cleaner interception is central: if capture is not running or a file was already captured, deletion proceeds immediately through the original cleaner. Otherwise the file is marked obsolete and actual deletion is deferred until after copying.

## State and Persistence Behavior
The collector persists captured workload files into a destination directory on a destination VFS. It tracks per-file state by Pebble base filename. Manifest copying is incremental because the active manifest can continue to receive version edits. SSTables and blob files are copied as whole immutable files.

## Dependencies and Integration Points
The collector integrates with `pebble.Options`, `pebble.EventListener`, `pebble.Cleaner`, `base.FileType` naming, `vfs.CopyAcrossFS`, and flush/table ingest metadata. It also now observes blob references from flushed tables through `GetBlobReferenceFiles`.

## Risks
This is concurrency-sensitive code. The lock is intentionally released around I/O and reacquired before loop continuation; incorrect lock ordering could deadlock or race. Panics are used for copy/open/close failures in the background goroutine, so production callers should treat collector failures as fatal. `copySSTablesAndBlobs` calls `cleanFile` with `FileTypeTable` even for blob paths, which depends on the wrapped cleaner tolerating or ignoring the type. Manifest seeding and rotation must stay aligned with Pebble manifest lifecycle or replay can miss edits.

## Test Signals
The paired datadriven collector test exercises start/stop, manifest creation, flush, ingest, deferred cleaning, file comparison, waiting for copy completion, and destination listings.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/replay/workload_capture.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/replay/workload_capture_test.go -->
# sources/storage-engines/pebble/replay/workload_capture_test.go

## Purpose
This file validates `WorkloadCollector` behavior against datadriven capture scenarios over an in-memory VFS.

## Important APIs, Types, and Functions
`TestWorkloadCollector` supports commands for `start`, `stop`, `wait`, `create-manifest`, `flush`, `ingest`, `clean`, `cmp-files`, `stat`, and `ls`.

Helpers include `randData`, `writeFile`, and `readFile` for deterministic-size random file creation and verification.

## Control Flow
The test attaches a collector to Pebble options, manually simulates manifest creation, flushes, ingests, and cleaner calls, then waits on the collector's `copyCond` until `filesEnqueued == filesCopied`. Flush and ingest commands create table files and append fake manifest bytes to model version edits.

## State and Persistence Behavior
All source and destination files live in a memory filesystem under `src` and `dst`. The test explicitly keeps the current manifest file open, matching Pebble's active manifest append behavior. Copied-file counts and queued-file counts are internal collector state used for synchronization.

## Dependencies and Integration Points
The test uses Pebble event payload types (`FlushInfo`, `TableIngestInfo`, `ManifestCreateInfo`), base filename parsing, VFS helpers, datadriven testdata, and the collector's wrapped cleaner.

## Risks
The random contents mean equality checks compare bytes but expected outputs focus on sizes and names. The test manually invokes event handlers, so it does not fully exercise Pebble's real event ordering. It does exercise race-prone synchronization with the copy goroutine.

## Test Signals
Strong signals include equality between captured and source files, destination listings after `wait`, deferred cleaner behavior, manifest size growth after flush/ingest, and clean handling for files that are copied or not relevant.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/replay/workload_capture_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/scan_internal.go -->
# sources/storage-engines/pebble/scan_internal.go

## Purpose
This file implements Pebble's internal-key scanning machinery for `DB`, `Snapshot`, and eventually-file-only snapshots. It exposes all logical internal state needed by external consumers such as replication or file-only snapshot transfer while optionally skipping lower-level shared or external files and returning ingestable metadata for them.

## Important APIs, Types, and Functions
`ErrInvalidSkipSharedIteration` reports invalid skip-shared or skip-external scans when required lower-level files are not remote/shareable or contain newer keys than the snapshot.

`SharedSSTMeta` captures remote backing, truncated internal bounds, point/range bounds, level, estimated size, and debug table number for a shared SSTable.

`DB.ScanInternal` creates a `scanInternalIterator` with `newInternalIter` and delegates to `scanInternalImpl`.

`newInternalIter` pins read state or version, chooses the read sequence number, initializes blob value fetching, and prepares iterator allocation.

`pointCollapsingIterator` wraps a keyspan interleaving iterator to return at most one point internal key per user key, while still exposing range deletions and hiding points covered by visible range tombstones.

`IteratorLevel` and `IteratorLevelKind` annotate point-key callbacks with memtable, LSM level, and L0 sublevel origin when available.

`truncateSharedFile` and `truncateExternalFile` produce bounded shared/external metadata for skipped files. Shared truncation may open point, range-delete, and range-key iterators to find tight in-range bounds.

`scanInternalImpl` validates options, visits skipped remote files, iterates internal keys, applies rate limiting, and dispatches point, range-delete, range-key, shared-file, and external-file callbacks.

`constructPointIter` builds memtable, L0 sublevel, lower-level, range-delete, and merging iterator stacks while respecting skip levels and blob value fetchers.

`constructRangeKeyIter` builds the internal range-key iterator stack without eliding range key unsets/deletes.

## Control Flow
Initialization pins the read version, trims memtables newer than the scan sequence, copies bounds into owned buffers, constructs point/range-delete iterators, constructs range-key iterators, and then interleaves point and range-key streams.

Skip mode first scans metadata for levels at and below the configured threshold. It verifies remote object metadata, rejects unsupported mixes, ensures file high sequence numbers are visible to the scan snapshot, truncates metadata to `[lower, upper)`, and calls the appropriate visitor. The actual key iterator excludes deeper skipped levels and excludes remote files from the boundary level that are represented through visitors.

Normal key iteration starts at `LowerBound`, calls an optional rate limiter with the current key/value, then dispatches by key kind. Range-key callback keys are copied, zeroed to sequence number 0, sorted by trailer, and passed with span bounds. Range deletions pass start/end/largest sequence. Point keys pass lazy values and origin metadata.

## State and Persistence Behavior
The scanner does not persist new state, but it pins read state/version references, open table iterators, blob readers, range-key iterator pools, and block/cache resources until `Close`. It may read table contents to tighten shared file metadata and estimate remote file size. Blob values for ingested flushables are fetched through a combined blob file mapping.

## Dependencies and Integration Points
The implementation integrates with Pebble read state, versions, memtables, L0 sublevels, manifest levels, objstorage providers, remote/shared storage metadata, external file ingestion metadata, `keyspan` merging/interleaving, `sstable` iterators, blob `ValueFetcher`, block categories, iterator stats, and inflight iterator tracking.

## Risks
Skip-shared and skip-external correctness depends on strict visibility checks and remote object classification. Boundary-level filtering must keep key iteration and visitor metadata mutually consistent. `pointCollapsingIterator` intentionally panics on merges and single deletes and should only be used where those are impossible or handled elsewhere. Shared truncation opens extra iterators and can be expensive. Resource release is complex: read-state refs, version refs, blob fetchers, iterator pools, and range-key states must all be closed even on errors.

## Test Signals
`scan_internal_test.go` covers datadriven internal scans, skip-shared and skip-external visitors, snapshots, eventually-file-only snapshots, file-only snapshot waiting, external ingestion, point collapsing behavior, and scan statistics.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/scan_internal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/scan_internal_test.go -->
# sources/storage-engines/pebble/scan_internal_test.go

## Purpose
This file provides datadriven tests for `ScanInternal`, `ScanStatistics`, skip-shared/external scanning, snapshot variants, and the point-collapsing iterator.

## Important APIs, Types, and Functions
`TestScanStatistics` drives DB setup, batches, snapshots, compactions, flushes, commits, and `ScanStatistics` output over selected levels and key kinds.

`TestScanInternal` drives DB definition/reset, snapshots, eventually-file-only snapshots, batches, ingest, external ingest, compaction, flush, LSM display, and `scan-internal` callbacks.

The local `writeSST` helper writes point, range deletion, and range key data into SSTables for ingest paths.

`TestPointCollapsingIter` constructs fake point keys and range-deletion spans from datadriven input and runs common internal iterator commands against `pointCollapsingIterator`.

## Control Flow
Datadriven commands maintain maps of named batches, snapshots, and file-only snapshots. `scan-internal` selects a reader (`DB`, `Snapshot`, or EFOS), parses lower/upper bounds and skip flags, installs visitors that print points, range deletions, range keys, shared files, and external files, and calls `ScanInternal`.

External ingest builds an SST into remote in-memory storage, constructs an `ExternalFile` with encoded bounds, and ingests it through `IngestExternalFiles`.

## State and Persistence Behavior
Tests use in-memory local and remote storage. Named batches and snapshots are explicitly closed during cleanup. File-only snapshots can wait for transition before scanning. Remote storage is configured through `remote.MakeSimpleFactory`, `CreateOnSharedAll`, and external-storage locators.

## Dependencies and Integration Points
The tests touch Pebble DB options, object storage providers, remote storage, bloom filters, sstable raw writing, range-key spans, batch sorting, datadriven commands, snapshot APIs, and test comparers.

## Risks
The test harness intentionally covers many codepaths, so output changes can reflect small iterator ordering changes, metadata truncation changes, or remote storage classification changes. It relies on format versions that support shared objects, virtual SSTables, and external files.

## Test Signals
Signals include printed internal keys and values, shared-file metadata bounds, external-file metadata, scan statistics counts and snapshot-pinned keys, LSM output after compactions, and iterator traces for point collapse around range tombstones.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/scan_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/scripts/changed-go-pkgs.sh -->
# sources/storage-engines/pebble/scripts/changed-go-pkgs.sh

## Purpose
This small CI helper prints the unique directories containing Go files changed between a base SHA and head SHA, excluding `internal/devtools`.

## Important APIs, Types, and Functions
The script accepts `<base-sha> <head-sha>`, validates only that `HEAD_SHA` is non-empty, and uses `git diff --name-only`, `dirname`, `sort -u`, `grep -v`, and `xargs echo`.

## Control Flow
It exits with usage if the second argument is missing. Otherwise it diffs `BASE_SHA..HEAD_SHA` for `*.go`, maps files to directories, de-duplicates, filters devtools, and emits a space-separated package-directory list.

## State and Persistence Behavior
No persistent state is written. Output is derived from git history.

## Dependencies and Integration Points
It depends on git and standard Unix pipeline tools. It likely feeds CI package-selection or coverage scripts.

## Risks
If no Go files match, `xargs` behavior may still produce an empty line. It does not validate `BASE_SHA`, so git errors propagate through the pipeline only according to shell defaults because `set -euo pipefail` is not enabled.

## Test Signals
No direct tests are present; correctness is observable through CI package selection.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/scripts/changed-go-pkgs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/scripts/check-workspace-clean.sh -->
# sources/storage-engines/pebble/scripts/check-workspace-clean.sh

## Purpose
This CI helper fails if the git workspace is dirty, typically after running generation commands.

## Important APIs, Types, and Functions
The script uses `set -euo pipefail`, `git status --porcelain`, `git status`, and `git diff --no-ext-diff -a`.

## Control Flow
It captures porcelain status including stderr. If non-empty, it prints status and diff to stderr, emits a generation-change error, and exits 1. Otherwise it exits successfully.

## State and Persistence Behavior
It does not mutate the workspace.

## Dependencies and Integration Points
It integrates with CI generation checks and any target that must prove generated files are committed.

## Risks
The error message is specific to `make generate`, even if another command dirtied the workspace. Capturing stderr into the condition means git command errors also cause failure.

## Test Signals
No direct tests are present; signal is CI failure with printed status and diff.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/scripts/check-workspace-clean.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/scripts/code-coverage-publish.sh -->
# sources/storage-engines/pebble/scripts/code-coverage-publish.sh

## Purpose
This script turns LCOV artifacts into HTML coverage reports with `genhtml` and publishes them to a Google Cloud Storage bucket.

## Important APIs, Types, and Functions
`publish PROFILE TITLE` validates the profile, builds a timestamp/SHA/title output directory, copies the profile with a useful name, runs `genhtml`, and uploads the directory with `gsutil -m cp -Z -r`.

The script publishes tests-only, meta-only, and combined coverage profiles, then regenerates and uploads an index page.

## Control Flow
With `set -euxo pipefail`, it publishes three reports under `artifacts/`, lists existing bucket directories, emits an HTML index sorted newest first, uploads it, and sets short cache-control metadata.

## State and Persistence Behavior
Local generated state is under `artifacts/`. Remote persistent state is under `gs://$BUCKET/pebble`, with default bucket `crl-codecover-public`.

## Dependencies and Integration Points
It depends on `genhtml`, `gsutil`, git, date, sed, grep, and LCOV files produced by `code-coverage.sh`.

## Risks
Bucket permissions, missing tools, or malformed profile paths fail the script. The generated index is hand-built HTML, so unexpected bucket names could affect output. It assumes `date -r` behavior available in the environment.

## Test Signals
No direct tests are present; success is published coverage directories and refreshed bucket index.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/scripts/code-coverage-publish.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/scripts/code-coverage.sh -->
# sources/storage-engines/pebble/scripts/code-coverage.sh

## Purpose
This script runs Pebble unit tests and metamorphic tests with coverage instrumentation, producing LCOV files for tests, meta tests, and combined coverage.

## Important APIs, Types, and Functions
It runs `go test -tags invariants ./... -coverprofile ... -coverpkg=./...`, builds an instrumented `internal/metamorphic/metarunner`, runs metamorphic tests with `GOCOVERDIR`, converts coverage with `go tool covdata textfmt`, and converts Go coverage to LCOV through `github.com/cockroachdb/code-cov-utils/convert@v1.1.0`.

## Control Flow
The script creates `artifacts`, allocates a temp directory with cleanup trap, records whether either test phase failed, still attempts coverage conversion, and warns at the end if tests failed.

## State and Persistence Behavior
Persistent outputs are `artifacts/profile-tests.gocov`, `profile-meta.gocov`, `profile-tests.lcov`, `profile-meta.lcov`, and `profile-tests-and-meta.lcov`. Temporary metarunner and coverage directories are removed on exit.

## Dependencies and Integration Points
It integrates with Go coverage tooling, Pebble metamorphic tests, `code-cov-utils`, and the publish script.

## Risks
Because it continues after failed tests, generated coverage can be incomplete. It intentionally does not cover crossversion metamorphic tests. Network/module availability is needed for `go run .../convert`.

## Test Signals
The main signal is successful artifact creation; a warning indicates coverage exists but may not represent a clean test run.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/scripts/code-coverage.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/scripts/crossversion_smoke_test.sh -->
# sources/storage-engines/pebble/scripts/crossversion_smoke_test.sh

## Purpose
This script validates the cross-version metamorphic test infrastructure by proving it passes on a clean release-to-HEAD combination and fails after introducing an intentional backward-compatibility bug.

## Important APIs, Types, and Functions
It defines colored `log`, `warn`, and `error` helpers plus a `cleanup` trap. It uses a patch file `crossversion_smoke_test.patch`, the `internal/metamorphic/crossversion` package, release and head test binaries, and `go test -run TestMetaCrossVersion`.

## Control Flow
The script verifies prerequisites and a clean git workspace, finds the latest `crl-release-*` branch, checks it out to build a release metamorphic test binary, returns to the original HEAD, builds a clean HEAD binary, and runs crossversion once expecting success.

It then applies the intentional patch, builds a buggy binary, verifies the buggy binary passes single-version testing, reverts the patch, and runs crossversion with release plus buggy head for up to 10 seeds expecting at least one failure. Cleanup removes generated binaries/artifacts and reverts patch changes if still applied.

## State and Persistence Behavior
It mutates git checkout state and applies/reverts a patch. It writes test binaries and smoke artifacts under `internal/metamorphic/crossversion`, and logs under `/tmp`. Cleanup removes these generated files and may run `git checkout -- .` if the patch was applied.

## Dependencies and Integration Points
Dependencies include git, Go, release branches, the intentional patch file, metamorphic and crossversion test packages, and CI grouping markers. It integrates directly with compatibility testing infrastructure.

## Risks
The script requires a clean repository and uses `git checkout -- .` during cleanup after patch application, which would be destructive if run with uncommitted work despite the upfront cleanliness check. Release-branch discovery by lexical sort may not match semantic latest in every naming scheme. The expected failure is randomized, so it loops over seeds but could still miss a bug if the patch/test relation changes.

## Test Signals
Success means clean crossversion passed, buggy single-version passed, and buggy crossversion failed within the attempt budget. Failure messages distinguish infrastructure regression, patch mismatch, existing compatibility bugs, and inability to detect the intentional bug.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/scripts/crossversion_smoke_test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/scripts/pr-codecov-run-tests.sh -->
# sources/storage-engines/pebble/scripts/pr-codecov-run-tests.sh

## Purpose
This script runs coverage-enabled tests for a caller-provided list of package paths and converts the result to JSON for PR code coverage workflows.

## Important APIs, Types, and Functions
Arguments are `output_json_file` and a space-separated `packages` string. It checks each package path for Go files, normalizes non-root paths to `./path`, runs `make testcoverage COVER_PROFILE=... PKG=...`, and converts with `gocover2json@v1.0.0`.

## Control Flow
It builds a valid path list, skips with an empty output file if no packages exist in the current checkout, creates a temporary coverprofile, runs coverage, converts to JSON, and removes the temp file on exit.

## State and Persistence Behavior
It writes the requested JSON file and a temporary coverage profile.

## Dependencies and Integration Points
It depends on Bash, `ls`, `mktemp`, `make testcoverage`, Go, and CockroachDB code coverage utilities. It tolerates package paths not present in the checkout, which is useful for PR diffs across branches.

## Risks
Package splitting uses shell word splitting, so paths with whitespace are unsupported. Missing packages are silently skipped. Conversion requires module/network availability unless cached.

## Test Signals
The JSON output is the primary artifact. Empty touched output means no valid packages were found.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/scripts/pr-codecov-run-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/scripts/run-crossversion-meta.sh -->
# sources/storage-engines/pebble/scripts/run-crossversion-meta.sh

## Purpose
This script builds metamorphic test binaries for provided branches and runs the crossversion metamorphic test across those versions.

## Important APIs, Types, and Functions
It records the current branch, creates a temp directory, iterates branch arguments, checks out each branch, derives a version label, optionally selects a Go toolchain for version `24.1`, builds `./internal/metamorphic` test binaries, then runs `./internal/metamorphic/crossversion` with accumulated `-version` flags.

## Control Flow
After building binaries for all branches, it checks out the original branch and either runs `go test` directly or wraps it in `stress -p 1` when `STRESS` is set. Runtime parameters come from `TIMEOUT`, `SEED`, and `FACTOR` environment variables. The temp directory is removed after the run.

## State and Persistence Behavior
The script mutates git checkout state and writes temporary binaries. Test artifacts are written to `./artifacts`.

## Dependencies and Integration Points
It depends on git, Go, optional Go toolchain selection through `GOTOOLCHAIN`, optional `stress`, and the crossversion metamorphic test package.

## Risks
There is no cleanup trap, so failures before the final `rm -rf` can leave temp files or the repo on a different branch. It uses a Bash array assignment style with backticks that works but is unusual. Dirty worktrees are not checked, so branch checkout can fail or disturb user state.

## Test Signals
Success is a passing `TestMetaCrossVersion` run over all provided branch binaries, optionally under stress. Artifacts in `./artifacts` capture failure details.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/scripts/run-crossversion-meta.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/scripts/run-tests-with-custom-go.sh -->
# sources/storage-engines/pebble/scripts/run-tests-with-custom-go.sh

## Purpose
This script builds or reuses a custom CockroachDB Go toolchain, then runs `go test -tags cockroach_go` for the provided arguments.

## Important APIs, Types, and Functions
It resolves `GO_SHA` directly or from `GO_BRANCH` with `git ls-remote`, caches toolchains under `${XDG_CACHE_HOME:-$HOME/.cache}/cockroachdb-go/$GO_SHA`, clones `https://github.com/cockroachdb/go.git`, builds with `src/make.bash`, sets `GOROOT` and `PATH`, and executes tests in `GITHUB_WORKSPACE` or the current directory.

## Control Flow
If the cached `go` binary is absent, it creates the cache directory, removes any partial checkout, clones and checks out the requested SHA, and builds the toolchain. It then exports the new Go path, prints `go version`, changes to the repo root, echoes the test command, and runs it.

## State and Persistence Behavior
Persistent state is the custom Go source/build cache. It may perform network clone and branch resolution. It does not modify repository source except through normal test side effects.

## Dependencies and Integration Points
It depends on git, Bash, Go bootstrap prerequisites, and CockroachDB's Go fork. It is designed for GitHub Actions and local runs.

## Risks
The default branch name is hard-coded. Cache corruption is handled only by removing the source tree when binary is missing, not by verifying an existing binary. Building Go is expensive and network-dependent. All caller arguments are passed to `go test` with the `cockroach_go` tag.

## Test Signals
Signal is the custom `go version` plus pass/fail from the target `go test` command.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/scripts/run-tests-with-custom-go.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/scripts/stress-new-tests.sh -->
# sources/storage-engines/pebble/scripts/stress-new-tests.sh

## Purpose
This script finds newly added Go test functions relative to a base branch and stress-runs only those tests package by package.

## Important APIs, Types, and Functions
It defaults `BASE_BRANCH` to `origin/master`, loops over `go list ./...`, normalizes module paths to relative package paths, extracts added `func Test...` names from zero-context git diff hunks, builds a `-run` regex, and runs `go test --tags invariants --exec 'stress ...'`.

## Control Flow
For each package with added tests, it prints the stress command and runs it with `stress -p 2 --maxruns 1000 --maxtime 10m --timeout 2m`. On first failure it prints the package/test regex and exits 1. If no failures occur, it prints a success message.

## State and Persistence Behavior
No persistent state is intentionally written beyond normal test artifacts.

## Dependencies and Integration Points
It depends on Go, git, grep, awk, cut, paste, sort, and the `stress` binary. It integrates with PR validation workflows focused on new tests.

## Risks
The parser only catches lines beginning `+func Test`, missing methods, fuzz tests, examples, or multiline declarations. It uses Unicode status symbols in output. Diffing package `*.go` paths can miss tests in unusual generated locations.

## Test Signals
A successful run means all detected new test functions survived stress settings. Failure exits at the first failing package.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/scripts/stress-new-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/scripts/stress.sh -->
# sources/storage-engines/pebble/scripts/stress.sh

## Purpose
This script stress-tests every Go package in Pebble one package at a time, giving high-state-space packages longer runtimes and lower parallelism.

## Important APIs, Types, and Functions
It loops through `go list ./...`, rewrites module paths to `.`-relative package paths, chooses stress parameters by package, and invokes `make stress STRESSFLAGS=... PKG=...`.

## Control Flow
Root, `internal/manifest`, `internal/metamorphic`, `sstable`, and `wal` get `30m`, `1000` max runs, and `75%` parallelism. Other packages get `5m`, `1000` max runs, and `100%` parallelism. The script stops on first failure through `set -euo pipefail`.

## State and Persistence Behavior
It does not intentionally persist state beyond whatever `make stress` and tests write.

## Dependencies and Integration Points
It depends on Go package listing and the repository's `make stress` target, which likely wraps the stress binary.

## Risks
Running all packages can be expensive. The package classification is hard-coded and may need updates as expensive packages shift. Because packages run serially, early failures prevent later package coverage.

## Test Signals
Success means every listed package passed its assigned stress budget. Command echoes show the exact stress settings per package.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/scripts/stress.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/snapshot.go -->
# sources/storage-engines/pebble/snapshot.go

## Purpose
This file implements Pebble point-in-time snapshots and eventually-file-only snapshots. Ordinary snapshots pin a sequence number and participate in snapshot-list compaction constraints. Eventually-file-only snapshots reduce write amplification by transitioning from a normal snapshot to a version-pinning file-only snapshot after relevant memtables are flushed.

## Important APIs, Types, and Functions
`Snapshot` stores the owning DB, sequence number, optional EFOS backpointer, and links in `snapshotList`. It implements `Reader` with `Get`, `NewIter`, `NewIterWithContext`, `ScanInternal`, and `Close`.

`snapshotList` is a doubly linked list with `init`, `empty`, `count`, `earliest`, `toSlice`, `pushBack`, and `remove`.

`EventuallyFileOnlySnapshot` stores either a wrapped `Snapshot` or refcounted `manifest.Version`, protected key ranges, DB pointer, sequence number, and closed channel.

`DB.makeEventuallyFileOnlySnapshot` chooses the snapshot sequence number while avoiding overlap with ongoing ingest-and-excise operations, then either immediately refs the current version or registers a normal snapshot until memtables flush.

`transitionToFileOnlySnapshot`, `hasTransitioned`, `waitForFlush`, `WaitForFileOnlySnapshot`, `Close`, `Get`, `NewIterWithContext`, and `ScanInternal` implement the EFOS lifecycle and reader behavior.

## Control Flow
Regular snapshot reads delegate to DB internals with the fixed snapshot sequence. Closing removes the snapshot from `db.mu.snapshots`, updates wide tombstone earliest-snapshot state if the earliest snapshot advances, and schedules compaction.

EFOS creation loops while overlapping ingest-and-excise operations with future sequence numbers exist, waiting on `ongoingExcisesRemovedCond`. It checks protected ranges against memtables to decide whether it can be file-only immediately. If not, it creates a normal `Snapshot` and later `waitForFlush` forces or schedules flushes until all relevant sequence numbers are flushed; compaction/flush code then transitions it to a version ref.

EFOS iterators and `ScanInternal` choose snapshot options from the version ref if transitioned, otherwise from the sequence number alone.

## State and Persistence Behavior
Snapshots pin sequence numbers and can keep obsolete keys or files live. EFOS eventually releases the normal snapshot and pins a manifest version instead, increasing space amplification through zombie SSTable retention while avoiding memtable pinning. Closing releases snapshot-list membership or version refs and closes a channel used to signal waiters.

## Dependencies and Integration Points
This code integrates with DB mutex state, visible sequence numbers, memtable queues, flush scheduling, compaction scheduling, wide tombstone tracking, manifest version refcounts, ingest-and-excise bookkeeping, iterator construction, and `scanInternalImpl`.

## Risks
Lock ordering is critical: DB mutex before EFOS mutex. EFOS creation can starve if overlapping ingest-and-excise operations keep appearing. `Close` is not idempotent for EFOS and closes a channel directly. Snapshot methods panic on use after close. Incorrect transition timing around excise could expose pre-excise keys, which the comments and tests explicitly guard against.

## Test Signals
`snapshot_test.go` covers snapshot iteration, snapshot closure panics, range-deletion stress, snapshot creation race, and EFOS/excise race. `scan_internal_test.go` also exercises `ScanInternal` through snapshots and EFOS.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/snapshot.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/snapshot_test.go -->
# sources/storage-engines/pebble/snapshot_test.go

## Purpose
This file tests ordinary snapshots and eventually-file-only snapshots for read consistency, closure semantics, range deletion correctness, snapshot creation atomicity, and EFOS interaction with ingest-and-excise.

## Important APIs, Types, and Functions
`TestSnapshotListToSlice` verifies linked-list insertion order.

`testSnapshotImpl` is a datadriven harness shared by `TestSnapshot` and `TestEventuallyFileOnlySnapshot`, using commands for DB definition, writes, deletes, merges, snapshots, compactions, DB state, and iterator movement.

`TestSnapshotClosed` verifies that using a closed snapshot panics with `ErrClosed`.

`TestSnapshotRangeDeletionStress` creates many snapshots around expanding range deletions and checks each snapshot's visible key count in parallel.

`TestNewSnapshotRace` exercises atomicity between sequence-number acquisition and snapshot list insertion under mutex contention and concurrent overwrite/flush.

`TestEFOSAndExciseRace` reproduces and validates a race fix around EFOS creation during a blocked ingest-and-excise.

## Control Flow
The shared datadriven harness rebuilds an in-memory DB per `define`, applies scripted operations, captures named readers, and drives iterators through commands. Stress and race tests use goroutines, channels, wait groups, and explicit mutex blocking hooks to force interleavings.

## State and Persistence Behavior
All state is in-memory. Snapshot maps are closed during cleanup. EFOS tests create protected ranges covering the snapshot test keyspace. The excise race test uses a private testing hook to block ingest apply while creating EFOS.

## Dependencies and Integration Points
Tests integrate with DB writes, flushes, compactions, `Reader` interface methods, VFS, private ingest hooks, range deletion visibility, and Go concurrency primitives.

## Risks
Race tests rely on timing and forced hooks. The range-deletion stress test is parallel and can surface data races or iterator bugs. The EFOS test depends on precise sequencing around ingest-and-excise visibility and file-only transition.

## Test Signals
Signals include stable datadriven iterator output, expected panics after close, exact key counts for historical snapshots under range deletions, no lost key during concurrent snapshot creation, and EFOS seeing only post-excise keys before and after file-only transition.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/snapshot_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/attributes.go -->
# sources/storage-engines/pebble/sstable/attributes.go

## Purpose
This file defines an `Attributes` bitset describing notable features present in an SSTable, such as value blocks, range keys, range deletions, two-level indexes, blob values, and point keys.

## Important APIs, Types, and Functions
`Attributes` is a `uint32` bitset. Constants include `AttributeValueBlocks`, `AttributeRangeKeySets`, `AttributeRangeKeyUnsets`, `AttributeRangeKeyDels`, `AttributeRangeDels`, `AttributeTwoLevelIndex`, `AttributeBlobValues`, and `AttributePointKeys`.

`Intersects` checks whether any requested bits are present. `Has` checks whether all requested bits are present. `Add` mutates the receiver by OR-ing bits. `String` returns a deterministic bracketed comma-separated list for testing and diagnostics.

## Control Flow
The methods are direct bit operations. `String` appends names in constant declaration order and joins them.

## State and Persistence Behavior
No persistence is performed here, but the bitset likely reflects persisted table properties or computed table metadata elsewhere in the sstable package.

## Dependencies and Integration Points
The only dependency is `strings`. Callers use attributes to reason about table contents and feature-dependent behavior.

## Risks
Adding new attributes requires updating `String` to keep diagnostics complete. `Has(0)` returns true by bitset convention, which callers should understand.

## Test Signals
No direct test file is listed, but string output is explicitly described as for testing and should be covered where attributes are emitted.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/attributes.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/blob.go -->
# sources/storage-engines/pebble/sstable/blob/blob.go

## Purpose
This file implements blob file writing, footer encoding/decoding, blob file reading, layout inspection, and V2 properties. Blob files store separated values referenced by SSTables.

## Important APIs, Types, and Functions
`FileFormat` defines `FileFormatV1`, `FileFormatV2`, and string formatting. V2 adds property and reserved metaindex handles to the footer.

`FileWriterOptions` controls format, compression, checksum, flush governor, compression counters, and CPU measurement.

`FileWriterStats` reports block count, value count, uncompressed bytes, file length, properties, and likely MVCC garbage bytes.

`FileWriter` writes value blocks asynchronously through a write queue, tracks an `indexBlockEncoder`, and emits metadata/footer on close.

`NewFileWriter`, `AddValue`, `FlushForTesting`, `EstimatedSize`, `Close`, and `writeMetadataBlock` are the primary writer APIs.

`fileFooter` encodes and decodes checksummed V1/V2 footers with magic strings, index handle, checksum type, format, original file number, and V2 properties handle.

`FileReader` wraps a block reader and footer. `NewFileReader`, `ReadValueBlock`, `ReadIndexBlock`, `IndexHandle`, `Layout`, `ReadProperties`, and `FormatVersion` provide read access.

`FileProperties` currently stores compression stats and encodes/decodes them through a key-value colblk block.

## Control Flow
Writer creation initializes encoders, compression, and a goroutine draining compressed value blocks. `AddValue` flushes if the governor says the current block should close, encodes the value, updates stats, and returns a handle with file, block, value ID, and value length. `flush` compresses a value block, updates offsets/stats, and sends it to the write goroutine, which writes bytes and records index block handles. `Close` flushes pending values, waits for the write queue, writes the index block, optionally writes V2 properties, writes the footer, finishes the writable, resets pooled state, and returns stats.

Reader creation reads the max footer length from the tail, decodes the footer, and initializes a block reader with the file checksum type. Value/index/properties reads use block reader APIs and metadata initializers.

## State and Persistence Behavior
The persisted blob file layout is value blocks, index block, optional V2 properties block, and footer. Footer CRC protects footer fields. Index blocks map block IDs to offsets and optional virtual mappings for rewrites. Writer state is pooled and reset after successful close; failed close aborts the writable and keeps the error for subsequent close attempts.

## Dependencies and Integration Points
This code integrates with objstorage `Writable`/`Readable`, sstable `block` compression/checksum/cache APIs, colblk key-value blocks, CRC, CPU measurement, compression counters, file cache options, and blob index/value block metadata.

## Risks
`Close` panics if no blocks were written or block counts mismatch. Async write queue errors are deferred to close. Pooled writer reuse requires thorough reset. Footer magic and format checks must stay backward compatible. `Layout` is diagnostic and reads all physical blocks, so it is not for hot paths.

## Test Signals
`blob_test.go` datadriven writer tests cover V1/V2 output, sparse virtual mappings, file stats, compression counters, reader footer/properties inspection, and handle round-trip via `handle.go`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/blob.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/blob_test.go -->
# sources/storage-engines/pebble/sstable/blob/blob_test.go

## Purpose
This file tests blob file writing, reader footer/properties inspection, sparse virtual-block layouts, writer stats, compression counters, and inline handle encode/decode round trips.

## Important APIs, Types, and Functions
`TestBlobWriter` supports datadriven `build`, `build-sparse`, and `open` commands. It uses `scanFileWriterOptions` to parse target block size, threshold, compression, and format.

`printFileWriterStats` renders writer stats and compression counters.

`TestHandleRoundtrip` encodes `InlineHandle`, decodes preface and suffix, and compares the results.

## Control Flow
`build` creates a memory object, writes each input line as a blob value, prints handles, closes the writer, and prints stats. `build-sparse` also interprets flush and virtual-block marker lines to force sparse/rewritten-style layouts. `open` creates a `FileReader`, prints footer fields and properties, then closes it.

## State and Persistence Behavior
The in-memory object persists between `build` and `open` commands within a datadriven run. Writer options decide format and compression behavior.

## Dependencies and Integration Points
Tests use `objstorage.MemObj`, blob writer/reader APIs, block compression profiles, datadriven input, and handle encode/decode from `handle.go`.

## Risks
Golden output is sensitive to compression, block-size thresholds, footer format, stats accounting, and handle string formatting. `build-sparse` reaches into writer internals, so refactoring may require test updates.

## Test Signals
Stable handles, stats, compression counters, footer fields, property text, and handle roundtrip equality signal correctness across writer, reader, and handle encoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/blob_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/blocks.go -->
# sources/storage-engines/pebble/sstable/blob/blocks.go

## Purpose
This file implements the columnar encoders and decoders for blob file index blocks and blob value blocks.

## Important APIs, Types, and Functions
`indexBlockEncoder` tracks physical block count, virtual block count, virtual block mappings, offsets, and a colblk encoder. `AddBlockHandle` records block start/end offsets. `AddVirtualBlockMapping` maps original virtual block IDs to physical block indexes and value-ID offsets, filling gaps as unreferenced. `Finish` serializes the index block with a custom header containing virtual block count.

`indexBlockDecoder` decodes virtual block mappings and offsets. `BlockHandle`, `RemapVirtualBlockID`, `BlockCount`, `DebugString`, and `Describe` expose decoded metadata.

`initIndexBlockMetadata` casts block metadata to an index decoder and converts initialization panics into corruption errors.

`blobValueBlockEncoder` stores blob values in a single `colblk.RawBytesBuilder` column. `Init`, `Reset`, `AddValue`, `Count`, `size`, and `Finish` manage encoding and serialization.

`blobValueBlockDecoder` decodes the raw-bytes column and provides `DebugString` and `Describe` diagnostics. `initBlobValueBlockMetadata` initializes decoder metadata and converts panics into corruption errors.

## Control Flow
Index encoding stores offsets as `n+1` entries for `n` physical blocks. The first handle records offset 0, later handles must start at the previous end offset or panic. Virtual mappings must be added in ascending virtual ID order; gaps are filled with sentinel mappings to unreferenced blocks. Decoding reads the virtual count from the first four bytes, then decodes virtual and offset columns from the colblk block. Value-block encoding serializes all pending raw values into one colblk block and appends the standard padding byte.

## State and Persistence Behavior
The index block is persisted inside each blob file and drives all later value retrieval. Physical block lengths are inferred from adjacent offsets minus `block.TrailerLen`. Virtual mappings preserve handle compatibility after blob file rewrite. Each physical value block persists a count of rows and raw-byte offsets/data for constant-time value lookup.

## Dependencies and Integration Points
The implementation depends on `colblk` builders/decoders, `block.Handle`, block metadata casting, `binfmt` and `treeprinter` diagnostics, invariants bounds checks, and base corruption/assertion errors. It is consumed by `FileWriter`, `FileReader`, `ValueFetcher`, and `FileRewriter`.

## Risks
Incorrect offset accounting corrupts all blob value reads. The virtual-block sentinel uses the low 32 bits as `0xffffffff`; readers treat a value-ID offset equal to that mask as unreferenced, so encoding/decoding assumptions must remain aligned. Panic-to-corruption conversion is important for untrusted file data.

## Test Signals
`blocks_test.go` covers index block build, debug formatting, block handle lookup, and virtual block remapping. Fetcher and rewrite tests indirectly cover value block decoding.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/blocks.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/blocks_test.go -->
# sources/storage-engines/pebble/sstable/blob/blocks_test.go

## Purpose
This file provides datadriven coverage for blob index block encoding and decoding.

## Important APIs, Types, and Functions
`TestIndexBlockEncoding` supports `build`, `get`, and `remap-virtual-blockid`. It builds an `indexBlockEncoder` from input block handles and optional virtual mappings, initializes an `indexBlockDecoder`, prints debug structure, retrieves physical block handles, and remaps virtual IDs.

## Control Flow
The `build` command reads offset/length lines until a `virtual-block-mappings` marker, then parses mapping rows as virtual block ID, physical block index, and value ID offset. Subsequent commands operate on the last decoded block.

## State and Persistence Behavior
The encoded index block is held in memory by the decoder across datadriven commands.

## Dependencies and Integration Points
The test uses `datadriven`, `crstrings`, `block.Handle`, and `require`. It directly tests index block APIs used by blob readers and rewriters.

## Risks
Debug-string golden output can change when colblk formatting changes. The test focuses on index blocks and does not cover value block payloads.

## Test Signals
Expected output validates offset-column encoding, custom header decoding, virtual mapping gap behavior, block handle reconstruction, and remap results.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/blocks_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/doc.go -->
# sources/storage-engines/pebble/sstable/blob/doc.go

## Purpose
This package documentation explains the blob file format used for separated values, including value blocks, index blocks, footers, and sparse rewrites.

## Important APIs, Types, and Functions
Although it contains no executable APIs, it defines the conceptual contract for `BlockID`, `BlockValueID`, index block virtual mappings, physical offsets, value block raw-byte columns, and V1/V2 footer fields.

## Control Flow
The documented read path is: an SSTable stores a blob handle with blob file reference, block ID, and block value ID; a reader loads the blob file index block; it maps the block ID to a physical block handle; then it loads the value block and indexes into the raw-bytes column.

## State and Persistence Behavior
The documentation is the persisted-format guide. It describes a file as value blocks followed by an index block and fixed footer. Rewrites may elide unreferenced values while keeping old handles valid through virtual block mappings and empty value placeholders.

## Dependencies and Integration Points
It aligns with `handle.go`, `blocks.go`, `blob.go`, `fetcher.go`, and `rewrite.go`, and references `colblk` as the columnar encoding mechanism.

## Risks
Documentation drift would be high impact because this file explains on-disk compatibility. The TODOs around virtual-block integer interleaving and possible null bitmap indicate future format evolution considerations.

## Test Signals
The executable tests in the blob package validate the format described here through writer, reader, index block, fetcher, and rewrite behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/fetcher.go -->
# sources/storage-engines/pebble/sstable/blob/fetcher.go

## Purpose
This file implements `ValueFetcher`, the hot-path component that retrieves separated values from blob files using blob handles, reader caching, index blocks, and value block caching.

## Important APIs, Types, and Functions
`ValueReader` abstracts blob file readers that can return index and value blocks and initialize read handles.

`ReaderProvider` obtains `ValueReader`s for object metadata, typically through Pebble's file cache.

`SuggestedCachedReaders` sizes the fetcher's reader cache from read amplification.

`ValueFetcher.Init`, `FetchHandle`, `Fetch`, `retrieve`, and `Close` provide the public lifecycle and retrieval APIs implementing `base.ValueFetcher`.

`cachedReader` stores a value reader, close function, read handle, lazy-loaded index block decoder, and currently loaded value block decoder.

`cachedReader.GetUnsafeValue` remaps virtual block IDs when needed, reads the relevant physical block, records retrieval profiling, and returns a slice into cached block data.

## Control Flow
On first retrieval, `ValueFetcher` obtains a pooled cached-reader set sized to `maxCachedReaders` with a minimum allocation. Each lookup scans the reader array for the blob file ID or the least recently used slot. Cache misses close any replaced reader, map the blob file ID to object info, obtain a new reader, initialize a read handle, and update stats.

Within a cached reader, the index block is read lazily. If the requested virtual block differs from the loaded block, it remaps through the index block if rewritten, loads the physical value block, and releases the previous block. It then converts the handle's value ID plus any value-ID offset into a raw-bytes index and returns that value.

## State and Persistence Behavior
No persistent state is written. Runtime state includes cached file readers, read handles, block buffer handles, decoded metadata pointers, fetch counts, stats, and optional invariant buffer mangling. Returned values are unsafe slices valid only until the next fetch on that reader or close.

## Dependencies and Integration Points
The fetcher integrates with base blob file mapping and value fetcher interfaces, objstorage read handles, block cache/read environments/stats, file cache reader providers, blob `HandleSuffix`, index/value block decoders, and value retrieval profiling.

## Risks
This is a performance-sensitive path with O(cache-size) reader lookup. It relies on callers closing the fetcher to release readers and block buffers. Returned values are not caller-owned. Virtual remapping and unreferenced sentinel handling must match rewrite encoding. Bounds checks are invariant-based, so corrupted files must be caught earlier by block/index initialization where possible.

## Test Signals
`fetcher_test.go` covers datadriven fetcher cache state, multi-file reader reuse, randomized sequential and random retrieval over large blobs, and benchmarks for cached/uncached retrieval patterns.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/fetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/fetcher_test.go -->
# sources/storage-engines/pebble/sstable/blob/fetcher_test.go

## Purpose
This file tests and benchmarks blob `ValueFetcher` retrieval, reader caching, block caching, and sequential/random access patterns.

## Important APIs, Types, and Functions
`identityFileMapping` maps blob file IDs directly to disk file numbers for tests.

`mockReaderProvider` records reader requests and returns prebuilt `FileReader`s.

`TestValueFetcher` is a datadriven harness with `define`, `new-fetcher`, and `fetch` commands.

`writeValueFetcherState` prints cached reader slots and current physical block indexes.

`TestValueFetcherRetrieveRandomized` writes about 4 MiB of random values and validates sequential and random retrieval against saved handles.

`BenchmarkValueFetcherRetrieve` and `benchmarkValueFetcherRetrieve` measure sequential/random retrieval with and without block cache priming.

`makeMockReaderProvider` constructs readers with optional block cache handles and can prepopulate value blocks.

## Control Flow
Datadriven `define` writes a blob file into a memory object, opens a `FileReader`, and registers it. `new-fetcher` creates a fetcher with a selected reader cache size. `fetch` encodes a handle suffix, calls `FetchHandle`, prints cache state, and prints the returned value.

Randomized tests generate values and handles, close the writer, open a reader, then exercise `retrieve` in sequential and shuffled orders. Benchmarks generate larger blob files and repeatedly fetch handles.

## State and Persistence Behavior
Memory objects hold blob files for each test. Fetchers and readers are closed in defers. Optional cache state is held by `cache.Cache` and `cache.Handle`.

## Dependencies and Integration Points
Tests integrate with objstorage memory objects, block reader cache options, sstable internal cache options, random test utilities, and leaktest.

## Risks
Randomized tests log time-based seeds, so failures require seed capture. Benchmarks are sensitive to compression/block-cache behavior and hardware. The mock provider's close function is a no-op, so production file-cache refcount behavior is not fully modeled.

## Test Signals
Signals include exact returned values, expected reader cache state, reader cache miss traces, equality over randomized retrieval, and benchmark performance deltas for cached versus uncached access.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/fetcher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/handle.go -->
# sources/storage-engines/pebble/sstable/blob/handle.go

## Purpose
This file defines blob value handle types and fast varint encoding/decoding used inside SSTable values and blob retrieval paths.

## Important APIs, Types, and Functions
`MaxInlineHandleLength` bounds encoded inline handles.

`BlockValueID`, `BlockID`, and `Handle` identify a value within a blob file. `Handle` string formatting is redact-safe.

`InlineHandlePreface` stores the SSTable-local blob reference ID and value length. `HandleSuffix` stores block ID and value ID. `InlineHandle` combines both.

`HandleSuffix.Encode` and `InlineHandle.Encode` varint-encode fields.

`DecodeInlineHandlePreface` decodes reference ID and value length with manually inlined unsafe uvarint logic.

`DecodeHandleSuffix` decodes block ID and value ID with manually inlined unsafe uvarint logic.

## Control Flow
Encoding uses `binary.PutUvarint`. Decoding reads up to five bytes per uint32 field with unrolled branches, updating the remaining source slice for preface decoding and an unsafe pointer for suffix decoding.

## State and Persistence Behavior
Inline handles are persisted within SSTable value blocks, referring indirectly to blob files through the containing table's blob references. Full `Handle` values are runtime descriptions that include the resolved blob file ID.

## Dependencies and Integration Points
The code integrates with `base.BlobFileID`, `base.BlobReferenceID`, redact-safe formatting, and `ValueFetcher.FetchHandle`. It is exercised by blob writer/fetcher tests and by SSTable code that returns `InternalValue`s.

## Risks
Unsafe decoders assume the source buffer is well-formed and long enough for encoded fields; malformed inputs can panic or read out of bounds if not validated by higher layers. Manual decoding must stay semantically equivalent to uvarint encoding. Maximum length assumes four 32-bit varints.

## Test Signals
`TestHandleRoundtrip` in `blob_test.go` validates representative inline handle encode/decode round trips.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/handle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/rewrite.go -->
# sources/storage-engines/pebble/sstable/blob/rewrite.go

## Purpose
This file implements `FileRewriter`, which copies a live subset of values from an input blob file into a new blob file while preserving compatibility with existing handles.

## Important APIs, Types, and Functions
`FileRewriter` stores the original blob file ID, an output `FileWriter`, and an input `ValueFetcher`.

`NewFileRewriter` creates the writer, initializes a fetcher over a single input file mapping, and accepts output file number, writable, and writer options.

`CopyBlock` copies selected value IDs from one original block ID into the output file, preserving ascending block order and adding virtual block mappings.

`Close` closes the output writer and input fetcher, combining errors.

`inputFileMapping` implements `base.BlobFileMapping` by always returning the same input object.

## Control Flow
`CopyBlock` sorts requested value IDs. If pending output values plus the next block's total value size exceed the flush governor, it flushes before starting so all copied values for one original block remain in one physical block. It records a virtual block mapping from original block ID to current physical block and value offset. It skips duplicate value IDs, fills internal gaps with nil values to preserve value-ID indexing, fetches each referenced value from the original file, rejects empty copied values, and appends it to the output block.

## State and Persistence Behavior
The output blob file persists only live values plus nil placeholders for sparse gaps inside copied virtual blocks. The index block's virtual mapping allows old handles to resolve into the rewritten file. The rewriter does not persist liveness metadata itself; callers provide the value IDs to retain.

## Dependencies and Integration Points
It depends on blob `FileWriter`, `ValueFetcher`, objstorage writable, block read environment, base object info, and blob index virtual mapping semantics. It is intended for value-separation garbage collection or blob-file compaction.

## Risks
`CopyBlock` must be called with ascending block IDs; the encoder enforces ordering through virtual mapping assertions. Duplicate value IDs are tolerated due to missing per-SSTable liveness data, but this is a workaround. Empty values are rejected, so callers must not request handles that legitimately point to empty blob values. Incorrect `totalValueSize` can produce suboptimal or invalid block grouping decisions.

## Test Signals
Direct tests are not listed here, but blob writer sparse tests and fetcher retrieval tests exercise the core virtual mapping and handle-preservation mechanisms used by rewriter output.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/blob/rewrite.go -->
