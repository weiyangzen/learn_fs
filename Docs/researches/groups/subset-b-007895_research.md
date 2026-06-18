# subset-b-007895 Research

Grouped research for the listed Tahoe-LAFS files. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/node.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/node.py

## Purpose
Implements common node-directory configuration and base node service behavior for Tahoe-LAFS clients and introducers. It validates `tahoe.cfg`, rejects obsolete pre-1.3 config files, manages private config files, constructs Foolscap Tubs, enforces selected privacy constraints, initializes logging, and supplies the `Node` base `MultiService`.

## APIs, Types, And Control Flow
Key entry points are `create_node_dir`, `read_config`, `config_from_string`, `_Config`, `create_tub_options`, `create_connection_handlers`, `create_tub`, `_tub_portlocation`, `tub_listen_on`, `create_main_tub`, and `Node`. `_Config` wraps `ConfigParser` and exposes Tahoe-specific helpers for regular config, private config, paths, Grid Manager certificates, and introducer configuration. `read_config` normalizes the basedir, checks old-file names, reads `tahoe.cfg` as UTF-8-SIG, and validates against `ValidConfiguration`. Tub construction flows from options and connection handlers through `_tub_portlocation`; it allocates/persists a port if necessary, expands `AUTO` locations, rejects ambiguous disabled states, and raises `PrivacyError` when hidden-IP mode conflicts with TCP hints or address probing.

## State, Persistence, And Integration
Persists node state under the basedir: `private/README`, private config files, `portnum`, `my_nodeid`, `private/logport.furl`, log incident directories, Grid Manager cert files, and introducer cache paths. It integrates with Twisted services/logging, Foolscap, the HTTP/Foolscap protocol switch, Tor/I2P providers, `allmydata.util.configutil`, YAML introducer config, and client/storage configuration sections read by downstream node construction. `Node.__init__` writes the base32 node id when the main tub exists and attaches both the main tub and log tub as child services.

## Risks And Test Signals
Risks include privacy regressions around `reveal-IP-address = false`, malformed `AUTO` location expansion for multi-listener ports, config migration hazards from old flat files, and direct filesystem writes in `_Config` that future non-filesystem config stores would need to abstract. The code also has compatibility details such as duplicate `PRIV_README`, Python 2-era bytes handling, and option names that differ between Tahoe and Foolscap. Test signals are `allmydata/test/test_node.py`, connection/Tor/I2P tests, configutil tests, system tests that instantiate clients/introducers, and protocol switch tests when `create_tub_with_https_support` is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/node.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/nodemaker.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/nodemaker.py

## Purpose
Provides `NodeMaker`, the factory that turns Tahoe capability strings into in-memory file/directory node objects and creates new mutable or immutable nodes. It is the bridge between URI parsing and higher-level filesystem objects.

## APIs, Types, And Control Flow
`NodeMaker` implements `INodeMaker`. `create_from_cap(writecap, readcap, deep_immutable, name)` chooses a usable cap, parses it with `uri.from_string`, dispatches by URI type in `_create_from_single_cap`, wraps unknown caps in `UnknownNode`, and wraps blacklisted storage indexes in `ProhibitedNode`. It can create literal, immutable CHK, immutable verifier, mutable SSK/MDMF, and directory nodes. `create_mutable_file` generates or accepts RSA key pairs, initializes a `MutableFileNode`, and returns a Deferred. `create_new_mutable_directory` validates children and packs them into `MutableData`; `create_immutable_directory` packs deep-immutable children, uploads CHK data, then creates a directory wrapper.

## State, Persistence, And Integration
Holds references to the storage broker, secret holder, history, uploader, terminator, encoding parameters, mutable default format, key generator, and optional blacklist. It caches node objects in a `WeakValueDictionary` keyed by cap and mutability/deep-immutable mode; despite a stale comment, the implementation caches mutable nodes and avoids caching unknown/prohibited wrappers. Persistent state is produced indirectly through uploads, mutable publishes, and storage interactions performed by the created nodes.

## Risks And Test Signals
Risks center on URI-type coverage, cache correctness, mutable identity behavior, and blacklist checks for nodes whose storage index is absent or expensive. Directory creation depends on `pack_children` metadata shape and writekey handling. Test signals are `test_filenode.py`, mutable/immutable upload/download tests, no-network tests, blacklist tests, and directory tests that validate cap parsing and factory behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/nodemaker.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/protocol_switch.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/protocol_switch.py

## Purpose
Allows one listening port to serve both legacy Foolscap negotiation and the newer HTTPS storage protocol. This supports automatic HTTPS availability after upgrade without requiring users to configure a second port.

## APIs, Types, And Control Flow
`create_tub_with_https_support(**kwargs)` creates a Foolscap `Tub`, defines a per-Tub subclass of `_FoolscapOrHttps`, and installs it as `tub.negotiationClass`. `_FoolscapOrHttps` starts as a Twisted `Protocol`, buffers the first bytes, and chooses protocol mode: buffers beginning with `GET /id/` are converted into Foolscap `Negotiation`; all other traffic is passed into a TLS-wrapped Twisted Web `Site`. `add_storage_server(storage_server, swissnum)` configures HTTPS serving with the Tub certificate, builds NURLs from TCP/Tor location hints, and intentionally skips I2P until HTTP client support exists.

## State, Persistence, And Integration
State lives in class attributes on the per-Tub protocol subclass: the owning `Tub` and configured `https_factory`. No files are written. It integrates with Foolscap internals through a metaclass that makes wrapper instances pass `isinstance(..., Negotiation)` checks, Twisted TLS/Web protocol machinery, `storage.http_server.HTTPServer`, `build_nurl`, and `StorageServer`.

## Risks And Test Signals
Risks include brittle byte-level protocol detection, the 30-second abort timer, dynamic `__class__` and `__dict__` mutation, incorrect factory protocol bookkeeping, unsupported/compound location hint formats, and assertion failures for malformed Tor hints. Test signals are `allmydata/test/test_protocol_switch.py`, storage HTTPS tests, and integration tests that exercise mixed Foolscap/HTTPS storage access on upgraded nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/protocol_switch.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/__init__.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/__init__.py

## Purpose
Marks `allmydata.scripts` as a Python package. The file is intentionally empty and exposes no runtime API of its own.

## APIs, Types, And Control Flow
There are no functions, classes, constants, imports, or executable statements. Package import behavior is the only API surface: modules such as `runner`, `cli`, `create_node`, and command-specific implementations are imported by fully qualified `allmydata.scripts.*` names.

## State, Persistence, And Integration
No state is persisted. Integration is structural only, enabling Tahoe-LAFS command modules to share a package namespace.

## Risks And Test Signals
The practical risk is accidental addition of import-time side effects, which would affect CLI startup. Current test signal is indirect: any CLI test importing `allmydata.scripts` or a submodule validates that the package marker exists and remains harmless.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/admin.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/admin.py

## Purpose
Defines `tahoe admin` subcommands for key generation, deriving public keys, migrating crawler state from pickle to JSON, and adding Grid Manager certificates to a storage server configuration.

## APIs, Types, And Control Flow
Option classes are `GenerateKeypairOptions`, `DerivePubkeyOptions`, `MigrateCrawlerOptions`, `AddGridManagerCertOptions`, and `AdminCommand`. `do_admin` dispatches via `subDispatch`. Key commands call Ed25519 helpers and print ASCII private/public strings. `migrate_crawler` upgrades `storage/lease_checker.state`, `storage/bucket_counter.state`, and `storage/lease_checker.history`. `add_grid_manager_cert` reads a cert from a file or stdin, parses it, loads node config, enables storage grid management, registers the cert in `[grid_manager_certificates]`, writes `<name>.cert`, and reports the count.

## State, Persistence, And Integration
Writes crawler JSON replacement files through storage crawler/expirer helpers. `add_grid_manager_cert` rewrites `tahoe.cfg` through `_Config.set_config` and writes certificate JSON in the node basedir. It integrates with `allmydata.client.read_config`, Grid Manager certificate parsing, `jsonbytes`, CLI basedir resolution, and Twisted `usage`.

## Risks And Test Signals
Risks include trusting local pickle inputs during migration, partial config/cert writes if the cert file write fails after config updates, and name collisions or invalid names becoming filenames. Key material is printed to stdout and must be handled securely by callers. Test signals include `allmydata/test/cli/test_admin.py`, grid manager tests, and crawler migration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/admin.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/backupdb.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/backupdb.py

## Purpose
Implements the SQLite cache used by `tahoe backup` to avoid re-uploading unchanged files and re-creating identical immutable directories. It records local file metadata, caps, upload/check timestamps, and directory content hashes.

## APIs, Types, And Control Flow
`get_backupdb` opens or creates the database with schema v2 and returns `BackupDB_v2`. `FileResult` and `DirectoryResult` are callback handles used by backup code to report successful uploads/checks. `BackupDB_v2.check_file` stats the absolute path, compares size/mtime/ctime unless timestamps are ignored, retrieves the previous cap, and probabilistically decides whether to re-check health based on `NO_CHECK_BEFORE` and `ALWAYS_CHECK_AFTER`. `check_directory` netstring-encodes sorted child names and caps, hashes the result, and performs the same age-based check decision. Mutation methods update `caps`, `local_files`, `last_upload`, and `directories`.

## State, Persistence, And Integration
Persists `private/backupdb.sqlite` tables: `version`, `local_files`, `caps`, `last_upload`, and `directories`. It integrates with `allmydata.util.dbutil.get_db`, Tahoe base32/hash utilities, and `tahoe_backup.BackerUpper`.

## Risks And Test Signals
The cache trusts filesystem timestamps by default, so clock granularity or copied files can cause stale reuse unless `--ignore-timestamps` is used. Randomized health checks make behavior time/probability dependent. Directory hashes depend on deterministic child ordering and byte encodings. Test signals include `allmydata/test/cli/test_backupdb.py` and backup tests that verify reuse, schema upgrades, and timestamp-ignore behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/backupdb.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/cli.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/cli.py

## Purpose
Defines most user-facing Tahoe filesystem CLI option parsers and dispatch functions: aliases, `ls`, `get`, `put`, `cp`, `mv`, `ln`, `backup`, `webopen`, `manifest`, `stats`, `check`, `deep-check`, and `status`.

## APIs, Types, And Control Flow
The central base is `FileStoreOptions`, which resolves `--node-directory`, reads `node.url`, normalizes `--node-url`, loads aliases, and lets `--dir-cap` override the default alias. Command-specific subclasses parse and validate arguments and flags. `subCommands` exposes Twisted usage metadata, while `dispatch` maps command names to thin wrapper functions that import the implementation lazily and return its rc.

## State, Persistence, And Integration
Reads local node state from `node.url`, `private/root_dir.cap`, and `private/aliases`; most mutations happen in imported modules through the web API or alias files. It integrates with `common.get_aliases`, command modules such as `tahoe_put`, `tahoe_cp`, `tahoe_backup`, and `tahoe_check`, and the top-level `runner.dispatch`, which runs these blocking commands in a worker thread.

## Risks And Test Signals
Risks are mostly parsing and UX boundary cases: URL regex only accepts simple host/port HTTP(S) forms, `node.url` must exist unless explicitly overridden, Windows drive-letter paths interact with alias syntax in shared helpers, and command wrappers rely on lazy imports. Test signals are broad CLI tests under `allmydata/test/cli/`, including alias, list, put, cp, mv, backup, status, and check tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/cli.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/common.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/common.py

## Purpose
Contains shared CLI utilities for option formatting, basedir resolution, introducer and alias file handling, Tahoe alias/path parsing, platform drive-letter detection, and URL path escaping.

## APIs, Types, And Control Flow
`BaseOptions` customizes subcommand usage and forbids `--version` below the root command. `BasedirOptions` and `NoDefaultBasedirOptions` resolve `--basedir`, `--node-directory`, positional basedirs, and defaults with conflict checks. `write_introducer` writes `private/introducers.yaml`. `get_introducer_furl` reads configured introducers or falls back to `private/introducer.furl`. `get_aliases` reads root/default aliases and `private/aliases`. `get_alias` converts user paths into `(dircap, relative_path)` while accepting raw caps and handling default aliases. `escape_path` percent-encodes UTF-8 path segments.

## State, Persistence, And Integration
Writes `private/introducers.yaml`; reads `private/root_dir.cap`, `private/aliases`, and `private/introducer.furl`. It integrates with Twisted `usage`, YAML serialization, URI parsing, encoding utilities, and all CLI modules that need aliases or basedirs.

## Risks And Test Signals
Risks include ambiguous colon parsing, alias file lines split on the first colon, raw cap path suffix compatibility, and platform-specific Windows drive handling controlled by a test hook. `get_aliases` silently ignores file read errors, which is friendly but can hide permission problems. Test signals include CLI alias/path tests, create-node tests for introducer writing, and Windows path parsing tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/common_http.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/common_http.py

## Purpose
Provides blocking HTTP client helpers for CLI commands that talk to a Tahoe gateway web API.

## APIs, Types, And Control Flow
`parse_url` decomposes HTTP(S) URLs into scheme, host, port, and path. `do_http(method, url, body)` accepts bytes or a seekable/readable file-like body, computes `Content-Length`, builds an `HTTPConnection` or `HTTPSConnection`, sends the body in 64 KiB chunks, and returns the response. `BadResponse` represents connection setup failure. Formatting helpers convert response status/body into printable messages, `check_http_error` maps non-2xx responses to rc 1, and `HTTPError` wraps web API failures as `TahoeError`.

## State, Persistence, And Integration
No persistent state is written. It reads optional `__TAHOE_CLI_HTTP_TIMEOUT` from the environment and uses Tahoe full version as the User-Agent. It is used by alias creation, backup, check/deep-check, slow operations, and other command modules.

## Risks And Test Signals
Risks include a simple host/port parser that does not handle all URL forms, no redirect handling except where callers accept 302, blocking network behavior, and response bodies being consumed during error formatting. It rejects Unicode request bodies to avoid ambiguous encoding. Test signals are CLI tests with fake web servers and timeout/error-path tests around web API clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/common_http.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/create_node.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/create_node.py

## Purpose
Implements `tahoe create-node`, `create-client`, and `create-introducer`. It validates listener/privacy options, creates node directories, writes compatibility `.tac` files, generates `tahoe.cfg`, optionally joins an invited grid via magic-wormhole, and writes introducer configuration.

## APIs, Types, And Control Flow
Option classes are `CreateClientOptions`, `CreateNodeOptions`, and `CreateIntroducerOptions`. `validate_where_options`, `validate_tor_options`, and `validate_i2p_options` enforce combinations of `--listen`, `--hostname`, `--port`, `--location`, Tor, I2P, and hidden-IP settings. `write_node_config` asynchronously asks listener providers for `ListenerConfig`, merges configs, writes `[connections]`, `[node]`, tub port/location, and listener sections. `write_client_config` writes client, storage, and helper sections. `create_node` refuses non-empty basedirs, handles wormhole invite overrides through a whitelist, creates `private`, writes config, and prints setup reminders. `create_client` forces no storage and no listening; `create_introducer` writes only node config.

## State, Persistence, And Integration
Creates the basedir, `private/`, `tahoe-client.tac` or `tahoe-introducer.tac`, `tahoe.cfg`, and possibly `private/introducers.yaml`. It integrates with listener providers (`tcp`, `tor`, `i2p`, `none`), Twisted Deferred/coroutine bridging, magic-wormhole, encoding/file utilities, and CLI runner dispatch.

## Risks And Test Signals
Risks include option-combination gaps, listener config overlap errors, partial directory creation if async listener setup fails, sensitive invite data handling, and hidden-IP misconfiguration if listener capabilities change. `--i2p-launch` is explicitly not implemented. Test signals are `allmydata/test/cli/test_create.py`, listener/Tor/I2P provider tests, and invite tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/create_node.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/debug.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/debug.py

## Purpose
Defines `tahoe debug` tools for inspecting caps and share files, locating/cataloging shares, deliberately corrupting test shares, and invoking Foolscap `flogtool` with Tahoe imports.

## APIs, Types, And Control Flow
Command options include `DumpOptions`, `DumpCapOptions`, `FindSharesOptions`, `CatalogSharesOptions`, `CorruptShareOptions`, `FlogtoolOptions`, and `DebugCommand`. `dump_share` detects mutable versus immutable share headers and dispatches to parsers. Immutable parsing uses `ShareFile` and `ReadBucketProxy` to extract URI extension data, leases, offsets, and verify caps. Mutable parsing reads lease/header metadata and handles SDMF via `unpack_share` or MDMF via a local `MDMFSlotReadProxy`. `dump_cap` parses URI strings or `/uri/` URLs and prints keys, storage indexes, fingerprints, verifier details, and optional lease secrets. `find_shares` and `catalog_shares` scan storage share directories. `corrupt_share` flips a random data bit in supported share types for checker/repair testing.

## State, Persistence, And Integration
Mostly read-only inspection of share files and node storage directories. `corrupt_share` mutates a share in place with `rb+`. The module integrates tightly with storage layout internals, mutable layout parsers, URI classes, hash utilities, Foolscap logging CLI, and Twisted Deferred helpers.

## Risks And Test Signals
This is intentionally low-level and brittle: offset calculations duplicate storage internals, malformed shares can raise while cataloging, `corrupt-share` is destructive, and some code only supports SDMF mutable corruption. Test signals are debug CLI tests, storage layout tests, checker/repair tests that use corrupted shares, and manual diagnostics against test grids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/debug.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/default_nodedir.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/default_nodedir.py

## Purpose
Computes the default Tahoe node directory used by CLI commands.

## APIs, Types, And Control Flow
The module exposes `_default_nodedir`. On Windows it asks `allmydata.windows.registry.get_base_dir_path()` and uses that if available; otherwise it expands `~/.tahoe` to an absolute Unicode path. `precondition` assertions verify the result is text.

## State, Persistence, And Integration
No files are written. It integrates with Windows registry support, `abspath_expanduser_unicode`, and `scripts.common.get_default_nodedir`, which propagates the value into CLI option defaults.

## Risks And Test Signals
Import-time platform probing can affect tests and startup behavior. Windows registry failures or unexpected non-string values would fall back or assert. Test signals are CLI basedir tests and Windows fixup/registry tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/default_nodedir.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/runner.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/runner.py

## Purpose
Provides the top-level `tahoe` command parser and dispatcher. It combines create, admin, run, debug, file API, and invite subcommands, initializes optional Eliot logging, and runs under Twisted `task.react`.

## APIs, Types, And Control Flow
`Options` is the root Twisted `usage.Options` class with global flags (`--quiet`, `--version`, `--version-and-path`), global parameters (`--node-directory`, wormhole settings), and all subcommands. `parse_or_exit` parses argv, prints the most specific subcommand usage on errors, and exits with rc 1. `dispatch` selects the implementation module; blocking filesystem/web CLI commands are wrapped in `threads.deferToThread`, while create/run/invite/debug/admin commands are run through Deferred-aware dispatch. `run` initializes Windows fixups and calls `_run_with_reactor`; `_setup_coverage` supports multiprocess coverage when `--coverage` is present.

## State, Persistence, And Integration
No Tahoe data files are written directly. It mutates process state: stdio handles on options, `sys.argv` indirectly through invoked tools, `COVERAGE_PROCESS_START`, Twisted reactor lifecycle, and optional Eliot logging service. It integrates all command modules, magic-wormhole, Twisted threads/deferreds, and Tahoe version reporting.

## Risks And Test Signals
Risks include `SystemExit`-driven control flow, thread wrapping assumptions for blocking commands, argv conversion side effects, coverage typo in one error message, and keeping usage errors precise when nested parsers partially initialize. Test signals are `allmydata/test/test_runner.py`, CLI parser tests, run command tests, and integration tests that launch `tahoe`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/runner.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/slow_operation.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/slow_operation.py

## Purpose
Provides a reusable polling runner for web API operations that start asynchronously and expose status under `/operations/<handle>`.

## APIs, Types, And Control Flow
`SlowOperationRunner.run(options)` generates a random base32 operation handle, resolves the target alias/path, builds the operation URL via subclass-provided `make_url`, starts it with POST, and then calls `wait_for_results`. Polling uses a fixed schedule of 1, 5, 10, 30, 60, 90, then increasing 120-second intervals. `poll` GETs JSON status with `release-after-complete=true`; if unfinished it continues, if raw output is requested it writes printable ASCII JSON, otherwise it delegates to subclass `write_results`.

## State, Persistence, And Integration
No local persistence. Remote state is the gateway operation handle and server-side operation status, released after completion. Integrates with CLI aliases, `common_http.do_http`, JSON parsing, base32 random handles, and command modules that subclass it for slow operations.

## Risks And Test Signals
Risks include indefinite polling with no client-side timeout, blocking `time.sleep`, operation-handle lifecycle assumptions, and raw JSON output rejecting unprintable bytes. Test signals are slow-operation users such as deep operations/manifest/status tests and web API operation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/slow_operation.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_add_alias.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_add_alias.py

## Purpose
Implements alias management commands: add an existing directory cap, create a new Tahoe directory and alias it, and list configured aliases.

## APIs, Types, And Control Flow
`add_alias` validates alias characters, rejects duplicates, normalizes the provided cap as a directory URI, and appends it to `private/aliases`. `create_alias` performs the same validation, POSTs `uri?t=mkdir` to the gateway, then records the returned URI. `list_aliases` loads alias details, optionally emits JSON, and can show read-only caps. Helpers include `add_line_to_aliasfile`, `show_output`, `_get_alias_details`, and `_escape_format`.

## State, Persistence, And Integration
Writes `private/aliases` through a temporary file plus `move_into_place`; reads aliases through `common.get_aliases`. It integrates with URI parsing, `common_http.do_http`, JSON byte helpers, and CLI option classes in `cli.py`.

## Risks And Test Signals
Risks include non-atomic read-modify-write races on the alias file, silent alias-read errors inherited from `get_aliases`, output encoding complexity, and no creation of parent `private` if the node directory is malformed. Test signals are `allmydata/test/cli/test_alias.py` and `test_create_alias.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_add_alias.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_backup.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_backup.py

## Purpose
Implements `tahoe backup`, creating immutable, timestamped backups of a local directory tree under `ALIAS:TO/Archives/<timestamp>` and updating `ALIAS:TO/Latest`. It reuses prior file and directory caps through `backupdb`.

## APIs, Types, And Control Flow
`BackerUpper.run` opens `private/backupdb.sqlite`, resolves the destination alias, ensures the target `Archives` directory exists, collects backup targets deepest-first, runs `run_backup`, then links the completed root dircap into `Archives` and `Latest`. `collect_backup_targets` classifies files, directories, symlinks, special files, permission failures, and undecodable names. `FileTarget` uploads or reuses file caps; `DirectoryTarget` consumes accumulated child contents and creates or reuses immutable directories. `BackupProgress` tracks mutable progress counters and child maps; `BackupComplete.report` formats final output. HTTP helpers upload files with PUT `/uri`, create immutable directories with POST `?t=mkdir-immutable`, and link children with PUT `?t=uri`.

## State, Persistence, And Integration
Reads local filesystem metadata from `os.stat`, uploads file bytes to the gateway, writes backup cache records through `backupdb`, and mutates remote Tahoe directories. Metadata stored in created directory entries includes POSIX-ish stat fields when present. It integrates with CLI excludes from `BackupOptions`, `common_http`, alias parsing, Tahoe JSON byte encoding, and encoding utilities.

## Risks And Test Signals
Risks include trusting timestamp cache decisions, skipping symlinks/special files, memory use from materializing all targets, blocking uploads, partial remote state if linking `Archives` or `Latest` fails after upload, and returning rc 2 when skips occurred. Test signals include `allmydata/test/cli/test_backup.py`, backupdb tests, and web API tests for immutable directory creation/linking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_backup.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_check.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_check.py

## Purpose
Implements `tahoe check` and `tahoe deep-check`, including optional verification, repair, lease renewal, raw JSON output, and human-readable summaries of corrupt shares and repair results.

## APIs, Types, And Control Flow
`check_location` resolves an alias/path, POSTs `?t=check&output=JSON` with selected flags, and formats either normal check results or pre/post repair summaries. `check` applies it to all requested locations or the default root. Deep checking uses `DeepCheckStreamer`, which POSTs `?t=stream-deep-check`, reads the response stream in chunks, and feeds lines into `DeepCheckOutput` or `DeepCheckAndRepairOutput`. Those `LineOnlyReceiver` subclasses count checked objects, healthy/unhealthy files, repair attempts, and corrupt shares; verbose mode prints one line per object.

## State, Persistence, And Integration
No local files are written. Remote state may change when `--repair` repairs shares or `--add-lease` renews leases. Integrates with the gateway web API, shared alias/path escaping, blocking HTTP client, Twisted line parsing, JSON, and output encoding helpers.

## Risks And Test Signals
Risks include assuming JSON response shapes, reading deep-check streams synchronously, rc handling when a streamed `ERROR:` line appears, and remote mutation when repair or lease options are set. LIT files are special-cased because they lack some fields. Test signals are `allmydata/test/cli/test_check.py`, deep-check/checker tests, repairer tests, and web check-results tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_check.py -->
