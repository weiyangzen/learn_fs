# sources/cloud-native/cri-o/scripts/dependencies/dependencies.go

This Go script generates and optionally publishes a CRI-O dependency report. It writes `dependencies.md` under a requested output path and, when `GITHUB_TOKEN` is present, commits and pushes the report to the `gh-pages` branch.

Important APIs are `main` and `run`. `run` creates the output directory, disables `GOSUMDB`, executes `go list --mod=mod -u -m --json all`, stores the module JSON in a temp file, pipes it through `./build/bin/go-mod-outdated` twice for direct outdated and all dependencies, obtains the current Git HEAD, writes a Markdown report with links, then optionally checks out `gh-pages`, writes the report at repo root, commits, rebases, and retries push up to ten times. State/persistence includes temp module JSON, output report file, branch checkout, git commit, and remote push.

Dependencies include logrus, release-sdk git helpers, release-utils command piping, the Go toolchain, `go-mod-outdated`, and GitHub credentials. Integration points are CI, `gh-pages`, and dependency visibility. Risks include leaving branch state changed if deferred checkout errors are hidden, use of `os.Exit(0)` inside `run` when token is absent, unremoved temp files, network/toolchain dependence, and mutating module resolution because `--mod=mod` can update module files. There are no direct tests in this subset.
