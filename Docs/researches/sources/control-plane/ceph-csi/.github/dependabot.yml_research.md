<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/dependabot.yml -->
# sources/control-plane/ceph-csi/.github/dependabot.yml

Purpose: Dependabot schedule and grouping policy for Go modules and GitHub Actions.
Important surface: weekly updates for root, `/actions/retest`, `/api`, `/e2e`, and GitHub Actions; dependency groups for Golang, Kubernetes, and GitHub dependencies; Kubernetes component modules are ignored in root due to `k8s.io/kubernetes` constraints.
Control flow/state: declarative GitHub service config. It labels generated PRs with `rebase` and skip labels for e2e/multi-arch where appropriate and prefixes commit messages with `rebase`.
Dependencies/integration: feeds CI/Mergify rules that understand `rebase`, `ci/skip/e2e`, and `ci/skip/multi-arch-build`.
Risks/test signals: ignored Kubernetes modules require manual coordinated updates; grouped updates can obscure a single failing dependency. Dependabot PR creation and CI outcomes are the signals.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/.github/dependabot.yml -->
