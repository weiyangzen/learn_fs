# sources/control-plane/mayastor/.github/workflows/staging-dco.yml

## Purpose
Provides a `DCO` status on pushes to the `staging` branch.

## Important Jobs and Steps
Single `DCO` job on `ubuntu-latest` that echoes `DCO`.

## Control Flow
Triggered only by `push` to `staging`.

## State and Persistence
No state changes.

## Dependencies and Integration Points
Integrates with bors `pr_status = ["commitlint", "DCO"]`, likely satisfying the DCO status for bors-created staging branches.

## Risks
This does not validate signoffs; it only creates a passing status. Real DCO enforcement must exist elsewhere or be accepted as a policy tradeoff.

## Test Signals
Push to staging and confirm a passing `DCO` check appears.
