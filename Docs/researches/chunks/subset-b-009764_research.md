# sources/user-network-fs/rclone/cmd/bisync/testdata/bisync_vscode_debuggers_launch.json lines 37239-44846

## Scope

This chunk covers part of rclone's generated VS Code debug launch matrix for `cmd/bisync` tests. The file is a `launch.json`-shaped document with `"version": "0.2.0"` and a large `"configurations"` array. The requested range starts inside the `Test TestBox: test_changes RemoteLocal` object at its `"request": "launch"` field and ends inside the next `Test TestCache: test_resync RemoteLocal` object after its `"name"` field, so the chunk boundaries are not standalone JSON. Within the range, the repeated object schema is stable and contains 951 complete `"args"` arrays.

The range covers backend sections beginning near `TestBox:` and continuing through most of `TestCache:`. Complete or partial backend coverage in this chunk includes `TestBox:`, `TestFichier:`, `TestQingStor:`, `TestAzureBlob:`, `TestAzureBlob,directory_markers:`, `TestAzureFiles:`, `TestPcloud:`, `TestPikPak:`, `TestWebdavNextcloud:`, `TestWebdavOwncloud:`, `TestWebdavRclone:`, and `TestCache:`, plus the `local` side used in local/remote pairings.

## Purpose

`bisync_vscode_debuggers_launch.json` is developer tooling for debugging individual bisync integration-test cases from VS Code. Each configuration launches the Go test debugger against `./cmd/bisync` in test mode and passes the same flags that the bisync test harness accepts on the command line.

This chunk's main purpose is coverage enumeration, not runtime implementation. It materializes many combinations of:

- backend remote under test;
- path topology: `LocalRemote`, `RemoteLocal`, or `RemoteRemote`;
- individual bisync test case selected by `-case`;
- `-no-cleanup`, so a debug session leaves temporary remotes, logs, and work directories behind for inspection.

## Important APIs And Data Shapes

Each launch configuration in this chunk follows the same data shape:

```json
{
  "name": "Test <remote> <test_case> <variation>",
  "type": "go",
  "request": "launch",
  "mode": "test",
  "program": "./cmd/bisync",
  "args": ["-remote", "<path1>", "-remote2", "<path2>", "-case", "<test_case>", "-no-cleanup"]
}
```

Important fields:

- `"type": "go"`, `"request": "launch"`, and `"mode": "test"` target the VS Code Go debugger's test-launch path rather than a normal binary launch.
- `"program": "./cmd/bisync"` points the debugger at the rclone bisync package.
- `-remote` maps to the test harness's first path argument.
- `-remote2` maps to the second path argument.
- `-case` selects one scenario directory under `cmd/bisync/testdata`.
- `-no-cleanup` maps to the harness cleanup flag and intentionally preserves test artifacts after the run.

The test cases visible in the range are `test_all_changed`, `test_backupdir`, `test_basic`, `test_changes`, `test_check_access`, `test_check_access_filters`, `test_check_filename`, `test_check_sync`, `test_compare_all`, `test_createemptysrcdirs`, `test_dry_run`, `test_equal`, `test_ext_paths`, `test_extended_filenames`, `test_filters`, `test_filtersfile_checks`, `test_ignorelistingchecksum`, `test_max_delete_path1`, `test_max_delete_path2_force`, `test_nomodtime`, `test_normalization`, `test_rclone_args`, `test_resolve`, `test_resync`, `test_resync_modes`, `test_rmdirs`, and `test_volatile`.

## Control Flow

The JSON file itself has no executable control flow. Control flow is introduced when VS Code uses one entry:

1. VS Code's Go debug adapter reads the selected configuration.
2. It starts a Go test debug session for `./cmd/bisync`.
3. The bisync test package parses flags such as `-remote`, `-remote2`, `-case`, and `-no-cleanup`.
4. The harness dispatches one of the topology tests: `TestBisyncLocalRemote`, `TestBisyncRemoteLocal`, or `TestBisyncRemoteRemote`, corresponding to the selected path ordering.
5. `testBisync` creates per-run temporary remotes and work directories, copies initial fixture data, runs the requested scenario, and compares generated listings/logs to golden data unless the invoked flags change that behavior.

The generation path lives in `bisync_debug_test.go`: `generateDebuggers` reads `../../fstest/test_all/config.yaml`, enumerates bisync `testdata/test_*` directories, iterates backend remotes and the three variations, formats each object with `debugFormat`, wraps the result in `docFormat`, and writes `./testdata/bisync_vscode_debuggers_launch.json`.

## State And Persistence Behavior

This chunk is persisted repository data: a generated `launch.json` fixture stored under `cmd/bisync/testdata`. It is not consumed by production bisync code, but it is part of the developer/test surface.

Runtime state is created by the selected debug target. The bisync test harness allocates a random temp directory, creates test remotes for path1 and path2, builds a workdir, writes a test log, and may create listing and queue artifacts. Because every entry in this chunk passes `-no-cleanup`, `cleanupAll` returns early and leaves those artifacts in place. That is useful for debugging but can accumulate remote test directories, local temp data, and backend-side objects if developers run many configurations.

The generated launch file itself is overwritten by the generator with secure file permissions from `bilib.PermSecure`. It does not maintain incremental state; regeneration replaces the full file.

## Dependencies And Integration Points

Primary integration points are:

- VS Code plus the Go debug adapter, which interpret `"type": "go"` and `"mode": "test"`.
- `cmd/bisync/bisync_test.go`, which defines the command-line flags referenced in `"args"` and implements `TestBisyncLocalRemote`, `TestBisyncRemoteLocal`, `TestBisyncRemoteRemote`, and `testBisync`.
- `cmd/bisync/bisync_debug_test.go`, which generates this file from backend config and available test case directories.
- `fstest/test_all/config.yaml`, which supplies backend remote names such as `TestBox:`, `TestAzureFiles:`, and `TestCache:`.
- The backend registry import in the bisync tests, which makes configured remotes available during integration testing.
- Scenario directories under `cmd/bisync/testdata/test_*`, whose `initial`, `modfiles`, and `golden` contents define the behavior exercised by each `-case`.

The remotes in this chunk cover several backend families, including Box, Fichier, QingStor, Azure Blob, Azure Files, pCloud, PikPak, WebDAV variants, and cache. The `TestAzureBlob,directory_markers:` remote name is significant because the comma is part of the configured remote identifier used by the generated debugger entry.

## Risks And Maintenance Notes

- The file is extremely large. The generator comment warns developers to copy only needed entries into a real VS Code `launch.json`, because VS Code can crash when too many configurations are loaded.
- Chunk boundaries can split JSON objects, as this range does. Research and tooling that process slices should not assume each chunk is independently valid JSON.
- The launch matrix depends on remote names from `fstest/test_all/config.yaml` and test directories under `cmd/bisync/testdata`; stale generated output can silently miss new cases or retain removed remotes.
- `-no-cleanup` is intentional for debugging but risky for repeated runs, especially with paid or quota-limited cloud backends.
- Remote names with punctuation, especially `TestAzureBlob,directory_markers:`, must remain quoted correctly in JSON and passed as a single argument.
- The same remote is used for both sides in `RemoteRemote` entries. The harness creates distinct directories beneath that remote, but a bug in temp path creation or cleanup could make these tests destructive.
- Backend-specific behavior can make debug sessions slow, flaky, or environment-dependent because these entries target real integration-test remotes, not mocked storage.

## Test Signals

Useful validation signals for this chunk include:

- JSON parsing of the full `bisync_vscode_debuggers_launch.json` succeeds after regeneration.
- Representative entries from each backend in this range launch `./cmd/bisync` with the expected `-remote`, `-remote2`, `-case`, and `-no-cleanup` arguments.
- `go test ./cmd/bisync -remote <remote> -remote2 <remote-or-local> -case <case> -no-cleanup` reaches the same harness path as the corresponding VS Code configuration.
- Generator tests or golden checks confirm the output still includes the three topology variations for non-local remotes and only appropriate entries for local-only cases elsewhere in the file.
- The selected cases continue to map to real `testdata/test_*` directories with non-empty fixtures.
- Running a small representative set, such as `test_basic`, `test_resync`, and `test_filters` against one remote from this chunk, verifies the debug entries still match the current bisync flag surface and test harness.
