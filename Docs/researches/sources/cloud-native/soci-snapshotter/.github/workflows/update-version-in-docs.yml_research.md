# sources/cloud-native/soci-snapshotter/.github/workflows/update-version-in-docs.yml

Purpose: validates and automates documentation version updates for SOCI releases.

Important APIs/types/functions: triggers workflow dispatch/call/release/pull_request/release-branch push; input `tag_name`; script `scripts/update-version-in-docs.sh`; creates PRs with `peter-evans/create-pull-request`.

Control flow: PRs sparsely check out docs and script, then assert an update with a dummy version. Non-PR events derive tag and target branch from input, GitHub release event, or release branch plus latest-release API lookup, check out docs/script, run update script, and open an automated PR.

State and persistence: edits docs in PR branches and creates pull requests.

Dependencies/integration: called by release branch workflow and release events; relies on docs paths `docs/eks.md` and `docs/getting-started.md`.

Risks: API parsing with grep/cut/awk can select wrong tags. Workflow skips GitHub-action-authored branch pushes to avoid loops. Only selected docs are sparse-checked out.

Test signals: PR assertion job and automated PR creation on release events or branch pushes.
