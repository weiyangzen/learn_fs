# sources/cloud-native/stargz-snapshotter/.github/dependabot.yml

## Purpose
This Dependabot configuration automates dependency update pull requests for Go modules, Docker base images, and GitHub Actions in stargz-snapshotter.

## Important APIs, Types, and Functions
It uses Dependabot config version 2. Go module updates cover `/estargz`, `/ipfs`, `/`, and `/cmd`, run daily, ignore the internal estargz dependency that is manually upgraded on release, and group dependencies into golang-x, google-golang, containerd, opencontainers, k8s, and a catch-all gomod group. Docker and GitHub Actions updates also run daily.

## Control Flow, State, and Persistence
Dependabot reads this YAML in GitHub infrastructure and opens update PRs. There is no runtime code state.

## Dependencies and Integration Points
It integrates with GitHub Dependabot and repository module layout. Grouping reduces PR noise and keeps ecosystem updates coherent.

## Risks and Test Signals
Daily grouped updates can still create broad PRs that require CI capacity. The explicit ignore for estargz protects release-controlled coupling. The catch-all group uses exclude patterns, so missed ecosystem prefixes may group unrelated modules.
