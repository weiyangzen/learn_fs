# sources/control-plane/csi-driver-nfs/.github/dependabot.yaml

Purpose: configures automated dependency PRs for the NFS driver.

Important APIs and types: three Dependabot ecosystems: `gomod` at `/`, `github-actions` at `/`, and `docker` at `./`. Go and GitHub Actions have daily schedules and PR limit 1; Docker runs daily at 01:00 Asia/Shanghai with cleanup label.

Control flow: Dependabot monitors dependencies and opens PRs with standard labels.

State and persistence: generated PRs and dependency diffs in GitHub.

Dependencies and integration: integrates with GitHub labels, Go modules, workflow actions, and Dockerfile base image updates.

Risks: low PR limits serialize updates and may delay security updates when queues are busy. Docker PRs do not specify an open PR limit.

Test signals: Dependabot PRs and CI outcomes.
