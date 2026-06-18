# sources/control-plane/mayastor/test/grpc/test_common.js

## Purpose
`test_common.js` provides shared utilities and constants for Mayastor/io-engine gRPC integration tests. It starts and stops privileged Rust binaries, manages temporary config and socket paths, discovers the host IP, waits for services to respond, creates gRPC clients from the Mayastor protobuf schema, runs JSON-RPC commands, adjusts device/socket permissions, and exports protocol constants used by other tests.

## Important APIs, Types, and Functions
Important exported constants include `CSI_ENDPOINT`, `CSI_ID`, `SOCK`, `grpcEndpoint`, `NVME`, `NVME_NQN_PREFIX`, `NVME_MODEL_ID`, and `NVMF_URI`. Process helpers are `getCmdPath`, `runAsRoot`, `execAsRoot`, `startMayastor`, `stopAll`, `restartMayastor`, and internal `startProcess`/`killSudoedProcess`. RPC helpers are `waitFor`, `jsonrpcCommand`, `createGrpcClient`, `callGrpcMethod`, and `createBdevs`. Permission helpers are `ensureNbdWritable`, `restoreNbdPerms`, and `fixSocketPerms`.

## Control Flow, State, and Persistence
The module computes `grpcEndpoint` from `TEST_PORT` or port `10124` and the first non-loopback IPv4 address returned by `getMyIp()`. A module-level `procs` map tracks started child processes by command name plus optional suffix. `startMayastor` optionally writes a temporary config file under `/tmp/mayastor_test.cfg`, starts `target/debug/io-engine` with default reactor and gRPC args, and deletes the config file when the process closes. `stopAll` stops tracked processes in sorted order using SIGTERM through `killSudoedProcess`, then clears the map. `restartMayastor` kills the tracked io-engine process, starts a default replacement, and waits for a caller-provided ping to succeed. Permission helpers mutate `/dev/nbd*` and the CSI Unix socket permissions during tests, then attempt to restore them.

## Dependencies and Integration Points
This file is the central integration point between Node tests, privileged system operations, Rust debug binaries, the Mayastor protobuf schema, JSON-RPC tooling, Unix sockets, NBD devices, and environment variables such as `TEST_PORT`, `NVME`, `MY_POD_IP`, and `MAYASTOR_DELAY`. It depends on `sudo.js` for non-root privilege elevation, `grpc-kit` for client generation, `async` for sequencing and retries, `find-process` for process lookup, and lodash for object/env manipulation.

## Risks
Importing the module asserts that a non-loopback IPv4 address exists, which can fail in constrained CI containers even for tests that only need constants. Process identity handling is fragile: `startProcess` indexes by command string, but `restartMayastor` looks for `procs.io_engine` while `startMayastor` registers the command `io-engine`; unless some caller uses a matching suffix or naming convention elsewhere, this can be a latent bug. Killing sudoed processes depends on matching `pid` versus `ppid` from `find-process`, and same-name process collisions can affect unrelated processes. Shell construction in `jsonrpcCommand` embeds JSON in single quotes and can break if arguments contain single quotes. Permission helpers widen access to `/dev/nbd*` and sockets and must be paired with cleanup to avoid host-side residue.

## Test Signals
Signals are integration tests that start io-engine, wait for the gRPC endpoint, create and share bdevs through `BdevRpc`, execute JSON-RPC commands, restart io-engine, and always call `stopAll` and permission restoration in teardown. Unit-level coverage should target `getCmdPath`, `waitFor` retry behavior, `jsonrpcCommand` argument quoting, process-map key consistency, and root versus non-root `runAsRoot` behavior.
