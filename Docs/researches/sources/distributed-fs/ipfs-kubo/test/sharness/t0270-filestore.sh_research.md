## sources/distributed-fs/ipfs-kubo/test/sharness/t0270-filestore.sh

Purpose: tests filestore `--nocopy` behavior, repository size impact, and experimental feature gating.

Important APIs and helpers: defines `get_repo_size`, `assert_repo_size_less_than`, `assert_repo_size_greater_than`, `test_filestore_adds`, and `init_ipfs_filestore`. Uses `random-files`, `ipfs add --raw-leaves --nocopy`, normal `ipfs add`, `ipfs config Experimental.FilestoreEnabled`, `Experimental.UrlstoreEnabled`, and daemon lifecycle helpers.

Control flow and state: creates a large random dataset, asserts repo size thresholds, initializes repos with or without filestore, adds directories with `--nocopy`, compares expected hashes, checks normal add with file-store cache does not duplicate data unexpectedly, and verifies `--nocopy` fails when filestore is disabled or only urlstore is enabled, then succeeds when both relevant experimental configs are enabled.

Dependencies and integration points: covers filestore block references, blockstore size accounting, importer raw leaves, feature flags, and repo reinitialization.

Risks and test signals: catches accidental data copying, disabled-feature bypass, and hash divergence between nocopy and normal import. Signals are repo size bounds, expected root CIDs, and error messages for disabled filestore.
