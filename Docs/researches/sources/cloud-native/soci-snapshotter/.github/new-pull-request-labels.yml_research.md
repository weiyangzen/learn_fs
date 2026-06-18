# sources/cloud-native/soci-snapshotter/.github/new-pull-request-labels.yml

Purpose: labeler configuration for new pull requests.

Important APIs/types/functions: maps changed file globs to labels `documentation`, `github_actions`, `go`, `testing`, `benchmarking`, and `dependencies`.

Control flow: `actions/labeler` applies or syncs labels based on changed files.

State and persistence: mutates PR labels in GitHub.

Dependencies/integration: consumed by `new-pull-requests.yml` under `pull_request_target`.

Risks: broad `.github/**` and `scripts/**` labeling as `github_actions` may over-label script-only changes. Label names must exist or be creatable by the action.

Test signals: opening PRs with representative file changes validates labels.
