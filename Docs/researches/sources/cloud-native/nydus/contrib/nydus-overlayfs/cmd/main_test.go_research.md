# sources/cloud-native/nydus/contrib/nydus-overlayfs/cmd/main_test.go

## Purpose
This Go test file validates argument parsing, mount option conversion, and mount invocation behavior for the overlayfs helper.

## Important APIs, Types, and Functions
It defines `fakeArgs` implementing `cli.Args`, then tests `parseArgs`, `parseOptions`, and `run`. It temporarily replaces package-level `mountFn`.

## Control Flow
`TestParseArgs` table-tests normal filtering and validation failures. `TestParseOptions` asserts flag bitmasks and data passthrough. `TestRun` checks parse errors avoid mount calls, valid inputs call the injected mount function with expected source/target/fstype/flags/data, and mount errors are wrapped.

## State, Persistence, and Dependencies
Tests mutate global `mountFn` but restore it with defer. They do not perform real mounts. Dependencies include `testing`, `reflect`, `strings`, `urfave/cli`, and `unix`.

## Integration Points
The tests lock the helper’s CLI-to-syscall contract and make future refactors safer by verifying the injectable mount seam.

## Risks and Test Signals
The tests are good unit signals but do not exercise real CLI `Before` behavior, short argument panic cases, privileged mount semantics, or every flags table option. They encode the current controversial mapping of options such as `nosuid`, but do not validate whether mappings are semantically correct for Linux overlay mounts.
