# sources/distributed-fs/ipfs-kubo/core/commands/update.go

Purpose: implements experimental local `ipfs update` commands for checking, listing, installing, reverting, and cleaning Kubo binaries from GitHub Releases.

Important APIs/types/functions: `UpdateCmd` is `NoRemote` and repo/config-input independent. Outputs include `UpdateCheckOutput`, `UpdateVersionsOutput`, `UpdateInstallOutput`, `UpdateRevertOutput`, and `UpdateCleanOutput`. Helpers cover context timeout, daemon lock check, stash path management, binary replacement, archive extraction, and semver comparison.

Control flow: `check` gets latest release with platform asset and compares versions. `versions` lists releases. `install` refuses to run while daemon lock is active when detectable, resolves target tag, rejects same/older versions unless forced, downloads and verifies archive, extracts `kubo/ipfs`, resolves current executable path, stashes current binary under `$IPFS_PATH/old-bin`, and atomically replaces it or writes a temp fallback on permission errors. `revert` finds newest semver-named stash, reads it, replaces the current binary or writes fallback, then removes restored stash. `clean` deletes semver-named stashes and reports freed bytes.

State and persistence behavior: mutates the local executable and `$IPFS_PATH/old-bin` stash directory. Uses `atomicfile.New` for replacement, `fsrepo.BestKnownPath` for stash location, `dst.Sync` and temp file sync/chmod for durability. It does not open or mutate repo config.

Dependencies and integration points: relies on GitHub helpers in `update_github.go`, Kubo version constants, fsrepo lock detection, migration executable naming for `.exe`, `hashicorp/go-version`, and fsrepo migrations `atomicfile`.

Risks: trust boundary is GitHub API/CDN plus SHA-512 sidecar fetched from adjacent URL; it verifies integrity but not an independent signature. Lock check warnings allow proceeding when repo path/lock cannot be checked. Stashing happens before replacement, so permission fallback can leave an extra backup. Archive extraction limits decompressed binary size but does not inspect file mode or signatures.

Test signals: `update_github_test.go` covers helper hashing/API/archive behavior. CLI/integration tests referenced by comments cover `TEST_KUBO_VERSION` and mock GitHub URL flows.
