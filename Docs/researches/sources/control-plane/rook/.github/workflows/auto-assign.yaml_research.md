# sources/control-plane/rook/.github/workflows/auto-assign.yaml

Purpose: GitHub Actions workflow that lets contributors self-assign issues by commenting `/assign`.

Important configuration and control flow: it triggers on `issue_comment` `created` and `edited` events. Global permissions grant read-only contents; the `assign` job grants `issues: write`, runs on Ubuntu latest, and invokes pinned `bdougie/take-action` with a thank-you message, trigger `/assign`, and the repository `GITHUB_TOKEN`.

State, dependencies, and integration: state changes occur in GitHub issue assignees and issue comments. It depends on the third-party action and GitHub token permissions. It integrates with issue triage rather than code builds.

Risks and test signals: a third-party action pin is a specific commit, which is good for supply-chain stability but needs manual updates. Edited comments can retrigger assignment. Signals are successful workflow runs and issue assignee changes after `/assign`.
