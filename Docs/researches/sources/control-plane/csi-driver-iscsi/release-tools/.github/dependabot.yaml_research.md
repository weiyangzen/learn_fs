# sources/control-plane/csi-driver-iscsi/release-tools/.github/dependabot.yaml

Purpose: configures Dependabot for the release-tools repository copy to update GitHub Actions dependencies daily.

Important APIs and types: YAML uses Dependabot `version: 2`, `enable-beta-ecosystems: true`, a single `updates` item for `package-ecosystem: github-actions`, root directory `/`, daily schedule, labels, and an open PR limit of 10.

Control flow: GitHub Dependabot reads this declarative config and opens dependency update PRs for workflow actions. There is no runtime script logic.

State and persistence: state lives in GitHub Dependabot PRs and repository workflow files. This file only stores policy.

Dependencies and integration: integrates with GitHub Actions and project labels `area/dependency`, `release-note-none`, and `ok-to-test`.

Risks: broad daily updates with a PR limit of 10 can create maintenance churn. Only GitHub Actions are covered, not Go, Docker, or Python dependencies.

Test signals: effectiveness is visible through generated Dependabot PRs and CI on those PRs.
