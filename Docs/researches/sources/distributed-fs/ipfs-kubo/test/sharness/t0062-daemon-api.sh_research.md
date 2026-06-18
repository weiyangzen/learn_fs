## sources/distributed-fs/ipfs-kubo/test/sharness/t0062-daemon-api.sh

Purpose: validates daemon API discovery through `$IPFS_PATH/api`, including the CLI behavior when the daemon is online, offline, and when an API file points at an unusable address.

Important APIs and helpers: sources `lib/test-lib.sh`, uses `test_init_ipfs`, `test_launch_ipfs_daemon`, `test_kill_ipfs_daemon`, `test_check_peerid`, `test_cmp`, and local helpers `test_client`, `test_client_must_fail`, and `test_client_suite`. The main command surface is `ipfs id -f=<id>`, `ipfs config Identity.PeerID`, and the daemon-created `api` file.

Control flow and state: initializes a repo, records the configured peer ID as the expected API identity, runs client checks through the live daemon, kills the daemon, writes a fake API multiaddr into the persisted repo `api` file, and verifies commands fail with a targeted API connection error. It then restarts the daemon and asserts that startup recreates or updates the API file.

Dependencies and integration points: covers CLI-to-daemon HTTP API routing, repo path discovery, API multiaddr persistence, and daemon lifecycle helpers. The test relies on exact error text for the standalone-vs-daemon hint.

Risks and test signals: catches regressions where Kubo silently ignores stale API files, reports confusing client errors, uses the wrong daemon identity, or fails to create `$IPFS_PATH/api`. A pass signal is peer ID equality plus expected failure diagnostics when the API endpoint is invalid.
