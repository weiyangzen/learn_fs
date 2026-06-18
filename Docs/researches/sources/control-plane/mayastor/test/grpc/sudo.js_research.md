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
