## sources/distributed-fs/ipfs-kubo/test/sharness/t0088-repo-stat-symlink.sh

Purpose: verifies `ipfs repo stat` works when `.ipfs` is a symlink.

Important APIs and helpers: uses `ln -s`, `ipfs init`, `ipfs repo stat`, `awk`, and numeric comparison on `RepoSize`.

Control flow and state: creates a symlink target, links `.ipfs` to it, initializes the repo through the symlink, and parses `RepoSize` from `repo stat` to verify it is greater than zero.

Dependencies and integration points: covers repo path resolution, filesystem symlink handling, repo initialization, and stat size calculation.

Risks and test signals: catches code that resolves or walks repo paths incorrectly when the configured path is symlinked. The pass signal is a successful stat with positive `RepoSize`.
