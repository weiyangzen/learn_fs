# sources/control-plane/external-snapshotter/release-tools/.github/dependabot.yaml

Purpose: Dependabot configuration for the release-tools repository's GitHub Actions dependencies.

Important keys: `version: 2`, `enable-beta-ecosystems: true`, one update rule for `package-ecosystem: github-actions`, root directory `/`, daily schedule, labels `area/dependency`, `release-note-none`, and `ok-to-test`, and open PR limit `10`.

Control flow: GitHub Dependabot periodically scans workflow actions and opens dependency update PRs under the configured labels.

State and persistence: stored as repository configuration; resulting PRs are persisted in GitHub.

Dependencies and integration: integrates GitHub Dependabot and repository triage conventions.

Risks and test signals: risks are noisy daily PRs or stale action pins if Dependabot cannot parse pinned SHAs. Validation signal is Dependabot successfully opening labeled action-update PRs.
