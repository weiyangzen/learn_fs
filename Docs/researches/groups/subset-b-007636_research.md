# Research Group: subset-b-007636
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/uraft.cc -->
# sources/distributed-fs/lizardfs/src/uraft/uraft.cc

## Purpose
`uraft.cc` implements LizardFS' reduced Raft election engine. It elects one local "President" from configured metadata-server peers using UDP RPCs, heartbeat timers, vote requests, a data-version freshness check, and a loyalty window that prevents immediate split-brain after a leader heartbeat. It deliberately omits log replication and only decides leadership.

## Important APIs, Types, and Functions
The implementation backs the `uRaft` class declared in `uraft.h`. Public lifecycle and control APIs are `init()`, `set_options()`, `demoteLeader()`, and `set_block_promotion()`. Derived classes receive `nodePromote()`, `nodeDemote()`, `nodeLeader(int)`, and `nodeGetVersion()` callbacks. Internal election/RPC functions include `startElectionTimer()`, `startHearbeatTimer()`, `heartbeat()`, `electionTimeout()`, `sendHeartbeat()`, `sendRequestForVotes()`, `rpcAppend()`, `rpcAppendResponse()`, `rpcReqVote()`, `rpcReqVoteResponse()`, and `receivePacket()`. Address resolution and automatic local identity use `findNodeID()`, `findMatchingAddress()`, and `scanLocalInterfaces()`.

## Control Flow
Construction sets default election and heartbeat timing, node id/port, term, leader id, vote state, and promotion blocking. `init()` resolves every configured peer endpoint, chooses `state_.id` from options or local interfaces, computes quorum, binds the UDP socket to this node's endpoint, starts election and heartbeat timers, starts async receive, and signs an initial loyalty agreement for fast restarts. Election timeout moves the node to candidate, increments term, self-votes, refreshes `data_version` via `nodeGetVersion()`, sends vote requests, and either waits for quorum or immediately becomes leader in a one-node cluster. Heartbeat ticks advance logical local time, refresh self heartbeat, demote a president that loses loyal quorum, resend candidate vote requests, and send append-entry heartbeats as leader. A leader only calls `nodePromote()` after loyal heartbeat responses reach quorum.

## State and Persistence Behavior
All Raft state is runtime memory: `state_` tracks id, role, term, vote, leader, logical time, president flag, loyalty flag, and current data version; `node_` stores each peer endpoint plus vote, response, heartbeat, and version observations. No term or vote is persisted to disk here. The only persistent signal is indirect: derived `nodeGetVersion()` can read metadata version from the metadata server, and promotion/demotion side effects happen in `uRaftController`.

## Dependencies and Integration Points
The file depends on Boost.Asio UDP sockets and timers, Boost.Bind/date-time/lexical-cast, optional `getifaddrs`, and platform wrappers. It is extended by `uRaftStatus` for TCP status output and by `uRaftController` for LizardFS master/shadow transitions. It also depends on the configured server list matching actual bindable addresses or explicit ids.

## Risks and Edge Cases
The algorithm is intentionally not full Raft: terms/votes are volatile, there is no replicated log, and packet structs are sent as raw in-memory layouts. Safety rests on quorum, version comparison, heartbeat loyalty, and controller-side promotion blocking. Timing is sensitive because `rand()` election jitter is simple and `voteCount(true)` interprets heartbeat age from local ticks. `validPacket()` indexes `data[0]` before checking an empty packet, so callers must keep the current `bytes_recvd > 0` guard. Address auto-detection fails if zero or multiple local interfaces match configured peers.

## Test Signals
Useful tests simulate UDP packets with stale/newer terms, vote denial on lower data versions, loyalty agreement behavior, leader demotion on lost quorum, single-node promotion, id auto-detection failures, blocked promotion, and restart behavior. Integration signals come from HA cluster tests that promote/demote metadata servers and from status output showing term, leader, vote, and heartbeat transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/uraft.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/uraft.h -->
# sources/distributed-fs/lizardfs/src/uraft/uraft.h

## Purpose
`uraft.h` declares the micro-Raft election engine used by LizardFS metadata HA. It exposes a reduced consensus API whose only responsibility is selecting a single President with a metadata version at least as fresh as the quorum that elected it.

## Important APIs, Types, and Functions
`uRaft::Options` configures local id, UDP port, server list, election timeout range, heartbeat period, and quorum. Protected enums define node roles (`kFollower`, `kCandidate`, `kLeader`) and raw RPC packet types (`kRpcAppendEntries`, `kRpcRequestVote`, response types). `NodeInfo`, `RaftState`, `RpcHeader`, `RpcRequest`, and `RpcResponse` define the in-memory state and wire packet layout. Public APIs are `init()`, `demoteLeader()`, `set_block_promotion()`, `set_options()`, and the virtual callbacks `nodePromote()`, `nodeDemote()`, `nodeLeader(int)`, and `nodeGetVersion()`.

## Control Flow
Consumers configure options, optionally subclass callbacks, then call `init()` to bind sockets and start timers. The protected methods model the full event loop: timer starts, receive dispatch, heartbeat/vote sends, election timeout, heartbeat tick, RPC handlers, socket send, and local interface scanning.

## State and Persistence Behavior
The header stores no persistence, but it defines the runtime ownership: Boost.Asio `io_service`, UDP socket, election/heartbeat/loyalty timers, packet buffer, sender endpoint, per-node vector, local `RaftState`, promotion block flag, and options. Any persistence must be implemented by subclasses through callback side effects.

## Dependencies and Integration Points
It includes platform setup plus Boost.Asio and Boost.Array. `uRaftStatus` inherits it to expose state over TCP, and `uRaftController` inherits that status layer to manage LizardFS metadata server roles.

## Risks and Edge Cases
The wire protocol structs are not explicitly packed or endian-normalized, so the cluster assumes homogeneous ABI. The API requires callbacks to return quickly because they run on the Asio event loop. `Options::quorum` is public but `init()` recomputes it from server count, so external quorum overrides are not effective in the current implementation.

## Test Signals
Compile tests should verify subclass overrides and access to protected state through derived classes. Behavioral tests should cover callback ordering, timer-driven role transitions, and raw packet size assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/uraft.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/uraftcontroller.cc -->
# sources/distributed-fs/lizardfs/src/uraft/uraftcontroller.cc

## Purpose
`uraftcontroller.cc` connects uRaft leadership decisions to real LizardFS metadata-server process management. It runs helper commands to promote, demote, detect local metadata-server liveness, fetch metadata version, and handle dead-server recovery while keeping leader promotion blocked during unsafe local states.

## Important APIs, Types, and Functions
The file implements `uRaftController`: `init()`, `set_options()`, callback overrides `nodePromote()`, `nodeDemote()`, `nodeGetVersion()`, and `nodeLeader()`, periodic checks `checkCommandStatus()` and `checkNodeStatus()`, command helpers `runSlowCommand()`, `checkSlowCommand()`, `stopSlowCommand()`, `setSlowCommandTimeout()`, `runCommand()`, and `readString()`. It uses `CommandType` states `kCmdNone`, `kCmdPromote`, `kCmdDemote`, and `kCmdStatusDead`.

## Control Flow
Construction initializes timers, command pid/type, forced demote state, local liveness, and command timeouts. `init()` starts the status/uRaft base, blocks promotion, and, unless in elector-only mode, schedules periodic command-status and node-status checks. `nodePromote()` starts `lizardfs-uraft-helper promote` unless another incompatible command is running; conflicts demote the Raft leader and block promotion. `nodeDemote()` similarly starts helper demotion and blocks promotion until it completes. `checkCommandStatus()` reaps slow commands, cancels command timeout, unblocks promotion after demotion, marks node alive after promotion, and runs delayed forced demotion if needed. `checkNodeStatus()` polls `lizardfs-uraft-helper isalive`; a transition to alive unblocks promotion, while a transition to dead demotes Raft state, blocks promotion, and starts `lizardfs-uraft-helper dead`.

## State and Persistence Behavior
Runtime state tracks one child process pid, command type, timeout timer, forced-demote flag, and last liveness. Persistent effects are delegated to `lizardfs-uraft-helper`, which restarts LizardFS master/shadow services, assigns or drops floating IPs, and reads metadata version. `nodeGetVersion()` preserves the last known `state_.data_version` when helper output times out or is invalid, avoiding a downgrade from transient command failure.

## Dependencies and Integration Points
The controller depends on Boost.Asio timers, Boost lexical cast/version fork notifications, POSIX `fork`, `exec`, `pipe`, `poll`, `waitpid`, `kill`, syslog, and `common/time_utils::Timeout`. It integrates with `uRaftStatus` and `uRaft`, and with the installed `lizardfs-uraft-helper` command.

## Risks and Edge Cases
Slow helper commands are shell-executed strings, while fast commands use `execvp` argument vectors. Timeout killing only kills the direct child, so helper scripts that spawn descendants need their own cleanup. Command completion status is not inspected beyond process exit; any exit is treated as completion. Promotion is blocked during demotion/dead handling, making missed unblock paths dangerous. Poll-based `readString()` treats EOF after data as success but kills the child on timeout or read error.

## Test Signals
Mock helper commands should cover promote/demote conflicts, timeout killing, invalid metadata-version output, isalive alive/dead transitions, dead handler invocation, elector mode, forced demote after a running promote, and promotion blocking/unblocking. HA integration tests should verify service personality and floating IP transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/uraftcontroller.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/uraftcontroller.h -->
# sources/distributed-fs/lizardfs/src/uraft/uraftcontroller.h

## Purpose
`uraftcontroller.h` declares the controller layer that turns uRaft status changes into LizardFS metadata-server management actions.

## Important APIs, Types, and Functions
`uRaftController` extends `uRaftStatus`. Its `Options` adds local master host/port, elector mode, status polling periods, get-version timeout, promote/demote timeouts, and dead-handler timeout. Public methods are constructor/destructor, `init()`, `set_options()`, and overrides for `nodePromote()`, `nodeDemote()`, `nodeGetVersion()`, and `nodeLeader(int)`. Protected helpers manage periodic checks and child process execution.

## Control Flow
The header's API establishes the lifecycle: configure options, call `init()`, let inherited uRaft elect a leader, and have controller callbacks run helper commands. Periodic status timers keep local process liveness synchronized with promotion eligibility.

## State and Persistence Behavior
The class stores Asio timers, a child pid, command type, elapsed command timer, forced-demote flag, last node liveness, and options. Persistent behavior is indirect through helper commands that mutate local service state and network addresses.

## Dependencies and Integration Points
It includes `common/time_utils.h`, POSIX `unistd.h`, and `uraftstatus.h`. It is the main class used by the `lizardfs-uraft` executable and must stay compatible with the helper script interface.

## Risks and Edge Cases
The controller assumes only one slow helper command is active. Any new callback path must preserve that invariant and avoid blocking the Asio loop. Option defaults live in the `.cc`, so callers must set complete options or rely on constructor defaults.

## Test Signals
Tests should instantiate with a fake helper path or controlled environment and verify timer scheduling, command-state transitions, and inherited status output after callback activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/uraftcontroller.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/uraftstatus.cc -->
# sources/distributed-fs/lizardfs/src/uraft/uraftstatus.cc

## Purpose
`uraftstatus.cc` adds a TCP status endpoint to uRaft. It accepts client connections and returns a text snapshot of the local election state, leader identity, promotion block state, and per-node votes/heartbeats/versions when relevant.

## Important APIs, Types, and Functions
`uRaftStatusConnection` owns one TCP socket and response buffer; `init()` writes the prepared buffer asynchronously. `uRaftStatus` implements `init()`, `set_options()`, `storeData()`, and `acceptConnection()`. `storeData()` formats fields from inherited `state_`, `node_`, `opt_`, and `block_leader_promotion_`.

## Control Flow
`uRaftStatus::init()` first initializes the base uRaft election engine, then opens, binds, and listens on the configured status TCP port. `acceptConnection()` allocates a shared connection, accepts asynchronously, fills the response buffer with `storeData()`, starts async write, and immediately re-arms accept for the next client.

## State and Persistence Behavior
The status layer is runtime-only. It exposes inherited volatile election state and does not persist or mutate leadership. Each connection owns its response buffer long enough for async write through `shared_from_this()`.

## Dependencies and Integration Points
The file uses Boost.Asio TCP acceptor/socket/write and Boost.Format. It is inherited by `uRaftController`, and external tools can query the TCP port for operational diagnostics.

## Risks and Edge Cases
The status format is plain text and appears intentionally human-oriented, including the misspelled `"I'M THE BOOSSSS"` marker. Consumers should not assume a stable machine protocol unless maintained. `boost::format("%i")` is used with `uint64_t` fields, which can truncate or format incorrectly on some platforms. Accept errors are ignored and accept is always rearmed.

## Test Signals
Tests should connect to the status port and verify key fields after follower/candidate/leader transitions, blocked promotion, and per-node arrays. Compatibility tests should catch accidental changes if scripts parse the text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/uraftstatus.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/uraftstatus.h -->
# sources/distributed-fs/lizardfs/src/uraft/uraftstatus.h

## Purpose
`uraftstatus.h` declares the TCP status wrapper around the uRaft election engine.

## Important APIs, Types, and Functions
`uRaftStatusConnection` exposes `socket()` and `init()` and stores a response byte vector. `uRaftStatus::Options` extends `uRaft::Options` with `status_port`. `uRaftStatus` exposes constructor/destructor, `init()`, `set_options()`, and protected `acceptConnection()`/`storeData()`.

## Control Flow
After options are set, `init()` starts the base election machinery and then the status accept loop. Each accepted connection gets a freshly generated snapshot and an async write.

## State and Persistence Behavior
Only TCP acceptor/socket state and options are stored in this layer. It reads but does not persist inherited Raft state.

## Dependencies and Integration Points
It includes `<list>` but primarily depends on `uraft.h` and Boost.Asio types through the base class. `uRaftController` subclasses this to combine status reporting with service control.

## Risks and Edge Cases
`uRaftStatusConnection::data_` is public so the server fills it directly before `init()`. The class is tightly coupled to Asio lifetime rules; forgetting `shared_from_this()` would risk use-after-free during async writes.

## Test Signals
Compile and integration tests should confirm accepted connections remain alive through write completion and that configured `status_port` is honored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/uraft/uraftstatus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/tests/CMakeLists.txt

## Purpose
This CMake file wires the bash-based LizardFS test suite into a GoogleTest executable. It generates suite and case headers from `test_suites/`, configures runtime constants, and installs the `lizardfs-tests` runner.

## Important APIs, Types, and Functions
The `list_of_test_cases` custom target builds `test_suites.h` from suite directory names, runs `tools/generate_tests_from_templates.sh`, discovers `test_*.sh` files, optionally filters out polonaise tests, and emits `test_cases.h` entries using `add_test_case(suite,test)`. It configures `set_lizardfs_constants.sh` from the `.in` template and builds `lizardfs-tests` from `lizardfs-tests.cc`.

## Control Flow
At build time, generated headers are refreshed via `copy_if_different`; `lizardfs-tests.cc` has object dependencies on those headers and depends on `list_of_test_cases`. At runtime, each generated gtest case delegates to `run-test.sh`.

## State and Persistence Behavior
Generated state lives in the CMake binary directory: `test_suites.h`, `test_cases.h`, and `set_lizardfs_constants.sh`. Installed state includes the executable and constants script.

## Dependencies and Integration Points
It depends on GTest, Boost.System, Boost.Filesystem, shell utilities (`ls`, `find`, `sed`, `awk`, `xargs`), and the test template generator. It integrates the bash suite with CTest/GTest and packaging install paths.

## Risks and Edge Cases
The generated source property is assigned twice with `OBJECT_DEPENDS`; depending on CMake behavior, the second assignment may override the first. Shell discovery order and optional polonaise filtering can affect test inventory. Template generation must run before `find` output is consumed.

## Test Signals
Build validation should inspect generated headers, `--gtest_list_tests`, and polonaise-enabled/disabled configurations. A clean build should regenerate headers without causing needless rebuilds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/data/extract_tests_durations.py -->
# sources/distributed-fs/lizardfs/tests/data/extract_tests_durations.py

## Purpose
`extract_tests_durations.py` parses Jenkins/GTest logs and emits averaged per-test duration hints for Sanity, Short, and Long LizardFS suites. These hints can feed scheduling or timeout estimates.

## Important APIs, Types, and Functions
`TestSuite` normalizes supported suite names. `create_test_suite_enum()` accepts aliases. `process_one_build()` parses a direct Sanity log or discovers concurrent subjob logs for Short/Long. `parse_logfile_for_tests()` extracts `Suite.test (milliseconds)` lines. `get_subjobs_from_mainjob_log()` and `convert_to_correct_subjob_path()` locate concurrent job logs. `print_result()` averages durations, converts to seconds, rounds down to a 10-second bucket, and floors zero to 5 seconds.

## Control Flow
`main()` validates arguments, normalizes the suite, processes every provided log path, aggregates durations by test name, and prints `name=duration` lines sorted by name. Missing subjob logs cause the whole build to be skipped rather than partially counted.

## State and Persistence Behavior
The script is read-only with respect to logs and writes results to stdout plus errors to stderr. No cache or output file is persisted.

## Dependencies and Integration Points
It depends on Python 3 standard library modules `os`, `re`, `sys`, `enum`, and `typing`. It is coupled to Jenkins log text and GTest output formatting.

## Risks and Edge Cases
Regexes assume word-character test names and a specific concurrent-job phrase. Rounding down can understate slow tests, and skipping whole builds on one missing subjob trades completeness for consistency. Unsupported suite aliases raise a generic exception.

## Test Signals
Fixture logs should cover direct Sanity parsing, Short/Long subjob discovery, missing subjob handling, multiple-build averaging, zero-duration flooring, unsupported suite names, and malformed/empty logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/data/extract_tests_durations.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/dispatcher/Dockerfile -->
# sources/distributed-fs/lizardfs/tests/dispatcher/Dockerfile

## Purpose
This Dockerfile packages the Flask test dispatcher service in a minimal Python 3.10 image.

## Important APIs, Types, and Functions
It creates a non-root `runner` user, sets `/code` as workdir, configures `FLASK_APP`, exposes port 5000, installs `requirements.txt`, copies the dispatcher tree, and starts waitress with `--threads=1 --call app:create_app`.

## Control Flow
Docker build installs dependencies before copying the app source, improving cache reuse. Container start launches waitress serving the factory-created Flask app.

## State and Persistence Behavior
The image has no volume or persistence. Dispatcher queues remain in process memory and vanish on restart.

## Dependencies and Integration Points
It depends on `python:3.10-slim`, `requirements.txt`, waitress, Flask app factory, and Docker Compose port mapping.

## Risks and Edge Cases
Single-thread waitress matches the app's unsynchronized in-memory queue but limits concurrency. No healthcheck, authentication, or persistent store is configured.

## Test Signals
Build and container smoke tests should verify dependency install, non-root execution, `/` response, and queue behavior through mapped port 5000.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/dispatcher/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/dispatcher/app.py -->
# sources/distributed-fs/lizardfs/tests/dispatcher/app.py

## Purpose
`dispatcher/app.py` provides a small Flask service that coordinates distributed test execution. It stores per-build, per-suite queues of test names and hands out the next test atomically within the single-process Flask app.

## Important APIs, Types, and Functions
`create_app()` builds the Flask app, initializes `current_app.config["tests"]`, and registers `/`, `/push_list`, and `/next_test`. Type aliases document the nested shape: build id -> suite -> list of tests.

## Control Flow
`GET /` returns the current in-memory queue map. `POST /push_list` reads JSON with `build_id`, `test_suite`, and `tests`, rejects duplicate suite lists for the same build with HTTP 412, and stores the queue. `GET /next_test` validates query arguments, returns an empty detail for missing queues, pops the first queued test, and removes empty suite/build containers.

## State and Persistence Behavior
All state is in Flask process memory. Restarting the service loses queues; concurrent access relies on the deployment being single-threaded or externally serialized. The provided Dockerfile runs waitress with one thread, matching that assumption.

## Dependencies and Integration Points
It depends on Flask and JSON. The dispatcher client posts gtest-derived test lists and asks for next tests from build agents.

## Risks and Edge Cases
The code uses `assert json_data is not None`, which can be disabled under optimized Python and yields 500-style behavior for bad payloads. There is no authentication, persistence, locking, or schema validation. Running with multiple workers/threads would race list mutation.

## Test Signals
HTTP tests should cover duplicate push, missing args, empty queues, pop order, cleanup of empty build/suite entries, bad JSON, and multi-client behavior under the intended one-thread deployment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/dispatcher/app.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/dispatcher/client/dispatcher_client.py -->
# sources/distributed-fs/lizardfs/tests/dispatcher/client/dispatcher_client.py

## Purpose
`dispatcher_client.py` is the command-line client for the test dispatcher. It pushes a filtered gtest list for a build/suite and retrieves the next test to run.

## Important APIs, Types, and Functions
`TESTS_DISPATCHER_URL` comes from the environment. `slash_join()` normalizes URL segments. `_call()` wraps requests for GET/POST/PUT/DELETE and JSON decoding. `push_list()` builds a list via `get_gtest_testlist()` and posts it. `next_test()` queries the dispatcher and returns the `details` field. The CLI parser exposes `--action`, `--build_id`, `--lizardfs_tests_path`, `--test_suite`, and `--excluded_tests`.

## Control Flow
For `push_list`, the client shells out through `tests_list.py` to list tests, sends JSON to `/push_list`, and returns the decoded response. For `next_test`, it sends build/suite parameters to `/next_test` and prints the next test name.

## State and Persistence Behavior
The client keeps no local state. Dispatcher state is remote and in-memory.

## Dependencies and Integration Points
It depends on `requests`, the local `tests_list` module, and the `lizardfs-tests` binary. It integrates with CI agents that split a suite across workers.

## Risks and Edge Cases
HTTP errors are logged gently and can return an empty string object, but `next_test()` assumes a `details` key and can raise. `excluded_tests` is typed as a string by argparse although `tests_list` expects a list, so callers must be careful about how exclusions are supplied. Connection and timeout errors exit the process.

## Test Signals
Mocked request tests should cover URL joining, duplicate push HTTP errors, connection failures, malformed JSON, missing `details`, exclusion handling, and CLI argument validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/dispatcher/client/dispatcher_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/dispatcher/client/tests_list.py -->
# sources/distributed-fs/lizardfs/tests/dispatcher/client/tests_list.py

## Purpose
`tests_list.py` extracts a filtered list of gtest test names for one LizardFS suite.

## Important APIs, Types, and Functions
`get_excluded_tests_two_types()` expands exclusions so both `Suite.test` and `test` forms are recognized. `get_gtest_testlist()` runs `lizardfs-tests --gtest_list_tests --gtest_filter=<suite>*`, skips the first two lines, and returns stripped test names not in the exclusion set.

## Control Flow
The dispatcher client calls `get_gtest_testlist()`, which shells out through `os.popen`, consumes gtest list output, and filters names.

## State and Persistence Behavior
No persistent state is written. The function depends entirely on the current executable output.

## Dependencies and Integration Points
It depends on Python standard `os` and generated gtest inventory from `lizardfs-tests`. It feeds `dispatcher_client.py`.

## Risks and Edge Cases
The command is assembled as a shell string, so paths or suite names with shell metacharacters are unsafe. Skipping exactly two lines assumes stable gtest output. Type hints expect `excluded_tests` as a list, while the CLI passes a string unless split elsewhere.

## Test Signals
Use fixture command output or monkeypatch `os.popen` to test exclusion expansion, suite filtering, empty output, and shell argument handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/dispatcher/client/tests_list.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/dispatcher/docker-compose.yml -->
# sources/distributed-fs/lizardfs/tests/dispatcher/docker-compose.yml

## Purpose
This compose file runs the dispatcher Flask service for CI or local distributed test scheduling.

## Important APIs, Types, and Functions
It defines one service, `flask`, built from the dispatcher directory, mapping host `${EXTERNAL_PORT}` to container `5000`, with `restart: unless-stopped`.

## Control Flow
`docker compose up` builds the local Dockerfile and starts the service. Agents can point `TESTS_DISPATCHER_URL` at the chosen external port.

## State and Persistence Behavior
No volumes are declared, so dispatcher state is container memory only and is lost on restart/recreate.

## Dependencies and Integration Points
It depends on Docker Compose variable substitution for `EXTERNAL_PORT` and the dispatcher Dockerfile.

## Risks and Edge Cases
Missing `EXTERNAL_PORT` prevents predictable port binding. Restarting the service during a run loses queues. The service is exposed without auth.

## Test Signals
Compose validation should include config rendering with `EXTERNAL_PORT`, container startup, and a simple push/next-test HTTP round trip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/dispatcher/docker-compose.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/lizardfs-tests.cc -->
# sources/distributed-fs/lizardfs/tests/lizardfs-tests.cc

## Purpose
`lizardfs-tests.cc` is the C++ GoogleTest bridge for bash system tests. It creates one gtest case per generated shell test and reports shell failures as gtest failures with captured error text.

## Important APIs, Types, and Functions
`BashTestEnvironment` creates and removes `/tmp/Lizardfs_bashtests_global_env`. `BashTestingSuite::run_test_case()` constructs `ERROR_FILE`, `TEST_SUITE_NAME`, and `TEST_CASE_NAME`, runs `run-test.sh` with the suite script, and reads the shared error file on failure. The `add_test_case` macro expands generated test entries into `TEST_F` bodies.

## Control Flow
The global environment prepares a world-writable temp directory. Each test creates an empty writable error file, calls the shell runner, and fails with either script crash text or the error file content. Generated `test_suites.h` and `test_cases.h` supply test classes and cases.

## State and Persistence Behavior
State is transient under `/tmp/Lizardfs_bashtests_global_env` and whatever the shell runner creates. The shared error file is outside per-test `TEMP_DIR` so it survives shell cleanup long enough for gtest to read it.

## Dependencies and Integration Points
It depends on GTest, Boost.Filesystem, generated headers, and `TEST_DATA_PATH` from CMake. It integrates with `run-test.sh` and the shell harness in `tools/test_main.sh`.

## Risks and Edge Cases
The command is assembled as a shell string, so paths with shell metacharacters would be risky. `system()` status is only checked for nonzero, not decoded. The global temp path is fixed, so concurrent independent runners could interfere.

## Test Signals
Signals include `--gtest_list_tests`, a deliberately failing shell test producing readable output, and concurrent runner isolation checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/lizardfs-tests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/revert_setup_machine.sh -->
# sources/distributed-fs/lizardfs/tests/revert_setup_machine.sh

## Purpose
This shell scenario exercises tests scenario coverage for revert setup machine in the LizardFS bash test harness. The script is part of `tests` and focuses on `revert setup machine` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `usage() {`

External commands and harness APIs used by the scenario:
- `setup_machine`
- `lizardfstest`
- `lizardfstest_`
- `lizardfstests`
- `lizardfs_tests`
- `umount`
- `lizardfs`
- `lizardfstest_loop`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 70 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for tests scenario coverage for revert setup machine. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/revert_setup_machine.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/run-test.sh -->
# sources/distributed-fs/lizardfs/tests/run-test.sh

## Purpose
This shell scenario exercises tests scenario coverage for run-test in the LizardFS bash test harness. The script is part of `tests` and focuses on `run-test` using a temporary cluster prepared by `tools/test_main.sh`. It also contains generator markers consumed by `run-test.sh` to run variants.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `start_test() {`
- `unwrap_generators() {`
- `stop_tests() {`

External commands and harness APIs used by the scenario:
- `lizardfstest`
- `lizardfstest_`
- `lizardfs_error_dir`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 118 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for tests scenario coverage for run-test. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/run-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/set_lizardfs_constants.sh.in -->
# sources/distributed-fs/lizardfs/tests/set_lizardfs_constants.sh.in

## Purpose
This template emits shell constants describing the compiled LizardFS block geometry, version, and install library path for bash tests.

## Important APIs, Types, and Functions
Configured variables are `LIZARDFS_BLOCKS_IN_CHUNK`, `LIZARDFS_BLOCK_SIZE`, computed `LIZARDFS_CHUNK_SIZE`, normalized `LIZARDFS_VERSION`, `LIZARDFS_INSTALL_LIBDIR`, and `LIZARDFS_INSTALL_FULL_LIBDIR`.

## Control Flow
CMake substitutes `@...@` placeholders into `set_lizardfs_constants.sh`; shell tests source the generated file to use chunk size and install paths.

## State and Persistence Behavior
The generated script is build/install state. It does not mutate runtime state when sourced, except defining variables in the caller shell.

## Dependencies and Integration Points
It depends on CMake package/block constants and on `LIZARDFS_ROOT` being set by the test harness for full library path expansion.

## Risks and Edge Cases
Version normalization strips suffixes after `-`, which may hide prerelease/build metadata. Missing `LIZARDFS_ROOT` produces a relative or incorrect full libdir.

## Test Signals
Build tests should source the generated file and validate numeric chunk size, version normalization, and expected library path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/set_lizardfs_constants.sh.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/setup_machine.sh -->
# sources/distributed-fs/lizardfs/tests/setup_machine.sh

## Purpose
This shell scenario exercises tests scenario coverage for setup machine in the LizardFS bash test harness. The script is part of `tests` and focuses on `setup machine` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `usage() {`

External commands and harness APIs used by the scenario:
- `lizardfstest`
- `lizardfstest_0`
- `lizardfstest_9`
- `mount`
- `lizardfstest_loop`
- `cmake`
- `git`
- `acl`
- `dbench`
- `rsync`
- `make`
- `lizardfs_error_dir`
- `lizardfstests`
- `lizardfstest_`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 248 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for tests scenario coverage for setup machine. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/setup_machine.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/Benchmarks/test_dbench_throughput.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/Benchmarks/test_dbench_throughput.sh

## Purpose
This shell scenario exercises filesystem workload benchmarking in the LizardFS bash test harness. The script is part of `Benchmarks` and focuses on `dbench throughput` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 6 minutes`
- `CHUNKSERVERS=3`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `dbench`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 23 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for filesystem workload benchmarking. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/Benchmarks/test_dbench_throughput.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/Benchmarks/test_disk_speed.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/Benchmarks/test_disk_speed.sh

## Purpose
This shell scenario exercises Benchmarks scenario coverage for disk speed in the LizardFS bash test harness. The script is part of `Benchmarks` and focuses on `disk speed` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 30 minutes`
- `CHUNKSERVERS=3`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs`
- `dd`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 42 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for Benchmarks scenario coverage for disk speed. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/Benchmarks/test_disk_speed.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/Benchmarks/test_ramdisk_speed.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/Benchmarks/test_ramdisk_speed.sh

## Purpose
This shell scenario exercises Benchmarks scenario coverage for ramdisk speed in the LizardFS bash test harness. The script is part of `Benchmarks` and focuses on `ramdisk speed` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 3 minutes`
- `CHUNKSERVERS=3`
- `USE_RAMDISK=YES`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs`
- `dd`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 47 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for Benchmarks scenario coverage for ramdisk speed. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/Benchmarks/test_ramdisk_speed.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ContinuousTests/test_building_lizardfs.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ContinuousTests/test_building_lizardfs.sh

## Purpose
This shell scenario exercises ContinuousTests scenario coverage for building lizardfs in the LizardFS bash test harness. The script is part of `ContinuousTests` and focuses on `building lizardfs` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 60 minutes`
- `MINIMUM_PARALLEL_JOBS=4`
- `MAXIMUM_PARALLEL_JOBS=16`
- `PARALLEL_JOBS=$(get_nproc_clamped_between`
- `N=1000`
- `MESSAGE="testing`

External commands and harness APIs used by the scenario:
- `lizardfs`
- `git`
- `cmake`
- `make`

Assertions and expectations include:
- `assert_success git clone "https://github.com/lizardfs/lizardfs.git" lizardfs`
- `assert_success git pull`
- `assert_success touch .  # Update timestamp checked by this 'if'`
- `assert_success git clone "$workspace/lizardfs" "$subdir"`
- `assert_success lizardfs setgoal -r "$(random 2 3)" "$subdir"  # Change goal to 2 or 3 (randomly)`
- `assert_success git reset --hard HEAD^  # Make sure that 'git pull' will change something`
- `assert_success mkdir -p build`
- `assert_success cmake .. -DCMAKE_BUILD_TYPE=Debug -DCMAKE_INSTALL_PREFIX=../install_prefix`
- `assert_success make -j${PARALLEL_JOBS}`
- `assert_success make install`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 42 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ContinuousTests scenario coverage for building lizardfs. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ContinuousTests/test_building_lizardfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ContinuousTests/test_generating_files.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ContinuousTests/test_generating_files.sh

## Purpose
This shell scenario exercises ContinuousTests scenario coverage for generating files in the LizardFS bash test harness. The script is part of `ContinuousTests` and focuses on `generating files` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 60 minutes`
- `FILE_SIZE=$size`

External commands and harness APIs used by the scenario:
- `lizardfs`
- `file-validate`
- `file-overwrite`
- `file-generate`
- `mfssetgoal`

Assertions and expectations include:
- `assert_success file-validate "$file"`
- `assert_success mv -v "$file" "$file.tmp"`
- `assert_success truncate -s "$size" "$file.tmp"`
- `assert_success file-overwrite "$file.tmp"`
- `assert_success mv -v "$file.tmp" "$file"`
- `FILE_SIZE=$size assert_success file-generate "$file.tmp"`
- `assert_success mfssetgoal "$(random 2 4)" "$file"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 27 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ContinuousTests scenario coverage for generating files. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ContinuousTests/test_generating_files.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ContinuousTests/test_tar_archives.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ContinuousTests/test_tar_archives.sh

## Purpose
This shell scenario exercises ContinuousTests scenario coverage for tar archives in the LizardFS bash test harness. The script is part of `ContinuousTests` and focuses on `tar archives` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 240 minutes  # Must be high when the 30G file is validated`
- `MESSAGE="Verifying`
- `FILE_SIZE=$size`
- `verify_archive() {`

External commands and harness APIs used by the scenario:
- `tar`
- `file-validate`
- `lizardfs`
- `file-generate`

Assertions and expectations include:
- `assert_success mkdir work/verify`
- `assert_success tar -xf "$archive" -C work/verify`
- `assert_less_than 4 $(echo "$files" | wc -l)`
- `assert_success file-validate "$file"`
- `assert_success rm -rf work/verify`
- `assert_success rm -rf work/*`
- `assert_success mkdir -p "work/$path"`
- `FILE_SIZE=$size assert_success file-generate "$filename"`
- `assert_success touch "$archive"  # Create if not exists`
- `assert_success lizardfs makesnapshot "$archive" work/tmp.tar`
- `assert_success tar -f work/tmp.tar --append --seek -v -C work "$path"`
- `assert_success mv -v work/tmp.tar "$archive"`
- `assert_success mv -v "$archive.$((i))" "$archive.$((i+1))"`
- `assert_success mv -v "$archive" "$archive.1"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 69 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ContinuousTests scenario coverage for tar archives. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ContinuousTests/test_tar_archives.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ExtraTests/test_nfs_ganesha.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ExtraTests/test_nfs_ganesha.sh

## Purpose
This shell scenario exercises NFS/Ganesha integration in the LizardFS bash test harness. The script is part of `ExtraTests` and focuses on `nfs ganesha` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 5 minutes`
- `CHUNKSERVERS=5`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `CHUNKSERVER_EXTRA_CONFIG="READ_AHEAD_KB`
- `MINIMUM_PARALLEL_JOBS=4`
- `MAXIMUM_PARALLEL_JOBS=16`
- `PARALLEL_JOBS=$(get_nproc_clamped_between`
- `CC="ccache`
- `test_error_cleanup() {`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `umount`
- `ganesha.nfsd`
- `ganesha-2.5-stable`
- `cmake`
- `make`
- `ganesha.conf`
- `lizardfs_info_`
- `mount`
- `git`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 105 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for NFS/Ganesha integration. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ExtraTests/test_nfs_ganesha.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ExtraTests/test_nfs_ganesha_multi_export.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ExtraTests/test_nfs_ganesha_multi_export.sh

## Purpose
This shell scenario exercises NFS/Ganesha integration in the LizardFS bash test harness. The script is part of `ExtraTests` and focuses on `nfs ganesha multi export` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 5 minutes`
- `CHUNKSERVERS=5`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `CHUNKSERVER_EXTRA_CONFIG="READ_AHEAD_KB`
- `MINIMUM_PARALLEL_JOBS=4`
- `MAXIMUM_PARALLEL_JOBS=16`
- `PARALLEL_JOBS=$(get_nproc_clamped_between`
- `CC="ccache`
- `FILE_SIZE=1234567`
- `FILE_SIZE=2345678`
- `test_error_cleanup() {`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `umount`
- `ganesha.nfsd`
- `ganesha-2.5-stable`
- `cmake`
- `make`
- `ganesha.conf`
- `lizardfs_info_`
- `showmount`
- `mount`
- `file-generate`
- `file-validate`

Assertions and expectations include:
- `assert_eventually 'showmount -e localhost'`
- `assert_empty "$(find $TEMP_DIR/mnt/nfs1 | grep test2 | cat)"`
- `assert_empty "$(find $TEMP_DIR/mnt/nfs2 | grep test1 | cat)"`
- `assert_failure file-validate $TEMP_DIR/mnt/nfs97/export1/test1.bin`
- `assert_failure file-validate $TEMP_DIR/mnt/nfs97/export2/test2.bin`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 152 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for NFS/Ganesha integration. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ExtraTests/test_nfs_ganesha_multi_export.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ExtraTests/test_tapeserver_goal.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ExtraTests/test_tapeserver_goal.sh

## Purpose
This shell scenario exercises ExtraTests scenario coverage for tapeserver goal in the LizardFS bash test harness. The script is part of `ExtraTests` and focuses on `tapeserver goal` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=2`
- `USE_RAMDISK=YES`
- `MASTER_CUSTOM_GOALS="5`
- `FILE_SIZE=150K`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_probe_master`
- `file-generate`
- `lizardfs`
- `mfsfileinfo`

Assertions and expectations include:
- `assert_eventually_prints 1 'lizardfs_probe_master list-tapeservers | wc -l'`
- `assert_equals 0 $(lizardfs fileinfo file | grep "tape replica" | wc -l)`
- `assert_eventually_prints 1 'mfsfileinfo file | grep "tape replica 1: OK" | wc -l'`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 18 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ExtraTests scenario coverage for tapeserver goal. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ExtraTests/test_tapeserver_goal.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_acl_permissions.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_acl_permissions.sh

## Purpose
This shell scenario exercises ACL and permission semantics, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `acl permissions` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set '4 minutes'`
- `MESSAGE="Testing`
- `CHUNKSERVERS=1`
- `USE_RAMDISK=YES`
- `LZFS_MOUNT_COMMAND=mfsmount3`
- `MFSEXPORTS_EXTRA_OPTIONS=nomasterpermcheck,ignoregid`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`

External commands and harness APIs used by the scenario:
- `setfacl`
- `getfacl`
- `mfsmount3`
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs_master_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `lizardfstest`
- `lizardfstest_`
- `lizardfstest_1`
- `lizardfstest_2`
- `lizardfstest_0`
- `make`

Assertions and expectations include:
- `assert_program_installed setfacl getfacl python3`
- `MESSAGE="Testing ACL support in $TEMP_DIR/" assert_success setfacl -m group:fuse:rw "$TEMP_DIR/f"`
- `expect_equals "$(ls $lizdir)" "$(ls $tmpdir)"`
- `expect_equals "$expected_perm" "$actual_perm"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 77 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ACL and permission semantics, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_acl_permissions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_auto_recovery_build.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_auto_recovery_build.sh

## Purpose
This shell scenario exercises metadata auto-recovery, EC goal behavior in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `auto recovery build` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 hour`
- `CHUNKSERVERS=2`
- `MOUNTS=1`
- `CHUNKSERVER_EXTRA_CONFIG="MASTER_RECONNECTION_DELAY`
- `MASTER_EXTRA_CONFIG="AUTO_RECOVERY`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `MINIMUM_PARALLEL_JOBS=5`
- `MAXIMUM_PARALLEL_JOBS=16`
- `PARALLEL_JOBS=$(get_nproc_clamped_between`
- `master_kill_loop() {`

External commands and harness APIs used by the scenario:
- `git`
- `cmake`
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs_stop_master_without_saving_metadata`
- `lizardfs_master_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `lizardfs`
- `make`

Assertions and expectations include:
- `assert_program_installed git`
- `assert_program_installed cmake`
- `assert_success git clone https://github.com/lizardfs/lizardfs.git`
- `assert_success cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=../install`
- `assert_success make -j${PARALLEL_JOBS} install`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 34 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for metadata auto-recovery, EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_auto_recovery_build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_big_files.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_big_files.sh

## Purpose
This shell scenario exercises LongSystemTests scenario coverage for big files in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `big files` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 3 hours`
- `CHUNKSERVERS=3`
- `MOUNTS=2`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `FILE_SIZE=$size`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `file-generate`
- `file-validate`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 18 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for LongSystemTests scenario coverage for big files. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_big_files.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_build_lizardfs.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_build_lizardfs.sh

## Purpose
This shell scenario exercises LongSystemTests scenario coverage for build lizardfs in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `build lizardfs` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 10 minutes`
- `CHUNKSERVERS=8`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `CHUNKSERVER_EXTRA_CONFIG="READ_AHEAD_KB`
- `MINIMUM_PARALLEL_JOBS=4`
- `MAXIMUM_PARALLEL_JOBS=16`
- `PARALLEL_JOBS=$(get_nproc_clamped_between`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `git`
- `cmake`
- `make`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 26 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for LongSystemTests scenario coverage for build lizardfs. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_build_lizardfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_changing_master_during_build.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_changing_master_during_build.sh

## Purpose
This shell scenario exercises LongSystemTests scenario coverage for changing master during build in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `changing master during build` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set '40 minutes'`
- `MASTERSERVERS=$metaservers_nr`
- `CHUNKSERVERS=2`
- `CHUNKSERVER_EXTRA_CONFIG="MASTER_RECONNECTION_DELAY`
- `MFSEXPORTS_EXTRA_OPTIONS="allcanchangequota"`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `MASTER_EXTRA_CONFIG="MAGIC_AUTO_FILE_REPAIR`
- `MINIMUM_PARALLEL_JOBS=5`
- `MAXIMUM_PARALLEL_JOBS=16`
- `PARALLEL_JOBS=$(get_nproc_clamped_between`
- `master_kill_loop() {`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `git`
- `cmake`
- `lizardfs_master_n`
- `lizardfs_shadow_synchronized`
- `lizardfs_stop_master_without_saving_metadata`
- `lizardfs_make_conf_for_shadow`
- `lizardfs_make_conf_for_master`
- `lizardfs_master_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `lizardfs`
- `make`

Assertions and expectations include:
- `assert_program_installed git`
- `assert_program_installed cmake`
- `assert_eventually "lizardfs_shadow_synchronized $shadow_id"`
- `assert_eventually "lizardfs_shadow_synchronized $new_master_id"`
- `assert_eventually "lizardfs_shadow_synchronized $prev_master_id"`
- `assert_success git clone https://github.com/lizardfs/lizardfs.git`
- `assert_success cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=../install`
- `assert_success make -j${PARALLEL_JOBS} install`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 63 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for LongSystemTests scenario coverage for changing master during build. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_changing_master_during_build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_chunk_rebalancing.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_chunk_rebalancing.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `chunk rebalancing` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 120 seconds`
- `CHUNKSERVERS=5`
- `USE_LOOP_DISKS=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `CHUNKSERVER_EXTRA_CONFIG="HDD_TEST_FREQ`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `MESSAGE="Chunks`
- `MESSAGE="Validating`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_ready_chunkservers`
- `lizardfs`
- `file-generate`
- `lizardfs_rebalancing_status`
- `file-validate`
- `lizardfs_wait_for_all_ready_chunkservers`

Assertions and expectations include:
- `( FILE_SIZE=1M expect_success file-generate "dir/file_$i" ) &`
- `( FILE_SIZE=2M expect_success file-generate "dirxor/file_$i" ) &`
- `MESSAGE="Chunks are not rebalanced properly" assert_equals "$expected_rebalancing_status" "$status"`
- `MESSAGE="Validating files without chunkserver $csid" expect_success file-validate dir/*`
- `MESSAGE="Validating files without chunkserver $csid" expect_success file-validate dirxor/*`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 51 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_chunk_rebalancing.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_chunkserver_restart.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_chunkserver_restart.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `chunkserver restart` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set '200 seconds'`
- `CHUNKSERVERS=64`
- `CHUNKSERVERS=$CHUNKSERVERS`
- `USE_RAMDISK=YES`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_chunkserver_daemon`

Assertions and expectations include:
- `assert_eventually 'lizardfs_chunkserver_daemon $c isalive' '20 seconds'`
- `assert_eventually '! lizardfs_chunkserver_daemon $c isalive' '20 seconds'`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 30 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_chunkserver_restart.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_compilation_and_rsync.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_compilation_and_rsync.sh

## Purpose
This shell scenario exercises I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `compilation and rsync` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 2 hours`
- `MINIMUM_PARALLEL_JOBS=5`
- `MAXIMUM_PARALLEL_JOBS=16`
- `PARALLEL_JOBS=$(get_nproc_clamped_between`
- `CHUNKSERVERS=3`
- `MOUNTS=1`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `test_worker() {`

External commands and harness APIs used by the scenario:
- `git`
- `cmake`
- `rsync`
- `lizardfs`
- `make`
- `mfscachemode`
- `setup_local_empty_lizardfs`

Assertions and expectations include:
- `assert_program_installed git`
- `assert_program_installed cmake`
- `assert_program_installed rsync`
- `expect_files_equal "$file" "copy_$file"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 36 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_compilation_and_rsync.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_custom_goals_generate_no_accidental_rebalancing.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_custom_goals_generate_no_accidental_rebalancing.sh

## Purpose
This shell scenario exercises custom goal and label placement policy in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `custom goals generate no accidental rebalancing` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set "5 minutes"`
- `CHUNKSERVERS=6`
- `USE_LOOP_DISKS=YES`
- `CHUNKSERVER_LABELS="0:us|1,2,3:eu|4:au|5:cn"`
- `MASTER_CUSTOM_GOALS="1`
- `CHUNKSERVER_EXTRA_CONFIG="HDD_TEST_FREQ`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `MESSAGE="Step`
- `FILE_SIZE=1M`
- `MESSAGE=$'Status:\n'"$(status)"$'\nWaiting`
- `status() {`

External commands and harness APIs used by the scenario:
- `lizardfs-probe`
- `setup_local_empty_lizardfs`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_ready_chunkservers`
- `file-generate`

Assertions and expectations include:
- `assert_awk_finds_no '/cs.matocs.replicate/' "$(cat "$replication_log")"`
- `assert_eventually '[[ $(awk "/cs.matocs.replicate/" "$replication_log" | wc -l) != 0 ]]'`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 45 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for custom goal and label placement policy. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_custom_goals_generate_no_accidental_rebalancing.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_custom_goals_rebalancing_case_1.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_custom_goals_rebalancing_case_1.sh

## Purpose
This shell scenario exercises custom goal and label placement policy in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `custom goals rebalancing case 1` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set "6 minutes"`
- `CHUNKSERVERS=5`
- `USE_LOOP_DISKS=YES`
- `CHUNKSERVER_LABELS="0,1,2:ssd|3,4:hdd"`
- `MASTER_CUSTOM_GOALS="1`
- `CHUNKSERVER_EXTRA_CONFIG="PERFORM_FSYNC`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=1M`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_ready_chunkservers`
- `file-generate`
- `lizardfs_rebalancing_status`

Assertions and expectations include:
- `assert_eventually_prints "" "lizardfs_rebalancing_status | awk '\$2 < 90 || \$2 > 110'" "2 minutes"`
- `assert_eventually_prints "" "lizardfs_rebalancing_status | awk '\$2 < 70 || \$2 > 90'" "3 minutes"`
- `assert_awk_finds_no '$2 < 70 || $2 > 90' "$(lizardfs_rebalancing_status)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 33 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for custom goal and label placement policy. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_custom_goals_rebalancing_case_1.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_custom_goals_rebalancing_case_2.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_custom_goals_rebalancing_case_2.sh

## Purpose
This shell scenario exercises custom goal and label placement policy in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `custom goals rebalancing case 2` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set "10 minutes"`
- `CHUNKSERVERS=5`
- `USE_LOOP_DISKS=YES`
- `CHUNKSERVER_LABELS="0:A|1:B|2:C|3:D|4:E"`
- `MASTER_CUSTOM_GOALS="1`
- `CHUNKSERVER_EXTRA_CONFIG="PERFORM_FSYNC`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=1M`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_ready_chunkservers`
- `file-generate`
- `lizardfs_rebalancing_status`

Assertions and expectations include:
- `assert_eventually_prints "" "lizardfs_rebalancing_status | awk '\$2 < 90 || \$2 > 110'" "5 minutes"`
- `assert_eventually_prints "" "lizardfs_rebalancing_status | awk '\$2 < 70 || \$2 > 90'" "5 minutes"`
- `assert_awk_finds_no '$2 < 70 || $2 > 90' "$(lizardfs_rebalancing_status)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 34 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for custom goal and label placement policy. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_custom_goals_rebalancing_case_2.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_custom_goals_rebalancing_case_3.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_custom_goals_rebalancing_case_3.sh

## Purpose
This shell scenario exercises custom goal and label placement policy in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `custom goals rebalancing case 3` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set "6 minutes"`
- `CHUNKSERVERS=6`
- `USE_LOOP_DISKS=YES`
- `CHUNKSERVER_LABELS="0,1,2:eu|3,4,5:us"`
- `MASTER_CUSTOM_GOALS="5`
- `CHUNKSERVER_EXTRA_CONFIG="PERFORM_FSYNC`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=1M`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `lizardfs_rebalancing_status`

Assertions and expectations include:
- `assert_eventually_prints 3 "lizardfs_rebalancing_status | awk '/eu/ && \$2 > 0' | wc -l" "1 minute"`
- `assert_equals 3 $(lizardfs_rebalancing_status | awk '/us/ && $2 == 0' | wc -l)`
- `assert_eventually_prints "" "lizardfs_rebalancing_status | awk '\$2 < 40 || \$2 > 60'" "2 minutes"`
- `assert_awk_finds_no '$2 < 40 || $2 > 60' "$(lizardfs_rebalancing_status)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 34 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for custom goal and label placement policy. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_custom_goals_rebalancing_case_3.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_data_integrity.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_data_integrity.sh

## Purpose
This shell scenario exercises LongSystemTests scenario coverage for data integrity in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `data integrity` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 hour`
- `CHUNKSERVERS=3`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `test_worker() {`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `file-validate`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 53 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for LongSystemTests scenario coverage for data integrity. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_data_integrity.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_dbench.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_dbench.sh

## Purpose
This shell scenario exercises filesystem workload benchmarking in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `dbench` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 hour`
- `MESSAGE="Testing`
- `CHUNKSERVERS=3`
- `MOUNTS=1`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `dbench_tester() {`

External commands and harness APIs used by the scenario:
- `dbench`
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`

Assertions and expectations include:
- `assert_program_installed dbench`
- `MESSAGE="Testing directory $dir" expect_success dbench -s -S -t 1800 5`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 22 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for filesystem workload benchmarking. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_dbench.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_disk_to_delete_replication.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_disk_to_delete_replication.sh

## Purpose
This shell scenario exercises I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `disk to delete replication` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 2 minutes`
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=4`
- `DISK_PER_CHUNKSERVER=3`
- `CHUNKSERVER_EXTRA_CONFIG="HDD_TEST_FREQ`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=$size`
- `print_disks() {`
- `mark_disks() {`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs_chunkserver_daemon`
- `lizardfs`
- `file-generate`

Assertions and expectations include:
- `assert_less_or_equal 2 "$(ls $RAMDISK_DIR/hdd_${cs}_${disk}/*/* | wc -l)"`
- `assert_eventually_prints 0 "ls $RAMDISK_DIR/hdd_0_1/*/* | wc -l" "30 seconds"`
- `assert_equals 3 "$(lizardfs fileinfo $file | grep copy | wc -l)"`
- `assert_eventually_prints 0 "find_chunkserver_chunks 1 | wc -l" "60 seconds"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 97 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_disk_to_delete_replication.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_overwrite_file.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_overwrite_file.sh

## Purpose
This shell scenario exercises upgrade compatibility in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `lizardfs upgrade overwrite file` using a temporary cluster prepared by `tools/test_main.sh`. It delegates shared behavior through sourced helper/template files, so its effective test body includes those external harness fragments.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `MOOSEFS_CHUNK_FORMAT="0"`
- `GOAL=ec21`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 3 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- `source test_suites/TestTemplates/test_lizardfs_upgrade_overwrite_file.inc`

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for upgrade compatibility. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_overwrite_file.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_overwrite_file_legacy_chunkformat.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_overwrite_file_legacy_chunkformat.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, upgrade compatibility in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `lizardfs upgrade overwrite file legacy chunkformat` using a temporary cluster prepared by `tools/test_main.sh`. It delegates shared behavior through sourced helper/template files, so its effective test body includes those external harness fragments.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `MOOSEFS_CHUNK_FORMAT="1"`
- `GOAL=ec21`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 3 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- `source test_suites/TestTemplates/test_lizardfs_upgrade_overwrite_file.inc`

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, upgrade compatibility. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_overwrite_file_legacy_chunkformat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_undergoal_chunks_ec21.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_undergoal_chunks_ec21.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, EC goal behavior, upgrade compatibility in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `lizardfs upgrade undergoal chunks ec21` using a temporary cluster prepared by `tools/test_main.sh`. It delegates shared behavior through sourced helper/template files, so its effective test body includes those external harness fragments.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `MOOSEFS_CHUNK_FORMAT="0"`
- `GOAL="ec21"`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 3 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- `source test_suites/TestTemplates/test_lizardfs_upgrade_undergoal_chunks.inc`

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, EC goal behavior, upgrade compatibility. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_undergoal_chunks_ec21.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_undergoal_chunks_ec21_legacy_chunkformat.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_undergoal_chunks_ec21_legacy_chunkformat.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, EC goal behavior, upgrade compatibility in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `lizardfs upgrade undergoal chunks ec21 legacy chunkformat` using a temporary cluster prepared by `tools/test_main.sh`. It delegates shared behavior through sourced helper/template files, so its effective test body includes those external harness fragments.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `MOOSEFS_CHUNK_FORMAT="1"`
- `GOAL="ec21"`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 3 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- `source test_suites/TestTemplates/test_lizardfs_upgrade_undergoal_chunks.inc`

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, EC goal behavior, upgrade compatibility. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_undergoal_chunks_ec21_legacy_chunkformat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_undergoal_chunks_ec32.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_undergoal_chunks_ec32.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, EC goal behavior, upgrade compatibility in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `lizardfs upgrade undergoal chunks ec32` using a temporary cluster prepared by `tools/test_main.sh`. It delegates shared behavior through sourced helper/template files, so its effective test body includes those external harness fragments.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `MOOSEFS_CHUNK_FORMAT="0"`
- `GOAL="ec32"`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 3 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- `source test_suites/TestTemplates/test_lizardfs_upgrade_undergoal_chunks.inc`

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, EC goal behavior, upgrade compatibility. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_undergoal_chunks_ec32.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_undergoal_chunks_ec32_legacy_chunkformat.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_undergoal_chunks_ec32_legacy_chunkformat.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, EC goal behavior, upgrade compatibility in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `lizardfs upgrade undergoal chunks ec32 legacy chunkformat` using a temporary cluster prepared by `tools/test_main.sh`. It delegates shared behavior through sourced helper/template files, so its effective test body includes those external harness fragments.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `MOOSEFS_CHUNK_FORMAT="1"`
- `GOAL="ec32"`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 3 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- `source test_suites/TestTemplates/test_lizardfs_upgrade_undergoal_chunks.inc`

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, EC goal behavior, upgrade compatibility. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_lizardfs_upgrade_undergoal_chunks_ec32_legacy_chunkformat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_polonaise.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_polonaise.sh

## Purpose
This shell scenario exercises LongSystemTests scenario coverage for polonaise in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `polonaise` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set '30 minutes'`
- `CHUNKSERVERS=1`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `MINIMUM_PARALLEL_JOBS=4`
- `MAXIMUM_PARALLEL_JOBS=16`
- `PARALLEL_JOBS=$(get_nproc_clamped_between`

External commands and harness APIs used by the scenario:
- `git`
- `cmake`
- `lizardfs-polonaise-server`
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `mfspolon`
- `lizardfs`
- `make`

Assertions and expectations include:
- `assert_program_installed git`
- `assert_program_installed cmake`
- `assert_program_installed lizardfs-polonaise-server`
- `assert_program_installed polonaise-fuse-client`
- `assert_eventually 'lizardfs dirinfo "$mnt"'`
- `assert_success git clone https://github.com/lizardfs/lizardfs.git`
- `assert_success cmake .. -DCMAKE_INSTALL_PREFIX="$mnt"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 34 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for LongSystemTests scenario coverage for polonaise. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_polonaise.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_punching_holes.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_punching_holes.sh

## Purpose
This shell scenario exercises LongSystemTests scenario coverage for punching holes in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `punching holes` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=1`
- `CHUNKSERVER_EXTRA_CONFIG="HDD_PUNCH_HOLES`
- `test_fallocate() {`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `dd`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 47 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for LongSystemTests scenario coverage for punching holes. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_punching_holes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_overwriting_faulty_chunkservers.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_overwriting_faulty_chunkservers.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, XOR erasure-coded data behavior in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `xor overwriting faulty chunkservers` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `FAULTY_CHUNKSERVERS=YES`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 1 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, XOR erasure-coded data behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_overwriting_faulty_chunkservers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_overwriting_faulty_master.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_overwriting_faulty_master.sh

## Purpose
This shell scenario exercises XOR erasure-coded data behavior in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `xor overwriting faulty master` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `FAULTY_MASTER=YES`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 1 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for XOR erasure-coded data behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_overwriting_faulty_master.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_overwriting_faulty_master_and_chunkservers.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_overwriting_faulty_master_and_chunkservers.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, XOR erasure-coded data behavior in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `xor overwriting faulty master and chunkservers` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `FAULTY_MASTER=YES`
- `FAULTY_CHUNKSERVERS=YES`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 2 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, XOR erasure-coded data behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_overwriting_faulty_master_and_chunkservers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_reading_consistency_faulty_chunkservers.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_reading_consistency_faulty_chunkservers.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, XOR erasure-coded data behavior in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `xor reading consistency faulty chunkservers` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `FAULTY_CHUNKSERVERS=YES`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 1 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, XOR erasure-coded data behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_reading_consistency_faulty_chunkservers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_reading_consistency_faulty_master.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_reading_consistency_faulty_master.sh

## Purpose
This shell scenario exercises XOR erasure-coded data behavior in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `xor reading consistency faulty master` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `FAULTY_MASTER=YES`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 1 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for XOR erasure-coded data behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_reading_consistency_faulty_master.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_reading_consistency_faulty_master_and_chunkservers.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_reading_consistency_faulty_master_and_chunkservers.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, XOR erasure-coded data behavior in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `xor reading consistency faulty master and chunkservers` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `FAULTY_MASTER=YES`
- `FAULTY_CHUNKSERVERS=YES`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 2 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, XOR erasure-coded data behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_reading_consistency_faulty_master_and_chunkservers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_writing_faulty_chunkservers.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_writing_faulty_chunkservers.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, XOR erasure-coded data behavior in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `xor writing faulty chunkservers` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `FAULTY_CHUNKSERVERS=YES`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 1 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, XOR erasure-coded data behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_writing_faulty_chunkservers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_writing_faulty_master.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_writing_faulty_master.sh

## Purpose
This shell scenario exercises XOR erasure-coded data behavior in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `xor writing faulty master` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `FAULTY_MASTER=YES`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 1 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for XOR erasure-coded data behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_writing_faulty_master.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_writing_faulty_master_and_chunkservers.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_writing_faulty_master_and_chunkservers.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, XOR erasure-coded data behavior in the LizardFS bash test harness. The script is part of `LongSystemTests` and focuses on `xor writing faulty master and chunkservers` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `FAULTY_MASTER=YES`
- `FAULTY_CHUNKSERVERS=YES`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 2 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, XOR erasure-coded data behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/LongSystemTests/test_xor_writing_faulty_master_and_chunkservers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_acl_group_class.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_acl_group_class.sh

## Purpose
This shell scenario exercises ACL and permission semantics in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `acl group class` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`

External commands and harness APIs used by the scenario:
- `setfacl`
- `setup_local_empty_lizardfs`
- `getfacl`

Assertions and expectations include:
- `assert_program_installed setfacl`
- `assert_equals '-rwxr-x---' "$mask"`
- `assert_awk_finds '/^user::rwx$/' "$acls"`
- `assert_awk_finds '/^group::r-x$/' "$acls"`
- `assert_awk_finds '/^other::---$/' "$acls"`
- `assert_awk_finds_no '/^mask:/' "$acls"`
- `assert_equals "-rwxr-xr--" "$mask"`
- `assert_awk_finds '/^other::r--$/' "$acls"`
- `assert_equals "-rwxrwxr--" "$mask"`
- `assert_awk_finds '/^group:fuse:rwx$/' "$acls"`
- `assert_awk_finds '/^mask::rwx$/' "$acls"`
- `assert_equals "-rwx------" "$mask"`
- `assert_awk_finds '/^mask::---$/' "$acls"`
- `expect_equals "$(getfacl -cE file | sort)" "$(getfacl -cE copy | sort)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 63 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ACL and permission semantics. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_acl_group_class.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_cgi_using_pylint.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_cgi_using_pylint.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for cgi using pylint in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `cgi using pylint` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- No top-level timeout, uppercase harness assignment, or local shell function was detected.

External commands and harness APIs used by the scenario:
- `mfscgi`
- `lizardfs-cgiserver`

Assertions and expectations include:
- `expect_empty "$($pylintexec -E $files || true)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 13 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for cgi using pylint. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_cgi_using_pylint.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_chunk_replication.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_chunk_replication.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `chunk replication` using a temporary cluster prepared by `tools/test_main.sh`. It delegates shared behavior through sourced helper/template files, so its effective test body includes those external harness fragments.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- No top-level timeout, uppercase harness assignment, or local shell function was detected.

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 7 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- `source $(readlink -m test_suites/ShortSystemTests/test_chunk_replication.sh)`

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_chunk_replication.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_chunk_type_conversion.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_chunk_type_conversion.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `chunk type conversion` using a temporary cluster prepared by `tools/test_main.sh`. It delegates shared behavior through sourced helper/template files, so its effective test body includes those external harness fragments.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 60 seconds`
- `WAIT_FOR_REPLICATION=40`
- `NUMBER_OF_CHUNKSERVERS=4`
- `GOALS_TO_BE_TESTED="2`
- `VERIFY_FILE_CONTENT=NO`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 7 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- `source test_suites/TestTemplates/test_chunk_type_conversion.inc`

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_chunk_type_conversion.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_chunk_version_change.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_chunk_version_change.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `chunk version change` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=1`
- `DISK_PER_CHUNKSERVER=1`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=123456`
- `FILE_SIZE=234567`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `file-generate`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `dd`
- `file-validate`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 28 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_chunk_version_change.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_code_style.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_code_style.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for code style in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `code style` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 minute`
- `verify_file() {`

External commands and harness APIs used by the scenario:
- `git`
- `cmake`
- `mfs`
- `lizardfs_c_api`
- `lizardfs_error_codes`

Assertions and expectations include:
- `assert_program_installed python3`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 70 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for code style. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_code_style.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_crc_error_fixing.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_crc_error_fixing.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for crc error fixing in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `crc error fixing` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=4`
- `USE_RAMDISK="yes"`
- `MOUNT_EXTRA_CONFIG="mfscachemode=never"`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `CHUNKSERVER_EXTRA_CONFIG="HDD_TEST_FREQ`
- `FILE_SIZE=1234567`
- `MESSAGE="Reading`
- `get_damaged_area() {`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `dd`
- `lizardfs`
- `file-generate`
- `file-validate`

Assertions and expectations include:
- `assert_equals 4 $(lizardfs fileinfo file | grep -c copy)`
- `assert_equals 1 $(wc -l <<< "$chunk")`
- `MESSAGE="Reading file with corrupted chunk" expect_success file-validate file`
- `assert_success wait_for '[[ $(get_damaged_area "$chunk") == $correct_data ]]' "25 seconds"`
- `assert_success wait_for '[[ $(lizardfs fileinfo file | grep -c copy) == 4 ]]' "5 seconds"`
- `MESSAGE="Reading file with fixed chunk" expect_success file-validate file`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 40 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for crc error fixing. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_crc_error_fixing.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_data_generator.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_data_generator.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for data generator in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `data generator` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 2 minutes`
- `FILE_SIZE=64`
- `SEED=997`
- `SEED=666`
- `SEED=42`
- `SEED=2137`

External commands and harness APIs used by the scenario:
- `file-generate`
- `file-overwrite`
- `file-validate`
- `file-validate-growing`

Assertions and expectations include:
- `assert_failure diff file_seed666 file_seed42`
- `assert_failure diff file_seed666 copied_file`
- `SEED=666 assert_success file-validate file_seed666`
- `SEED=997 assert_success file-validate copied_file`
- `SEED=42  assert_success file-validate file_seed42`
- `SEED=997 assert_failure file-validate file_seed666`
- `SEED=2137 assert_success file-validate-growing big_file $big_size`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 23 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for data generator. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_data_generator.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_dirinfo.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_dirinfo.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for dirinfo in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `dirinfo` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=4`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `USE_RAMDISK=YES`
- `MESSAGE="$field`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `dd`
- `mfs_dir_info`

Assertions and expectations include:
- `MESSAGE="$field for $file mismatch" expect_equals "$expected" "$actual"`
- `MESSAGE="$field for directory mismatch" expect_equals $fieldsum $(mfs_dir_info "$field" dir)`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 98 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for dirinfo. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_dirinfo.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_ec_read_data_corrupted.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_ec_read_data_corrupted.sh

## Purpose
This shell scenario exercises EC goal behavior in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `ec read data corrupted` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 45 seconds`
- `CHUNKSERVERS=4`
- `DISK_PER_CHUNKSERVER=1`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `USE_RAMDISK=YES`
- `FILE_SIZE=6M`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `dd`
- `file-validate`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 28 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_ec_read_data_corrupted.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_ec_read_from_parity.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_ec_read_from_parity.sh

## Purpose
This shell scenario exercises EC goal behavior in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `ec read from parity` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=4`
- `DISK_PER_CHUNKSERVER=1`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `USE_RAMDISK=YES`
- `FILE_SIZE=6M`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `lizardfs_chunkserver_daemon`
- `file-validate`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 22 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_ec_read_from_parity.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_ec_read_parity_corrupted.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_ec_read_parity_corrupted.sh

## Purpose
This shell scenario exercises EC goal behavior in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `ec read parity corrupted` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=4`
- `DISK_PER_CHUNKSERVER=1`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `USE_RAMDISK=YES`
- `FILE_SIZE=6M`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `dd`
- `file-validate`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 26 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_ec_read_parity_corrupted.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_ec_write_corrupted.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_ec_write_corrupted.sh

## Purpose
This shell scenario exercises EC goal behavior in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `ec write corrupted` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=4`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `USE_RAMDISK=YES`
- `MESSAGE="Overwriting`
- `MESSAGE="Validating`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `lizardfs_chunkserver_daemon`
- `file-overwrite`
- `file-validate`
- `lizardfs_wait_for_all_ready_chunkservers`

Assertions and expectations include:
- `MESSAGE="Overwriting $file" expect_success file-overwrite $file`
- `MESSAGE="Validating overwritten file" expect_success file-validate $file`
- `MESSAGE="Validating $file after restart" expect_success file-validate $file`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 33 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_ec_write_corrupted.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_fileinfo.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_fileinfo.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for fileinfo in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `fileinfo` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=5`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `CHUNKSERVER_EXTRA_CONFIG="CREATE_NEW_CHUNKS_IN_MOOSEFS_FORMAT=0"`
- `USE_RAMDISK=YES`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `dd`

Assertions and expectations include:
- `expect_equals "$chunks_real" "$chunks_info"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 66 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for fileinfo. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_fileinfo.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_goals.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_goals.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for goals in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `goals` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=3`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `FILE_SIZE=12345678`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `file-validate`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 18 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for goals. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_goals.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_liblizardfs_client_example.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_liblizardfs_client_example.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for liblizardfs client example in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `liblizardfs client example` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=1`
- `USE_RAMDISK=YES`
- `MOUNTS=0`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`

Assertions and expectations include:
- `assert_success c-client-example ${info[matocl]}`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 6 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for liblizardfs client example. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_liblizardfs_client_example.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_petabyte_file.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_petabyte_file.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for petabyte file in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `petabyte file` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=2`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `mfs_dir_info`

Assertions and expectations include:
- `assert_equals $(parse_si_suffix 1P) $(stat --format="%s" petabyte_sparse_file)`
- `expect_equals 0 $(mfs_dir_info realsize petabyte_sparse_file)`
- `expect_equals "LizardFS.org" $(tail -c12 petabyte_sparse_file)`
- `expect_less_or_equal $(mfs_dir_info realsize petabyte_sparse_file) $LIZARDFS_CHUNK_SIZE`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 16 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for petabyte file. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_petabyte_file.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_quota_size.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_quota_size.sh

## Purpose
This shell scenario exercises quota accounting in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `quota size` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 45 seconds`
- `USE_RAMDISK=YES`
- `MFSEXPORTS_EXTRA_OPTIONS="allcanchangequota,ignoregid"`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfstest_1`
- `lizardfstest`
- `lizardfstest_3`
- `mfs_dir_info`
- `lizardfs`
- `dd`

Assertions and expectations include:
- `expect_failure sudo -nu lizardfstest_1 bash -c 'head -c 1024 /dev/zero > file_4'`
- `assert_equals "$(stat --format=%s file_4)" 0 # file was created, but no data was written`
- `expect_failure sudo -nu lizardfstest_1 bash -c 'head -c $((64*1024*1024)) /dev/zero >> file_1'`
- `expect_failure sudo -nu lizardfstest_1 dd if=/dev/zero of=file_2 bs=1M seek=64 count=1 conv=notrunc`
- `expect_failure lizardfs makesnapshot file_2 snapshot_3`
- `expect_failure sudo -nu lizardfstest_1 dd if=/dev/zero of=snapshot_2 bs=1k count=1 conv=notrunc`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 80 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for quota accounting. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_quota_size.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_read_cache_consistency.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_read_cache_consistency.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for read cache consistency in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `read cache consistency` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 70 seconds`
- `CHUNKSERVERS=4`
- `USE_RAMDISK=YES`
- `MOUNTS=2`
- `MOUNT_EXTRA_CONFIG="cacheexpirationtime=10000"`
- `FILE_SIZE=32M`
- `repeated_validate() {`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `file-validate`
- `file-generate`
- `dd`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 46 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for read cache consistency. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_read_cache_consistency.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_read_corrupted_file_with_goal_9.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_read_corrupted_file_with_goal_9.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for read corrupted file with goal 9 in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `read corrupted file with goal 9` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=9`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `CHUNKSERVER_EXTRA_CONFIG="HDD_TEST_FREQ`
- `USE_RAMDISK=YES`
- `FILE_SIZE=1234567`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `dd`
- `file-validate`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 25 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for read corrupted file with goal 9. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_read_corrupted_file_with_goal_9.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_readdir_faulty_master.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_readdir_faulty_master.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for readdir faulty master in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `readdir faulty master` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 minute`
- `CHUNKSERVERS=1`
- `USE_RAMDISK=YES`
- `FILE_COUNT=200`
- `MASTER_CFG_FILE="${info[master${info[current_master]}_cfg]}"`
- `FILES_ITERATED=$(python3`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `mfsmaster`

Assertions and expectations include:
- `assert_equals $FILE_COUNT $FILES_ITERATED`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 26 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for readdir faulty master. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_readdir_faulty_master.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_set_get_goal.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_set_get_goal.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for set get goal in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `set get goal` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=1`
- `USE_RAMDISK=YES`
- `MASTER_CUSTOM_GOALS="8`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs`

Assertions and expectations include:
- `assert_equals "directory: $new_goal" "$(lizardfs setgoal "$new_goal" directory || echo FAILED)"`
- `assert_equals "directory: $new_goal" "$(lizardfs getgoal directory || echo FAILED)"`
- `assert_success lizardfs setgoal $goal directory/file$goal`
- `assert_equals "directory/file$goal: $goal" "$(lizardfs getgoal directory/file$goal)"`
- `assert_success lizardfs setgoal 3 directory/file{2..3}`
- `expect_equals $'directory/file2: 3\ndirectory/file3: 3' "$(lizardfs getgoal directory/file{2..3})"`
- `assert_success lizardfs setgoal -r 3 directory`
- `expect_equals "directory/file2: 3" "$(lizardfs getgoal directory/file2)"`
- `expect_equals "directory/file3: 3" "$(lizardfs getgoal directory/file3)"`
- `expect_equals "directory/file5: 3" "$(lizardfs getgoal directory/file5)"`
- `expect_equals "directory/fileX: 3" "$(lizardfs getgoal directory/fileX)"`
- `expect_equals "directory/filexor2: 3" "$(lizardfs getgoal directory/filexor2)"`
- `expect_equals "directory/filexor5: 3" "$(lizardfs getgoal directory/filexor5)"`
- `expect_equals "directory/filexor7: 3" "$(lizardfs getgoal directory/filexor7)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 61 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for set get goal. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_set_get_goal.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_simultaneous_write_read.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_simultaneous_write_read.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for simultaneous write read in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `simultaneous write read` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 3 minutes`
- `CHUNKSERVERS=4`
- `USE_RAMDISK=YES`
- `FILE_SIZE=100000000`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `file-generate`
- `file-validate-growing`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 17 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for simultaneous write read. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_simultaneous_write_read.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_snapshot.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_snapshot.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for snapshot in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `snapshot` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=4`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER,mfsdirentrycacheto=0"`
- `FILE_SIZE=1M`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `mfsdirentrycacheto`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `file-validate`
- `dd`
- `file-overwrite`

Assertions and expectations include:
- `assert_success file-validate file*`
- `assert_equals 6 $(find_all_chunks | wc -l)`
- `assert_success file-validate file1* file2_snapshot*`
- `assert_equals 10 $(find_all_chunks | wc -l)`
- `assert_equals 14 $(find_all_chunks | wc -l)`
- `assert_equals 16 $(find_all_chunks | wc -l)`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 42 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for snapshot. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_snapshot.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_sparse_file.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_sparse_file.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for sparse file in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `sparse file` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=1`
- `USE_RAMDISK=YES`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `dd`
- `mfs_dir_info`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 28 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for sparse file. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_sparse_file.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_valgrind.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_valgrind.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for valgrind in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `valgrind` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=1`
- `MOUNTS=${number_of_mounts}`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `FILE_SIZE=8M`
- `MESSAGE="Validating`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `dd`
- `file-generate`
- `file-validate`
- `lizardfs_master_daemon`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `lizardfs_mount_unmount_async`
- `lizardfstest`
- `mfsmount`

Assertions and expectations include:
- `MESSAGE="Validating $mnt1dir2/file2" expect_success file-validate "$mnt1dir2/file2" &`
- `MESSAGE="Validating $mnt0dir2/file2" expect_success file-validate "$mnt0dir2/file2" &`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 50 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for valgrind. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_valgrind.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_wireshark_plugin_generation.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_wireshark_plugin_generation.sh

## Purpose
This shell scenario exercises I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `wireshark plugin generation` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- No top-level timeout, uppercase harness assignment, or local shell function was detected.

External commands and harness APIs used by the scenario:
- `lizardfs`

Assertions and expectations include:
- `assert_success lizardfs/generate.sh "$SOURCE_DIR/src/protocol/MFSCommunication.h"`
- `assert_success test -s lizardfs/packet-lizardfs.c`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 10 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_wireshark_plugin_generation.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_write_and_read.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_write_and_read.sh

## Purpose
This shell scenario exercises SanityChecks scenario coverage for write and read in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `write and read` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 70 seconds`
- `CHUNKSERVERS=23`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `CHUNKSERVER_EXTRA_CONFIG="READ_AHEAD_KB`
- `MASTER_CUSTOM_GOALS="8`
- `FILE_SIZE=123456789`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `file-generate`
- `file-validate`
- `lizardfs`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 37 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for SanityChecks scenario coverage for write and read. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_write_and_read.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_xor_read_from_parity.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_xor_read_from_parity.sh

## Purpose
This shell scenario exercises XOR erasure-coded data behavior in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `xor read from parity` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=4`
- `DISK_PER_CHUNKSERVER=1`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `USE_RAMDISK=YES`
- `FILE_SIZE=6M`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `lizardfs_chunkserver_daemon`
- `file-validate`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 18 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for XOR erasure-coded data behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_xor_read_from_parity.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_xor_read_parity_corrupted.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_xor_read_parity_corrupted.sh

## Purpose
This shell scenario exercises XOR erasure-coded data behavior in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `xor read parity corrupted` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=4`
- `DISK_PER_CHUNKSERVER=1`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `USE_RAMDISK=YES`
- `FILE_SIZE=6M`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `dd`
- `file-validate`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 20 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for XOR erasure-coded data behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_xor_read_parity_corrupted.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_xor_read_part_1_corrupted.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_xor_read_part_1_corrupted.sh

## Purpose
This shell scenario exercises XOR erasure-coded data behavior in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `xor read part 1 corrupted` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 45 seconds`
- `CHUNKSERVERS=4`
- `DISK_PER_CHUNKSERVER=1`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `USE_RAMDISK=YES`
- `FILE_SIZE=6M`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `dd`
- `file-validate`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 22 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for XOR erasure-coded data behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_xor_read_part_1_corrupted.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_xor_write_corrupted.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_xor_write_corrupted.sh

## Purpose
This shell scenario exercises XOR erasure-coded data behavior in the LizardFS bash test harness. The script is part of `SanityChecks` and focuses on `xor write corrupted` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=4`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `USE_RAMDISK=YES`
- `MESSAGE="Overwriting`
- `MESSAGE="Validating`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `lizardfs_chunkserver_daemon`
- `file-overwrite`
- `file-validate`
- `lizardfs_wait_for_all_ready_chunkservers`

Assertions and expectations include:
- `MESSAGE="Overwriting $file" expect_success file-overwrite $file`
- `MESSAGE="Validating overwritten file" expect_success file-validate $file`
- `MESSAGE="Validating $file after restart" expect_success file-validate $file`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 30 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for XOR erasure-coded data behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/SanityChecks/test_xor_write_corrupted.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_acl_behavior.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_acl_behavior.sh

## Purpose
This shell scenario exercises ACL and permission semantics, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `acl behavior` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 2 minutes`
- `MESSAGE="Testing`
- `USE_RAMDISK=YES`

External commands and harness APIs used by the scenario:
- `setfacl`
- `setup_local_empty_lizardfs`
- `lizardfs_master_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `getfacl`
- `lizardfstest`

Assertions and expectations include:
- `assert_program_installed setfacl`
- `MESSAGE="Testing ACL support in $TEMP_DIR/" assert_success setfacl -m group:fuse:rw "$TEMP_DIR/f"`
- `assert_equals "$(stat --format=%A "$tmpdir/$f")" "$(stat --format=%A "$lizdir/$f")"`
- `assert_equals "$(getfacl -cpE "$tmpdir/$f" | sort)" "$(getfacl -cpE "$lizdir/$f" | sort)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 126 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ACL and permission semantics, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_acl_behavior.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_acl_cache.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_acl_cache.sh

## Purpose
This shell scenario exercises ACL and permission semantics in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `acl cache` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=1`
- `USE_RAMDISK=YES`
- `MFSEXPORTS_EXTRA_OPTIONS=nomasterpermcheck,ignoregid`
- `MASTER_EXTRA_CONFIG="MAGIC_DEBUG_LOG`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER|mfsaclcachesize=2|mfsaclcacheto=5.0|mfsattrcacheto=50"`
- `count_misses() {`
- `check_misses() {`
- `function get_facl() {`

External commands and harness APIs used by the scenario:
- `setfacl`
- `getfacl`
- `lizardfstest_1`
- `lizardfstest_4`
- `lizardfstest_2`
- `lizardfstest_5`
- `lizardfstest_3`
- `lizardfstest_6`
- `mfscachemode`
- `mfsaclcachesize`
- `mfsaclcacheto`
- `mfsattrcacheto`
- `setup_local_empty_lizardfs`

Assertions and expectations include:
- `assert_program_installed setfacl getfacl`
- `assert_equals "$1" "$(count_misses file1)"`
- `assert_equals "$2" "$(count_misses file2)"`
- `assert_equals "$3" "$(count_misses file3)"`
- `assert_equals "$(get_facl file1)" "$file1_acl"`
- `assert_equals "$(get_facl file2)" "$file2_acl"`
- `assert_equals "$(get_facl file3)" "$file3_acl"`
- `assert_equals "$(get_facl file1)" "user::rw- group::rw- other::-wx"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 71 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ACL and permission semantics. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_acl_cache.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_admin_magic_recalculate_metadata_checksum.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_admin_magic_recalculate_metadata_checksum.sh

## Purpose
This shell scenario exercises EC goal behavior, metadata persistence in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `admin magic recalculate metadata checksum` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=1`
- `USE_RAMDISK="YES"`
- `MASTER_EXTRA_CONFIG="$master_cfg"`
- `ADMIN_PASSWORD="pass"`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_info_`
- `lizardfs-admin`

Assertions and expectations include:
- `assert_failure lizardfs-admin magic-recalculate-metadata-checksum localhost "$port" <<< "no-pass"`
- `assert_equals 0 $(grep updater_end "$TEMP_DIR/log" | wc -l)`
- `assert_equals 0 $(grep updater_start "$TEMP_DIR/log" | wc -l)`
- `time assert_success lizardfs-admin magic-recalculate-metadata-checksum localhost "$port" <<< "pass"`
- `assert_equals 1 $(echo "$log_data" | grep updater_end | wc -l)`
- `assert_equals 1 $(echo "$log_data" | grep updater_start | wc -l)`
- `time assert_success lizardfs-admin magic-recalculate-metadata-checksum localhost "$port" --async <<< "pass"`
- `assert_equals 2 $(echo "$log_data" | grep updater_start | wc -l)`
- `assert_eventually_prints 2 'grep updater_end "$TEMP_DIR/log" | wc -l'`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 39 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for EC goal behavior, metadata persistence. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_admin_magic_recalculate_metadata_checksum.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_admin_reload_config.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_admin_reload_config.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for admin reload config in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `admin reload config` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK="YES"`
- `ADMIN_PASSWORD="$password"`
- `MASTER_EXTRA_CONFIG="MAGIC_DEBUG_LOG=${reload_log}|LOG_FLUSH_ON=DEBUG"`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_info_`
- `lizardfs-admin`
- `lizardfs_master_daemon`

Assertions and expectations include:
- `assert_equals 0 $(grep main.reload "$reload_log" | wc -l)`
- `assert_failure lizardfs-admin reload-config localhost "$master_port" <<< "wrong-password"`
- `assert_success lizardfs-admin reload-config localhost "$master_port" <<< "$password"`
- `assert_eventually_prints 1 'grep main.reload "$reload_log" | wc -l'`
- `assert_eventually_prints 2 'grep main.reload "$reload_log" | wc -l'`
- `assert_eventually_prints 3 'grep main.reload "$reload_log" | wc -l'`
- `assert_success lizardfs-admin reload-config localhost "$shadow_port" <<< "$password"`
- `assert_eventually_prints 4 'grep main.reload "$reload_log" | wc -l'`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 33 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for admin reload config. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_admin_reload_config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_admin_save_metadata.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_admin_save_metadata.sh

## Purpose
This shell scenario exercises metadata persistence in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `admin save metadata` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=1`
- `USE_RAMDISK="YES"`
- `MASTER_EXTRA_CONFIG="$master_cfg"`
- `ADMIN_PASSWORD="pass"`
- `count_metadata_files() {`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_info_`
- `mfsmetarestore`
- `make`
- `lizardfs-admin`
- `lizardfs_admin_master`

Assertions and expectations include:
- `expect_equals 2 $(count_metadata_files) # 'MFSM NEW' and it's binary form`
- `assert_failure lizardfs-admin save-metadata localhost "$port" <<< "no-pass"`
- `assert_equals 2 $(count_metadata_files)`
- `assert_file_not_exists "$TEMP_DIR/dump_started"`
- `assert_success lizardfs-admin save-metadata localhost "$port" <<< "pass"`
- `assert_file_exists "$TEMP_DIR/dump_finished"`
- `assert_equals 3 $(count_metadata_files)`
- `assert_success lizardfs-admin save-metadata localhost "$port" --async <<< "pass"`
- `assert_file_not_exists "$TEMP_DIR/dump_finished"`
- `assert_failure lizardfs-admin save-metadata localhost "$port" --async <<< "pass"`
- `assert_failure lizardfs-admin save-metadata localhost "$port" <<< "pass"`
- `assert_eventually_prints 4 'count_metadata_files'`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 70 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for metadata persistence. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_admin_save_metadata.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_admin_stop_master.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_admin_stop_master.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for admin stop master in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `admin stop master` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `MASTERSERVERS=2`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_master_n`
- `lizardfs-admin`
- `lizardfs_probe_master`
- `lizardfs_master_daemon`
- `mfs`
- `lizardfs_shadow_synchronized`

Assertions and expectations include:
- `assert_failure lizardfs-admin stop-master-without-saving-metadata \`
- `assert_success lizardfs-admin stop-master-without-saving-metadata \`
- `assert_eventually "! lizardfs_master_daemon isalive"`
- `assert_file_exists "$lockfile"`
- `assert_equals "quick_stop: $last_metadata_version" "$(cat "$lockfile")"`
- `assert_failure lizardfs_master_n 0 start`
- `assert_success lizardfs_master_n 0 start -o auto-recovery`
- `assert_eventually "lizardfs_shadow_synchronized 1"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 31 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for admin stop master. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_admin_stop_master.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_metarestore.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_metarestore.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for auto metarestore in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `auto metarestore` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 3 minutes`
- `USE_RAMDISK=YES`
- `MESSAGE="Veryfing`
- `verify_recovery() {`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs`
- `mfsmetalogger`
- `lizardfs_metalogger_daemon`
- `lizardfs_master_daemon`
- `mfs`
- `metadata_ml`
- `mfsmetarestore`
- `dd`

Assertions and expectations include:
- `expect_equals 100 $(ls "${info[mount0]}" | wc -l)`
- `expect_success lizardfs_master_daemon kill`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 75 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for auto metarestore. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_metarestore.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_freeinodes.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_freeinodes.sh

## Purpose
This shell scenario exercises metadata auto-recovery, EC goal behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `auto recovery freeinodes` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 minute`
- `CHUNKSERVERS=1`
- `MOUNTS=1`
- `USE_RAMDISK="YES"`
- `MOUNT_0_EXTRA_CONFIG="mfscachemode=NEVER,mfsattrcacheto=0,mfsreportreservedperiod=1"`
- `MFSEXPORTS_EXTRA_OPTIONS="allcanchangequota"`
- `MASTER_EXTRA_CONFIG="$master_cfg"`
- `AUTO_SHADOW_MASTER="NO"`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `mfsattrcacheto`
- `mfsreportreservedperiod`
- `setup_local_empty_lizardfs`
- `mfs`
- `metadata_file`
- `metadata_version`
- `metadata_get_version`
- `lizardfs`
- `lizardfs_master_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `metadata_print`

Assertions and expectations include:
- `assert_eventually '[[ $(grep RELEASE "$changelog_file" | wc -l) == 100 ]]'`
- `assert_equals "$metadata_version" "$(metadata_get_version "$metadata_file")"`
- `assert_success lizardfs_master_daemon start`
- `assert_less_than "$metadata_version" "$new_metadata_version"`
- `assert_awk_finds_no '/CREATE.*:20$/' "$(cat "$changelog_file")"`
- `assert_awk_finds    '/CREATE.*:20$/' "$(cat "$changelog_file")" # Make sure that inode 20 was reused`
- `assert_equals "$new_metadata_version" "$(metadata_get_version "$metadata_file")"`
- `assert_no_diff "$metadata" "$(metadata_print "${info[mount0]}")"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 55 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for metadata auto-recovery, EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_freeinodes.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_incversion.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_incversion.sh

## Purpose
This shell scenario exercises metadata auto-recovery, EC goal behavior, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `auto recovery incversion` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=2`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `MFSEXPORTS_EXTRA_OPTIONS="allcanchangequota"`
- `CHUNKSERVER_EXTRA_CONFIG="HDD_TEST_FREQ`
- `MASTER_EXTRA_CONFIG="$master_cfg"`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `metadata_version`
- `metadata_get_version`
- `mfs`
- `lizardfs`
- `make`
- `metadata_print`
- `lizardfs_master_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`

Assertions and expectations include:
- `assert_equals 1 $(find_chunkserver_chunks 0 | wc -l)`
- `assert_equals 1 $(find_chunkserver_chunks 1 | wc -l)`
- `assert_success rm "$chunk"`
- `assert_awk_finds '/INCVERSION/' "$(cat "${info[master_data_path]}"/changelog.mfs)"`
- `assert_equals "$metadata_version" "$(metadata_get_version "${info[master_data_path]}"/metadata.mfs)"`
- `assert_success lizardfs_master_daemon start`
- `assert_no_diff "$metadata" "$(metadata_print)"`
- `assert_equals "a" "$(cat dir/file)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 45 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for metadata auto-recovery, EC goal behavior, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_incversion.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_metarestore_while_starting.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_metarestore_while_starting.sh

## Purpose
This shell scenario exercises metadata auto-recovery, EC goal behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `auto recovery metarestore while starting` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=0`
- `USE_RAMDISK=YES`
- `MASTER_EXTRA_CONFIG="AUTO_RECOVERY`
- `MOUNTS=0`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_master_daemon`
- `metadata_get_version`
- `mfs`
- `mfsmetarestore`
- `lizardfs-probe`

Assertions and expectations include:
- `assert_equals 1 $(metadata_get_version "${info[master_data_path]}/metadata.mfs")`
- `assert_eventually 'test -e "${info[master_data_path]}/metadata.mfs.lock"'`
- `expect_failure mfsmetarestore -a -d "${info[master_data_path]}"`
- `expect_failure lizardfs-probe info localhost "${info[matocl]}"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 22 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for metadata auto-recovery, EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_metarestore_while_starting.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_multiple_kills.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_multiple_kills.sh

## Purpose
This shell scenario exercises metadata auto-recovery, EC goal behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `auto recovery multiple kills` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 20 minutes`
- `CHUNKSERVERS=1`
- `MOUNTS=2`
- `USE_RAMDISK="YES"`
- `MOUNT_0_EXTRA_CONFIG="mfscachemode=NEVER,mfsreportreservedperiod=1,mfsdirentrycacheto=0"`
- `MOUNT_1_EXTRA_CONFIG="mfsmeta"`
- `MFSEXPORTS_EXTRA_OPTIONS="allcanchangequota,ignoregid"`
- `MFSEXPORTS_META_EXTRA_OPTIONS="nonrootmeta"`
- `MASTER_EXTRA_CONFIG="$master_cfg"`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `mfsreportreservedperiod`
- `mfsdirentrycacheto`
- `mfsmeta`
- `setup_local_empty_lizardfs`
- `mfs`
- `metadata_get_all_generators`
- `metadata_version`
- `metadata_get_version`
- `metadata_print`
- `lizardfs_master_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `metadata_validate_files`

Assertions and expectations include:
- `assert_equals "$metadata_version" "$(metadata_get_version "${info[master_data_path]}"/metadata.mfs)"`
- `assert_failure lizardfs_master_daemon start # Should fail without -o auto-recovery!`
- `assert_success lizardfs_master_daemon start -o auto-recovery`
- `assert_no_diff "$metadata" "$(metadata_print "${info[mount0]}")"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 48 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for metadata auto-recovery, EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_multiple_kills.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_nextchunkid.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_nextchunkid.sh

## Purpose
This shell scenario exercises metadata auto-recovery, chunk placement, replication, or chunkserver behavior, EC goal behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `auto recovery nextchunkid` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=1`
- `USE_RAMDISK=YES`
- `MFSEXPORTS_EXTRA_OPTIONS="allcanchangequota"`
- `MASTER_EXTRA_CONFIG="$master_cfg"`
- `AUTO_SHADOW_MASTER="NO"`
- `FILE_SIZE=1K`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `file-generate`
- `mfs`
- `lizardfs_master_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `lizardfs`
- `metadata_print`

Assertions and expectations include:
- `assert_awk_finds 0000000000000007 "$(lizardfs fileinfo 7)"`
- `assert_awk_finds '/NEXTCHUNKID/' "$(cat "${info[master_data_path]}"/changelog.mfs)"`
- `assert_success lizardfs_master_daemon start`
- `assert_no_diff "$metadata" "$(metadata_print "${info[mount0]}")"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 39 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for metadata auto-recovery, chunk placement, replication, or chunkserver behavior, EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_nextchunkid.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_repair.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_repair.sh

## Purpose
This shell scenario exercises metadata auto-recovery, EC goal behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `auto recovery repair` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 2 minutes`
- `CHUNKSERVERS=3`
- `USE_RAMDISK=YES`
- `MFSEXPORTS_EXTRA_OPTIONS="allcanchangequota"`
- `MASTER_EXTRA_CONFIG="MAGIC_DISABLE_METADATA_DUMPS`
- `FILE_SIZE=$((`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `metadata_version`
- `metadata_get_version`
- `mfs`
- `lizardfs`
- `file-generate`
- `lizardfs_chunkserver_daemon`
- `dd`
- `lizardfs_wait_for_ready_chunkservers`
- `metadata_print`
- `lizardfs_master_daemon`

Assertions and expectations include:
- `assert_equals 4 $(find_chunkserver_chunks 0 | wc -l)`
- `assert_equals 4 $(find_chunkserver_chunks 1 | wc -l)`
- `assert_equals 4 $(find_chunkserver_chunks 2 | wc -l)`
- `assert_success rm "$chunk"`
- `assert_equals 1 $(find_chunkserver_chunks 0 -name "chunk_000000000000000${chunk}_00000001.???" | wc -l)`
- `assert_equals 1 $(find_chunkserver_chunks 1 -name "chunk_000000000000000${chunk}_00000002.???" | wc -l)`
- `assert_equals 1 $(find_chunkserver_chunks 2 -name "chunk_000000000000000${chunk}_00000002.???" | wc -l)`
- `assert_equals 1 $(find_chunkserver_chunks 2 -name "chunk_000000000000000${chunk}_00000003.???" | wc -l)`
- `assert_awk_finds '/chunks with 0 copies: *3$/' "$(lizardfs checkfile dir/file)"`
- `assert_awk_finds '/chunks not changed: *1$/' "$repairinfo"`
- `assert_awk_finds '/chunks erased: *1$/' "$repairinfo"`
- `assert_awk_finds '/chunks repaired: *2$/' "$repairinfo"`
- `assert_awk_finds '/id:1 ver:2/' "$fileinfo"`
- `assert_awk_finds '/id:2 ver:1/' "$fileinfo"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 81 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for metadata auto-recovery, EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_repair.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_start_during_metarestore.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_start_during_metarestore.sh

## Purpose
This shell scenario exercises metadata auto-recovery, EC goal behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `auto recovery start during metarestore` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=0`
- `USE_RAMDISK=YES`
- `MASTER_EXTRA_CONFIG="AUTO_RECOVERY`
- `MOUNTS=0`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_master_daemon`
- `metadata_get_version`
- `mfs`
- `mfsmetarestore`

Assertions and expectations include:
- `assert_equals 1 $(metadata_get_version "${info[master_data_path]}/metadata.mfs")`
- `assert_eventually 'test -e "${info[master_data_path]}/metadata.mfs.lock"'`
- `expect_failure lizardfs_master_daemon start`
- `expect_equals 1 $(metadata_get_version "${info[master_data_path]}/metadata.mfs")`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 22 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for metadata auto-recovery, EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_start_during_metarestore.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_subdir.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_subdir.sh

## Purpose
This shell scenario exercises metadata auto-recovery, EC goal behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `auto recovery subdir` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 3 minutes`
- `CHUNKSERVERS=1`
- `MOUNTS=2`
- `USE_RAMDISK="YES"`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `MFSEXPORTS_EXTRA_OPTIONS="allcanchangequota,ignoregid"`
- `MASTER_EXTRA_CONFIG="MAGIC_DISABLE_METADATA_DUMPS`
- `MESSAGE="Comparing`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs_mount_unmount`
- `mfssubfolder`
- `lizardfs_mount_start`
- `metadata_file`
- `mfs`
- `metadata_version`
- `metadata_get_version`
- `metadata_get_all_generators`
- `metadata_subdir`
- `metadata_print`
- `metadata_root`
- `lizardfs_master_daemon`

Assertions and expectations include:
- `assert_equals "" "$(ls)" # some/subfolder should be empty!`
- `assert_equals "$metadata_version" "$(metadata_get_version "$metadata_file")"`
- `assert_success lizardfs_master_daemon start`
- `MESSAGE="Comparing metadata in root" assert_no_diff "$metadata_root" "$(metadata_print "${info[mount0]}")"`
- `MESSAGE="Comparing metadata in subdir" assert_no_diff "$metadata_subdir" "$(metadata_print)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 45 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for metadata auto-recovery, EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_subdir.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_switch.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_switch.sh

## Purpose
This shell scenario exercises metadata auto-recovery, EC goal behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `auto recovery switch` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `MASTER_EXTRA_CONFIG="MAGIC_DISABLE_METADATA_DUMPS`
- `FILE_SIZE=1K`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `file-generate`
- `lizardfs_admin_master`
- `lizardfs_master_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `file-validate`

Assertions and expectations include:
- `FILE_SIZE=1K assert_success file-generate "${info[mount0]}"/file_{1..5}`
- `assert_success lizardfs_admin_master stop-master-without-saving-metadata`
- `assert_eventually "! lizardfs_master_daemon isalive"`
- `assert_failure lizardfs_master_daemon start`
- `assert_success lizardfs_master_daemon start -o auto-recovery`
- `assert_success file-validate "${info[mount0]}"/file_{1..5}`
- `FILE_SIZE=1K assert_success file-generate "${info[mount0]}"/file_{6..10}`
- `assert_success lizardfs_master_daemon kill`
- `assert_failure "lizardfs_master_daemon isalive"`
- `assert_success lizardfs_master_daemon start`
- `assert_success file-validate "${info[mount0]}"/file_{1..10}`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 26 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for metadata auto-recovery, EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_switch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_xor_repair.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_xor_repair.sh

## Purpose
This shell scenario exercises metadata auto-recovery, XOR erasure-coded data behavior, EC goal behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `auto recovery xor repair` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 5 minutes`
- `CHUNKSERVERS=4`
- `USE_RAMDISK=YES`
- `CHUNKSERVER_LABELS="0,1,2:X|3:B"`
- `MFSEXPORTS_EXTRA_OPTIONS="allcanchangequota"`
- `MASTER_EXTRA_CONFIG="MAGIC_DISABLE_METADATA_DUMPS`
- `MASTER_CUSTOM_GOALS="10`
- `FILE_SIZE=$((`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `metadata_version`
- `metadata_get_version`
- `mfs`
- `lizardfs`
- `file-generate`
- `lizardfs_master_daemon`
- `lizardfs_chunkserver_daemon`
- `dd`
- `lizardfs_wait_for_ready_chunkservers`
- `metadata_print`

Assertions and expectations include:
- `assert_equals 4 $(find_chunkserver_chunks $cs -name "chunk_xor*" | wc -l)`
- `assert_eventually_prints 4 'find_chunkserver_chunks 3 -name "chunk_0*" | wc -l'`
- `assert_success rm "$chunk"`
- `assert_equals 1 $(find_chunkserver_chunks $CS -name "$chunk_name" | wc -l)`
- `assert_success rm $chunk`
- `assert_equals 1 $(find_chunkserver_chunks 0 -name "chunk_xor*0000000000000005_00000001.???" | wc -l)`
- `assert_equals 1 $(find_chunkserver_chunks 1 -name "chunk_xor*0000000000000005_00000002.???" | wc -l)`
- `assert_equals 1 $(find_chunkserver_chunks 2 -name "chunk_xor*0000000000000005_00000002.???" | wc -l)`
- `assert_awk_finds '/chunks with 0 copies: *2$/' "$checkfile"`
- `assert_awk_finds '/chunks with 1 copy: *2$/' "$checkfile"`
- `assert_awk_finds '/chunks not changed: *2$/' "$repairinfo"`
- `assert_awk_finds '/chunks erased: *1$/' "$repairinfo"`
- `assert_awk_finds '/chunks repaired: *1$/' "$repairinfo"`
- `assert_awk_finds '/id:5 ver:1/' "$fileinfo"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 130 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for metadata auto-recovery, XOR erasure-coded data behavior, EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_auto_recovery_xor_repair.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_backwards_changelog_compatibilty.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_backwards_changelog_compatibilty.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for backwards changelog compatibilty in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `backwards changelog compatibilty` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `MASTER_EXTRA_CONFIG="MAGIC_DISABLE_METADATA_DUMPS`
- `changelog_checksums() {`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_metalogger_daemon`
- `mfs`
- `metadata_file`
- `metadata_get_version`
- `lizardfs_admin_master`
- `lizardfs_master_daemon`

Assertions and expectations include:
- `assert_success lizardfs_admin_master save-metadata`
- `assert_less_than "$prev_version" "$(metadata_get_version "$metadata_file")"`
- `assert_file_exists "${info[master_data_path]}/changelog.mfs.$n"`
- `assert_not_equal "$expected_changelogs" "$(changelog_checksums)"`
- `assert_no_diff "$expected_changelogs" "$(changelog_checksums)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 51 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for backwards changelog compatibilty. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_backwards_changelog_compatibilty.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cache_per_inode.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cache_per_inode.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for cache per inode in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `cache per inode` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 minute`
- `CHUNKSERVERS=1`
- `MOUNT_EXTRA_CONFIG="mfscacheperinodepercentage=$percent`
- `USE_RAMDISK=YES`
- `testing_thread() {`

External commands and harness APIs used by the scenario:
- `mfscacheperinodepercentage`
- `mfswritecachesize`
- `setup_local_empty_lizardfs`
- `lizardfs_chunkserver_daemon`
- `dd`

Assertions and expectations include:
- `assert_success wait_for 'test -a "$file_created_on_success"' '15 seconds'`
- `assert_eventually_prints "" "jobs -p"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 36 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for cache per inode. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cache_per_inode.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cgi_validate_html.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cgi_validate_html.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for cgi validate html in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `cgi validate html` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 4 minutes`
- `CHUNKSERVERS=3`
- `DISK_PER_CHUNKSERVER=3`
- `CGI_SERVER="YES"`
- `MOUNTS=3`
- `USE_RAMDISK="YES"`
- `CHUNKSERVER_LABELS="0,1:de|2:us"`
- `MASTER_CUSTOM_GOALS="11`
- `MOUNT_0_EXTRA_CONFIG="mfscachemode=NEVER,mfsreportreservedperiod=1,mfsdirentrycacheto=0"`
- `MOUNT_1_EXTRA_CONFIG="mfsmeta"`
- `MFSEXPORTS_EXTRA_OPTIONS="allcanchangequota,ignoregid"`
- `MFSEXPORTS_META_EXTRA_OPTIONS="nonrootmeta"`
- `MOUNT_2_EXTRA_EXPORTS="mingoal=1,maxgoal=10,maxtrashtime=2w"`
- `MESSAGE="Validating`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `mfsreportreservedperiod`
- `mfsdirentrycacheto`
- `mfsmeta`
- `setup_local_empty_lizardfs`
- `mfs`
- `mfsmaster`
- `metadata_generate_all`
- `lizardfs_chunkserver_daemon`

Assertions and expectations include:
- `assert_program_installed wget tidy`
- `assert_less_than '20' "$(find "$cgi_pages/empty" -name "mfs.cgi*" | wc -l)"`
- `assert_less_than '20' "$(find "$cgi_pages/full" -name "mfs.cgi*" | wc -l)"`
- `expect_empty "$(grep -Inri -A 20 'Traceback' "$cgi_pages" || true)"`
- `MESSAGE="Validating $file" assert_empty "$(tidy -q -errors $file 2>&1)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 70 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for cgi validate html. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cgi_validate_html.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_chunk_creation_on_small_instalation.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_chunk_creation_on_small_instalation.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `chunk creation on small instalation` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set "30 seconds"`
- `CHUNKSERVERS=5`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `FILE_SIZE=1M`
- `FILE_SIZE=1k`
- `MESSAGE="There`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `file-validate`

Assertions and expectations include:
- `expect_equals 5 $(grep -v part <<< "$chunks" | grep -v parity | wc -l)`
- `MESSAGE="There should be at least 30 '$part'" expect_less_or_equal 30 $count`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 26 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_chunk_creation_on_small_instalation.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_chunk_replication.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_chunk_replication.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `chunk replication` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set "$test_timeout"`
- `CHUNKSERVERS=$number_of_chunkservers`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=1M`
- `get_list_of_chunks() {`

External commands and harness APIs used by the scenario:
- `lizardfs`
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `file-generate`
- `lizardfs_chunkserver_daemon`
- `file-validate`
- `lizardfs_wait_for_ready_chunkservers`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 61 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_chunk_replication.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_chunk_type_conversion.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_chunk_type_conversion.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `chunk type conversion` using a temporary cluster prepared by `tools/test_main.sh`. It delegates shared behavior through sourced helper/template files, so its effective test body includes those external harness fragments.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 2 minutes`
- `WAIT_FOR_REPLICATION=60`
- `NUMBER_OF_CHUNKSERVERS=10`
- `GOALS_TO_BE_TESTED="xor9`
- `VERIFY_FILE_CONTENT=YES`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 7 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- `source test_suites/TestTemplates/test_chunk_type_conversion.inc`

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_chunk_type_conversion.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_chunk_type_conversion_with_custom_goals.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_chunk_type_conversion_with_custom_goals.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, custom goal and label placement policy, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `chunk type conversion with custom goals` using a temporary cluster prepared by `tools/test_main.sh`. It delegates shared behavior through sourced helper/template files, so its effective test body includes those external harness fragments.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 2 minutes`
- `WAIT_FOR_REPLICATION=60`
- `NUMBER_OF_CHUNKSERVERS=11`
- `CHUNKSERVER_LABELS="0,1,2:us|3,4,5:eu|6,7,8:cn"`
- `MASTER_CUSTOM_GOALS="2`
- `GOALS_TO_BE_TESTED="xor9`
- `VERIFY_FILE_CONTENT=YES`

External commands and harness APIs used by the scenario:
- The script relies mostly on sourced harness functions and ordinary shell commands.

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 9 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- `source test_suites/TestTemplates/test_chunk_type_conversion.inc`

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, custom goal and label placement policy, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_chunk_type_conversion_with_custom_goals.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_chunkserver_start_with_damaged_disk.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_chunkserver_start_with_damaged_disk.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `chunkserver start with damaged disk` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=1`
- `DISK_PER_CHUNKSERVER=3`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `lizardfs_probe_master`

Assertions and expectations include:
- `assert_success lizardfs_chunkserver_daemon 0 stop`
- `assert_success chmod 000 "$(sort ${info[chunkserver0_hdd]} | head -n 1)"`
- `assert_success lizardfs_chunkserver_daemon 0 start`
- `assert_equals 3 "$(wc -l <<< "$list")"`
- `assert_awk_finds 'NR==1 && $4=="yes"' "$list"`
- `assert_awk_finds 'NR==2 && $4=="no"' "$list"`
- `assert_awk_finds 'NR==3 && $4=="no"' "$list"`
- `assert_eventually_prints 2 'lizardfs_probe_master list-disks | wc -l'`
- `assert_no_diff "$expected_list" "$actual_list"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 29 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_chunkserver_start_with_damaged_disk.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_clear_symlink_cache.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_clear_symlink_cache.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for clear symlink cache in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `clear symlink cache` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=1`
- `MOUNTS=2`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="symlinkcachetimeout=60"`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`

Assertions and expectations include:
- `assert_success ls -l | grep "symlink -> file"`
- `assert_success ls -l | grep "symlink2 -> file2"`
- `assert_success ls -l | grep "symlink3 -> file3"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 26 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for clear symlink cache. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_clear_symlink_cache.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_close_eio_in_chunkserver.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_close_eio_in_chunkserver.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `close eio in chunkserver` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=3`
- `CHUNKSERVER_EXTRA_CONFIG="HDD_TEST_FREQ`
- `CHUNKSERVER_0_DISK_0="$RAMDISK_DIR/close_EIO_hdd_0"`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `LD_PRELOAD="${LIZARDFS_INSTALL_FULL_LIBDIR}/libchunk_operations_eio.so"`
- `FILE_SIZE=1234`
- `FILE_SIZE=1M`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `lizardfs`
- `file-generate`
- `lizardfs_probe_master`

Assertions and expectations include:
- `assert_success lizardfs_chunkserver_daemon 0 restart`
- `FILE_SIZE=1234 assert_success file-generate test/small_{1..10}`
- `FILE_SIZE=1M   assert_success file-generate test/big_{1..10}`
- `assert_eventually_prints yes "lizardfs_probe_master list-disks | awk '/EIO/ {print \$4}'"`
- `assert_equals 3 "$(wc -l <<< "$list")"`
- `assert_awk_finds_no '(/EIO/ && $4 != "yes") || (!/EIO/ && $4 != "no")' "$list"`
- `assert_eventually_prints "" "lizardfs fileinfo '$f' | grep ':${info[chunkserver0_port]}'"`
- `assert_eventually_prints 2 "lizardfs fileinfo '$f' | grep copy | wc -l"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 40 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_close_eio_in_chunkserver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_connectathon_nfs_suite.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_connectathon_nfs_suite.sh

## Purpose
This shell scenario exercises EC goal behavior, NFS/Ganesha integration in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `connectathon nfs suite` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 70 seconds`
- `CHUNKSERVERS=3`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER,enablefilelocks=1"`
- `CHUNKSERVER_EXTRA_CONFIG="READ_AHEAD_KB`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `git`
- `make`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 21 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for EC goal behavior, NFS/Ganesha integration. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_connectathon_nfs_suite.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cs_failure_during_xor_read.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cs_failure_during_xor_read.sh

## Purpose
This shell scenario exercises XOR erasure-coded data behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `cs failure during xor read` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 minute`
- `CHUNKSERVERS=4`
- `DISK_PER_CHUNKSERVER=1`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `USE_RAMDISK=YES`
- `FILE_SIZE=123456789`
- `LD_PRELOAD="${LIZARDFS_INSTALL_FULL_LIBDIR}/libredirect_bind.so"`
- `start_proxy() {`

External commands and harness APIs used by the scenario:
- `dd`
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `file-validate`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 40 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for XOR erasure-coded data behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cs_failure_during_xor_read.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cs_failure_during_xor_write.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cs_failure_during_xor_write.sh

## Purpose
This shell scenario exercises XOR erasure-coded data behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `cs failure during xor write` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 10 minutes`
- `CHUNKSERVERS=4`
- `MOUNTS=10`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `USE_RAMDISK=YES`
- `LD_PRELOAD=${libredirect_bind_path}`
- `FILE_SIZE=2000K`
- `FILE_SIZE=200M`
- `MESSAGE="Validating`
- `start_proxy() {`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `lizardfs`
- `file-generate`
- `dd`
- `mount`
- `file-validate`

Assertions and expectations include:
- `assert_program_installed socat`
- `MESSAGE="Validating data" expect_success file-validate "${info[mount2]}"/dir/*`
- `MESSAGE="Validating data (CS$csid is down)" expect_success file-validate "${info[mount3]}"/dir/*`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 68 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for XOR erasure-coded data behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cs_failure_during_xor_write.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cs_failure_recovery_speed.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cs_failure_recovery_speed.sh

## Purpose
This shell scenario exercises EC goal behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `cs failure recovery speed` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=4`
- `USE_RAMDISK=YES`
- `MOUNTS=5`
- `CHUNKSERVER_EXTRA_CONFIG="MASTER_TIMEOUT`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER|mfschunkserverwriteto=500"`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `mfschunkserverwriteto`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `lizardfs_chunkserver_daemon`
- `file-overwrite`
- `mount`
- `file-validate`

Assertions and expectations include:
- `( assert_success file-overwrite "${info[mount$i]}/dir/file$i" && touch "$TEMP_DIR/finish$i" & )`
- `assert_success wait_for '(( $(ls "$TEMP_DIR"/finish? 2>/dev/null | wc -l) == 5 ))' '4 seconds'`
- `assert_success file-validate "${info[mount0]}/dir/"file*`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 23 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cs_failure_recovery_speed.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cstoma_timeout.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cstoma_timeout.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for cstoma timeout in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `cstoma timeout` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=1`
- `USE_RAMDISK=YES`
- `CHUNKSERVER_EXTRA_CONFIG="MASTER_TIMEOUT`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_wait_for_all_ready_chunkservers`
- `lizardfs_ready_chunkservers_count`
- `lizardfs_chunkserver_daemon`

Assertions and expectations include:
- `assert_equals 1 $(lizardfs_ready_chunkservers_count)`
- `assert_equals 0 $(lizardfs_ready_chunkservers_count)`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 17 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for cstoma timeout. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_cstoma_timeout.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goal_migration_during_delay_disconnect.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goal_migration_during_delay_disconnect.sh

## Purpose
This shell scenario exercises custom goal and label placement policy, EC goal behavior, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `custom goal migration during delay disconnect` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set "1 minute"`
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=4`
- `CHUNKSERVER_LABELS="0:raid|2,3:something"`
- `MASTER_CUSTOM_GOALS="1`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=1K`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_ready_chunkservers`
- `file-generate`
- `lizardfs`

Assertions and expectations include:
- `assert_equals 20 $(lizardfs checkfile "${info[mount0]}"/* | grep 'with 2 copies:' | wc -l)`
- `assert_equals 20 $(lizardfs checkfile "${info[mount0]}"/* | grep 'with 1 copy:' | wc -l)`
- `assert_eventually_prints 20 'find_chunkserver_chunks 0 | wc -l' '5 seconds'`
- `assert_equals 0 $(find_chunkserver_chunks 1 | wc -l)`
- `assert_eventually_prints 20 'find_chunkserver_chunks 1 | wc -l' '20 seconds'`
- `assert_equals 20 $(lizardfs checkfile "${info[mount0]}"/* | grep 'with 3 copies:' | wc -l)`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 53 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for custom goal and label placement policy, EC goal behavior, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goal_migration_during_delay_disconnect.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goal_replication_delay_disconnect.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goal_replication_delay_disconnect.sh

## Purpose
This shell scenario exercises custom goal and label placement policy, EC goal behavior, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `custom goal replication delay disconnect` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set "1 minute"`
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=4`
- `CHUNKSERVER_LABELS="0,1:ssd"`
- `MASTER_CUSTOM_GOALS="1`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=1K`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_ready_chunkservers`
- `file-generate`
- `lizardfs`

Assertions and expectations include:
- `assert_equals 20 $(lizardfs checkfile "${info[mount0]}"/* | grep 'with 2 copies:' | wc -l)`
- `assert_equals 20 $(lizardfs checkfile "${info[mount0]}"/* | grep 'with 1 copy:' | wc -l)`
- `assert_eventually_prints 20 'find_chunkserver_chunks 1 | wc -l' "4 seconds"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 52 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for custom goal and label placement policy, EC goal behavior, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goal_replication_delay_disconnect.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_chunk_replication_case_1.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_chunk_replication_case_1.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, custom goal and label placement policy, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `custom goals chunk replication case 1` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set "1 minute"`
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=4`
- `CHUNKSERVER_LABELS="0,1:ssd|2,3:hdd"`
- `MASTER_CUSTOM_GOALS="1`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=1K`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_ready_chunkservers`
- `file-generate`
- `lizardfs`

Assertions and expectations include:
- `assert_equals 20 $(lizardfs checkfile "${info[mount0]}"/* | grep 'with 2 copies: *1' | wc -l)`
- `assert_equals 20 $(find_chunkserver_chunks 0 | wc -l)`
- `assert_equals 20 $(lizardfs checkfile "${info[mount0]}"/* | grep 'with 1 copy: *1' | wc -l)`
- `assert_eventually_prints 20 'lizardfs checkfile "${info[mount0]}"/* | grep "with 2 copies: *1" | wc -l'`
- `assert_equals 0 $(find_chunkserver_chunks 0 | wc -l)`
- `assert_eventually_prints 20 'find_chunkserver_chunks 0 | wc -l'`
- `assert_eventually_prints 60 'find_all_chunks | wc -l'`
- `assert_eventually_prints 20 'find_chunkserver_chunks 1 | wc -l'`
- `assert_eventually_prints 40 'find_all_chunks | wc -l'`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 51 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, custom goal and label placement policy, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_chunk_replication_case_1.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_chunk_replication_case_2.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_chunk_replication_case_2.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, custom goal and label placement policy, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `custom goals chunk replication case 2` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set "1 minute"`
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=8`
- `CHUNKSERVER_LABELS="0,1,2:us|3,4,5,6,7:eu"`
- `MASTER_CUSTOM_GOALS="1`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=1K`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `file-generate`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_ready_chunkservers`
- `lizardfs`
- `file-validate`

Assertions and expectations include:
- `assert_eventually_prints 40 "lizardfs checkfile file* | grep 'with [2-5] copies: *1' | wc -l"`
- `assert_equals 0 $(lizardfs checkfile file* | grep -i 'with 0 copies' | wc -l)`
- `assert_eventually_prints 40 "lizardfs checkfile file* | grep 'with 2 copies: *1' | wc -l"`
- `assert_success file-validate file*`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 35 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, custom goal and label placement policy, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_chunk_replication_case_2.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_missing_server.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_missing_server.sh

## Purpose
This shell scenario exercises custom goal and label placement policy in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `custom goals missing server` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=4`
- `CHUNKSERVER_LABELS="0,1:ssd|2,3:hdd"`
- `MASTER_CUSTOM_GOALS=$goals`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=1K`
- `MESSAGE="New`
- `MESSAGE="Veryfing`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`

Assertions and expectations include:
- `MESSAGE="New $file: $fileinfo" assert_equals "$expected_copies" "$actual_copies"`
- `MESSAGE="Veryfing $file" expect_equals "${infos[$file]}" "$(lizardfs fileinfo "$file")"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 44 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for custom goal and label placement policy. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_missing_server.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_when_changing_label_of_chunkserver.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_when_changing_label_of_chunkserver.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, custom goal and label placement policy in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `custom goals when changing label of chunkserver` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=4`
- `CHUNKSERVER_LABELS="0,1:us|2,3:eu"`
- `MASTER_CUSTOM_GOALS="1`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=1K`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `file-generate`
- `lizardfs_chunkserver_daemon`

Assertions and expectations include:
- `assert_equals 0 $(find_chunkserver_chunks 2 | wc -l)`
- `assert_equals 0 $(find_chunkserver_chunks 3 | wc -l)`
- `assert_eventually_prints 0 'find_chunkserver_chunks 0 | wc -l'`
- `assert_equals 20 $(find_chunkserver_chunks 1 | wc -l)`
- `assert_equals  0 $(find_chunkserver_chunks 2 | wc -l)`
- `assert_equals  0 $(find_chunkserver_chunks 3 | wc -l)`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 28 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, custom goal and label placement policy. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_when_changing_label_of_chunkserver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_when_creating_new_chunks.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_when_creating_new_chunks.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, custom goal and label placement policy in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `custom goals when creating new chunks` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set "1 minute"`
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=5`
- `CHUNKSERVER_LABELS="0,1:de|2,3:us|4:cn"`
- `MASTER_CUSTOM_GOALS="11`
- `MESSAGE="Testing`
- `get_file_labels() {`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs`

Assertions and expectations include:
- `assert_matches "^(${expected_labels[goal]})\$" "$(get_file_labels "$file")"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 54 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, custom goal and label placement policy. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_when_creating_new_chunks.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_with_many_labels.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_with_many_labels.sh

## Purpose
This shell scenario exercises custom goal and label placement policy in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `custom goals with many labels` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=20`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `MASTER_CUSTOM_GOALS="1`
- `FILE_SIZE=1K`
- `MESSAGE="Testing`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `file-generate`
- `file-validate`
- `lizardfs`

Assertions and expectations include:
- `expect_success file-validate "$file"`
- `expect_equals 20 $(lizardfs fileinfo "$file" | grep copy | wc -l)`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 14 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for custom goal and label placement policy. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_custom_goals_with_many_labels.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_defective_files_tool.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_defective_files_tool.sh

## Purpose
This shell scenario exercises EC goal behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `defective files tool` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 60 seconds`
- `CHUNKSERVERS=5`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `MASTER_EXTRA_CONFIG="OPERATIONS_DELAY_INIT`
- `FILE_SIZE=$((3*64*1024))`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `lizardfs_chunkserver_daemon`
- `lizardfs_admin_master`

Assertions and expectations include:
- `assert_eventually_prints 1 "lizardfs_admin_master list-defective-files --undergoal --porcelain | wc -l"`
- `assert_equals 0 $(lizardfs_admin_master list-defective-files --unavailable --porcelain | wc -l)`
- `assert_equals 0 $(lizardfs_admin_master list-defective-files --structure-error --porcelain | wc -l)`
- `assert_eventually_prints 1 "lizardfs_admin_master list-defective-files --unavailable --porcelain | wc -l"`
- `assert_equals 0 $(lizardfs_admin_master list-defective-files --undergoal --porcelain | wc -l)`
- `assert_eventually_prints 0 "lizardfs_admin_master list-defective-files --unavailable --porcelain | wc -l"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 34 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_defective_files_tool.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_descriptors_leak_check.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_descriptors_leak_check.sh

## Purpose
This shell scenario exercises EC goal behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `descriptors leak check` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 minute`
- `CHUNKSERVERS=1`
- `DISK_PER_CHUNKSERVER=1`
- `USE_RAMDISK=YES`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `dd`
- `lizardfs_chunkserver_daemon`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 36 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_descriptors_leak_check.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_direntry_cache_invalidation.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_direntry_cache_invalidation.sh

## Purpose
This shell scenario exercises I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `direntry cache invalidation` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `FILE_SIZE=1K`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `file-generate`
- `file-validate`

Assertions and expectations include:
- `assert_empty "$("$TEMP_DIR/test.cc" back 2>&1)" # rename 'file' to 'back', create a new empty 'file'`
- `assert_file_exists back`
- `assert_success file-validate back`
- `assert_file_exists file`
- `assert_equals 0 "$(stat -c %s file)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 43 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_direntry_cache_invalidation.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_disk_failure.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_disk_failure.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for disk failure in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `disk failure` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=3`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=5M`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `file-validate`
- `file-overwrite`

Assertions and expectations include:
- `assert_success file-validate dir/file{1..10}`
- `assert_success file-overwrite dir/file{1..10}`
- `assert_success file-validate dir/file{5..15}`
- `assert_awk_finds    "/copy 1/" "$fileinfo"`
- `assert_awk_finds_no "/copy 2/" "$fileinfo"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 30 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for disk failure. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_disk_failure.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_disk_failure_with_endangered_chunks_priority.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_disk_failure_with_endangered_chunks_priority.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `disk failure with endangered chunks priority` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=3`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=5M`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `file-validate`
- `file-overwrite`

Assertions and expectations include:
- `assert_success file-validate dir/file{1..10}`
- `assert_success file-overwrite dir/file{1..10}`
- `assert_success file-validate dir/file{5..15}`
- `assert_awk_finds    "/copy 1/" "$fileinfo"`
- `assert_awk_finds_no "/copy 2/" "$fileinfo"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 31 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_disk_failure_with_endangered_chunks_priority.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_duptrunc.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_duptrunc.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for duptrunc in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `duptrunc` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set '1 minute'`
- `CHUNKSERVERS=4`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `FILE_SIZE=$filesize`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `file-validate`

Assertions and expectations include:
- `assert_success file-validate file snapshot1 snapshot2`
- `assert_success truncate -s $((filesize + diff)) snapshot1`
- `assert_success file-validate file # This file shouldn't be changed!`
- `expect_files_equal <(head -c $diff /dev/zero) <(tail -c $diff snapshot1)`
- `expect_files_equal <(head -c $filesize file) <(head -c $filesize snapshot1)`
- `assert_success truncate -s $filesize snapshot1`
- `assert_success truncate -s $truncated snapshot2`
- `expect_files_equal <(head -c $truncated file) <(head -c $truncated snapshot2)`
- `assert_success truncate -s $filesize snapshot2`
- `expect_files_equal <(head -c $diff /dev/zero) <(tail -c $diff snapshot2)`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 49 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for duptrunc. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_duptrunc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_ec_goal_with_labels.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_ec_goal_with_labels.sh

## Purpose
This shell scenario exercises EC goal behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `ec goal with labels` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 4 minutes`
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=12`
- `CHUNKSERVER_LABELS="3,4,5:hdd|6,7,8:ssd|9,10,11:floppy"`
- `MASTER_CUSTOM_GOALS="10`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=1K`
- `chunks_state() {`
- `count_chunks_on_chunkservers() {`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`

Assertions and expectations include:
- `assert_equals "3 ec2_1" "$(chunks_state)"`
- `assert_equals 3 "$(count_chunks_on_chunkservers {6..8})"`
- `assert_equals 3 "$(count_chunks_on_chunkservers {0..11})"`
- `assert_eventually_prints '6 ec3_3' 'chunks_state' '2 minutes'`
- `assert_equals 3 "$(count_chunks_on_chunkservers {3..5})"`
- `assert_equals 6 "$(count_chunks_on_chunkservers {0..11})"`
- `assert_eventually_prints '4 ec2_2' 'chunks_state' '2 minutes'`
- `assert_equals 2 "$(count_chunks_on_chunkservers {3..5})"`
- `assert_equals 2 "$(count_chunks_on_chunkservers {6..8})"`
- `assert_eventually_prints '9 ec3_6' 'chunks_state' '2 minutes'`
- `assert_equals 3 "$(count_chunks_on_chunkservers {9..11})"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 62 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_ec_goal_with_labels.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_ec_read_combinations.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_ec_read_combinations.sh

## Purpose
This shell scenario exercises EC goal behavior, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `ec read combinations` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 10 minutes`
- `CHUNKSERVERS=8`
- `DISK_PER_CHUNKSERVER=1`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `MASTER_CUSTOM_GOALS="6`
- `USE_RAMDISK=YES`
- `FILE_SIZE=876M`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `lizardfs_chunkserver_daemon`
- `file-validate`
- `lizardfs_wait_for_all_ready_chunkservers`

Assertions and expectations include:
- No explicit `assert_*`/`expect_*` call was detected in this wrapper; behavior is likely in a sourced template.

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 26 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for EC goal behavior, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_ec_read_combinations.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_exit_status.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_exit_status.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for exit status in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `exit status` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=1`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `get_status() {`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `mfschunkserver`
- `lizardfs_chunkserver_daemon`
- `lizardfs_master_daemon`
- `mfs`

Assertions and expectations include:
- `expect_less_or_equal 2 $(get_status mfschunkserver -c "$TEMP_DIR/nonexistent_file" start)`
- `expect_less_or_equal 2 $(get_status lizardfs_chunkserver_daemon 0 wrongusage)`
- `expect_equals 0 $(get_status lizardfs_chunkserver_daemon 0 isalive)`
- `expect_equals 0 $(get_status lizardfs_chunkserver_daemon 0 restart)`
- `expect_equals 0 $(get_status lizardfs_chunkserver_daemon 0 stop)`
- `expect_equals 1 $(get_status lizardfs_chunkserver_daemon 0 isalive)`
- `expect_equals 0 $(get_status lizardfs_chunkserver_daemon 0 start)`
- `expect_less_or_equal 2 $(get_status lizardfs_master_daemon some_typo)`
- `expect_less_or_equal 2 $(get_status lizardfs_master_daemon -@ restart)`
- `expect_equals 0 $(get_status lizardfs_master_daemon isalive)`
- `expect_equals 0 $(get_status lizardfs_master_daemon restart)`
- `expect_equals 0 $(get_status lizardfs_master_daemon stop)`
- `expect_equals 1 $(get_status lizardfs_master_daemon isalive)`
- `expect_less_or_equal 2 $(get_status lizardfs_master_daemon start)`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 38 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for exit status. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_exit_status.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_exports_goal_limits.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_exports_goal_limits.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for exports goal limits in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `exports goal limits` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=1`
- `USE_RAMDISK=YES`
- `MOUNTS=4`
- `MOUNT_1_EXTRA_EXPORTS="mingoal=2"`
- `MOUNT_2_EXTRA_EXPORTS="maxgoal=14"`
- `MOUNT_3_EXTRA_EXPORTS="mingoal=10,maxgoal=12"`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs`

Assertions and expectations include:
- `assert_success lizardfs setgoal     2 dir1/sub1`
- `assert_success lizardfs setgoal -r  3 dir1/sub2`
- `assert_success lizardfs setgoal     4 dir1/sub3`
- `assert_success lizardfs setgoal -r  2 dir1`
- `assert_success lizardfs setgoal -r  7 dir1`
- `assert_success lizardfs setgoal    13 dir1`
- `assert_success lizardfs setgoal -r 20 dir1`
- `assert_failure lizardfs setgoal     1 dir1/sub4 # Too low!`
- `assert_failure lizardfs setgoal -r  1 dir1      # Too low!`
- `assert_success lizardfs setgoal -r 13 dir1`
- `assert_success lizardfs setgoal     1 dir2/sub1`
- `assert_success lizardfs setgoal -r  4 dir2/sub1`
- `assert_success lizardfs setgoal     9 dir2/sub1`
- `assert_success lizardfs setgoal -r 13 dir2/sub1`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 52 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for exports goal limits. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_exports_goal_limits.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_file_locks_interrupt.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_file_locks_interrupt.sh

## Purpose
This shell scenario exercises file locking semantics in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `file locks interrupt` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 minutes`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="enablefilelocks=1"`
- `MOUNTS=2`
- `function test_interrupt() {`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`

Assertions and expectations include:
- `assert_eventually_prints "write lock:   $lockfile0" 'tail -1 lock0.log'`
- `assert_eventually_matches '.*failed: Interrupted system call' 'tail -1 lock1_err.log'`
- `assert_eventually_prints $rmpcount "get_changes ${info[master0_data_path]} | grep RMPLOCK | wc -l"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 52 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for file locking semantics. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_file_locks_interrupt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_file_locks_ping_pong.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_file_locks_ping_pong.sh

## Purpose
This shell scenario exercises file locking semantics in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `file locks ping pong` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 minutes`
- `USE_RAMDISK=YES`
- `MOUNTS=5`
- `MOUNT_EXTRA_CONFIG="enablefilelocks=1"`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `mount`

Assertions and expectations include:
- `assert_equals 0 $?`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 21 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for file locking semantics. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_file_locks_ping_pong.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_file_repair_correct_only_chunk_missing.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_file_repair_correct_only_chunk_missing.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, EC goal behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `file repair correct only chunk missing` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=5`
- `MASTER_CUSTOM_GOALS="10`
- `FILE_SIZE=1K`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `file-validate`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `lizardfs_mount_unmount`
- `lizardfs_mount_start`

Assertions and expectations include:
- `assert_success file-validate test/file$i`
- `assert_success lizardfs_mount_unmount 0`
- `assert_success lizardfs_mount_start 0`
- `assert_failure file-validate test/file1`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 66 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_file_repair_correct_only_chunk_missing.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_file_repair_correct_only_chunk_parts_missing.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_file_repair_correct_only_chunk_parts_missing.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, EC goal behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `file repair correct only chunk parts missing` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=5`
- `MASTER_CUSTOM_GOALS="10`
- `FILE_SIZE=1K`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `file-validate`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `lizardfs_mount_unmount`
- `lizardfs_mount_start`

Assertions and expectations include:
- `assert_success file-validate test/file$i`
- `assert_success lizardfs_mount_unmount 0`
- `assert_success lizardfs_mount_start 0`
- `assert_failure file-validate test/file1`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 66 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, EC goal behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_file_repair_correct_only_chunk_parts_missing.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_fileinfo_missing_parts.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_fileinfo_missing_parts.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for fileinfo missing parts in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `fileinfo missing parts` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 70 seconds`
- `CHUNKSERVERS=7`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `FILE_SIZE=123456789`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `lizardfs_chunkserver_daemon`

Assertions and expectations include:
- `assert_failure "lizardfs fileinfo dir_ec/file | grep 'not enough parts available'"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 22 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for fileinfo missing parts. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_fileinfo_missing_parts.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_files_by_inode_permissions.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_files_by_inode_permissions.sh

## Purpose
This shell scenario exercises I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `files by inode permissions` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `FILE_SIZE="$size"`
- `INODE_PATH="${info[mount0]}/.lizardfs_file_by_inode"`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `file-generate`
- `lizardfs_file_by_inode`
- `file-validate`
- `dd`

Assertions and expectations include:
- `FILE_SIZE="$size" assert_success file-generate "${info[mount0]}/dir/file_$size"`
- `assert_success file-validate "$INODE_PATH/3"`
- `assert_failure dd if=/dev/random of="$INODE_PATH/3" bs=1 count=1`
- `assert_failure file-validate "$INODE_PATH/4"`
- `assert_failure dd if=/dev/random of="$INODE_PATH/5" bs=1 count=1`
- `assert_failure file-validate "$INODE_PATH/5"`
- `assert_success file-validate "$INODE_PATH/6"`
- `assert_success dd if=/dev/random of="$INODE_PATH/6" bs=1 count=1`
- `assert_success printf "#/bin/bash\necho 'Hello!\n' > /dev/null" > "$INODE_PATH/7"`
- `assert_success "$INODE_PATH/7"`
- `assert_failure ls $INODE_PATH`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 37 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_files_by_inode_permissions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_find_during_write.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_find_during_write.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for find during write in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `find during write` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 minute`
- `CHUNKSERVERS=1`
- `MOUNTS=1`
- `USE_RAMDISK="YES"`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`

Assertions and expectations include:
- `assert_equals 5 $(cat $output | wc -l)`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 19 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for find during write. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_find_during_write.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_flushing_changes_to_shadow.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_flushing_changes_to_shadow.sh

## Purpose
This shell scenario exercises shadow master synchronization in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `flushing changes to shadow` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set '40 seconds'`
- `CHUNKSERVERS=1`
- `MASTERSERVERS=2`
- `USE_RAMDISK="YES"`
- `MASTER_EXTRA_CONFIG="MASTER_TIMEOUT`
- `start_proxy() {`

External commands and harness APIs used by the scenario:
- `dd`
- `setup_local_empty_lizardfs`
- `lizardfs_master_n`
- `lizardfs_shadow_synchronized`
- `lizardfs_master_daemon`

Assertions and expectations include:
- `assert_program_installed socat`
- `assert_success lizardfs_master_n 1 start`
- `assert_eventually "lizardfs_shadow_synchronized 1"`
- `assert_success lizardfs_master_daemon stop`
- `assert_less_or_equal 10 $duration`
- `assert_eventually_equals 'get_changes "$m" | tail' 'get_changes "$s" | tail'`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 53 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for shadow master synchronization. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_flushing_changes_to_shadow.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_fsync_eio_in_chunkserver.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_fsync_eio_in_chunkserver.sh

## Purpose
This shell scenario exercises chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `fsync eio in chunkserver` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=3`
- `CHUNKSERVER_EXTRA_CONFIG="HDD_TEST_FREQ`
- `CHUNKSERVER_0_DISK_0="$RAMDISK_DIR/fsync_EIO_hdd_0"`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `LD_PRELOAD="${LIZARDFS_INSTALL_FULL_LIBDIR}/libchunk_operations_eio.so"`
- `FILE_SIZE=1234`
- `FILE_SIZE=1M`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `lizardfs`
- `file-generate`
- `lizardfs_probe_master`

Assertions and expectations include:
- `assert_success lizardfs_chunkserver_daemon 0 restart`
- `FILE_SIZE=1234 assert_success file-generate test/small_{1..10}`
- `FILE_SIZE=1M   assert_success file-generate test/big_{1..10}`
- `assert_eventually_prints yes "lizardfs_probe_master list-disks | awk '/EIO/ {print \$4}'"`
- `assert_equals 3 "$(wc -l <<< "$list")"`
- `assert_awk_finds_no '(/EIO/ && $4 != "yes") || (!/EIO/ && $4 != "no")' "$list"`
- `assert_eventually_prints "" "lizardfs fileinfo '$f' | grep ':${info[chunkserver0_port]}'"`
- `assert_eventually_prints 2 "lizardfs fileinfo '$f' | grep copy | wc -l"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 40 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for chunk placement, replication, or chunkserver behavior, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_fsync_eio_in_chunkserver.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_getting_length_of_open_file.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_getting_length_of_open_file.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for getting length of open file in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `getting length of open file` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`

Assertions and expectations include:
- `assert_empty "$("$TEMP_DIR/test.cc" "${info[mount0]}/file$i" 2>&1)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 41 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for getting length of open file. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_getting_length_of_open_file.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_global_io_limiting_many_clients.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_global_io_limiting_many_clients.sh

## Purpose
This shell scenario exercises I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `global io limiting many clients` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 minute`
- `N=5`
- `E=11`
- `E=$((5`
- `CHUNKSERVERS=3`
- `MOUNTS=$N`
- `USE_RAMDISK=YES`
- `MASTER_EXTRA_CONFIG="GLOBALIOLIMITS_FILENAME`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `start_readers() {`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `mount`

Assertions and expectations include:
- `assert_near 0 $relerr $E`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 50 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_global_io_limiting_many_clients.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_global_io_limiting_read_write.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_global_io_limiting_read_write.sh

## Purpose
This shell scenario exercises I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `global io limiting read write` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 minute`
- `E=11`
- `E=$((5`
- `CHUNKSERVERS=3`
- `MOUNTS=2`
- `USE_RAMDISK=YES`
- `MASTER_EXTRA_CONFIG="GLOBALIOLIMITS_FILENAME`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`

Assertions and expectations include:
- `assert_near 0 $relerr $E`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 35 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_global_io_limiting_read_write.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_global_io_limiting_reconfiguration.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_global_io_limiting_reconfiguration.sh

## Purpose
This shell scenario exercises EC goal behavior, I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `global io limiting reconfiguration` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 minute`
- `E=11`
- `E=$((5`
- `CHUNKSERVERS=3`
- `USE_RAMDISK=YES`
- `MASTER_EXTRA_CONFIG="GLOBALIOLIMITS_FILENAME`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs_master_daemon`

Assertions and expectations include:
- `assert_near 0 $relerr $E`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 40 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for EC goal behavior, I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_global_io_limiting_reconfiguration.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_global_io_limiting_transition.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_global_io_limiting_transition.sh

## Purpose
This shell scenario exercises I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `global io limiting transition` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 1 minute`
- `N=5`
- `R=3`
- `E=11`
- `E=$((5`
- `CHUNKSERVERS=3`
- `MOUNTS=$N`
- `USE_RAMDISK=YES`
- `MASTER_EXTRA_CONFIG="GLOBALIOLIMITS_FILENAME`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `mount`

Assertions and expectations include:
- `assert_near 0 $relerr $E`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 41 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_global_io_limiting_transition.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_ha_cluster_managed_personality.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_ha_cluster_managed_personality.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for ha cluster managed personality in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `ha cluster managed personality` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=1`
- `MASTER_EXTRA_CONFIG="PERSONALITY=ha-cluster-managed"`
- `MASTER_START_PARAM="-o`
- `SHADOW_START_PARAM="-o`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_master_daemon`
- `lizardfs_master_daemon_ha`

Assertions and expectations include:
- `assert_failure lizardfs_master_daemon ${command}`
- `assert_success lizardfs_master_daemon_ha stop`
- `assert_success lizardfs_master_daemon_ha start -o initial-personality=master`
- `assert_success lizardfs_master_daemon_ha restart -o initial-personality=master`
- `assert_success lizardfs_master_daemon_ha ${command}`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 28 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for ha cluster managed personality. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_ha_cluster_managed_personality.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_hardlink.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_hardlink.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for hardlink in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `hardlink` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 4 minutes`
- `CHUNKSERVERS=2`
- `USE_RAMDISK="YES"`
- `FILE_SIZE=123`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `file-validate`
- `lizardfs_master_daemon`

Assertions and expectations include:
- `assert_equals $(inode_of file$i) $(inode_of file$((i+1)))`
- `assert_success file-validate file63`
- `assert_equals $(inode_of file63) $(inode_of file63-backup)`
- `assert_success file-validate file63-backup`
- `assert_success diff file63{,-backup}`
- `assert_equals $(inode_of file63) $(inode_of file63-$i)`
- `assert_success lizardfs_master_daemon restart`
- `assert_success file-validate file63-$i`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 48 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for hardlink. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_hardlink.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_io_limits.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_io_limits.sh

## Purpose
This shell scenario exercises I/O limiting or data path behavior in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `io limits` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 2 minutes`
- `CHUNKSERVERS=3`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER|mfsiolimits=$iolimits"`
- `rescale_value() {`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `mfsiolimits`
- `setup_local_empty_lizardfs`
- `file-generate`
- `file-validate`

Assertions and expectations include:
- `assert_near $expected_time_ms $actual_time_ms $(rescale_value 250)`
- `assert_near $((2 * expected_time_ms)) $actual_time_ms $(rescale_value 250)`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 45 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for I/O limiting or data path behavior. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_io_limits.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_label_spill.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_label_spill.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for label spill in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `label spill` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 2 minutes`
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=6`
- `CHUNKSERVER_LABELS="0,1,2:hdd|3,4:floppy|5:_"`
- `MASTER_CUSTOM_GOALS="10`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `FILE_SIZE=32K`
- `count_chunks_on_chunkservers() {`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_ready_chunkservers`
- `lizardfs`
- `file-generate`

Assertions and expectations include:
- `expect_eventually_prints 30 'count_chunks_on_chunkservers {0..2}'`
- `assert_eventually_prints 30 'find_all_chunks | wc -l'`
- `assert_equals 0 $(count_chunks_on_chunkservers {3,4})`
- `expect_eventually_prints 30 'count_chunks_on_chunkservers {0..2}' '1 minute'`
- `assert_eventually_prints 30 'find_all_chunks | wc -l' '1 minute'`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 51 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for label spill. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_label_spill.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_lizardfs_upgrade_ec_basic.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_lizardfs_upgrade_ec_basic.sh

## Purpose
This shell scenario exercises EC goal behavior, upgrade compatibility in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `lizardfs upgrade ec basic` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 90 seconds`
- `CHUNKSERVERS=5`
- `USE_RAMDISK=YES`
- `START_WITH_LEGACY_LIZARDFS=YES`
- `MASTERSERVERS=2`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `CHUNKSERVER_1_EXTRA_CONFIG="CREATE_NEW_CHUNKS_IN_MOOSEFS_FORMAT`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_MIN_TIME`
- `REPLICATION_TIMEOUT='30`
- `FILE_SIZE=12345678`
- `function generate_file {`

External commands and harness APIs used by the scenario:
- `mfsmount`
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs_admin_master`
- `lizardfsXX`
- `mfssetgoal`
- `file-generate`
- `file-validate`
- `lizardfs_master_n`
- `lizardfs_shadow_synchronized`
- `lizardfs_master_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `lizardfsXX_chunkserver_daemon`
- `lizardfs_chunkserver_daemon`

Assertions and expectations include:
- `assert_equals 1 $(lizardfs_admin_master info | grep $LIZARDFSXX_TAG | wc -l)`
- `assert_equals 5 $(lizardfs_admin_master list-chunkservers | grep $LIZARDFSXX_TAG | wc -l)`
- `assert_equals 1 $(lizardfs_admin_master list-mounts | grep $LIZARDFSXX_TAG | wc -l)`
- `assert_success lizardfsXX mfssetgoal ec32 dir`
- `assert_success generate_file file0`
- `assert_success file-validate file0`
- `assert_eventually "lizardfs_shadow_synchronized 1"`
- `assert_equals 0 $(lizardfs_admin_master info | grep $LIZARDFSXX_TAG | wc -l)`
- `assert_success lizardfs_mount_unmount 0`
- `assert_success lizardfs_mount_start 0`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 66 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for EC goal behavior, upgrade compatibility. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_lizardfs_upgrade_ec_basic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_lizardfs_upgrade_general.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_lizardfs_upgrade_general.sh

## Purpose
This shell scenario exercises upgrade compatibility in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `lizardfs upgrade general` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 90 seconds`
- `CHUNKSERVERS=2`
- `USE_RAMDISK=YES`
- `MASTERSERVERS=2`
- `START_WITH_LEGACY_LIZARDFS=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `CHUNKSERVER_1_EXTRA_CONFIG="CREATE_NEW_CHUNKS_IN_MOOSEFS_FORMAT`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_TIME`
- `REPLICATION_TIMEOUT='30`
- `FILE_SIZE=12345678`
- `function generate_file {`

External commands and harness APIs used by the scenario:
- `mfsmount`
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs_admin_master`
- `lizardfsXX`
- `mfssetgoal`
- `file-generate`
- `file-validate`
- `lizardfs_master_n`
- `lizardfs_shadow_synchronized`
- `lizardfs_master_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `mfsgetgoal`
- `lizardfsXX_chunkserver_daemon`

Assertions and expectations include:
- `assert_equals 1 $(lizardfs_admin_master info | grep $LIZARDFSXX_TAG | wc -l)`
- `assert_equals 2 $(lizardfs_admin_master list-chunkservers | grep $LIZARDFSXX_TAG | wc -l)`
- `assert_equals 1 $(lizardfs_admin_master list-mounts | grep $LIZARDFSXX_TAG | wc -l)`
- `assert_success lizardfsXX mfssetgoal 2 dir`
- `assert_success generate_file file0`
- `assert_success file-validate file0`
- `assert_eventually "lizardfs_shadow_synchronized 1"`
- `assert_equals 0 $(lizardfs_admin_master info | grep $LIZARDFSXX_TAG | wc -l)`
- `assert_success mkdir dir`
- `assert_equals "dir: $goal" "$(lizardfsXX mfssetgoal "$goal" dir || echo FAILED)"`
- `assert_equals "dir: $goal" "$(lizardfsXX mfsgetgoal dir || echo FAILED)"`
- `assert_equals "$expected" "$(lizardfsXX mfsgetgoal -r dir || echo FAILED)"`
- `assert_success generate_file file1`
- `assert_success file-validate file1`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 113 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for upgrade compatibility. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_lizardfs_upgrade_general.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_lizardfs_upgrade_new_mount_with_old_lizardfs.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_lizardfs_upgrade_new_mount_with_old_lizardfs.sh

## Purpose
This shell scenario exercises upgrade compatibility in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `lizardfs upgrade new mount with old lizardfs` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set 45 seconds`
- `CHUNKSERVERS=2`
- `MOUNTS=2`
- `START_WITH_LEGACY_LIZARDFS=YES`
- `USE_RAMDISK=YES`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `CHUNKSERVER_1_EXTRA_CONFIG="CREATE_NEW_CHUNKS_IN_MOOSEFS_FORMAT`
- `MASTER_EXTRA_CONFIG="CHUNKS_LOOP_TIME`
- `FILE_SIZE=12345678`
- `function generate_file {`

External commands and harness APIs used by the scenario:
- `mfsmount`
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs_admin_master`
- `lizardfsXX`
- `mfssetgoal`
- `file-generate`
- `file-validate`
- `lizardfs_mount_unmount`
- `lizardfs_mount_start`

Assertions and expectations include:
- `assert_equals 1 $(lizardfs_admin_master info | grep $LIZARDFSXX_TAG | wc -l)`
- `assert_equals 2 $(lizardfs_admin_master list-chunkservers | grep $LIZARDFSXX_TAG | wc -l)`
- `assert_equals 2 $(lizardfs_admin_master list-mounts | grep $LIZARDFSXX_TAG | wc -l)`
- `assert_success lizardfsXX mfssetgoal 2 dir0`
- `assert_success generate_file file0`
- `assert_success file-validate file0`
- `assert_success lizardfs_mount_unmount 1`
- `assert_success lizardfs_mount_start 1`
- `assert_success lizardfsXX mfssetgoal 2 dir1`
- `assert_success generate_file file1`
- `assert_success file-validate file1`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 58 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for upgrade compatibility. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_lizardfs_upgrade_new_mount_with_old_lizardfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_long_readdir.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_long_readdir.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for long readdir in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `long readdir` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `timeout_set '6 minutes'`
- `CHUNKSERVERS=1`
- `USE_RAMDISK=YES`
- `file_names() {`

External commands and harness APIs used by the scenario:
- `setup_local_empty_lizardfs`

Assertions and expectations include:
- `assert_no_diff "$(file_names | sort)" "$(ls | sort)"`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 19 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for long readdir. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_long_readdir.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_magic_auto_file_repair.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_magic_auto_file_repair.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for magic auto file repair in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `magic auto file repair` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `CHUNKSERVERS=1`
- `USE_RAMDISK="YES"`
- `MASTER_EXTRA_CONFIG="MAGIC_AUTO_FILE_REPAIR`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `FILE_SIZE=1K`
- `MESSAGE="Check`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `file-generate`
- `lizardfs_chunkserver_daemon`
- `lizardfs_wait_for_all_ready_chunkservers`
- `file-overwrite`
- `file-validate`

Assertions and expectations include:
- `assert_equals 2 $(find_all_chunks | grep '_00000001.' | wc -l)`
- `assert_equals 2 $(find_all_chunks | grep '_00000002.' | wc -l)`
- `assert_equals 1 $(egrep 'master.fs.file_auto_repaired: [0-9]+ 1' "$TEMP_DIR/log" | wc -l)`
- `assert_equals 2 $(egrep 'master.fs.file_auto_repaired: [0-9]+ 1' "$TEMP_DIR/log" | wc -l)`
- `assert_equals 2 $(egrep 'master.fs.file_auto_repaired' "$TEMP_DIR/log" | wc -l)`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 39 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for magic auto file repair. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_magic_auto_file_repair.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_many_serverrooms.sh -->
# sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_many_serverrooms.sh

## Purpose
This shell scenario exercises ShortSystemTests scenario coverage for many serverrooms in the LizardFS bash test harness. The script is part of `ShortSystemTests` and focuses on `many serverrooms` using a temporary cluster prepared by `tools/test_main.sh`.

## Important APIs, Types, and Functions
Harness configuration and local helpers detected in the full file:
- `USE_RAMDISK=YES`
- `CHUNKSERVERS=9`
- `CHUNKSERVER_LABELS="0,1,2:sr1|3,4,5:sr2|6,7,8:sr3"`
- `MASTER_CUSTOM_GOALS="10`
- `MOUNT_EXTRA_CONFIG="mfscachemode=NEVER"`
- `FILE_SIZE="$size"`

External commands and harness APIs used by the scenario:
- `mfscachemode`
- `setup_local_empty_lizardfs`
- `lizardfs`
- `file-generate`
- `lizardfs_chunkserver_daemon`
- `file-validate`

Assertions and expectations include:
- `FILE_SIZE="$size" assert_success file-generate "${info[mount0]}/dir/file_$size"`
- `assert_success lizardfs_chunkserver_daemon "$csid" stop &`
- `assert_success file-validate  "${info[mount0]}/dir/file_"*`

## Control Flow
The script is read by `run-test.sh`, which sources `tools/test_main.sh`, calls `test_begin`, sources this file, and then calls `test_end`. Within its 24 lines, this scenario typically sets cluster size or feature knobs, prepares files/directories under `${info[mountN]}`, mutates LizardFS state through CLI or daemon helpers, and validates the resulting state with harness assertions. Sourced fragments are:
- No extra source/template file was detected.

## State and Persistence Behavior
The test mutates only the ephemeral LizardFS test installation and its temporary mounts unless it explicitly invokes external system services. Persistent signals under test may include metadata files, chunk files on temporary chunkserver disks, generated workload files, daemon logs, quotas, ACLs, labels, and admin/probe output. The harness cleanup path is responsible for unmounting, stopping daemons, and deleting temporary state after the scenario.

## Dependencies and Integration Points
This test integrates with the common bash harness, generated constants from `set_lizardfs_constants.sh`, LizardFS command-line tools, local daemons, and the gtest wrapper. Any listed source/template dependencies must remain compatible with the variables set here. Environment prerequisites come from `setup_machine.sh` and may include FUSE permissions, helper users, loop disks, ramdisk, and optional external packages.

## Risks and Edge Cases
Primary risks are timing-sensitive assertions, daemon restart races, assumptions about available loop/ramdisk space, and template wrappers hiding important control flow. Tests touching upgrades, NFS, build tools, network ports, or destructive chunk/metadata edits are especially sensitive to host configuration and cleanup reliability.

## Test Signals
Passing this script is a regression signal for ShortSystemTests scenario coverage for many serverrooms. Failures should be triaged using the gtest error file, per-test logs in the error directory, daemon logs, and any files copied to `TEST_OUTPUT_DIR`. The most useful follow-up checks are the extracted assertion lines above plus the final LizardFS metadata/chunkserver/probe state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/tests/test_suites/ShortSystemTests/test_many_serverrooms.sh -->
