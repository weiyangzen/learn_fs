## sources/distributed-fs/ipfs-kubo/test/sharness/lib/test-lib.sh

Purpose: Kubo-specific sharness bootstrap and helper library, sourced by nearly every shell test.

Important APIs and control flow: it configures PATH unless `MAKE_SKIP_PATH=1`, maps environment flags to sharness prerequisites, sources `test-lib-hashes.sh`, symlinks and sources sharness, aborts if leftover daemons have CWDs under the current test directory, sets `IPFS_PATH`, imports `ipfs-test-lib.sh` and `iptb-lib.sh`, and defines helpers for repeat comparisons, polling, daemon launch, mount/unmount, daemon kill, curl response checks, content assertions, disk/stat portability, peer ID checks, multiaddr conversion, provider assertions, and blockstore purge.

State and persistence: creates symlinks, `stuck_cwd_list`, temporary assertion files, `.ipfs` repos, mount directories, daemon output files, and process state. It also controls `IPFS_PID`, API/gateway/swarm address variables, and ulimit.

Dependencies and integration points: relies on local `ipfs`, sharness, `pollEndpoint`, `go-sleep`, lsof, netstat, curl, FUSE tools, and many POSIX utilities.

Risks: this is high-blast-radius infrastructure. Daemon cleanup, polling timeouts, platform-specific stat/base64/FUSE behavior, and global variables can affect unrelated tests. Test signals include stable daemon startup readiness, mount output, peer ID validation, and reusable assertion helpers.
