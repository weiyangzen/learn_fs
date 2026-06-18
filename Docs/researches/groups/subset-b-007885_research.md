# Research: subset-b-007885

Grouped research for Tahoe-LAFS integration files under `sources/distributed-fs/tahoe-lafs/integration`. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_get_put.py -->
# sources/distributed-fs/tahoe-lafs/integration/test_get_put.py

## Purpose
Integration coverage for Tahoe CLI upload/download paths, especially binary data through stdin/stdout, large immutable files, and compatibility between old and current immutable segment-size defaults.

## Important APIs, Types, and Functions
`DATA` is intentionally non-UTF-8 binary input. `get_put_alias` creates the `getput:` alias once per session through `util.cli`. `read_bytes` verifies byte-preserving output. The tests use `subprocess.Popen`, `check_call`, and `check_output` directly for stream-oriented CLI behavior, plus `blockingCallFromThread` to call `alice.reconfigure_zfec` from tests decorated with `run_in_thread`.

## Control Flow
The stdin test starts `tahoe put - getput:fromstdin`, writes `DATA` to the child stdin, waits for exit code 0, then downloads to a temp file. The stdout test uploads from a temp file, then runs `tahoe get getput:tostdout -` and compares stdout bytes. The large-file test writes `DATA * 1_000_000`, uploads it by path, downloads by path, and compares full file bytes. The segment-size test uploads and downloads the same multi-megabyte payload while toggling `shares._max_immutable_segment_size_for_testing` between 1 MiB and 128 KiB.

## State and Persistence
The alias and remote objects persist inside Alice's Tahoe node for the test session. The segment-size test mutates Alice's `tahoe.cfg` and restarts the node via `reconfigure_zfec`, so later tests depending on the same fixture may observe changed ZFEC state unless their fixtures reset it.

## Dependencies and Integration Points
Depends on the `tahoe` executable, Alice's node directory, Twisted reactor interop, and the Tahoe CLI semantics for `put`, `get`, aliases, stdin `-`, and stdout `-`.

## Risks
Direct subprocess use bypasses the common `util.run_tahoe` error wrapper in several tests. Large stdout comparisons can be memory-heavy. Reconfiguration is reactor-sensitive and may be platform-sensitive, especially because tests run blocking code in worker threads.

## Test Signals
Strong signals are exact byte equality, successful process exit codes, and cross-version segment-size compatibility for immutable uploads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_get_put.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_grid_manager.py -->
# sources/distributed-fs/tahoe-lafs/integration/test_grid_manager.py

## Purpose
Exercises the Grid Manager CLI and Grid Manager certificate enforcement in live Tahoe grids. It verifies key creation, certificate signing, client add/remove behavior, public identity reporting, and storage-server acceptance/rejection based on signed certificates.

## Important APIs, Types, and Functions
`_run_gm` runs `allmydata.cli.grid_manager` in a subprocess, optionally under coverage, and raises `util.ProcessFailed` with combined output on non-zero exit. The tests use `ed25519.signing_keypair_from_string`, `ed25519.string_from_verifying_key`, `base32.a2b`, and `configutil.get_config`. The grid scenarios use `create_grid`, storage node `restart`, `grid.add_client`, and `util.run_tahoe admin add-grid-manager-cert`.

## Control Flow
Certificate tests create a Grid Manager config on stdin, add named storage-server public keys, sign certificates, then verify signatures with the Grid Manager public key. File-backed config tests create a config directory and inspect `config.json` after add/remove operations. Rejection setup builds a two-server grid but gives only one server a valid certificate, configures client `diana` with happy=2 and the Grid Manager public key, and expects upload failure with `UploadUnhappinessError`. Acceptance setup signs both servers, restarts them, configures client `freya`, and expects upload success. Identity test compares the CLI-reported public key to the key derived from stored private config.

## State and Persistence
Grid Manager state is either streamed through stdin/stdout JSON or persisted in a temp config directory as `config.json`. Storage servers persist certs in their node directories and require restart for cert changes. Client trust roots are persisted in `tahoe.cfg` under `[grid_managers]`.

## Dependencies and Integration Points
Integrates Grid Manager CLI, Tahoe admin CLI, Ed25519 certificate primitives, storage node key files (`node.pubkey`), Tahoe config writing, and live grid/client lifecycle from `integration.grid` and `integration.util`.

## Risks
The enforcement tests are helper-named with leading underscores and may rely on external collection or manual enabling. They are expensive because they create and restart multiple nodes. The failure assertion accepts only `UploadUnhappinessError`; unrelated process failures are re-raised as generic assertion failures with limited diagnosis.

## Test Signals
Signals include valid Ed25519 signatures, expected JSON storage-server membership, exact public-key byte equality, upload rejection when one certified server cannot satisfy happiness, and upload success when all required servers have certificates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_grid_manager.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_i2p.py -->
# sources/distributed-fs/tahoe-lafs/integration/test_i2p.py

## Purpose
Defines integration support for I2P transport testing: local i2pd startup, I2P introducer creation, anonymous node creation, and a skipped end-to-end storage exchange over I2P.

## Important APIs, Types, and Functions
`i2p_network` starts `purplei2p/i2pd:release-2.45.1` via Docker and waits for `_MagicTextProtocol("ephemeral keys")`. `i2p_introducer` creates and runs an introducer with `--listen=i2p`, rewrites config via `read_config`, and waits for "introducer running". `i2p_introducer_furl` polls for `private/introducer.furl`. `_create_anonymous_node` creates a hidden-IP I2P node and writes a minimal config. `test_i2p_service_storage` is skipped.

## Control Flow
Module-level skips disable all tests when Docker is unavailable or on Windows. The network fixture launches i2pd with a bad reseed URL so it remains local. The introducer fixture creates an introducer directory if absent, configures web/logging settings, runs it, and terminates it on finalization. The skipped test creates two anonymous nodes, uploads a file through one CLI process, extracts the capability from stdout, downloads through the other, and compares bytes.

## State and Persistence
Temporary introducer and node directories contain Tahoe config, introducer furl, web port, and log gatherer settings. Docker runs as an external process and is cleaned up by INT. Node configs enable `[i2p]`.

## Dependencies and Integration Points
Requires Docker, a specific i2pd image, Tahoe runner, Twisted process management, `write_introducer`, `read_config`, `FilePath`, and allocated web ports.

## Risks
The only end-to-end test is explicitly skipped because I2P tests are nonfunctional. Fixed Docker host port `7656` can conflict with local services. Polling for furl creation has no explicit timeout. Cleanup depends on process signaling and Twisted deferred completion.

## Test Signals
Current live signal is fixture startup readiness. If unskipped, the intended signal is successful capability transfer: upload through Carol and byte-identical retrieval through Dave over I2P.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_i2p.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_servers_of_happiness.py -->
# sources/distributed-fs/tahoe-lafs/integration/test_servers_of_happiness.py

## Purpose
Checks that an upload fails when a client's `shares.happy` requirement exceeds the number of available storage servers.

## Important APIs, Types, and Functions
Uses `util._create_node` to create a non-storage client `edna` with needed=3, happy=7, total=10, `util.await_client_ready` for readiness, and `_CollectOutputProtocol` to capture CLI output. `util.ProcessFailed` is the expected failure path.

## Control Flow
The test creates and starts Edna against the shared introducer and storage nodes, waits until it sees the grid, then spawns `allmydata.scripts.runner -d edna put __file__`. It expects the process deferred to fail, asserts `UploadUnhappinessError` appears in the captured output, and verifies the user-facing placement message mentions shares could be placed on only too few servers.

## State and Persistence
Creates a temp node directory named `edna` with Tahoe config reflecting the high happiness requirement. The attempted upload should not result in a successful immutable file capability.

## Dependencies and Integration Points
Depends on existing storage-node fixtures, introducer furl, flog gatherer, Tahoe CLI upload, and the upload happiness algorithm.

## Risks
The test assumes the fixture grid has fewer than seven usable storage servers. If future fixtures scale up, the failure assumption changes. It captures both stdout and stderr and relies on message substrings that may change with error formatting.

## Test Signals
The primary signal is a failed CLI upload containing `UploadUnhappinessError`; the secondary signal is human-readable placement diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_servers_of_happiness.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_sftp.py -->
# sources/distributed-fs/tahoe-lafs/integration/test_sftp.py

## Purpose
Validates Tahoe-LAFS SFTP access using Paramiko: authentication behavior, SSH-key login, file read/write, directory mutation, and rename semantics.

## Important APIs, Types, and Functions
`connect_sftp` creates a Paramiko `SSHClient`, disables agent/key discovery, accepts host keys automatically, and returns an `SFTPClient`. It also recursively removes previous root contents. `sftp_client_key` loads Alice's generated private key from `private/ssh_client_rsa_key`. Tests use `generate_ssh_key` for bad-key setup and `run_in_thread` around blocking Paramiko calls.

## Control Flow
Authentication tests attempt invalid usernames/passwords and invalid key/username combinations, expecting `AuthenticationException`. The positive key test logs in as `alice-key` and expects an empty directory. File tests write bytes in multiple calls and read them back in chunks. Directory tests create a child directory, create files, change directories, read nested files, remove files, and attempt directory removal. Rename tests create `dir/file`, rename the file and then the directory, and read content at the final path.

## State and Persistence
All SFTP operations modify Tahoe mutable directory state exposed as Alice's SFTP root. `connect_sftp` tries to clean the root before each test, which mutates shared state and reduces test isolation issues from previous failures.

## Dependencies and Integration Points
Depends on Alice's Tahoe SFTP server listening on localhost port 8022, Paramiko transport/SFTP implementation, Tahoe account configuration for `alice-key`, and the test helper SSH key material.

## Risks
The hard-coded port 8022 can conflict or fail if Alice's fixture changes. Recursive root cleanup may mask leakage between tests and can be destructive within the test grid. `AutoAddPolicy` is acceptable for local integration tests but does not validate host identity.

## Test Signals
Signals are Paramiko authentication failures/successes, exact byte reads, directory listings, and successful final reads after file and directory renames.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_sftp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_streaming_logs.py -->
# sources/distributed-fs/tahoe-lafs/integration/test_streaming_logs.py

## Purpose
Tests the private WebSocket streaming log endpoint by authenticating with Alice's API token, provoking a log event, and requiring a JSON message before connection close.

## Important APIs, Types, and Functions
`_url_to_endpoint` maps a WebSocket URL to `HostnameEndpoint`. `_StreamingLogClientProtocol` reports open, first message, and close through Deferreds. `_connect_client` builds an Autobahn `WebSocketClientFactory` with `Authorization: <SCHEME> <api_auth_token>`. `_race` returns a `Left` or `Right` wrapper for whichever Deferred fires first and cancels the loser.

## Control Flow
`_test_streaming_logs` reads Alice's `node.url` and private `api_auth_token`, converts HTTP URL to WS URL, connects to `private/logs/v1`, prepares close/message Deferreds, makes a normal HTTP GET with `treq` to generate a log event, then asserts the race resolves to `Right` and the payload parses as JSON.

## State and Persistence
Reads node config/private config but does not modify persistent Tahoe state. The only state is live WebSocket connection state and transient log events.

## Dependencies and Integration Points
Depends on Autobahn WebSocket client, Twisted endpoint connection, Tahoe private web API auth scheme, `treq`, and Alice's web node configuration.

## Risks
Race logic is sensitive to connection close timing. The test validates only that some first payload is JSON, not schema content. It uses private API token material and will fail if auth scheme formatting changes.

## Test Signals
The key signal is receiving a JSON log payload before the WebSocket closes after a web request provokes logging.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_streaming_logs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_tor.py -->
# sources/distributed-fs/tahoe-lafs/integration/test_tor.py

## Purpose
End-to-end integration for Tor transport: onion-service storage nodes and anonymous client access to a normal grid.

## Important APIs, Types, and Functions
`test_onion_service_storage` creates two anonymous Tor nodes and exchanges data between them. `upload_to_one_download_from_the_other` is an async helper that shells out to Tahoe `put` and `get`, comparing downloaded bytes. `_create_anonymous_node` creates a node with `--hide-ip`, `--listen tor`, Tor control port, and share parameters, then writes Tor onion config before starting the node.

## Control Flow
Windows is skipped at module level; `test_anonymous_client` is skipped on macOS. Onion-service storage creates Carol and Dave with total shares 2, waits up to 600 seconds for both to see two servers, uploads through Carol, downloads through Dave. The anonymous-client test creates a normal storage node, then an anonymized Tor client with total shares 1, waits up to 1200 seconds, and downloads data uploaded through the normal node.

## State and Persistence
Each anonymous node gets a temp node directory with introducer data, web port, base Tahoe config, and `[tor]` settings including onion private key path. Uploads create real Tahoe capabilities and shares in the fixture grid.

## Dependencies and Integration Points
Requires the `tor_network` fixture and its `client_control_endpoint`, Tahoe runner, introducer fixtures, `write_introducer`, `basic_node_configuration`, client readiness polling, and Twisted process protocols.

## Risks
Transport tests are slow and platform-sensitive. The helper includes a TODO questioning whether Tor usage is actually proven. Long readiness timeouts increase CI duration. Hard-coded web/onion external ports can conflict in parallel runs.

## Test Signals
Signals are readiness with required server counts and byte-identical transfer across nodes when one or both nodes are configured to use Tor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_tor.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_vectors.py -->
# sources/distributed-fs/tahoe-lafs/integration/test_vectors.py

## Purpose
Verifies deterministic Tahoe capability generation against stored test vectors for combinations of convergence secrets, ZFEC parameters, plaintext samples, segment size, and object formats.

## Important APIs, Types, and Functions
`test_convergence` validates 16-byte convergence secrets. `test_capability` parametrizes over `vectors.capabilities.items()`, reconfigures Alice, uploads data with `util.upload`, and compares the capability string. `skiptest_generate` is a disabled helper for regenerating vectors. `generate` is an async generator that iterates cases, reconfigures ZFEC, customizes mutable formats, uploads, and yields `(case, cap)`.

## Control Flow
For each vector case, Alice is restarted if needed with `(happy=1, required, total)`, the case convergence secret, and case segment size. Data is uploaded in the requested CHK/SSK format, and the resulting cap must exactly match the stored expected value. The generator constructs a Cartesian product from parameter lists and incrementally rewrites the vector YAML through `vectors.save_capabilities`.

## State and Persistence
Tests mutate Alice's share configuration and convergence secret. The skipped generator can persist new vector data to `integration/vectors/test_vectors.yaml` if deliberately enabled.

## Dependencies and Integration Points
Depends on vector model/parameters modules, stored vector YAML exposed by `vectors.capabilities`, `attrs.evolve`, pytest-twisted async bridging, `integration.grid.Client`, and `util.upload`.

## Risks
The exact-capability assertion is intentionally brittle and will catch any cryptographic, encoding, segment-size, or serialization change. The generator path appears more fragile than the test path because it calls `upload(alice.process, ...)` while `util.upload` expects an object with a `.process` attribute in current usage.

## Test Signals
Signals include convergence-secret shape validation and exact equality between generated and known capability strings for all slow vector cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_vectors.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_web.py -->
# sources/distributed-fs/tahoe-lafs/integration/test_web.py

## Purpose
Broad black-box WebAPI coverage originally added for Python 3 porting. It validates index endpoints, uploads/downloads, status and operations pages, deep check/repair, storage and introducer pages, directory creation with children, and deterministic directory capabilities when private RSA keys are supplied.

## Important APIs, Types, and Functions
Uses `requests` for blocking HTTP, `util.web_get`/`web_post`/`node_url`, `html5lib` and BeautifulSoup for HTML inspection, `allmydata.uri` for capability parsing, Tahoe RSA helpers (`create_signing_keypair`, `der_string_from_signing_key`), and `derive_mutable_keys`. `DATA_PATH` points at Tahoe test RSA PEM fixtures. `test_directory_deep_check` uses `pytest_twisted.ensureDeferred` and `deferToThread` so blocking HTTP work runs off the reactor.

## Control Flow
The file first verifies root index HTML and JSON. Upload tests POST or PUT file content to `/uri`, parse returned CHK or mutable caps, and fetch by readcap. Status tests upload/download content, parse `/status`, follow upload/download links, and inspect event JSON byte counts. Deep stats and deep check tests create mutable directories, upload files, start operation handles, poll `/operations/<handle>` or returned URLs until completion, and validate JSON/HTML outputs. Storage and introducer tests fetch their web pages and JSON summaries. Directory-construction tests create child metadata JSON and call `mkdir-with-children`. Private-key tests base64-url encode DER RSA private keys and assert the resulting directory cap's writekey/fingerprint, including exact known caps for fixed PEM keys.

## State and Persistence
Creates directories, immutable files, mutable files, operation handles, and upload/download status entries in Alice's node and storage grid. Some tests reconfigure Alice's ZFEC parameters before deep-check. Known private-key tests rely on stable PEM fixture files and deterministic mutable key derivation.

## Dependencies and Integration Points
Integrates Tahoe WebAPI routes `/`, `/uri`, `/status`, `/storage`, `/operations`, helper status, introducer root JSON, mutable directory capabilities, RSA key serialization, and web configuration files such as `node.url`.

## Risks
The file comments explicitly state that many assertions encode historical behavior rather than a coherent WebAPI contract. Polling loops have fixed retry counts. HTML assertions are shallow and may be brittle to presentation changes. Private-key capability tests are intentionally exact and will fail on serialization or derivation changes. Blocking requests require `run_in_thread` or `deferToThread` to keep Twisted process IO alive.

## Test Signals
Signals include 2xx HTTP responses, JSON parseability, exact content round trips, expected capability classes and share counts, operation completion statistics, storage reserved-space value, introducer summary keys, and deterministic RSA-derived directory caps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/test_web.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/util.py -->
# sources/distributed-fs/tahoe-lafs/integration/util.py

## Purpose
Shared integration-test infrastructure for spawning Tahoe processes, collecting output, managing node lifecycle, waiting for readiness/filesystem events, performing HTTP/CLI operations, generating SSH/RSA keys, representing upload formats, and reconfiguring nodes.

## Important APIs, Types, and Functions
Process helpers include `block_with_timeout`, `dump_python_output`, `dump_output`, `_ProcessExitedProtocol`, `ProcessFailed`, `_CollectOutputProtocol`, `_DumpOutputProtocol`, and `_MagicTextProtocol`. Tahoe lifecycle APIs include `run_tahoe`, `_tahoe_runner_optional_coverage`, `TahoeProcess`, `_run_node`, `basic_node_configuration`, and `_create_node`. Blocking helpers include `run_in_thread`, `await_file_contents`, `await_files_exist`, `await_file_vanishes`, `cli`, `node_url`, `web_get`, `web_post`, and `await_client_ready`. Crypto/format helpers include `generate_ssh_key`, `CHK`, `SSK`, `upload`, `reconfigure`, and `generate_rsa_key`.

## Control Flow
Subprocesses are spawned through Twisted reactors, with output either collected into memory, dumped to stdout, or watched for a magic readiness string. `_create_node` invokes `create-node`, applies common config, then starts the node. `_run_node` starts `tahoe run` with Eliot logging and registers cleanup finalizers. `await_client_ready` polls the web JSON status until enough recently active servers are visible. `reconfigure` compares desired shares/convergence/segment-size settings against current config, writes only changed values, restarts if needed, and waits for readiness.

## State and Persistence
Writes Tahoe node directories, `tahoe.cfg`, private convergence config, Eliot logs, generated SSH keys, temporary RSA key files for mutable upload, and uploaded Tahoe shares/capabilities. It also registers pytest finalizers that terminate live node processes.

## Dependencies and Integration Points
Core dependencies are Twisted process/deferred APIs, pytest-twisted, requests, Paramiko, cryptography RSA serialization, Tahoe config utilities, Tahoe client config reader, and `allmydata.scripts.runner`. This file is the central integration point used by most tests in the directory.

## Risks
Several helpers mix blocking and asynchronous code; using them outside `run_in_thread`/Deferred contexts can stall the reactor or fill process output buffers. `_MagicTextProtocol` readiness depends on log text. `await_client_ready` assumes status JSON shape and wall-clock liveness. `upload` is typed as accepting `TahoeProcess` but current test usage passes a grid client with `.process`, so callers must match the actual wrapper shape. Cleanup blocks on process exit and can hang until timeout if a process ignores termination.

## Test Signals
This is support code rather than a test file; its signals are reliable process failure propagation, captured stdout/stderr, readiness polling success, exact file appearance/content waits, HTTP 2xx enforcement, and deterministic key/format argument generation for higher-level tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/vectors/__init__.py -->
# sources/distributed-fs/tahoe-lafs/integration/vectors/__init__.py

## Purpose
Package facade for vector-related constants, data types, serialization helpers, loaded capabilities, and maximum share metadata.

## Important APIs, Types, and Functions
Defines `__all__` and re-exports `DATA_PATH`, `CURRENT_VERSION`, `Case`, `Sample`, `SeedParam`, `encode_bytes`, `save_capabilities`, `capabilities`, and `MAX_SHARES` from sibling modules.

## Control Flow
Import-time work is limited to importing names from `.vectors` and `.parameters`. Any YAML loading side effects belong to `.vectors`, not this facade.

## State and Persistence
No local persistence. It exposes persisted vector state through `capabilities` and `DATA_PATH`.

## Dependencies and Integration Points
Used by `test_vectors.py` as `from . import vectors`, allowing tests to access a curated package-level API without reaching into implementation modules.

## Risks
Facade drift is the main risk: adding new vector model names without updating `__all__` or imports can make package-level consumers fail.

## Test Signals
Indirect signal is successful import and access to vector constants/classes by `test_vectors.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/vectors/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/vectors/model.py -->
# sources/distributed-fs/tahoe-lafs/integration/vectors/model.py

## Purpose
Defines small immutable data models used to describe vector inputs and ZFEC parameters.

## Important APIs, Types, and Functions
`MAX_SHARES` is a symbolic sentinel. `Sample` stores a seed byte string and target length. `Param` stores realized `required` and `total` share counts. `SeedParam` stores `required` and either a concrete total or `MAX_SHARES`; `realize(max_total)` returns a concrete `Param`.

## Control Flow
The only logic is `SeedParam.realize`: substitute `max_total` when `total == MAX_SHARES`, otherwise preserve the configured total.

## State and Persistence
No persistence. Instances are frozen `attrs` values suitable as deterministic vector-case components.

## Dependencies and Integration Points
Depends on `attrs.frozen` and Python union types. Used by parameter definitions and vector serialization/loading.

## Risks
`MAX_SHARES` is a string sentinel, so accidental user-supplied string equality could trigger substitution. There is no validation that `required <= total` or that totals are within CHK/SSK bounds; callers are responsible for using valid parameter sets.

## Test Signals
Signals come indirectly from vector generation and capability tests; incorrect realization changes produced capabilities or causes upload failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/vectors/model.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/vectors/parameters.py -->
# sources/distributed-fs/tahoe-lafs/integration/vectors/parameters.py

## Purpose
Defines the deterministic input space for capability test-vector generation: convergence secrets, segment size, plaintext object samples, ZFEC parameters, and CHK/SSK formats.

## Important APIs, Types, and Functions
`digest` and `hexdigest` wrap SHA-256. `CONVERGENCE_SECRETS` contains two 16-byte secrets. `SEGMENT_SIZE` is 128 KiB. `OBJECT_DESCRIPTIONS` contains `Sample` values chosen around literal/segment/multi-segment boundaries. `ZFEC_PARAMS` contains several `SeedParam` values including `MAX_SHARES`. `FORMATS` includes `CHK()`, `SSK(name="sdmf", key=None)`, and `SSK(name="mdmf", key=None)`.

## Control Flow
The module constructs constants at import time. `test_vectors.skiptest_generate` later forms a Cartesian product across these constants to generate vector cases.

## State and Persistence
No direct persistence, but changing any constant changes the vector-generation space and requires regenerating stored capabilities.

## Dependencies and Integration Points
Depends on `hashlib.sha256`, vector model classes, and upload format adapters from `integration.util`. Integrated by `test_vectors.py` for validation and generation.

## Risks
The chosen values encode a compatibility contract. Any change in order or content can make the stored YAML incomplete or stale. `MAX_SHARES` must be realized against each format's maximum because CHK and mutable SSK formats have different limits.

## Test Signals
Signals are convergence secret shape checks and exact capability matches across all combinations selected from these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/integration/vectors/parameters.py -->
