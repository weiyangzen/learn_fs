# sources/distributed-fs/ipfs-kubo/test/cli/harness/ipfs.go

Purpose: convenience methods on `Node` for common `ipfs` CLI operations and config mutation.

Important APIs/functions: `IPFSCommands`, `SetIPFSConfig`, `GetIPFSConfig`, `IPFSAddStr`, `IPFSAddDeterministic`, `IPFSAddDeterministicBytes`, `IPFSAdd`, `IPFSBlockPut`, `IPFSDAGPut`, `IPFSDagImport`, and `IPFSDagExport`.

Control flow: helpers assemble CLI args, pipe readers to stdin when needed, run commands through `Runner.MustRun`, trim CIDs from stdout, and validate config writes by reading back JSON into a value of the same type. DAG import verifies success by checking `block stat --offline` for the expected root CID.

State and persistence: operations mutate the node repo by writing config, adding blocks, importing CARs, and exporting CAR files. Deterministic random readers make CIDs reproducible across tests.

Dependencies/integration: uses Kubo testutils for random data and line splitting, JSON reflection for config verification, and the process runner for CLI execution.

Risks: reflection-based config comparison can be sensitive to JSON number types and nil representation. `IPFSDagImport` uses `MustRun`, so command errors panic before returned errors are useful. Test signals are returned CIDs, successful config round trips, and block availability checks.
