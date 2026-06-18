## sources/control-plane/longhorn/.github/workflows/scorecards.yml

### Purpose
`scorecards.yml` runs OpenSSF Scorecard supply-chain security analysis.

### Important APIs, Types, And Functions
It triggers on branch protection rule changes, weekly schedule, and pushes to `master`. It sets default read-only permissions, grants the job `security-events: write` and `id-token: write`, checks out without persisted credentials, runs `ossf/scorecard-action` producing SARIF, uploads the SARIF artifact, and uploads it to GitHub code scanning.

### Control Flow
Scorecard writes `results.sarif`; subsequent steps publish it as an artifact and code-scanning result.

### State, Persistence, And Dependencies
It creates workflow artifacts and code-scanning alerts. Dependencies are pinned checkout, scorecard, upload-artifact, and codeql upload actions.

### Integration Points
Results feed GitHub security/code scanning and OpenSSF public score publication.

### Risks
`publish_results: true` exposes public score data. Branch protection checks may require optional PAT for full public-branch analysis, currently commented out.

### Test Signals
Successful scheduled run with uploaded SARIF and visible code-scanning results validates the workflow.
