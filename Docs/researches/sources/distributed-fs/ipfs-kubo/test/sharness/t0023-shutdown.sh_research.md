## sources/distributed-fs/ipfs-kubo/test/sharness/t0023-shutdown.sh

Purpose: validates the `ipfs shutdown` command against online and offline-mode daemons.

Important control flow: starts a normal daemon, runs `ipfs shutdown`, asserts the daemon process no longer runs, then repeats with `test_launch_ipfs_daemon_without_network`. This script intentionally does not use the standard kill helper after shutdown because the command under test should terminate the daemon.

State and dependencies: creates temporary repo/daemon process state and uses `IPFS_PID` from `test-lib.sh`. Depends on API readiness and shell `kill -0`.

Risks: process termination timing can be flaky if shutdown is asynchronous; the script must avoid double-killing successfully stopped daemons. Test signal is successful shutdown command and dead process in both networked and offline daemon modes.
