# sources/cloud-native/containerd/.github/workflows/windows-hyperv-periodic-trigger.yml

## Purpose
This scheduled/manual trigger delegates to the upstream reusable Windows Hyper-V integration workflow.

## Important APIs, Types, And Functions
It runs daily at 01:00 UTC or manually, checks `github.repository == 'containerd/containerd'`, and uses `containerd/containerd/.github/workflows/windows-hyperv-periodic.yml@main` with Azure secrets.

## Control Flow
The single job invokes the reusable workflow and passes `AZURE_SUB_ID` and `AZURE_CREDS`.

## State And Persistence
State is created by the called workflow, not this trigger.

## Dependencies And Integration Points
It depends on GitHub reusable workflows and Azure secrets. It hard-codes the upstream repository because dynamic `uses` references are not supported.

## Risks
Forks cannot easily reuse this trigger without edits. The called workflow always comes from `main`, so scheduled coverage tracks main workflow changes.

## Test Signals
Successful delegated workflow runs validate the trigger.
