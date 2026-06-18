## sources/distributed-fs/ipfs-kubo/test/sharness/t0064-api-file.sh

Purpose: checks how commands classify local-only, offline-capable, and daemon-required operations when the repo API file is absent, stale, present, or produced from wildcard API listen config.

Important APIs and helpers: uses `ipfs version`, `ipfs swarm peers`, `ipfs pin ls`, `ipfs id`, `ipfs config Addresses.API`, `test_init_ipfs`, daemon launch/kill helpers, `test_must_fail`, and `test_cmp`.

Control flow and state: starts from an initialized offline repo with no daemon, verifies daemon-required commands fail when no API is available, writes `$API_MADDR` manually to `$IPFS_PATH/api`, then verifies commands that can run locally still work while daemon-required ones fail. After launching the daemon it checks that all selected commands work, removes the API file again, and verifies fallback behavior. The final case configures `Addresses.API` on `0.0.0.0` and asserts the emitted API file is normalized to `127.0.0.1`.

Dependencies and integration points: covers command request routing, repo-local command execution, daemon endpoint discovery, API multiaddr serialization, and wildcard address rewriting.

Risks and test signals: catches accidental daemon dependency for offline commands, stale API endpoint misuse, and unsafe API file exposure on unspecified addresses. Exact pass signals are command exit codes and the normalized API file content.
