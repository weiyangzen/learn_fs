# File Research: sources/block-storage/mdadm/.github/dependabot.yml

## Purpose
This is a minimal Dependabot configuration for the mdadm GitHub repository. It enables Dependabot version checks for GitHub Actions workflows.

## Behavior
- Uses Dependabot config `version: 2`.
- Defines one update entry for `package-ecosystem: "github-actions"`.
- Scans the repository root directory `/`.
- Schedules checks daily.

## Integration Notes
The file affects only GitHub-hosted dependency automation for workflow action versions. It has no direct runtime or build impact on mdadm itself.

## Risks and Maintenance Notes
Because this tracks GitHub Actions actions from the repository root, changes in `.github/workflows/*` action versions can be proposed automatically. There are no grouping, ignore, or target-branch policies in this file, so all default Dependabot behavior applies.
