# Research: subset-b-007898

This grouped report covers Tahoe-LAFS CLI test modules and related test helpers. Each section preserves its original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_cli.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_cli.py

## Purpose
This module is the broad smoke and behavior suite for many Tahoe-LAFS CLI entry points. It verifies debug capability decoding, alias parsing, help strings, top-level runner option parsing, admin key commands, and graceful error behavior for user-facing commands such as `get`, `ln`, `manifest`, `mkdir`, `unlink`, `stats`, and `webopen`. It also intentionally imports the script modules near the top so import regressions in command modules are caught.

## Important APIs, Types, and Functions
- `CLI._dump_cap` constructs `debug.DumpCapOptions`, parses arguments, runs `debug.dump_cap`, and returns captured stdout.
- `CLI._catalog_shares` constructs `debug.CatalogSharesOptions` and captures stdout/stderr from `debug.catalog_shares`.
- `CLI.test_alias` exercises `allmydata.scripts.common.get_alias`, `DEFAULT_ALIAS`, and `DefaultAliasMarker` with explicit aliases, raw `URI:` values, Windows drive-letter behavior via `common.pretend_platform_uses_lettercolon`, and missing aliases.
- `Help` instantiates option classes including `cli.GetOptions`, `cli.PutOptions`, `cli.CpOptions`, `cli.MakeDirectoryOptions`, `tahoe_run.RunOptions`, and `create_node` option classes to validate generated usage text.
- `Ln`, `Errors`, `Get`, `Manifest`, `Mkdir`, `Unlink`, `Stats`, and `Webopen` combine `GridTestMixin` and `CLITestMixin` to run real CLI flows against an in-memory/no-network grid.
- `Admin` uses `run_cli("admin", ...)` to validate `generate-keypair` and `derive-pubkey` output against `allmydata.crypto.ed25519` helpers.
- `Options.parse` uses `runner.Options` and unwraps `subOptions` to validate top-level argument dispatch.

## Control Flow
Most tests build a command object, grid, or client directory, invoke a CLI helper, then attach Deferred callbacks that assert exit code, stdout/stderr, and persisted state. Capability tests construct CHK, Literal, SDMF, MDMF, and directory URI objects, feed them to `tahoe debug dump-cap`, and assert printed fields for keys, storage indexes, renewal secrets, lease secrets, and read-only/verifier forms. Alias tests run pure parsing checks before command-specific classes test how missing aliases are surfaced. The option parser tests traverse from top-level `runner.Options` to command-specific options, ensuring flags are accepted or rejected at the right layer.

## State and Persistence Behavior
The module writes temporary client directories and config-like files under test-specific `cli/...` paths, including `private/secret`, `node.url`, and `private/root_dir.cap`. Grid-backed tests create aliases, directories, mutable/immutable nodes, and local files, then verify resulting Tahoe state through follow-up CLI calls. Some tests monkey-patch process-local state, such as `common.pretend_platform_uses_lettercolon`, `webbrowser.open`, and `HTTPConnection.endheaders`, and restore it with `try/finally` or Deferred cleanup. The runner exception test swaps in a `MemoryReactor` via `AlternateReactor` and checks that the reactor ran and stopped after dispatch failure.

## Dependencies and Integration Points
The suite integrates with `allmydata.uri`, `allmydata.immutable.upload`, `allmydata.dirnode.normalize`, `allmydata.scripts.common`, `common_http`, `debug`, `runner`, and individual command modules. It depends on Twisted Trial, `MemoryReactor`, `AlternateReactor`, the Tahoe test `GridTestMixin`, and `CLITestMixin`. It also probes platform/encoding behavior through `listdir_unicode`, `get_io_encoding`, and filename representability skips.

## Risks and Edge Cases
High-risk areas are user-facing error messages, alias ambiguity with Windows drive letters, raw-cap path parsing, secret derivation output, Unicode filename handling, malformed share catalogs, socket connection failures, and correct cleanup after monkey-patching. Capability-output assertions are intentionally brittle because they lock down cryptographic formatting and derived-secret values. The tests also protect against stack traces leaking to users when aliases are absent or invalid.

## Test Signals
Strong positive signals include exhaustive capability variants, parser rejection checks, Deferred grid command round-trips, exact error-message assertions, and help text validation. Residual gaps are that many assertions check snippets rather than full structured results, and several command behaviors are delegated to more focused modules in the same folder.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_cli.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_cp.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_cp.py

## Purpose
This module is the detailed behavior suite for `tahoe cp`. It validates local-to-grid, grid-to-local, grid-to-grid, filecap/dircap, recursive, Unicode, mutable overwrite, read-only mutable, verbose output, trailing slash, destination naming, duplicate directory, empty directory, and collision behavior.

## Important APIs, Types, and Functions
- `Cp` is the main command behavior test case using `GridTestMixin` and `CLITestMixin`.
- `CopyOut` is a table-driven test case for copying Tahoe objects out to the local filesystem.
- `COPYOUT_TESTCASES` encodes dozens of `cp`/`cp -r` scenarios with expected filesystem results or normalized error codes.
- `CopyOut.do_setup` builds a Tahoe hierarchy containing parent dircaps, child dircaps, filecaps, alias mappings, empty directories, and colliding directory names.
- `CopyOut.run_one_case`, `do_one_test`, and `do_tests` substitute caps into table rows, reset the local target tree, run the CLI, normalize stderr into symbolic errors, and compare observed output trees.

## Control Flow
The `Cp` class starts with simple parser and Unicode filename checks, then builds increasingly complex grids. Tests create aliases, upload files, call `cp`, use `get` or `ls --json` to inspect results, and assert both content and capability stability. Mutable tests capture original read-write/read-only URIs, copy new local data over existing mutable nodes, and verify in-place updates retain mutable URIs while immutable replacements produce new caps. The copy-out matrix creates a known Tahoe filesystem once, then iterates every scenario from the table, resetting the local destination for each row.

## State and Persistence Behavior
The tests create local source files, symlinks, output directories, target files, and full directory trees under test basedirs. Remote state includes aliases, mutable files, immutable files, literal filecaps, directory caps, nested directories, empty directories, and read-only links. `CopyOut.check_output` walks the local target tree and encodes both directory presence and file contents into a set for comparison. The read-only mutable tests intentionally preserve server state after failed overwrites to confirm no partial update occurred.

## Dependencies and Integration Points
The module depends on `cli.CpOptions`, Twisted `defer`, Tahoe `fileutil`, encoding helpers `quote_output`, `unicode_to_output`, `to_bytes`, `GridTestMixin`, `CLITestMixin`, and `skip_if_cannot_represent_filename`. It integrates with other CLI commands (`create-alias`, `put`, `mkdir`, `ln`, `ls`, `get`) as setup and verification tools, so it covers the copy command through realistic command-line workflows rather than isolated internals.

## Risks and Edge Cases
Covered risks include Unicode conversion failures, dangling symlink recursion assertions, unnamed caps copied into directories, target slash semantics, collisions from multiple source trees, directory-to-file errors, recursive copy requirements, duplicate origin/destination directories, mutable file content replacement, and read-only mutable overwrite refusal. The table-driven expectations are central because small path parsing changes can silently alter copy semantics.

## Test Signals
The strongest signal is the table-driven `CopyOut` matrix, which turns complex path/cap combinations into deterministic expected local trees or exact error classes. Additional high-value signals are content round-trips, JSON cap comparison, URI retention checks for mutable nodes, and exact verbose progress output. A residual risk is the large Deferred chains can obscure the failing step unless Trial reports callback context clearly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_cp.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_create.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_create.py

## Purpose
This module tests node/client/introducer creation CLI behavior and listener configuration merging. It verifies generated `tahoe.cfg` contents, share parameter validation, privacy settings, basedir clobber prevention, listener option compatibility, and Tor/I2P provider integration.

## Important APIs, Types, and Functions
- `read_config` loads `tahoe.cfg` using `configutil.get_config`.
- `MergeConfigTests` targets `create_node.merge_config` and `ListenerConfig`.
- `Config` tests `parse_cli`, `run_cli`, `create_node.write_node_config`, `create_node.write_client_config`, and `client.read_config`.
- `fake_config` monkey-patches `tor_provider.create_config` or `i2p_provider.create_config` and records calls.
- `Tor` and `I2P` validate provider option propagation and parser restrictions for launch/control/SAM settings.

## Control Flow
Parser-focused tests call `parse_cli` and expect `usage.UsageError` for invalid combinations. Creation tests run `create-client`, `create-node`, or `create-introducer`, load the generated config, and assert specific sections and values. Provider tests replace provider `create_config` with a fake returning a Deferred `ListenerConfig` or `None`, then run `create-node` with listener options and inspect both calls and persisted config. The slow-listener test installs a synthetic listener in `create_node._LISTENERS`, starts creation, fires the Deferred, and checks successful completion.

## State and Persistence Behavior
Tests create temporary basedirs and inspect generated `tahoe.cfg` files. Existing non-empty basedirs are used to ensure creation aborts without clobbering files. Configuration state under `[node]`, `[client]`, `[storage]`, `[connections]`, `[tor]`, and `[i2p]` is checked for exact values. Some tests temporarily remove importable modules with `disable_modules` to simulate optional dependency absence, and provider monkey-patches are scoped to individual test cases.

## Dependencies and Integration Points
The module integrates with `allmydata.scripts.create_node`, `allmydata.listeners.ListenerConfig`, `StaticProvider`, `tor_provider`, `i2p_provider`, Twisted Deferreds/reactor, Tahoe client config parsing, and common CLI helpers. It is a main contract for how CLI flags become node configuration and how optional network privacy providers plug into creation.

## Risks and Edge Cases
Risk areas include invalid share counts, `--hide-ip` fallback behavior when Tor/I2P modules are missing, incompatible `--listen`, `--hostname`, `--port`, and `--location` combinations, listener provider overlap in config keys, async listener creation, and avoiding overwrite of non-empty directories. Tor/I2P tests also protect against accepting mutually exclusive launch/control settings.

## Test Signals
The tests provide strong configuration-level signals because they parse the generated files instead of only checking exit codes. They also assert explicit usage-error strings for parser contracts and simulate optional dependency states. Gaps are mostly around actual Tor/I2P runtime behavior, which is intentionally replaced by provider fakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_create.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_create_alias.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_create_alias.py

## Purpose
This module tests `create-alias`, `add-alias`, alias persistence, alias validation, `webopen` URL construction, and Unicode alias/filename interoperability.

## Important APIs, Types, and Functions
- `CreateAlias._test_webopen` builds `runner.Options`, parses `webopen` with a test client directory, captures streams, and injects `urls.append` instead of opening a browser.
- `test_create` covers alias creation, duplicate rejection, manual alias file newline repair, invalid alias names, and web URLs for root, alias, subdir, file, and info modes.
- `test_create_unicode` covers non-ASCII aliases and remote filenames through `put`, `ls`, and `get`.

## Control Flow
The main test creates a grid, runs `create-alias`, loads aliases from `private/aliases`, creates a second alias, computes expected web URLs from `node.url`, and verifies duplicate create/add behavior. It then loops over invalid alias strings for both `create-alias` and `add-alias`. Webopen checks are synchronous calls into `cli.webopen` with parsed options. The newline-corruption regressions manually strip the trailing newline from the alias file before adding more aliases.

## State and Persistence Behavior
The central persistent artifact is the client directory's `private/aliases` file. Tests verify entries are not overwritten, duplicated, or concatenated after manual newline removal. The module also reads `node.url` and stores generated directory caps. Unicode tests persist alias entries keyed by Unicode names and remote files under those aliases.

## Dependencies and Integration Points
Dependencies include `fileutil`, `get_aliases`, `cli`, `runner`, `GridTestMixin`, `CLITestMixin`, `quote_output_u`, and URL quoting. It integrates alias persistence with web URL generation and with other CLI commands that resolve aliases.

## Risks and Edge Cases
Important risks are corrupting a manually edited aliases file, accepting malformed aliases containing spaces/colons, duplicate alias replacement, incorrect URL quoting for caps and subpaths, and Unicode alias encoding. The webopen tests intentionally preserve even questionable user paths, such as a file path ending in `/`, because that is the CLI contract.

## Test Signals
The tests check both user-visible output and underlying alias map contents. Unicode flow does full write/list/read round-trips. The main residual gap is `list-aliases` Unicode behavior, explicitly left as a TODO in the source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_create_alias.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_grid_manager.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_grid_manager.py

## Purpose
This module tests the Grid Manager CLI and the `tahoe admin add-grid-manager-cert` subcommand. It validates grid-manager config creation, stdout config mode, public identity, server add/list/remove/sign flows, error handling, file permissions, and certificate installation into a node directory.

## Important APIs, Types, and Functions
- `GridManagerCommandLine.setUp` creates a `click.testing.CliRunner`.
- `invoke_and_check` runs a Click command and re-raises exceptions with their traceback, then asserts exit code zero.
- `GridManagerCommandLine` covers `grid_manager --config ... create`, `public-identity`, `list`, `add`, `sign`, and `remove`.
- `TahoeAddGridManagerCert` uses `run_cli("admin", "add-grid-manager-cert", ...)` to test the Tahoe admin subcommand.

## Control Flow
Click tests run inside isolated filesystems and inspect resulting files such as `config.json` and `storage0.cert.N`. Some tests feed config JSON through stdin with `--config -` and inspect stdout. Add/sign flows create a manager, add a storage server public key, sign certificates, parse JSON output, and confirm certificate content. Admin tests run the Tahoe CLI with missing arguments or stdin cert data, then inspect `tahoe.cfg` and written cert files.

## State and Persistence Behavior
Grid Manager state persists under the configured directory as `config.json` plus certificate files named by storage server and sequence. The admin command persists a certificate file such as `foo.cert` and updates `tahoe.cfg` with a `[grid_managers]` style mapping. Permission tests temporarily chmod the config directory to make certificate creation fail, skipping on Windows and superuser runs where permission semantics differ.

## Dependencies and Integration Points
This module depends on `allmydata.cli.grid_manager.grid_manager`, Click's test runner, Tahoe `jsonbytes`, Twisted Trial, `FilePath`, platform detection, and `run_cli`. It bridges the standalone Click-based grid-manager CLI with the Twisted/Tahoe admin command surface.

## Risks and Edge Cases
Risks include invalid config JSON producing friendly errors, accidental overwrite on repeated create, duplicate storage server names, missing servers for remove/sign, certificate sequence numbering, stdin/stdout config handling, platform-specific permission behavior, and missing required admin options.

## Test Signals
The suite has strong CLI-level signals: real command invocation, file layout checks, JSON parsing, and error-output assertions. It does not validate cryptographic certificate verification deeply; it mainly confirms command mechanics and persistence format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_grid_manager.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_invite.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_invite.py

## Purpose
This module tests `tahoe invite` and `create-client --join` invitation flows over a controlled in-memory magic-wormhole implementation. It validates successful invite generation, join-side config creation, share-parameter propagation, introducer FURL handling, and protocol ability negotiation failures.

## Important APIs, Types, and Functions
- `open_wormhole` creates a `MemoryWormholeServer`, injects it into `runner.Options`, creates one wormhole endpoint, and returns a `run_cli` partial, wormhole, and code.
- `make_simple_peer` returns an async peer function that waits for the invite wormhole, mirrors its code, and sends preselected JSON messages.
- `send_messages` serializes JSON-like values with `dumps_bytes` and sends them over a wormhole.
- `concurrently` runs client and server coroutine/generator functions through `defer.gatherResults`.
- `Join` tests consuming an invitation during `create-client --join`.
- `Invite._invite_success` factors successful server-side invite tests.

## Control Flow
Join tests create one end of a wormhole, send server abilities and invite payloads, run `create-client --join <code>`, and inspect the resulting client config. Invite tests create an introducer directory, write `private/introducer.furl` when needed, run the server-side `invite` command with injected wormhole options, and concurrently run a simple peer that sends client abilities. After success, the peer reads two server messages: abilities followed by the invitation.

## State and Persistence Behavior
Tests create introducer and client node directories. `private/introducer.furl` is manually written because the introducer is not started. `tahoe.cfg` may be overwritten with specific share settings, then read back through `read_config` or direct file reads. Joined clients persist nickname, introducer FURL, and share settings into their config. Wormhole state lives only in memory and is isolated per test.

## Dependencies and Integration Points
The module depends on Twisted Deferreds, `runner.Options`, `run_cli`, `GridTestMixin`, `CLITestMixin`, `read_config`, Tahoe JSON byte helpers, and `.wormholetesting`. It is the integration point between CLI creation, introducer configuration, invitation protocol JSON, and magic-wormhole transport abstraction.

## Risks and Edge Cases
Covered risks include unknown invite payload keys, missing introducer FURL, missing nickname argument, wrong or missing client abilities, wrong or missing server abilities, and share configuration defaults. The tests ensure unsupported protocol versions fail with clear messages while harmless unknown invite fields are ignored on join.

## Test Signals
The tests exercise both protocol directions and parse real JSON messages exchanged over the fake wormhole. They also verify persisted client config after join. A limitation is that real network wormhole behavior is intentionally replaced by the in-memory helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_invite.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_list.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_list.py

## Purpose
This module tests `tahoe ls` behavior for normal directories, missing entries, unrecoverable directories, direct filecaps, unknown caps, read-only alias listing, and JSON output for MDMF/SDMF/immutable nodes.

## Important APIs, Types, and Functions
- `List.test_list` builds a directory with Unicode entries, one-share and zero-share damaged subdirectories, unknown child caps, and direct filecap listing assertions.
- `List._create_directory_structure` creates a directory containing MDMF, SDMF, and immutable files for format tests.
- `test_list_readonly` checks `list-aliases --readonly-uri`.
- `test_list_mdmf` and `test_list_mdmf_json` assert human and JSON output include mutable formats and caps.

## Control Flow
The main test creates a dirnode via the test client, adds a Unicode file, creates damaged subdirectories by deleting shares, maps it to the `tahoe` alias, and runs `ls` variants. It then renames the Unicode child to ASCII to repeat key assertions independent of terminal encoding. Later it creates an immutable unknown child and checks both directory listing and direct unknown-cap listing. The MDMF helper creates mutable files with different versions and an immutable file, then links them into the directory before CLI listing.

## State and Persistence Behavior
Remote grid state is central: dirnodes, files, mutable nodes, damaged share sets, aliases, and unknown URI children. Local state is limited to test basedirs. Tests mutate the remote directory by moving a Unicode child to an ASCII name and by deleting shares to simulate unrecoverable objects.

## Dependencies and Integration Points
Dependencies include `upload.Data`, `MutableData`, `MDMF_VERSION`, `SDMF_VERSION`, `quote_output`, `GridTestMixin`, and `CLITestMixin`. The module integrates low-level node creation APIs with CLI listing, giving coverage of how web/API metadata is rendered by `ls`.

## Risks and Edge Cases
Risks include Unicode output conversion failures, missing path reporting, insufficient shares producing correct 410/Unrecoverable messages, direct filecap metadata without edge names, unknown objects still rendering with warnings, and JSON output preserving mutable format and cap fields. A suspicious detail is that `_create_directory_structure` assigns `_sdmf_uri = mdmf_node.get_uri()` instead of the SDMF node; tests may still pass due to broad string checks but this deserves attention if failures appear.

## Test Signals
The tests provide strong behavior signals through real grid objects, share deletion, CLI output checks, and JSON format/cap assertions. They also explicitly cover graceful missing alias errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_list.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_mv.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_mv.py

## Purpose
This module tests `tahoe mv` command semantics: renaming, overwriting files, moving into directories with trailing slash, nested path behavior, DELETE failure handling, and user-friendly alias errors.

## Important APIs, Types, and Functions
- `Mv.test_mv_behavior` is the main end-to-end scenario.
- `Mv.test_mv_error_if_DELETE_fails` monkey-patches `tahoe_mv.do_http` to simulate a failed source deletion after copy/link work.
- `test_mv_without_alias` and `test_mv_with_nonexistent_alias` validate validation of both source and target aliases.

## Control Flow
The main test creates two local files, uploads them, renames `file1` to `file3`, overwrites `file2`, creates a remote directory, checks that moving a file to a directory without trailing slash is rejected, then moves into the directory with a slash. It verifies the moved file exists at the destination and the old path returns 404. It also builds nested directories and ensures moving a nested file into another directory moves only the file, not an ancestor directory.

## State and Persistence Behavior
The tests persist local files and remote grid files/directories under a `tahoe` alias. Remote state is mutated by `mv`: source links should disappear, target links should appear or be overwritten, and directories should remain directories. The DELETE failure test temporarily replaces module-level `tahoe_mv.do_http` and restores it with `addBoth`.

## Dependencies and Integration Points
The module depends on `fileutil`, `GridTestMixin`, `CLITestMixin`, and `allmydata.scripts.tahoe_mv`. It uses other CLI commands (`create-alias`, `cp`, `mkdir`, `get`, `put`) to set up and verify move behavior.

## Risks and Edge Cases
Key risks are directory overwrite protection, trailing slash interpretation, nested destination basename selection, incomplete moves when DELETE fails, and validation order for missing aliases. The DELETE mock ensures the CLI does not print success or return a success code when cleanup fails.

## Test Signals
Signals are practical end-to-end assertions against remote behavior and HTTP failure injection. Coverage is narrower than `cp`, but it targets the high-risk semantics for a move operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_mv.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_put.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_put.py

## Purpose
This module tests `tahoe put` for immutable and mutable uploads, stdin and file sources, linked and unlinked destinations, explicit private-key mutable creation, format selection, direct mutable cap updates, Unicode filenames, missing aliases, and leading-slash rejection.

## Important APIs, Types, and Functions
- `Put` combines grid and CLI mixins for command execution.
- `_test_mutable_specified_key` validates `--private-key-path` by deriving mutable keys from an OpenSSL RSA private key and comparing them to the returned cap.
- `_check_mdmf_json`, `_check_sdmf_json`, and `_check_chk_json` validate `ls --json` format and cap families after uploads.
- `test_format` is a matrix over `--mutable`, `--format=SDMF`, `--format=MDMF`, `--format=CHK`, linked destinations, and unlinked uploads.

## Control Flow
Upload tests write local data, run `put`, capture returned caps and stderr status (`200 OK` or `201 Created`), then run `get` or `ls --json` to verify content and metadata. Mutable tests first create caps, then call `put` against the same cap or path and verify in-place replacement returns the same cap. Private-key tests create data files, run `put --mutable --private-key-path`, parse the returned cap, derive expected keys from the PEM file, and fetch the data back.

## State and Persistence Behavior
State includes local data files, grid aliases, linked remote paths, unlinked caps, mutable file contents, and PEM key material in the adjacent test data directory. Mutable operations intentionally preserve capability identity while replacing content. Unicode tests create local non-ASCII filenames and upload them under non-ASCII remote names. The leading slash test checks that a bad remote path does not produce output.

## Dependencies and Integration Points
The module depends on Twisted Trial, `FilePath`, cryptography `load_pem_private_key`, Tahoe RSA key types, `uri.from_string`, `derive_mutable_keys`, `fileutil`, `get_aliases`, CLI option parsing, encoding helpers, and `CLITestMixin`/`GridTestMixin`. It integrates upload behavior with listing and download commands for verification.

## Risks and Edge Cases
Covered risks include stdin status messaging, deterministic LIT/CHK caps for small immutable data, path variants (`./`, absolute, dircap `:./`), mutable in-place updates, explicit private key compatibility, invalid format rejection, MDMF cap extension handling, nonexistent alias errors, Unicode encoding, and rejecting remote paths beginning with `/`.

## Test Signals
The module gives strong format and capability-family signals through JSON checks and direct cap parsing. Content round-trips catch data-path regressions. Some tests assert substrings in stderr rather than full responses, but that keeps the suite less brittle around status wording.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_put.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_run.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_run.py

## Purpose
This module tests `allmydata.scripts.tahoe_run`: daemon startup validation, stdin-close shutdown behavior, `--allow-stdin-close`, invalid pidfile handling, and pidfile content validation.

## Important APIs, Types, and Functions
- `DaemonizeTheRealServiceTests._verify_error` builds a minimal node directory, starts `DaemonizeTheRealService` under `MemoryReactor`, runs pending `callWhenRunning` hooks, and asserts stderr and reactor stop.
- `DaemonizeStopTests` constructs daemon services with custom stdin/stdout/stderr and a `MemoryReactor` whose `stop` method records calls.
- `RunTests.test_non_numeric_pid` calls `run` directly with a fake `runApp` collector.
- `RunTests.test_pidfile_contents` uses Hypothesis text generation with `check_pid_process` and expects `InvalidPidFile` for invalid pidfile data.

## Control Flow
Startup validation writes `tahoe.cfg` and `tahoe-client.tac`, parses `run` options, starts the daemon service, manually fires reactor startup hooks, and checks for configuration errors. Stop tests start the service, fire startup hooks, simulate stdin reader connection loss with `ConnectionDone`, and check whether the reactor stop hook was called depending on flags. `run` tests bypass process execution to confirm invalid pidfile data prevents `runApp` invocation.

## State and Persistence Behavior
Tests create temporary node directories with `tahoe.cfg`, `tahoe-client.tac`, and `running.process`/pidfile data. They use in-memory streams for stdout/stderr/stdin and a `MemoryReactor` to avoid spawning real daemon processes. Hypothesis writes a local `pidfile` in the current test context.

## Dependencies and Integration Points
Dependencies include `DaemonizeTheRealService`, `RunOptions`, `run`, `parse_options`, `check_pid_process`, `InvalidPidFile`, Twisted `MemoryReactor`, `AlternateReactor`, `Failure`, `ConnectionDone`, testtools matchers, and Hypothesis. The tests sit at the boundary between CLI option parsing, Twisted service lifecycle, and pidfile safety.

## Risks and Edge Cases
Risks include accepting invalid configs, allowing port 0, privacy misconfiguration, accidental daemon survival after stdin closes, incorrectly stopping when `--allow-stdin-close` is present, proceeding with corrupt pidfiles, and parsing arbitrary pidfile content. The Hypothesis property broadens pidfile validation beyond fixed examples.

## Test Signals
The service lifecycle tests provide strong deterministic signals without real process spawning. Reactor hook manual execution is coupled to implementation details, so refactors of startup scheduling may require test updates even if behavior remains valid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_run.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_status.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_status.py

## Purpose
This module tests `tahoe status` progress rendering, command rendering over status JSON, simple grid integration, and JSON HTTP helper validation.

## Important APIs, Types, and Functions
- `FakeStatus` supplies minimal status-object methods consumed by `marshal_json`.
- `ProgressBar` tests `pretty_progress` for ASCII and Unicode progress bars.
- `_FakeOptions` creates a temporary node directory with `private/api_auth_token` and `node.url`, and captures stdout/stderr.
- `Integration` starts a test grid, creates mutable activity, waits for the web status endpoint, and runs `tahoe status`.
- `CommandStatus` calls `do_status` with fake HTTP response sequences.
- `JsonHelpers` targets `_handle_response_for_fragment` and `_get_request_parameters_for_fragment`.

## Control Flow
Progress tests are pure function assertions. Integration setup creates a mutable file and verifies the client's web status endpoint responds before running the CLI. Renderer tests provide two JSON fragments to `do_status`: operations and counters/stats. Helper tests feed valid, null, or `BadResponse` values to response handling and validate GET/POST argument constraints.

## State and Persistence Behavior
`_FakeOptions` creates a temporary node-like directory with an API auth token and node URL. Integration tests create grid state and a mutable file to populate status data. Command renderer tests keep state in local `BytesIO`/`StringIO` response queues consumed by the fake HTTP function.

## Dependencies and Integration Points
The module integrates `allmydata.scripts.tahoe_status`, `allmydata.web.status.marshal_json`, immutable/mutable status classes, `common_http.BadResponse`, `do_http`, `GridTestMixin`, and `CLITestMixin`. It covers both direct helper APIs and the CLI-to-web-status path.

## Risks and Edge Cases
Covered risks include Unicode/ASCII progress calculations, no active/recent operations, renderer robustness over several status object types, HTTP fetch exceptions, null responses, BadResponse wrapping, and invalid GET/POST parameter combinations. Integration also protects the status command from failing when skipped operations are present.

## Test Signals
Signals are moderate to strong: pure progress output is exact, helper failures assert exceptions, and the integration test hits a real local web status endpoint. Renderer tests mainly assert no catastrophic failure, so detailed formatting regressions may not be caught.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/test_status.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/wormholetesting.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/wormholetesting.py

## Purpose
This file provides an in-memory implementation of the subset of magic-wormhole interfaces used by Tahoe-LAFS tests. It lets invite/join tests exercise wormhole protocol behavior without a real relay server or network.

## Important APIs, Types, and Functions
- Public `__all__`: `MemoryWormholeServer`, `TestingHelper`, `memory_server`, and `IWormhole`.
- `MemoryWormholeServer.create` mimics `wormhole.wormhole.create`, validates unsupported Tor/dilation options, creates `_MemoryWormhole` instances, and notifies app waiters.
- `TestingHelper.wait_for_wormhole` waits for a wormhole for a given appid/relay URL pair.
- `_verify` compares the fake `create` signature against the real wormhole `create` function enough to detect incompatible API drift.
- `_WormholeApp` stores wormholes by code, generates deterministic test codes, and manages waiters for peers.
- `_WormholeServerView` scopes app state by `(relay_url, appid)` and finds peer wormholes by code.
- `_MemoryWormhole` implements `IWormhole` methods used by tests: code allocation, `set_code`, `when_code`, `get_welcome`, `send_message`, `when_received`, aliases `get_message`/`get`, and `close`.
- `memory_server` returns a server plus helper pair.

## Control Flow
Tests call `MemoryWormholeServer.create` to create endpoint A. `get_code` lazily allocates a code through `_WormholeApp.allocate_code`. A second endpoint calls `set_code`, which registers it under the same code. `send_message` enqueues payload bytes on the sending endpoint's `DeferredQueue`. `when_received` locates the opposite endpoint under the same code and returns a Deferred for its queued payload. Helper waiters allow tests to wait until a command under test has created its wormhole before creating the peer endpoint.

## State and Persistence Behavior
All state is in memory. `MemoryWormholeServer._apps` maps `(relay_url, appid)` to `_WormholeApp`. `_WormholeApp.wormholes` maps codes to endpoint lists, `_waiting` stores Deferreds for future endpoints, and `_counter` generates deterministic codes. `_MemoryWormhole` stores its code, outgoing payload queue, and Deferreds waiting for code assignment. There is no persistence, cleanup, or network I/O.

## Dependencies and Integration Points
The helper depends on `attrs`, Twisted `Deferred`, `DeferredQueue`, `succeed`, `wormhole._interfaces.IWormhole`, the real `wormhole.wormhole.create` for signature comparison, and `zope.interface.implementer`. It is used by `test_invite.py` through `MemoryWormholeServer`, `TestingHelper`, and `memory_server`.

## Risks and Edge Cases
Risks include drift from real magic-wormhole APIs, unsupported Tor/dilation paths, multiple waiters for the same app key, code reuse, trying to receive before code assignment, and peer lookup when the other endpoint is absent. The implementation is intentionally incomplete and deterministic; it is not suitable outside tests.

## Test Signals
The `_verify` call runs at import time and catches broad signature incompatibility. Invite tests provide behavioral coverage of the message-passing paths. The helper itself does not have a standalone test suite in this subset, so behavior is mostly exercised indirectly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli/wormholetesting.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli_node_api.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli_node_api.py

## Purpose
This helper module exposes a small API for starting, observing, and stopping a Tahoe node via the CLI runner in tests. It also provides protocols for waiting for expected process output and adapting child process file descriptors to Twisted protocols.

## Important APIs, Types, and Functions
- Public `__all__`: `CLINodeAPI`, `Expect`, `on_stdout`, `on_stdout_and_stderr`, and `on_different`.
- `Expect` is a `Protocol` that buffers output and returns Deferreds that fire once expected bytes appear.
- `_ProcessProtocolAdapter` maps child stdout/stderr file descriptors to protocols and forwards connection/data/lost events.
- `on_stdout`, `on_stdout_and_stderr`, and `on_different` are convenience constructors for common fd mappings.
- `CLINodeAPI` is an `attr.s` class with `reactor`, `basedir`, and optional `process`.
- `CLINodeAPI._execute` spawns `python -b -m allmydata.scripts.runner ...`.
- `run`, `stop`, `stop_and_wait`, `active`, and `cleanup` manage process lifecycle.

## Control Flow
Tests create a `CLINodeAPI` with a reactor and node `FilePath`, then call `run` with a process protocol. `run` validates that the protocol provides `IProcessProtocol`, constructs runner arguments, spawns the process, and touches the exit-trigger file via `active`. Output protocols can use `Expect.expect` to wait until specific bytes arrive. `stop_and_wait` repeatedly sends `TERM` until Twisted reports `ProcessExitedAlready`, yielding via `deferLater` between attempts. `cleanup` wraps stopping and tolerates `ProcessTerminated`.

## State and Persistence Behavior
The helper exposes path properties for `running.process`, `node.url`, `private/storage.furl`, `private/introducer.furl`, `tahoe.cfg`, and the client exit-trigger file. `active` touches the exit-trigger file so the launched client should terminate after its built-in timeout if tests fail to stop it. Process state is stored in `self.process`.

## Dependencies and Integration Points
Dependencies include Twisted `Protocol`, `ProcessProtocol`, `IProcessProtocol`, `Deferred`, `deferLater`, `FilePath`, process errors, Eliot logging decorators, and Tahoe `_Client.EXIT_TRIGGER_FILE`. The module integrates tests with the actual `allmydata.scripts.runner` module by spawning a Python subprocess.

## Risks and Edge Cases
Risks include unhandled child fd output, expectations that never fire if output differs, process cleanup loops, process already exited conditions, ENOENT when checking activity before files exist, and environment leakage because subprocesses inherit `os.environ`. The output adapter intentionally logs unhandled fd data instead of failing directly.

## Test Signals
This is test infrastructure rather than a test suite. It enables higher-level CLI node integration tests to observe stdout/stderr and manage node lifetime. Its own reliability depends on Twisted process behavior and the exit-trigger safety file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/test/cli_node_api.py -->
