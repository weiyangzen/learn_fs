# sources/cloud-native/soci-snapshotter/.github/workflows/create-third-party-licenses.yml

Purpose: generates and PRs `THIRD_PARTY_LICENSES` updates for release branches and validates license generation on PRs.

Important APIs/types/functions: supports workflow dispatch, workflow call, release branch pushes, and PRs; inputs `tag_name`; installs `go-licenses`; runs `scripts/build-third-party-licenses.sh`; creates PRs with `peter-evans/create-pull-request`.

Control flow: PRs only run test generation. Non-PR events determine `TAG_NAME` and `TARGET_BRANCH` from input or latest release API lookup for release branch pushes, check out the target branch, generate licenses, and open an automated PR.

State and persistence: creates/updates license files and PR branches; uses GitHub API reads for latest tag inference.

Dependencies/integration: called from release branch workflow and triggered on release branch pushes.

Risks: release API parsing uses grep/cut/awk on JSON and can select unexpected tags. It skips GitHub-action-authored push events to avoid automation loops.

Test signals: PR path validation and release-branch push/dispatch PR creation.
