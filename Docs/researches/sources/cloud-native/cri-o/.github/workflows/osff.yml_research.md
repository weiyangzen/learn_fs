# sources/cloud-native/cri-o/.github/workflows/osff.yml

Purpose: OpenSSF Scorecard workflow named `ossf`.

Important jobs and flow: triggers on branch protection rule changes, weekly schedule, and pushes to main. It checks out code without persisted credentials, runs `ossf/scorecard-action` to produce SARIF, publishes public results, uploads the SARIF artifact with short retention, and uploads SARIF to GitHub code scanning.

State and persistence: persists Scorecard results externally in OpenSSF and GitHub code scanning; stores a temporary workflow artifact.

Dependencies and integration: depends on GitHub Actions, OpenSSF Scorecard, upload-artifact, and CodeQL SARIF upload.

Risks: this overlaps with `scorecards.yml`, potentially duplicating supply-chain checks. Pinned action versions reduce but do not eliminate action supply-chain risk.

Test signals: successful SARIF generation/upload and visible code scanning results.
