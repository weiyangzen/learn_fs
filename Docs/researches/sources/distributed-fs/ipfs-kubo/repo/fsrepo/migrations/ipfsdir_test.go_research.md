# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/ipfsdir_test.go

Purpose: tests repo path discovery and version file parsing/writing.

Important APIs and control flow: `TestRepoDir` sets fake HOME, USERPROFILE, and `IPFS_PATH`, then runs subtests for `IpfsDir`, `CheckIpfsDir`, and `RepoVersion`. Cases cover missing directory, env path, `~/.ipfs` expansion, unsupported `~user` expansion, nonexistent directory, missing version file, valid version write/read, and invalid version data.

State and persistence: creates a fake `.ipfs` directory and writes/removes version files under it.

Dependencies and integration: exercises `config.EnvDir`, `config.PathRoot`, `fsutil.ExpandHome`, and migration version helpers.

Risks and test signals: useful cross-platform signal via `USERPROFILE`; does not cover permission errors or atomicity of version writes.
