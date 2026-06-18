# sources/user-network-fs/rclone/cmd/bisync/testdata/bisync_vscode_debuggers_launch.json lines 52674-59190

## Scope

This chunk covers the final 6,516 lines of the generated VS Code debugger launch matrix for rclone `cmd/bisync` integration tests. The requested range starts at line 52674 inside the `args` field of an already-open `TestSeafileV6: test_rmdirs RemoteLocal` configuration, then continues through complete launch configurations and the closing `configurations` array at EOF. The file has 59,189 lines, so the requested line 59190 is effectively the end of file.

Within this range there are 814 launch entries or entry fragments:

- the tail of `TestSeafileV6:`: the `test_rmdirs RemoteLocal` args line plus complete `test_rmdirs RemoteRemote` and all three `test_volatile` topologies;
- full 27-test-case by 3-topology matrices for `TestSeafile:`, `TestSeafileEncrypted:`, `TestSia:`, `TestSMB:rclone`, `TestStorj:`, `TestZoho:`, `TestHdfs:`, `TestOracleObjectStorage:`, `TestQuatrix:`, and `TestUlozto:`.

The repeated test cases in the full backend groups are `test_all_changed`, `test_backupdir`, `test_basic`, `test_changes`, `test_check_access`, `test_check_access_filters`, `test_check_filename`, `test_check_sync`, `test_compare_all`, `test_createemptysrcdirs`, `test_dry_run`, `test_equal`, `test_ext_paths`, `test_extended_filenames`, `test_filters`, `test_filtersfile_checks`, `test_ignorelistingchecksum`, `test_max_delete_path1`, `test_max_delete_path2_force`, `test_nomodtime`, `test_normalization`, `test_rclone_args`, `test_resolve`, `test_resync`, `test_resync_modes`, `test_rmdirs`, and `test_volatile`.

## Purpose

`bisync_vscode_debuggers_launch.json` is a generated helper file for developers debugging individual bisync integration-test permutations in VS Code. It is not production code and does not implement bisync behavior. Each object is a Go debug configuration that launches tests in `./cmd/bisync` with a specific backend remote, a specific bisync fixture case, and one of three path topologies.

The generator is `generateDebuggers` in `cmd/bisync/bisync_debug_test.go`. It reads backend definitions from `../../fstest/test_all/config.yaml`, discovers fixture directories beginning with `test_`, and emits this file under `cmd/bisync/testdata`. The generator comment says developers should copy only needed entries into a real VS Code `launch.json`, because VS Code can crash if it loads too many configurations.

## Important Data Shape

Each complete launch configuration in this chunk has the same schema:

- `name`: human-readable label, for example `Test TestSeafile: test_basic LocalRemote`.
- `type`: always `go`, selecting the VS Code Go debugger integration.
- `request`: always `launch`.
- `mode`: always `test`, so the Go extension runs the target package as a test binary.
- `program`: always `./cmd/bisync`, the package containing the bisync tests.
- `args`: always `["-remote", <path1>, "-remote2", <path2>, "-case", <testcase>, "-no-cleanup"]`.

The topology encoded in `args` is:

- `LocalRemote`: `-remote local`, `-remote2 <backend>`.
- `RemoteLocal`: `-remote <backend>`, `-remote2 local`.
- `RemoteRemote`: both paths use the same backend remote.

The backend strings are rclone test remote names, not local filesystem paths. Most end with `:`, while SMB uses `TestSMB:rclone`, which includes a subpath after the remote name.

## Control Flow

The JSON file has no executable control flow. Runtime behavior comes from the VS Code Go extension and the Go test binary:

1. A developer chooses one copied configuration in VS Code.
2. VS Code launches the Go debugger in test mode for `./cmd/bisync`.
3. The test binary receives `-remote`, `-remote2`, `-case`, and `-no-cleanup`.
4. `bisync_test.go` binds those flags to test globals such as `argRemote2`, `argTestCase`, and `argNoCleanup`.
5. The bisync test harness runs only the selected fixture case against the selected path topology and leaves work files behind for debugging because `-no-cleanup` is set.

The generation flow is deterministic for a given backend config and fixture directory listing, but this chunk itself is static data.

## State And Persistence Behavior

The launch file persists developer/debug metadata in the repository under `cmd/bisync/testdata`. Running a configuration does not modify this JSON. The launched bisync test can create remote objects, local working directories, logs, listings, and retained test artifacts because every entry includes `-no-cleanup`.

State sensitivity is mostly in the external test remotes. Entries for Seafile, Sia, SMB, Storj, Zoho, HDFS, Oracle Object Storage, Quatrix, Ulozto, and related services assume the corresponding rclone test remotes are configured and reachable. `RemoteRemote` entries can exercise same-remote synchronization behavior and may require isolation in the test harness to avoid collisions.

## Dependencies And Integration Points

Primary local integration points:

- `cmd/bisync/bisync_debug_test.go`: defines the `Config`, `Backend`, and `Test` structs for parsing `fstest/test_all/config.yaml`, plus the `debugFormat` and `docFormat` templates that generate this JSON.
- `cmd/bisync/bisync_test.go`: defines the command-line flags consumed by the generated `args`, including `-case`, `-remote2`, and `-no-cleanup`.
- `cmd/bisync/testdata/test_*`: fixture directories discovered by the generator and represented by the `-case` values.
- `fstest/test_all/config.yaml`: source of backend remote names and ordering.
- backend-specific tests and test-server assets, for example SMB, HDFS, Oracle Object Storage, Quatrix, and Ulozto test remote definitions.

External integration points are VS Code, the VS Code Go extension/debug adapter, Go test execution, and the configured rclone remotes named by the entries.

## Risks And Maintenance Notes

- The requested range starts mid-object, so this chunk alone is not standalone JSON. It must be interpreted as part of the full `bisync_vscode_debuggers_launch.json`.
- The file is very large. The generator explicitly warns that VS Code can crash if too many generated configurations are copied into a real launch file.
- The JSON is generated but checked in as testdata. Any change to backend config, fixture case names, generator ordering, or launch schema can produce broad churn.
- Every entry uses `-no-cleanup`. That is useful for debugging but can leave local and remote test artifacts, consume storage, or affect later manual runs if developers reuse the same remotes carelessly.
- Remote names depend on local rclone test configuration and service availability. Many entries will fail outside an environment with credentials or test servers for the named backend.
- `RemoteRemote` uses the same remote name for both paths; correctness depends on bisync's test harness deriving isolated subpaths.
- Because launch names and args are repeated mechanically, a single generator bug can silently affect hundreds of configurations.

## Test Signals

Useful checks for this chunk are mostly structural and integration-oriented:

- parse the full JSON file successfully, not just this chunk;
- verify all complete entries use `type: go`, `request: launch`, `mode: test`, and `program: ./cmd/bisync`;
- verify every `args` array contains `-remote`, `-remote2`, `-case`, and `-no-cleanup` in the generator's expected order;
- compare generated output from `generateDebuggers` against this testdata after backend or fixture changes;
- run representative configurations for each topology, especially `LocalRemote`, `RemoteLocal`, and `RemoteRemote`;
- run representative backend configurations for the full groups in this chunk, including service-backed remotes such as SMB, HDFS, Oracle Object Storage, Quatrix, and Ulozto;
- confirm `bisync_test.go` still recognizes the flags emitted here.

This chunk has no direct unit tests of its own behavior beyond parse/golden-file checks and successful execution of selected generated launch entries.
