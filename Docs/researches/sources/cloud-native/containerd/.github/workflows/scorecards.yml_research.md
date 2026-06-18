# sources/cloud-native/containerd/.github/workflows/scorecards.yml

## Purpose
This workflow runs OSSF Scorecard supply-chain security analysis.

## Important APIs, Types, And Functions
It triggers on branch protection rule changes, weekly schedule, and pushes to main. It uses read-all default permissions, grants `security-events: write` and `id-token: write` for analysis, runs `ossf/scorecard-action`, uploads `results.sarif`, and uploads SARIF to code scanning.

## Control Flow
The job checks out code without persisting credentials, runs Scorecard with SARIF output and `publish_results: false`, uploads the SARIF artifact for five days, and uploads it to GitHub code scanning.

## State And Persistence
Persistent outputs are code-scanning results and short-lived SARIF artifacts.

## Dependencies And Integration Points
It integrates with OSSF Scorecard, GitHub code scanning, and repository branch protection/security posture.

## Risks
Only default branch is supported per comment. Scorecard checks can change behavior as the action evolves, although the action is pinned by SHA.

## Test Signals
Successful scheduled runs and visible SARIF/code scanning results validate it.
