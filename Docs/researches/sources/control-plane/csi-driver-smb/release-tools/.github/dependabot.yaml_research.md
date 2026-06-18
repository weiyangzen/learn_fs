<!-- BEGIN_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/.github/dependabot.yaml -->
# sources/control-plane/csi-driver-smb/release-tools/.github/dependabot.yaml

Purpose: Configures Dependabot for the release-tools repository copy to update GitHub Actions dependencies.

Important configuration: Uses schema `version: 2`, enables beta ecosystems, watches `github-actions` in the repository root daily, applies labels `area/dependency`, `release-note-none`, and `ok-to-test`, and limits open pull requests to ten.

Control flow: GitHub Dependabot consumes this declarative file; there is no runtime code.

State and persistence behavior: Dependabot creates PRs against repository workflow references. The file itself persists policy only.

Dependencies and integration points: Integrates with GitHub Actions, repository labeling conventions, and Kubernetes CSI PR automation.

Risks: The directory is `/`, so it assumes workflows live at the root of the repo that imports release-tools. Updates are limited to actions, not Go, Docker, or Python dependencies.

Test signals: No local tests; behavior is observable through Dependabot PRs.
<!-- END_FILE_RESEARCH: sources/control-plane/csi-driver-smb/release-tools/.github/dependabot.yaml -->
