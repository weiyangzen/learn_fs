# sources/cloud-native/containerd/.github/workflows/links.yml

## Purpose
This workflow checks Markdown links in the repository.

## Important APIs, Types, And Functions
It runs on manual dispatch, daily schedule, and PR changes to the workflow itself. It uses `lycheeverse/lychee-action` with arguments excluding `vendor` and `releases`, a 30-second timeout, markdown output, and job summary.

## Control Flow
For the upstream repository, the job checks out code and runs Lychee against `./**/*.md`, failing on broken links.

## State And Persistence
No persistent repository state exists; results are workflow status and job summary.

## Dependencies And Integration Points
It integrates with Markdown documentation health and external URL availability.

## Risks
Scheduled link checks can fail due to transient external outages. PRs changing Markdown do not trigger this workflow unless the workflow file changes.

## Test Signals
Passing scheduled runs and Lychee summaries are the evidence.
