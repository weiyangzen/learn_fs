<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/windows-2022.yml -->
# sources/cloud-native/moby/.github/workflows/windows-2022.yml

## Purpose
Scheduled/manual wrapper for the reusable Windows workflow on `windows-2022`, running both graphdriver and snapshotter storage modes with coverage upload enabled.

## Important APIs, Types, And Functions
- Triggers daily at `0 10 * * *` and via `workflow_dispatch`.
- Reuses `.dco.yml` and `.windows.yml`.
- Matrix `storage` includes `graphdriver` and `snapshotter`.
- Passes `os: windows-2022` and `send_coverage: true`.

## Control Flow
DCO validation runs, then the `run` job delegates to `.windows.yml` for each storage mode with Codecov token forwarding.

## State And Persistence
Child workflow publishes build/test artifacts and coverage. This wrapper has no additional state.

## Dependencies And Integration Points
Uses Windows Server 2022 GitHub-hosted runners and the shared Windows workflow. Coverage behavior integrates with `.codecov.yml`.

## Risks And Edge Cases
It is not triggered on PRs or pushes, so Windows 2022 coverage is scheduled/manual. The inherited PR validate-only condition is effectively redundant for current triggers.

## Test Signals
Signals are child workflow results for both storage modes and Codecov uploads.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/windows-2022.yml -->
