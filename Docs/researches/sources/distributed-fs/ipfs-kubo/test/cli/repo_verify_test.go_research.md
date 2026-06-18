# sources/distributed-fs/ipfs-kubo/test/cli/repo_verify_test.go

Purpose: tests `ipfs repo verify` for healthy repos, corruption detection, dropping corrupt blocks, healing from peers, partial healing, empty repos, scale, and removal-failure reporting.

Important APIs and helpers: constants name flatfs filenames for empty UnixFS file and directory blocks, which are excluded from corruption due to special behavior. `getEligibleFlatfsBlockFiles` glob-searches `blocks/*/*.data`, filters special blocks, and returns mutable block paths. `corruptRandomBlock` and `corruptMultipleBlocks` overwrite selected flatfs files with invalid bytes.

Control flow: `TestRepoVerify` contains parallel subtests. Healthy and empty repos expect `all blocks validated`. Corruption tests overwrite blocks, then expect non-zero verification and count summaries. `--drop` should remove corrupt blocks and make `block stat` fail. `--heal` requires online mode, can repair by fetching from a connected peer, verifies healed content and raw block equality, can partially heal only available blocks, and fails when no peer has content. Scale tests corrupt 10 of 1000 blocks. Removal-failure tests chmod a corrupted file and directory read-only, then require partial remove failure counts.

State and persistence: tests directly mutate the flatfs blockstore on disk and observe repo state through `repo verify`, `block stat`, `cat`, and `repo gc`. Heal removes corrupt local blocks and attempts network refetch.

Dependencies and integration points: depends on flatfs layout, filesystem permissions, Kubo block validation, Bitswap/network retrieval, pinning/GC to control availability, and diagnostic count reporting.

Risks and test signals: tests are flatfs-specific and may not apply to alternate blockstores. Permission simulation can be platform-sensitive, especially under privileged users. Failures indicate corrupt blocks not detected, summaries wrong, drop/heal exit codes wrong, healed bytes mismatched, or partial failure accounting broken.
