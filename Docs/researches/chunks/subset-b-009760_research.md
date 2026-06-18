# sources/user-network-fs/rclone/cmd/bisync/testdata/bisync_vscode_debuggers_launch.json lines 7282-14457

## Purpose

This chunk is part of rclone bisync's generated VS Code debugger launch matrix. The file is produced by `cmd/bisync/bisync_debug_test.go` so developers can copy selected configurations into a real `.vscode/launch.json` and debug individual bisync integration-style test cases from VS Code.

The assigned range is not a standalone JSON document. It starts inside the `args` field for `Test TestChunkerChunk50bYandex: test_resync_modes LocalRemote` and ends inside the next object after `Test TestCompressSwift: test_rmdirs RemoteRemote`. Within those boundaries it contains 896 complete launch configuration objects, plus one leading partial object and one trailing partial object. The complete objects cover backend remotes from late `TestChunkerChunk50bYandex:` through most of `TestCompressSwift:`.

## Structure And Data Shape

Each complete entry follows the generator's fixed `debugFormat` shape:

- `name`: `Test <remote> <testcase> <variation>`.
- `type`: always `go`, selecting the VS Code Go debugger.
- `request`: always `launch`.
- `mode`: always `test`, so the Go extension launches a test binary rather than a normal program.
- `program`: always `./cmd/bisync`.
- `args`: always `["-remote", <path1>, "-remote2", <path2>, "-case", <testcase>, "-no-cleanup"]`.

The three debugger variations encode bisync side placement:

- `LocalRemote`: `-remote local`, `-remote2 <backend>`.
- `RemoteLocal`: `-remote <backend>`, `-remote2 local`.
- `RemoteRemote`: both sides use the same backend remote.

The complete objects in this chunk exercise the 27 bisync test-case directories generated from `b.dataRoot`: `test_all_changed`, `test_backupdir`, `test_basic`, `test_changes`, `test_check_access`, `test_check_access_filters`, `test_check_filename`, `test_check_sync`, `test_compare_all`, `test_createemptysrcdirs`, `test_dry_run`, `test_equal`, `test_ext_paths`, `test_extended_filenames`, `test_filters`, `test_filtersfile_checks`, `test_ignorelistingchecksum`, `test_max_delete_path1`, `test_max_delete_path2_force`, `test_nomodtime`, `test_normalization`, `test_rclone_args`, `test_resolve`, `test_resync`, `test_resync_modes`, `test_rmdirs`, and `test_volatile`.

## Covered Remotes

The line span is a contiguous slice through the backend loop from the generator. It contains:

- the last `TestChunkerChunk50bYandex:` entries for `test_resync_modes`, `test_rmdirs`, and `test_volatile`;
- full 27-case, 3-variation blocks for `TestChunkerChunk50bBox:`, `TestChunkerS3:`, `TestChunkerChunk50bS3:`, `TestChunkerChunk50bMD5HashS3:`, `TestChunkerChunk50bSHA1HashS3:`, `TestChunkerOverCrypt:`, `TestChunkerChunk50bMD5QuickS3:`, `TestChunkerChunk50bSHA1QuickS3:`, `TestCombine:dir1`, and `TestCompress:`;
- most of the `TestCompressSwift:` block, ending after complete `test_rmdirs` variations and before the `args` for `test_volatile LocalRemote`.

Line-oriented counts in the exact range show 897 `args` lines and 897 `name` lines because the first included line is an `args` field for an object whose `name` is just before the range, while the final included object has a `name` and fixed metadata but its `args` line is just after the range.

## Control Flow

There is no runtime control flow in the JSON testdata itself. The relevant control flow is in `bisync_debug_test.go`:

1. `parseConfig` reads `../../fstest/test_all/config.yaml` into `Config`.
2. `generateDebuggers` builds `testList` by scanning bisync testdata directories whose names begin with `test_` and are non-empty.
3. It iterates every configured backend, defaulting an empty backend remote to `local`.
4. For each backend/testcase pair, it iterates `LocalRemote`, `RemoteLocal`, and `RemoteRemote`.
5. It skips local-only duplicate variations when the backend remote is `local`.
6. It emits a fixed VS Code Go test launch object using `debugFormat`.
7. It writes the assembled document to `./testdata/bisync_vscode_debuggers_launch.json` with `bilib.PermSecure`.

This chunk is therefore a materialized product of backend order, discovered bisync test-case order, and the fixed three-variation loop.

## State And Persistence Behavior

The JSON file persists generated developer tooling state in the source tree under `cmd/bisync/testdata`. It is not read by bisync production code during synchronization.

Every launch entry includes `-no-cleanup`, which intentionally preserves test artifacts after a debug run. That is useful for inspecting path1/path2 listings, backup directories, lock files, and failure residue, but it means repeated manual debugging can leave remote-side or local-side state behind. Debuggers copied from this file should normally run against test remotes, not user data.

The generator overwrites the whole launch file when invoked. Manual edits to this generated testdata are not durable unless the generator or its config inputs are also changed.

## Dependencies And Integration Points

- VS Code's Go debug adapter consumes the object shape: `type: go`, `request: launch`, `mode: test`, and `program: ./cmd/bisync`.
- `cmd/bisync` test code consumes the command-line arguments, especially `-remote`, `-remote2`, `-case`, and `-no-cleanup`.
- `bisync_debug_test.go` depends on `gopkg.in/yaml.v3` for the backend config, `github.com/rclone/rclone/fs` for error logging, `github.com/stretchr/testify/assert` for write assertions, and `github.com/rclone/rclone/cmd/bisync/bilib.PermSecure` for output permissions.
- Backend remote names such as `TestChunkerS3:`, `TestCombine:dir1`, and `TestCompressSwift:` come from `fstest/test_all/config.yaml` and the user's rclone test configuration.
- The `-case` values integrate with bisync's test harness, selecting one testdata scenario at a time rather than running the full package test suite.

## Risks And Edge Cases

- The full file is not strict JSON as checked in: a direct `jq` parse fails because the generator leaves a trailing comma before the closing `configurations` array. VS Code may tolerate JSON-with-comments style syntax in `launch.json`, but strict JSON tooling will reject it unless the trailing comma is removed.
- The file is very large. The generator comment warns that VS Code can crash if all entries are copied into a real launch configuration. Developers should copy only the needed debugger object.
- The assigned chunk boundaries are not object-aligned. Any merge lane or research consumer must treat this file as a chunked generated artifact and not assume each chunk is independently parseable.
- Remote-to-remote entries use the same backend name for both sides. For backends without strong isolation, a copied debugger may need extra test-path scoping from the harness to avoid source/destination collisions.
- `-no-cleanup` is intentional for debugging but can accumulate state and affect later manual reruns if the harness or remote cleanup is not performed separately.
- Backend capability differences matter. This chunk concentrates on wrapper and object-storage remotes such as chunker, combine, compress, S3, Swift, and crypt-over-chunker paths; failures in modtime, checksums, empty directories, normalization, filters, or backup-dir behavior may be backend-specific rather than generic bisync defects.
- Because the file is generated from config and filesystem discovery, changes in backend order or testdata directory presence can cause large diffs with no semantic change to bisync itself.

## Test Signals

- Regenerating via the bisync debug generator should reproduce this matrix shape: fixed Go test launch entries with the same argument order and naming convention.
- A lightweight static check can confirm every complete object has `type = go`, `request = launch`, `mode = test`, `program = ./cmd/bisync`, and exactly the expected `args` flag sequence.
- Strict JSON parsing currently fails on the raw file; a permissive VS Code-oriented parse or a normalization step that removes the final trailing comma should be used when validating generated content with `jq`.
- Representative copied launch entries from this chunk should start a focused bisync test for backends such as `TestChunkerS3:`, `TestCombine:dir1`, and `TestCompressSwift:` with one of the three side-placement variations.
- Behavioral coverage comes from the selected `-case` scenarios: deletion limits, dry-run behavior, filters and filter-file checks, checksum-listing behavior, modtime-less backends, filename normalization, rclone argument forwarding, resync modes, directory removal, and volatile file handling.
- For generated-file regression tests, compare the set of emitted test cases and the three variation names rather than relying only on line numbers, because backend config changes can legitimately move this chunk's content.
