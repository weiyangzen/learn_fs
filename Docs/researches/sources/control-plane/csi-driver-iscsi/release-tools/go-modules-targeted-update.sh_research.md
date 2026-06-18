# sources/control-plane/csi-driver-iscsi/release-tools/go-modules-targeted-update.sh

Purpose: batch-updates a selected list of Go modules across selected CSI sidecar release branches and opens PRs.

Important APIs and types: variables `org`, `modules`, and `releases` define target organization, module versions, and `repo branch` pairs. The script requires `GITHUB_USER`.

Control flow: for each release row, fetches upstream, recreates `module-update-<branch>`, checks out from `upstream/<branch>`, runs `go get` for each configured module, tidies and vendors, commits all changes, force pushes, and opens a PR with the module list in the body.

State and persistence: mutates local repos, branches, `go.mod`, `go.sum`, `vendor`, remote branches, and GitHub PRs.

Dependencies and integration: depends on `gh`, git remotes, Go tooling, vendored repos, and sibling checkout layout.

Risks: release list is commented out by default. It does not resolve API incompatibilities after dependency bumps. `set -x` reveals commands. The `if [ "$repo" != "#" ]` check does not robustly skip commented lines unless parsed exactly.

Test signals: successful build/tests after PR creation, clean vendor diff, and CI on generated PRs.
