<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/dependabot.yml -->

# sources/distributed-fs/ipfs-kubo/.github/dependabot.yml


## Purpose
Dependabot configuration for GitHub Actions and Go modules in Kubo.


## Important APIs, Types, and Functions
Defines weekly github-actions updates, monthly gomod updates at root, PR limit, dependency label, ignored datastore wrapper dependencies, and grouped update families for IPFS, libp2p, golang-x, OpenTelemetry, Prometheus, and Uber packages.


## Control Flow
Dependabot reads this schedule/grouping to open dependency PRs; companion workflow dependabot-tidy handles multi-module tidy.


## State and Persistence Behavior
State persists as Dependabot PRs and labels, not runtime application state.


## Dependencies and Integration Points
Depends on Dependabot v2 schema, Go module dependency names, and repo label conventions.


## Risks and Test Signals
Risks include ignored dependencies going stale and groups becoming too broad. Signal controls dependency maintenance cadence and PR shape.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/dependabot.yml -->
