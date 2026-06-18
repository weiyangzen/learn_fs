# sources/cloud-native/soci-snapshotter/.github/workflows/review-dependencies.yml

Purpose: runs GitHub dependency review for Go dependency changes.

Important APIs/types/functions: pull_request trigger for `go.*` and `cmd/go.*`; `actions/dependency-review-action@v5`; config file `.github/dependency-review-config.yml`; `comment-summary-in-pr: always`.

Control flow: checks out PR code and invokes dependency review with license policy, writing PR comments.

State and persistence: comments on PRs and may fail checks; no code writes.

Dependencies/integration: paired with dependency review config and Go module files.

Risks: only Go module path changes trigger it; Docker/GitHub Actions dependency changes are governed elsewhere.

Test signals: PRs modifying `go.mod`/`go.sum` should produce dependency review comments.
