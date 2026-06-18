# Research: subset-b-007896

Grouped research for Tahoe-LAFS CLI helpers, storage share persistence, crawler/lease maintenance, and HTTP storage transport. Each section preserves the source path in the title and is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_cp.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_cp.py

## Purpose
Implements `tahoe cp`, including local-to-grid, grid-to-local, grid-to-grid, file-cap-to-file, and recursive directory copying. It abstracts sources and targets as local/Tahoe file/directory/missing objects so `Copier.try_copy()` can enforce cp-like semantics before dispatching to byte copy, URI link, directory creation, and child-link updates.

## Important APIs, Types, and Functions
Key exceptions are `MissingSourceError`, `FilenameWithTrailingSlashError`, and `WeirdSourceError`. HTTP helpers `GET_to_file`, `GET_to_string`, `PUT`, `POST`, `mkdir`, and `make_tahoe_subdirectory` wrap `common_http.do_http` with Tahoe webapi status checks. Source/target classes include `LocalFileSource`, `LocalDirectorySource`, `TahoeFileSource`, `TahoeDirectorySource`, `LocalFileTarget`, `LocalDirectoryTarget`, `TahoeFileTarget`, `TahoeDirectoryTarget`, and missing-target variants. `Copier.do_copy()` is the command entry point, `get_source_info()` and `get_target_info()` classify operands, `copy_file_to_file()` handles single-file output, and `copy_things_to_directory()` handles recursive/directory cases.

## Control Flow
`copy(options)` instantiates `Copier` and calls `do_copy()`. `try_copy()` normalizes the node URL, resolves aliases first for the destination and then each source, determines whether the destination is a file or directory, validates recursive and multi-source constraints, and then either copies one file or builds a target map. Directory copies populate sources recursively, lazily populate target children, create missing local/Tahoe directories, detect same-name collisions in each target directory, then walk the target map copying files and calling `set_children()` for Tahoe directories.

## State and Persistence Behavior
Local output is persisted with `fileutil.put_file()` or `os.makedirs()`. Tahoe uploads go through webapi `PUT /uri` or `PUT /uri/<cap>/<path>`, while directory link mutations are batched in `TahoeDirectoryTarget.new_children` until `set_children()` posts `?t=set_children`. Tahoe directory/source objects cache parsed child JSON by read/write capability in `Copier.cache`, limiting duplicate directory fetches during recursive copies. Immutable Tahoe-to-Tahoe file copies can avoid byte transfer by linking the source cap; mutable files and local targets force byte copies.

## Dependencies and Integration Points
Depends on `allmydata.scripts.common` for alias parsing and path escaping, `common_http` for webapi calls, `allmydata.uri` for readonly caps after mkdir, `encodingutil` for terminal/path conversions, and `jsonbytes` for directory JSON. Integrates with Tahoe webapi endpoints `GET ?t=json`, `POST ?t=mkdir`, `PUT ?t=uri`, and `POST ?t=set_children`.

## Risks and Edge Cases
`need_to_copy_bytes()` checks `source.need_to_copy_bytes` rather than calling it, matching an in-file FIXME and preserving bug-compatible behavior. URI-link copying has TODOs around forward compatibility and mutable handling. Local special files are rejected or skipped; dangling symlinks under recursive local dirs are ignored. The module relies on webapi JSON shapes and may fail hard on unknown node types.

## Test Signals
`src/allmydata/test/cli/test_cp.py` covers Unicode filenames/directories, dangling symlinks, raw filecaps, missing aliases, recursive copy behavior, collision and directory/file overwrite cases, verbose progress, and grid/local round trips. Broader CLI help/import tests in `test_cli.py` also exercise command registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_cp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_get.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_get.py

## Purpose
Implements `tahoe get`, downloading a file or cap from the Tahoe webapi to a local file or stdout.

## Important APIs, Types, and Functions
The single public entry point is `get(options)`. It resolves `options.from_file` with `get_alias()`, constructs `/uri/<rootcap>/<escaped-path>`, performs `do_http("GET", url)`, streams response chunks of 4096 bytes, and formats errors with `format_http_error()`.

## Control Flow
The command normalizes `node-url`, resolves aliases using `DEFAULT_ALIAS`, opens `to_file` in binary mode if supplied, otherwise writes to `stdout.buffer` when stdout is text, loops over response reads until EOF, and returns `0` on status 200/201 or `1` on HTTP/alias errors.

## State and Persistence Behavior
The only persistence is local output file creation when `to_file` is set. It streams from the HTTP response to avoid buffering whole downloads in memory.

## Dependencies and Integration Points
Integrates with CLI alias configuration through `allmydata.scripts.common` and Tahoe webapi `GET /uri`. It depends on `common_http.do_http` for transport and response abstraction.

## Risks and Edge Cases
Output file handles are opened directly and closed only after a successful read loop; exceptional reads could leak handles. It treats 201 as success for GET even though 200 is the expected response. Alias errors are user-facing and produce exit code 1.

## Test Signals
`test_cli.py` includes get help, normal get behavior, broken socket handling, missing default alias, and nonexistent alias coverage; `test_cp.py` and `test_mv.py` use `tahoe get` heavily for integration verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_get.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_invite.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_invite.py

## Purpose
Implements the `tahoe invite` subcommand, creating a Magic Wormhole exchange that sends introducer and share-configuration data to a new client node.

## Important APIs, Types, and Functions
`InviteOptions` parses a single nickname plus optional share parameters. `_send_config_via_wormhole(options, config)` performs the server-side wormhole protocol. `invite(options)` reads the local node config, derives the introducer FURL, builds the remote config, and sends it. `subCommands` and `dispatch` register the command.

## Control Flow
`invite()` chooses a basedir from the global node directory or default, reads `tahoe.cfg`, obtains the introducer FURL, and fills missing share values from the `[client]` config. `_send_config_via_wormhole()` connects to the configured wormhole relay/appid, allocates and prints an invite code, sends server abilities, waits for a client intro, verifies `client-v1`, sends JSON config, and closes.

## State and Persistence Behavior
This module does not write local state. It reads node config and transmits a JSON config over the wormhole. The visible invite code is transient and printed to stdout.

## Dependencies and Integration Points
Uses Twisted `inlineCallbacks`, global runner-provided wormhole settings, `read_config()`, `get_introducer_furl()`, and `jsonbytes`. It integrates with `create-node --join` on the receiving side and with Magic Wormhole relay/application IDs.

## Risks and Edge Cases
Protocol negotiation is strict: missing `abilities` or `client-v1` returns 1 from the helper. Missing introducer FURL raises `SystemExit(1)`. Share options are strings from CLI/config, so downstream consumers must tolerate string numeric values. The helper imports the global `reactor`, which makes isolation/testing more delicate.

## Test Signals
`src/allmydata/test/cli/test_invite.py` covers successful invites, share config fallback, missing FURL, wrong/missing client/server abilities, missing nickname, illegal create-node join options, and create-node join integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_invite.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_ls.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_ls.py

## Purpose
Implements `tahoe ls`, listing directory children or a single file node from Tahoe webapi JSON with optional JSON passthrough, long format, classification suffixes, and URI display.

## Important APIs, Types, and Functions
The public API is `ls(options)`. It resolves aliases, calls `GET /uri/<cap>/<path>?t=json`, optionally prints raw JSON, otherwise parses the node tuple and formats rows using metadata, readonly/write caps, file sizes, and terminal-safe output helpers.

## Control Flow
The command normalizes node URL and trailing slash input, handles 404 as exit code 2 and connection status 0 as exit code 3, parses webapi JSON, derives `children` from either a dirnode or a single node, computes row widths, and prints rows to stdout unless Unicode encoding fails, in which case it prints escaped names to stderr and returns 1.

## State and Persistence Behavior
No persistent writes. It reads remote node metadata and uses current wall clock time to choose GNU-ls-like date formatting for link creation/modification times.

## Dependencies and Integration Points
Depends on `common.get_alias`, `escape_path`, `common_http.do_http`, `encodingutil` conversions, and Tahoe webapi JSON node format. It uses `six.ensure_text` to normalize URI cells.

## Risks and Edge Cases
Unknown child node types are listed with `?` and trigger a warning. Metadata assumptions can fail if webapi payloads omit expected `metadata`. Raw JSON mode rejects unprintable non-ASCII bytes even though webapi should return printable ASCII. Long output width computation is display-width naive for complex Unicode.

## Test Signals
`test_cli.py` covers help, list behavior, empty directories, Unicode listing behavior via `test_cp.py`, missing aliases, and JSON/formatting paths indirectly through grid CLI integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_ls.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_manifest.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_manifest.py

## Purpose
Implements `tahoe manifest` streaming output and `tahoe stats` deep-statistics retrieval for Tahoe directory trees.

## Important APIs, Types, and Functions
`ManifestStreamer` subclasses `LineOnlyReceiver` to parse newline-delimited manifest records from `?t=stream-manifest`. `manifest(options)` runs it. `StatsGrabber` subclasses `SlowOperationRunner`, overrides `make_url()` for `?t=start-deep-stats`, and formats count/size/histogram results in `write_results()`. `stats(options)` runs the stats operation.

## Control Flow
Manifest mode resolves the target alias, posts to `stream-manifest`, reads chunks, either writes raw bytes to stdout or feeds Twisted line parsing. Each line is JSON-decoded unless it begins with `ERROR:`; selected fields are printed according to `storage-index`, `verify-cap`, `repair-cap`, or default cap/path mode. Stats mode uses the slow-operation runner to poll an operation handle and then prints selected counters and histograms.

## State and Persistence Behavior
No local persistence. It streams server output incrementally, preserving memory for large trees. `ManifestStreamer.rc` accumulates error state when server-side stream lines indicate errors.

## Dependencies and Integration Points
Depends on Tahoe webapi `stream-manifest` and deep-stats operation endpoints, `SlowOperationRunner`, `encodingutil.quote_output`/`quote_path`, and `abbreviate_space_both`.

## Risks and Edge Cases
Malformed stream JSON produces stderr errors but does not necessarily abort the stream. Raw mode writes to `stdout.buffer`, so tests/options must provide binary-capable stdout. HTTP 302 is accepted for manifest. Stats output assumes certain keys, while optional keys are skipped.

## Test Signals
`test_cli.py` includes manifest help, missing alias/nonexistent alias handling, stats command help, stats missing alias handling, and integration around deep traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_manifest.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_mkdir.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_mkdir.py

## Purpose
Implements `tahoe mkdir`, creating an unlinked Tahoe directory or a linked child directory at a path.

## Important APIs, Types, and Functions
The public function `mkdir(options)` resolves aliases and issues `POST ?t=mkdir`. It uses `check_http_error()` for response handling and prints the returned directory writecap with `quote_output()`.

## Control Flow
If no target or no path is supplied, it posts to `/uri?t=mkdir`, optionally adding `format=...`. Otherwise it resolves the alias/path, strips a trailing slash, posts to `/uri/<rootcap>/<path>?t=mkdir`, optionally appending format, prints the new URI, and returns 0 unless early alias or HTTP errors occur.

## State and Persistence Behavior
All persistent state is remote Tahoe directory creation/link mutation through the webapi. No local files are changed.

## Dependencies and Integration Points
Depends on `common.get_alias`, `common_http.do_http/check_http_error`, and webapi mkdir semantics. It integrates with CLI options for mutable directory format selection.

## Risks and Edge Cases
The linked-path URL uses `url_quote(path)` rather than `escape_path(path)`, which may encode slashes differently than other modules; this appears intentional/legacy but is a path-handling risk. It calls `check_http_error()` for linked mkdir but does not return early on nonzero status before reading/printing the body.

## Test Signals
`test_cli.py` covers mkdir help, normal mkdir, mutable type selection, unlinked mutable creation, bad mutable type, Unicode path creation, and missing/nonexistent aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_mkdir.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_mv.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_mv.py

## Purpose
Implements `tahoe mv` and related move/rename behavior within Tahoe directories by linking the target to an existing child and deleting the original.

## Important APIs, Types, and Functions
`mv(options, mode="move")` is the public command. It uses alias parsing, regex URL splitting, webapi JSON inspection, `PUT ?t=uri` for target creation/linking, and `DELETE` for source removal.

## Control Flow
The command resolves source and destination aliases, rejects cross-rootcap moves, fetches source JSON, determines whether destination denotes a directory by trailing slash or existing JSON node, builds the target URL and child name, prevents overwriting a directory with a file, writes the source URI to the destination with `PUT ?t=uri`, then deletes the original. If delete fails after the put, it returns 2 to signal partial move failure.

## State and Persistence Behavior
Persistence is entirely remote Tahoe directory mutation: target link creation followed by source link deletion. This ordering means delete failure can leave both links present, and the module reports that as a distinct error path.

## Dependencies and Integration Points
Depends on `common.get_alias`, `escape_path`, `common_http.do_http`, `json`, and `encodingutil.to_bytes`. It integrates with Tahoe webapi JSON node metadata and URI-link endpoints.

## Risks and Edge Cases
The move is not atomic because it uses separate PUT and DELETE requests. Cross-alias/rootcap moves are rejected. Existing destination directory handling depends on JSON type inspection and trailing slash semantics. Regex-based parent/name splitting is sensitive to unusual paths.

## Test Signals
`src/allmydata/test/cli/test_mv.py` covers rename, overwrite file, directory collision rejection, trailing-slash move into directory, nested directories, DELETE failure partial error, missing default alias, and nonexistent aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_mv.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_put.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_put.py

## Purpose
Implements `tahoe put`, uploading file data from a local path or stdin to an unlinked cap, alias path, or mutable file writecap, with optional mutable format/private key parameters.

## Important APIs, Types, and Functions
`load_private_key(path)` loads a PEM RSA private key, converts it to DER signing key bytes, and URL-safe-base64 encodes it for query use. `put(options)` is the command entry point and builds the upload URL, request body, and query parameters.

## Control Flow
The command normalizes the node URL, determines whether `to_file` is a direct mutable writecap, an alias/path, or omitted unlinked upload, rejects remote paths beginning with `/`, adds `mutable=true`, `private-key`, and `format` query arguments as needed, reads either a local binary file or all of stdin into `BytesIO`, performs `PUT`, and prints the resulting cap on success.

## State and Persistence Behavior
Remote persistence is via Tahoe webapi upload/link mutation. Local persistence is none. Stdin uploads are fully buffered to provide a content length compatible with `do_http()`.

## Dependencies and Integration Points
Depends on cryptography PEM loading, Tahoe RSA helpers, Twisted `FilePath`, `common.get_alias`, `escape_path`, and `common_http`. It integrates with webapi mutable creation, unlinked upload, and path-linked upload endpoints.

## Risks and Edge Cases
Private keys are passed as URL query parameters, which is functional but sensitive to logging of URLs. Supplying a private key for immutable upload raises a generic `Exception`. Stdin buffering can consume large memory. Mutable writecap detection is hard-coded to `URI:MDMF:` and `URI:SSK:`.

## Test Signals
`test_cli.py` covers put help/basic behavior and many downstream tests use `put` to seed grid state. Mutable/private-key-specific paths require focused tests beyond the broad CLI smoke coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_put.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_run.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_run.py

## Purpose
Implements `tahoe run`, starting a client or introducer node in the foreground through Twisted `twistd` machinery while adding Tahoe-specific basedir, pidfile, stdin-close, and startup-error behavior.

## Important APIs, Types, and Functions
Public exports are `RunOptions` and `run`. Helpers include `get_pidfile()`, `get_pid_from_pidfile()`, `identify_node_type()`, `MyTwistdConfig`, `DaemonizeTheRealService`, `DaemonizeTahoeNodePlugin`, and `on_stdin_close()`.

## Control Flow
`RunOptions` parses an optional basedir plus pass-through twistd args. `run()` validates basedir and node type from `*.tac`, constructs `twistd` args with `--nodaemon` and `--rundir`, checks Tahoe's own `running.process` pidfile, registers pidfile cleanup on reactor shutdown, installs an in-memory twistd plugin, and calls `runApp()`. `DaemonizeTheRealService.startService()` schedules actual client/introducer creation when the reactor runs, attaches the resulting service to its parent, maps known config/startup failures to concise stderr messages, and optionally stops the reactor when stdin closes.

## State and Persistence Behavior
Reads node directory contents and `tahoe.cfg` indirectly through client/introducer factories. Uses `running.process` pidfile parsing/checking/cleanup to prevent duplicate node starts. Does not daemonize because `--nodaemon` is always passed.

## Dependencies and Integration Points
Integrates with Twisted `twistd`, Tahoe client and introducer factories via `namedAny`, `HookMixin`, pid utilities, crawler pickle-migration errors, storage-client plugin errors, and node privacy/port assignment validation.

## Risks and Edge Cases
Twistd option pass-through is syntactically constrained: explicit NODEDIR must precede twistd options. Startup uses global/reactor scheduling and late imports, making failure modes asynchronous. Windows skips twistd pidfile disabling. Stdin-close shutdown is convenient for subprocess cleanup but may surprise callers unless `--allow-stdin-close` is used.

## Test Signals
`src/allmydata/test/cli/test_run.py` covers configuration/privacy/port/plugin/crawler migration error rendering, stdin-close behavior, run option parsing, pid checks, and reactor interactions. `test_cli.py` covers run help.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_run.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_status.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_status.py

## Purpose
Implements `tahoe status`, rendering node upload/download/mutable operation status and aggregate byte/file statistics from local node web endpoints.

## Important APIs, Types, and Functions
`_get_request_parameters_for_fragment()` builds authenticated POST request parameters. `_handle_response_for_fragment()` parses JSON and sanitizes URL-sensitive errors. `pretty_progress()` builds ASCII/Unicode progress bars. Renderers include `_render_active_upload`, `_render_active_download`, generic active/recent renderers, `render_active()`, `render_recent()`, and `do_status()`. `TahoeStatusCommand` registers CLI options.

## Control Flow
`do_status()` reads `private/api_auth_token` and `node.url` from the node directory, posts to `status?t=json` and `statistics?t=json` with the token, renders summary statistics, active operations, and recent operations, and returns 2 on retrieval/parsing errors. Rendering filters recent operations unless `--verbose` is set.

## State and Persistence Behavior
No writes. Reads local authentication and URL files from the node directory, then reads status/statistics over the node webapi.

## Dependencies and Integration Points
Depends on `BaseOptions`, `common_http.BadResponse`, `abbreviate_space/time`, and JSON status payloads from `allmydata.web.status.marshal_json`. Integrates with the node private API token mechanism.

## Risks and Edge Cases
The module overrides `print()` to replace unencodable Unicode, which protects terminals but can hide exact characters. Fetch failures are collapsed to exit code 2. `_handle_response_for_fragment()` deliberately avoids `format_http_error()` to avoid leaking sensitive `/uri/<key>` URLs.

## Test Signals
`src/allmydata/test/cli/test_status.py` covers progress bars, JSON helpers, fetch errors, renderer smoke tests, command help, and grid integration with skipped recent operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_status.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_unlink.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_unlink.py

## Purpose
Implements `tahoe unlink`/delete-like removal of a directory entry from a Tahoe directory.

## Important APIs, Types, and Functions
The command function is `unlink(options, command="unlink")`. It resolves aliases, requires a non-empty path, constructs `/uri/<rootcap>/<path>`, sends `DELETE`, and prints formatted success or error messages.

## Control Flow
After node URL normalization and alias resolution, the command rejects attempts to unlink an alias root without a child path. It sends one DELETE request and returns 0 only for HTTP 200.

## State and Persistence Behavior
All persistence is remote Tahoe directory entry removal. The target object may remain reachable by other caps/links; this command only removes the named link.

## Dependencies and Integration Points
Depends on `common.get_alias`, `escape_path`, `common_http.do_http`, and webapi DELETE semantics.

## Risks and Edge Cases
It cannot remove alias roots. It treats only status 200 as success, so alternate no-content delete responses would be reported as failures. As with other path commands, behavior depends on precise alias/path escaping.

## Test Signals
`test_cli.py` covers unlink help, missing default alias, nonexistent alias, missing path, and normal unlink behavior through CLI integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_unlink.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_webopen.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_webopen.py

## Purpose
Implements `tahoe webopen`, opening the node web UI or a specific Tahoe object/path in a browser.

## Important APIs, Types, and Functions
The public function is `webopen(options, opener=None)`. It resolves optional `where`, constructs a web URL, optionally appends `?t=info`, and calls an injectable opener for testability.

## Control Flow
If no target is supplied, the node URL is opened. Otherwise the command resolves aliases, treats path `/` as empty, builds `/uri/<rootcap>/<escaped-path>`, appends info query if requested, and opens the URL. Alias errors return 1.

## State and Persistence Behavior
No local or remote persistence; this is a URL construction and browser-dispatch helper.

## Dependencies and Integration Points
Depends on `common.get_alias`, `escape_path`, and `urllib.parse.url_quote`. Integrates with the host browser through the opener callback or default webbrowser behavior supplied by the caller.

## Risks and Edge Cases
Opening writecaps in a browser may expose sensitive caps to browser history/logs. URL construction must preserve Tahoe path escaping. Behavior for absent opener depends on runner wiring not shown in this file.

## Test Signals
`test_cli.py` covers webopen help, nonexistent alias handling, and URL construction/opening behavior with a fake opener.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/tahoe_webopen.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/types_.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/types_.py

## Purpose
Provides shared typing aliases for Tahoe script option declarations and subcommand tables.

## Important APIs, Types, and Functions
Exports `SubCommand`, `SubCommands`, `Parameters`, and `Flags`. `SubCommand` is a tuple of command name, `None`, Twisted `Options` subclass, and description.

## Control Flow
No runtime control flow beyond type alias evaluation at import time.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Depends on `typing` and `twisted.python.usage.Options`. Used by script modules such as `tahoe_invite.py` to annotate subcommand registries.

## Risks and Edge Cases
The comments note that command lists historically used mutable lists, while mypy requires tuple element shapes. Runtime code does not enforce these aliases.

## Test Signals
Coverage is indirect through script imports and CLI command registration tests in `test_cli.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/scripts/types_.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/stats.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/stats.py

## Purpose
Provides node statistics aggregation and CPU usage monitoring as Twisted services.

## Important APIs, Types, and Functions
`CPUUsageMonitor` implements `IStatsProducer`, samples wall/process CPU time every 60 seconds, and reports 1/5/15-minute CPU fractions plus total CPU. `StatsProvider` stores counters, registers producers, and returns `{"counters": ..., "stats": ...}` from `get_stats()`.

## Control Flow
`CPUUsageMonitor.startService()` records initial CPU time. A `TimerService` calls `check()` to append bounded samples. `_average_N_minutes()` calculates process CPU delta divided by wall-clock delta when enough samples exist. `StatsProvider.get_stats()` queries registered producers and logs the combined result.

## State and Persistence Behavior
State is in memory only: a bounded `deque` of CPU samples, a Unicode-key counter dictionary, and producer references. There is no disk persistence.

## Dependencies and Integration Points
Depends on Twisted service/TimerService, `IStatsProducer`, `dictutil.UnicodeKeyDict`, and Tahoe logging. The node web/status paths consume `StatsProvider.get_stats()` output.

## Risks and Edge Cases
CPU fraction can exceed 1.0 on multi-core workloads because it uses process CPU time over wall time. No guard exists for zero wall delta, though one-minute sampling makes that unlikely. Producer failures would propagate out of `get_stats()`.

## Test Signals
Test coverage is mostly indirect through status/statistics web and CLI tests. Dedicated producer registration/counter tests would strengthen confidence in edge cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/stats.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/__init__.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/__init__.py

## Purpose
Marks `allmydata.storage` as a Python package. The file is intentionally empty.

## Important APIs, Types, and Functions
No APIs, classes, functions, or module constants are defined.

## Control Flow
No runtime control flow.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Enables imports of sibling modules such as `allmydata.storage.immutable`, `http_client`, `http_server`, `crawler`, `expirer`, and `lease`.

## Risks and Edge Cases
Because it exports nothing, package-level imports must import concrete submodules explicitly. Empty-file behavior is stable.

## Test Signals
Covered indirectly by every test importing `allmydata.storage.*`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/common.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/common.py

## Purpose
Provides common storage helpers: storage-index base32 conversion, share directory layout, and unknown share container version exceptions.

## Important APIs, Types, and Functions
Defines `UnknownContainerVersionError`, `UnknownMutableContainerVersionError`, `UnknownImmutableContainerVersionError`, re-exports `DataTooLargeError`, and provides `si_b2a()`, `si_a2b()`, `si_to_human_readable()`, and `storage_index_to_dir()`.

## Control Flow
The conversion helpers are thin wrappers around Tahoe base32 utilities. `storage_index_to_dir()` encodes the storage index and returns `<first-two-chars>/<full-storage-index>` for share directory fanout.

## State and Persistence Behavior
No state. The directory-layout helper is central to persistent storage paths but does not itself touch disk.

## Dependencies and Integration Points
Used by storage server, crawler, HTTP client/server logging/path conversion, and tests. The exception types are raised by immutable/mutable share-file readers when on-disk magic/version values are unknown.

## Risks and Edge Cases
The functions assume valid storage-index bytes or base32 input; invalid values raise from lower-level base32 assertions/errors. Directory fanout is coupled to the on-disk share tree layout.

## Test Signals
`test_storage.py::UtilTests` covers encoding and `storage_index_to_dir()`, and corrupt-version tests exercise exception paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/crawler.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/crawler.py

## Purpose
Implements rate-limited background traversal of storage-server shares, plus JSON state serialization/migration helpers and a bucket-counting crawler.

## Important APIs, Types, and Functions
Defines `TimeSliceExceeded`, `MigratePickleFileError`, conversion helpers `_convert_cycle_data()`, `_convert_pickle_state_to_json()`, `_upgrade_pickle_to_json()`, `_confirm_json_format()`, `_dump_json_to_file()`, `_LeaseStateSerializer`, `ShareCrawler`, and `BucketCountingCrawler`.

## Control Flow
`ShareCrawler.startService()` schedules a slow-start timer. Each `start_slice()` processes prefixes until `cpu_slice` is exceeded, saves state, computes a sleep interval from `allowed_cpu_percentage`, and schedules the next slice. `start_current_prefix()` initializes cycles, walks sorted 10-bit prefix dirs, delegates to `process_prefixdir()`, tracks progress timing, and calls subclass hooks. `process_prefixdir()` skips already processed buckets and calls `process_bucket()` for subclasses.

## State and Persistence Behavior
Crawler state is JSON persisted through `_LeaseStateSerializer.save()` with temp-file move-into-place. State tracks version, current/last cycle, current cycle start time, last complete prefix, and last complete bucket. Legacy pickle state is rejected by `_confirm_json_format()` unless explicitly upgraded through `_upgrade_pickle_to_json()`. Bucket counting stores per-cycle prefix counts and sample storage indexes, pruning old cycles after completion.

## Dependencies and Integration Points
Depends on Twisted service/reactor, `FilePath`, `fileutil.move_into_place`, and storage-index base32 helpers. Subclasses such as `LeaseCheckingCrawler` attach to `StorageServer` and consume `server.sharedir`.

## Risks and Edge Cases
SIGKILL during a time slice can duplicate work after restart because state is saved at slice/cycle boundaries unless subclasses save more often. Pickle-format files now block startup/migration paths through `MigratePickleFileError`. Timing estimates may be `None` or inaccurate for very fast/slow prefixes. JSON migration must preserve tuple-key structures carefully.

## Test Signals
`src/allmydata/test/test_crawler.py` exercises prefix traversal, pacing, state persistence, resumption, one-shot behavior, and migration-related helpers. `tahoe_run.py` handles `MigratePickleFileError` as a startup error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/crawler.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/expirer.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/expirer.py

## Purpose
Implements `LeaseCheckingCrawler`, a storage crawler that examines share leases, records expiration/recovery statistics, and optionally cancels expired leases to reclaim storage.

## Important APIs, Types, and Functions
Defines `_convert_pickle_state_to_json()`, `_HistorySerializer`, and `LeaseCheckingCrawler`. Important methods include `create_empty_cycle_dict()`, `process_bucket()`, `process_share()`, `add_lease_age_to_histogram()`, `finished_cycle()`, and `get_state()`.

## Control Flow
For each bucket, `process_bucket()` stats the bucket dir, iterates numeric share files, calls `process_share()`, records corrupt shares for unknown container/struct errors, and accumulates bucket-level recovery predictions. `process_share()` loads immutable/mutable share files via `get_share_file()`, evaluates each lease against original expiry and configured age/cutoff policy, optionally cancels expired leases, and returns booleans indicating whether original/configured/actual policies would keep the share.

## State and Persistence Behavior
Uses the base crawler JSON state for cycle-to-date data and `_HistorySerializer` for `lease_checker.history.json`, retaining the last 10 cycles. Cycle state includes corrupt shares, histograms, expiration mode, and recovered/examined bucket/share byte counters split by mutable/immutable. Actual deletion happens through `sf.cancel_lease()` when `expiration_enabled` is true and all configured-valid leases are gone.

## Dependencies and Integration Points
Depends on `ShareCrawler`, `get_share_file()`, unknown container exceptions, Twisted logging, `FilePath`, and share lease APIs. Storage web status pages consume `get_state()` output.

## Risks and Edge Cases
Lease-age mode uses original expiration time unless override duration is configured, which is subtle. `sharetype` for a bucket is derived from the last processed share. Corrupt shares are logged and counted but not repaired. Windows may lack `st_blocks`; code falls back to share bytes or zero bucket disk bytes. Expiration is destructive when enabled.

## Test Signals
`src/allmydata/test/test_storage_web.py` exercises lease checker status/rendering and no-`st_blocks` behavior; storage tests cover underlying lease cancellation and share-file semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/expirer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/http_client.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/http_client.py

## Purpose
Implements the Tahoe HTTP storage client transport, including TLS pinning, swissnum authorization, CBOR schema validation, immutable uploads/downloads, mutable read-test-write operations, lease renewal, and corrupt-share reporting.

## Important APIs, Types, and Functions
Important types include `ClientException`, `_LengthLimitedCollector`, `ImmutableCreateResult`, `_TLSContextFactory`, `_StorageClientHTTPSPolicy`, `StorageClientFactory`, `StorageClient`, `StorageClientGeneral`, `UploadProgress`, `StorageClientImmutables`, `WriteVector`, `TestVector`, `ReadVector`, `TestWriteVectors`, `ReadTestWriteResult`, and `StorageClientMutables`. Helpers include `_encode_si()`, `limited_content()`, `read_share_chunk()`, and `advise_corrupt_share()`.

## Control Flow
`StorageClientFactory.create_storage_client()` parses NURLs, creates a Twisted/Tor agent, pins TLS by SPKI hash, and builds a base HTTPS URL plus swissnum. `StorageClient.request()` injects Authorization and Tahoe secret headers, serializes CBOR bodies off-thread, applies timeouts, and logs via Eliot. Higher-level clients construct endpoint URLs, send requests, decode CBOR under pycddl schemas, and map HTTP status codes to typed results or `ClientException`.

## State and Persistence Behavior
Client state is connection-oriented: base URL, swissnum, treq client, HTTP connection pool, reactor clock, and optional cached Tor instance in the factory. No local storage is persisted. Remote persistence is triggered by storage-server operations such as allocate/write immutable shares, mutable RTW writes, and lease renewal.

## Dependencies and Integration Points
Depends on Twisted web client, treq, hyperlink, OpenSSL, cryptography certificates, pycddl, CBOR helpers, Range/Content-Range parsing, Eliot, Tahoe HTTP common utilities, Tor provider integration, and cputhreadpool offloading. Exposes an API used by Tahoe storage-client selection and tests.

## Risks and Edge Cases
Retry behavior is explicitly TODO for failed uploads/downloads. `limited_content()` bounds memory and silence but still buffers into `BytesIO`. TLS validation intentionally accepts self-signed/expired certs only when SPKI hash matches. Mutable RTW error reporting includes response content only for some paths. Content-Range validation is strict and treats unexpected OK responses for ranged reads as errors.

## Test Signals
`src/allmydata/test/test_storage_http.py` has extensive coverage for content-type helpers, secret extraction, authorization, schema validation, limited content length/timeouts, immutable upload/read/list/abort/conflict paths, mutable RTW/read/list paths, lease renewal, corrupt-share reporting, and shared range-read behavior. `test_storage_https.py` covers TLS policy behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/http_client.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/http_common.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/http_common.py

## Purpose
Provides shared HTTP storage protocol constants and helpers for content types, authorization headers, operation-secret enum values, and SPKI certificate hashing.

## Important APIs, Types, and Functions
Defines `CBOR_MIME_TYPE`, `get_content_type()`, `response_is_not_html()`, `swissnum_auth_header()`, `Secrets`, `get_spki()`, and `get_spki_hash()`.

## Control Flow
Header helpers parse Twisted `Headers` with Werkzeug `parse_options_header`, construct `Authorization: Tahoe-LAFS <base64-swissnum>`, assert non-HTML responses in tests, and derive URL-safe base64 SHA-256 hashes of certificate SubjectPublicKeyInfo bytes.

## State and Persistence Behavior
No state or persistence.

## Dependencies and Integration Points
Used by both HTTP client and server. Depends on cryptography certificate serialization, hashlib SHA-256, Twisted headers/response interfaces, and Werkzeug header parsing.

## Risks and Edge Cases
`response_is_not_html()` is test-oriented and asserts for non-404 HTML responses. `get_content_type()` uses only the first content-type header value. SPKI hashes strip padding for NURL embedding, so callers must consistently use the same encoding.

## Test Signals
`test_storage_http.py::HTTPUtilities` covers content-type parsing, while HTTP auth/client/server tests exercise `Secrets`, `swissnum_auth_header()`, and non-HTML response assertions. `test_storage_https.py` covers SPKI-pinning integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/http_common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/http_server.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/http_server.py

## Purpose
Implements the HTTP storage server API for Tahoe storage operations, including authorization, CBOR validation/encoding, immutable upload lifecycle, mutable RTW operations, lease renewal, range reads, corrupt-share notifications, TLS endpoint wrapping, and NURL construction.

## Important APIs, Types, and Functions
Important definitions include `ClientSecretsException`, `_extract_secrets()`, `_authorization_decorator()`, `_authorized_route()`, `StorageIndexUploads`, `UploadsInProgress`, `StorageIndexConverter`, `_HTTPError`, `_ReadAllProducer`, `_ReadRangeProducer`, `read_range()`, `_add_error_handling()`, `read_encoded()`, `HTTPServer`, `_TLSEndpointWrapper`, `build_nurl()`, and `listen_tls()`.

## Control Flow
Each route is decorated to clear default HTML content type, verify swissnum Authorization, extract required `X-Tahoe-Authorization` secrets, and log request/response metadata. Immutable creation validates CBOR allocate requests, calls `StorageServer.allocate_buckets()`, and tracks returned `BucketWriter`s by upload secret. PATCH writes stream request content into the bucket at the Content-Range offset, returning remaining ranges and closing on completion. Reads use producer-backed range/full-body streaming. Mutable RTW validates CBOR, converts vectors to storage-server tuples, and returns read data plus success. TLS helpers wrap endpoints and generate `pb`/`pb+...` NURLs with SPKI hash userinfo and swissnum path.

## State and Persistence Behavior
`HTTPServer` owns in-memory `UploadsInProgress`, removed via a bucket-writer close handler when uploads finish, abort, or time out. Durable share data and leases are persisted by the underlying `StorageServer`, `BucketWriter`, and mutable share APIs. CBOR responses may be spooled to a temporary file before producer streaming.

## Dependencies and Integration Points
Depends on Klein/Twisted web server, pycddl, cbor utilities, Tahoe `StorageServer`, immutable `BucketWriter`, base32 storage-index conversion, werkzeug range/accept parsing, TLS certificate loading, and Tahoe secret/auth helpers. It is the server-side counterpart to `storage/http_client.py`.

## Risks and Edge Cases
The immutable allocate endpoint intentionally leaks existence of parallel in-progress uploads for the same storage index/share. Mutable RTW accepts very large bodies (`2**48` max) but uses mmap/off-thread validation to limit copies. Range support is intentionally narrow: one byte range with explicit end. Upload content length mismatch hits assertions. Secret extraction requires exact required-secret sets and 32-byte lease secrets.

## Test Signals
`test_storage_http.py` extensively covers auth failures, secret validation, storage-index converter, schema validation, MIME negotiation, immutable upload conflicts/aborts/timeouts/listing, mutable RTW/listing/wrong write enabler, corrupt-share reporting, lease renewal, and read range behavior. `test_storage_https.py` covers `_TLSEndpointWrapper` and TLS policy interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/http_server.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/immutable.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/immutable.py

## Purpose
Implements persistent immutable share files and the bucket writer/reader objects used by Foolscap and HTTP storage protocols.

## Important APIs, Types, and Functions
Defines `_fix_lease_count_format()`, `ShareFile`, `BucketWriter`, `FoolscapBucketWriter`, `BucketReader`, and `FoolscapBucketReader`. `ShareFile` handles on-disk data and lease records. `BucketWriter` manages in-progress upload ranges, conflicts, timeouts, final rename, and abort. `BucketReader` reads committed share bytes and reports corruption.

## Control Flow
Creating a `ShareFile` writes a schema header and later appends leases after the maximum data area. Opening an existing file reads version, lease count, schema, data length, and lease offset. `BucketWriter.write()` resets a 30-minute timeout, checks overlapping writes for byte equality, writes data, updates a `RangeMap`, records server latency/counts, and returns completion. `close()` renames incoming to final location and cleans empty incoming dirs. `abort()` removes incoming state and notifies the storage server.

## State and Persistence Behavior
Immutable share files persist as `version`, capped data length, lease count, share data, and fixed-size lease records. Uploads are staged under incoming paths, then atomically renamed to final share paths on close. Lease add/renew/cancel mutates records in place; cancelling the last lease unlinks the share. `BucketWriter` tracks required ranges in memory.

## Dependencies and Integration Points
Depends on versioned schemas from `immutable_schema`, lease serializers, `RangeMap`, Foolscap `Referenceable`, Tahoe storage interfaces, `fileutil`, logging, and `StorageServer` callbacks/counters. HTTP server tracks `BucketWriter` instances directly; Foolscap wrappers expose remote methods.

## Risks and Edge Cases
Crashes during lease compaction could leave partially rewritten lease records, though ordering tries not to lose non-cancelled leases. `close()` cannot assert completion for backward compatibility with old Foolscap clients. Timeout/abort cleanup must avoid deleting non-empty shared incoming dirs. Lease count format is test-configurable and can overflow.

## Test Signals
`test_storage.py` covers share create/read/write, bounds, overlapping writes, required ranges, timeouts, close/abort cleanup, bad versions, lease renewal/cancel/overflow, immutable length, server allocation, and Foolscap bucket wrappers. HTTP tests add upload/read/conflict coverage through the new transport.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/immutable.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/immutable_schema.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/immutable_schema.py

## Purpose
Defines versioned immutable share container schemas and header creation logic.

## Important APIs, Types, and Functions
`_Schema` stores a version number and lease serializer, and `header(max_size)` builds the 12-byte immutable share header. Module constants are `ALL_SCHEMAS`, `ALL_SCHEMA_VERSIONS`, and `NEWEST_SCHEMA_VERSION`. `schema_from_version(version)` resolves a schema object.

## Control Flow
On import, schemas for immutable versions 1 and 2 are built from lease-schema serializers. `header()` packs version, capped 32-bit share size, and zero initial lease count. `schema_from_version()` linearly searches known schemas.

## State and Persistence Behavior
No runtime state beyond constants. The header format directly determines persisted immutable share-file metadata. The size field is saturated at `2**32 - 1` for downgrade compatibility.

## Dependencies and Integration Points
Used by `ShareFile` to write new containers and decode existing versions. Depends on `.lease_schema.v1_immutable` and `.lease_schema.v2_immutable`.

## Risks and Edge Cases
The schema set is unordered, though newest is computed by max version. Unknown versions return `None` and are translated by `ShareFile` into `UnknownImmutableContainerVersionError`.

## Test Signals
`test_storage.py` property tests sample all immutable schemas for read/write, bounds, lease overflow, and secret behavior. Bad-version storage tests exercise lookup failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/immutable_schema.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/lease.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/storage/lease.py

## Purpose
Defines storage lease interfaces and concrete lease records for immutable and mutable shares, including hashed-secret wrappers for safer persisted lease secrets.

## Important APIs, Types, and Functions
Exports `IMMUTABLE_FORMAT`, `MUTABLE_FORMAT`, `ILeaseInfo`, `LeaseInfo`, `HashedLeaseInfo`, and `_HashedCancelSecret`. `LeaseInfo` serializes/deserializes immutable and mutable lease records, compares renew/cancel secrets, computes age, and creates renewed copies. `HashedLeaseInfo` proxies `ILeaseInfo` while hashing candidate secrets before comparison.

## Control Flow
`LeaseInfo.from_immutable_data()` and `from_mutable_data()` unpack struct records into attrs objects. `to_immutable_data()` and `to_mutable_data()` pack fields for persistence. `renew()` returns an updated immutable attrs copy. `HashedLeaseInfo.is_*_secret()` hashes external candidates and delegates timing-safe comparison; `_HashedCancelSecret` allows in-process lease expiration code to cancel leases when only the hashed cancel secret is known.

## State and Persistence Behavior
Lease records persist owner number, renew secret, cancel secret, expiration time, and for mutable leases nodeid. Version-2 immutable schemas store hashed secrets through lease serializers. `LeaseInfo` objects are frozen; updates create new objects rather than mutating fields.

## Dependencies and Integration Points
Used by immutable and mutable share-file implementations, lease expiration, storage server lease renewal, and HTTP tests. Depends on attrs, Zope interfaces, Twisted `proxyForInterface`, base32 display, and timing-safe comparisons.

## Risks and Edge Cases
`get_grant_renew_time_time()` estimates grant time by subtracting a fixed 31-day interval, so age is approximate. `_HashedCancelSecret` is intentionally an internal bypass and would be dangerous if exposed over a network API. `nodeid` validation is strict 20-byte data for mutable leases.

## Test Signals
`test_storage.py::LeaseInfoTests` covers renew/cancel secret comparison, serialized sizes, and storage share tests cover hashed secret behavior through immutable schemas and lease renewal/cancellation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/storage/lease.py -->
