# sources/cloud-native/soci-snapshotter/.github/workflows/new-pull-requests.yml

Purpose: automatically labels newly opened or updated non-draft pull requests.

Important APIs/types/functions: `pull_request_target` trigger, permissions `contents: read` and `pull-requests: write`, `actions/labeler@v6`, config `.github/new-pull-request-labels.yml`, `sync-labels: true`.

Control flow: without checking out untrusted PR code, the labeler reads main-branch config and synchronizes labels on non-draft PRs.

State and persistence: mutates PR labels.

Dependencies/integration: secure pairing with label config and GitHub pull request metadata.

Risks: `pull_request_target` is safe here because no PR code is checked out, but future edits adding checkout/run steps would raise security risk. Draft PRs are ignored until state changes retrigger.

Test signals: PR label changes for known file patterns.
