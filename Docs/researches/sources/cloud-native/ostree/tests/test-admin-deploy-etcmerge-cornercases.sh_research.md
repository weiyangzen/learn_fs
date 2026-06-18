# sources/cloud-native/ostree/tests/test-admin-deploy-etcmerge-cornercases.sh

Purpose: exercises difficult `/etc` merge cases across deployments: modified files, directory permissions, removed paths, symlinks, and file/directory conflicts.

Important APIs/functions: `setup_os_repository`, `pull-local`, `ostree admin deploy`, `os_repository_new_commit`, shell filesystem mutation, `stat`, `readlink`, and assertion helpers.

Control flow: deploys a base commit, edits the live deployment's `/etc`, creates nested directories with custom modes, removes and replaces selected defaults, creates symlink cases, generates a new upstream commit, redeploys, and validates that local admin changes and permissions are merged or pruned as intended.

State/persistence: modifies deployed `/etc` in place and compares it with the next deployment. Dependencies are admin harness default config files and kernel boot state.

Integration/risk/test signals: covers one of OSTree admin's highest-risk persistence contracts: preserving local config without keeping obsolete defaults. Risks are broad fixture coupling and exact mode expectations. TAP ok lines segment the merge scenarios.
