# sources/control-plane/rook/.github/workflows/scorecards.yml

## Purpose

Runs OpenSSF Scorecard supply-chain analysis and uploads results as SARIF.

## Important APIs, Types, and Functions

The `analysis` job triggers on branch protection changes, weekly schedule, and pushes to `master`. It uses read-all default permissions, elevates `security-events: write` and `id-token: write`, runs `ossf/scorecard-action` with SARIF output and `publish_results: true`, uploads the SARIF artifact, and uploads SARIF to code scanning.

## Control Flow

The workflow checks out without persisted credentials, runs Scorecard, stores `results.sarif`, uploads it as a short-retention artifact, and sends it to GitHub code scanning.

## State and Persistence Behavior

Persistent outputs are OpenSSF published results, GitHub artifact, and code scanning alerts. The repo worktree is not modified.

## Dependencies and Integration Points

It integrates with OpenSSF Scorecard, GitHub code scanning, branch protection checks, and public Scorecard result publishing.

## Risks and Edge Cases

Publishing results is public for public repositories. Some Scorecard checks need additional tokens for complete branch-protection analysis, but the optional PAT is commented out.

## Test Signals

Success produces a SARIF artifact and code-scanning upload; the Scorecard score and findings are the primary security signal.
