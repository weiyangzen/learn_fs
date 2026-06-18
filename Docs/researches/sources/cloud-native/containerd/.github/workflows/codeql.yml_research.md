# sources/cloud-native/containerd/.github/workflows/codeql.yml

## Purpose
This workflow runs GitHub CodeQL analysis for containerd on pushes and pull requests to main and release branches.

## Important APIs, Types, And Functions
It uses checkout, the local Go install action, `github/codeql-action/init`, a build step that installs `libseccomp-dev` and runs `make`, and `github/codeql-action/analyze`. It grants `security-events: write`.

## Control Flow
The job only runs for `github.repository == 'containerd/containerd'`, checks out code, installs Go, initializes CodeQL, builds the project, and uploads analysis.

## State And Persistence
Persistent output is CodeQL SARIF/security events in GitHub code scanning.

## Dependencies And Integration Points
It integrates with GitHub Advanced Security, the Makefile default build, and libseccomp build dependency.

## Risks
Only Ubuntu is scanned despite comments mentioning other platforms. Build failures block analysis. It runs only in the upstream repository, not forks.

## Test Signals
Successful CodeQL workflow runs and uploaded code-scanning alerts are validation.
