<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/codeql.yml -->
# sources/cloud-native/moby/.github/workflows/codeql.yml

## Purpose
Runs GitHub CodeQL analysis for Go on pushes, PRs, tags, weekly schedule, and manual-equivalent branch events.

## Important APIs, Types, And Functions
- Triggers include release branches, `v*`, `docker-v*`, `api/v*`, and `client/v*` tags, PRs, and Thursday 09:00 UTC schedule.
- Uses Go `1.26.4`.
- Steps use checkout, setup-go, CodeQL init, autobuild, and analyze.
- Grants `security-events: write` only to the CodeQL job.

## Control Flow
The single job checks out with shallow history depth 2, initializes CodeQL for Go, lets CodeQL autobuild the project, and uploads analysis results with category `/language:go`.

## State And Persistence
Analysis results persist in GitHub code scanning. The runner build state is temporary.

## Dependencies And Integration Points
Integrates with GitHub Advanced Security/CodeQL and Go setup. It is separate from `govulncheck` in `ci.yml`.

## Risks And Edge Cases
Autobuild may miss project-specific build tags or generated code if CodeQL cannot infer the full build. The job timeout is only 10 minutes, which can be tight for large Go projects.

## Test Signals
Successful CodeQL analysis upload and code-scanning alerts are the primary signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/.github/workflows/codeql.yml -->
