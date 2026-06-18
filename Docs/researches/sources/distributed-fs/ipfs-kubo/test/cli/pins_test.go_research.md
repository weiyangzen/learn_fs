# sources/distributed-fs/ipfs-kubo/test/cli/pins_test.go

Purpose: broad CLI coverage for local pin operations, including pin add/rm/update/verify/list, daemon and offline modes, progress output, DAG corruption error reporting, CID base handling, pin names, name filters, overwrite behavior, and JSON wire output.

Important APIs and types: `testPinsArgs` parameterizes daemon use, pin arguments, `pin ls` arguments, and CID base arguments. Helpers `testPins`, `testPinsErrorReporting`, `testPinDAG`, and `testPinProgress` run reusable suites. `StrCat` from testutils composes optional argument slices. `pinLs` local helper splits text output into lines.

Control flow: `TestPins` runs the core helpers without a daemon and with an offline daemon across combinations such as `--progress`, `--stream`, and `--cid-base=base32`. The core test adds seven blocks unpinned, pins them through stdin, verifies output, runs `pin verify`, checks verbose verify, lists pins, removes them, and tests `pin update --unpin=true`, including idempotent update. Error helpers use missing random CIDs and deliberately removed DAG blocks to require `ipld: could not find`. Additional subtests validate text output with `--names`, name substring filtering through `--name` and `-n`, overwriting a pin name on the same CID, and JSON output where `Name` appears only under `--names`.

State and persistence: pin state is local to each node and is mutated sequentially within each helper. `pin update` should transfer recursive pin state and optional name metadata. DAG corruption is produced by removing a referenced block after unpinning.

Dependencies and integration points: exercises pinner, blockstore, DAG traversal, CLI stdin handling, CID encoding, JSON output, progress reporting, and offline daemon RPC behavior.

Risks and test signals: exact progress text such as `5 nodes (1.0 MB)` is format-sensitive. The tests intentionally run many parallel nodes, so repo isolation is critical. Regressions show as wrong pin command output, verify omissions, missing error details, failed name transfer, or JSON/text mismatch.
