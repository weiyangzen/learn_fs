# sources/cloud-native/nydus/.github/dependabot.yml

## Purpose
This Dependabot config schedules weekly dependency update checks for Go modules, Cargo crates, and GitHub Actions.

## Important APIs, Types, and Functions
The config is version `2` and has three update entries:
- `gomod` in `/contrib/`
- `cargo` in `/`
- `github-actions` in `/`
All run weekly.

## Control Flow
Dependabot scans the configured ecosystems on its schedule and opens update PRs when newer compatible versions are found.

## State and Persistence
Dependabot state lives in GitHub. The repository receives PRs and updated lock/config files when changes are proposed.

## Dependencies and Integration Points
This integrates with Cargo workspace dependencies, Go contrib modules, and workflow action versions. The smoke, release, convert, benchmark, and e2e workflows are the primary CI gates for resulting PRs.

## Risks and Edge Cases
Only `/contrib/` is scanned for Go modules, so Go modules elsewhere would be missed unless covered by that root. Weekly batching can create large update PRs. No groups, ignore rules, or labels are configured.

## Test Signals
Successful Dependabot PR creation and CI pass/fail on those PRs are the test signals.
