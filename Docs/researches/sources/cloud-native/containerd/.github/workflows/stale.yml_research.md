# sources/cloud-native/containerd/.github/workflows/stale.yml

## Purpose
This workflow marks and closes stale issues and pull requests that already carry labels indicating they need more information, updates, or rebasing.

## Important APIs, Types, And Functions
It runs `actions/stale` with 90 days before stale, 7 days before close, `any-of-labels` limited to `status/more-info-needed,status/needs-update,needs-rebase`, custom issue/PR messages, and dry-run behavior on PRs changing the workflow.

## Control Flow
Scheduled upstream runs request issue and pull-request write permissions and execute the stale action. PR-triggered runs operate in debug-only mode.

## State And Persistence
The workflow can add stale labels/comments and close issues/PRs.

## Dependencies And Integration Points
It integrates with GitHub issue/PR metadata and containerd triage labels.

## Risks
Label names are policy-critical. Misconfiguration could close active work, but the workflow is constrained to specific labels and dry-runs on workflow PRs.

## Test Signals
Scheduled action logs and observed stale/close comments on qualifying issues/PRs are the main signals.
