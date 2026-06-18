# sources/control-plane/rook/.github/dependabot.yml

Purpose: Dependabot configuration for Rook dependencies.

Important configuration: version 2 with beta ecosystems enabled. It checks Go modules in `/` weekly and groups updates into `golang-dependencies` for `github.com/golang*`, `k8s-dependencies` for `k8s.io*` and `sigs.k8s.io*`, and `github-dependencies` for `github.com*`. It also checks GitHub Actions dependencies in `/` weekly.

State, dependencies, and integration: Dependabot stores update state in GitHub and opens PRs based on this file. It integrates with `go.mod` at the repository root and workflows under `.github/workflows/*.yml`.

Risks and test signals: the broad `github.com*` group may overlap with the more specific `github.com/golang*` pattern depending on Dependabot grouping precedence. Weekly cadence can batch large update sets. Signals are generated Dependabot PRs grouped as configured and action-version update PRs.
