# sources/control-plane/csi-driver-iscsi/release-tools/.github/workflows/codespell.yml

Purpose: runs codespell on pushes and pull requests for release-tools.

Important APIs and types: one `codespell` job runs on `ubuntu-latest`, checks out code with a pinned `actions/checkout` SHA, then runs pinned `codespell-project/actions-codespell` with filename checking and skip patterns.

Control flow: GitHub triggers the workflow on every push and PR. The action scans tracked text while skipping binary image extensions, sums, `.git`, its own workflow file, and `prow.sh`.

State and persistence: no durable state is written except workflow logs and check status.

Dependencies and integration: depends on GitHub Actions, checkout, and the codespell action. It complements `verify-spelling.sh`, which uses `misspell`.

Risks: skip patterns intentionally exclude `prow.sh`, so spelling errors there are not caught by this workflow. Pinned action SHAs improve reproducibility but require manual updates.

Test signals: workflow pass/fail is the direct signal.
