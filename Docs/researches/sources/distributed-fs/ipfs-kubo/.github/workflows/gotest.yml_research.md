# sources/distributed-fs/ipfs-kubo/.github/workflows/gotest.yml

## Purpose
This workflow runs Kubo's main Go test lanes: unit tests with coverage, CLI integration tests, FUSE tests, and example tests.

## Important APIs, Types, And Functions
Jobs call `make test_unit`, `make test_cli`, `make test_fuse`, and `make test_examples`. They use Codecov, `ipdxco/gotest-json-to-junit-xml`, `ipdxco/junit-xml-to-html`, and `actions/upload-artifact` to convert and publish reports.

## Control Flow
Unit and CLI jobs install `zsh`; CLI and FUSE tests set `IPFS_PATH` to runner temp dirs. FUSE tests install `fuse3` when needed, clean stale mounts before and after tests, and run with `GOTRACEBACK=all`. Each report-generation/upload step runs on success or failure.

## State And Persistence Behavior
The workflow creates coverage profiles, JSON test logs, JUnit XML, HTML/Markdown reports, temporary repos, and temporary FUSE mounts. Artifacts and coverage are persisted externally.

## Dependencies And Integration Points
It integrates Kubo Make targets, test harnesses, FUSE kernel/userland tools, Codecov, report conversion tools, and GitHub self-hosted runner labels.

## Risks And Test Signals
Risks include FUSE mount leakage, self-hosted runner state, report conversion failures hiding raw test context, and Make target coupling. Signals include no failed entries in `gotest.json`, successful CLI/FUSE/example targets, uploaded reports, and coverage artifacts.
