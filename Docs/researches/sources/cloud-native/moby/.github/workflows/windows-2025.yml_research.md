<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/windows-2025.yml -->
# sources/cloud-native/moby/.github/workflows/windows-2025.yml

## Purpose
Push/PR/manual wrapper for the reusable Windows workflow on `windows-2025`, running graphdriver and snapshotter modes without coverage upload.

## Important APIs, Types, And Functions
- Triggers on manual dispatch, pushes to master/release branches, and PRs.
- Reuses `.dco.yml` and `.windows.yml`.
- Matrix `storage` includes `graphdriver` and `snapshotter`.
- Passes `os: windows-2025` and `send_coverage: false`.

## Control Flow
After DCO validation, the wrapper delegates to `.windows.yml` for each storage mode unless a PR has `ci/validate-only`.

## State And Persistence
Child workflow produces build/test artifacts; no Codecov coverage is uploaded because `send_coverage` is false.

## Dependencies And Integration Points
Provides current Windows PR coverage through the shared workflow. It uses the `ltsc2025` base image selected in `.windows.yml`.

## Risks And Edge Cases
Windows 2025 runner/image behavior can differ from Windows 2022. Disabling coverage keeps PR runs lighter but means Windows coverage comes from other lanes.

## Test Signals
Signals are child workflow build, unit, integration, daemon log, and report summary results across both storage modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/windows-2025.yml -->
