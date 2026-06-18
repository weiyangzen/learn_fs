# sources/cloud-native/ostree/tests/test-admin-deploy-bootid-gc.sh

Purpose: ensures failed deployment staging directories are scoped by boot ID and garbage-collected when a later deploy uses a different boot ID.

Important APIs/functions: uses `OSTREE_REPO_TEST_ERROR=pre-commit`, `OSTREE_BOOTID`, `ostree admin deploy`, and temporary staging path assertions under `sysroot/ostree/repo/tmp`.

Control flow: deploys a base commit, creates a new commit, forces a pre-commit failure with one synthetic boot ID, asserts a `staging-${TEST_BOOTID}-*` directory exists, then deploys with another boot ID and checks old staging is removed.

State/persistence: manipulates repo tmp staging directories and sysroot deployments. Dependencies include test-only OSTree failure injection and boot ID environment handling.

Integration/risk/test signals: targets cleanup of interrupted deploy transactions. Risks are reliance on private test error hooks and tmp naming format. The single TAP case passes when stale staging does not survive the replacement deploy.
