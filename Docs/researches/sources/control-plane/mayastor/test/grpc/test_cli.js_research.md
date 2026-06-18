# sources/control-plane/mayastor/test/grpc/test_cli.js

## Purpose
`test_cli.js` is a Mocha test suite for the Rust `io-engine-client` CLI. It isolates the CLI from a real Mayastor server by running a `grpc-mock` service with exact request/response rules, then shells out to the debug CLI binary and verifies stdout, stderr, and exit status for pool, nexus, controller, and replica commands.

## Important APIs, Types, and Functions
The local `runMockServer(rules)` function creates a mock Mayastor gRPC server from `mayastor.proto`, package `mayastor`, service `Mayastor`, and listens on `127.0.0.1:50051`. Constants define fixed test inputs: `POOL`, `DISK`, `UUID`, `UUID1`, `UUID2`, `CLIENT_CMD`, and `EGRESS_CMD`. The suite uses `child_process.exec` to run commands such as `pool create`, `pool list`, `nexus create`, `nexus publish`, `nexus children`, `controller list`, `replica create`, `replica list`, `replica stats`, and failure cases. Assertions come from `chai.assert`.

## Control Flow, State, and Persistence
At module load, `process.env.API_VERSION` is forced to `v0`. The success suite starts one mock server in `before()` with successful rules for create, list, publish, unpublish, add, remove, destroy, and stat calls. Each test builds a CLI command, executes it, parses output when needed, and asserts formatting and field mapping. The success suite closes the server in `after()`. The failure suite starts a separate mock server with gRPC errors such as ALREADY_EXISTS, NOT_FOUND, and UNKNOWN, then verifies the CLI exits with an error, writes the server message to stderr, and leaves stdout empty. Persistent effects are minimal: the test binds a local TCP port and launches subprocesses, but it does not create real pools or replicas.

## Dependencies and Integration Points
The suite integrates Node/Mocha with the Rust `io-engine-client` binary built at `../../target/debug/io-engine-client`, the protobuf schema at `../../utils/dependencies/apis/io-engine/protobuf/mayastor.proto`, and the CLI's `--bind 127.0.0.1:50051` endpoint option. It imports `NVME_NQN_PREFIX` from `test_common.js` so controller output expectations match the shared Mayastor NQN convention.

## Risks
`grpc-mock` rules require exact input object matches; any CLI request shape drift can hang rather than fail quickly. The fixed port `50051` can collide with local services or parallel test runs. Parsing CLI tables by whitespace makes these tests sensitive to formatting changes and unable to handle values containing spaces. `exec` uses shell command strings, which is acceptable for fixed constants here but would be risky with untrusted input. Because the test only mocks the gRPC API, it verifies CLI marshalling and rendering but not real server behavior, timing, or storage side effects.

## Test Signals
Strong signals are the success cases for pools, nexus, NVMe controllers, nexus children, replicas, and replica stats, plus failure cases for common gRPC errors. Additional useful signals would be command timeout protection for unmatched mock rules, a dynamically allocated port for parallel CI, and coverage for API versions beyond the forced `v0` value if supported by the CLI.
