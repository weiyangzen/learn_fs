# sources/control-plane/beegfs-csi-driver/release-tools/go-modules-update.sh

Purpose: Batch automation for updating Kubernetes CSI sidecar repositories to a target Kubernetes dependency version and creating PRs.

Important APIs/types/functions: Accepts `-u` username and `-v` version. Uses `MAX_RETRY=10`. Iterates a hardcoded list of CSI repos and branches. Calls `gh auth login`, `git subtree pull` for release-tools, `release-tools/go-get-kubernetes.sh -p`, `go mod tidy`, `go mod vendor`, `make test`, git push, and `gh pr create`.

Control flow: For each repo/branch, it fetches origin, recreates a `module-update-<branch>` branch from `origin/<branch>`, refreshes release-tools via subtree. On subtree conflicts it replaces `release-tools` with an archive of `FETCH_HEAD` and commits the merge message. It retries Kubernetes dependency update with tidy/vendor cleanup, commits all changes, points origin at the user's fork, tests, force-pushes, and opens a PR against Kubernetes CSI upstream.

State and persistence: Performs extensive git mutations across many repositories: branch deletion/creation, subtree commits, module/vendor file edits, all-file commits, remote URL changes, force pushes, and PR creation.

Dependencies and integration points: Requires local checkouts of all listed repos, GitHub CLI, authenticated GitHub access, Go, Makefile test targets, and `go-get-kubernetes.sh`.

Risks: Highly destructive if run in a working tree with local changes. The PR head is hardcoded as `module-update-master` even inside a loop over branches, which may be wrong for non-master branches. It changes `origin` remote URL permanently. It does not resolve API incompatibilities automatically despite updating dependencies.

Test signals: Runs `make test` before pushing. Success is also visible through pushed branches and created PRs.
