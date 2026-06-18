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
