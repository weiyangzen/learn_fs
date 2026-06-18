# sources/user-network-fs/rclone/cmd/bisync/testdata/bisync_vscode_debuggers_launch.json lines 21882-29582

## Scope

This chunk covers a middle segment of the generated VS Code debugger launch matrix for rclone bisync tests. The assigned range begins inside the tail of one `:memory:` `test_equal` launch object and ends inside a `TestSFTPOpenssh:` `test_compare_all RemoteLocal` object, so it is a partial view of the enclosing JSON document. The full file is a `launch.json`-style object with `version: "0.2.0"` and a single `configurations` array.

Within this range there are 963 complete `name`/`args` launch entries. They all use the same Go debug adapter shape:

- `"type": "go"`
- `"request": "launch"`
- `"mode": "test"`
- `"program": "./cmd/bisync"`
- `"args": ["-remote", <path1>, "-remote2", <path2>, "-case", <testcase>, "-no-cleanup"]`

## Purpose

The file is developer tooling testdata, not runtime product logic. It gives rclone maintainers prebuilt VS Code Go debugger configurations for running individual bisync integration scenarios against selected backend pairs. The generator in `cmd/bisync/bisync_debug_test.go` documents the intended workflow: generate a large launch file, then copy only the needed entries into a real VS Code `launch.json` because VS Code can struggle with the full matrix.

This chunk specifically exercises the same bisync test-case set across memory, nStorage, OneDrive, OneDriveBusiness, multiple S3 variants, and the opening part of the SFTP OpenSSH backend block. Each entry pins a single `-case` value and keeps test artifacts with `-no-cleanup`, which is useful during debugger sessions.

## Important Data Shapes And APIs

The data shape is a repeated VS Code debug configuration object. There are no JSON functions or exported APIs, but each object maps directly to the Go test flags defined by the bisync test harness:

- `-remote`: the first bisync path under test, consumed through rclone's fstest remote flag path.
- `-remote2`: the second bisync path, defined in `bisync_test.go` as `argRemote2`.
- `-case`: the bisync fixture directory selector, defined as `argTestCase`.
- `-no-cleanup`: leaves remote and local test state behind for post-debug inspection.
- `program: "./cmd/bisync"` plus `mode: "test"`: tells the Go VS Code adapter to launch tests for the `cmd/bisync` package.

The visible launch names encode `Test <backend> <case> <orientation>`. The orientation maps to how the generator fills `-remote` and `-remote2`:

- `LocalRemote`: `-remote local`, `-remote2 <backend>`
- `RemoteLocal`: `-remote <backend>`, `-remote2 local`
- `RemoteRemote`: both sides use `<backend>`

The chunk contains these remote names in the `args` fields: `local`, `:memory:`, `TestnStorage:`, `TestOneDrive:`, `TestOneDriveBusiness:`, `TestS3:`, `TestS3,directory_markers:`, `TestS3Rclone:`, `TestS3Minio:`, `TestS3MinioEdge:`, `TestS3Wasabi:`, `TestS3Alibaba:`, `TestS3R2:`, and `TestSFTPOpenssh:`.

The 27 visible test cases are `test_all_changed`, `test_backupdir`, `test_basic`, `test_changes`, `test_check_access`, `test_check_access_filters`, `test_check_filename`, `test_check_sync`, `test_compare_all`, `test_createemptysrcdirs`, `test_dry_run`, `test_equal`, `test_ext_paths`, `test_extended_filenames`, `test_filters`, `test_filtersfile_checks`, `test_ignorelistingchecksum`, `test_max_delete_path1`, `test_max_delete_path2_force`, `test_nomodtime`, `test_normalization`, `test_rclone_args`, `test_resolve`, `test_resync`, `test_resync_modes`, `test_rmdirs`, and `test_volatile`.

## Control Flow

There is no control flow in the JSON itself. The effective control flow appears when a developer selects one launch entry in VS Code:

1. VS Code invokes the Go debug adapter in test mode for `./cmd/bisync`.
2. The adapter starts the package tests with the configured `args`.
3. The bisync test harness routes to `TestBisyncLocalRemote`, `TestBisyncRemoteLocal`, or `TestBisyncRemoteRemote` depending on the selected arguments and test function selected by Go.
4. `testBisync` creates a unique temp directory, workdir, log path, and remote pair.
5. `runTestCase` selects the `test_<case>` fixture directory under `cmd/bisync/testdata`, copies initial content to both sides, executes scripted fixture steps, and runs `bisync.Bisync` through `runBisync`.
6. `-no-cleanup` keeps generated state after the run for debugger inspection.

The generator control flow in `bisync_debug_test.go` is matrix expansion: parse backend config from `fstest/test_all/config.yaml`, list non-empty `test_*` fixture directories, iterate backends, cases, and the three variations, then write `testdata/bisync_vscode_debuggers_launch.json` using a fixed text template.

## State And Persistence Behavior

The JSON file is static generated testdata committed in the source tree. It does not persist state by itself. When used, each launch entry causes the bisync test harness to create temporary per-run state:

- unique temp roots and workdirs under the OS temp directory;
- remote test directories for path1 and path2;
- listing, queue, filter, lock, and log files under the bisync workdir;
- copied fixture data from `testdata/test_<case>/initial` and optional `modfiles`.

The `-no-cleanup` flag deliberately changes cleanup behavior. It preserves these artifacts so a developer can inspect listings, queues, logs, and remote contents after a debug run. That is valuable for debugging but can leave remote objects, local temp directories, and credentials-backed backend state until manually removed.

## Dependencies And Integration Points

Primary integration points:

- VS Code Go debugging: consumes the `launch.json` schema fields and starts Go package tests.
- `cmd/bisync/bisync_debug_test.go`: source generator for this file. Its `debugFormat` and `docFormat` define the repeated JSON layout.
- `cmd/bisync/bisync_test.go`: defines the command-line flags used by every `args` array, including `-case`, `-remote2`, and `-no-cleanup`.
- `fstest/test_all/config.yaml`: supplies backend remotes used by the generator, including the backend names visible in this chunk.
- `cmd/bisync/testdata/test_*`: fixture directories supplying the cases named by `-case`.
- rclone filesystem backends: entries such as OneDrive, S3 variants, and SFTP require configured test remotes and their normal credentials/environment.
- `bisync.Bisync`: the product function ultimately exercised by the test harness.

This chunk's backend coverage is broad enough to signal cross-backend bisync debugging needs: in-memory behavior, local/remote permutations, cloud object stores, directory-marker S3 behavior, OneDrive variants, and SFTP.

## Risks And Maintenance Notes

- The file is generated and very large. Manual edits are likely to drift from `bisync_debug_test.go` and may be overwritten by regeneration.
- The full file is intentionally too large for comfortable VS Code use. Developers should copy selected entries rather than load the whole matrix into an active workspace configuration.
- Some chunk boundaries split JSON objects. Research or tooling that validates only this range as standalone JSON will fail even though the full file is structured as one document.
- Launch names must stay aligned with `args`; otherwise a developer could run a different backend/case/orientation than the label says.
- Backend names are environment-sensitive. `TestOneDrive:`, `TestS3R2:`, `TestSFTPOpenssh:`, and similar entries require configured rclone test remotes and may fail or skip outside the maintainer's test environment.
- `-no-cleanup` is useful for debugging but increases cleanup burden and can leave remote test data or local temp files behind.
- The generator skips non-`RemoteRemote` variations only for the `local` backend. Non-local backends expand to all three orientations, producing many entries and making duplicate or stale config harder to spot by inspection.

## Test Signals

Good validation signals for this chunk and its generator include:

- Regenerating `bisync_vscode_debuggers_launch.json` from `bisync_debug_test.go` produces the same repeated object shape and argument ordering.
- A representative entry from each orientation launches the expected Go bisync test and reaches the matching `-case` fixture.
- The `name` backend, case, and orientation agree with the `-remote`, `-remote2`, and `-case` values.
- `:memory:` and fully remote backends exercise the same case list where the generator's backend/case matrix permits it.
- S3 variant entries remain present for backend-specific bisync behavior such as directory markers, object-store modtime/checksum handling, and R2/Wasabi/Alibaba/Minio compatibility.
- Debug runs with `-no-cleanup` leave enough workdir artifacts for inspection, and cleanup procedures can remove those artifacts afterwards.

Because this chunk is generated JSON, the strongest regression coverage is generator-level comparison plus a small set of end-to-end debug/test launches rather than hand-validating all 963 repeated entries.
