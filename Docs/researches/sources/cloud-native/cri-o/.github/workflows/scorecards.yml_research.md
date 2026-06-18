# sources/cloud-native/cri-o/.github/workflows/scorecards.yml

Purpose: OpenSSF Scorecard supply-chain security workflow.

Important jobs and flow: triggers on branch protection changes, weekly schedule, and pushes to main. It uses read-all default permissions, grants security-events and id-token for the analysis job, checks out without persisted credentials, runs `ossf/scorecard-action`, writes `results.sarif`, publishes public results, uploads the SARIF artifact, and uploads to GitHub code scanning.

State and persistence: produces external OpenSSF results and GitHub code scanning entries; artifact retention is five days.

Dependencies and integration: same Scorecard ecosystem as `osff.yml`, but with a different workflow name and slightly newer SARIF upload action.

Risks: duplicate Scorecard workflows can waste CI time and create duplicate code scanning alerts. Publish settings expose public scorecard results for public repos.

Test signals: successful SARIF artifact and code scanning upload.
