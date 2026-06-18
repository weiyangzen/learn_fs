# sources/cloud-native/cri-o/.github/dependabot.yml

Purpose: Dependabot configuration for Go modules and GitHub Actions updates.

Important settings and flow: version 2 config defines daily updates for root `gomod` and repository GitHub Actions. Both use `release-note-none` labels and an open PR limit of 10. Go updates group Kubernetes-related modules under `kubernetes` and all major/minor/patch Go module updates under `gomod`. Actions updates group all update types under `actions`.

State and persistence: creates and updates dependency PRs in GitHub; no runtime state.

Dependencies and integration: depends on Dependabot's GitHub service. PRs then flow through CI, release-note labeling, and review.

Risks: broad grouping can produce large PRs with mixed dependency changes. Daily cadence can create review pressure.

Test signals: Dependabot PR creation and passing CI validate the config.
