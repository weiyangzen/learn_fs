# sources/distributed-fs/ipfs-kubo/.github/workflows/stale.yml

## Purpose
This scheduled/manual workflow delegates stale issue handling to a unified reusable workflow.

## Important APIs, Types, And Functions
It grants write permissions to issues and pull requests and invokes `reusable-stale-issue.yml@v1`.

## Control Flow
The workflow runs daily at midnight UTC or by manual dispatch. The downstream reusable workflow owns all labeling/commenting/closing policy.

## State And Persistence Behavior
It can mutate GitHub issue and PR metadata but does not modify repository files.

## Dependencies And Integration Points
It integrates with GitHub Issues and PR APIs through the reusable workflow and token permissions.

## Risks And Test Signals
Risks include incorrect stale policy inherited from the external workflow and permission drift. Signals are successful scheduled runs and expected stale issue transitions.
