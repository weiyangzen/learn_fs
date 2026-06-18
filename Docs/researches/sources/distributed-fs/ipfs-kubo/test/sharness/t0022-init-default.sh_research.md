## sources/distributed-fs/ipfs-kubo/test/sharness/t0022-init-default.sh

Purpose: validates `ipfs init` behavior with default configuration.

Important control flow: initializes a repo, asserts `.ipfs/config` exists, reads config through `ipfs config`, removes the repo, runs default init again, and compares expected config output. State is the temporary `.ipfs` repository.

Dependencies and integration points: uses the local `ipfs` binary and shared shell comparison helpers. It exercises fs-repo initialization and default config generation without a daemon.

Risks: expected output can shift with intentional default config changes. Test signal is that init succeeds, writes config, and produces readable default config values.
