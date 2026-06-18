# subset-b-007607 research

Grouped research report for the requested source files. Each file section is delimited for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0272-urlstore.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0272-urlstore.sh

Purpose: exercises Kubo's experimental URL-backed filestore path through `ipfs add --nocopy --cid-version=1` against gateway URLs. It proves URL store entries can be created only after `Experimental.UrlstoreEnabled` is set, can be read through `ipfs get`, show up in `ipfs filestore ls`, verify with `ipfs filestore verify`, and fail once the remote gateway content disappears.

Important commands and control flow: the script creates deterministic random files, adds them normally with trickle DAGs and no raw leaves, launches an offline daemon, then uses the daemon gateway as the remote URL source. `test_urlstore` is parameterized by the add command and runs the full lifecycle: disabled-urlstore failures, enable config, URL ingest, retrieval, filestore listing/verification, GC of unpinned URL blocks, removal of original gateway content, failed verification, large-file ingest, trickle CID parity, and base32 CID output checks.

State and persistence: state spans the IPFS repo, the daemon gateway, filestore URL metadata, pins, and GC. URL-store blocks point to external URLs plus offsets, so removing the original gateway blocks turns previously valid filestore entries into verification errors and unreadable data. The test deliberately toggles daemon lifetime around config and remote availability.

Dependencies and integration points: depends on sharness helpers, `random-data`, `curl`, gateway/API ports, `ipfs add/get/cat/pin/repo gc/filestore/cid`, and Kubo's filestore/urlstore internals. It integrates CID conversion, raw-leaf UnixFS generation, trickle DAG layout, and gateway fetch behavior.

Risks and test signals: the test is sensitive to large 50 MB data generation, daemon startup timing, gateway reachability, exact `filestore ls` formatting, and CID constants. It provides strong regression signals for URL-store enablement, metadata offsets, GC behavior, retrieval through URL references, and `--cid-base=base32` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0272-urlstore.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0275-cid-security.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0275-cid-security.sh

Purpose: verifies Kubo rejects insecure CIDs and unsafe multihashes on write and read paths. It guards `verifcid` policy by checking `ipfs add`, `ipfs block put`, `ipfs cat`, `ipfs get`, repo GC, and traversal through a maliciously linked block.

Important commands and control flow: after repo init, it asserts `ipfs add --hash shake-128` fails with a "potentially insecure hash functions not allowed" reason and `ipfs block put --mhlen 19` fails with "digest too small". Helper `test_cat_get` runs the same read-side rejection offline and online. Helper `test_gc` injects prepared bad block files directly into the flatfs blockstore and expects `ipfs repo gc` to remove them. The final online case injects a valid-looking block that links to insecure content and ensures `ipfs cat` exits quickly with code 1 instead of hanging.

State and persistence: the test bypasses normal blockstore writes by copying fixture `.data` files into `$IPFS_PATH/blocks/*`, so it validates defensive reads and GC cleanup of persisted invalid blocks, not just API validation.

Dependencies and integration points: uses fixture data under `t0275-cid-security-data`, sharness helpers, daemon lifecycle, `go-timeout`, and CID/security validation shared by blockstore and DAG traversal.

Risks and test signals: failures may indicate policy drift in `verifcid.DefaultAllowlist`, flatfs layout changes, error-message churn, or traversal paths that fail to validate linked CIDs. Timeout assertion is important because rejecting malicious links must be bounded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0275-cid-security.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0276-cidv0v1.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0276-cidv0v1.sh

Purpose: validates interoperability between CIDv0 and CIDv1 for dag-pb UnixFS blocks. It confirms that equivalent multihash/content can be addressed by either CID version locally and across nodes, while GC behavior still respects pins and local references.

Important commands and control flow: deterministic files are added using CIDv1 with `--raw-leaves=false --pin=false` and CIDv0. `cid-fmt` checks version/codec and converts CIDv1 to CIDv0. The script confirms both blocks exist, runs GC, checks pinned CIDv0 survives while unpinned CIDv1 disappears, and verifies access through converted forms. It then creates a two-node `iptb` testbed, connects nodes, and tests fetching CIDv0 content by CIDv1 and CIDv1 content by CIDv0 over the network.

State and persistence: repo state includes pinned and unpinned DAG blocks; GC removes unpinned aliases while content remains accessible through an equivalent pinned block when available. Network state includes two initialized local IPFS nodes with LAN DHT loopback enabled.

Dependencies and integration points: relies on `cid-fmt`, `iptb`, `ipfs add/block stat/repo gc/cat`, pinning, Bitswap/content routing, and dag-pb CID conversion rules.

Risks and test signals: signals regressions in CID canonicalization, dag-pb v0/v1 conversion, provider/fetch logic, and GC treatment of equivalent links. It is timing-sensitive around daemon startup and network fetch timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0276-cidv0v1.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-dag-jose.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-dag-jose.sh

Purpose: validates the `dag-jose` IPLD plugin codec in offline and daemon-backed modes. It proves fixture files can be encoded as `dag-jose`, decoded back to their original codec, and rendered through other DAG output codecs.

Important commands and control flow: helper `test_dag_jose` iterates fixture files under `t0280-plugin-dag-jose-data`, derives input codec from the parent directory, runs `ipfs dag put --store-codec dag-jose --input-codec=<codec>`, then `ipfs dag get --output-codec <codec>` and diffs against the original. A second pass gets the same CIDs as `dag-cbor` and `dag-json` to ensure cross-codec traversal/rendering.

State and persistence: stored DAG nodes are inserted into the local repo, then read both offline and through a launched daemon. No permanent config is changed beyond test repo initialization.

Dependencies and integration points: depends on Kubo plugin registration, IPLD codec table, `ipfs dag put/get`, fixture codecs, `find`, `xargs`, and shell quoting.

Risks and test signals: regressions show up as missing plugin registration, broken codec roundtrips, fixture parsing changes, or DAG output codec incompatibility. The test is broad across fixtures but has limited assertion detail beyond successful diff/get.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-dag-jose.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-data/example.go -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-data/example.go

Purpose: provides a minimal Go plugin fixture for Kubo sharness plugin-loading tests. It exports `Plugins`, containing one implementation of `plugin.Plugin`, so `go build -buildmode=plugin` can produce a loadable `.so`.

Important APIs/types/functions: `Plugins` is the symbol Kubo's plugin loader discovers. `testPlugin.Name` returns `test-plugin`; `Version` returns `0.1.0`; `Init` receives `*plugin.Environment` and prints the repo path and config value to stderr with a `testplugin` prefix consumed by the shell test.

State and persistence: the plugin does not mutate Kubo state. It observes environment data and writes diagnostic output to stderr during initialization.

Dependencies and integration points: imports `github.com/ipfs/kubo/plugin`, `fmt`, and `os`. It integrates with the Kubo plugin loader's expected exported symbol and environment contract.

Risks and test signals: any change to plugin discovery, `plugin.Environment`, or Go plugin ABI can break this fixture. Its stderr format is part of `t0280-plugin.sh` assertions and should remain stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-data/example.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-fx.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-fx.sh

Purpose: verifies that the fx-based test plugin path is invoked during daemon startup when the test environment enables it.

Important commands and control flow: initializes a repo, exports `GOLOG_LOG_LEVEL=fxtestplugin=debug` and `TEST_FX_PLUGIN=1`, launches the daemon, then searches `daemon_err` for the expected log entry `invoked test fx function`.

State and persistence: only environment variables and daemon logs are involved; no repo content is written beyond initialization.

Dependencies and integration points: depends on sharness daemon helpers, Kubo's fx dependency-injection/plugin hook, go-log output routing, and the test plugin compiled into the binary under the `TEST_FX_PLUGIN` gate.

Risks and test signals: the test is a concise startup integration signal. It is sensitive to log message text, logger name/level, and changes in where daemon stderr is captured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-fx.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-git.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-git.sh

Purpose: validates the git IPLD codec plugin by importing raw git objects and traversing decoded DAG structures.

Important commands and control flow: extracts a fixture repository archive, then `test_dag_git` finds git object files and stores them using `ipfs dag put --store-codec=git-raw --input-codec=0x300078 --hash=sha1`. It reads every produced hash with `ipfs dag get`, checks a known tag object JSON, and traverses paths through author, tree file hash, and nested parent/tree entries.

State and persistence: fixture git objects become IPFS DAG blocks in the test repo. The test runs once offline and once with a daemon, reusing the same logical object graph.

Dependencies and integration points: relies on plugin codec registration, git raw codec number, SHA-1 multihash support, `ipfs dag put/get`, tar fixtures, and path traversal through IPLD selectors.

Risks and test signals: catches missing git plugin support, codec-number changes, JSON representation drift, SHA-1 allowance issues, and path traversal regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-git.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-peerlog.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-peerlog.sh

Purpose: tests the peerlog plugin's default-disabled behavior and config-enabled logging of peer IDs in an `iptb` cluster.

Important commands and control flow: creates a two-node testbed and starts it, then asserts node 0 logs do not contain `peerlog`. It stops, recreates the testbed, sets `Plugins.Plugins.peerlog.Config.Enabled true`, starts again, checks logs for `peerlog`, obtains node 1's peer ID, and confirms node 0 logs include that ID.

State and persistence: config state is written through `ipfs config` inside each testbed repo. Runtime state is daemon logs and peer connections.

Dependencies and integration points: depends on `iptb`, `startup_cluster`, Kubo plugin config namespacing, daemon logging, and peer discovery/connection startup.

Risks and test signals: sensitive to log timing and exact log inclusion. It provides useful coverage that plugin config is honored and peer observation hooks are active only when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin-peerlog.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin.sh

Purpose: exercises dynamic Go plugin loading, plugin failure handling, disable/re-enable config, plugin-specific config injection, and `--enable-plugins=false` command behavior.

Important commands and control flow: gated by `PLUGIN` prereq. It initializes a repo, confirms `ipfs id` works, writes an executable invalid `.so` and expects `ipfs id` to fail, removes it, builds `t0280-plugin-data/example.go` with `-buildmode=plugin`, and runs `test_plugin` to inspect stderr output. The helper validates whether plugin output is absent or matches expected repo/config lines. The script toggles `Plugins.Plugins.test-plugin.Disabled`, writes plugin config, and checks `--enable-plugins=false` suppresses loading.

State and persistence: modifies `$IPFS_PATH/plugins`, plugin config under `Plugins.Plugins.test-plugin`, and command stderr. The built plugin observes but does not mutate repo state.

Dependencies and integration points: depends on Go plugin support, build flags, plugin loader, Kubo config schema, `ipfs id`, sharness prereqs, and the fixture plugin's stderr contract.

Risks and test signals: strong signal for plugin ABI/load errors, bad plugin isolation, config-disable behavior, and CLI no-plugin flags. It is platform-sensitive because Go plugins are unavailable on some systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0280-plugin.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0290-cid.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0290-cid.sh

Purpose: comprehensive sharness coverage for `ipfs cid` commands, including base conversion, formatting, codec/multibase/multihash listings, numeric output, and error handling for incompatible CID options.

Important commands and control flow: the script defines known CIDs and expected outputs, tests `cid base32`, `cid format` with version/base/codec options from argv and stdin, validates `cid bases` with prefix and numeric modes, validates `cid codecs` with numeric and supported filters, validates `cid hashes` with numeric output, and exercises codec rewrites such as raw, dag-pb v0, dag-cbor, and base256emoji conversion.

State and persistence: this is mostly stateless command-line transformation; it does not require daemon state. Test output files are created and compared with expected fixtures generated inline.

Dependencies and integration points: depends on CID library behavior, multibase registry, multicodec registry, multihash registry, CLI formatting parser, stdin handling, and `test_cmp`.

Risks and test signals: exact registry output can churn when supported bases/codecs/hashes change. The test catches compatibility regressions in v0/v1 conversion rules, base encoders, unsupported codec errors, and stdin/argv handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0290-cid.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0295-multibase.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0295-multibase.sh

Purpose: validates `ipfs multibase` list, encode, decode, and transcode CLI behavior for stdin and file inputs, including failure messages for invalid prefixes/characters.

Important commands and control flow: creates expected encoded values, checks `multibase list`, encodes stdin and files with default/custom bases, decodes stdin and files, performs encode/decode roundtrips, transcodes between bases, and asserts errors on unknown prefixes and invalid characters.

State and persistence: no daemon or repo state is needed; temporary input and output files capture command results for `test_cmp`.

Dependencies and integration points: depends on multibase registry, CLI input dispatch, base-specific validators, and sharness comparison helpers.

Risks and test signals: good coverage for streaming/file input parity and error semantics. It is sensitive to list ordering and registry additions if expected fixtures are exact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0295-multibase.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0320-pubsub.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0320-pubsub.sh

Purpose: integration-tests experimental pubsub command behavior across a five-node `iptb` cluster, including config-enabled mode, daemon-flag-enabled mode, unsigned-message filtering, and CLI flag precedence.

Important commands and control flow: initializes a testbed, disables DHT, defines helpers using `ipfsi` to publish, subscribe, list topics, list peers, and verify JSON/base64url payloads. It runs normal pubsub tests after enabling `Pubsub.Enabled`, then again with `--enable-pubsub-experiment`. It disables signing on nodes 1-3 and confirms a subscriber receives no unsigned messages. Finally it sets config enabled but launches daemon with `--enable-pubsub-experiment=false`, expecting pubsub commands to fail with the disabled-feature error.

State and persistence: state includes multi-node configs, daemon flags, FIFOs used to synchronize long-running subscribers, and pubsub topic membership. No durable content is required beyond repo config.

Dependencies and integration points: depends on `iptb`, pubsub router, command JSON encoding, multibase base64url output, shell FIFOs, `jq`, daemon flags, and config precedence.

Risks and test signals: highly timing-sensitive around subscriber readiness and peer discovery. Strongly signals regressions in pubsub enablement, message encoding, signing policy, and config-vs-CLI precedence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0320-pubsub.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0321-pubsub-gossipsub.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0321-pubsub-gossipsub.sh

Purpose: verifies pubsub behavior when all nodes use the `gossipsub` router.

Important commands and control flow: creates a five-node testbed, sets `Pubsub.Router gossipsub` on every node, starts with `--enable-pubsub-experiment`, captures peer IDs, starts long-running JSON subscribers in the background, checks `pubsub peers`, publishes payloads from file and stdin, and compares subscriber output to base64url-encoded expected values.

State and persistence: runtime-only state covers topic subscriptions, peer IDs, FIFOs, output files, and daemon pubsub state. Config persists router selection in each repo.

Dependencies and integration points: depends on gossipsub configuration, `iptb`, `jq`, multibase encoding, shell FIFOs, and pubsub CLI JSON format.

Risks and test signals: catches router-specific discovery/delivery regressions and JSON encoding changes. Readiness sleeps are a flake risk when cluster startup or subscription propagation slows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0321-pubsub-gossipsub.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0322-pubsub-http-rpc.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0322-pubsub-http-rpc.sh

Purpose: validates HTTP RPC input validation for `/api/v0/pubsub/pub` topic arguments.

Important commands and control flow: initializes and launches a daemon with pubsub enabled. It posts multipart data to `pubsub/pub?arg=foobar` and expects an error that URL args must be multibase encoded. It then posts with a regular base64 multibase prefix and expects an error requiring URL-safe base64url.

State and persistence: only daemon runtime pubsub/API state and temporary data/result files are used.

Dependencies and integration points: depends on HTTP API routing, pubsub command argument parsing, multibase validation, `curl`, and sharness `test_should_contain`.

Risks and test signals: targeted regression coverage for browser/HTTP-safe pubsub topic encoding. Sensitive to exact error text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0322-pubsub-http-rpc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0400-api-no-gateway.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0400-api-no-gateway.sh

Purpose: verifies the RPC API listener does not behave as a general IPFS gateway by default, preventing browser scripting vulnerabilities, while `--unrestricted-api` explicitly enables gateway behavior.

Important commands and control flow: imports a CAR fixture with `ipfs dag import`, sets a known fixture hash, launches a default daemon and expects `http://127.0.0.1:$API_PORT/ipfs/$HASH` to return 404. It restarts with `--unrestricted-api` and expects the same URL to return 200.

State and persistence: content is imported into the test repo; daemon flag determines API route exposure.

Dependencies and integration points: depends on CAR import, API listener, gateway route gating, `test_curl_resp_http_code`, and daemon lifecycle helpers.

Risks and test signals: catches accidental exposure of gateway routes on the API port and regressions in the explicit unrestricted mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0400-api-no-gateway.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0401-api-browser-security.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0401-api-browser-security.sh

Purpose: validates browser-origin protections for the RPC API, including localhost origins, known IPFS Companion extension IDs, and custom CORS allowlists.

Important commands and control flow: after daemon launch, browser-like POSTs without `Origin` or with invalid origin must return 403. Localhost origins for IPv4, IPv6, and hostname must return 200 and include the peer ID. Random extension origins are rejected, while production/beta Companion extension origins are allowed. The script then configures `API.HTTPHeaders.Access-Control-Allow-*`, restarts, confirms Companion still works, validates an OPTIONS preflight response, and checks valid custom origin POST access.

State and persistence: persists API CORS headers in repo config and observes daemon HTTP response headers/status codes.

Dependencies and integration points: depends on API origin security middleware, config header overrides, extension allowlist, HTTP preflight handling, `curl`, and peer identity.

Risks and test signals: high security value. Sensitive to header casing/text, HTTP protocol formatting, and changes to extension allowlist. Failures can indicate either overly permissive browser API access or broken legitimate localhost/Companion access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0401-api-browser-security.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0410-api-add.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0410-api-add.sh

Purpose: narrow regression test that the HTTP API `add` command response includes a `Size` field.

Important commands and control flow: initializes and launches a daemon, pipes `hi` as multipart file data to `http://localhost:$API_PORT/api/v0/add`, and greps for `"Size": "11"` in the JSON response.

State and persistence: the uploaded data is added to the repo through the API; no further cleanup-specific behavior is asserted.

Dependencies and integration points: depends on HTTP multipart handling, UnixFS add response formatting, `curl`, and daemon lifecycle.

Risks and test signals: catches response schema regressions for API clients relying on `Size`. Exact size includes multipart/add semantics and may change if response accounting changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0410-api-add.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0500-issues-and-regressions-offline.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0500-issues-and-regressions-offline.sh

Purpose: offline regression collection for historical Kubo issues around stdin handling, help commands, large stdin adds, and `ipfs refs -e` output.

Important commands and control flow: verifies `ipfs init` works when stdin is occupied, `ipfs cat --help` and `ipfs pin ls --help` return under a timeout while stdin remains open, adds a 1 MiB random stream from stdin, runs recursive refs with edge output, and compares first-level refs extracted from edge output against `ipfs refs`.

State and persistence: initializes a repo, stores a 1 MiB object, and generates temporary hash/ref output files.

Dependencies and integration points: depends on command stdin behavior, timeout helper, UnixFS add, refs traversal, and edge formatting.

Risks and test signals: catches command hangs when stdin is open, regressions in refs output shape, and large stdin add failures. There is a typo in the test description text ("woks"), but it does not affect behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0500-issues-and-regressions-offline.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0600-issues-and-regressions-online.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0600-issues-and-regressions-online.sh

Purpose: online regression collection for HTTP API behavior, metrics, pin API response shape, malformed upload handling, offline daemon/mount behavior, and IPNS operations in offline-network daemon mode.

Important commands and control flow: starts a daemon with a non-empty repo, checks `/api/v0/commands?flags`, confirms `/api/v0/refs/local` returns NDJSON-like fields, posts to an arg-stdin command without crashing, checks daemon stderr for no panic, fetches Prometheus metrics, validates `pin/add` and `pin/rm` JSON responses, optionally uses `socat` to send malformed multipart data and expect 500 without daemon crash, then checks `ipfs daemon --offline --mount` fails. It restarts without network and publishes/resolves the self key offline.

State and persistence: involves daemon state, metrics endpoint, pins, key/IPNS records, and daemon stderr. It stops and restarts daemons across online and offline-network modes.

Dependencies and integration points: depends on HTTP API routes, metrics registry, pinning, multipart parser, `socat` prereq, IPNS publish/resolve, key listing, and sharness daemon helpers.

Risks and test signals: broad smoke coverage but sensitive to exact JSON ordering and metrics names. The offline IPNS section catches local routing/resolution regressions after daemon identity operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0600-issues-and-regressions-online.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0800-blake3.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0800-blake3.sh

Purpose: validates BLAKE3 multihash support across block, DAG, UnixFS add, and cat paths.

Important commands and control flow: defines known raw CIDs for `foo\n` using 32, 64, and 128 byte BLAKE3 digests. It runs `ipfs block put --mhtype=blake3 --cid-codec=raw` with default and explicit digest lengths, verifies `block get`, runs `ipfs dag put --hash=blake3` with raw codecs and `dag get`, then adds a raw-leaf file with `--hash=blake3` and checks `ipfs cat`.

State and persistence: stores raw blocks and UnixFS content in the local repo. No daemon is needed.

Dependencies and integration points: depends on multihash BLAKE3 registration, digest-length handling, raw codec, DAG command path, UnixFS add hash selection, and hard-coded CID constants.

Risks and test signals: catches missing BLAKE3 support, digest-length mishandling, CID generation changes, and read path incompatibilities. The comments warn that newline handling changes will produce different known hashes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0800-blake3.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/x0601-pin-fail-test.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/x0601-pin-fail-test.sh

Purpose: stress/regression test for managing a very large number of recursive pins.

Important commands and control flow: initializes and launches a daemon, records existing recursive pins, loops 9000 times adding and pinning a small file, then compares sorted recursive pin output with the union of new pins and original pins.

State and persistence: writes thousands of pinned objects into the repo and relies on pinset persistence and query correctness.

Dependencies and integration points: depends on daemon operation, `ipfs add`, `ipfs pin ls --type=recursive -q`, shell loop performance, and sharness comparison helpers.

Risks and test signals: intentionally expensive and likely excluded from normal runs by `x` prefix. It catches pinset scaling/corruption regressions but can be slow and storage-heavy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/x0601-pin-fail-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness_test_coverage_helper.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness_test_coverage_helper.sh

Purpose: shell utility that estimates sharness command coverage by matching `ipfs commands --flags` output against `ipfs` invocations in sharness test files.

Important functions and control flow: parses `-h/--help` and `-v/--verbose`, creates a timestamped temp directory, uses `git grep` to collect sharness lines containing `ipfs`, filters out test descriptions, comments, variable definitions, grep/cat/rmdir/echo false positives, and `/ipfs` or `.ipfs` path references, then calls `ipfs commands --flags`. `reverse` abstracts `tac` versus `tail -r`. `process_command` builds regexes for command/subcommand paths, counts matching test files by sharness prefix, and appends coverage summaries. It also produces a file of matched command lines for diffing.

State and persistence: writes all intermediate files under `/tmp/coverage_helper.<timestamp>.*`; it does not clean the temp directory despite the trailing comment. It requires running from the test tree layout where `sharness/t*-*.sh` exists.

Dependencies and integration points: depends on POSIX shell plus `git`, `egrep`, `sed`, `cut`, `sort`, `uniq`, `expr`, and a built `ipfs` binary in PATH. It integrates with CLI command discovery rather than static command registries.

Risks and test signals: regex filtering can undercount/overcount commands, especially multiline shell, helper aliases, variable-expanded subcommands, or changed sharness paths. Useful as a heuristic coverage report, not a precise test oracle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness_test_coverage_helper.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/unit/Rules.mk -->
## sources/distributed-fs/ipfs-kubo/test/unit/Rules.mk

Purpose: make fragment for unit-test report artifacts.

Important targets and control flow: includes `mk/header.mk`, adds `$(d)/gotest.json` and `$(d)/gotest.junit.xml` to `CLEAN`, defines `$(d)/gotest.junit.xml` as generated from `test/bin/gotestsum` and `$(d)/gotest.json`, then runs `gotestsum --no-color --junitfile $@ --raw-command cat $(@D)/gotest.json`.

State and persistence: consumes JSON test output and writes JUnit XML beside it; both artifacts are cleanable.

Dependencies and integration points: depends on the repository make system, `gotestsum`, and the `test_unit` pipeline that produces `gotest.json`.

Risks and test signals: failures indicate missing `gotestsum`, malformed JSON, or changed make directory variables. The target is a reporting bridge for CI systems expecting JUnit XML.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/unit/Rules.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/thirdparty/unit/unit.go -->
## sources/distributed-fs/ipfs-kubo/thirdparty/unit/unit.go

Purpose: defines binary information-size constants and a string formatter for byte counts.

Important APIs/types/functions: `type Information int64` represents sizes. Constants `KB`, `MB`, `GB`, `TB`, `PB`, and `EB` are powers of 1024 using `iota`. `Information.String` chooses the largest unit whose threshold is strictly less than the value, divides by that unit, and returns an integer string like `12 MB`.

State and persistence: stateless pure formatting code.

Dependencies and integration points: imports only `fmt`; likely used by user-facing size output in older Kubo code.

Risks and test signals: threshold comparisons use `>` rather than `>=`, so exactly `1 KB` formats as `1024 B`, not `1 KB`. The function truncates fractional units. Any callers requiring conventional human-readable output should account for this behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/thirdparty/unit/unit.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/thirdparty/unit/unit_test.go -->
## sources/distributed-fs/ipfs-kubo/thirdparty/unit/unit_test.go

Purpose: verifies the binary size constants in `thirdparty/unit`.

Important APIs/types/functions: `TestByteSizeUnit` asserts `KB` through `EB` equal repeated powers of 1024. It does not test `Information.String`.

State and persistence: no state; pure unit test.

Dependencies and integration points: uses Go `testing` only.

Risks and test signals: catches accidental constant drift but leaves formatter boundary behavior untested, including exact-unit and truncation cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/thirdparty/unit/unit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/thirdparty/verifbs/verifbs.go -->
## sources/distributed-fs/ipfs-kubo/thirdparty/verifbs/verifbs.go

Purpose: wraps Boxo blockstores to enforce CID validation on reads and writes.

Important APIs/types/functions: `VerifBSGC` embeds `bstore.GCBlockstore`; `VerifBS` embeds `bstore.Blockstore`. Both override `Put`, `PutMany`, and `Get`, calling `verifcid.ValidateCid(verifcid.DefaultAllowlist, ...)` before delegating to the embedded store. `PutMany` validates every block before writing any batch.

State and persistence: wrappers do not store state themselves; they guard operations against the underlying persistent blockstore.

Dependencies and integration points: depends on `github.com/ipfs/boxo/blockstore`, `github.com/ipfs/boxo/verifcid`, go-block-format blocks, and go-cid. It integrates with repo/blockservice construction where blockstores should reject insecure CIDs.

Risks and test signals: wrappers only cover `Put`, `PutMany`, and `Get`; other methods inherited from the embedded interfaces may bypass validation if they accept CIDs. The CID security sharness test provides black-box signals for this layer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/thirdparty/verifbs/verifbs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/tracing/doc.go -->
## sources/distributed-fs/ipfs-kubo/tracing/doc.go

Purpose: package-level documentation for Kubo tracing, describing experimental status, OpenTelemetry environment variables, exporter choices, Jaeger example setup, and span naming conventions.

Important content: documents `OTEL_TRACES_EXPORTER` values `otlp`, `zipkin`, and `file`, common OTLP/Zipkin/file env vars, an example Jaeger all-in-one Docker command, and the convention `<Component>.<Span>` with examples like `Gateway.Request`.

State and persistence: documentation only; it describes trace export side effects such as writing JSON traces to `OTEL_EXPORTER_FILE_PATH`.

Dependencies and integration points: links package behavior to OpenTelemetry SDK environment-variable conventions and the global tracer provider.

Risks and test signals: because tracing is marked experimental, docs may drift from actual exporter support in Boxo tracing or OpenTelemetry defaults. No tests are present in this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/tracing/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/tracing/tracing.go -->
## sources/distributed-fs/ipfs-kubo/tracing/tracing.go

Purpose: constructs Kubo's OpenTelemetry tracer provider and provides a helper for consistently named spans.

Important APIs/types/functions: `shutdownTracerProvider` extends `traceapi.TracerProvider` with `Shutdown`. `noopShutdownTracerProvider` wraps a no-op provider when no exporters are configured. `NewTracerProvider` calls Boxo `tracing.NewSpanExporters(ctx)`, adds each exporter as a batcher, merges default resource data with service name `Kubo` and service version from `version.CurrentVersionNumber`, and returns an SDK tracer provider. `Span` starts spans using global tracer name `Kubo` and span name `component.span`.

State and persistence: runtime state is the created tracer provider and exporter pipelines. Exporters may persist or send traces depending on environment configuration.

Dependencies and integration points: depends on Boxo tracing exporter discovery, Kubo version package, OpenTelemetry SDK/resource/semconv, global `otel` tracer registry, and noop provider.

Risks and test signals: errors from exporter construction or resource merging propagate. If no exporters are configured, callers still get a provider with a no-op `Shutdown`, simplifying lifecycle code. Span naming is string-concatenated and can produce odd names if callers pass empty component/span strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/tracing/tracing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/version.go -->
## sources/distributed-fs/ipfs-kubo/version.go

Purpose: centralizes Kubo version, repo version, API version, user-agent construction, implicit fork suffix detection, and version-info reporting.

Important APIs/types/functions: `CurrentCommit`, `taggedRelease`, and `buildOrigin` are ldflag-populated variables. `CurrentVersionNumber` is `0.43.0-dev`; `ApiVersion` is `/kubo/<version>/`; `RepoVersion` is `18`. `GetUserAgentVersion` builds `kubo/<version>[/commit][/suffix]`, omitting commit for tagged releases and cleaning via `cmdutils.CleanAndTrim`. `SetUserAgentSuffix` sets the cleaned suffix. `ImplicitAgentSuffix` prefers `buildOrigin`, then `debug.ReadBuildInfo().Main.Path`, and calls `suffixFromForkPath`. `suffixFromForkPath` strips known public forge hosts and a trailing `kubo` repo name, returning empty for upstream. `GetVersionInfo` reports version, commit, repo version, GOARCH/GOOS, and Go runtime.

State and persistence: package-level mutable variables influence process-wide user-agent output. No disk state is touched.

Dependencies and integration points: used by libp2p identify, HTTP user agent, API versioning, repo migration checks, and tracing resource metadata. Depends on runtime/debug build info and command utility sanitization.

Risks and test signals: mutable global suffix/ldflag variables require tests to restore state. Fork suffix heuristics assume normalized `host/org/repo` paths and may misrepresent unusual remotes. Tagged-release commit omission changes observability but reduces redundant identify bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/version_test.go -->
## sources/distributed-fs/ipfs-kubo/version_test.go

Purpose: unit tests for fork suffix derivation, implicit suffix precedence, and user-agent version formatting.

Important tests and control flow: `TestSuffixFromForkPath` covers empty/upstream paths, known forge forks, renamed repos, unknown hosts, nested paths, leading/trailing slashes, and short inputs. `TestImplicitAgentSuffix_PrefersBuildOrigin` mutates `buildOrigin` and verifies it overrides build info for forks while upstream/empty origin produce no suffix under the test module path. `TestGetUserAgentVersion` saves/restores globals and verifies combinations of commit, tagged release marker, and suffix.

State and persistence: tests mutate package globals (`CurrentCommit`, `taggedRelease`, `userAgentSuffix`, `buildOrigin`) with cleanup restoration.

Dependencies and integration points: uses `testify/assert` and the implementation in `version.go`.

Risks and test signals: strong coverage for expected string formatting and fork heuristics. Does not test `cmdutils.CleanAndTrim` edge inputs directly beyond using `SetUserAgentSuffix`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/cache_eviction.go -->
## sources/distributed-fs/juicefs/pkg/chunk/cache_eviction.go

Purpose: defines disk-cache key indexing and eviction policies for JuiceFS chunk cache.

Important APIs/types/functions: constants define policies `none`, `2-random`, and `lru`. `cacheItem` stores logical size and access time; negative size marks staging blocks. `KeyIndex` abstracts add/remove/get/iteration/reset. `NewKeyIndex` instantiates policy implementations from `Config.CacheEviction`. `noneEviction` is a map with no eviction iterator and protects staging blocks unless removal explicitly passes `staging=true`. `randomEviction` samples pairs from map iteration, preferring expired or older entries. `lruEviction` tracks `cacheKey` to `lruItem` plus a min-heap ordered by access time, then size, then id; staging entries are kept out of the heap.

Control flow and state: `get` updates atime, `reset` returns a snapshot while clearing active state for rescans, and `evictionIter` removes yielded entries from the index as it yields. LRU uses `heap.Fix` on access/update and `heap.Remove` on deletion.

Dependencies and integration points: used by `cacheStore` to track cached and staged blocks, choose removals under capacity/free-space pressure, and preserve atime across scans. Depends on `container/heap`, `time`, and `cacheKey` from disk cache.

Risks and test signals: `EvictionNone.evictionIter` panics by design and must not be called. Staging blocks rely on negative sizes and explicit staging removal, so sign mistakes can leak staged files or evict unuploaded data. `verifyHeap` is available but unused; LRU integrity depends on correct heap position bookkeeping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/cache_eviction.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/cached_store.go -->
## sources/distributed-fs/juicefs/pkg/chunk/cached_store.go

Purpose: implements the public `ChunkStore` over object storage with read cache, disk/memory cache manager, compression, rate limiting, writeback staging, delayed upload, prefetch, singleflight read de-duplication, and Prometheus metrics.

Important APIs/types/functions: `rSlice` maps a slice id/length to object keys and implements `ReadAt`. `wSlice` buffers pages, writes blocks, flushes block uploads, supports `SetWriteback`, `Finish`, and `Abort`. `Config` carries cache directories, sizes, checksum/eviction, upload/download limits, timeouts, writeback/delay/hour policy, block size, readahead, and prefetch settings; `SelfCheck` normalizes invalid combinations. `cachedStore` owns object storage, `CacheManager`, `prefetcher`, `Controller`, semaphores, pending staging queue, compressor, rate-limit buckets, and metrics. Public methods implement `NewReader`, `NewWriter`, `Remove`, `FillCache`, `EvictCache`, `CheckCache`, `UsedMemory`, `UpdateLimit`, and `BlobStorage`.

Control flow: reads first try `bcache.load`; cache misses may do range reads for seekable storage/compression conditions, otherwise use singleflight full-block `load`, optionally caching the block. Writes buffer by block/page; `FlushTo` starts uploads for complete blocks; `Finish` waits for pending upload errors. `upload` compresses and retries object `Put`; synchronous writes may cache blocks locally. Writeback stages small blocks to disk, acknowledges success early, and queues background upload immediately or after delay/hour gates. `scanDelayedStaging` and `uploader` drain persisted staging files.

State and persistence: object data persists in `object.ObjectStorage`. Cache state persists through `CacheManager`, disk raw/staging files, pending maps, and metrics. Writeback staging can survive process restart and is scanned by disk cache. `pendingKeys` protects staged blocks from being uploaded after deletion.

Dependencies and integration points: integrates `compress`, `object.ObjectStorage`, `utils.WithTimeout`, `ratelimit`, Prometheus, `CacheManager`, `Page`, `prefetcher`, and `Controller`. Object request IDs/storage classes feed metrics/logging.

Risks and test signals: complex concurrency around page refcounts, `currentUpload/currentDownload` semaphores, pending upload cancellation, and staging validity. Error paths must release pages exactly once. Writeback can acknowledge data before object-store persistence, so staging durability and forced upload cleanup are critical. Tests cover default/memory/compressed/limited/full/small-buffer stores, async and delayed writeback, force upload, fill/evict/check cache, retry behavior, cache file tier/checksum parsing, and benchmarks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/cached_store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/cached_store_test.go -->
## sources/distributed-fs/juicefs/pkg/chunk/cached_store_test.go

Purpose: unit and integration tests for `cachedStore`, writer/reader behavior, cache modes, writeback, delayed upload, cache fill/evict/check APIs, retry behavior, and cache-file tier/checksum parsing.

Important tests and helpers: `testStore` writes sparse/multi-block data, flushes, reads offsets across blocks, and concurrently writes/removes slices. `defaultConf` defines a temp disk cache baseline. Tests cover default disk cache, memory cache, lz4 compression, upload/download limits, low free-space config, small buffer, async writeback scanning staged files, forced direct upload versus writeback, delayed upload, hash-prefix bucket layout, `FillCache`/`EvictCache`/`CheckCache`, cached/uncached read benchmarks, `load` no-retry behavior on direct object errors, and `openCacheFile` handling of data-only, checksum+tier, invalid size, and invalid tier files.

State and persistence: uses in-memory object storage plus temp disk cache directories. Some tests precreate staging files or remove caches to assert upload/recovery behavior.

Dependencies and integration points: depends on `object.CreateStorage("mem")`, `utils.RandRead`, `testify`, local cache constants, and public `ChunkStore` APIs.

Risks and test signals: strong functional coverage for common cache paths. It relies on sleeps for async flush/scan timing, which can flake under slow CI. It validates recent tier-ID behavior in cache files and protects writeback semantics where cache-only data should fail after staged cache removal but direct-upload data should remain readable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/cached_store_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/chunk.go -->
## sources/distributed-fs/juicefs/pkg/chunk/chunk.go

Purpose: defines the core chunk storage interfaces used by JuiceFS higher layers.

Important APIs/types/functions: `Reader` exposes context-aware `ReadAt(ctx, *Page, off)`. `Writer` embeds `io.WriterAt` and adds `ID`, `SetID`, `SetWriteback`, `FlushTo`, `Finish`, and `Abort`. `ChunkStore` creates readers/writers and exposes removal, cache fill/evict/check, memory usage, runtime limit updates, and underlying blob storage access.

State and persistence: interface only; implementations decide persistence. In this package `cachedStore` is the main implementation.

Dependencies and integration points: imports `context`, `io`, and JuiceFS `object.ObjectStorage`. This is the boundary between file/chunk logic and object-backed storage/cache implementations.

Risks and test signals: callers rely on `Finish(length)` as write completion and on `Abort` cleanup. `CheckCache` uses a callback rather than returning structured results, so callback semantics are part of the contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/chunk.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/disk_cache.go -->
## sources/distributed-fs/juicefs/pkg/chunk/disk_cache.go

Purpose: implements JuiceFS disk cache and cache manager, including raw cache files, staging files for writeback, space/inode pressure cleanup, cache scanning, consistent hashing across cache directories, checksum/tier metadata, and device health integration.

Important APIs/types/functions: `cacheStore` manages one cache directory with capacity, max items, free-ratio policy, key index, pending memory pages, raw/stage fullness flags, checksum mode, uploader callback, active IO tracking, and disk-cache state machine. Key methods include `newCacheStore`, `checkErr`, `flushPage`, `cache`, `load`, `exist`, `stage`, `uploaded`, `cleanupFull`, `uploadStaging`, `scanCached`, and `scanStaging`. `cacheManager` distributes keys across stores via consistent hashing and falls back to legacy hashing for reads. `CacheManager` abstracts cache/stage/load/remove/stats behavior. `cacheFile` wraps an on-disk cache file and validates optional CRC32C checksums plus optional tier ID.

Control flow: new stores create directories/lock files, adjust capacity by free ratio, and start background goroutines for lock checks, pending flush, free-space cleanup, expiry cleanup, scans, staging scans, and IO timeout checks. `cache` queues a `Page` for async disk flush. `flush` writes pending pages to temp files and atomically renames. `stage` writes a staging file, optionally hard-links it into raw cache with negative size, and background upload later calls `uploaded` to make it positive. `cleanupFull` removes entries from the eviction iterator to meet byte/item/free-space targets. `scanCached` rebuilds index state from files; hard-linked stage/raw files are treated as negative staging entries.

State and persistence: raw cache files live under `raw/chunks/...`; writeback files live under `rawstaging/chunks/...`; `.lock` stores a UUID for consistent hashing identity. Files can contain data, checksum trailer, and optional one-byte tier ID. Metrics track writes, evictions, staging counts, and bytes.

Dependencies and integration points: uses filesystem APIs, `fastwalk`, consistent hashing, murmur3/FNV hashing, humanize logging, Prometheus metrics, OS helpers from `utils_*.go`, `Page`, eviction indexes, and disk-cache state from `disk_cache_state.go`.

Risks and test signals: high concurrency and persistence risk: hard links, negative sizes, stale scans, IO timeouts, page refcounts, full-disk cleanup, and checksum-level differences must stay coherent. `checkErr` can transition disks to unstable/down. Tests cover metrics, scanning, checksums, staging metrics, path expansion, cache file format variants, and disk state behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/disk_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/disk_cache_state.go -->
## sources/distributed-fs/juicefs/pkg/chunk/disk_cache_state.go

Purpose: implements a small disk-cache health state machine used by `cacheStore` to degrade or disable a cache directory after IO errors or timeouts.

Important APIs/types/functions: globals configure thresholds such as IO errors to unstable, successes to normal, max duration to down, unstable concurrency limit, tick durations, and probe settings. States implement `dcState`: `normalDC`, `unstableDC`, `downDC`, and `unchangedDC`. `normalDC` counts IO errors and transitions to unstable after the threshold. `unstableDC` counts successes/errors, probes the cache by writing/reading/removing probe pages, limits concurrent operations, returns to normal when enough successes and low error percentage occur, or transitions down after max duration. `downDC` rejects operations with `errCacheDown`. `cacheStore.event` coordinates transitions and stops prior state goroutines. `getEnvs` overrides thresholds from environment variables.

State and persistence: state is in memory per `cacheStore`; probes create and remove files under a `probe` cache path. Environment variables tune process-wide globals.

Dependencies and integration points: `cacheStore.checkErr` calls `beforeCacheOp`, `checkCacheOp`, `afterCacheOp`, `onIOErr`, and `onIOSucc`. `disk_cache.go` removes unavailable stores from `cacheManager`.

Risks and test signals: concurrency limit uses atomic counters and must balance before/after calls. Probe loops can add load to unstable devices. Global env overrides affect all stores in process. Tests exercise state transitions and environment-dependent behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/disk_cache_state.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/disk_cache_state_test.go -->
## sources/distributed-fs/juicefs/pkg/chunk/disk_cache_state_test.go

Purpose: tests disk cache health-state transitions for different numbers of cache directories.

Important tests and control flow: helper `setState` swaps a `cacheStore` into a requested `dcState`. `testDiskCacheState` creates a cache manager, manipulates stores through normal/unstable/down states, triggers events and IO outcomes, and verifies manager length/removal behavior. `TestDiskCacheState` runs the helper for multiple cache counts.

State and persistence: uses temp cache directories and live `cacheStore` goroutines. State changes are in-memory but affect cache manager store maps and consistent hash membership.

Dependencies and integration points: depends on `newCacheManager`, `dcState` implementations, and testing assertions.

Risks and test signals: protects the degraded-disk removal path. Because production code has background goroutines and timers, tests may require careful sleeps or direct state injection to avoid flakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/disk_cache_state_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/disk_cache_test.go -->
## sources/distributed-fs/juicefs/pkg/chunk/disk_cache_test.go

Purpose: tests disk cache store creation, metrics, scanning, checksum validation, staging accounting, path expansion, and platform-sensitive cache behavior.

Important tests and helpers: `toFloat64` reads Prometheus collectors. `testConf` creates unique temp cache dirs. Tests instantiate cache stores/managers, write cache pages, inspect metrics counters/gauges, stage and remove staging files, scan raw cache directories, validate checksum modes and corrupted data behavior, and exercise cache manager path/glob handling. Mocking libraries are imported for targeted filesystem/metric scenarios.

State and persistence: creates real temporary cache directory structures under raw/staging paths and writes cache files with optional checksums.

Dependencies and integration points: depends on Prometheus metric internals, `fastwalk`/filesystem layout, `utils.RandRead`, `testify/require`, GoConvey, and Mockey.

Risks and test signals: robust for disk-format regressions, but async cache flushes use sleeps. Tests involving corruption/checksum mode are important because disk cache correctness is otherwise silent until bad data is returned.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/disk_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/mem_cache.go -->
## sources/distributed-fs/juicefs/pkg/chunk/mem_cache.go

Purpose: in-memory implementation of `CacheManager` behavior for disabled/memory cache modes and disk-cache fallback.

Important APIs/types/functions: `memItem` stores access time and `*Page`. `memcache` tracks capacity, max items, used bytes, map entries, eviction policy, expiry, and metrics. Methods implement cache/store contract: `cache`, `remove`, `load`, `exist`, `stats`, `usedMemory`, `cleanup`, `cleanupExpire`, and no-op/unsupported staging methods.

Control flow and state: `cache` acquires page references, records metrics, and evicts using two-random sampling if full and eviction is enabled. `load` and `exist` refresh access time. A finalizer releases all retained pages if the memcache is collected. Expiry cleanup periodically removes old entries.

Dependencies and integration points: used by `newCacheManager` when `CacheDir == "memory"`, cache size is disabled, no cache dirs exist, or disk cache becomes empty. Integrates with `Page` refcounting and cache metrics.

Risks and test signals: staging/writeback is unsupported in memory cache mode, so config must disable writeback before selecting it. Refcount leaks are possible if entries are not released on eviction/removal. Eviction is approximate and map-order dependent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/mem_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/metrics.go -->
## sources/distributed-fs/juicefs/pkg/chunk/metrics.go

Purpose: declares and registers Prometheus metrics for cache manager operations.

Important APIs/types/functions: `cacheManagerMetrics` contains counters for cache drops/writes/evicts/write bytes/stage write bytes, a histogram for cache write latency, and gauges for staged blocks and staged bytes. `newCacheManagerMetrics` initializes and registers metrics. `registerMetrics` also adds a gauge function `staging_writing_blocks` backed by global `stagingBlocks`.

State and persistence: metrics are process-local Prometheus collectors; no disk persistence.

Dependencies and integration points: used by disk and memory cache implementations and registered into the supplied Prometheus registerer from `NewCachedStore`.

Risks and test signals: repeated registration into the same registry can panic through `MustRegister`. Tests read collectors directly to validate stage/cache counters. Metric names are user-facing operational contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/page.go -->
## sources/distributed-fs/juicefs/pkg/chunk/page.go

Purpose: provides a refcounted byte buffer abstraction used throughout chunk cache read/write paths, including off-heap allocation and dependent slices.

Important APIs/types/functions: `Page` stores `refs`, `offheap`, optional dependency, `Data`, and optional debug stack. `NewPage` wraps existing data. `NewOffPage` allocates off-heap memory with `utils.Alloc`, sets a finalizer that logs leaked refcounts, and optionally captures stacks via `JFS_PAGE_STACK`. `Slice` creates a dependent `Page` sharing a subslice and retaining the parent. `Acquire` and `Release` adjust refcounts; release frees off-heap data and releases dependencies when count reaches zero. `pageReader` implements `Read`, `ReadAt`, and `Close` over a retained page.

State and persistence: in-memory/off-heap only. Page lifetime is explicit and refcounted.

Dependencies and integration points: central to `cachedStore`, disk/memory cache, singleflight, and tests. Depends on JuiceFS `utils.Alloc/Free`.

Risks and test signals: double release, missing release, or shared-slice misuse can corrupt reads or leak off-heap memory. Finalizer logging helps diagnose but is not deterministic. Tests cover page slicing and reader behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/page.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/page_test.go -->
## sources/distributed-fs/juicefs/pkg/chunk/page_test.go

Purpose: verifies `Page` refcount/slice behavior and `pageReader` read semantics.

Important tests: `TestPage` exercises `NewOffPage`, slicing, acquire/release interactions, and data availability through dependent pages. `TestPageReader` checks sequential `Read`, random `ReadAt`, EOF behavior, and close/released-page error handling.

State and persistence: in-memory only.

Dependencies and integration points: uses Go testing and `Page` APIs used by cache code.

Risks and test signals: catches basic lifetime and reader contract regressions, but cannot prove absence of all refcount leaks in concurrent cache paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/page_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/prefetch.go -->
## sources/distributed-fs/juicefs/pkg/chunk/prefetch.go

Purpose: small concurrent prefetch scheduler for cache reads.

Important APIs/types/functions: `prefetcher` tracks a bounded `pending` channel, a `busy` map to deduplicate keys, and an `op` callback. `newPrefetcher` starts `parallel` workers and sizes the queue to `max(parallel*4, 10)`. `fetch` enqueues a key if it is not already busy and drops it if the queue is full. Workers call `op` and clear the busy marker.

State and persistence: in-memory queue and busy map only.

Dependencies and integration points: used by `cachedStore.loadRange` to trigger full-block cache fill after range reads. The callback in `NewCachedStore` uses singleflight and cache insertion.

Risks and test signals: enqueue drops are silent by design. If `op` blocks, busy keys remain blocked until completion. Tests cover deduplication and bounded parallel execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/prefetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/prefetch_test.go -->
## sources/distributed-fs/juicefs/pkg/chunk/prefetch_test.go

Purpose: tests the prefetch scheduler's deduplication and execution behavior.

Important tests: `TestPrefetcher` constructs a prefetcher with a callback that records fetched keys, enqueues repeated and distinct keys, waits for worker processing, and asserts expected fetch counts/order properties.

State and persistence: in-memory synchronization only.

Dependencies and integration points: uses Go testing, sleeps/channels, and `prefetcher.fetch`.

Risks and test signals: protects against duplicate concurrent prefetches and dropped worker execution. Timing-based assertions can be sensitive to scheduler delays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/prefetch_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/singleflight.go -->
## sources/distributed-fs/juicefs/pkg/chunk/singleflight.go

Purpose: custom singleflight controller for coalescing concurrent full-block loads while preserving `Page` reference counts.

Important APIs/types/functions: `request` holds a waitgroup, resulting `*Page`, duplicate count, and error. `Controller` maps keys to active requests. `Execute` waits on existing requests or registers a new one, runs `fn`, acquires the returned page once for every duplicate waiter, deletes the request, and releases waiters. `TryPiggyback` waits only if a request already exists, otherwise returns nil.

State and persistence: in-memory active-request map only.

Dependencies and integration points: used in `cachedStore.ReadAt`, `loadRange`, and prefetch to deduplicate object-store reads and let range reads piggyback on full reads.

Risks and test signals: assumes `fn` returns a non-nil page even on errors before duplicate acquisition; nil pages with duplicates could panic. Correct page refcounts are critical because all waiters release returned pages. Tests exercise concurrent Execute and piggyback semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/singleflight.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/singleflight_test.go -->
## sources/distributed-fs/juicefs/pkg/chunk/singleflight_test.go

Purpose: verifies `Controller` coalesces concurrent calls and shares returned pages safely.

Important tests: `TestSingleFlight` starts concurrent `Execute`/`TryPiggyback` calls for the same key, checks the underlying function runs once for duplicates, validates returned page data/errors, and exercises non-piggyback behavior when no request is active.

State and persistence: in-memory goroutines, counters, and pages.

Dependencies and integration points: uses Go testing and `Page` reference release semantics.

Risks and test signals: protects the read de-duplication path used by cache misses. Does not cover nil-page error edge cases explicitly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/singleflight_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/utils_darwin.go -->
## sources/distributed-fs/juicefs/pkg/chunk/utils_darwin.go

Purpose: Darwin-specific helpers for cache file metadata and OS cache handling.

Important APIs/types/functions: `getAtime` extracts access time from `syscall.Stat_t.Atimespec`. `dropOSCache` is a no-op on Darwin.

State and persistence: reads file metadata only; does not mutate state.

Dependencies and integration points: used by disk-cache scans to preserve access time and by read/write paths when `OSCache` is disabled.

Risks and test signals: Darwin atime availability depends on filesystem mount behavior. No-op cache dropping means disabling OS cache has no effect on Darwin through this helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/utils_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/utils_linux.go -->
## sources/distributed-fs/juicefs/pkg/chunk/utils_linux.go

Purpose: Linux-specific helpers for atime extraction and kernel page-cache dropping.

Important APIs/types/functions: `getAtime` reads `syscall.Stat_t.Atim`. `dropOSCache` calls `unix.Fadvise` with `FADV_DONTNEED` when passed an `*os.File`, logging warnings on failure.

State and persistence: reads metadata and asks the kernel to drop cached pages for a file descriptor; no file contents are changed.

Dependencies and integration points: used by disk-cache scans and by cache/object reads when JuiceFS config disables OS cache.

Risks and test signals: `dropOSCache` only works for readers that are `*os.File`; other `ReadCloser` implementations are ignored. Fadvise behavior is advisory and platform/kernel dependent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/utils_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/utils_unix.go -->
## sources/distributed-fs/juicefs/pkg/chunk/utils_unix.go

Purpose: Unix shared filesystem helpers for disk cache metadata, permissions, and root-volume detection.

Important APIs/types/functions: `getNlink` extracts hard-link count from `syscall.Stat_t.Nlink`. `getDiskUsage` wraps `syscall.Statfs` and returns blocks/free blocks/files/free files. `changeMode` recursively chmods a directory tree when mode differs, logging errors. `inRootVolume` compares device IDs of a dir and `/` to determine whether the cache is on the root volume.

State and persistence: reads filesystem stats and may mutate permissions through chmod.

Dependencies and integration points: used by disk-cache scanning to identify hard-linked staging files, free-space checks, directory creation permission correction, and conservative root-volume free-ratio adjustment.

Risks and test signals: recursive chmod can be expensive on large cache trees. Device comparison can fail on unusual filesystems. Tests cover `inRootVolume`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/utils_unix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/utils_unix_test.go -->
## sources/distributed-fs/juicefs/pkg/chunk/utils_unix_test.go

Purpose: tests Unix root-volume detection helper.

Important tests: `TestInRootVolume` checks expected behavior for temporary/current/root-like paths by calling `inRootVolume`.

State and persistence: no persistent mutation; reads filesystem metadata.

Dependencies and integration points: depends on local filesystem device layout, so expectations may vary in containers or unusual mount configurations.

Risks and test signals: useful for cache free-ratio safety logic but potentially environment-sensitive if test assumptions about mounts do not hold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/utils_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/utils_windows.go -->
## sources/distributed-fs/juicefs/pkg/chunk/utils_windows.go

Purpose: Windows-specific cache filesystem helpers.

Important APIs/types/functions: `getAtime` returns `fi.ModTime()` instead of true access time. `dropOSCache` is a no-op. `getNlink` returns 0. `getDiskUsage` calls `windows.GetDiskFreeSpaceEx` and reports total/free bytes with inode counts as zero. `changeMode` is a no-op. `inRootVolume` returns false.

State and persistence: reads disk free-space data only.

Dependencies and integration points: used by the same disk-cache code paths as Unix helpers while acknowledging Windows lacks or does not use inode/link/permission behavior here.

Risks and test signals: hard-link/staging detection and atime eviction are less precise on Windows. Free-space logic ignores inode pressure. No OS-cache drop support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/chunk/utils_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/backup.go -->
## sources/distributed-fs/juicefs/pkg/meta/backup.go

Purpose: defines JuiceFS metadata backup serialization primitives and options for dump/load workflows.

Important APIs/types/functions: constants define backup magic/version/EOS and segment type IDs. `SegType2Name` maps segment IDs to names. `getMessageFromType` and `createMessageByName` instantiate protobuf messages. `BakFormat` tracks current write position and footer; `writeSegment` serializes a `BakSegment`, records footer offsets/counts, and advances position; `ReadSegment`, `writeFooter`, `writeEOS`, and `ReadFooter` handle stream boundaries and footer access. `BakFooter.Marshal/Unmarshal` writes/reads protobuf footer plus trailing 8-byte length. `BakSegment` stores type, length, and protobuf value; `newBakSegment` infers segment type from `pb.Format` or populated `pb.Batch` field; `num` counts records; `Marshal` writes type/length/data; `Unmarshal` reads them and returns `errBakEOF` on EOS. `DumpOption` and `LoadOption` normalize thread counts; `dumpFormat` writes sanitized or secret-preserving format JSON; `dumpResult` sends results with context cancellation.

Control flow and state: backup files are `BakSegment... + BakEOS + BakFooter`. Footer infos accumulate offsets and counts by segment name for later indexed reading/validation. Segment payloads are protobuf; format payload embeds JSON bytes of filesystem format.

Dependencies and integration points: depends on JuiceFS metadata protobufs, `protojson`, global protobuf registry, binary big-endian encoding, `baseMeta.GetFormat`, and context-aware dump pipelines. Transaction marker key types are declared for later context use.

Risks and test signals: `io.Reader.Read` is used once for segment/footer payloads and may under-read on non-buffered readers; robust callers may need `io.ReadFull`. Error checks on writes use `err != nil && n != expected`, which can miss short writes with nil error. Segment type inference assumes exactly one populated `pb.Batch` field. Secret stripping in `dumpFormat` is critical for safe backups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/juicefs/pkg/meta/backup.go -->
