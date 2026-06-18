# Research: subset-b-007890 Tahoe-LAFS support, configuration, crypto, client, directory, and SFTP files

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/simulators/storage-overhead.py -->
# sources/distributed-fs/tahoe-lafs/misc/simulators/storage-overhead.py

## Purpose

This standalone simulator estimates Tahoe-LAFS immutable-file storage overhead for a given file size. It reports URI length, one-share allocated size, total allocated share space across all shares, ideal expansion, and effective expansion. It is an operational/modeling helper rather than production node code.

## Important APIs, Types, And Functions

`roundup(size, blocksize=4096)` rounds share allocations to disk blocks. `BigFakeString` is a seek/tell-only fake file object used to satisfy uploader encoder setup without holding real data. `calc(filesize, params=(3,7,10), segsize=DEFAULT_IMMUTABLE_MAX_SEGMENT_SIZE)` is the main API; it switches between literal-file URI accounting and CHK share accounting. `main()` prints one calculation from `sys.argv[1]`, and `chart()` emits CSV-like rows for geometrically increasing file sizes.

## Control Flow

The script parses the first command-line argument. If it is `chart`, `chart()` loops from size 2 to under 1 MiB, calling `calc()` and printing expansion. Otherwise `main()` converts the argument to an integer, calls `calc()`, and prints human-readable fields. In `calc()`, files at or below `upload.Uploader.URI_LIT_SIZE_THRESHOLD` are represented as literal URIs with no shares. Larger files instantiate `upload.FileUploader`, configure erasure-coding parameters, install the fake file handle and a fixed encryption key, run encoder setup, and then compute share allocation metadata and URI size.

## State And Persistence

The file owns no persistent state. It mutates only the fake file pointer in `BigFakeString`, the local `FileUploader`, and command-line output. It uses fixed dummy key/storage-index bytes for sizing, not for security.

## Dependencies And Integration Points

It depends on `allmydata.uri`, `allmydata.storage`, `allmydata.immutable.upload`, `DEFAULT_IMMUTABLE_MAX_SEGMENT_SIZE`, and `mathutil`. The constants and uploader behavior tie the simulator to Tahoe-LAFS immutable upload internals and share layout assumptions.

## Risks

The simulator reaches into upload internals (`FileUploader(None)`, `set_filehandle`, `setup_encoder`) and comments that this was changed, so it can drift when uploader APIs or share layout change. The extension size is hard-coded as 429 bytes, making the output stale if URI extension serialization changes. `sys.argv[1]` is accessed unconditionally, so missing arguments raise `IndexError`.

## Test Signals

Useful checks are running the script for small literal sizes, boundary sizes around `URI_LIT_SIZE_THRESHOLD`, large files across segment boundaries, and `chart` output. Regression tests should compare monotonicity and known expansion values after changes to immutable upload layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/simulators/storage-overhead.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/windows-enospc/passthrough.py -->
# sources/distributed-fs/tahoe-lafs/misc/windows-enospc/passthrough.py

## Purpose

This Windows helper passes stdin to stdout using Twisted's Windows-aware stdio machinery. It exists to avoid ENOSPC errors that can occur when writing to non-blocking pipes through Unix-like APIs on Windows.

## Important APIs, Types, And Functions

`Passthrough` implements `IHalfCloseableProtocol`. `dataReceived()` writes received bytes to the transport, `readConnectionLost()` closes output, and `writeConnectionLost()`/`connectionLost()` stop the reactor while tolerating `ReactorNotRunning`. At module import/run time, `StandardIO(Passthrough())` attaches the protocol to process stdio and `reactor.run()` starts the event loop.

## Control Flow

The module executes immediately. Twisted delivers stdin bytes to `dataReceived()`, which mirrors them to stdout. Half-close and full-close notifications shut down transport or reactor so the process exits after data transfer completes.

## State And Persistence

There is no durable state. Runtime state is Twisted reactor state and the protocol transport. The script does not buffer beyond Twisted's normal transport behavior.

## Dependencies And Integration Points

It depends on `twisted.internet.stdio.StandardIO`, `reactor`, `Protocol`, `IHalfCloseableProtocol`, `ReactorNotRunning`, and `zope.interface.implementer`. It is likely invoked as a subprocess in Windows-specific test or tooling paths.

## Risks

Because the reactor starts at import time, importing this module in tests would block. It assumes Twisted stdio is the desired pipe abstraction on the target Windows runtime. Exceptions from `transport.write()` are not translated, so unexpected transport errors propagate through Twisted logging.

## Test Signals

Exercise by piping binary and text data through the script on Windows, closing stdin early, closing stdout early, and verifying process exit without ENOSPC or hanging reactor failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/misc/windows-enospc/passthrough.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/mypy.ini -->
# sources/distributed-fs/tahoe-lafs/mypy.ini

## Purpose

This is Tahoe-LAFS's mypy configuration. It sets a permissive global baseline with selected strictness flags and then enables a much stricter profile for a few typed modules.

## Important APIs, Types, And Functions

The `[mypy]` section enables `ignore_missing_imports`, the `mypy_zope` plugin, pretty output, column numbers, error codes, no implicit optionals, redundant-cast warnings, and strict equality. A targeted module section applies strict checks such as `disallow_untyped_defs`, `check_untyped_defs`, `warn_return_any`, `no_implicit_reexport`, and `strict_concatenate` to `allmydata.test.cli.wormholetesting`, `allmydata.listeners`, and `allmydata.test.test_connection_status`.

## Control Flow

There is no runtime control flow. Mypy reads this file to decide which imports to ignore and which static-analysis checks to enforce per module pattern.

## State And Persistence

The file is static configuration. Its state is persisted in the repository and affects developer/CI type-check behavior, not Tahoe node runtime behavior.

## Dependencies And Integration Points

It integrates with mypy and `mypy_zope:plugin`, which is important for Zope interface-heavy code. The strict target list signals incremental typing adoption.

## Risks

`ignore_missing_imports = True` can hide missing or untyped dependency problems. The global baseline is not fully strict, so typed and untyped regions can diverge. The typo-like spacing in `warn_unused_configs =True` is accepted by config parsing but should be kept consistent if edited.

## Test Signals

Run mypy with this config and confirm the targeted modules still pass strict checks. Adding a new strict module should produce expected failures for untyped definitions and imports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/mypy.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/pyproject.toml -->
# sources/distributed-fs/tahoe-lafs/pyproject.toml

## Purpose

This is the package, build, dependency, script, and optional-extra definition for Tahoe-LAFS. It declares project metadata, runtime requirements, command entry points, optional Tor/I2P/build/test dependencies, hatch-vcs versioning, and wheel contents.

## Important APIs, Types, And Functions

The `[project]` table names the package `tahoe-lafs`, uses dynamic versioning, requires Python `>=3.9`, declares GPL-related licensing, and lists classifiers. `dependencies` is the core runtime contract: zfec, zope.interface, Foolscap, cryptography, pyOpenSSL, Twisted with `tls,conch`, PyYAML, six, magic-wormhole, eliot, attrs, Autobahn, Klein/Werkzeug/treq, CBOR/CDDL libraries, Click, psutil, filelock, Windows `pywin32`, and Python 3.13 `legacy-cgi`. `[project.scripts]` exposes `tahoe` and `grid-manager`. Optional extras cover `tor`, `i2p`, `build`, `testenv`, and `test`. Hatch configuration derives versions from VCS tags and writes `src/allmydata/_version.py`; build include/exclude lists define source distributions and wheels.

## Control Flow

Build frontends read `[build-system]`, load hatchling and hatch-vcs, calculate a version from tags matching `tahoe-lafs-(.*)`, and package `src/allmydata` into wheels. Installers resolve project dependencies and extras. Console-script generation points invocations to `allmydata.scripts.runner:run` and `allmydata.cli.grid_manager:grid_manager`.

## State And Persistence

The file persists dependency and packaging policy. It can generate persistent build artifacts and `_version.py` during build hooks, but it has no direct application runtime state.

## Dependencies And Integration Points

It is the central integration point for pip, build, hatchling, hatch-vcs, console scripts, CI, optional anonymity transports, the SFTP frontend, web frontend, and test tooling. Comments encode compatibility history for Foolscap, Twisted, cryptography, Werkzeug, cbor2, and Paramiko.

## Risks

Dependency comments document several fragile compatibility edges. Broad dependencies without upper bounds can admit regressions, while testenv pins can become stale. `Twisted[tls,conch]` is intentionally used to satisfy SFTP/manhole constraints, so changing extras can break SFTP installs. The direct Chutney git dependency in the test extra depends on external network and repository availability. Build include/exclude lists must stay synchronized with repository layout.

## Test Signals

Signals include `python -m build`, wheel install smoke tests, `tahoe --help`, `grid-manager --help`, extras resolution for `tor`, `i2p`, and `test`, and CI coverage across supported Python versions 3.9 through 3.12 plus any Python 3.13 compatibility lane.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/pyproject.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/pytest.ini -->
# sources/distributed-fs/tahoe-lafs/pytest.ini

## Purpose

This file declares pytest metadata for the Tahoe-LAFS test suite.

## Important APIs, Types, And Functions

The only configured marker is `slow`, described as tests not run by default and enabled with `--runslow`.

## Control Flow

Pytest reads this file during collection to register the marker and avoid unknown-marker warnings.

## State And Persistence

The file is static test configuration with no runtime state.

## Dependencies And Integration Points

It integrates with pytest and any local conftest/plugin logic that interprets `--runslow`.

## Risks

The marker description implies custom `--runslow` handling elsewhere; without that hook the marker alone does not skip slow tests. Adding markers in tests without updating this file can produce warnings or strict-marker failures.

## Test Signals

Run `pytest --markers` and confirm `slow` appears. Run normal pytest and `pytest --runslow` in the repository's supported test environment to confirm intended selection behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/pytest.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/release-tools/fetch-pr.py -->
# sources/distributed-fs/tahoe-lafs/release-tools/fetch-pr.py

## Purpose

This release helper fetches GitHub pull-request metadata, lists commit authors and commenters, and prints reStructuredText-style credit/link lines for release notes.

## Important APIs, Types, And Functions

`_find_pull_request_numbers()` reads PR numbers from arguments or tokens starting with `PR` on stdin. `_read_github_token()` reads a local `token` file containing username and token. `_initialize_headers()` creates API headers. `_report_authors()` fetches commit data and returns non-ignored author handles. `_report_helpers()` fetches comments and returns non-ignored commenter handles. `_request_pr_information()` loops over PRs and gathers coder/helper sets. `main(reactor)` orchestrates the process under Twisted `react()`.

## Control Flow

When executed, `react(main)` starts a Twisted reactor. `main()` reads credentials, builds headers, finds PR numbers, fetches each PR JSON from `https://api.github.com/repos/tahoe-lafs/tahoe-lafs/pulls/{}`, then follows `commits_url` and `comments_url`. It prints commit/comment diagnostics first, then sorted PR summary lines and reference definitions for PRs and GitHub handles.

## State And Persistence

The only local persisted input is the `token` file. The script writes no files; output is stdout. State is accumulated in local sets/dicts of PRs, authors, helpers, and unique handles.

## Dependencies And Integration Points

It depends on Twisted Deferreds/task reactor, `treq`, GitHub's REST API, JSON parsing, and Basic Authorization. It integrates with Tahoe release-note preparation.

## Risks

`_initialize_headers()` formats `base64.b64encode()` bytes directly into a string, which can produce a `b'...'` representation instead of the expected token unless handled by treq/Twisted in a forgiving way. It lacks HTTP status checks and assumes PR JSON contains expected keys. Rate limits, missing scopes, deleted users, pagination, and API schema changes can produce misleading output or exceptions. The printed label uses `contributers`, preserving a typo in comments only.

## Test Signals

Use a fake treq responder for PR, commits, and comments URLs; cover argv and stdin PR parsing; cover missing/malformed token file; verify ignored handles are excluded; and smoke-test against a known PR with a valid token.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/release-tools/fetch-pr.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/__init__.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/__init__.py

## Purpose

This package initializer exposes Tahoe-LAFS version metadata, applies third-party monkey patches, and configures BytesWarning handling for allmydata modules.

## Important APIs, Types, And Functions

`__all__` exports version and app-name symbols. `__version__`, `full_version`, and `branch` default to `"unknown"` and are optionally imported from generated `allmydata._version`. `__appname__` is `tahoe-lafs`, and `__full_version__` combines the app name with `__version__`. The module imports and calls `._monkeypatch.patch()`, then installs a warnings filter that turns `BytesWarning` into errors for modules matching `.*allmydata.*`.

## Control Flow

Importing `allmydata` attempts to import generated version values twice, tolerating `ImportError`. It computes `__full_version__`, applies monkey patches, deletes the local patch binding, and updates the warnings filter.

## State And Persistence

State is module-global version metadata and process-global warning filter state. There is no on-disk persistence from this file.

## Dependencies And Integration Points

It integrates with hatch-vcs-generated `_version.py`, application version announcements in client code, and any monkey-patches needed before the rest of Tahoe imports third-party libraries.

## Risks

Import-time side effects affect the whole process. Missing `_version.py` produces `"unknown"` metadata, which can weaken diagnostics and peer version reporting. Turning BytesWarnings into errors can surface only under `python -b`, so production/test differences remain possible.

## Test Signals

Import `allmydata` with and without `_version.py`, verify exported version strings, and run tests under `python -b` to ensure allmydata BytesWarnings fail as intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/__main__.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/__main__.py

## Purpose

This module makes `python -m allmydata` behave like the Tahoe-LAFS command-line entry point.

## Important APIs, Types, And Functions

It imports `run` from `allmydata.scripts.runner` and, when executed as `__main__`, exits with `sys.exit(run())`.

## Control Flow

The module has no behavior on import beyond imports. Under module execution, it calls the shared runner and propagates the returned exit code.

## State And Persistence

No local state or persistence is owned here.

## Dependencies And Integration Points

It integrates Python module execution with the same runner used by the `tahoe` console script declared in `pyproject.toml`.

## Risks

Any import error or behavior change in `allmydata.scripts.runner.run` directly affects `python -m allmydata`. There is no wrapper error handling here.

## Test Signals

Run `python -m allmydata --help` and compare behavior and exit status with the `tahoe --help` console script.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/__main__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/_monkeypatch.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/_monkeypatch.py

## Purpose

This file is the central hook for Tahoe-LAFS third-party monkey patches.

## Important APIs, Types, And Functions

`patch()` is the only function. In the current source it contains only a docstring and performs no patching.

## Control Flow

`allmydata.__init__` imports and calls `patch()` at package import time. Because the function body is empty, control immediately returns.

## State And Persistence

No state is modified in the current implementation.

## Dependencies And Integration Points

It is intentionally integrated into package import. Future compatibility shims for third-party libraries would likely be placed here to run before deeper Tahoe imports.

## Risks

The docstring says "Path third-party libraries", likely meaning "Patch". Adding real monkey patches here would create process-global import-time side effects and would need tight ordering tests. The current empty implementation can mislead readers expecting active compatibility logic.

## Test Signals

Import `allmydata` and verify no third-party objects are changed unexpectedly. If patches are later added, tests should assert idempotence and ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/_monkeypatch.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/blacklist.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/blacklist.py

## Purpose

This module implements storage-index-based access prohibition. It loads a blacklist file mapping base32 storage indexes to reasons, checks objects against it, and wraps prohibited file nodes with an object that lists safely but fails on content operations.

## Important APIs, Types, And Functions

`FileProhibited` carries a human-readable reason. `Blacklist` owns `blacklist_fn`, `last_mtime`, and `entries`; `read_blacklist()` reloads on first use or newer mtime, and `check_storageindex(si)` returns a reason if blocked. `ProhibitedNode` implements `IFileNode` and delegates identity/query methods to a wrapped node while making size/check operations harmless and mutating/download operations raise `FileProhibited`.

## Control Flow

A client creates `Blacklist` from the configured `access.blacklist` path. Each check calls `read_blacklist()`, which clears entries if the file is missing/unreadable or reloads non-comment lines as `storage-index reason`. `check_storageindex()` logs prohibited hits and returns the reason to callers that can substitute `ProhibitedNode`.

## State And Persistence

The persistent state is the external blacklist file. In-memory state caches entries and last modification time. `ProhibitedNode` keeps a wrapped node and reason but does not persist anything.

## Dependencies And Integration Points

The module depends on Twisted logging, Zope interface declarations, `IFileNode`/`IFilesystemNode`, Tahoe base32 utilities, and output quoting. It integrates with `client.init_blacklist()` and node construction paths that apply blacklist decisions.

## Risks

Malformed blacklist lines or invalid base32 raise after logging, potentially preventing access checks rather than failing open. Reload is based on mtime greater-than only, so coarse timestamp filesystems or same-time rewrites can leave stale entries. Missing/unreadable blacklist clears entries and permits access. `ProhibitedNode.check()` and repair methods return `None`, which callers must handle as a non-distributed or unavailable result.

## Test Signals

Cover missing file, comments/blank lines, valid reload, malformed line/base32 failure, mtime updates, prohibited download/overwrite/read failures, and directory listing behavior that still exposes wrapped identity without content access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/blacklist.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/check_results.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/check_results.py

## Purpose

This module provides result containers for file checks, check-and-repair operations, deep-check traversals, and deep-check-and-repair traversals. It adapts checker output into stable interfaces and serializable counters used by CLI/web/API consumers.

## Important APIs, Types, And Functions

`CheckResults` implements `ICheckResults` and stores URI, storage index, health/recoverability, share counters, server lists, share maps, corrupt/incompatible share lists, reports, share problems, and optional mutable servermap. `CheckAndRepairResults` implements `ICheckAndRepairResults` with pre/post results and repair flags. `DeepResultsBase` stores root storage index, aggregate result maps, corrupt shares, and stats. `DeepCheckResults.add_check()` and `get_counters()` aggregate plain checks. `DeepCheckAndRepairResults.add_check_and_repair()`, `get_counters()`, and `get_remaining_corrupt_shares()` aggregate repair-aware results.

## Control Flow

Checkers instantiate `CheckResults` with detailed counters and lists. The constructor validates URI/server interfaces and normalizes byte summaries to text. Deep traversal code calls `add_check()` or `add_check_and_repair()` for each distributed object; LIT/non-distributed falsey results are ignored. Each add method updates counters, stores path-indexed and storage-index-indexed results, and extends corrupt share lists. API consumers call getters or `as_dict()`/`get_counters()`.

## State And Persistence

All state is in-memory result data. There is no direct persistence, but these objects are serialized or rendered by higher-level web/CLI code. `all_results` is keyed by path tuple, and `all_results_by_storage_index` is keyed by raw storage index.

## Dependencies And Integration Points

It depends on interfaces from `allmydata.interfaces`, base32 encoding, and mutable `ServerMap` validation when servermap data is present. It integrates with file node `check`, repair, directory deep traversal, web status, and CLI reporting.

## Risks

The constructors rely heavily on assertions, which can be disabled with optimized Python and are not user-facing validation. `CheckAndRepairResults` initializes only `repair_attempted`; callers must set `repair_successful`, `pre_repair_results`, and `post_repair_results` before getters are used. Duplicate storage indexes overwrite previous entries in `all_results_by_storage_index`. Some result fields may contain bytes while API consumers expect JSON-friendly data.

## Test Signals

Construct healthy/unhealthy/recoverable/unrecoverable results, verify summary defaults and `as_dict()` server ID conversion, test corrupt/incompatible share propagation, ensure LIT falsey results are ignored in deep counters, and verify repair counters for attempted/successful/failed repairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/check_results.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/cli/__init__.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/cli/__init__.py

## Purpose

This is an empty package marker for `allmydata.cli`.

## Important APIs, Types, And Functions

The file defines no symbols.

## Control Flow

Importing `allmydata.cli` executes no package-specific code.

## State And Persistence

There is no state or persistence.

## Dependencies And Integration Points

Its presence makes the CLI package importable and allows sibling modules such as `grid_manager.py` to live under `allmydata.cli`.

## Risks

No direct behavioral risk. Adding import-time behavior here would affect every CLI submodule import.

## Test Signals

`import allmydata.cli` should succeed without side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/cli/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/cli/grid_manager.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/cli/grid_manager.py

## Purpose

This Click-based CLI manages Tahoe Grid Manager configuration, identity keys, storage-server entries, and signed certificates for servers.

## Important APIs, Types, And Functions

`grid_manager` is the root Click group and requires `--config/-c`, either a directory or `-` for stdin/stdout-style config. The nested `Config` object lazy-loads the grid manager via `load_grid_manager()`. Commands are `create`, `public_identity`, `add`, `remove`, `list`, and `sign`. `_config_path_from_option()` converts a path string to `FilePath` or `None`.

## Control Flow

The root command stores a lazy config object in `ctx.obj`. `create` creates and saves a new grid manager. `public_identity` prints the public key. `add` decodes a storage node public key and saves the updated config. `remove` removes the server and deletes certificate files named `{name}.cert.{n}` from the config directory. `list` prints server keys and certificate validity relative to `current_datetime_with_zone()`. `sign` creates a certificate with a bounded expiry in days, prints JSON, and writes the next available certificate file when config is directory-backed.

## State And Persistence

Persistent state is the grid-manager configuration directory or stdin/stdout-backed config represented by `None`. Commands mutate and save grid manager state, remove old cert files, and create new certificate files atomically enough for `FilePath.create()` to reject existing names.

## Dependencies And Integration Points

It depends on Click, Twisted `FilePath`, Tahoe Ed25519 helpers, `abbreviate_time`, `allmydata.grid_manager`, and `jsonbytes`. `pyproject.toml` exposes it as the `grid-manager` console script.

## Risks

The command named `list` shadows the built-in, hence the noqa. Removing a server deletes sequential certificate files only until the first missing index, so sparse certificate files can remain. `add` assumes ASCII public-key input and maps duplicate names to ClickException. `sign` writes certificate JSON after printing it; filesystem failure can leave printed-but-not-saved certificates. Expiry is capped at five years by CLI policy.

## Test Signals

Use Click's test runner for create/add/remove/list/sign/public-identity, cover `--config -`, duplicate/missing server errors, invalid public keys, certificate file collision handling, sparse cert cleanup behavior, and expiry formatting for valid and expired certificates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/cli/grid_manager.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/client.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/client.py

## Purpose

This is the main Tahoe-LAFS client/server node construction module. It validates client-style configuration, builds network providers and Foolscap tubs, creates introducer clients and the storage broker, initializes storage server announcements and plugins, wires uploader/helper/web/SFTP services, manages secrets and node keys, and exposes high-level node creation/upload APIs.

## Important APIs, Types, And Functions

Configuration APIs include `_is_valid_section()`, `_client_config`, `_valid_config()`, `read_config()`, and `config_from_string`. Construction APIs are `create_client()` and async `create_client_from_config()`. Secret/key helpers are `_make_secret()`, `SecretHolder`, `KeyGenerator`, and `Terminator`. Storage/plugin APIs include `_StoragePlugins.from_config()`, `_sequencer()`, `create_introducer_clients()`, `create_storage_farm_broker()`, `_register_reference()`, `AnnounceableStorageServer`, `_add_to_announcement()`, `storage_enabled()`, and `anonymous_storage_enabled()`. `_Client` implements `IStatsProducer` and provides node lifecycle, storage, web, SFTP, nodemaker, upload, and filesystem-object factory methods.

## Control Flow

`create_client()` ensures the node directory exists, reads config, and delegates to `create_client_from_config()`. That function creates I2P/Tor providers, connection handlers, tub options, the main tub, introducer clients, and the storage broker; constructs `_Client`; then loads storage plugins and calls `client.init_storage()` before parenting providers, introducers, and broker under the client service. `_Client.__init__()` initializes stats, secrets, node keys, client internals, static servers, optional helper, optional SFTP, optional exit-trigger timer, optional web frontend, and storage NURL placeholders. `init_storage()` validates tub listening, registers anonymous and plugin storage references, builds announcements including grid-manager certificates, and publishes to all introducers.

## State And Persistence

The module reads and writes node-directory state: private lease/convergence secrets, `node.privkey`, `node.pubkey`, `api_auth_token`, `announcement-seqnum`, `permutation-seed`, storage fURLs, helper fURLs, `servers.yaml`, blacklist files, and service-specific configuration. Runtime state lives in Twisted services, the tub, introducer clients, storage broker, stats provider, history, terminator, uploader, nodemaker, helper, webish server, SFTP server, and optional exit-trigger timer. The API auth token is intentionally recreated on every node start.

## Dependencies And Integration Points

This file is a hub for `allmydata.node`, crypto RSA/Ed25519, `DirectoryNode`, storage server and client modules, immutable upload/offloaded helper, mutable file nodes, introducer client, configuration utilities, Tor/I2P providers, CPU threadpool, stats/history/nodemaker/blacklist, webish, SFTP frontend, Foolscap fURLs, Twisted services/reactor/deferreds, and Zope interfaces.

## Risks

Initialization order is delicate: storage plugins need a partially created client for anonymous storage access, while storage announcements require initialized node keys and tub references. Many configuration values are parsed late and can raise during startup. `announcement-seqnum` is read/rewritten without explicit locking, which could race if two nodes share a config directory. `load_static_servers()` ignores all `EnvironmentError`, so unreadable or missing `servers.yaml` are indistinguishable. Storage requires a listening tub, and helper requires the same. Grid-manager certificates are attached but not validated here. The exit-trigger timer stops the global reactor.

## Test Signals

High-value tests cover `read_config()` validation, creation with fake factories, plugin discovery including unknown plugin errors, introducer config parsing, stable fURL registration, storage enabled/disabled/anonymous combinations, reserved-space and expiration parsing, node key persistence, auth token recreation, static server loading, helper/web/SFTP service parenting, grid-manager announcement contents, and `debug_wait_for_client_connections()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/codec.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/codec.py

## Purpose

This module wraps zfec's Cauchy Reed-Solomon erasure codec behind Tahoe-LAFS encoder/decoder interfaces and Deferred-friendly async methods.

## Important APIs, Types, And Functions

`CRSEncoder` implements `ICodecEncoder`. `set_params()` records data size and share counts, computes share size and padding, and creates `zfec.Encoder`. `encode()` validates input share sizes and desired IDs, then runs zfec encoding in the CPU threadpool. `CRSDecoder` implements `ICodecDecoder`; `set_params()` computes chunk/share sizing and creates `zfec.Decoder`, `get_needed_shares()` returns k, and `decode()` validates counts and runs zfec decode in the threadpool. `parse_params()` parses serialized `data-required-max` bytes.

## Control Flow

Callers configure an encoder/decoder with data size, required shares, and max shares. Encoding optionally defaults desired share IDs to all shares and returns `(shares, desired_share_ids)`. Decoding requires exactly the needed number of shares and corresponding IDs, then returns reconstructed data chunks from zfec.

## State And Persistence

Encoder/decoder instances keep sizing parameters and a zfec object. There is no persistence; serialized parameters are returned for storage in higher-level share metadata.

## Dependencies And Integration Points

It depends on `zfec`, Tahoe math/assert/deferred utilities, the CPU threadpool, and Tahoe codec interfaces. Immutable upload/download code uses this layer for CPU-heavy erasure coding without blocking the reactor.

## Risks

The code uses assertions for some invariants and `precondition()` for others. `encode_proposal()` is unimplemented. `parse_params()` trusts the byte format and can raise generic exceptions. Threadpool offload is required for reactor health; calling zfec directly elsewhere would risk blocking.

## Test Signals

Round-trip encode/decode with multiple k/n settings, desired share subsets, invalid share counts, invalid share lengths, parameter serialization parsing, and reactor responsiveness under large encode/decode operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/codec.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/__init__.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/__init__.py

## Purpose

This package initializer documents the intended abstraction boundary for Tahoe-LAFS cryptography helpers.

## Important APIs, Types, And Functions

It defines no runtime symbols. The module docstring states that code inside Tahoe should use helper functions from `allmydata.crypto` modules instead of relying directly on `cryptography` object methods.

## Control Flow

Importing `allmydata.crypto` executes only the docstring.

## State And Persistence

No state or persistence exists.

## Dependencies And Integration Points

The package contains concrete helper modules for AES, Ed25519, RSA, shared errors, and prefix utilities.

## Risks

Because there are no re-exports, callers must import concrete submodules. Adding import-time crypto setup here would affect security-sensitive code globally.

## Test Signals

`import allmydata.crypto` should be side-effect free. Submodule tests cover actual behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/aes.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/aes.py

## Purpose

This module provides Tahoe-local AES-CTR encryptor/decryptor helpers around the `cryptography` library.

## Important APIs, Types, And Functions

`DEFAULT_IV` is sixteen zero bytes. `Encryptor` and `Decryptor` dataclasses wrap `CipherContext` objects. `create_encryptor()` and `create_decryptor()` validate key/IV and create AES-CTR contexts. `encrypt_data()` and `decrypt_data()` call `update()` after validating bytes-like input. `_validate_key()` allows 16- or 32-byte keys, and `_validate_iv()` allows `None` or a 16-byte IV.

## Control Flow

Callers create a context, then stream data through `encrypt_data()` or `decrypt_data()`. `_create_cryptor()` always creates an encryptor context over AES-CTR because CTR encryption and decryption are the same keystream operation; the wrapper names separate caller intent.

## State And Persistence

The only state is cryptography cipher context state inside wrapper dataclasses. Contexts are not persisted and should not be reused across unrelated streams.

## Dependencies And Integration Points

It depends on `cryptography.hazmat` ciphers and is used by directory-node writecap encryption and other Tahoe crypto paths that require AES-CTR.

## Risks

The default all-zero IV is safe only when the caller's keying construction guarantees unique keystreams for its context; careless reuse with the same key would be catastrophic in CTR mode. `decrypt_data()` names its second parameter `plaintext`, a misleading label for ciphertext input. The functions do not finalize contexts, which is acceptable for CTR but should remain intentional.

## Test Signals

Round-trip 16- and 32-byte keys, explicit and default IVs, memoryview input, invalid key/IV types and lengths, and known AES-CTR vectors. Tests should also ensure context reuse behavior is understood.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/aes.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/ed25519.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/ed25519.py

## Purpose

This module centralizes Ed25519 key generation, serialization, signing, verification, and parsing for Tahoe-LAFS.

## Important APIs, Types, And Functions

`PRIVATE_KEY_PREFIX` and `PUBLIC_KEY_PREFIX` are `priv-v0-` and `pub-v0-`. `create_signing_keypair()` returns a private/public pair. `verifying_key_from_signing_key()` derives a public key. `sign_data()` signs bytes. `string_from_signing_key()` and `string_from_verifying_key()` serialize raw keys as base32 with prefixes. `signing_keypair_from_string()` and `verifying_key_from_string()` parse prefixed strings. `verify_signature()` raises `BadSignature` on invalid signatures. `_validate_public_key()` and `_validate_private_key()` enforce cryptography object types.

## Control Flow

Creation uses cryptography's Ed25519 generator. Serialization extracts raw key bytes and base32-encodes them with Tahoe prefixes. Parsing removes the expected prefix and base32-decodes raw key bytes. Signing and verification validate inputs before invoking cryptography methods.

## State And Persistence

The module has no mutable global state. Serialized keys are persisted by callers, notably node private/public keys and grid-manager identities.

## Dependencies And Integration Points

It depends on `cryptography` Ed25519 primitives, Tahoe base32 helpers, `remove_prefix()`, and `BadSignature`. It integrates with node identity, storage announcements, grid-manager CLI/certificates, and any signature validation path.

## Risks

Prefix and base32 format are compatibility contracts. `signing_keypair_from_string()` and `verifying_key_from_string()` rely on lower layers for length/encoding errors and expose ValueError/BadPrefixError. Ed25519 signing requires exact bytes; text callers must encode explicitly.

## Test Signals

Generate/sign/verify round trips, reject modified signatures/data, serialize/parse private and public keys, reject bad prefixes and non-bytes inputs, and verify known key string lengths and prefixes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/ed25519.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/error.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/error.py

## Purpose

This module defines shared exception types for Tahoe-LAFS crypto helpers.

## Important APIs, Types, And Functions

`BadSignature` indicates a signature did not match. `BadPrefixError` indicates an encoded key or byte string lacked an expected prefix.

## Control Flow

There is no control flow beyond class definitions.

## State And Persistence

No state or persistence exists.

## Dependencies And Integration Points

`ed25519.py`, `rsa.py`, and `util.py` raise these exceptions to provide Tahoe-local error names independent of cryptography internals.

## Risks

The exceptions carry no structured fields. Callers that need detail must inspect messages or wrap errors themselves.

## Test Signals

Tests should assert invalid signatures map to `BadSignature` and bad key prefixes map to `BadPrefixError`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/error.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/rsa.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/rsa.py

## Purpose

This module wraps RSA signing-key creation, DER serialization/deserialization, signing, and verification behind Tahoe-local helper functions.

## Important APIs, Types, And Functions

`PublicKey` and `PrivateKey` are type aliases for cryptography RSA key types. `RSA_PSS_SALT_LENGTH` is fixed at 32 for pycryptopp compatibility. `RSA_PADDING` is PSS with MGF1/SHA-256 and the fixed salt length. `create_signing_keypair()` generates a new key. `create_signing_keypair_from_string()` loads DER private keys with careful validation. `der_string_from_signing_key()` and `der_string_from_verifying_key()` serialize private/public keys. `create_verifying_key_from_string()` loads a public DER key. `sign_data()` and `verify_signature()` perform PSS/SHA-256 signatures, raising `BadSignature` for invalid signatures. Validation helpers enforce RSA key object types.

## Control Flow

Key loading first attempts an unsafe-skip-validation load when supported, checks that the object is an RSA private key and exactly 2048 bits, then reloads with OpenSSL validation. This balances protection from expensive malformed-key validation with final safety. Signing and verification validate key types and delegate to cryptography.

## State And Persistence

The module has immutable padding constants. DER private/public keys are persisted by callers, especially mutable-file key material. No mutable module state exists.

## Dependencies And Integration Points

It depends on cryptography RSA, hashes, PSS padding, DER serializers/loaders, `typing_extensions.TypeAlias`, and Tahoe `BadSignature`. It integrates with mutable file/directory key generation and client `KeyGenerator`, which creates 2048-bit RSA pairs on a CPU thread.

## Risks

The fixed 2048-bit requirement is a compatibility/security policy; loading other key sizes raises. The unsafe initial load path depends on cryptography version support and must remain paired with later validation. PSS salt length must not be changed casually because old signatures depend on 32 bytes, not cryptography's max salt length. Serialization is unencrypted DER, so caller storage protections are critical.

## Test Signals

Generate 2048-bit keys, serialize/load DER, sign/verify success, reject tampered signatures and data, reject non-RSA/private/public object misuse, reject non-2048 private keys, and run tests under cryptography versions with and without `unsafe_skip_rsa_key_validation`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/rsa.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/util.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/util.py

## Purpose

This module provides a small shared utility for validating and stripping byte prefixes from encoded crypto values.

## Important APIs, Types, And Functions

`remove_prefix(s_bytes, prefix)` returns `s_bytes` without `prefix` when present, otherwise raises `BadPrefixError`.

## Control Flow

The function checks `s_bytes.startswith(prefix)`, slices on success, and raises with a message on failure.

## State And Persistence

There is no state or persistence.

## Dependencies And Integration Points

It depends on `BadPrefixError` and is used by Ed25519 parsing and client node ID handling to enforce Tahoe key prefixes.

## Risks

It assumes byte-like objects with `startswith()` and slicing. Error messages include `repr(prefix)` but not the input, avoiding accidental key disclosure.

## Test Signals

Cover successful removal, empty suffix, wrong prefix, and non-bytes misuse if callers rely on strict type behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/crypto/util.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/deep_stats.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/deep_stats.py

## Purpose

This module implements deep traversal statistics for Tahoe directory trees, producing counters and histograms for files, directories, unknown nodes, and aggregate sizes.

## Important APIs, Types, And Functions

`DeepStats` has `API_VERSION = 1`. The constructor initializes counters, histograms, bucket state, and root `sqrt(10)` growth. `set_monitor()` attaches a monitor and initial status. `add_node()` classifies nodes as unknown, directory, mutable file, immutable file, or literal file and updates counters and histograms. `enter_directory()` records directory byte size and child count. `add()`, `max()`, `which_bucket()`, `histogram()`, `get_results()`, and `finish()` support aggregation.

## Control Flow

Directory traversal code calls `add_node()` for each reachable node and `enter_directory()` for directory contents. Immutable file sizes are bucketed and counted as literal or immutable CHK based on URI parsing. `get_results()` copies counters and renders histogram buckets into sorted `(min, max, count)` tuples.

## State And Persistence

State is in-memory counters, histograms, dynamic bucket list, monitor reference, and origin node. Results are consumed by web/API/CLI code but not persisted here.

## Dependencies And Integration Points

It depends on Tahoe node interfaces, `UnknownNode`, `LiteralFileURI`, URI parsing, and math utilities. It is used by `dirnode.DeepChecker`, `ManifestWalker`, and deep-stats API surfaces.

## Risks

Mutable file sizes are not counted, with TODO comments for servermap/size support. `which_bucket()` mutates the bucket list as sizes grow. URI parsing in `add_node()` can raise if an immutable node returns an unexpected URI. `set_monitor()` assumes the monitor accepts arbitrary attributes and status objects.

## Test Signals

Traverse synthetic trees with directories, CHK files, LIT files, mutable files, and unknown nodes; verify counters, largest values, histogram bucket boundaries, and monitor status updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/deep_stats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/dirnode.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/dirnode.py

## Purpose

This module implements Tahoe-LAFS directory nodes. A directory is backed by a file node whose contents serialize child names, read caps, encrypted write caps, and metadata. The module supports metadata updates, child add/delete/set/move operations, immutable-directory packing, recursive traversal, manifests, deep stats, and deep check/repair.

## Important APIs, Types, And Functions

Eliot fields and `ADD_FILE` instrument file additions. `update_metadata()` preserves Tahoe system metadata and updates link creation/modification times. Modifier classes `Deleter`, `MetadataSetter`, and `Adder` implement callbacks passed to mutable file `modify()`. `_encrypt_rw_uri()`, `pack_children()`, and `_pack_normalized_children()` serialize children and optionally superencrypt write caps. `DirectoryNode` implements `IDirectoryNode`, `ICheckable`, and `IDeepCheckable` with methods for reading/listing, child lookup, metadata, setting caps/nodes, uploading files, deleting, creating subdirectories, moving children, and deep traversal. `ManifestWalker` extends `DeepStats`; `DeepChecker` collects check/repair results.

## Control Flow

Reads call `_read()`, which downloads the backing mutable/immutable file and unpacks netstring entries. Unpacking normalizes names, decrypts write caps only for writable directories, strips padding spaces, constructs child nodes through the nodemaker, validates constraints, and caches packed entries in `AuxValueDict`. Mutations create a modifier object and pass its `modify()` method to the backing mutable file node, which reads old contents, edits the child map, repacks bytes, and publishes the new version. `add_file()` uploads content before linking the resulting node. Deep traversal is a strict depth-first Deferred chain that tracks verifier caps to avoid loops and processes file-like children before directories to reduce memory.

## State And Persistence

Persistent directory state is the packed backing file contents: sorted netstring child entries with UTF-8 names, readonly caps, encrypted write-cap data, and JSON metadata. Write caps are encrypted with a key derived from the directory writekey and a salt derived from the child write cap; a legacy MAC is appended for older readers. Runtime state includes the backing node, wrapped directory URI, nodemaker, uploader, traversal monitor, found verifier set, and result aggregators.

## Dependencies And Integration Points

The module integrates with AES helpers, hash/base32 utilities, mutable and immutable file nodes, unknown nodes, Tahoe interfaces/errors, check result classes, monitors, upload consumers, URI wrapping, netstring/json utilities, Eliot tracing, Twisted Deferreds, Foolscap scheduling, and deep stats.

## Risks

Serialization compatibility is critical; changing netstring order, metadata JSON, cap stripping, or writecap encryption would affect all directories. AES-CTR leaks encrypted writecap length as noted in comments. Assertions enforce many invariants but can be disabled. Move is implemented as set in destination then delete from source, with comments in SFTP noting possible data-loss windows for path moves. Deep traversal is intentionally serial and may be slow on huge trees, though it avoids high memory use. Duplicate verifier caps are skipped, which can under-count multiply linked objects.

## Test Signals

Round-trip pack/unpack across mutable and immutable directories, Unicode normalization, metadata timestamp preservation, no-write readonly wrapping, add/set/delete/move semantics with overwrite modes, encrypted writecap decryptability, deep-immutable constraint failures, traversal loop avoidance, manifest contents, deep stats counters, and deep check/repair aggregation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/dirnode.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/frontends/__init__.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/frontends/__init__.py

## Purpose

This is an empty package marker for Tahoe-LAFS frontend modules.

## Important APIs, Types, And Functions

The file defines no symbols.

## Control Flow

Importing `allmydata.frontends` executes no package-specific logic.

## State And Persistence

There is no state or persistence.

## Dependencies And Integration Points

It makes modules such as `allmydata.frontends.auth` and `allmydata.frontends.sftpd` importable.

## Risks

No direct risk. Adding imports here could create heavyweight frontend dependencies at package import time.

## Test Signals

`import allmydata.frontends` should succeed without side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/frontends/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/frontends/auth.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/frontends/auth.py

## Purpose

This module implements account-file authentication support for frontends, currently centered on SSH public-key credentials for SFTP users mapped to Tahoe root caps.

## Important APIs, Types, And Functions

`NeedRootcapLookupScheme` signals missing account lookup configuration. `FTPAvatarID` stores username and rootcap. `AccountFileChecker` implements Twisted `ICredentialsChecker` for `ISSHPrivateKey`, loads account maps, and delegates key validation to `SSHPublicKeyChecker`. Helper functions are `open_account_file()`, `load_account_file()`, `content_lines()`, `parse_accounts()`, and `create_account_maps()`.

## Control Flow

`AccountFileChecker` expands and opens the account file at construction, parses non-empty non-comment lines, rejects password-based entries, builds username-to-rootcap and username-to-key maps, and creates an in-memory SSH key checker. During authentication, `requestAvatarId()` validates SSH private-key credentials and maps the resulting username to an `FTPAvatarID`.

## State And Persistence

Persistent state is the account file. Runtime state is `rootcaps`, public-key maps, and the Twisted key checker. There is no reload logic after construction.

## Dependencies And Integration Points

It depends on Twisted cred/conch checkers, SSH key parsing, Tahoe `BytesKeyDict`, and path expansion. `frontends.sftpd.SFTPServer` uses `AccountFileChecker` to authenticate users and supply root caps to the SFTP dispatcher.

## Risks

Password-based accounts are explicitly unsupported. Account files are loaded only once, so changes require service restart. `parse_accounts()` uses whitespace splitting and assumes the final field is the rootcap; malformed lines raise. Duplicate names overwrite prior rootcaps/pubkeys in the maps. Rootcaps are encoded as UTF-8 bytes and later passed to node creation.

## Test Signals

Parse comments/blanks, valid SSH public-key account lines, password rejection, malformed line errors, duplicate-name behavior, credential success/failure through `SSHPublicKeyChecker`, and SFTP integration mapping username to rootcap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/frontends/auth.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/frontends/sftpd.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/frontends/sftpd.py

## Purpose

This module implements Tahoe-LAFS's SFTP frontend using Twisted Conch. It maps SFTP file, directory, attribute, rename, remove, and extension requests onto Tahoe capability nodes and directory operations while handling Tahoe's immutable/mutable semantics and asynchronous uploads/downloads.

## Important APIs, Types, And Functions

Helper functions include `createSFTPError()`, `eventually_callback()`, `eventually_errback()`, `_utf8()`, `_to_sftp_time()`, `_convert_error()`, `_repr_flags()`, `_lsLine()`, `_no_write()`, `_populate_attrs()`, `_attrs_to_metadata()`, and `_direntry_for()`. `OverwriteableFileConsumer` buffers downloads and overwrites in an encrypted temp file. `ShortReadOnlySFTPFile` serves small immutable read-only files from memory. `GeneralSFTPFile` handles read/write/create/truncate/append lifecycle, delayed commits, mutable overwrite, and immutable upload+link. `SFTPUserHandler` implements `ISFTPServer` and owns request handling plus per-user and global heisenfile tracking. `FakeTransport`, `ShellSession`, `Dispatcher`, and `SFTPServer` wire SSH/SFTP service behavior.

## Control Flow

On service startup, `SFTPServer` builds a Twisted portal with `AccountFileChecker`, loads SSH host keys, creates an SSH factory, and listens on the configured strports endpoint. Successful authentication returns an `SFTPUserHandler` rooted at the user's configured cap. Path parsing handles normal paths and `/uri/CAP` roots. `openFile()` validates flags, creates early write handles for race-prone clients, resolves parent/child or cap roots, performs permission checks, and returns a file handle. Reads and writes are serialized through Deferred chains. Closing a changed write handle waits for pending work, then overwrites mutable files or uploads immutable content and links it into the parent. Rename/remove/getAttrs/setAttrs coordinate with open write handles called "heisenfiles" to avoid commits landing at stale paths.

## State And Persistence

Persistent state is Tahoe grid data reached through root caps, mutable file publishes, immutable uploads, directory metadata, account files, and SSH host key files. Runtime state includes Conch session objects, open file handles, encrypted temporary files, per-user `_heisenfiles`, process-global `all_heisenfiles`, download milestone queues, overwrite heaps, Deferred chains, and convergence secret references. `_reload()` clears global heisenfile state for tests.

## Dependencies And Integration Points

The module depends on Twisted Conch SFTP/SSH interfaces, portal auth, strports, Deferreds, Foolscap eventual scheduling, Tahoe file/directory interfaces, mutable/immutable upload handles, directory metadata helpers, encrypted temporary files, frontend auth, and Tahoe logging. It is instantiated by `_Client.init_sftp_server()` when `[sftpd] enabled` is true.

## Risks

This is high-concurrency adapter code with subtle ordering constraints. Write success can be delayed until close, and close behavior differs for abandoned files. Global `all_heisenfiles` is single-process state and comments assume single-threaded updates. Rename uses `move_child_to()` with a FIXME about avoiding data loss for path moves. `setAttrs()` does not support size changes except on open handles. SFTP permissions are approximations over Tahoe caps and metadata, not POSIX ACLs. `statvfs` returns synthetic fixed values. The service requires an account file; anonymous operation is rejected. Host key file errors fail startup.

## Test Signals

Use SFTP integration tests for login, path normalization, `/uri` access, invalid UTF-8 paths, reads of small immutable and large/mutable files, write/create/truncate/append/close flows, delayed write errors, close after disconnect, rename and remove with open write handles, metadata/no-write propagation, directory listing longnames, unsupported symlink requests, OpenSSH `posix-rename` and `statvfs` extensions, host key loading, and account-file authentication failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/frontends/sftpd.py -->
