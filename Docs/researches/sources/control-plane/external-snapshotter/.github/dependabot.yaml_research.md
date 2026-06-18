# sources/control-plane/external-snapshotter/.github/dependabot.yaml

## Purpose
Dependabot configuration for automated dependency update pull requests. It groups Go module updates and GitHub Actions updates, applies Kubernetes project labels, and limits open PR volume.

## Important APIs, Types, and Functions
- `version: 2` and `enable-beta-ecosystems: true`.
- Go module update entry for directory `/`, scheduled weekly.
- GitHub Actions update entry for directory `/`, scheduled daily.
- Go module dependency groups: `golang-dependencies`, `k8s-dependencies`, and catch-all `github-dependencies`.
- Labels: `area/dependency`, `release-note-none`, and `ok-to-test`.

## Control Flow
Dependabot scans according to each ecosystem schedule, groups updates by pattern, and opens at most ten pull requests per ecosystem. The catch-all GitHub group excludes dependencies already matched by Go/Kubernetes/CSI groups.

## State and Persistence Behavior
Dependabot maintains PR state in GitHub. This file itself stores no runtime state, but changes to grouping directly alter future PR batching and review load.

## Dependencies and Integration Points
Integrates with GitHub Dependabot, repository labels, branch protection, and CI/Prow label conventions. It targets `gomod` and `github-actions` ecosystems.

## Risks
Broad grouping can combine unrelated dependency changes, which may obscure regressions. Pinned or generated dependencies in the client module may require extra vendor verification beyond Dependabot's root module scan.

## Test Signals
Signals are Dependabot PR creation, expected labels, grouped dependency names, and successful downstream CI including vendor checks.
