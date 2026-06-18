## sources/distributed-fs/ipfs-kubo/test/sharness/t0063-daemon-init.sh

Purpose: verifies that `ipfs daemon --init` can bootstrap a missing or empty repository and then run a daemon that can be shut down cleanly.

Important APIs and helpers: sources `lib/test-lib.sh`, defines `test_ipfs_daemon_init`, and uses `test_launch_ipfs_daemon --init --offline`, `test_kill_ipfs_daemon`, and direct filesystem resets of `$IPFS_PATH`.

Control flow and state: the helper starts a daemon with `--init --offline`, then kills it. It is invoked after removing `$IPFS_PATH` entirely and again after recreating an empty `$IPFS_PATH` directory. The core persistent state is repo initialization data written under `$IPFS_PATH`.

Dependencies and integration points: exercises daemon initialization code, repo creation, offline daemon start, lock acquisition, and shutdown paths from sharness helpers.

Risks and test signals: protects against regressions where `--init` only works for nonexistent paths but not empty directories, or where repo creation succeeds but daemon shutdown leaves stale state. A pass is a daemon that starts and stops in both filesystem states without explicit `ipfs init`.
