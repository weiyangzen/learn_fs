# sources/control-plane/csi-lib-utils/release-tools/.github/dependabot.yaml

## Purpose

This Dependabot configuration enables automated dependency update pull requests for GitHub Actions used by the `release-tools` repository. It opts into beta ecosystems, scans the repository root daily, and caps open Dependabot PRs at ten.

## Important Behavior

The only configured `package-ecosystem` is `github-actions` with `directory: "/"`. Dependabot-created PRs get the labels `area/dependency`, `release-note-none`, and `ok-to-test`, which integrate with Kubernetes CSI triage and Prow/GitHub automation conventions.

## State, Dependencies, and Integration

There is no runtime state. The file is interpreted by GitHub Dependabot. It directly affects update cadence for workflow pins such as checkout, codespell, Trivy, and other actions in this repository.

## Risks and Test Signals

The main risk is update noise or action breakage from daily PRs. The explicit PR limit reduces queue growth, and labels make updates easier to route. Validation is indirect: GitHub accepts or rejects the YAML, and generated PRs exercise CI workflows.
