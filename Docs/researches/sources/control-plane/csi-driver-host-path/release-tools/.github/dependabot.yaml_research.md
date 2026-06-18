## sources/control-plane/csi-driver-host-path/release-tools/.github/dependabot.yaml

Purpose: configures Dependabot for the csi-release-tools repository copy. It enables beta ecosystems and checks GitHub Actions in the repository root daily.

Control flow is declarative: Dependabot opens up to ten action-update PRs and labels them `area/dependency`, `release-note-none`, and `ok-to-test`. There is no runtime state besides GitHub's dependency update queue.

Dependencies and integration points are GitHub Dependabot and the workflows in `.github/workflows`. Risks include action churn from daily updates and the high PR limit compared with application repos. Test signal is GitHub platform validation of the YAML and actual Dependabot PR creation.
