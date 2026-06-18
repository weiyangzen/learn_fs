# Group Research: subset-b-007606

This grouped report covers Kubo sharness integration tests under `sources/distributed-fs/ipfs-kubo/test/sharness`. Each section is source-tree aligned and wrapped for deterministic splitting into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0062-daemon-api.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0062-daemon-api.sh

Purpose: validates daemon API discovery through `$IPFS_PATH/api`, including the CLI behavior when the daemon is online, offline, and when an API file points at an unusable address.

Important APIs and helpers: sources `lib/test-lib.sh`, uses `test_init_ipfs`, `test_launch_ipfs_daemon`, `test_kill_ipfs_daemon`, `test_check_peerid`, `test_cmp`, and local helpers `test_client`, `test_client_must_fail`, and `test_client_suite`. The main command surface is `ipfs id -f=<id>`, `ipfs config Identity.PeerID`, and the daemon-created `api` file.

Control flow and state: initializes a repo, records the configured peer ID as the expected API identity, runs client checks through the live daemon, kills the daemon, writes a fake API multiaddr into the persisted repo `api` file, and verifies commands fail with a targeted API connection error. It then restarts the daemon and asserts that startup recreates or updates the API file.

Dependencies and integration points: covers CLI-to-daemon HTTP API routing, repo path discovery, API multiaddr persistence, and daemon lifecycle helpers. The test relies on exact error text for the standalone-vs-daemon hint.

Risks and test signals: catches regressions where Kubo silently ignores stale API files, reports confusing client errors, uses the wrong daemon identity, or fails to create `$IPFS_PATH/api`. A pass signal is peer ID equality plus expected failure diagnostics when the API endpoint is invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0062-daemon-api.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0063-daemon-init.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0063-daemon-init.sh

Purpose: verifies that `ipfs daemon --init` can bootstrap a missing or empty repository and then run a daemon that can be shut down cleanly.

Important APIs and helpers: sources `lib/test-lib.sh`, defines `test_ipfs_daemon_init`, and uses `test_launch_ipfs_daemon --init --offline`, `test_kill_ipfs_daemon`, and direct filesystem resets of `$IPFS_PATH`.

Control flow and state: the helper starts a daemon with `--init --offline`, then kills it. It is invoked after removing `$IPFS_PATH` entirely and again after recreating an empty `$IPFS_PATH` directory. The core persistent state is repo initialization data written under `$IPFS_PATH`.

Dependencies and integration points: exercises daemon initialization code, repo creation, offline daemon start, lock acquisition, and shutdown paths from sharness helpers.

Risks and test signals: protects against regressions where `--init` only works for nonexistent paths but not empty directories, or where repo creation succeeds but daemon shutdown leaves stale state. A pass is a daemon that starts and stops in both filesystem states without explicit `ipfs init`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0063-daemon-init.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0064-api-file.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0064-api-file.sh

Purpose: checks how commands classify local-only, offline-capable, and daemon-required operations when the repo API file is absent, stale, present, or produced from wildcard API listen config.

Important APIs and helpers: uses `ipfs version`, `ipfs swarm peers`, `ipfs pin ls`, `ipfs id`, `ipfs config Addresses.API`, `test_init_ipfs`, daemon launch/kill helpers, `test_must_fail`, and `test_cmp`.

Control flow and state: starts from an initialized offline repo with no daemon, verifies daemon-required commands fail when no API is available, writes `$API_MADDR` manually to `$IPFS_PATH/api`, then verifies commands that can run locally still work while daemon-required ones fail. After launching the daemon it checks that all selected commands work, removes the API file again, and verifies fallback behavior. The final case configures `Addresses.API` on `0.0.0.0` and asserts the emitted API file is normalized to `127.0.0.1`.

Dependencies and integration points: covers command request routing, repo-local command execution, daemon endpoint discovery, API multiaddr serialization, and wildcard address rewriting.

Risks and test signals: catches accidental daemon dependency for offline commands, stale API endpoint misuse, and unsafe API file exposure on unspecified addresses. Exact pass signals are command exit codes and the normalized API file content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0064-api-file.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0065-active-requests.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0065-active-requests.sh

Purpose: validates `ipfs diag cmds` reporting for active and inactive daemon API requests.

Important APIs and helpers: uses `test_init_ipfs`, daemon launch/kill helpers, `ipfs diag cmds`, `ipfs log tail`, `go-sleep`, `grep`, and shell process management via background PID, `kill`, and `wait`.

Control flow and state: starts a daemon, captures `diag cmds` output for a normal command, starts long-running `ipfs log tail` in the background, and checks that `diag cmds` reports `log/tail` as active. It then kills the log tail process, waits briefly, and checks the same command is retained as inactive.

Dependencies and integration points: exercises command instrumentation in the daemon, request lifecycle tracking, and the log streaming endpoint. The persisted repo state is minimal; the important state is daemon in-memory active request tracking.

Risks and test signals: catches leaks or incorrect active flags in diagnostic state, especially for streaming endpoints that are easy to leave open. Passing output contains `diag/cmds`, `log/tail`, `true` while active, and `false` after termination.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0065-active-requests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0066-migration.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0066-migration.sh

Purpose: tests repo migration prompting, explicit migration flags, `ipfs repo migrate`, and failure behavior when migration is blocked by a repo lock.

Important APIs and helpers: defines `gen_mock_migrations` to synthesize `fs-repo-<n>-to-<n+1>` executables, `check_migration_output` to assert ordered migration messages, and uses `IPFS_REPO_VER`, `$IPFS_PATH/version`, `ipfs daemon --migrate=false/true`, `ipfs repo migrate`, and daemon launch/kill helpers.

Control flow and state: creates mock migration binaries on `PATH`, downgrades the repo version file, checks that `--migrate=false` fails with a requires-migration diagnostic, checks `--migrate=true` runs migrations and starts far enough to shut down, checks interactive daemon startup can auto-migrate, runs `ipfs repo migrate` directly, verifies no-op behavior when already current, then holds a daemon lock and confirms `repo migrate` fails with `repo.lock`.

Dependencies and integration points: covers fs-repo versioning, external migration binary discovery, daemon startup migration gating, direct migration command behavior, repo lock enforcement, and migration output compatibility including hybrid migration messages.

Risks and test signals: protects against accidental automatic upgrades when disabled, bad migration ordering, poor user diagnostics, and unsafe migration under lock. Signals are expected exit codes, version-file transitions, and exact migration or lock text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0066-migration.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0067-unix-api.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0067-unix-api.sh

Purpose: verifies that Kubo can expose and consume the HTTP API over a Unix domain socket.

Important APIs and helpers: uses `ipfs config Addresses.API`, `ipfs --api=/unix/... id -f=<id>`, `test_init_ipfs`, daemon launch/kill helpers, and `test_cmp`.

Control flow and state: initializes a repo, records the local peer ID, configures the daemon API address to a socket under a test directory, launches the daemon, and performs an explicit `--api` client call through the Unix socket.

Dependencies and integration points: covers multiaddr support for `/unix` API endpoints, daemon listener binding, client transport selection, and peer identity retrieval over the daemon API.

Risks and test signals: catches regressions in Unix socket path handling, endpoint serialization, or client API dialing. The test signal is equality between the configured peer ID and `ipfs id` fetched through the socket endpoint.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0067-unix-api.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0070-user-config.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0070-user-config.sh

Purpose: ensures `ipfs init` bootstrap defaults do not overwrite user-provided top-level config keys.

Important APIs and helpers: uses `test_init_ipfs`, `ipfs config Datastore.StorageMax`, `ipfs init`, and `test_cmp`.

Control flow and state: initializes a repo, sets `Datastore.StorageMax` to `42GB`, re-runs `ipfs init`, and confirms the setting remains `42GB`. The persistent state under test is the repo config JSON.

Dependencies and integration points: covers config bootstrap behavior, idempotent init, and preservation of user-edited top-level configuration.

Risks and test signals: catches accidental reapplication of defaults over existing config, which could corrupt storage limits or other user intent. The pass signal is exact equality between the configured value after reinit and the expected user value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0070-user-config.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0080-repo.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0080-repo.sh

Purpose: broad integration coverage for repo garbage collection, pin commands, refs traversal, repo stats, and repo version reporting.

Important APIs and helpers: uses `ipfs repo gc`, `ipfs add`, `ipfs pin add/rm/ls`, `ipfs refs`, `ipfs refs local`, `ipfs repo stat`, `ipfs repo version`, `random-data`, `test_cmp`, and helper `get_field_num` for parsing stat values.

Control flow and state: adds files and random multiblock data, observes automatic recursive pins, removes pins, confirms GC removes only unpinned blocks, checks `--silent`, direct vs recursive pin conflicts, indirect pin listing, refs uniqueness and recursion behavior, and repo stats before and after adding data. It also removes `Datastore.StorageMax` from config and ensures stat still works.

Dependencies and integration points: covers blockstore persistence, pinset state, DAG traversal, local refs index, storage accounting, config-backed storage limit display, and repo version metadata.

Risks and test signals: protects against data loss from GC, inaccurate pin classification, duplicate or missing refs, and unstable stat output. Test signals include exact pin output, content retrievability, absence from `refs local` after GC, increasing repo size, expected human-readable stats fields, and version text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0080-repo.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0081-repo-pinning.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0081-repo-pinning.sh

Purpose: focuses on recursive, direct, indirect, and no-pin behavior across nested UnixFS directories and GC.

Important APIs and helpers: defines `test_pin_flag` and `test_pin`, uses `ipfs add -r`, `ipfs cat`, `ipfs dag get`, `ipfs pin ls/add/rm`, `ipfs repo gc`, `jq`, and daemon lifecycle helpers.

Control flow and state: builds a nested directory tree, records file and directory CIDs, verifies recursive root pin and indirect child pins, runs GC and confirms all reachable data remains, removes recursive pins, adds a mix of direct and recursive pins, then verifies GC removes unprotected subtrees while preserving directly or indirectly protected blocks. It also verifies failed recursive pinning does not remove existing direct pins and checks `--pin=false` for files and dirs.

Dependencies and integration points: covers pinset invariants, DAG link reachability, GC mark/sweep behavior, UnixFS DAG structure through `dag get`, and error handling for missing blocks.

Risks and test signals: catches pin classification bugs and dangerous rollback behavior after failed pin attempts. Signals are pin list content, cat/ls success or failure after GC, and expected no-pin absence from pin sets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0081-repo-pinning.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0082-repo-gc-auto.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0082-repo-gc-auto.sh

Purpose: stress-tests automatic garbage collection triggered by datastore storage limits and GC watermarks.

Important APIs and helpers: defines `check_ipfs_storage` and `test_gc`, uses `random-data`, `test_config_set Datastore.StorageMax`, `Datastore.StorageGCWatermark`, `Datastore.GCPeriod`, `disk_usage`, `ipfs add`, `ipfs pin rm`, and daemon lifecycle helpers.

Control flow and state: generates fixed-size data, configures a small `StorageMax` and aggressive GC period, adds and unpins data below and above the watermark, waits for periodic GC, and repeats the GC scenario multiple times to surface timing failures. Storage state is the blockstore size under `$IPFS_PATH/blocks`.

Dependencies and integration points: covers daemon background GC scheduling, datastore accounting, pin removal, blockstore cleanup, and platform-specific disk usage tolerances.

Risks and test signals: catches auto-GC that never fires, fires too early, or leaves storage above watermark. The pass signal is disk usage below expected thresholds after unpinned data crosses configured limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0082-repo-gc-auto.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0084-repo-read-rehash.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0084-repo-read-rehash.sh

Purpose: verifies repository read-time hash validation and `repo verify` reporting when block files are swapped or corrupted.

Important APIs and helpers: defines `test_check_bad_blocks`, uses `ipfs add --raw-leaves`, `ipfs cat`, `ipfs repo verify`, `cid-fmt`, `grep`, and daemon lifecycle helpers.

Control flow and state: creates content with multiple blocks, swaps or tampers with block files in the flatfs blockstore, confirms `ipfs cat` fails on modified data, confirms `repo verify` reports the bad multihash, then adds and reads a fresh raw-leaf block as a sanity check.

Dependencies and integration points: covers blockstore path layout, CID/multihash validation, UnixFS read path, and verify output normalization through `cid-fmt`.

Risks and test signals: catches unsafe reads that trust filenames over block bytes and verify output that omits corrupted blocks. Passing requires read failure for tampered content and matching multihash in `repo verify` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0084-repo-read-rehash.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0086-repo-verify.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0086-repo-verify.sh

Purpose: tests `ipfs repo verify` on deterministic and random block corruption.

Important APIs and helpers: defines `sort_rand` and `check_random_corruption`, uses `random-files`, `ipfs add -r`, direct file corruption in `.ipfs/blocks`, `ipfs repo verify`, and backup/restore shell operations.

Control flow and state: corrupts a selected block file, asserts verify exits nonzero, restores the block, and asserts verify succeeds. It then generates a larger random directory, adds it recursively, and repeats random corruption checks to broaden block coverage.

Dependencies and integration points: covers flatfs storage layout, recursive add block generation, repo verification traversal, and failure exit codes.

Risks and test signals: catches verify false negatives, false positives after restore, and traversal gaps over larger DAGs. The key signals are nonzero status for corrupted blocks and zero status after restoring original bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0086-repo-verify.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0087-repo-robust-gc.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0087-repo-robust-gc.sh

Purpose: validates that `ipfs repo gc` handles missing, unreadable, and corrupted blocks without deleting protected data incorrectly.

Important APIs and helpers: defines `to_raw_cid`, `test_gc_robust_part1`, and `test_gc_robust_part2`; uses `random-data`, `ipfs add`, `ipfs refs -r`, `ipfs cat`, `ipfs pin rm`, `ipfs block rm`, `repo gc --stream-errors`, `cid-fmt`, `dd`, `chmod`, and direct block file lookup.

Control flow and state: creates multiblock data, maps root and leaf CIDs to block files, deletes one leaf, checks reads fail but GC still completes when safe, corrupts a protected root and requires GC to abort without sweeping, tests permission-denied block deletion, then repeats with multiple missing/corrupt blocks and `--stream-errors` to ensure separate errors are reported.

Dependencies and integration points: covers GC error aggregation, mark phase failure safety, block removal permissions, raw CID formatting, and blockstore integrity checks.

Risks and test signals: prevents GC from turning read corruption into data loss. Passing signals include aborted GC on corrupt pinned roots, preserved accessible leaves, partial cleanup only after unpin, and streamed error diagnostics for multiple failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0087-repo-robust-gc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0088-repo-stat-symlink.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0088-repo-stat-symlink.sh

Purpose: verifies `ipfs repo stat` works when `.ipfs` is a symlink.

Important APIs and helpers: uses `ln -s`, `ipfs init`, `ipfs repo stat`, `awk`, and numeric comparison on `RepoSize`.

Control flow and state: creates a symlink target, links `.ipfs` to it, initializes the repo through the symlink, and parses `RepoSize` from `repo stat` to verify it is greater than zero.

Dependencies and integration points: covers repo path resolution, filesystem symlink handling, repo initialization, and stat size calculation.

Risks and test signals: catches code that resolves or walks repo paths incorrectly when the configured path is symlinked. The pass signal is a successful stat with positive `RepoSize`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0088-repo-stat-symlink.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0090-get.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0090-get.sh

Purpose: tests `ipfs get` output layout, archive modes, path validation, output file behavior, and error handling.

Important APIs and helpers: defines `test_ipfs_get_flag`, `test_get_cmd`, and `test_get_fail`; uses `ipfs get`, `ipfs add`, `ipfs dag put`, `tar`, `curl`, `test_cmp`, and daemon lifecycle helpers.

Control flow and state: verifies help output, gets single files and directories by CID, compares materialized output with original data, checks archive output for tar, gzip, and compression flags, rejects invalid paths such as `../..`, writes to explicit `-o` outputs for small and medium files, creates a malformed DAG object to test bad object retrieval behavior, and checks empty requests fail rather than panic.

Dependencies and integration points: covers UnixFS exporter, path validation, archive creation, raw leaves, DAG decoding, CLI stdout/stderr messages, and daemon-backed gateway/API behavior when running online.

Risks and test signals: catches unsafe path traversal, archive naming regressions, corrupted object panics, and wrong materialized filenames. Signals are exact save messages, byte-for-byte file comparisons, tar extraction success, and expected nonzero failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0090-get.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0095-refs.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0095-refs.sh

Purpose: validates `ipfs refs` traversal ordering, recursion depth, uniqueness, edge formatting, and base conversion over a directory DAG with repeated subtrees.

Important APIs and helpers: defines `test_refs_output`, uses `ipfs add -r -Q`, `ipfs refs`, `test_cmp`, optional filtering/sorting, and daemon lifecycle helpers.

Control flow and state: builds a directory tree with repeated names and content, adds it recursively, records the root, and compares `ipfs refs` output under combinations of recursive traversal, `--unique`, `--edges`, `--max-depth`, and CID base options. It checks both offline and daemon-backed execution.

Dependencies and integration points: covers DAG traversal, UnixFS directory links, recursive ref emission, duplicate suppression, depth limiting, edge output formatting, and CID formatting.

Risks and test signals: catches nondeterministic refs output, broken depth handling, duplicate filtering mistakes, and edge-format regressions. Passing requires exact expected ref lists for each option set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0095-refs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0101-iptb-name.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0101-iptb-name.sh

Purpose: verifies multi-node IPNS publishing and recursive IPNS resolution across an IPTB cluster.

Important APIs and helpers: uses `iptb testbed create`, `ipfsi <node> add`, `ipfsi <node> name publish`, `iptb attr get id`, `ipfsi cat`, `test_cmp`, and `iptb stop`.

Control flow and state: creates a three-node localipfs testbed, adds a file on node 1, publishes it under node 1's IPNS name, publishes a second IPNS entry on node 2 that points to node 1's name, then cats the node 2 name from node 3 and compares content.

Dependencies and integration points: covers IPTB orchestration, multi-node routing, IPNS record publication, recursive name resolution, and cross-node content retrieval.

Risks and test signals: catches failures in namesys recursion, provider discovery, or multi-node IPNS propagation. The pass signal is node 3 retrieving exactly the file initially added by node 1 through a chained `/ipns/` reference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0101-iptb-name.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0109-gateway-web-_redirects.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0109-gateway-web-_redirects.sh

Purpose: end-to-end coverage for HTTP gateway `_redirects` files, including redirects, rewrites, custom errors, validation failures, DNSLink, and origin-isolation boundaries.

Important APIs and helpers: uses `ipfs dag import --pin-roots` with fixture CARs, `curl -sD - --resolve`, gateway hostnames, `IPFS_NS_MAP`, `ipfs resolve`, `Gateway.NoDNSLink`, and daemon launch/kill helpers.

Control flow and state: imports multiple fixture directories, requests subdomain gateway URLs whose content roots include `_redirects`, and checks default 301 redirects, explicit 301/302, 200 rewrites, placeholder and splat expansion, custom 404/410/451 responses, catch-all behavior, CRLF parsing, accepted and rejected status codes, invalid file diagnostics, and too-large file rejection. It also verifies path gateway requests do not apply custom `_redirects` without origin isolation, and tests DNSLink-enabled vs DNSLink-disabled hosts.

Dependencies and integration points: covers Boxo gateway web routing, `_redirects` parser limits, subdomain origin isolation, DNSLink resolution, public gateway config, and HTTP status/header semantics.

Risks and test signals: catches security-sensitive redirect leakage across origins, bad parser acceptance, incorrect status codes, and DNSLink policy regressions. Signals are HTTP status lines, `Location` headers, response bodies, and absence of redirects when disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0109-gateway-web-_redirects.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0112-gateway-cors.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0112-gateway-cors.sh

Purpose: tests gateway CORS defaults and custom `Gateway.HTTPHeaders` behavior for GET and OPTIONS requests.

Important APIs and helpers: uses `ipfs config Gateway.HTTPHeaders`, `curl -X GET/OPTIONS`, `test_should_contain`, daemon launch/kill helpers, and fixture content served through the gateway.

Control flow and state: confirms the default `Gateway.HTTPHeaders` config is empty while implicit CORS headers are supplied by the gateway stack, performs GET and OPTIONS against gateway resources and subdomain redirects, then configures custom headers. It verifies configured `Access-Control-Allow-Headers` extends the implicit list and configured `Access-Control-Allow-Origin` replaces the implicit origin list.

Dependencies and integration points: covers gateway header injection, preflight handling, subdomain redirect CORS behavior, and config reload after daemon restart.

Risks and test signals: catches accidental removal of implicit browser CORS support, duplicate or overwritten custom headers, and OPTIONS behavior changes. Passing is based on expected CORS headers in captured HTTP responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0112-gateway-cors.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0114-gateway-subdomains.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0114-gateway-subdomains.sh

Purpose: comprehensive gateway subdomain support test for localhost defaults, custom public gateways, IPFS/IPNS subdomain routing, DNSLink inlining, proxy headers, wildcard gateway config, and path whitelist enforcement.

Important APIs and helpers: defines `test_localhost_gateway_response_should_contain` to test direct HTTP plus proxy, proxy1.0, and CONNECT modes, and `test_hostname_gateway_response_should_contain` for Host-header routing. It uses fixture CAR import, `ipfs routing put --allow-offline` for IPNS records, `Gateway.PublicGateways`, `Gateway.NoDNSLink`, `IPFS_NS_MAP`, `curl`, and daemon restarts.

Control flow and state: starts with empty public gateway config and validates implicit localhost subdomain redirects from `/ipfs` and `/ipns`, CIDv0-to-CIDv1 conversion, payload serving from `{cid}.ipfs.localhost`, directory-listing links, and IPNS key forms. It then enables DNSLink inlining, configures `example.com` with subdomains, checks redirects, invalid CID errors, `X-Forwarded-Proto`, protocol-handler `uri=` redirects, directory breadcrumb generation, long CID DNS label rejection, path whitelist 404s, path-gateway mode, DNSLink-only hosts, wildcard DNSLink, `X-Forwarded-Host`, wildcard public gateway host patterns, and explicit disabling of localhost defaults.

Dependencies and integration points: spans gateway router host matching, subdomain origin isolation, DNS label encoding, CID and PeerID codec conversion, DNSLink resolver injection, reverse proxy headers, directory listing HTML, public gateway policy, and HTTP proxy behavior.

Risks and test signals: protects many security and compatibility edges: origin isolation bypass, unsafe long DNS labels, wrong redirect schemes behind proxies, wildcard host misrouting, and DNSLink exposure when disabled. Signals are exact `Location` headers, HTTP 400/404/301/200 statuses, expected payload text, and directory listing link fragments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0114-gateway-subdomains.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0115-gateway-dir-listing.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0115-gateway-dir-listing.sh

Purpose: verifies generated gateway directory listing HTML for path, subdomain, and DNSLink gateway modes.

Important APIs and helpers: uses `ipfs dag import` fixtures, gateway `curl` requests, `Gateway.PublicGateways`, `IPFS_NS_MAP`, daemon restarts, and HTML substring assertions.

Control flow and state: initializes a repo, imports a test directory, serves it through path gateway, subdomain gateway, and DNSLink gateway variants. For each mode it checks root backlink hiding, trailing-slash redirects, ETag presence, parent links, breadcrumb construction, name-column links, and hash-column CID links. It cleans up the repo at the end.

Dependencies and integration points: covers UnixFS directory listing generation, gateway mode-specific URL construction, DNSLink content roots, `filename` query linking, and cache validators.

Risks and test signals: catches broken relative links that can escape content roots or fail behind subdomains, missing ETags, and invalid breadcrumbs. Passing signals are expected HTML anchor fragments and redirect/header presence for all gateway modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0115-gateway-dir-listing.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0116-gateway-cache.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0116-gateway-cache.sh

Purpose: tests gateway cache validators for generated UnixFS directory listings over both `/ipfs/` and `/ipns/` content paths.

Important APIs and helpers: uses fixture CAR import, offline IPNS record injection with `ipfs routing put --allow-offline`, `curl -svX GET`, and assertions on response header traces.

Control flow and state: imports a fixed fixture tree, maps an IPNS ID to the root, requests a nested directory listing through `/ipfs/<root>/root2/root3/` and `/ipns/<id>/root2/root3/`, then asserts both responses contain special `Etag` values beginning with `DirIndex` and including the resolved directory CID.

Dependencies and integration points: covers gateway UnixFS directory rendering, cache-control metadata, IPNS resolution to immutable CIDs, and generated HTML ETag construction.

Risks and test signals: catches cache validator regressions where generated listings share weak or incorrect ETags, especially when mutable IPNS paths resolve to immutable directory roots. Passing requires matching `DirIndex-..._CID-<ROOT3_CID>` headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0116-gateway-cache.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0119-prometheus.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0119-prometheus.sh

Purpose: verifies Prometheus metrics exposure and metric-set changes caused by ResourceMgr config and the `flatfs-measure` profile.

Important APIs and helpers: uses `ipfs config --json Swarm.ResourceMgr.Enabled`, `test_init_ipfs_with_profile`, daemon launch/kill helpers, `curl` against the metrics endpoint, and filtering of Prometheus output.

Control flow and state: enables ResourceMgr, starts the daemon, collects metrics, filters relevant series, and checks the expected resource-manager metrics are present and stable. It repeats initialization with the `flatfs-measure` profile and checks additional flatfs-related metrics without losing baseline metrics.

Dependencies and integration points: covers daemon metrics server, Prometheus exposition format, resource manager instrumentation, profile-driven repo initialization, and flatfs datastore measurement hooks.

Risks and test signals: catches missing metrics after config/profile changes, unstable metric names, and disabled instrumentation. Passing is determined by expected metric lines after filtering and no loss of initial metric set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0119-prometheus.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0120-bootstrap.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0120-bootstrap.sh

Purpose: tests `ipfs bootstrap` list/add/remove operations offline and through a running daemon.

Important APIs and helpers: defines fixed bootstrap peers `BP1` through `BP7`, helper `test_bootstrap_list_cmd`, and helper `test_bootstrap_cmd`. It uses `ipfs bootstrap`, `bootstrap list`, `bootstrap add`, `bootstrap rm`, `bootstrap rm --all`, stdin input, `test_cmp`, and daemon lifecycle helpers.

Control flow and state: clears all bootstrap peers, verifies empty listing, adds peers by arguments, verifies exact output and persisted ordering, removes selected peers, rejects a malformed peer, removes all, then repeats add/remove using stdin. The whole sequence runs once offline and once with the daemon online.

Dependencies and integration points: covers config persistence for `Bootstrap`, multiaddr validation, command output stability, stdin parsing, and daemon-vs-offline command routing.

Risks and test signals: catches bootstrap config drift, broken batch input, bad error handling for invalid peers, and output changes that can break scripts. Signals are exact `added`/`removed` lines and list output equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0120-bootstrap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0121-bootstrap-iptb.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0121-bootstrap-iptb.sh

Purpose: verifies that bootstrap peer configuration affects real swarm connectivity in an IPTB cluster.

Important APIs and helpers: defines `betterwait`, uses `iptb testbed create`, `iptb start/stop/reset`, `ipfsi swarm peers`, `ipfsi bootstrap add/rm`, and disables mDNS to isolate bootstrap behavior.

Control flow and state: creates a local multi-node testbed, disables mDNS, starts nodes without bootstrap connectivity and checks peer counts, stops and resets nodes, configures bootstrap addresses, restarts, and checks the expected number of swarm peers. Persistent state is each node's bootstrap config and peerstore state after reset.

Dependencies and integration points: covers IPTB orchestration, Kubo bootstrap dialing, swarm peer discovery, mDNS isolation, and multi-node startup timing.

Risks and test signals: catches bootstrap peers being ignored, mDNS hiding bootstrap failures, and cluster timing issues. Pass signals are peer count checks before and after bootstrap configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0121-bootstrap-iptb.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0131-multinode-client-routing.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0131-multinode-client-routing.sh

Purpose: tests DHT client-mode routing in a multi-node network.

Important APIs and helpers: defines `check_file_fetch` and `run_single_file_test`, uses `iptb`, `ipfsi`, `random-data`, `ipfs add`, `ipfs cat`, config for routing/client mode, and cluster connect helpers.

Control flow and state: sets up a testbed, starts nodes, connects them, adds a file on a node configured in client mode, and fetches that file from another client-mode node. It then shuts down the cluster. State includes provider records, blockstore content on the adding node, and DHT/routing state across peers.

Dependencies and integration points: covers libp2p connectivity, routing mode configuration, content providing/finding, Bitswap fetch after routing discovery, and IPTB cluster lifecycle.

Risks and test signals: catches regressions where client-mode nodes cannot publish or discover content through routing peers. The pass signal is byte-for-byte retrieval of the generated file from a different node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0131-multinode-client-routing.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0140-swarm.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0140-swarm.sh

Purpose: validates `ipfs swarm` and related address behavior, including local address reporting, announce/no-announce config, peering commands, connect/disconnect, and `/p2p` address support.

Important APIs and helpers: uses `ipfs swarm peers`, `swarm addrs local`, `ipfs id`, config keys `Addresses.Announce`, `Addresses.AppendAnnounce`, `Addresses.NoAnnounce`, `ipfs swarm peering ls/add/rm`, and IPTB cluster commands.

Control flow and state: checks disconnected daemon peer/address output, verifies local swarm addresses match `ipfs id`, modifies announce settings and confirms advertised address lists change, tests peering add/remove output and config state, creates a TCP testbed, connects and disconnects peers using transport-stripped addresses and `/p2p` addresses, and verifies IDs and peer address formatting.

Dependencies and integration points: covers swarm address manager, config-driven announce filtering, peering service persistence, peer ID formatting, and libp2p connection commands.

Risks and test signals: catches incorrect advertised addresses, ignored no-announce CIDR filters, peering config regressions, and broken address parsing. Signals are exact address presence/absence, peer counts, and successful connect/disconnect operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0140-swarm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0141-addfilter.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0141-addfilter.sh

Purpose: tests swarm address filter configuration through legacy and current config paths.

Important APIs and helpers: defines `test_swarm_filter_cmd`, `test_config_swarm_addrfilters_cmd`, and `test_swarm_filters`. Uses `ipfs swarm filters`, `ipfs config Swarm.AddrFilters`, `ipfs config --json`, and `test_cmp`.

Control flow and state: starts from a repo without filters, adds and removes filter entries through swarm filter commands, verifies output, then manipulates the config array directly and checks the resulting filters list. Persistent state is the `Swarm.AddrFilters` config.

Dependencies and integration points: covers multiaddr filter parsing, config serialization, compatibility between command and config interfaces, and command output stability.

Risks and test signals: catches filter entries not persisting, duplicate or malformed output, and divergence between config and `swarm filters`. Passing is exact output comparison for each mutation scenario.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0141-addfilter.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0142-testfilter.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0142-testfilter.sh

Purpose: verifies swarm address filters are enforced during real peer connection attempts.

Important APIs and helpers: uses IPTB setup, `ipfsi config Swarm.AddrFilters`, `iptb start`, `iptb connect`, `ipfsi swarm peers`, and DNS-style addresses.

Control flow and state: creates a multi-node testbed, applies a filter for `127.0.0.0/24` on one node, starts the cluster, confirms connections involving the filtered node fail in both directions including DNS addresses, and confirms other unfiltered nodes can connect. State is per-node swarm filter config and live libp2p connections.

Dependencies and integration points: covers address filter enforcement, transport dialing, DNS multiaddr resolution, and IPTB cluster connectivity.

Risks and test signals: catches filters that only affect displayed addresses but not actual dialing, or that overblock unrelated peers. Pass signals are failed filtered connects, zero peer count for blocked nodes, and successful allowed connects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0142-testfilter.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0150-clisuggest.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0150-clisuggest.sh

Purpose: tests CLI typo suggestions for unknown commands both offline and through a daemon.

Important APIs and helpers: defines `test_suggest`, uses `test_must_fail ipfs kog`, `test_must_fail ipfs li`, `grep`, `test_fsh`, and daemon lifecycle helpers.

Control flow and state: initializes a repo, runs typo cases offline, starts the daemon, repeats the cases online, and kills the daemon. The command state is transient; no persistent config is modified beyond repo initialization.

Dependencies and integration points: covers command parser suggestion logic, CLI error output, and daemon command dispatch consistency.

Risks and test signals: catches missing or misleading suggestions and offline/online divergence. Passing requires singular "Did you mean this?" with `log` and plural "Did you mean any of these?" with both `ls` and `log`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0150-clisuggest.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0151-sysdiag.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0151-sysdiag.sh

Purpose: verifies `ipfs diag sys` reports expected system diagnostic fields and aligns with `uname`.

Important APIs and helpers: uses `ipfs diag sys`, `uname`, `grep`, and `test_cmp` style comparisons.

Control flow and state: initializes the repo if needed, runs `ipfs diag sys`, checks for expected keys in the output, runs `uname`, and compares relevant platform information. It does not depend on daemon state.

Dependencies and integration points: covers system diagnostics collection, platform metadata formatting, and CLI output compatibility with common Unix tools.

Risks and test signals: catches missing diagnostic keys, platform detection regressions, and output that drifts away from expected OS/kernel values. Passing requires key presence and similarity to `uname` output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0151-sysdiag.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0152-profile.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0152-profile.sh

Purpose: tests daemon profiling command behavior and the structure of generated profile archives.

Important APIs and helpers: uses `ipfs diag profile`, `unzip`, profile output files, `grep`, daemon launch/kill helpers, and checks for CPU, heap, goroutine, mutex, block, and stacktrace data.

Control flow and state: confirms profiling requires a running daemon, starts one, captures a default profile archive, verifies filename reporting and archive creation, repeats with `-o`, runs a profile with selected collectors, unpacks archives, and validates expected profile files are present while omitted collectors are absent from the small archive.

Dependencies and integration points: covers daemon debug/pprof collection, ZIP archive creation, CLI output, collector selection, and filesystem writes.

Risks and test signals: catches profiling available offline, missing collector outputs, invalid archive structure, and `-o` output path regressions. Passing requires archive existence and expected internal files after unzip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0152-profile.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0160-resolve.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0160-resolve.sh

Purpose: validates `ipfs resolve` over `/ipfs`, `/ipld`, and `/ipns` paths, including recursion, partial resolution, CID base preservation, and PeerID CID codec errors.

Important APIs and helpers: defines `test_resolve_setup_name`, `test_resolve`, `test_resolve_cmd`, `test_resolve_cmd_b32`, and `test_resolve_cmd_success`. Uses `ipfs add`, `ipfs dag put`, `ipfs key gen/list`, `ipfs name publish --allow-offline --ttl=0s`, `ipfs resolve`, `cid-fmt`, and daemon lifecycle helpers.

Control flow and state: prepares a nested UnixFS tree, an IPLD DAG, self and alternate IPNS keys, then checks resolution of roots and child paths. It publishes IPNS names to different targets, tests chained IPNS recursion, tests `-r=false` partial resolution, verifies recursion limit errors, and repeats base32 CID cases including a meaningful error when a PeerID is represented as CIDv1 with `dag-pb` instead of `libp2p-key`. A daemon-backed success subset runs online.

Dependencies and integration points: covers namesys cache bypass via TTL 0, UnixFS resolver, IPLD path resolver, key management, CID formatting, and daemon/offline command parity.

Risks and test signals: catches wrong terminal paths, infinite IPNS recursion, base conversion loss, and opaque codec errors. Passing requires exact resolved path strings and targeted error messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0160-resolve.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0165-keystore.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0165-keystore.sh

Purpose: comprehensive keystore command coverage for key generation, export/import formats, OpenSSL compatibility, protected self key operations, online behavior, and HTTP API restrictions.

Important APIs and helpers: defines `test_key_cmd`, private-key size checks, `test_key_import_export_all_formats`, `test_key_import_export`, `test_openssl_compatibility`, and `test_openssl_compatibility_all_types`. Uses `ipfs key gen/list/export/import/rm/rename`, `ipfs key rotate`, `curl`, OpenSSL fixture PEMs, and peer ID validation helpers.

Control flow and state: generates RSA and Ed25519 keys in b58mh/base36 IPNS bases, validates exported secret key sizes, round-trips PEM PKCS8 cleartext and libp2p protobuf formats, imports OpenSSL-generated keys, rejects unsupported key types unless `--allow-any-key-type`, verifies `-o` export, blocks export/import/remove/rename of `self`, checks list and long-list output, then starts a daemon to test online import/export compatibility, HTTP `key/export` 404, and disabled online key rotation.

Dependencies and integration points: covers keystore persistence, libp2p key encoding, PeerID bases, PEM/protobuf converters, API route exposure policy, and daemon keystore access.

Risks and test signals: protects secret key handling and self identity invariants. Signals include exact key IDs after import, sorted key lists, expected error text for protected operations, OpenSSL byte-for-byte round trips, and HTTP 404 for export.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0165-keystore.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0180-p2p.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0180-p2p.sh

Purpose: exercises experimental `ipfs p2p` listener, forwarding, stream, close, and protocol validation behavior across IPTB nodes.

Important APIs and helpers: defines `check_test_ports`, `spawn_sending_server`, and `test_server_to_client`. Uses `iptb`, `ipfsi p2p listen/forward/ls/close`, `p2p stream ls/close`, local TCP servers, generated test data, and peer IDs.

Control flow and state: initializes a testbed, verifies commands fail before the feature is enabled, enables the required config, starts listeners, rejects duplicate registrations, tests server-to-client and client-to-server data flow, validates dead-server handling, listing output, zero-port rejection, stream listing and targeted/all close modes, reported peer listeners, custom protocol listeners, and rejection of non-`/x/` scoped protocols. It ends by stopping IPTB.

Dependencies and integration points: covers libp2p stream forwarding, local TCP sockets, p2p protocol namespace policy, stream manager state, and multi-node peer addressing.

Risks and test signals: catches leaked streams/listeners, duplicate handler acceptance, bad protocol validation, and broken data proxying. Passing requires expected p2p lists, empty or matching data outputs, failed invalid operations, and successful close cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0180-p2p.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0181-private-network.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0181-private-network.sh

Purpose: tests private network `swarm.key` enforcement and its conflict with AutoConf.

Important APIs and helpers: defines `pnet_key`, `set_key`, `run_single_file_test`, and `check_file_fetch`. Uses `ipfs daemon`, IPTB, `ipfsi config`, `iptb connect`, `ipfsi swarm peers`, generated data, and AutoConf config.

Control flow and state: disables AutoConf for private-network tests, checks daemon failure diagnostics for incompatible setup, creates a multi-node testbed with public and two distinct private-network keys, attempts cross-network connections and verifies they fail, connects nodes sharing the same key and verifies peer counts, then creates a repo with AutoConf enabled plus `swarm.key` and asserts daemon startup fails with a clear conflict message.

Dependencies and integration points: covers pnet protector setup, swarm connection gating, testbed key distribution, AutoConf safety checks, and daemon startup diagnostics.

Risks and test signals: catches private-network isolation bypass, unclear startup errors, and incompatible AutoConf use. Signals are failed cross-key connects, empty peer lists, successful same-key peer counts, and error text mentioning AutoConf/private network conflict.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0181-private-network.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0182-circuit-relay.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0182-circuit-relay.sh

Purpose: verifies relay-v2 circuit relay connectivity through a configured relay node.

Important APIs and helpers: uses IPTB, `ipfsi id`, JSON config with `jq`, static relay configuration, swarm connect, peer ID extraction, and peer list assertions.

Control flow and state: initializes nodes, starts them for configuration, records peer IDs, configures one node as a static relay for node A, configures the relay node and node B, restarts nodes, connects A and B to the relay, waits until relay reservation/readiness is available, connects A to B through the relay, then checks connection output and peer lists for A and B.

Dependencies and integration points: covers libp2p relay service/client config, reservation readiness, multiaddr relay paths, swarm connection reporting, and IPTB orchestration.

Risks and test signals: catches relay reservation timing, wrong static relay config, and peer list inconsistencies after relayed connections. Passing requires successful relay connection output and expected peer entries on both endpoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0182-circuit-relay.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0183-namesys-pubsub.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0183-namesys-pubsub.sh

Purpose: validates IPNS over pubsub behavior when enabled by config and when disabled by CLI flag.

Important APIs and helpers: defines `run_ipnspubsub_tests`, uses IPTB, `ipfsi name pubsub state/subs/cancel`, `ipfsi add`, `ipfsi name publish`, `ipfsi name resolve`, `grep`, and config keys for IPNS pubsub.

Control flow and state: initializes an IPTB cluster, checks pubsub state, subscribes nodes to the publisher topic, verifies subscriptions, publishes an IPNS record, waits for propagation, resolves from subscriber nodes, cancels subscriptions, and checks cleanup. It runs enabled configurations, then verifies the command fails when the subsystem is disabled through CLI flag and emits guidance to enable IPNS pubsub.

Dependencies and integration points: covers namesys pubsub topic management, IPNS publication propagation, subscription state, resolver behavior, and feature gating through config/flags.

Risks and test signals: catches pubsub records not flooding, stale subscriptions, disabled feature leakage, and poor error messages. Passing requires successful subscriber resolution and expected disabled-subsystem errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0183-namesys-pubsub.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0184-http-proxy-over-p2p.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0184-http-proxy-over-p2p.sh

Purpose: tests HTTP gateway proxying over `ipfs p2p`, including error propagation, multipart requests, protocol parsing, and `/p2p` subdomain gateway routing.

Important APIs and helpers: requires `socat`, uses IPTB nodes, `ipfsi p2p listen`, gateway config with `/p2p` path whitelisted, local HTTP server fixtures, `curl`, Host headers, receiver/sender peer IDs, and daemon stop/start helpers.

Control flow and state: configures two nodes and a subdomain gateway, connects them, registers a p2p listener on the receiver for HTTP, sets sender gateway environment, checks bad gateway when the remote server is absent, starts a local HTTP server, verifies remote error propagation and successful HTTP content, rejects invalid requests and unknown/invalid peers, tests custom and missing protocols, rejects missing `/http`, sends multipart/form-data, and checks subdomain gateway behavior for `/p2p/<peer>/http` including full-path rejection and path-to-subdomain redirect.

Dependencies and integration points: covers gateway `/p2p` router, p2p stream forwarding, HTTP proxy request mapping, multipart body transfer, peer ID CIDv1 subdomains, and public gateway path policy.

Risks and test signals: catches SSRF-like path confusion, bad peer validation, broken body streaming, and origin-isolation mistakes for p2p gateways. Signals are HTTP status lines, body text, redirect `Location`, and expected failures for malformed paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0184-http-proxy-over-p2p.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0185-autonat.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0185-autonat.sh

Purpose: smoke-tests daemon startup with AutoNAT service mode enabled and disabled.

Important APIs and helpers: uses `test_init_ipfs`, `ipfs config AutoNAT.ServiceMode`, and daemon launch/kill helpers.

Control flow and state: sets `AutoNAT.ServiceMode` to `enabled`, launches and kills the daemon, then sets it to `disabled` and repeats. Persistent state is the AutoNAT config key.

Dependencies and integration points: covers AutoNAT service configuration parsing and daemon subsystem startup/shutdown.

Risks and test signals: catches invalid config values, startup panics, or stale subsystem state between daemon runs. Passing requires clean daemon lifecycle in both service modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0185-autonat.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0190-quic-ping.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0190-quic-ping.sh

Purpose: validates peer ping over QUIC-v1 swarm addresses.

Important APIs and helpers: uses IPTB, `ipfsi config --json Addresses.Swarm`, peer ID retrieval, `ipfsi ping -n2`, invalid self-ping and zero-count cases, and `iptb stop`.

Control flow and state: initializes a two-node testbed, configures QUIC swarm addresses, starts nodes, records peer IDs, verifies each node can ping the other, verifies pinging self through the command fails, verifies `-n0` fails, and stops the cluster.

Dependencies and integration points: covers QUIC transport listener/dialer setup, libp2p ping protocol, swarm address config, and command validation.

Risks and test signals: catches QUIC transport regressions and bad ping argument handling. Passing requires bidirectional remote ping success and expected failures for self and zero-count pings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0190-quic-ping.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0191-webtransport-ping.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0191-webtransport-ping.sh

Purpose: validates peer ping over WebTransport swarm addresses.

Important APIs and helpers: uses IPTB, `ipfsi config --json Addresses.Swarm`, peer IDs, `ipfsi ping -n2`, self-ping failure, zero-count failure, and cluster stop.

Control flow and state: initializes a two-node testbed, configures WebTransport addresses, starts nodes, records identities, performs bidirectional remote pings, asserts self-ping and `-n0` calls fail, then stops IPTB.

Dependencies and integration points: covers WebTransport transport setup, TLS/cert requirements hidden in Kubo transport config, libp2p ping, and command argument validation.

Risks and test signals: catches WebTransport listener or dialer regressions and command validation drift. Passing requires remote ping success over WebTransport and expected failures for invalid ping targets/counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0191-webtransport-ping.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0195-noise.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0195-noise.sh

Purpose: verifies Noise security transport interoperability and incompatibility with TLS-only peers.

Important APIs and helpers: uses IPTB, `ipfs config --json Swarm.Transports.Security.TLS/Noise`, swarm addresses, peer IDs, `ipfsi ping`, `iptb connect`, and error assertions.

Control flow and state: initializes testbed nodes, configures security transports so selected nodes support Noise and another supports TLS-only behavior, starts compatible nodes, verifies Noise-backed bidirectional ping, then starts incompatible nodes and asserts connection negotiation fails with a security protocol error.

Dependencies and integration points: covers libp2p security transport selection, Noise/TLS negotiation, ping over secured streams, and connection diagnostics.

Risks and test signals: catches accidental fallback to disabled security transports or unclear negotiation failures. Signals are successful pings among compatible nodes and expected failure text for TLS-incompatible connection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0195-noise.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0220-bitswap.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0220-bitswap.sh

Purpose: tests Bitswap command output for stats and wantlists.

Important APIs and helpers: uses `ipfs bitswap stat`, `ipfs bitswap stat --human`, `ipfs bitswap wantlist -p`, `ipfs bitswap wantlist`, `ipfs config Identity.PeerID`, `test_check_peerid`, `test_cmp`, and daemon lifecycle helpers.

Control flow and state: starts a daemon, checks Bitswap stats output includes expected fields, validates local peer ID formatting, checks wantlist output with peer display, confirms the wantlist is empty after no outstanding requests, and repeats stat checks including human-readable output.

Dependencies and integration points: covers Bitswap session/accounting introspection, peer ID display, wantlist query endpoints, and human-size formatting.

Risks and test signals: catches renamed/missing stats fields, stale wantlist entries, and peer ID formatting regressions. Passing requires expected output fields and empty wantlist where appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0220-bitswap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0230-channel-streaming-http-content-type.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0230-channel-streaming-http-content-type.sh

Purpose: verifies HTTP API streaming response content type and CORS headers for channel-streaming commands.

Important APIs and helpers: defines `test_ls_cmd`, uses `ipfs add -r`, API endpoint `http://$API_ADDR/api/v0/refs?...&stream-channels=true`, `curl -X POST -i`, `grep`, `test_cmp`, and daemon lifecycle helpers.

Control flow and state: creates a small test directory, adds it, calls the refs API with channel streaming enabled, and compares HTTP headers for status, allowed CORS headers, content type, and stream output behavior. The helper is run for relevant command variants.

Dependencies and integration points: covers API command HTTP envelope, streaming channel negotiation, CORS header generation, and refs traversal over API.

Risks and test signals: catches browser/API compatibility regressions caused by wrong content type or missing stream headers. Passing is exact header comparison against the expected HTTP response prefix.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0230-channel-streaming-http-content-type.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0231-channel-streaming.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0231-channel-streaming.sh

Purpose: tests that channel-streaming API output is newline-delimited rather than concatenated JSON objects.

Important APIs and helpers: defines `get_api_port` and `test_ls_cmd`, uses `random-data`, `ipfs add`, `curl http://localhost:<port>/api/v0/refs/<hash>`, `grep`, and daemon lifecycle helpers.

Control flow and state: adds a large random file, calls the refs API through the daemon, writes output to a file, and asserts the stream does not contain adjacent `}{` JSON boundaries without separators.

Dependencies and integration points: covers API port discovery, refs endpoint streaming, JSON event framing, and daemon HTTP response behavior.

Risks and test signals: catches response framing regressions that break streaming clients. Passing requires grep not finding `}{` in the response.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0231-channel-streaming.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0235-cli-request.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0235-cli-request.sh

Purpose: inspects raw HTTP generated by CLI commands when using a DNS multiaddr API endpoint.

Important APIs and helpers: requires `SOCAT`, uses FIFOs, `socat` as a fake API server on `127.0.0.1:5005`, `ipfs cat --api /dns4/localhost/tcp/5005`, shell file descriptors, and `grep`.

Control flow and state: starts the fake server, runs `ipfs cat`, manually responds to the client's `/api/v0/version` probe and then `/api/v0/cat`, captures request headers, stops the server, and verifies the request is a POST to `/api/v0/cat`, has `Host: localhost:5005`, does not include multipart markers, and does not leak the `api=` query value.

Dependencies and integration points: covers CLI HTTP client request construction, DNS multiaddr host preservation, API version negotiation, and command argument serialization.

Risks and test signals: catches leaking API endpoint details into command requests, wrong host header generation, or accidental multipart encoding. Passing is raw request text matching expected and missing forbidden substrings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0235-cli-request.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0236-cli-api-dns-resolve.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0236-cli-api-dns-resolve.sh

Purpose: verifies CLI API dialing resolves `/dns4/localhost` multiaddrs correctly while preserving the HTTP request target.

Important APIs and helpers: requires `SOCAT`, uses fake API server on port 5006, FIFOs, `ipfs cat --api /dns4/localhost/tcp/5006`, manual HTTP responses, and `grep`.

Control flow and state: starts a fake API server, runs an `ipfs cat` command against a DNS multiaddr, responds to version and cat requests, captures headers, stops the server, and verifies a POST to `/api/v0/cat` was sent. State is transient socket/FIFO state only.

Dependencies and integration points: covers DNS multiaddr resolution, CLI API HTTP transport, version probing, and request path construction.

Risks and test signals: catches failures to resolve DNS API addresses or attempts to use the unresolved multiaddr as an invalid network endpoint. Passing is the fake server seeing the expected API request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0236-cli-api-dns-resolve.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0240-republisher.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0240-republisher.sh

Purpose: tests IPNS republishing behavior across multiple nodes, including self key and alternate key records.

Important APIs and helpers: defines `setup_iptb`, `teardown_iptb`, `verify_can_resolve`, and `verify_cannot_resolve`; uses IPTB, `ipfsi config Ipns.RepublishPeriod`, `Ipns.ResolveCacheSize`, `ipfsi name publish -t`, `ipfsi name resolve`, `ipfsi key gen`, and date-based content.

Control flow and state: creates a testbed, configures short republish periods and zero resolve cache, publishes expiring IPNS records, records IDs, verifies resolution before and after expected republish windows, and repeats for an alternate Ed25519 key. State includes IPNS records in routing, local keystore keys, and node resolver caches.

Dependencies and integration points: covers IPNS republisher scheduling, record TTL/lifetime handling, routing publication, key-specific publishing, and resolver cache behavior.

Risks and test signals: catches records expiring without republish, resolve cache masking failures, and alternate-key republishing bugs. Passing is successful resolution to the expected `/ipfs/<hash>` when republish should have occurred and failure when it should not.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0240-republisher.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0250-files-api.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0250-files-api.sh

Purpose: large integration suite for the Mutable File System `ipfs files` API, covering mkdir, ls, stat, cp, read, write, rm, mv, flush, CID/hash config, sharding, and automatic shard/unshard behavior.

Important APIs and helpers: defines `restart_daemon`, `create_files`, `verify_path_exists`, `verify_dir_contents`, `test_sharding`, `test_files_api`, `tests_for_files_api`, and `test_add_large_sharded_dir`. Uses `ipfs files mkdir/ls/stat/cp/read/write/rm/mv/flush/chcid`, `ipfs add`, `ipfs repo gc`, `ipfs config Import.CidVersion`, `Import.HashFunction`, `Import.UnixFSHAMTDirectorySizeThreshold`, `cid-fmt`, `pollEndpoint`, daemon lifecycle helpers, and `dd`.

Control flow and state: runs the API matrix offline and daemon-backed. It creates fixture CIDs, checks root/default ls, stat formats and `--with-local`, rejects invalid root operations, copies immutable `/ipfs` content into MFS, validates long listings and base32 CIDs, reads with offsets/counts, writes with create/offset/truncate/raw-leaves/parents/flush flags, checks no-flush behavior against daemon API, moves directories, removes files and dirs including force and multiple-target cases, tests `chcid`, and validates root CID changes under import config. It then enables HAMT sharding, verifies sorted and unsorted listings, file reads and pins within sharded dirs, and tests automatic sharding/unsharding of a large directory near the threshold.

Dependencies and integration points: covers MFS DAG mutation, UnixFS importer settings, root persistence, daemon flush semantics, CID version/hash-function propagation, HAMT directory implementation, local refs visibility, and GC interaction.

Risks and test signals: catches high-blast-radius MFS regressions: corrupted root updates, wrong hashes, bad sparse writes, path creation mistakes, force removal semantics, daemon/offline divergence, and shard threshold errors. Signals are exact expected root/file hashes, byte-for-byte reads, directory listings, command failure codes, and sharded directory CIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0250-files-api.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0251-files-flushing.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0251-files-flushing.sh

Purpose: focused test for MFS flush persistence after copying content into files.

Important APIs and helpers: defines `verify_path_exists` and `verify_dir_contents`, uses `ipfs add`, `ipfs files cp`, `ipfs files ls`, and daemon lifecycle helpers.

Control flow and state: starts a daemon, adds a small file, copies it from `/ipfs/<hash>` into `/file` in MFS, and verifies the path exists/listing is correct. The relevant state is the flushed MFS root and file entry.

Dependencies and integration points: covers MFS root mutation through daemon, flushing to repo state, and immutable-to-mutable file copy.

Risks and test signals: catches writes that appear in memory but do not flush/persist. Passing requires `ipfs files ls` and path existence checks to see `/file` after the copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0251-files-flushing.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0252-files-gc.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0252-files-gc.sh

Purpose: verifies garbage collection preserves blocks reachable from MFS and handles incomplete directories safely.

Important APIs and helpers: uses `ipfs files write/mkdir/cp/read/stat`, `ipfs repo gc`, `ipfs cat`, `ipfs dag get`, `ipfs pin add`, `ipfs add --pin=false`, and `test_cmp`.

Control flow and state: writes `/hello.txt` through MFS and confirms GC does not remove it, reads it back, creates directories and direct pins, runs GC with incomplete nodes, adds an unpinned directory whose file can be removed by GC, copies the directory into MFS while missing content, then restores content and verifies GC preserves it once reachable. State is the MFS root, direct pins, unpinned blocks, and incomplete DAG links.

Dependencies and integration points: covers GC mark roots from MFS, direct pin interaction, DAG completeness checks, and UnixFS directory reachability.

Risks and test signals: catches data loss for MFS roots or GC crashes on incomplete MFS/directory state. Signals are successful `files read`/`cat` for protected blocks and expected failure for unprotected removed content.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0252-files-gc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0260-sharding.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0260-sharding.sh

Purpose: tests UnixFS HAMT-sharded directory import, access, gateway/resolve support, and behavior with incomplete sharded DAGs.

Important APIs and helpers: defines `test_add_dir`, `test_add_dir_v1`, and `test_list_incomplete_dir`; uses `ipfs add -r -Q`, `ipfs get`, `ipfs ls`, `ipfs cat`, `ipfs resolve`, `ipfs block rm`, gateway `curl`, and config `Import.UnixFSHAMTDirectorySizeThreshold`.

Control flow and state: creates 2000-file test data, forces sharding off and on to compare deterministic CIDs, checks sharded and unsharded listings match, verifies cat errors match for directories, checks `ipfs ls --resolve-type=false --size=false` tolerates missing blocks, tests gateway and `ipfs resolve` access to sharded paths, imports CIDv1 sharded dirs, tests SHA3-256/CIDv1 sharded import, removes a child block, and verifies listing reports an incomplete fetch error.

Dependencies and integration points: covers UnixFS importer sharding thresholds, HAMT traversal, gateway path resolution, resolver integration, multihash/hash-function config, and incomplete DAG error handling.

Risks and test signals: catches incorrect sharded CIDs, inability to resolve files inside shards, and over-eager metadata fetches. Signals are expected root hashes, matching listings, file content via gateway/cat, and targeted missing-block errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0260-sharding.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0270-filestore.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0270-filestore.sh

Purpose: tests filestore `--nocopy` behavior, repository size impact, and experimental feature gating.

Important APIs and helpers: defines `get_repo_size`, `assert_repo_size_less_than`, `assert_repo_size_greater_than`, `test_filestore_adds`, and `init_ipfs_filestore`. Uses `random-files`, `ipfs add --raw-leaves --nocopy`, normal `ipfs add`, `ipfs config Experimental.FilestoreEnabled`, `Experimental.UrlstoreEnabled`, and daemon lifecycle helpers.

Control flow and state: creates a large random dataset, asserts repo size thresholds, initializes repos with or without filestore, adds directories with `--nocopy`, compares expected hashes, checks normal add with file-store cache does not duplicate data unexpectedly, and verifies `--nocopy` fails when filestore is disabled or only urlstore is enabled, then succeeds when both relevant experimental configs are enabled.

Dependencies and integration points: covers filestore block references, blockstore size accounting, importer raw leaves, feature flags, and repo reinitialization.

Risks and test signals: catches accidental data copying, disabled-feature bypass, and hash divergence between nocopy and normal import. Signals are repo size bounds, expected root CIDs, and error messages for disabled filestore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0270-filestore.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0271-filestore-utils.sh -->
## sources/distributed-fs/ipfs-kubo/test/sharness/t0271-filestore-utils.sh

Purpose: tests `ipfs filestore` utility commands for listing, verification, missing/changed file detection, bad-block removal, and duplicate reporting.

Important APIs and helpers: defines `test_init_filestore`, `test_init_dataset`, `test_init`, `test_filestore_adds`, `test_filestore_state`, `test_filestore_verify`, `test_filestore_rm_bad_blocks`, and `test_filestore_dups`. Uses `ipfs add --raw-leaves --nocopy`, `ipfs filestore ls`, `filestore verify`, `verify --remove-bad-blocks`, `filestore dups`, `ipfs cat`, `random-data`, `dd`, and daemon lifecycle helpers.

Control flow and state: initializes filestore-enabled repos and deterministic datasets, adds files by reference, validates root hash and utility listing order, reads referenced files, verifies all entries, renames a source file to simulate missing data, restores it, corrupts source bytes to simulate changed data, removes bad blocks with verify, and checks duplicate detection. The suite runs across configured command contexts through `$IPFS_CMD`.

Dependencies and integration points: covers filestore metadata persistence, source file path tracking, block verification against external files, block removal side effects, duplicate block mapping, and daemon/offline command routing.

Risks and test signals: catches stale references, false verification success after external mutation, unsafe bad-block removal, and unstable listing order. Signals are exact `filestore ls/verify` output, failed `cat` for missing/changed backing files, successful reads after restore, and duplicate reports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/test/sharness/t0271-filestore-utils.sh -->
