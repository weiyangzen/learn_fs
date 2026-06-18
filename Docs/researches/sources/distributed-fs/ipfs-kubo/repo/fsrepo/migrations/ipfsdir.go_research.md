# sources/distributed-fs/ipfs-kubo/repo/fsrepo/migrations/ipfsdir.go

Purpose: resolves repo directories and reads/writes repo version files for migration code.

Important APIs and control flow: `IpfsDir` uses an explicit path or `config.PathRoot`, expands home directories, and returns the normalized repo path. `CheckIpfsDir` additionally requires the directory to exist. `RepoVersion` checks the directory then parses `version`. `WriteRepoVersion` expands the path and writes `<version>\n`. Private `repoVersion` trims and converts version text.

State and persistence: reads and writes the `version` file in the repo directory.

Dependencies and integration: used by `fsrepo.Init`, `fsrepo.Open`, legacy and embedded migration runners, and version tests.

Risks and test signals: invalid version file returns a generic error. `WriteRepoVersion` does not ensure directory existence or atomic write. Tests cover env/default path expansion, nonexistent dirs, user-specific home expansion errors, missing version, invalid data, and successful write/read.
