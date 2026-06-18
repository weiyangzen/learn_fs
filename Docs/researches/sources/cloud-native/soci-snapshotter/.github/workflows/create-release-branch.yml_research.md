# sources/cloud-native/soci-snapshotter/.github/workflows/create-release-branch.yml

Purpose: orchestrates release branch creation and follow-up release maintenance PRs for licenses and docs.

Important APIs/types/functions: workflow dispatch inputs `major_minor_version` and `base_commit`; PR test job; scripts `create-release-branch.sh`, `build-third-party-licenses.sh`, and `update-version-in-docs.sh`; reusable workflows `create-third-party-licenses.yml` and `update-version-in-docs.yml`.

Control flow: PR runs dry-run validation and doc/license generation checks. Manual dispatch checks out main sparsely, validates version format, creates `release/<major.minor>` from requested base, outputs tag version, then calls downstream workflows with write permissions to create PRs.

State and persistence: on dispatch, creates a release branch and later PR branches for generated files.

Dependencies/integration: depends on GitHub token write permissions, release scripts, Go/go-licenses, and downstream workflows.

Risks: version validation prepends `v` in `VERSION` while input description says major.minor, so formatting expectations are strict. Sparse checkout in create job only includes branch script.

Test signals: PR dry run and manual workflow dispatch.
