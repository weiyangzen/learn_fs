<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/.github/workflows/auto-close-prs.yml -->
# sources/cloud-native/containers-storage/.github/workflows/auto-close-prs.yml

- Purpose: GitHub Actions workflow that closes newly opened pull requests against `main` because development moved to `containers/container-libs`.
- Important behavior: Triggers on `pull_request_target` opened events for `main` and uses `superbrothers/close-pull-request` pinned to commit `9c18513d...` with a migration comment.
- Control flow and state: Event-triggered job on `ubuntu-latest` mutates PR state and comments through the third-party action.
- Dependencies and integration: Relies on `pull_request_target` permissions and the pinned close-pull-request action.
- Risks: `pull_request_target` is privileged; although this workflow does not check out PR code, any future expansion must avoid executing untrusted content. All matching PRs are closed unconditionally.
- Test signals: Workflow run logs and PR timeline migration comment.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/.github/workflows/auto-close-prs.yml -->
