# sources/compression/zstd/.github/workflows/scorecards.yml

Purpose: OpenSSF Scorecards supply-chain security analysis for the canonical `facebook/zstd` repository.

Important behavior: triggers on branch protection rule changes, weekly schedule, and pushes to `dev`. The job is gated by `github.repository == 'facebook/zstd'`, checks out code without persisted credentials, runs `ossf/scorecard-action` to produce SARIF and publish public results, uploads the SARIF as an artifact with five-day retention, and uploads it to GitHub code scanning.

State, dependencies, and integration: depends on GitHub security-events/id-token permissions, Scorecards action, artifact upload, and CodeQL SARIF upload. Generated state is `results.sarif`.

Risks and test signals: this is not a build test; it reports repository security posture. Action SHAs are pinned, which supports supply-chain integrity. Failures or score regressions signal branch protection, pinned dependency, token, or workflow-hardening issues.
