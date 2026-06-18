# Research: subset-b-000420

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/package-lock.json -->
# sources/control-plane/mayastor/test/grpc/package-lock.json

## Purpose
`package-lock.json` is the npm v3 lockfile for the `mayastor-test` Node.js gRPC test package. It records deterministic registry tarball URLs, integrity hashes, resolved versions, dependency edges, executable bins, install scripts, optional packages, engine constraints, deprecation metadata, and the root package metadata needed to reproduce the test harness install.

## Important APIs, Types, and Functions
This file is data rather than executable code. The root `packages[""]` entry mirrors the direct dependency contract from `package.json`: gRPC clients and mocks (`@grpc/grpc-js`, `@grpc/proto-loader`, `grpc`, `grpc-kit`, `grpc-mock`, `grpc-promise`), test tools (`mocha`, `chai`, `semistandard`, `wtfnode`), process and privilege helpers (`find-process`, `pidof`, `inpath`, `read`), utility libraries (`async`, `lodash`, `glob`, `sleep-promise`, `systeminformation`), and archive support (`tar`). The lock resolves notable direct versions including `@grpc/grpc-js` 1.12.5, `@grpc/proto-loader` 0.7.13, `grpc` 1.24.11, `grpc-mock` 0.7.0, `mocha` 10.8.2, `semistandard` 17.0.0, `lodash` 4.18.1, `tar` 7.5.13, and `systeminformation` 5.31.5.

## Control Flow, State, and Persistence
There is no runtime control flow. The persisted state is the full dependency graph under `packages`, with 477 package entries and `lockfileVersion: 3`. npm consumes this graph during `npm ci` or lockfile-respecting installs. Integrity fields protect downloaded artifacts, engine fields constrain compatible Node.js runtimes, and bin/install-script metadata controls which package executables and lifecycle steps are made available during install.

## Dependencies and Integration Points
The lockfile integrates the Node test directory with npm, CI, linting, and the JavaScript gRPC tests in this folder. It must remain synchronized with `package.json`, especially because the manifest declares overrides for `serialize-javascript` and `tar`. The lock currently resolves `serialize-javascript` to 7.0.5 and `tar` to 7.5.13 at the direct dependency level, while the legacy native `grpc` package still brings its own older transitive stack.

## Risks
Key risk is dependency age and runtime portability. `grpc` 1.24.11 is deprecated in favor of `@grpc/grpc-js` and has an install script/native component path. Several transitive packages are marked deprecated, including ESLint 8.57.1 support metadata, `@humanwhocodes/*`, `are-we-there-yet`, `gauge`, older nested `glob` versions, `inflight`, `npmlog`, and `rimraf` 3.0.2. Node version compatibility is also mixed: `serialize-javascript` 7.0.5 requires Node >=20, and `tar` 7.x transitive packages such as `@isaacs/fs-minipass`, `chownr`, and `yallist` require Node >=18. This can break older CI images even if most of the test harness itself is CommonJS.

## Test Signals
Useful signals are `npm ci` in `sources/control-plane/mayastor/test/grpc`, `npm run check`, and the Mocha gRPC tests that exercise `test_cli.js` and other files in the directory. Security and supply-chain signals should include `npm audit` or the repository's normal scanner, plus explicit checks that the `serialize-javascript` and `tar` overrides remain effective after lockfile refreshes.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/package-lock.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/package.json -->
# sources/control-plane/mayastor/test/grpc/package.json

## Purpose
`package.json` defines the Node.js package used by Mayastor/io-engine gRPC tests. It gives the package name `mayastor-test`, version `0.1.0`, BSD-2-Clause license, lint scripts, runtime/test dependencies, dependency overrides, and semistandard environment settings for Mocha and Node globals.

## Important APIs, Types, and Functions
The executable surface is script based. `npm run check` runs `semistandard --verbose`; `npm run fix` runs `semistandard --fix`. The dependency set supports two styles of gRPC testing: real or mocked protobuf RPC interaction through `grpc-kit`, `grpc-mock`, `grpc-promise`, `@grpc/grpc-js`, `@grpc/proto-loader`, and the deprecated native `grpc`; and process-oriented integration helpers through `find-process`, `pidof`, `inpath`, `read`, `systeminformation`, and `wtfnode`. `chai`, `mocha`, `async`, `lodash`, `glob`, and `sleep-promise` provide the local assertion and async test utility layer.

## Control Flow, State, and Persistence
The manifest has no application control flow. It controls npm install resolution, available npm scripts, and lint behavior. Dependency state is persisted in `package-lock.json`; the manifest supplies ranges while the lock pins concrete versions. The `semistandard.env` setting allows test files to use Mocha and Node globals without lint failures.

## Dependencies and Integration Points
This package is tightly coupled to the JavaScript files in `sources/control-plane/mayastor/test/grpc`, the Rust debug binaries under `sources/control-plane/mayastor/target/debug`, and the protobuf definition under `utils/dependencies/apis/io-engine/protobuf/mayastor.proto`. The `overrides` block forces `serialize-javascript >=7.0.5` and `tar ^7.5.11`, which is likely intended to keep transitive security fixes in place while preserving the existing test dependency stack.

## Risks
The manifest mixes old and new gRPC stacks. Keeping both `grpc` and `@grpc/grpc-js` increases install risk because `grpc` is deprecated and native-install sensitive, while the tests mostly depend on command-line behavior rather than a pure JS API boundary. The overrides can raise the effective Node.js floor: the locked `serialize-javascript` requires Node >=20 and `tar` 7.x requires Node >=18. No `test` script is declared, so CI must invoke Mocha explicitly elsewhere; otherwise this package can pass lint without running behavioral tests.

## Test Signals
Signals are `npm ci`, `npm run check`, `npm run fix` for style repair, and explicit Mocha invocation for `test_cli.js` and integration tests that import `test_common.js`. After dependency edits, verify that `package-lock.json` changes intentionally and that the mocked CLI tests still launch `io-engine-client` against `grpc-mock`.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/package.json -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/sudo.js -->
# sources/control-plane/mayastor/test/grpc/sudo.js

## Purpose
`sudo.js` is a small helper for running privileged commands from the Node test harness when the current test process is not already root. It wraps `sudo -S -E`, prompts for a password through stdin, optionally caches the password in memory, and emits a custom `started` event once the target process is detected.

## Important APIs, Types, and Functions
The exported API is `sudo(command, options, nameInPs)`. `command` is an array whose first item is the binary and remaining items are arguments. `options.spawnOptions` is passed to `child_process.spawn`, with `stdio` forced to `pipe`; `options.prompt` customizes the password prompt; `options.cachePassword` enables module-level password reuse through `cachedPassword`. The helper uses `inpath.sync` to locate `sudo`, `read` to collect a silent password, and `pidof` to poll for the process name that should appear in the process table.

## Control Flow, State, and Persistence
On each call, the helper builds sudo args `-S -E -p #node-sudo-passwd#`, spawns sudo, starts a `pidof(nameInPs)` polling loop, and returns the child process immediately. If the target process appears or the child exits, it emits `started`. stderr is parsed line by line for the exact prompt token. The first prompt sends the cached password when available; a second prompt clears the cache because it indicates the previous password failed. State is process-local only: `cachedPassword` lives in memory and is not written to disk.

## Dependencies and Integration Points
`test_common.js` calls this helper from `runAsRoot` when `process.geteuid() !== 0`. That makes it part of the privileged path for starting io-engine, chmodding sockets or `/dev/nbd*`, killing processes, and other system-level setup in gRPC tests. The `nameInPs` parameter exists because `sudo` itself is not the process whose readiness matters; tests want to wait for binaries such as `io-engine`.

## Risks
Readiness detection is explicitly unreliable for multiple instances with the same process name. The function mutates the caller-provided `spawnOptions` object by forcing `stdio = 'pipe'`. If `sudo` is not found, `spawn` receives a bad executable path and failure behavior depends on the platform. Errors thrown inside async callbacks can crash the test process instead of reaching Mocha callbacks. The password cache reduces repeated prompting but keeps a sensitive secret in memory for the life of the module. Prompt parsing requires the sudo prompt token to arrive as its own trimmed line.

## Test Signals
Unit signals should cover password prompt handling, cache invalidation on repeated prompts, `started` emission on process detection and on early child exit, and spawn option propagation. Integration signals are non-root test runs that start and stop io-engine through `test_common.runAsRoot`, plus root test runs that bypass this helper entirely.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/sudo.js -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/test_cli.js -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/test_cli.js -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/test_common.js -->
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
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/test/grpc/test_common.js -->
