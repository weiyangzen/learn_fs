# sources/cloud-native/soci-snapshotter/.github/workflows/bump-deps.yml

Purpose: scheduled/manual automation that runs repository dependency bump script and opens a PR.

Important APIs/types/functions: weekly Tuesday cron, workflow dispatch, Go setup, `./scripts/bump-deps.sh`, and `peter-evans/create-pull-request`.

Control flow: runs only for the upstream repository or manual dispatch, checks out code, sets Go version, runs bump script, and creates a signed-off PR labeled `dependencies`.

State and persistence: creates commits/branches/PRs through GitHub token write permissions.

Dependencies/integration: tied to repo scripts and Dependabot policy.

Risks: generated PR body says checks require close/reopen, so automated PRs may not be fully self-validating. Upstream repository guard prevents fork noise.

Test signals: scheduled run or manual dispatch producing a dependency PR.
