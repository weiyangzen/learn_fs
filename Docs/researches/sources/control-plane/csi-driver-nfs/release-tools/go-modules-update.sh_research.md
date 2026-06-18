# sources/control-plane/csi-driver-nfs/release-tools/go-modules-update.sh

Purpose: batch-updates Kubernetes-related Go module dependencies across multiple Kubernetes CSI repositories and opens PRs.

Important arguments and variables: options `-u` for GitHub username and `-v` for Kubernetes version, `MAX_RETRY`, built-in repo/branch list, and required GitHub CLI authentication.

Control flow: logs into `gh`, iterates repository/branch pairs, fetches origin, recreates `module-update-<branch>`, refreshes `release-tools` via git subtree pull with conflict fallback by replacing the subtree from `FETCH_HEAD`, retries `go-get-kubernetes.sh -p <version>` with tidy/vendor cleanup, commits all changes, switches origin URL to the user's fork, runs `make test`, force-pushes, and creates a PR against `kubernetes-csi/<repo>`.

State and persistence behavior: heavily mutates local git checkouts, release-tools subtree, go.mod/go.sum/vendor, branches, remotes, and GitHub PRs.

Dependencies and integration points: depends on `go-get-kubernetes.sh`, git subtree, `gh`, Go tooling, Makefile tests, fork remotes, and a directory containing all listed repos.

Risks: uses `git reset --hard`-like cleanup indirectly through branch recreation and subtree replacement; can delete local update branches; force pushes; PR head uses `module-update-master` even when iterating variable branches, which may be wrong for non-master branches. Interface breakage is explicitly manual.

Test signals: `make test` before push is the local gate; downstream PR CI is final validation.
