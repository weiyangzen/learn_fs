# sources/distributed-fs/ipfs-kubo/repo/fsrepo/misc.go

Purpose: resolves the best-known fsrepo path for callers that need the default repo location.

Important APIs and control flow: `BestKnownPath` starts from `config.DefaultPathRoot`, overrides it with `IPFS_PATH` (`config.EnvDir`) when set, expands `~`, and returns the expanded path.

State and persistence: no file writes; reads environment and home-directory state.

Dependencies and integration: used by code that needs a repo path without opening the repo. Depends on Kubo config constants and `fsutil.ExpandHome`.

Risks and test signals: no direct test in this subset. Errors only come from home expansion. It does not check existence, initialization, or writability; callers needing those properties must use fsrepo/migration path checks.
