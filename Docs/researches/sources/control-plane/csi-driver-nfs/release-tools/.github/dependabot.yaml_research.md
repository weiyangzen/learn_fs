# sources/control-plane/csi-driver-nfs/release-tools/.github/dependabot.yaml

Purpose: configures Dependabot for the release-tools repository copy.

Important configuration: uses Dependabot `version: 2`, enables beta ecosystems, and defines one update rule for the `github-actions` ecosystem in the root directory.

Control flow: Dependabot runs daily, labels PRs with `area/dependency`, `release-note-none`, and `ok-to-test`, and limits open dependency PRs to ten.

State and persistence behavior: state is maintained by GitHub Dependabot outside the repository; this file only declares desired scheduling and labels.

Dependencies and integration points: integrates with GitHub Actions workflow dependency scanning and Kubernetes project labeling conventions.

Risks: only GitHub Actions dependencies are covered; Go modules, Docker images, and other ecosystems are not updated by this config. Labels must exist or be acceptable in target repos.

Test signals: no local tests. Validation happens when GitHub parses the config and Dependabot starts opening PRs.
