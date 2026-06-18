<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/.github/workflows/auto-close-issues.yml -->
# sources/cloud-native/containers-storage/.github/workflows/auto-close-issues.yml

- Purpose: GitHub Actions workflow that closes newly opened issues because the repository has migrated to `containers/container-libs`.
- Important behavior: Triggers on `issues` opened events, grants `issues: write`, sets `GH_TOKEN`, `REPO`, and `ISSUE`, and runs `gh issue close --repo "$REPO" --comment "...migrated..." "$ISSUE"`.
- Control flow and state: Event-triggered job on `ubuntu-latest` mutates GitHub issue state and posts the migration comment.
- Dependencies and integration: Uses GitHub CLI and `secrets.GITHUB_TOKEN`; integrates with repository migration policy.
- Risks: All newly opened issues are closed unconditionally, so any exception must be handled by changing the workflow.
- Test signals: Workflow logs and the issue timeline showing the migration close comment.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/.github/workflows/auto-close-issues.yml -->
