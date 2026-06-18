# sources/control-plane/csi-driver-nfs/release-tools/.github/workflows/codespell.yml

Purpose: runs codespell on pushes and pull requests for the release-tools repository copy.

Important configuration: workflow `codespell` checks out the repository at a pinned action commit and runs `codespell-project/actions-codespell` at a pinned commit. It enables filename checking and skips binary/image patterns, `.git`, the workflow itself, and `prow.sh`.

Control flow: GitHub Actions triggers on `push` and `pull_request`, runs on Ubuntu latest, checks out source, and executes the codespell action.

State and persistence behavior: no repository state is mutated. The workflow emits CI status and logs in GitHub Actions.

Dependencies and integration points: depends on GitHub Actions, actions/checkout, and the codespell action. It complements local spelling or boilerplate checks.

Risks: `prow.sh` is skipped, so spelling issues there are not caught. Pinned action SHAs must be maintained manually or by Dependabot.

Test signals: CI status is the signal; there are no in-repo tests for the workflow file.
