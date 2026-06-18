## sources/control-plane/csi-driver-iscsi/.github/dependabot.yaml

Purpose: configures Dependabot for csi-driver-iscsi dependencies. It checks Go modules, GitHub Actions, and Dockerfile dependencies daily.

Control flow is declarative. Gomod and actions checks run at root with one open PR each; Docker checks run in `./` daily at 01:00 Asia/Shanghai and add `kind/cleanup` in addition to dependency labels.

State is GitHub Dependabot queue and PRs. Dependencies are GitHub's gomod/actions/docker ecosystems. Risks include low PR limit causing backlog, daily Docker churn, and timezone-specific scheduling. Test signal is Dependabot PR creation and downstream CI.
