<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/dependabot-tidy.yml -->

# sources/distributed-fs/ipfs-kubo/.github/workflows/dependabot-tidy.yml


## Purpose
GitHub Actions workflow that tidies all Go modules on Dependabot PRs.


## Important APIs, Types, and Functions
Triggers on pull_request_target opened/synchronize and manual dispatch with pr_number. It discovers PR branch with gh, checks it out with write token, sets up Go, runs make mod_tidy, commits and pushes changes if git status is dirty.


## Control Flow
The workflow mutates Dependabot branches to keep secondary go.sum files in sync. It only runs for dependabot[bot] or manual dispatch.


## State and Persistence Behavior
State is committed tidy changes on PR branches and workflow outputs for PR number/branch/modified.


## Dependencies and Integration Points
Depends on pull_request_target permissions, secrets.GITHUB_TOKEN, gh CLI, actions/checkout/setup-go, make mod_tidy, and git identity config.


## Risks and Test Signals
Risks include elevated pull_request_target context and branch trust assumptions, though actor gating reduces exposure. Signal prevents CI failures from multi-module dependency drift.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ipfs-kubo/.github/workflows/dependabot-tidy.yml -->
